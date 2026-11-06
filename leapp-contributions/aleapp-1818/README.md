# Accounts, power, location and media from bug reports

Author: Daniel Kwaku Ntiamoah Addai, SectraTEK Lab. Contribution to ALEAPP, pull request 1818. State: Merged on October 27, 2026.

Which accounts were on the phone, when did sync last run, which apps held wake locks, what was running, and what were the sensors, camera and screen doing? An Android bug report records all of it. This contribution adds 59 tables so that each question has a place to look.

## Links

- Pull request: <https://github.com/abrignoni/ALEAPP/pull/1818>
- Parser source in the upstream repository (abrignoni/ALEAPP, at the commit of the pull request):
  - [`scripts/artifacts/bugreportAccountsPower.py`](https://github.com/abrignoni/ALEAPP/blob/fccd7acc99b9d90c7743a52f6b2ffa5411ef01a3/scripts/artifacts/bugreportAccountsPower.py)
  - [`scripts/artifacts/bugreportSensorsMedia.py`](https://github.com/abrignoni/ALEAPP/blob/fccd7acc99b9d90c7743a52f6b2ffa5411ef01a3/scripts/artifacts/bugreportSensorsMedia.py)
  - [`scripts/dumpstate_accountspower.py`](https://github.com/abrignoni/ALEAPP/blob/fccd7acc99b9d90c7743a52f6b2ffa5411ef01a3/scripts/dumpstate_accountspower.py)
  - [`scripts/dumpstate_reader.py`](https://github.com/abrignoni/ALEAPP/blob/fccd7acc99b9d90c7743a52f6b2ffa5411ef01a3/scripts/dumpstate_reader.py)
  - [`scripts/dumpstate_sensorsmedia.py`](https://github.com/abrignoni/ALEAPP/blob/fccd7acc99b9d90c7743a52f6b2ffa5411ef01a3/scripts/dumpstate_sensorsmedia.py)
- Lab write-up: lab.sectratek.com/open-source/aleapp-1818/ (published with the Lab website)

## What it reads

The accounts, sync, backup, battery and power, process, location, sensor, camera, audio, display and input sections of the bug report text. Flags, state bits and sensor values are kept as stored and are not decoded. Where the dump prints a time, the row keeps it as printed and a UTC column is added by a stated rule.

Report artifacts (59):

- Bug Report - Accounts
- Bug Report - Account History
- Bug Report - Account Authenticators
- Bug Report - Account Visibility
- Bug Report - Sync Adapter Status
- Bug Report - Sync Recent History
- Bug Report - Sync Adapter Last Syncs
- Bug Report - Sync Jobs
- Bug Report - Sync State
- Bug Report - Backup State
- Bug Report - Backup Transports
- Bug Report - Backup Package State
- and 47 more; the full list is in the parser source linked above

## Fixtures

Copied from the pull request at commit `fccd7acc`. All values are synthetic and invented. Licence: as the upstream repository.

How they were made (from the pull request): Built by the generators in scripts/bugreport_accountspower_fixture.py and scripts/bugreport_sensorsmedia_fixture.py: bug report text in Android 16 and Android 10 layouts (Europe/Paris zone, two users in the newer layout) with invented accounts and values.

Data files (zip archives shaped like an extraction, one set per test case):

| Name | What it is | How made |
| --- | --- | --- |
| `fixtures/data/bugreportAccountsPower/testdata.bugreportAccountsPower.<artifact>.casesynthetic_a10.zip` (33 files, 260 KB) | Synthetic Android 10 style bug report text (bugreport-*.txt, CRLF line endings) with one user, in the Europe/Paris zone: the same sections in the older shapes (sync entries printed as account/ uN (type uN [authority]). | See the note above |
| `fixtures/data/bugreportAccountsPower/testdata.bugreportAccountsPower.<artifact>.casesynthetic_a16.zip` (33 files, 293 KB) | Synthetic Android 16 style bug report text (dumpstate.txt) with two Android users, in the Europe/Paris zone: accounts with a history table and a visibility list, sync status tables (one with a failure cell), recent sync history, per adapter history. | See the note above |
| `fixtures/data/bugreportAccountsPower/testdata.bugreportAccountsPower.<artifact>.casesynthetic_cut.zip` (33 files, 294 KB) | Synthetic Android 16 style bug report text whose meminfo service dump ends with the DUMP TIMEOUT marker and has no trailer: the rows read before the cut are listed and the cut is logged. Invented values. | See the note above |
| `fixtures/data/bugreportAccountsPower/testdata.bugreportAccountsPower.<artifact>.casesynthetic_empty.zip` (33 files, 6 KB) | Synthetic bug report text with the banner and no sections. Invented values. | See the note above |
| `fixtures/data/bugreportAccountsPower/testdata.bugreportAccountsPower.<artifact>.casesynthetic_not_a_report.zip` (33 files, 20 KB) | Two files that match the path patterns but carry no dumpstate banner (a text and a block of arbitrary bytes): neither is read and no rows are reported. Invented values. | See the note above |
| `fixtures/data/bugreportAccountsPower/testdata.bugreportAccountsPower.<artifact>.casesynthetic_two_reports.zip` (33 files, 544 KB) | Two synthetic bug report texts in two folders (Android 16 style in Asia/Kolkata and Android 10 style in America/Sao_Paulo): both are read and the Source File column tells their rows apart. Invented values. | See the note above |
| `fixtures/data/bugreportSensorsMedia/testdata.bugreportSensorsMedia.<artifact>.casesynthetic_a10.zip` (26 files, 202 KB) | Synthetic Android 10 style bug report text (bugreport-*.txt, CRLF line endings) with the older layouts of the same dumps: Current Location Manager state, clock-time-only sensor events, package= registrations, Audio event log headings. | See the note above |
| `fixtures/data/bugreportSensorsMedia/testdata.bugreportSensorsMedia.<artifact>.casesynthetic_a16.zip` (26 files, 252 KB) | Synthetic Android 12 and later style bug report text (dumpstate.txt) with the base fixture sections plus invented location (providers, listeners, last locations for two users, aggregate usage, event log), location_time_zone_manager, sensorservice (list. | See the note above |
| `fixtures/data/bugreportSensorsMedia/testdata.bugreportSensorsMedia.<artifact>.casesynthetic_cut.zip` (26 files, 249 KB) | Synthetic Android 12 and later style bug report text in which the location and sensorservice dumps end with the DUMP TIMEOUT marker and no duration line. Invented values. | See the note above |
| `fixtures/data/bugreportSensorsMedia/testdata.bugreportSensorsMedia.<artifact>.casesynthetic_empty.zip` (26 files, 7 KB) | Synthetic bug report text with the banner and no sections: every sensors and media artifact has no rows. Invented values. | See the note above |
| `fixtures/data/bugreportSensorsMedia/testdata.bugreportSensorsMedia.<artifact>.casesynthetic_two_reports.zip` (26 files, 448 KB) | Two synthetic bug report texts in two folders (Android 12 and later style in Asia/Kolkata and Android 10 style in America/Sao_Paulo): rows of both are listed with their Source File. Invented values. | See the note above |

Scripts (the generators that build the synthetic files, and the unit tests that use them):

| Name | What it is | How made |
| --- | --- | --- |
| `fixtures/scripts/bugreport_accountspower_fixture.py` | Generator that builds the synthetic fixture data | Written for the pull request |
| `fixtures/scripts/bugreport_sensorsmedia_fixture.py` | Generator that builds the synthetic fixture data | Written for the pull request |
| `fixtures/scripts/test_bugreport_accountspower.py` | Unit tests for the parser, as added by the pull request | Written for the pull request |
| `fixtures/scripts/test_bugreport_sensorsmedia.py` | Unit tests for the parser, as added by the pull request | Written for the pull request |

Also not copied: the expected-output snapshots under `admin/test/results/` and the case descriptors `admin/test/cases/testdata.*.json`. They carry upstream commit metadata and are in the upstream pull request; running the parser on a fixture regenerates the output.

## Try it

From a checkout of abrignoni/ALEAPP, run the tool on one of the fixture zips (the output folder must already exist):

```
python aleapp.py -t zip -i <path to a fixture zip> -o <path to an existing output folder>
```

The fixtures are zip files shaped like an extraction, so they are read like any zip extraction. The upstream test harness uses the same files; with the zips in place under `admin/test/cases/data/` it is run per module:

```
python admin/test/scripts/run_test_cases.py --module bugreportAccountsPower
python admin/test/scripts/run_test_cases.py --module bugreportSensorsMedia
```

See the upstream README for current options and for installing the requirements.

## What it does not prove

Who set up an account, or what an app did with it, is not shown. A wake lock, sensor or camera event is not shown to have been caused by a person. No location history is in a bug report.

## Provenance

- Fixtures: copied unchanged from abrignoni/ALEAPP pull request 1818 at commit `fccd7acc`. They are synthetic with invented values and were checked for e-mail addresses, phone-number-like strings, device identifiers and file paths before copying. Licence: as the upstream repository.
- The pull request was reviewed and merged by the maintainers of ALEAPP, to whom the project belongs. Source: <https://github.com/abrignoni/ALEAPP/pull/1818>.
- Author: Daniel Kwaku Ntiamoah Addai, SectraTEK Lab.
- This README is licensed CC BY 4.0.
