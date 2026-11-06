# Contributing

Thank you for looking. This repository supports published research, so the aim is accuracy before volume.

## Good contributions

- A **wrong number or a broken self-test** on your Python or SQLite version (include versions and the printed output).
- A **failing case**: an input that breaks a decision rule, a reader or a calculus, as a small invented fixture.
- A **portability fix** (paths, line endings, Python version) that does not change results.
- A **clearer README line** or a missing "what this does not prove".

## Not accepted

- Any data from a real device, case, person or organization, including in an issue or a screenshot.
- New dependencies. Packages stay standard library only.
- Changes that alter a published number without an issue that explains why.

## How

1. Open an issue first for anything beyond a typo or portability fix.
2. Keep one change per pull request.
3. Run `python tools/check_packages.py` and `python tools/run_selftests.py --only lab-tr-NNNN` for the package you touched.
4. Say in the description what the change does and does not prove.

## Licensing of contributions

By contributing you agree your code is released under the MIT licence and your data and text under CC BY 4.0, as in the rest of the repository.

Contact: daniel@prudentialassociates.com
