# Security, storage, logs and crash records from bug reports

Author: Daniel Kwaku Ntiamoah Addai, SectraTEK Lab. Contribution to ALEAPP, pull request 1819. State: Merged on October 27, 2026.

Was a screen lock set? Was a device administrator active? What did the system log record around a time of interest, and why did the device last restart? An Android bug report holds the evidence. This contribution adds 38 tables and keeps the window of each log visible.

## Links

- Pull request: <https://github.com/abrignoni/ALEAPP/pull/1819>
- Parser source in the upstream repository (abrignoni/ALEAPP, at the commit of the pull request):
  - [`scripts/artifacts/bugreportLogsCrash.py`](https://github.com/abrignoni/ALEAPP/blob/7b57d1dc6f64f84c36d61af0a620e11a617ace32/scripts/artifacts/bugreportLogsCrash.py)
  - [`scripts/artifacts/bugreportSecurityStorage.py`](https://github.com/abrignoni/ALEAPP/blob/7b57d1dc6f64f84c36d61af0a620e11a617ace32/scripts/artifacts/bugreportSecurityStorage.py)
  - [`scripts/dumpstate_logscrash.py`](https://github.com/abrignoni/ALEAPP/blob/7b57d1dc6f64f84c36d61af0a620e11a617ace32/scripts/dumpstate_logscrash.py)
  - [`scripts/dumpstate_reader.py`](https://github.com/abrignoni/ALEAPP/blob/7b57d1dc6f64f84c36d61af0a620e11a617ace32/scripts/dumpstate_reader.py)
  - [`scripts/dumpstate_securitystorage.py`](https://github.com/abrignoni/ALEAPP/blob/7b57d1dc6f64f84c36d61af0a620e11a617ace32/scripts/dumpstate_securitystorage.py)
- Lab write-up: lab.sectratek.com/open-source/aleapp-1819/ (published with the Lab website)

## What it reads

The security, device policy, lock settings, storage and database sections, plus the system, event and kernel logs, ANR thread dumps, tombstones, dropbox entries and reset reasons. A log row keeps the printed time, user, process and thread ids, level, tag and message, with a UTC time added by a stated rule where the report allows it. The kernel log keeps seconds since boot and is not given a clock time.

Report artifacts (38):

- Bug Report - System Log
- Bug Report - Event Log
- Bug Report - Kernel Log
- Bug Report - ANR Trace Threads
- Bug Report - Tombstones
- Bug Report - Dropbox Entries
- Bug Report - Reset Reasons
- Bug Report - Vendor Service Lines
- Bug Report - Device Policy Admins
- Bug Report - Device Policy State
- Bug Report - Device Policies
- Bug Report - Lock Settings Users
- and 26 more; the full list is in the parser source linked above

## Fixtures

Copied from the pull request at commit `7b57d1dc`. All values are synthetic and invented. Licence: as the upstream repository.

How they were made (from the pull request): Built by the generators in scripts/bugreport_logscrash_fixture.py and scripts/bugreport_securitystorage_fixture.py: bug report text in Android 16 and Android 10 layouts with invented values.

Data files (zip archives shaped like an extraction, one set per test case):

| Name | What it is | How made |
| --- | --- | --- |
| `fixtures/data/bugreportLogsCrash/testdata.bugreportLogsCrash.<artifact>.casesynthetic_cut.zip` (8 files, 42 KB) | Synthetic text in which a command was stopped by the platform time limit inside the system log and two vendor service dumps carry a dump timeout marker. Invented values. | See the note above |
| `fixtures/data/bugreportLogsCrash/testdata.bugreportLogsCrash.<artifact>.casesynthetic_empty.zip` (8 files, 1 KB) | Synthetic bug report text that holds the banner and nothing else: every artifact returns no rows. Invented values. | See the note above |
| `fixtures/data/bugreportLogsCrash/testdata.bugreportLogsCrash.<artifact>.casesynthetic_l10.zip` (8 files, 21 KB) | Synthetic Android 10 style bug report text with CRLF line ends: logcat without a uid column, kernel lines with a cpu prefix, a thread dump time without an offset, a dropbox listing with one printed tag, no reset history and no vendor services. Invented values. | See the note above |
| `fixtures/data/bugreportLogsCrash/testdata.bugreportLogsCrash.<artifact>.casesynthetic_l16.zip` (8 files, 41 KB) | Synthetic Android 16 style bug report text (dumpstate.txt) in Europe/Paris: logcat with a uid column in four buffers, an event log, kernel log and last kmsg, thread dumps with nanosecond times and offsets, dropbox listing and printed entries. | See the note above |
| `fixtures/data/bugreportLogsCrash/testdata.bugreportLogsCrash.<artifact>.casesynthetic_not_a_report.zip` (8 files, 5 KB) | Files the patterns match that are not bug reports (no banner, bytes of all values): they are left out and nothing is read. Invented values. | See the note above |
| `fixtures/data/bugreportLogsCrash/testdata.bugreportLogsCrash.<artifact>.casesynthetic_odd_bytes.zip` (8 files, 41 KB) | Synthetic text with a byte order mark, no time zone, invalid UTF-8 bytes, NUL, a lone carriage return and a form feed inside log lines: the pass is not stopped and control characters are shown as spaces. Invented values. | See the note above |
| `fixtures/data/bugreportLogsCrash/testdata.bugreportLogsCrash.<artifact>.casesynthetic_two_reports.zip` (8 files, 79 KB) | Two synthetic bug reports in two folders (a zip with members in Asia/Kolkata and an Android 10 style text in America/Sao_Paulo): both are read and the Source File column tells their rows apart. Invented values. | See the note above |
| `fixtures/data/bugreportLogsCrash/testdata.bugreportLogsCrash.<artifact>.casesynthetic_zip_on_device.zip` (8 files, 61 KB) | Synthetic bug report zip as the Shell app keeps it on the device (Asia/Kolkata), holding the main text, an anr file, text and protobuf tombstones, an empty tombstone, a damaged protobuf and files that are not members of interest. Invented values. | See the note above |
| `fixtures/data/bugreportSecurityStorage/testdata.bugreportSecurityStorage.<artifact>.casesynthetic_cut.zip` (30 files, 361 KB) | Synthetic Android 16 style bug report text in which the dbinfo and knoxguard_service dumps end with a DUMP TIMEOUT line. Invented values. | See the note above |
| `fixtures/data/bugreportSecurityStorage/testdata.bugreportSecurityStorage.<artifact>.casesynthetic_empty.zip` (30 files, 5 KB) | Synthetic bug report text with the banner and no sections. Invented values. | See the note above |
| `fixtures/data/bugreportSecurityStorage/testdata.bugreportSecurityStorage.<artifact>.casesynthetic_new.zip` (30 files, 360 KB) | Synthetic Android 16 style bug report text (dumpstate.txt, device zone Europe/Paris) with the security and storage sections: device policy with two admins, a managed-profile administrator and the policy engine, lock settings with two users and a log. | See the note above |
| `fixtures/data/bugreportSecurityStorage/testdata.bugreportSecurityStorage.<artifact>.casesynthetic_not_a_report.zip` (30 files, 18 KB) | Text files that carry no dumpstate banner (one is binary): nothing is read. Invented values. | See the note above |
| `fixtures/data/bugreportSecurityStorage/testdata.bugreportSecurityStorage.<artifact>.casesynthetic_old.zip` (30 files, 209 KB) | Synthetic Android 10 style bug report text (CRLF line ends, device zone Asia/Kolkata): an empty admin list, the short lock settings dump, the older biometric JSON, a trust manager with wall-clock events, df without inodes, the short mount service. | See the note above |
| `fixtures/data/bugreportSecurityStorage/testdata.bugreportSecurityStorage.<artifact>.casesynthetic_two_reports.zip` (30 files, 562 KB) | Two synthetic bug report texts in one extraction (Android 16 style in zone Asia/Kolkata and Android 10 style in zone America/Sao_Paulo). Invented values. | See the note above |

Scripts (the generators that build the synthetic files, and the unit tests that use them):

| Name | What it is | How made |
| --- | --- | --- |
| `fixtures/scripts/bugreport_logscrash_fixture.py` | Generator that builds the synthetic fixture data | Written for the pull request |
| `fixtures/scripts/bugreport_securitystorage_fixture.py` | Generator that builds the synthetic fixture data | Written for the pull request |
| `fixtures/scripts/test_bugreport_logscrash.py` | Unit tests for the parser, as added by the pull request | Written for the pull request |
| `fixtures/scripts/test_bugreport_securitystorage.py` | Unit tests for the parser, as added by the pull request | Written for the pull request |

Also not copied: the expected-output snapshots under `admin/test/results/` and the case descriptors `admin/test/cases/testdata.*.json`. They carry upstream commit metadata and are in the upstream pull request; running the parser on a fixture regenerates the output.

## Try it

From a checkout of abrignoni/ALEAPP, run the tool on one of the fixture zips (the output folder must already exist):

```
python aleapp.py -t zip -i <path to a fixture zip> -o <path to an existing output folder>
```

The fixtures are zip files shaped like an extraction, so they are read like any zip extraction. The upstream test harness uses the same files; with the zips in place under `admin/test/cases/data/` it is run per module:

```
python admin/test/scripts/run_test_cases.py --module bugreportLogsCrash
python admin/test/scripts/run_test_cases.py --module bugreportSecurityStorage
```

See the upstream README for current options and for installing the requirements.

## What it does not prove

A setting is not shown to have been chosen by a person or at a given time. An empty or late-starting log or crash table is not shown to mean nothing happened. Lock secrets and ADB keys are not in a bug report.

## Provenance

- Fixtures: copied unchanged from abrignoni/ALEAPP pull request 1819 at commit `7b57d1dc`. They are synthetic with invented values and were checked for e-mail addresses, phone-number-like strings, device identifiers and file paths before copying. Licence: as the upstream repository.
- The pull request was reviewed and merged by the maintainers of ALEAPP, to whom the project belongs. Source: <https://github.com/abrignoni/ALEAPP/pull/1819>.
- Author: Daniel Kwaku Ntiamoah Addai, SectraTEK Lab.
- This README is licensed CC BY 4.0.
