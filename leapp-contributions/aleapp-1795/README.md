# Reading Android bug reports in a single pass

Author: Daniel Kwaku Ntiamoah Addai, SectraTEK Lab. Contribution to ALEAPP, pull request 1795. State: Merged on October 26, 2026.

An Android bug report zip holds one long text file (dumpstate) with build properties, the package list and a section for every system service. ALEAPP staged the zip but had no reader for that text, so an examiner got no rows about the device, its apps or their times. This contribution adds a one-pass reader and four tables. Each table keeps the line number of every row, and the Sections table says which parts of the text no table presents.

## Links

- Pull request: <https://github.com/abrignoni/ALEAPP/pull/1795>
- Parser source in the upstream repository (abrignoni/ALEAPP, at the commit of the pull request):
  - [`scripts/artifacts/bugreportDevice.py`](https://github.com/abrignoni/ALEAPP/blob/7b3d6f3de3845d8d41b00c7ecba4bfd81575cbe8/scripts/artifacts/bugreportDevice.py)
  - [`scripts/dumpstate_reader.py`](https://github.com/abrignoni/ALEAPP/blob/7b3d6f3de3845d8d41b00c7ecba4bfd81575cbe8/scripts/dumpstate_reader.py)
- Lab write-up: lab.sectratek.com/open-source/aleapp-1795/ (published with the Lab website)

## What it reads

The main text of an Android bug report (dumpstate.txt, bugreport-*.txt, or the text inside a bugreport zip), confirmed by its dumpstate banner before reading. Device Facts reads the header and a list of build and system properties. Sections lists every section the text opens, with line range, printed duration and any dump timeout marker. Installed Packages reads one row per package block (version, code path, flags, installer, users). Package Times reads firstInstallTime, lastUpdateTime and timeStamp as printed, with a UTC value only when the report records its zone.

Report artifacts (4):

- Bug Report - Device Facts
- Bug Report - Sections
- Bug Report - Installed Packages
- Bug Report - Package Times

## Fixtures

Copied from the pull request at commit `7b3d6f3d`. All values are synthetic and invented. Licence: as the upstream repository.

How they were made (from the pull request): Built by the generator in scripts/bugreport_fixture.py: bug report text laid out like Android 16 and Android 10 reports (two users, placeholder times, a cut dump, an empty file, a file that is not a report, odd bytes, two reports in one zip), with invented values and package names under com.example.*.

Data files (zip archives shaped like an extraction, one set per test case):

| Name | What it is | How made |
| --- | --- | --- |
| `fixtures/data/bugreportDevice/testdata.bugreportDevice.<artifact>.casesynthetic_a10.zip` (4 files, 208 KB) | Synthetic Android 10 style bug report text (bugreport-*.txt, CRLF line endings): userId instead of appId, package-level firstInstallTime, no installer line when none is set, 2009-01-01 00:00:00 placeholder stamps. | Built by `bugreport_fixture.py` |
| `fixtures/data/bugreportDevice/testdata.bugreportDevice.<artifact>.casesynthetic_a16.zip` (4 files, 309 KB) | Synthetic Android 16 style bug report text (dumpstate.txt) with two Android users: 22 image packages that carry a first-scan time burst and a placeholder timeStamp, an updated system app with a hidden system copy, user apps, a sideloaded app. | Built by `bugreport_fixture.py` |
| `fixtures/data/bugreportDevice/testdata.bugreportDevice.<artifact>.casesynthetic_cut.zip` (4 files, 215 KB) | Synthetic bug report text cut inside the package service dump, which ends with the DUMP TIMEOUT marker and has no trailer, and no later section. Invented values. | Built by `bugreport_fixture.py` |
| `fixtures/data/bugreportDevice/testdata.bugreportDevice.<artifact>.casesynthetic_empty.zip` (4 files, 1 KB) | Synthetic bug report text with the banner and no sections. Invented values. | Built by `bugreport_fixture.py` |
| `fixtures/data/bugreportDevice/testdata.bugreportDevice.<artifact>.casesynthetic_not_a_report.zip` (4 files, 5 KB) | Two files that match the path patterns but carry no dumpstate banner (a text and a block of arbitrary bytes): neither is read and no rows are reported. Invented values. | Built by `bugreport_fixture.py` |
| `fixtures/data/bugreportDevice/testdata.bugreportDevice.<artifact>.casesynthetic_odd_bytes.zip` (4 files, 233 KB) | Synthetic bug report text with a byte order mark, invalid UTF-8 bytes, a NUL, a lone carriage return and a form feed inside values, and no time zone property: control characters are shown as spaces and no UTC is given. Invented values. | Built by `bugreport_fixture.py` |
| `fixtures/data/bugreportDevice/testdata.bugreportDevice.<artifact>.casesynthetic_two_reports.zip` (4 files, 441 KB) | Two synthetic bug report texts in two folders (Android 16 style in Asia/Kolkata and Android 10 style in America/Sao_Paulo): both are read and the Source File column tells their rows apart. Invented values. | Built by `bugreport_fixture.py` |
| `fixtures/data/bugreportDevice/testdata.bugreportDevice.<artifact>.casesynthetic_zip_on_device.zip` (4 files, 24 KB) | Synthetic bug report zip as the Shell app keeps it on the device (data/user_de/0/com.android.shell/files/bugreports/bugreport-*.zip), with main_entry.txt and the main text inside; device zone Asia/Kolkata. Invented values. | Built by `bugreport_fixture.py` |

Scripts (the generators that build the synthetic files, and the unit tests that use them):

| Name | What it is | How made |
| --- | --- | --- |
| `fixtures/scripts/bugreport_fixture.py` | Generator that builds the synthetic fixture data | Written for the pull request |
| `fixtures/scripts/test_bugreport_dumpstate.py` | Unit tests for the parser, as added by the pull request | Written for the pull request |

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

A package time is not shown to be the time anyone installed or updated an app. An app missing from the list is not shown never to have been installed. A section marked not read is not shown to be empty.

## Provenance

- Fixtures: copied unchanged from abrignoni/ALEAPP pull request 1795 at commit `7b3d6f3d`. They are synthetic with invented values and were checked for e-mail addresses, phone-number-like strings, device identifiers and file paths before copying. Licence: as the upstream repository.
- The pull request was reviewed and merged by the maintainers of ALEAPP, to whom the project belongs. Source: <https://github.com/abrignoni/ALEAPP/pull/1795>.
- Author: Daniel Kwaku Ntiamoah Addai, SectraTEK Lab.
- This README is licensed CC BY 4.0.
