# Camera and microphone sessions in the unified log

Author: Daniel Kwaku Ntiamoah Addai, SectraTEK Lab. Contribution to iLEAPP, pull request 2517. State: Merged on October 20, 2026.

The camera capture daemon writes a line when a session starts. This contribution lists those lines, together with SpringBoard's recording-indicator lines, and explains why a session line says which process asked, not that anything was recorded.

## Links

- Pull request: <https://github.com/abrignoni/iLEAPP/pull/2517>
- Parser source in the upstream repository (abrignoni/iLEAPP, at the commit of the pull request):
  - [`scripts/artifacts/logarchive.py`](https://github.com/abrignoni/iLEAPP/blob/f45a60a4f6512190c8125d7515405d57a216f44d/scripts/artifacts/logarchive.py)
- Lab write-up: lab.sectratek.com/open-source/ileapp-2517/ (published with the Lab website)

## What it reads

Unified log lines from the camera capture daemon (session lifecycle and streaming power events) and SpringBoard recording-indicator lines, read through the logarchive module. Fields are copied as logged. State lines are listed only when the started flag or a stolen flag is 1.

Report artifacts (3):

- logarchive camera and microphone capture sessions
- logarchive camera streaming power events
- logarchive recording indicator lines

## Fixtures

Copied from the pull request at commit `f45a60a4`. All values are synthetic and invented. Licence: as the upstream repository.

How they were made (from the pull request): Built by scripts/synthetic_capture_sessions.py: a fabricated log show JSON export with invented app ids, process ids and process names, fixed timestamps, and decoy lines under other subsystems.

Data files (zip archives shaped like an extraction, one set per test case):

| Name | What it is | How made |
| --- | --- | --- |
| `fixtures/data/logarchive/testdata.logarchive.logarchive.case_synthetic_capture.zip` | Synthetic. A fabricated 'log show --style json' export (invented app ids, PIDs and process names, fixed 2026-03-14 timestamps at a -0500 offset) built by admin/test/scripts/synthetic_capture_sessions.py: camera capture daemon session. | Built by `synthetic_capture_sessions.py` |

Scripts (the generators that build the synthetic files, and the unit tests that use them):

| Name | What it is | How made |
| --- | --- | --- |
| `fixtures/scripts/synthetic_capture_sessions.py` | Generator that builds the synthetic fixture data | Written for the pull request |
| `fixtures/scripts/test_logarchive_capture_sessions.py` | Unit tests for the parser, as added by the pull request | Written for the pull request |

Also not copied: the expected-output snapshots under `admin/test/results/` and the case descriptors `admin/test/cases/testdata.*.json`. They carry upstream commit metadata and are in the upstream pull request; running the parser on a fixture regenerates the output.

## Try it

The fixture is a fabricated log export that feeds the logarchive module. The camera, microphone and state dump artifacts read the table that logarchive builds from it and declare no paths of their own, so the upstream case harness cannot supply their input; the upstream test drives the real chain instead. See the test script in `fixtures/scripts/` (it expects to sit under `admin/test/scripts/` in an iLEAPP checkout) and the upstream README.

To run the logarchive module over the fixture with the upstream harness, from a checkout:

```
python admin/test/scripts/run_test_cases.py --module logarchive
```

## What it does not prove

Audio or video is not shown to have been recorded or saved. An app is not shown to have used the camera. An empty result is not shown to mean nothing was captured: the log has a limited window.

## Provenance

- Fixtures: copied unchanged from abrignoni/iLEAPP pull request 2517 at commit `f45a60a4`. They are synthetic with invented values and were checked for e-mail addresses, phone-number-like strings, device identifiers and file paths before copying. Licence: as the upstream repository.
- The pull request was reviewed and merged by the maintainers of iLEAPP, to whom the project belongs. Source: <https://github.com/abrignoni/iLEAPP/pull/2517>.
- Author: Daniel Kwaku Ntiamoah Addai, SectraTEK Lab.
- This README is licensed CC BY 4.0.
