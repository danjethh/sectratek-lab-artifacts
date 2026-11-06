# Permission cache and location state dumps

Author: Daniel Kwaku Ntiamoah Addai, SectraTEK Lab. Contribution to iLEAPP, pull request 2518. State: Merged on October 20, 2026.

Processes write snapshots of their own state into the unified log. This contribution reads two of them, the permission cache and the location manager state, and explains why they show a state at a moment: not an event, and not who asked.

## Links

- Pull request: <https://github.com/abrignoni/iLEAPP/pull/2518>
- Parser source in the upstream repository (abrignoni/iLEAPP, at the commit of the pull request):
  - [`scripts/artifacts/logarchive.py`](https://github.com/abrignoni/iLEAPP/blob/c3248e0580a81040b340f1c195495951ddfd144d/scripts/artifacts/logarchive.py)
- Lab write-up: lab.sectratek.com/open-source/ileapp-2518/ (published with the Lab website)

## What it reads

Statedump records in the unified log titled TCC Authorization Cache and CLLocationManagerStateTracker. Each kind has two artifacts: one row per cached entry (or per dump), and a collapsed view that gives the first and last dump that held the same content and the number of dumps.

Report artifacts (4):

- logarchive TCC authorization cache dumps
- logarchive TCC authorization cache summary
- logarchive location manager state dumps
- logarchive location manager state summary

## Fixtures

Copied from the pull request at commit `c3248e05`. All values are synthetic and invented. Licence: as the upstream repository.

How they were made (from the pull request): Built by scripts/synthetic_statedumps.py: a fabricated log show JSON export with invented process paths, process ids and object addresses, repeated dumps, an empty cache, shapes marked as invented in the builder, and decoys that mention the same names.

Data files (zip archives shaped like an extraction, one set per test case):

| Name | What it is | How made |
| --- | --- | --- |
| `fixtures/data/logarchive/testdata.logarchive.<artifact>.<case>.zip` (1 files, 40 KB) | Synthetic test cases with invented values (cases: statedump); see the note above and the upstream pull request. | See the note above |

Scripts (the generators that build the synthetic files, and the unit tests that use them):

| Name | What it is | How made |
| --- | --- | --- |
| `fixtures/scripts/synthetic_statedumps.py` | Generator that builds the synthetic fixture data | Written for the pull request |
| `fixtures/scripts/test_logarchive_statedumps.py` | Unit tests for the parser, as added by the pull request | Written for the pull request |

Also not copied: the expected-output snapshots under `admin/test/results/` and the case descriptors `admin/test/cases/testdata.*.json`. They carry upstream commit metadata and are in the upstream pull request; running the parser on a fixture regenerates the output.

## Try it

The fixture is a fabricated log export that feeds the logarchive module. The camera, microphone and state dump artifacts read the table that logarchive builds from it and declare no paths of their own, so the upstream case harness cannot supply their input; the upstream test drives the real chain instead. See the test script in `fixtures/scripts/` (it expects to sit under `admin/test/scripts/` in an iLEAPP checkout) and the upstream README.

To run the logarchive module over the fixture with the upstream harness, from a checkout:

```
python admin/test/scripts/run_test_cases.py --module logarchive
```

## What it does not prove

A permission is not shown to have been granted, changed or used at a given time. A process is not shown to have used location. The app a dump describes is not identified.

## Provenance

- Fixtures: copied unchanged from abrignoni/iLEAPP pull request 2518 at commit `c3248e05`. They are synthetic with invented values and were checked for e-mail addresses, phone-number-like strings, device identifiers and file paths before copying. Licence: as the upstream repository.
- The pull request was reviewed and merged by the maintainers of iLEAPP, to whom the project belongs. Source: <https://github.com/abrignoni/iLEAPP/pull/2518>.
- Author: Daniel Kwaku Ntiamoah Addai, SectraTEK Lab.
- This README is licensed CC BY 4.0.
