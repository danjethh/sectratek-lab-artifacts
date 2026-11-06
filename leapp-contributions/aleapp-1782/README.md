# Reading every Android user's database

Author: Daniel Kwaku Ntiamoah Addai, SectraTEK Lab. Contribution to ALEAPP, pull request 1782. State: Merged on October 25, 2026.

When a phone has a second Android user, an artifact that takes the first database it finds can report the wrong user's data. This contribution makes four artifacts read every matching database, once per user, and names the user in an appended column. A second view of one file, such as an app folder reached through two paths, is read once.

## Links

- Pull request: <https://github.com/abrignoni/ALEAPP/pull/1782>
- Parser source in the upstream repository (abrignoni/ALEAPP, at the commit of the pull request):
  - [`scripts/artifacts/frosting.py`](https://github.com/abrignoni/ALEAPP/blob/d1e24e1950f758da2a9acb0f7ab8c1b0fb3ba7bb/scripts/artifacts/frosting.py)
  - [`scripts/artifacts/googleCalendar.py`](https://github.com/abrignoni/ALEAPP/blob/d1e24e1950f758da2a9acb0f7ab8c1b0fb3ba7bb/scripts/artifacts/googleCalendar.py)
  - [`scripts/artifacts/settingsSearch.py`](https://github.com/abrignoni/ALEAPP/blob/d1e24e1950f758da2a9acb0f7ab8c1b0fb3ba7bb/scripts/artifacts/settingsSearch.py)
  - [`scripts/artifacts/smyfilesRecents.py`](https://github.com/abrignoni/ALEAPP/blob/d1e24e1950f758da2a9acb0f7ab8c1b0fb3ba7bb/scripts/artifacts/smyfilesRecents.py)
  - [`scripts/artifacts/storagePathViews.py`](https://github.com/abrignoni/ALEAPP/blob/d1e24e1950f758da2a9acb0f7ab8c1b0fb3ba7bb/scripts/artifacts/storagePathViews.py)
- Lab write-up: lab.sectratek.com/open-source/aleapp-1782/ (published with the Lab website)

## What it reads

frosting.db (Play Store app updates), calendar.db (calendar provider), search_index.db (Settings search) and myfiles.db and FileInfo.db (My Files recent files). The user is taken from the folder the database sits in, and the shared helper is scripts/artifacts/storagePathViews.py.

Report artifacts (7):

- App Updates (Frosting.db)
- Calendar - Events
- Calendar - Calendars
- Google Calendar App Events
- Android Settings Search
- My Files - Recent Files
- My Files - Recent Files (FileInfo)

## Fixtures

Copied from the pull request at commit `d1e24e19`. All values are synthetic and invented. Licence: as the upstream repository.

How they were made (from the pull request): Synthetic databases with invented values, laid out for a primary user and a second user and for the same file reached through two storage paths; the unit test is scripts/test_multi_user_first_match.py.

Data files (zip archives shaped like an extraction, one set per test case):

| Name | What it is | How made |
| --- | --- | --- |
| `fixtures/data/frosting/testdata.frosting.frosting.casesynthetic_a16.zip` | Synthetic frosting.db with three invented packages for the primary user. | See the note above |
| `fixtures/data/googleCalendar/testdata.googleCalendar.<artifact>.casesynthetic_a16.zip` (2 files, 24 KB) | Synthetic calendar.db with one calendar and two invented events. | See the note above |
| `fixtures/data/settingsSearch/testdata.settingsSearch.get_settingsSearch.casesynthetic_a16.zip` | Synthetic search_index.db with two invented saved queries. | See the note above |
| `fixtures/data/smyfilesRecents/testdata.smyfilesRecents.<artifact>.casesynthetic_a16.zip` (2 files, 16 KB) | Synthetic My Files FileInfo.db with two invented recent files. | See the note above |

Scripts (the generators that build the synthetic files, and the unit tests that use them):

| Name | What it is | How made |
| --- | --- | --- |
| `fixtures/scripts/test_multi_user_first_match.py` | Unit tests for the parser, as added by the pull request | Written for the pull request |

Also not copied: the expected-output snapshots under `admin/test/results/` and the case descriptors `admin/test/cases/testdata.*.json`. They carry upstream commit metadata and are in the upstream pull request; running the parser on a fixture regenerates the output.

## Try it

From a checkout of abrignoni/ALEAPP, run the tool on one of the fixture zips (the output folder must already exist):

```
python aleapp.py -t zip -i <path to a fixture zip> -o <path to an existing output folder>
```

The fixtures are zip files shaped like an extraction, so they are read like any zip extraction. The upstream test harness uses the same files; with the zips in place under `admin/test/cases/data/` it is run per module:

```
python admin/test/scripts/run_test_cases.py --module frosting
python admin/test/scripts/run_test_cases.py --module googleCalendar
python admin/test/scripts/run_test_cases.py --module settingsSearch
python admin/test/scripts/run_test_cases.py --module smyfilesRecents
```

See the upstream README for current options and for installing the requirements.

## What it does not prove

A user number is not shown to say who used the phone: it names the storage the database sits in. Other artifacts that take the first match were not audited.

## Provenance

- Fixtures: copied unchanged from abrignoni/ALEAPP pull request 1782 at commit `d1e24e19`. They are synthetic with invented values and were checked for e-mail addresses, phone-number-like strings, device identifiers and file paths before copying. Licence: as the upstream repository.
- The pull request was reviewed and merged by the maintainers of ALEAPP, to whom the project belongs. Source: <https://github.com/abrignoni/ALEAPP/pull/1782>.
- Author: Daniel Kwaku Ntiamoah Addai, SectraTEK Lab.
- This README is licensed CC BY 4.0.
