# Permissions, usage, alarms and notifications from bug reports

Author: Daniel Kwaku Ntiamoah Addai, SectraTEK Lab. Contribution to ALEAPP, pull request 1816. State: Merged on October 27, 2026.

Which apps could use the microphone, and when did one last use it? An Android bug report holds the answer across eight sections of a very long text. This contribution reads those sections into 15 tables and keeps every mode, flag and reason code as the dump printed it.

## Links

- Pull request: <https://github.com/abrignoni/ALEAPP/pull/1816>
- Parser source in the upstream repository (abrignoni/ALEAPP, at the commit of the pull request):
  - [`scripts/artifacts/bugreportPermissions.py`](https://github.com/abrignoni/ALEAPP/blob/cd17cf0d16aa033c4aaf42868744af9f0799892f/scripts/artifacts/bugreportPermissions.py)
  - [`scripts/artifacts/bugreportUsageJobs.py`](https://github.com/abrignoni/ALEAPP/blob/cd17cf0d16aa033c4aaf42868744af9f0799892f/scripts/artifacts/bugreportUsageJobs.py)
  - [`scripts/dumpstate_permissions.py`](https://github.com/abrignoni/ALEAPP/blob/cd17cf0d16aa033c4aaf42868744af9f0799892f/scripts/dumpstate_permissions.py)
  - [`scripts/dumpstate_reader.py`](https://github.com/abrignoni/ALEAPP/blob/cd17cf0d16aa033c4aaf42868744af9f0799892f/scripts/dumpstate_reader.py)
  - [`scripts/dumpstate_usagejobs.py`](https://github.com/abrignoni/ALEAPP/blob/cd17cf0d16aa033c4aaf42868744af9f0799892f/scripts/dumpstate_usagejobs.py)
- Lab write-up: lab.sectratek.com/open-source/aleapp-1816/ (published with the Lab website)

## What it reads

Eight sections of the bug report text. Permissions and app ops: package permission lines, permission definitions, app ops modes and accesses, role holders and permission manager grants. Usage and scheduling: usage intervals and event counts, standby buckets, scheduled jobs, pending alarms, alarm history, notification records, listeners and policy. A UTC column is filled only where the dump gives enough to compute it, and a note column says why it is empty when it is.

Report artifacts (15):

- Bug Report - Package Permissions
- Bug Report - Permission Definitions
- Bug Report - App Ops Modes
- Bug Report - App Ops Accesses
- Bug Report - Role Holders
- Bug Report - Permission Manager Grants
- Bug Report - Usage Intervals
- Bug Report - Usage Interval Event Counts
- Bug Report - Standby Buckets
- Bug Report - Scheduled Jobs
- Bug Report - Pending Alarms
- Bug Report - Alarm History
- and 3 more; the full list is in the parser source linked above

## Fixtures

Copied from the pull request at commit `cd17cf0d`. All values are synthetic and invented. Licence: as the upstream repository.

How they were made (from the pull request): Built by the generators in scripts/bugreport_permissions_fixture.py and scripts/bugreport_usagejobs_fixture.py: bug report text in Android 16 and Android 15 layouts (second users, isolated uid, role and permission manager dumps), with invented values and package names under com.example.*.

Data files (zip archives shaped like an extraction, one set per test case):

| Name | What it is | How made |
| --- | --- | --- |
| `fixtures/data/bugreportPermissions/testdata.bugreportPermissions.<artifact>.casesynthetic_a10.zip` (6 files, 19 KB) | Synthetic Android 10 style bug report text (bugreport-*.txt, CRLF line endings): no tag lines, no capability lines, from uid= watchers, a runtime permissions heading printed after an overlay paths list, ROLE MANAGER STATE, no permissionmgr dump. | See the note above |
| `fixtures/data/bugreportPermissions/testdata.bugreportPermissions.<artifact>.casesynthetic_a15.zip` (6 files, 21 KB) | Synthetic Android 15 style bug report text (dumpstate.txt) with a second user 11: an install permission line that ends with userId=11, the ROLE STATE dump with fallback_enabled lines for two users, a permissionmgr dump. Invented values. | See the note above |
| `fixtures/data/bugreportPermissions/testdata.bugreportPermissions.<artifact>.casesynthetic_a16.zip` (6 files, 20 KB) | Synthetic Android 16 style bug report text (dumpstate.txt) with two Android users (0 and 10): package, hidden system package and shared user permission lines, a permission table, app ops with tag lines, Access, Reject, proxy and Running lines. | See the note above |
| `fixtures/data/bugreportPermissions/testdata.bugreportPermissions.<artifact>.casesynthetic_cut.zip` (6 files, 20 KB) | Synthetic Android 16 style bug report text whose package and appops service dumps end with the DUMP TIMEOUT mark and no duration line: the rows printed before the cut are read and the cut is logged. Invented values. | See the note above |
| `fixtures/data/bugreportPermissions/testdata.bugreportPermissions.<artifact>.casesynthetic_empty.zip` (6 files, 1 KB) | Synthetic bug report text with the banner and no sections. Invented values. | See the note above |
| `fixtures/data/bugreportPermissions/testdata.bugreportPermissions.<artifact>.casesynthetic_no_zone.zip` (6 files, 20 KB) | Synthetic Android 16 style bug report text with no persist.sys.timezone property: Time (UTC) is empty and Time Note says why. Invented values. | See the note above |
| `fixtures/data/bugreportPermissions/testdata.bugreportPermissions.<artifact>.casesynthetic_not_a_report.zip` (6 files, 4 KB) | Two files that match the path patterns but carry no dumpstate banner (a text and a block of arbitrary bytes): nothing is read. Invented values. | See the note above |
| `fixtures/data/bugreportPermissions/testdata.bugreportPermissions.<artifact>.casesynthetic_odd_bytes.zip` (6 files, 20 KB) | Synthetic Android 16 style bug report text with a byte order mark, invalid UTF-8 bytes, a NUL and a lone carriage return inside permission lines: the pass is not stopped and the characters are shown as spaces. Invented values. | See the note above |
| `fixtures/data/bugreportPermissions/testdata.bugreportPermissions.<artifact>.casesynthetic_two_reports.zip` (6 files, 38 KB) | Two synthetic bug report texts in two folders (Android 16 style in Asia/Kolkata and Android 10 style in America/Sao_Paulo): both are read and the Source File column tells their rows apart. Invented values. | See the note above |
| `fixtures/data/bugreportUsageJobs/testdata.bugreportUsageJobs.<artifact>.casesynthetic_a10.zip` (9 files, 54 KB) | Synthetic Android 10 style bug report text (bugreport-*.txt, CRLF line endings): usage statistics in the service form (formatted wall-clock text, indented App Standby States) and the checkin form, jobs without namespaces, alarm batches. | See the note above |
| `fixtures/data/bugreportUsageJobs/testdata.bugreportUsageJobs.<artifact>.casesynthetic_a16.zip` (9 files, 60 KB) | Synthetic Android 16 style bug report text (dumpstate.txt) with two Android users: usage statistics in the CHECKIN USAGESTATS section as epoch milliseconds with a User N App Standby States list, jobs with namespaces and a recently completed list. | See the note above |
| `fixtures/data/bugreportUsageJobs/testdata.bugreportUsageJobs.<artifact>.casesynthetic_cut.zip` (9 files, 42 KB) | Synthetic Android 16 style bug report text whose usagestats, jobscheduler, alarm and notification dumps end with the DUMP TIMEOUT marker. Invented values. | See the note above |
| `fixtures/data/bugreportUsageJobs/testdata.bugreportUsageJobs.<artifact>.casesynthetic_empty.zip` (9 files, 2 KB) | Synthetic bug report text with the banner and no sections. Invented values. | See the note above |
| `fixtures/data/bugreportUsageJobs/testdata.bugreportUsageJobs.<artifact>.casesynthetic_no_zone.zip` (9 files, 51 KB) | Synthetic Android 10 style bug report text that records no time zone: wall-clock texts get no UTC value and a note, offsets from the alarm dump still give UTC. Invented values. | See the note above |
| `fixtures/data/bugreportUsageJobs/testdata.bugreportUsageJobs.<artifact>.casesynthetic_not_a_report.zip` (9 files, 5 KB) | Two files that match the path patterns but carry no dumpstate banner (a text and a block of arbitrary bytes). Invented values. | See the note above |
| `fixtures/data/bugreportUsageJobs/testdata.bugreportUsageJobs.<artifact>.casesynthetic_odd_bytes.zip` (9 files, 60 KB) | Synthetic bug report text with a byte order mark, invalid UTF-8 bytes, a NUL, a lone carriage return and a form feed inside alarm tags and notification text, and no time zone. Invented values. | See the note above |
| `fixtures/data/bugreportUsageJobs/testdata.bugreportUsageJobs.<artifact>.casesynthetic_two_reports.zip` (9 files, 112 KB) | Two synthetic bug report texts in two folders (Android 16 style in Asia/Kolkata and Android 10 style in America/Sao_Paulo). Invented values. | See the note above |
| `fixtures/data/bugreportUsageJobs/testdata.bugreportUsageJobs.<artifact>.casesynthetic_zip_on_device.zip` (9 files, 65 KB) | Synthetic bug report zip as the Shell app keeps it on the device (data/user_de/0/com.android.shell/files/bugreports), holding an Android 16 style text in the Asia/Kolkata zone. Invented values. | See the note above |

Scripts (the generators that build the synthetic files, and the unit tests that use them):

| Name | What it is | How made |
| --- | --- | --- |
| `fixtures/scripts/bugreport_permissions_fixture.py` | Generator that builds the synthetic fixture data | Written for the pull request |
| `fixtures/scripts/bugreport_usagejobs_fixture.py` | Generator that builds the synthetic fixture data | Written for the pull request |
| `fixtures/scripts/test_bugreport_permissions.py` | Unit tests for the parser, as added by the pull request | Written for the pull request |
| `fixtures/scripts/test_bugreport_usagejobs.py` | Unit tests for the parser, as added by the pull request | Written for the pull request |

Also not copied: the expected-output snapshots under `admin/test/results/` and the case descriptors `admin/test/cases/testdata.*.json`. They carry upstream commit metadata and are in the upstream pull request; running the parser on a fixture regenerates the output.

## Try it

From a checkout of abrignoni/ALEAPP, run the tool on one of the fixture zips (the output folder must already exist):

```
python aleapp.py -t zip -i <path to a fixture zip> -o <path to an existing output folder>
```

The fixtures are zip files shaped like an extraction, so they are read like any zip extraction. The upstream test harness uses the same files; with the zips in place under `admin/test/cases/data/` it is run per module:

```
python admin/test/scripts/run_test_cases.py --module bugreportPermissions
python admin/test/scripts/run_test_cases.py --module bugreportUsageJobs
```

See the upstream README for current options and for installing the requirements.

## What it does not prove

An app is not shown to have used a permission, an alarm to have fired, a job to have run, or a person to have seen a notification. An entry missing from a dump is not shown never to have happened.

## Provenance

- Fixtures: copied unchanged from abrignoni/ALEAPP pull request 1816 at commit `cd17cf0d`. They are synthetic with invented values and were checked for e-mail addresses, phone-number-like strings, device identifiers and file paths before copying. Licence: as the upstream repository.
- The pull request was reviewed and merged by the maintainers of ALEAPP, to whom the project belongs. Source: <https://github.com/abrignoni/ALEAPP/pull/1816>.
- Author: Daniel Kwaku Ntiamoah Addai, SectraTEK Lab.
- This README is licensed CC BY 4.0.
