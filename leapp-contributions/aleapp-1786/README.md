# Reading App Ops history databases in ALEAPP

Author: Daniel Kwaku Ntiamoah Addai, SectraTEK Lab. Contribution to ALEAPP, pull request 1786. State: In review.

Android records which app used the camera, microphone or location in small history databases, and a report read only the last-access file. This contribution reads the databases, applies the write-ahead log, and also reports rows that exist outside the live view.

## Links

- Pull request: <https://github.com/abrignoni/ALEAPP/pull/1786>
- Parser source in the upstream repository (abrignoni/ALEAPP, at the commit of the pull request):
  - [`scripts/artifacts/appOpsHistoryDb.py`](https://github.com/abrignoni/ALEAPP/blob/889bf2d2289129bd63ed50e694aa1a9688752f5d/scripts/artifacts/appOpsHistoryDb.py)
- Lab write-up: lab.sectratek.com/open-source/aleapp-1786/ (published with the Lab website)

## What it reads

app_op_history*.db under system/appops: one report row for each row of app_op_accesses, in time order, after SQLite has applied the log, with stored numbers turned into readable names beside the raw values. A companion artifact reads the main file alone and reports any row that the log-applied view lacks or changes.

Report artifacts (2):

- App Ops Access History (Database)
- App Ops Access History (Database File Only)

## Fixtures

Copied from the pull request at commit `889bf2d2`. All values are synthetic and invented. Licence: as the upstream repository.

How they were made (from the pull request): Built by scripts/appops_history_fixture.py: synthetic App Ops history databases (a short-interval database and a long-interval database with a live write-ahead log that deletes, changes and adds rows) with com.example.* packages, invented uids and times.

Data files (zip archives shaped like an extraction, one set per test case):

| Name | What it is | How made |
| --- | --- | --- |
| `fixtures/data/appOpsHistoryDb/testdata.appOpsHistoryDb.<artifact>.casesynthetic_appops_discrete_a16.zip` (2 files, 2 KB) | Synthetic app_op_history.db in the Android 16.0 release layout (one row per access, no aggregate columns, device id not null); built from the AOSP table definition, Invented values. | Built by `appops_history_fixture.py` |
| `fixtures/data/appOpsHistoryDb/testdata.appOpsHistoryDb.<artifact>.casesynthetic_appops_empty.zip` (2 files, 2 KB) | Synthetic short and long databases with an empty app_op_accesses table. | Built by `appops_history_fixture.py` |
| `fixtures/data/appOpsHistoryDb/testdata.appOpsHistoryDb.<artifact>.casesynthetic_appops_history.zip` (2 files, 5 KB) | Synthetic Android 16 App Ops history databases: a short-interval database with no -wal (user 0 and user 150 uids, camera, microphone, location, a proxied access with attribution flags, an unnamed op. | Built by `appops_history_fixture.py` |
| `fixtures/data/appOpsHistoryDb/testdata.appOpsHistoryDb.appops_history_db.casesynthetic_appops_no_table.zip` | Synthetic database with the right file name but no app_op_accesses table. | Built by `appops_history_fixture.py` |
| `fixtures/data/appOpsHistoryDb/testdata.appOpsHistoryDb.appops_history_db.casesynthetic_appops_odd_values.zip` | Synthetic long-interval database with values the platform does not write: unreadable, negative, second-based and out-of-range times, text in numeric columns, NULLs, unknown uid state and flag bits; Invented values. | Built by `appops_history_fixture.py` |
| `fixtures/data/appOpsHistoryDb/testdata.appOpsHistoryDb.<artifact>.casesynthetic_appops_two_copies.zip` (2 files, 11 KB) | The history fixture twice, under two extraction roots, to check that each copy is read and named by Source File; Invented values. | Built by `appops_history_fixture.py` |
| `fixtures/data/appOpsHistoryDb/testdata.appOpsHistoryDb.<artifact>.casesynthetic_appops_unreadable.zip` (2 files, 4 KB) | Synthetic short-interval database file that is all zero bytes (an extraction can hold files like this) beside a readable long-interval database with its -wal; Invented values. | Built by `appops_history_fixture.py` |

Scripts (the generators that build the synthetic files, and the unit tests that use them):

| Name | What it is | How made |
| --- | --- | --- |
| `fixtures/scripts/appops_history_fixture.py` | Generator that builds the synthetic fixture data | Written for the pull request |
| `fixtures/scripts/test_appops_history_db.py` | Unit tests for the parser, as added by the pull request | Written for the pull request |

Also not copied: the expected-output snapshots under `admin/test/results/` and the case descriptors `admin/test/cases/testdata.*.json`. They carry upstream commit metadata and are in the upstream pull request; running the parser on a fixture regenerates the output.

## Try it

From a checkout of abrignoni/ALEAPP, run the tool on one of the fixture zips (the output folder must already exist):

```
python aleapp.py -t zip -i <path to a fixture zip> -o <path to an existing output folder>
```

The fixtures are zip files shaped like an extraction, so they are read like any zip extraction. The upstream test harness uses the same files; with the zips in place under `admin/test/cases/data/` it is run per module:

```
python admin/test/scripts/run_test_cases.py --module appOpsHistoryDb
```

See the upstream README for current options and for installing the requirements.

## What it does not prove

An app is not shown to have used a sensor, captured anything, or to have been known to the user. A missing row is not shown to mean the app did not use an op. Why a row was removed is not shown.

## Provenance

- Fixtures: copied unchanged from abrignoni/ALEAPP pull request 1786 at commit `889bf2d2`. They are synthetic with invented values and were checked for e-mail addresses, phone-number-like strings, device identifiers and file paths before copying. Licence: as the upstream repository.
- The pull request is open with the maintainers of ALEAPP, to whom the project belongs, and is in review. Source: <https://github.com/abrignoni/ALEAPP/pull/1786>.
- Author: Daniel Kwaku Ntiamoah Addai, SectraTEK Lab.
- This README is licensed CC BY 4.0.
