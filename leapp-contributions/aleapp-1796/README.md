# Usage, settings and boot history from bug reports

Author: Daniel Kwaku Ntiamoah Addai, SectraTEK Lab. Contribution to ALEAPP, pull request 1796. State: Merged on October 26, 2026.

A bug report records which apps came to the foreground, why recent processes ended, what each setting held and why the phone last started. ALEAPP listed those parts as not read. This contribution adds five tables for them, each with a stated rule for its times and a source line for every row.

## Links

- Pull request: <https://github.com/abrignoni/ALEAPP/pull/1796>
- Parser source in the upstream repository (abrignoni/ALEAPP, at the commit of the pull request):
  - [`scripts/artifacts/bugreportActivity.py`](https://github.com/abrignoni/ALEAPP/blob/1a123f30126341f931eeab2951854b9867397c8d/scripts/artifacts/bugreportActivity.py)
  - [`scripts/artifacts/bugreportDevice.py`](https://github.com/abrignoni/ALEAPP/blob/1a123f30126341f931eeab2951854b9867397c8d/scripts/artifacts/bugreportDevice.py)
  - [`scripts/dumpstate_reader.py`](https://github.com/abrignoni/ALEAPP/blob/1a123f30126341f931eeab2951854b9867397c8d/scripts/dumpstate_reader.py)
- Lab write-up: lab.sectratek.com/open-source/aleapp-1796/ (published with the Lab website)

## What it reads

The same bug report text as the earlier reader, now through readers registered for five sections: usage statistics events, application exit info, settings (system, secure and global, per user), the settings change log, and the boot reason history. Printed times are kept beside any UTC value.

Report artifacts (5):

- Bug Report - Usage Events
- Bug Report - Process Exit Info
- Bug Report - Settings
- Bug Report - Settings Changes
- Bug Report - Boot Reasons

## Fixtures

Copied from the pull request at commit `1a123f30`. All values are synthetic and invented. Licence: as the upstream repository.

How they were made (from the pull request): Synthetic bug report zips in the Android 16 and Android 10 layouts with invented values. The generator is the one added with ALEAPP #1795 (scripts/bugreport_fixture.py in that folder); this pull request adds the unit tests in scripts/test_bugreport_activity.py.

Data files (zip archives shaped like an extraction, one set per test case):

| Name | What it is | How made |
| --- | --- | --- |
| `fixtures/data/bugreportActivity/testdata.bugreportActivity.<artifact>.casesynthetic_a10.zip` (5 files, 260 KB) | Synthetic Android 10 style bug report text (bugreport-*.txt, CRLF line endings): userId instead of appId, package-level firstInstallTime, no installer line when none is set, 2009-01-01 00:00:00 placeholder stamps. | See the note above |
| `fixtures/data/bugreportActivity/testdata.bugreportActivity.<artifact>.casesynthetic_a16.zip` (5 files, 387 KB) | Synthetic Android 16 style bug report text (dumpstate.txt) with two Android users: 22 image packages that carry a first-scan time burst and a placeholder timeStamp, an updated system app with a hidden system copy, user apps, a sideloaded app. | See the note above |
| `fixtures/data/bugreportActivity/testdata.bugreportActivity.<artifact>.casesynthetic_cut.zip` (5 files, 269 KB) | Synthetic bug report text cut inside the package service dump, which ends with the DUMP TIMEOUT marker and has no trailer, and no later section. Invented values. | See the note above |
| `fixtures/data/bugreportActivity/testdata.bugreportActivity.<artifact>.casesynthetic_empty.zip` (5 files, 1 KB) | Synthetic bug report text with the banner and no sections. Invented values. | See the note above |
| `fixtures/data/bugreportActivity/testdata.bugreportActivity.<artifact>.casesynthetic_not_a_report.zip` (5 files, 7 KB) | Two files that match the path patterns but carry no dumpstate banner (a text and a block of arbitrary bytes): neither is read and no rows are reported. Invented values. | See the note above |
| `fixtures/data/bugreportActivity/testdata.bugreportActivity.<artifact>.casesynthetic_odd_bytes.zip` (5 files, 291 KB) | Synthetic bug report text with a byte order mark, invalid UTF-8 bytes, a NUL, a lone carriage return and a form feed inside values, and no time zone property: control characters are shown as spaces and no UTC is given. Invented values. | See the note above |
| `fixtures/data/bugreportActivity/testdata.bugreportActivity.<artifact>.casesynthetic_two_reports.zip` (5 files, 551 KB) | Two synthetic bug report texts in two folders (Android 16 style in Asia/Kolkata and Android 10 style in America/Sao_Paulo): both are read and the Source File column tells their rows apart. Invented values. | See the note above |
| `fixtures/data/bugreportActivity/testdata.bugreportActivity.<artifact>.casesynthetic_zip_on_device.zip` (5 files, 30 KB) | Synthetic bug report zip as the Shell app keeps it on the device (data/user_de/0/com.android.shell/files/bugreports/bugreport-*.zip), with main_entry.txt and the main text inside; device zone Asia/Kolkata. Invented values. | See the note above |

Scripts (the generators that build the synthetic files, and the unit tests that use them):

| Name | What it is | How made |
| --- | --- | --- |
| `fixtures/scripts/test_bugreport_activity.py` | Unit tests for the parser, as added by the pull request | Written for the pull request |

Also not copied: the expected-output snapshots under `admin/test/results/` and the case descriptors `admin/test/cases/testdata.*.json`. They carry upstream commit metadata and are in the upstream pull request; running the parser on a fixture regenerates the output.

## Try it

From a checkout of abrignoni/ALEAPP, run the tool on one of the fixture zips (the output folder must already exist):

```
python aleapp.py -t zip -i <path to a fixture zip> -o <path to an existing output folder>
```

The fixtures are zip files shaped like an extraction, so they are read like any zip extraction. The upstream test harness uses the same files; with the zips in place under `admin/test/cases/data/` it is run per module:

```
python admin/test/scripts/run_test_cases.py --module bugreportActivity
```

See the upstream README for current options and for installing the requirements.

## What it does not prove

A usage event is not shown to be caused by a person. An exit row does not say who or what ended a process. A setting row does not say who set the value or when. An entry missing from a list is not shown never to have happened.

## Provenance

- Fixtures: copied unchanged from abrignoni/ALEAPP pull request 1796 at commit `1a123f30`. They are synthetic with invented values and were checked for e-mail addresses, phone-number-like strings, device identifiers and file paths before copying. Licence: as the upstream repository.
- The pull request was reviewed and merged by the maintainers of ALEAPP, to whom the project belongs. Source: <https://github.com/abrignoni/ALEAPP/pull/1796>.
- Author: Daniel Kwaku Ntiamoah Addai, SectraTEK Lab.
- This README is licensed CC BY 4.0.
