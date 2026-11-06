# Reproducibility

## What "reproduces" means here

A package reproduces a table or figure when running its code on the package's invented data gives the numbers the report prints for that table or figure. The package README lists which tables and figures that covers. Results that come from the Lab's private research corpus are not reproducible from this repository, and the README says so.

## The self-test

`python tools/run_selftests.py` runs each package's self-test. A self-test:

1. Copies the package into two clean folders.
2. Runs the package's entry point in each with the same seed.
3. Compares the SHA-256 of every output file between the two runs.
4. Checks the key values the report prints (counts, percentages) against the run.

Exit code 0 means both runs match and the key values hold.

## Versions

- Python 3.10 or later. CI runs 3.10 and 3.12.
- SQLite behaviour can change between versions. Packages that depend on it print the version they ran with (the reports state 3.50.4 where it matters). A difference in a SQLite-dependent value on another version is worth an issue.

## Seeds

Generators take `--seed N`. The default seed is the one the report used. Changing it gives a different but valid sample, so counts will differ in a way the report's own variation figures describe.

## Results file

`tools/run_selftests.py` writes `tools/selftest_results.json` with the command, result and time per package. The catalog in `catalog.json` lists the package states.
