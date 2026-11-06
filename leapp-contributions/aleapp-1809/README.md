# Bug report artifact groups and invented fixture values

Author: Daniel Kwaku Ntiamoah Addai, SectraTEK Lab. Contribution to ALEAPP, pull request 1809. State: Merged on October 27, 2026.

All bug report tables sat in one category, device identifiers were not read, and three numbers in the fixtures also occur in real reports. This contribution groups the tables by the question they answer, adds a Device Identifiers table that shows the values as printed, and replaces the three fixture numbers with invented ones.

## Links

- Pull request: <https://github.com/abrignoni/ALEAPP/pull/1809>
- Parser source in the upstream repository (abrignoni/ALEAPP, at the commit of the pull request):
  - [`scripts/artifacts/bugreportActivity.py`](https://github.com/abrignoni/ALEAPP/blob/c915fb63d87a23968f236c3cc5428f071a48ecc0/scripts/artifacts/bugreportActivity.py)
  - [`scripts/artifacts/bugreportDevice.py`](https://github.com/abrignoni/ALEAPP/blob/c915fb63d87a23968f236c3cc5428f071a48ecc0/scripts/artifacts/bugreportDevice.py)
  - [`scripts/dumpstate_reader.py`](https://github.com/abrignoni/ALEAPP/blob/c915fb63d87a23968f236c3cc5428f071a48ecc0/scripts/dumpstate_reader.py)
- Lab write-up: lab.sectratek.com/open-source/aleapp-1809/ (published with the Lab website)

## What it reads

The bug report text. The new Bug Report - Device Identifiers table reads a list of identifier properties and the lines that print them, and shows each value exactly as printed with its source line. The other changes are category names and fixture values.

Report artifacts (1):

- Bug Report - Device Identifiers (new)

## Fixtures

Copied from the pull request at commit `c915fb63`. All values are synthetic and invented. Licence: as the upstream repository.

How they were made (from the pull request): Ten new synthetic bug report zips for the Device Identifiers table (invented values only) plus unit tests in scripts/test_bugreport_all.py. Existing fixture generators were changed upstream; only files this pull request added are copied here.

Data files (zip archives shaped like an extraction, one set per test case):

| Name | What it is | How made |
| --- | --- | --- |
| `fixtures/data/bugreportDevice/testdata.bugreportDevice.<artifact>.<case>.zip` (10 files, 47 KB) | Synthetic test cases with invented values (cases: identifiers, a10, a16, cut, empty, not_a_report, odd_bytes, two_reports, zip_on_device); see the note above and the upstream pull request. | See the note above |

Scripts (the generators that build the synthetic files, and the unit tests that use them):

| Name | What it is | How made |
| --- | --- | --- |
| `fixtures/scripts/test_bugreport_all.py` | Unit tests for the parser, as added by the pull request | Written for the pull request |

Also not copied: the expected-output snapshots under `admin/test/results/` and the case descriptors `admin/test/cases/testdata.*.json`. They carry upstream commit metadata and are in the upstream pull request; running the parser on a fixture regenerates the output.

## Try it

From a checkout of abrignoni/ALEAPP, run the tool on one of the fixture zips (the output folder must already exist):

```
python aleapp.py -t zip -i <path to a fixture zip> -o <path to an existing output folder>
```

The fixtures are zip files shaped like an extraction, so they are read like any zip extraction. The upstream test harness uses the same files; with the zips in place under `admin/test/cases/data/` it is run per module:

```
python admin/test/scripts/run_test_cases.py --module bugreportDevice
```

See the upstream README for current options and for installing the requirements.

## What it does not prove

An identifier printed in a bug report is not shown to belong to the device in front of the examiner. A property that is not on the list is not shown to be absent from the device.

## Provenance

- Fixtures: copied unchanged from abrignoni/ALEAPP pull request 1809 at commit `c915fb63`. They are synthetic with invented values and were checked for e-mail addresses, phone-number-like strings, device identifiers and file paths before copying. Licence: as the upstream repository.
- The pull request was reviewed and merged by the maintainers of ALEAPP, to whom the project belongs. Source: <https://github.com/abrignoni/ALEAPP/pull/1809>.
- Author: Daniel Kwaku Ntiamoah Addai, SectraTEK Lab.
- This README is licensed CC BY 4.0.
