# Three Parser Fixes for Empty and Failed Reports

Author: Daniel Kwaku Ntiamoah Addai, SectraTEK Lab. Contribution to iLEAPP, pull request 2574. State: Merged on October 25, 2026.

When a parser fails, the report goes quiet in a way that looks like an unused feature. Three small fixes make one calendar artifact, one location-services artifact and one app artifact read what the files hold, and the checks behind them show how to tell a real empty from a failed read.

## Links

- Pull request: <https://github.com/abrignoni/iLEAPP/pull/2574>
- Parser source in the upstream repository (abrignoni/iLEAPP, at the commit of the pull request):
  - [`scripts/artifacts/calendarAll.py`](https://github.com/abrignoni/iLEAPP/blob/1841fe44dee1308fc592c2086b0fd2c06634ecb5/scripts/artifacts/calendarAll.py)
  - [`scripts/artifacts/locServicesconfig.py`](https://github.com/abrignoni/iLEAPP/blob/1841fe44dee1308fc592c2086b0fd2c06634ecb5/scripts/artifacts/locServicesconfig.py)
  - [`scripts/artifacts/waze.py`](https://github.com/abrignoni/iLEAPP/blob/1841fe44dee1308fc592c2086b0fd2c06634ecb5/scripts/artifacts/waze.py)
- Lab write-up: lab.sectratek.com/open-source/ileapp-2574/ (published with the Lab website)

## What it reads

Calendar.sqlitedb (the four time conversions in Calendar Events now leave a value Python cannot hold blank instead of raising), the locationd and routined location-services lists (the Routine.bundle entry is read under both of its key forms), and the Waze artifacts (a helper returns the main database file when it is present and nothing when only sidecar files are present).

Report artifacts (3):

- Calendar Events (changed)
- Location services configuration artifacts (changed)
- Waze artifacts (changed)

## Fixtures

Copied from the pull request at commit `1841fe44`. All values are synthetic and invented. Licence: as the upstream repository.

How they were made (from the pull request): Built by scripts/synthetic_schema_drift.py: a fabricated Calendar.sqlitedb reduced to the columns the artifacts read (three events, one with a creation date that renders as year 0000, and one birthday), with example.invalid addresses. The location and Waze changes are covered by unit tests in scripts/.

Data files (zip archives shaped like an extraction, one set per test case):

| Name | What it is | How made |
| --- | --- | --- |
| `fixtures/data/calendarAll/testdata.calendarAll.<artifact>.case_synthetic.zip` (3 files, 109 KB) | Synthetic. A fabricated Calendar.sqlitedb (iOS 26 layout, reduced to the columns the calendar artifacts read) built by admin/test/scripts/synthetic_schema_drift.py: three events, one of them with a creation_date SQLite renders as year 0000, and one birthday. | Built by `synthetic_schema_drift.py` |
| `fixtures/data/locServicesconfig/testdata.locServicesconfig.locServicesConfig*.case_synthetic.zip` | Synthetic. A fabricated plist holding the Routine.bundle entry under the newer p&lt;path&gt;: key form, built by admin/test/scripts/synthetic_schema_drift.py with fixed dates; cut with make_test_data.py. | Built by `synthetic_schema_drift.py` |

Scripts (the generators that build the synthetic files, and the unit tests that use them):

| Name | What it is | How made |
| --- | --- | --- |
| `fixtures/scripts/synthetic_schema_drift.py` | Generator that builds the synthetic fixture data | Written for the pull request |
| `fixtures/scripts/test_calendar_year_zero.py` | Unit tests for the parser, as added by the pull request | Written for the pull request |
| `fixtures/scripts/test_loc_services_*.py` | Unit tests for the parser, as added by the pull request | Written for the pull request |
| `fixtures/scripts/test_waze_user_db_search.py` | Unit tests for the parser, as added by the pull request | Written for the pull request |

Also not copied: the expected-output snapshots under `admin/test/results/` and the case descriptors `admin/test/cases/testdata.*.json`. They carry upstream commit metadata and are in the upstream pull request; running the parser on a fixture regenerates the output.

## Try it

From a checkout of abrignoni/iLEAPP, run the tool on one of the fixture zips (the output folder must already exist):

```
python ileapp.py -t zip -i <path to a fixture zip> -o <path to an existing output folder>
```

The fixtures are zip files shaped like an extraction, so they are read like any zip extraction. The upstream test harness uses the same files; with the zips in place under `admin/test/cases/data/` it is run per module:

```
python admin/test/scripts/run_test_cases.py --module calendarAll
python admin/test/scripts/run_test_cases.py --module locServicesconfig
```

See the upstream README for current options and for installing the requirements.

## What it does not prove

Use of the calendar, location or Waze feature is not shown. Not every blank in these artifacts is a read failure.

## Provenance

- Fixtures: copied unchanged from abrignoni/iLEAPP pull request 2574 at commit `1841fe44`. They are synthetic with invented values and were checked for e-mail addresses, phone-number-like strings, device identifiers and file paths before copying. Licence: as the upstream repository.
- The pull request was reviewed and merged by the maintainers of iLEAPP, to whom the project belongs. Source: <https://github.com/abrignoni/iLEAPP/pull/2574>.
- Author: Daniel Kwaku Ntiamoah Addai, SectraTEK Lab.
- This README is licensed CC BY 4.0.
