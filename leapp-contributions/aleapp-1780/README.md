# Blocked numbers and Android Auto rejected cars

Author: Daniel Kwaku Ntiamoah Addai, SectraTEK Lab. Contribution to ALEAPP, pull request 1780. State: Merged on October 25, 2026.

A phone can hold a list of blocked numbers and a record of cars it has been set up with, and both were easy to miss. This contribution adds a Blocked Numbers reader, reads the rejected cars table of the Android Auto database, and reads one database per Android user.

## Links

- Pull request: <https://github.com/abrignoni/ALEAPP/pull/1780>
- Parser source in the upstream repository (abrignoni/ALEAPP, at the commit of the pull request):
  - [`scripts/artifacts/androidauto.py`](https://github.com/abrignoni/ALEAPP/blob/d7cdebb026995940423ab4889dbf8374ee4f58b9/scripts/artifacts/androidauto.py)
  - [`scripts/artifacts/blockedNumbers.py`](https://github.com/abrignoni/ALEAPP/blob/d7cdebb026995940423ab4889dbf8374ee4f58b9/scripts/artifacts/blockedNumbers.py)
- Lab write-up: lab.sectratek.com/open-source/aleapp-1780/ (published with the Lab website)

## What it reads

blockednumbers.db of the BlockedNumberProvider (the blocked table: ID, number as entered, E.164 form) and carservicedata.db of Android Auto (the allowedcars and rejectedcars tables, 13 columns each). The blocked table has no timestamp, so the artifact has no time column and says so in its notes.

Report artifacts (3):

- Blocked Numbers (new)
- Android Auto - Allowed Cars (changed)
- Android Auto - Rejected Cars (new)

## Fixtures

Copied from the pull request at commit `d7cdebb0`. All values are synthetic and invented. Licence: as the upstream repository.

How they were made (from the pull request): Synthetic databases with invented values, including a second Android user, a second storage view of one file, an older schema without the E.164 column, an empty table, and a car database without a rejected cars table.

Data files (zip archives shaped like an extraction, one set per test case):

| Name | What it is | How made |
| --- | --- | --- |
| `fixtures/data/androidauto/testdata.androidauto.<artifact>.casesynthetic_auto_both.zip` (2 files, 33 KB) | Synthetic carservicedata.db with two allowedcars rows and two rejectedcars rows, invented values. | See the note above |
| `fixtures/data/androidauto/testdata.androidauto.<artifact>.casesynthetic_auto_no_rejected_table.zip` (2 files, 25 KB) | Synthetic carservicedata.db without a rejectedcars table, one allowedcars row, invented values. | See the note above |
| `fixtures/data/blockedNumbers/testdata.blockedNumbers.get_blocked_numbers.casesynthetic_blocked_empty.zip` | Synthetic blockednumbers.db with an empty blocked table. | See the note above |
| `fixtures/data/blockedNumbers/testdata.blockedNumbers.get_blocked_numbers.casesynthetic_blocked_no_e164.zip` | Synthetic blockednumbers.db from an older schema without the e164_number column, invented values. | See the note above |
| `fixtures/data/blockedNumbers/testdata.blockedNumbers.get_blocked_numbers.casesynthetic_blocked_users.zip` | Synthetic blockednumbers.db for Android users 0 and 150 plus a second storage view of user 0 (data_mirror), invented values. | See the note above |

Also not copied: the expected-output snapshots under `admin/test/results/` and the case descriptors `admin/test/cases/testdata.*.json`. They carry upstream commit metadata and are in the upstream pull request; running the parser on a fixture regenerates the output.

## Try it

From a checkout of abrignoni/ALEAPP, run the tool on one of the fixture zips (the output folder must already exist):

```
python aleapp.py -t zip -i <path to a fixture zip> -o <path to an existing output folder>
```

The fixtures are zip files shaped like an extraction, so they are read like any zip extraction. The upstream test harness uses the same files; with the zips in place under `admin/test/cases/data/` it is run per module:

```
python admin/test/scripts/run_test_cases.py --module androidauto
python admin/test/scripts/run_test_cases.py --module blockedNumbers
```

See the upstream README for current options and for installing the requirements.

## What it does not prove

The time a number was blocked is not shown, because the table has no timestamp. A number missing from the table is not shown never to have been blocked. A row in a car table is not shown to mean a completed connection.

## Provenance

- Fixtures: copied unchanged from abrignoni/ALEAPP pull request 1780 at commit `d7cdebb0`. They are synthetic with invented values and were checked for e-mail addresses, phone-number-like strings, device identifiers and file paths before copying. Licence: as the upstream repository.
- The pull request was reviewed and merged by the maintainers of ALEAPP, to whom the project belongs. Source: <https://github.com/abrignoni/ALEAPP/pull/1780>.
- Author: Daniel Kwaku Ntiamoah Addai, SectraTEK Lab.
- This README is licensed CC BY 4.0.
