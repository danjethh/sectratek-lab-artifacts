# Reading the Android Health Connect store

Author: Daniel Kwaku Ntiamoah Addai, SectraTEK Lab. Contribution to ALEAPP, pull request 1784. State: Merged on October 25, 2026.

Health Connect is where Android keeps the steps, heart rate, sleep and exercise that fitness apps write, and ALEAPP could not read it. Thirteen artifacts now do. Record types, exercise types, sleep stages and recording methods are shown as the stored number followed by the Android source name.

## Links

- Pull request: <https://github.com/abrignoni/ALEAPP/pull/1784>
- Parser source in the upstream repository (abrignoni/ALEAPP, at the commit of the pull request):
  - [`scripts/artifacts/healthConnect.py`](https://github.com/abrignoni/ALEAPP/blob/cf9bf5c951bbe5e9f41bf16f69f2aaac5af79289/scripts/artifacts/healthConnect.py)
- Lab write-up: lab.sectratek.com/open-source/aleapp-1784/ (published with the Lab website)

## What it reads

healthconnect.db and the first-grant XML file under system_ce/<user>/healthconnect: apps, preferences, permission first-grant times, activity records, measurements, heart rate samples, sleep sessions and stages, and the rest of the record tables. Times are converted from milliseconds with the zone offset the writing app supplied.

Report artifacts (13):

- Health Connect - Apps
- Health Connect - Preferences
- Health Connect - Permission First Grant Times
- Health Connect - Activity Records
- Health Connect - Measurements
- Health Connect - Heart Rate Samples
- Health Connect - Sleep Sessions
- Health Connect - Sleep Stages
- Health Connect - Exercise Sessions
- Health Connect - Exercise Route
- Health Connect - Access Logs
- Health Connect - Read Access Logs
- and 1 more; the full list is in the parser source linked above

## Fixtures

Copied from the pull request at commit `cf9bf5c9`. All values are synthetic and invented. Licence: as the upstream repository.

How they were made (from the pull request): Built by scripts/health_connect_fixture.py: a synthetic healthconnect.db in the Android 16 layout (Android source schema, invented rows) plus a first-grant-times file.

Data files (zip archives shaped like an extraction, one set per test case):

| Name | What it is | How made |
| --- | --- | --- |
| `fixtures/data/healthConnect/testdata.healthConnect.<artifact>.synthetic_a16.zip` (13 files, 909 KB) | Synthetic healthconnect.db (Android 16 layout, AOSP schema, invented rows) built by admin/test/scripts/health_connect_fixture.py, plus a first-grant-times file. Not from a real device. | Built by `health_connect_fixture.py` |

Scripts (the generators that build the synthetic files, and the unit tests that use them):

| Name | What it is | How made |
| --- | --- | --- |
| `fixtures/scripts/health_connect_fixture.py` | Generator that builds the synthetic fixture data | Written for the pull request |
| `fixtures/scripts/test_health_connect.py` | Unit tests for the parser, as added by the pull request | Written for the pull request |

Also not copied: the expected-output snapshots under `admin/test/results/` and the case descriptors `admin/test/cases/testdata.*.json`. They carry upstream commit metadata and are in the upstream pull request; running the parser on a fixture regenerates the output.

## Try it

From a checkout of abrignoni/ALEAPP, run the tool on one of the fixture zips (the output folder must already exist):

```
python aleapp.py -t zip -i <path to a fixture zip> -o <path to an existing output folder>
```

The fixtures are zip files shaped like an extraction, so they are read like any zip extraction. The upstream test harness uses the same files; with the zips in place under `admin/test/cases/data/` it is run per module:

```
python admin/test/scripts/run_test_cases.py --module healthConnect
```

See the upstream README for current options and for installing the requirements.

## What it does not prove

A person is not shown to have slept, walked or exercised: the values are what the writing app supplied. A route point is not shown to be where the device was. A missing log row is not shown to mean no access took place.

## Provenance

- Fixtures: copied unchanged from abrignoni/ALEAPP pull request 1784 at commit `cf9bf5c9`. They are synthetic with invented values and were checked for e-mail addresses, phone-number-like strings, device identifiers and file paths before copying. Licence: as the upstream repository.
- The pull request was reviewed and merged by the maintainers of ALEAPP, to whom the project belongs. Source: <https://github.com/abrignoni/ALEAPP/pull/1784>.
- Author: Daniel Kwaku Ntiamoah Addai, SectraTEK Lab.
- This README is licensed CC BY 4.0.
