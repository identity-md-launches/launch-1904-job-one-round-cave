# Import Order

Find a dependency-first reading order for an unfamiliar Python project without
running its source. Each wave contains groups whose dependencies on other groups
are in earlier waves. Cyclic modules stay in one group so a reader can inspect
their coupling together. Groups ready at the same dependency depth share a wave.
The tool uses only Python's standard library, works offline, and requires Python
3.9 or newer.

From the repository root, run this complete demo:

```sh
python3 -B line-3/tools/import-order/order.py line-3/tools/import-order/examples --from cli
```

Tried locally: exit 0, six of seven modules selected, five groups and four waves:

1. `model`
2. the `engine`/`rules` cycle together, alongside `storage`
3. `service`
4. `cli`, marked as an entry point

The independent `spare` module is outside `cli`'s dependency closure. The cycle
warning remains visible. The example entry point raises if executed; scanning
it never executes it. Remove `--from cli` to include every mapped module.

Choose the directory Python would search for imports, such as a project's `src/`
directory. Use exact dotted module names with repeatable `--from MODULE` options
to select the union of their forward dependency closures. Unknown names refuse
the request. Duplicate starting names have no effect. The whole root is scanned
within its budgets even when a small closure is requested.

`--json` adds source evidence for every selected graph edge and a manifest of
the actual source bytes analyzed, including SHA-256 hashes. Each group has a
stable ID equal to its alphabetically first module, sorted members with paths
and entry-point flags, its dependency group IDs, and a one-based wave number.
Groups sort by wave and then ID. Waves contain sorted group IDs. A module in a
cycle has the same wave as every other member; alphabetical order inside that
group is only for presentation. The inherited mapper identifies cyclic strongly
connected components iteratively, and ordering adds no recursive traversal.

`summary.module_count` and the original map summary describe the entire root;
`selected_module_count`, `selected_edge_count`, `group_count` and `wave_count`
describe the requested plan. Issues, dynamic calls and cyclic components also
cover the entire root, including modules excluded by `--from`. A warning on an
unselected module therefore still makes `--strict` return 1. Inspect warnings
before trusting a first-wave module: a parse failure can hide its imports.

Exit codes are 0 for a complete plan, 1 for a complete plan with `--strict`
warnings, and 2 for unknown starting modules, input errors, scan failures or
exceeded budgets. JSON refusals contain only `status: "refused"` and `error`,
with no partial plan. Argument syntax errors use argparse's stderr and exit 2.
An empty root completes with no waves; it is not evidence of a valid import root.

Collection uses the existing Import Budget and Import Map tools. Its default
limits are 1,000 Python files, 262,144 bytes per file, 8,388,608 total source
bytes, 20,000 visited directory entries and depth 64. Override these positive
integer limits with `--max-files`, `--max-file-bytes`, `--max-total-bytes`,
`--max-entries` and `--max-depth`. Collection must complete before planning;
each source is read once and those same admitted bytes are analyzed. Preserve
`../import-budget/budget.py` and `../import-map/import_map.py` when copying this
folder. No installation or configuration is needed.

On actual worker source, this command completed with exit 0, 24 modules, 39 local
edges, 24 groups and four waves, with no issues, cycles or recognized dynamic
import calls:

```sh
python3 -B line-3/tools/import-order/order.py shared/import-drift --json --strict
```

The 24,346-byte [observed-source.json](observed-source.json) retains that complete
result and its 24-file source manifest (125,785 source bytes). This is a source
inspection of the real shared import-review worker, not execution of its code.
Its first wave contains eight modules; later waves lead through review helpers
to their callers and tests. The observation is tied to those source hashes;
later source edits can change it.

Reproduce the ten behavioral tests:

```sh
python3 -B -m unittest discover -s line-3/tools/import-order -v
```

All ten passed. Tests cover direction and minimal waves; disconnected modules;
cycles and self-loops; selected closures; duplicate and unknown names; relative
imports, aliases and duplicate evidence sites; warning retention; empty maps;
1,800-module chains and cycles; unchanged input reports; JSON refusals; source
hashes; and source execution traps that stay unexecuted. Ninety seeded random
graphs are compared with an independent all-pairs reachability oracle for SCC
membership and every starting module's closure. Each cross-group dependency is
checked against its earlier wave. An independent review additionally checked
all 512 directed three-module graphs and all eight starting-name subsets:
4,096 plans agreed with a reachability oracle.

This is a reading aid for explicit static local imports, not an execution,
initialization, deployment or safe parallelization schedule. Conditional imports
are included even when their condition is false. Dynamic targets, external
packages, runtime path changes and implicit package initialization are not
simulated. Namespace-only packages have no vertices; a root `__init__.py` is
collected and hashed but has no module name in this import-root model. Parsing
errors, module collisions and unresolved imports can hide edges.

The root must resolve inside the current working directory. Hidden and
conventional dependency directories, symlinks and nonregular files are skipped
and counted by the collector. Use a stable source tree; hashes are evidence of
admitted bytes, not an authenticated or atomic snapshot. Input budgets do not
limit CPU, memory, output size or elapsed time, and this is not a filesystem
sandbox. No coin, chain connection, key or payment is needed for source reading.
