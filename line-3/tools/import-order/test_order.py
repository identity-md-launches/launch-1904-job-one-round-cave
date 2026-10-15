"""Offline behavior checks; temporary source files stay in test/scratch."""

import contextlib
import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import random
import tempfile
import unittest


SPEC = importlib.util.spec_from_file_location('order', Path(__file__).with_name('order.py'))
O = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(O)
M = O.load_budget().load_mapper()


def mapped(sources):
    return M.inspect(Path('.'), source_bytes={name: source.encode() for name, source in sources.items()})


def graph_report(graph):
    return mapped({name + '.py': ''.join('import ' + target + '\n' for target in sorted(targets))
                   for name, targets in graph.items()})


def group_members(result):
    return [[module['module'] for module in group['modules']] for group in result['groups']]


class OrderTests(unittest.TestCase):
    def test_diamond_and_independent_modules_are_dependency_first(self):
        graph = {'app': {'left', 'right'}, 'left': {'base'}, 'right': {'base'},
                 'base': set(), 'spare': set()}
        result = O.plan(graph_report(graph))
        self.assertEqual(result['waves'], [{'number': 1, 'groups': ['base', 'spare']},
                                          {'number': 2, 'groups': ['left', 'right']},
                                          {'number': 3, 'groups': ['app']}])
        self.assertEqual(result['groups'][-1]['dependencies'], ['left', 'right'])
        self.assertFalse(any(group['cyclic'] for group in result['groups']))
        self.assertEqual(result['summary']['selected_edge_count'], 4)

    def test_cycles_and_self_loops_are_indivisible_groups(self):
        graph = {'app': {'a'}, 'a': {'b', 'base'}, 'b': {'a'},
                 'base': {'base'}, 'other': {'peer'}, 'peer': {'other'}}
        result = O.plan(graph_report(graph))
        self.assertEqual(result['waves'], [{'number': 1, 'groups': ['base', 'other']},
                                          {'number': 2, 'groups': ['a']},
                                          {'number': 3, 'groups': ['app']}])
        self.assertEqual(group_members(result), [['base'], ['other', 'peer'], ['a', 'b'], ['app']])
        self.assertEqual([group['cyclic'] for group in result['groups']], [True, True, True, False])
        internal = [edge for edge in result['edges'] if edge['from_group'] == edge['to_group']]
        self.assertEqual(len(internal), 5)

    def test_selected_forward_closure_dedupes_and_keeps_complete_cycle(self):
        report = graph_report({'app': {'a'}, 'a': {'b', 'base'}, 'b': {'a'},
                               'base': set(), 'spare': set()})
        result = O.plan(report, ['b', 'b'])
        self.assertEqual(result['selection'], {'from': ['b'], 'mode': 'dependency_closure'})
        self.assertEqual(group_members(result), [['base'], ['a', 'b']])
        self.assertEqual(result['summary']['module_count'], 5)
        self.assertEqual(result['summary']['selected_module_count'], 3)
        result = O.plan(report, ['spare', 'b', 'spare'])
        self.assertEqual(result['selection']['from'], ['b', 'spare'])
        self.assertEqual(group_members(result), [['base'], ['spare'], ['a', 'b']])
        with self.assertRaisesRegex(ValueError, 'unknown local module'):
            O.plan(report, ['absent'])

    def test_relative_alias_sites_and_entrypoints_are_preserved(self):
        report = mapped({'pkg/__init__.py': '', 'pkg/a.py':
                         '# comment\nfrom . import b as bee\nfrom . import b\n'
                         'if __name__ == "__main__": pass\n', 'pkg/b.py': ''})
        result = O.plan(report, ['pkg.a'])
        self.assertEqual(group_members(result), [['pkg.b'], ['pkg.a']])
        self.assertTrue(result['groups'][1]['modules'][0]['entrypoint'])
        self.assertEqual(result['edges'][0]['sites'], [
            {'path': 'pkg/a.py', 'line': 2, 'target': '. import b'},
            {'path': 'pkg/a.py', 'line': 3, 'target': '. import b'}])

    def test_warnings_outside_selection_and_parse_failures_remain_visible(self):
        report = mapped({'selected.py': '', 'dynamic.py': '__import__("plugin")\n',
                         'broken.py': '\x00', 'cyclic.py': 'import cyclic\n',
                         'pkg/__init__.py': '', 'pkg.py': ''})
        result = O.plan(report, ['selected'])
        self.assertEqual(group_members(result), [['selected']])
        self.assertEqual(result['issues'], report['issues'])
        self.assertEqual({issue['type'] for issue in result['issues']}, {'parse_error', 'module_collision'})
        self.assertEqual(result['dynamic_imports'], [{'module': 'dynamic', 'path': 'dynamic.py', 'line': 1}])
        self.assertEqual(result['cycles'], [['cyclic']])
        text = O.format_text(result)
        self.assertIn('Warnings across scanned root: 2 issues, 1 dynamic calls, 1 cyclic components', text)
        self.assertIn('broken.py:', text)
        self.assertIn('Cycle: cyclic', text)

    def test_empty_graph_and_excluded_root_initializer(self):
        report = mapped({'__init__.py': 'raise RuntimeError("not executed")\n'})
        result = O.plan(report)
        for key in ('waves', 'groups', 'edges'):
            self.assertEqual(result[key], [])
        self.assertEqual(result['summary']['wave_count'], 0)
        self.assertIn('No mapped modules', O.format_text(result))
        with self.assertRaisesRegex(ValueError, 'unknown local module'):
            O.plan(report, ['__init__'])

    def test_long_chain_and_large_cycle_do_not_recurse(self):
        names = [f'n{i:04}' for i in range(1800)]
        graph = {name: {names[i + 1]} if i + 1 < len(names) else set()
                 for i, name in enumerate(names)}
        result = O.plan(graph_report(graph))
        self.assertEqual(result['summary']['wave_count'], 1800)
        self.assertEqual(result['waves'][0]['groups'], [names[-1]])
        self.assertEqual(result['waves'][-1]['groups'], [names[0]])
        graph[names[-1]].add(names[0])
        result = O.plan(graph_report(graph), [names[900]])
        self.assertEqual(result['summary']['wave_count'], 1)
        self.assertEqual(group_members(result), [names])

    def test_random_graphs_against_independent_reachability_oracle(self):
        rng = random.Random(31)
        names = list('abcdefgh')
        for _ in range(90):
            graph = {name: {target for target in names if rng.random() < .19} for name in names}
            reachable = {(a, b): a == b or b in graph[a] for a in names for b in names}
            for middle in names:
                for start in names:
                    for end in names:
                        reachable[start, end] |= reachable[start, middle] and reachable[middle, end]
            expected = {tuple(b for b in names if reachable[a, b] and reachable[b, a]) for a in names}
            report = graph_report(graph)
            before = copy.deepcopy(report)
            result = O.plan(report)
            self.assertEqual(report, before)
            self.assertEqual({tuple(group) for group in group_members(result)}, expected)
            members = {module['module']: group for group in result['groups'] for module in group['modules']}
            for source in names:
                own = members[source]
                for target in graph[source]:
                    dependency = members[target]
                    self.assertTrue(own['id'] == dependency['id'] or dependency['wave'] < own['wave'])
                expected_dependencies = {members[target]['id'] for member in own['modules']
                                         for target in graph[member['module']]
                                         if members[target]['id'] != own['id']}
                self.assertEqual(own['dependencies'], sorted(expected_dependencies))
                self.assertEqual(own['wave'], 1 + max((members[d]['wave'] for d in expected_dependencies), default=0))
            for start in names:
                selected = O.plan(report, [start])
                self.assertEqual({m['module'] for g in selected['groups'] for m in g['modules']},
                                 {name for name in names if reachable[start, name]})
            shuffled = copy.deepcopy(report)
            rng.shuffle(shuffled['modules'])
            rng.shuffle(shuffled['edges'])
            # The mapper emits sorted warning lists; graph input order alone is irrelevant.
            self.assertEqual(O.plan(shuffled), result)

    def test_inconsistent_cycles_or_missing_evidence_refuse(self):
        report = graph_report({'a': {'b'}, 'b': {'a'}})
        report['cycles'] = []
        with self.assertRaisesRegex(ValueError, 'ungrouped cycle'):
            O.plan(report)
        report = graph_report({'a': {'b'}, 'b': set()})
        report['modules'][0]['imports'] = []
        with self.assertRaisesRegex(ValueError, 'missing source evidence'):
            O.plan(report)

    def test_cli_snapshot_hashes_refusals_warnings_and_no_execution(self):
        scratch = Path('test/scratch')
        scratch.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as name:
            root = Path(name)
            marker = root / 'executed'
            source = ('import b\n' + f'open({str(marker)!r}, "w").write("ran")\n').encode()
            (root / 'a.py').write_bytes(source)
            (root / 'b.py').write_text('')

            def cli(*args):
                out, err = io.StringIO(), io.StringIO()
                with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                    code = O.main([str(root), '--json', *args])
                self.assertEqual(err.getvalue(), '')
                return code, json.loads(out.getvalue())

            code, result = cli('--strict', '--from', 'a')
            self.assertEqual(code, 0)
            self.assertEqual(result['status'], 'complete')
            self.assertEqual(result['inventory']['manifest'][0]['sha256'], hashlib.sha256(source).hexdigest())
            for args in [('--from', 'absent'), ('--max-files', '1'),
                         ('--max-file-bytes', '1'), ('--max-total-bytes', '1'),
                         ('--max-entries', '1'), ('--max-depth', '0')]:
                code, result = cli(*args)
                self.assertEqual(code, 2)
                self.assertEqual(set(result), {'status', 'error'})
                self.assertEqual(result['status'], 'refused')
            (root / 'outside.py').write_text('import outside\n__import__("plugin")\n')
            self.assertEqual(cli('--from', 'a')[0], 0)
            self.assertEqual(cli('--from', 'a', '--strict')[0], 1)
            self.assertFalse(marker.exists())


if __name__ == '__main__':
    unittest.main()
