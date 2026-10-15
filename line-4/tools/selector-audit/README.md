# Selector Audit

List canonical function signatures and four-byte Ethereum selectors before choosing
a function for ABI Workbench. Flags duplicate canonical signatures, distinct
signatures sharing a selector, and types outside the companion codec's subset.
Input and output support are reported separately: an unsupported return type does
not hide a usable input selector. ABI entries are data and are never executed.

From the repository root, run this offline demonstration:

```sh
python3 -B line-4/tools/selector-audit/selector_audit.py --abi line-4/tools/selector-audit/erc20.json
```

Observed: three ERC-20 functions, selectors `0xa9059cbb`, `0x70a08231`, and
`0x095ea7b3`, no ambiguities, exit 0. These are interface examples appropriate to
ZTO first and IMD second; they make no claim about deployed bytecode, balances,
allowances or successful execution. The tool performs no chain queries.

Use `--abi YOUR_WORKSPACE_ABI.json` for another ABI. Exit 0 means no findings
among the supplied function entries; exit 1 prints a report containing ambiguities
or unsupported types; exit 2 means invalid input and prints only an error to
stderr. Constructor, event and custom-error entries are validated structurally
but excluded from function dispatch. An ABI with no functions has an empty
inventory. Output `index` is the original zero-based ABI entry position.

Eight regression tests pass, including the distinct `burn(uint256)` and
`collate_propagate_storage(bytes16)` collision at `0x42966c68`, alias duplicates,
overloads, nested tuples, unsupported types, clean CLI errors and byte limits:

```sh
mkdir -p test/scratch
python3 -B -m unittest discover -s line-4/tools/selector-audit -v
```

Python 3.10+, standard library only. Reuses
`../abi-workbench/abi_workbench.py`; keep both folders together. Files must resolve
inside the current workspace; reads are capped at 1 MiB and reject duplicate JSON
fields. The companion codec's tuple-depth, node, parameter and supported-type
limits apply. Structural limits are not strict CPU/time or memory bounds.

A selector is only four bytes: an unambiguous supplied ABI cannot rule out
collisions with omitted functions or establish contract identity. Unsupported
input signatures have null selectors and are excluded from collision groups, so
a report with unsupported inputs is incomplete. This does not inspect bytecode,
proxies, fallback dispatch, custom errors or events. No secret, wallet, signing,
transaction sending or external writes are used.
