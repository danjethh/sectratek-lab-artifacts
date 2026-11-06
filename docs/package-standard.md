# Package standard

Every folder under `reports/` follows this standard. `tools/check_packages.py` checks the mechanical parts in CI.

## Required

| Item | Rule |
|---|---|
| `README.md` | Names the report (title and LAB-TR number), the Python version, the files, the commands, what the package reproduces, and what needs the private corpus. |
| `LICENSE-CODE`, `LICENSE-DATA` | Code is MIT. Data and text are CC BY 4.0. |
| A self-test | `selftest.py` (or `tests.py`) runs the package from two clean copies with a fixed seed, compares SHA-256 of every output and checks the key values the report prints. Exit code 0 means pass. |
| Synthetic or fixture data only | Fixtures and phones come from generators or hand-written examples in the package, with invented values marked as such. |
| Standard library | Python 3.10 or later with no third-party installs. |

## Not allowed

- Any file containing data from a real device, case, person or organization.
- Network access, absolute paths, local clock dependence or unseeded randomness in a run that a self-test compares.
- Files over 5 MB without a stated reason in the package README.

## README sections

1. What this is and which report it belongs to.
2. Files (a table).
3. Run (commands and approximate time).
4. What it reproduces (tables, figures, sections of the report).
5. What needs the private corpus.
6. Limits: what the results do not prove.

## Packages in preparation

A package that is not ready has a folder with a README that says so and names the report. It has no code and no self-test, and the catalog marks it `preparation`.
