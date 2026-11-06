# Network, radio and telephony state from bug reports

Author: Daniel Kwaku Ntiamoah Addai, SectraTEK Lab. Contribution to ALEAPP, pull request 1817. State: Merged on October 27, 2026.

Which Wi-Fi networks did a phone know, which interfaces and apps carried data, and what did Bluetooth, NFC, USB and the SIM do? An Android bug report records all of it in a dozen layouts. This contribution reads those layouts into 37 tables and shows numbers such as result codes and class codes as stored.

## Links

- Pull request: <https://github.com/abrignoni/ALEAPP/pull/1817>
- Parser source in the upstream repository (abrignoni/ALEAPP, at the commit of the pull request):
  - [`scripts/artifacts/bugreportNetwork.py`](https://github.com/abrignoni/ALEAPP/blob/f4d6d15a8ab2aa401d1705b38eacb997d9ed0de6/scripts/artifacts/bugreportNetwork.py)
  - [`scripts/artifacts/bugreportRadios.py`](https://github.com/abrignoni/ALEAPP/blob/f4d6d15a8ab2aa401d1705b38eacb997d9ed0de6/scripts/artifacts/bugreportRadios.py)
  - [`scripts/dumpstate_network.py`](https://github.com/abrignoni/ALEAPP/blob/f4d6d15a8ab2aa401d1705b38eacb997d9ed0de6/scripts/dumpstate_network.py)
  - [`scripts/dumpstate_radios.py`](https://github.com/abrignoni/ALEAPP/blob/f4d6d15a8ab2aa401d1705b38eacb997d9ed0de6/scripts/dumpstate_radios.py)
  - [`scripts/dumpstate_reader.py`](https://github.com/abrignoni/ALEAPP/blob/f4d6d15a8ab2aa401d1705b38eacb997d9ed0de6/scripts/dumpstate_reader.py)
- Lab write-up: lab.sectratek.com/open-source/aleapp-1817/ (published with the Lab website)

## What it reads

The network, Wi-Fi, Bluetooth, NFC, USB and telephony sections of the bug report text: saved networks, connection events, scan results, state machine records, usage buckets, policy entries, paired devices, NFC services and logs, USB state, SIM subscriptions and carrier settings. Each row is what the dump printed for one entry.

Report artifacts (37):

- Bug Report - Wi-Fi Saved Networks
- Bug Report - Wi-Fi Connection Events
- Bug Report - Wi-Fi Current State
- Bug Report - Wi-Fi Scan Results
- Bug Report - Wi-Fi State Machine Records
- Bug Report - Wi-Fi Service Log
- Bug Report - Network Usage Buckets
- Bug Report - Network Policy UID Entries
- Bug Report - Network Policy Settings
- Bug Report - Network Policy Events
- Bug Report - Connected Networks
- Bug Report - Network Interfaces
- and 25 more; the full list is in the parser source linked above

## Fixtures

Copied from the pull request at commit `f4d6d15a`. All values are synthetic and invented. Licence: as the upstream repository.

How they were made (from the pull request): Built by the generators in scripts/bugreport_network_fixture.py and scripts/bugreport_radios_fixture.py: bug report text in Android 16, 15 and 10 layouts with invented network names, device addresses and subscriptions.

Data files (zip archives shaped like an extraction, one set per test case):

| Name | What it is | How made |
| --- | --- | --- |
| `fixtures/data/bugreportNetwork/testdata.bugreportNetwork.<artifact>.casesynthetic_a10.zip` (20 files, 118 KB) | Synthetic Android 10 style bug report text (bugreport-*.txt, CRLF line endings): Wi-Fi entries with creation and update times and a connect choice, the compact CHECKIN NETSTATS form, Dev and Xt stats with a second counter set. | See the note above |
| `fixtures/data/bugreportNetwork/testdata.bugreportNetwork.<artifact>.casesynthetic_a16.zip` (20 files, 144 KB) | Synthetic Android 16 style bug report text (dumpstate.txt) with the network sections: three saved Wi-Fi networks (one marked current, one disabled, one with a comma in the SSID) and a stray entry outside the block, connection events with unpadded times. | See the note above |
| `fixtures/data/bugreportNetwork/testdata.bugreportNetwork.<artifact>.casesynthetic_cut.zip` (20 files, 144 KB) | Synthetic Android 16 style bug report text whose netpolicy service dump ends with the DUMP TIMEOUT marker and has no trailer: the rows are read and the cut is logged once. Invented values. | See the note above |
| `fixtures/data/bugreportNetwork/testdata.bugreportNetwork.<artifact>.casesynthetic_empty.zip` (20 files, 6 KB) | Synthetic bug report text with the banner and no sections. Invented values. | See the note above |
| `fixtures/data/bugreportNetwork/testdata.bugreportNetwork.<artifact>.casesynthetic_not_a_report.zip` (20 files, 26 KB) | Two files that match the path patterns but carry no dumpstate banner (a text and a block of arbitrary bytes): neither is read and no rows are reported. Invented values. | See the note above |
| `fixtures/data/bugreportNetwork/testdata.bugreportNetwork.<artifact>.casesynthetic_odd_bytes.zip` (20 files, 144 KB) | Synthetic bug report text with a byte order mark, an invalid UTF-8 byte, a NUL, a lone carriage return and a form feed inside values, and no time zone property: control characters are shown as spaces and no UTC is given. Invented values. | See the note above |
| `fixtures/data/bugreportNetwork/testdata.bugreportNetwork.<artifact>.casesynthetic_two_reports.zip` (20 files, 260 KB) | Two synthetic bug report texts in two folders (Android 16 style in Asia/Kolkata and Android 10 style in America/Sao_Paulo): both are read and the Source File column tells their rows apart. Invented values. | See the note above |
| `fixtures/data/bugreportNetwork/testdata.bugreportNetwork.<artifact>.casesynthetic_zip_on_device.zip` (20 files, 155 KB) | Synthetic bug report zip as the Shell app keeps it on the device (data/user_de/0/com.android.shell/files/bugreports/bugreport-*.zip), with main_entry.txt and the main text inside; device zone Asia/Kolkata. Invented values. | See the note above |
| `fixtures/data/bugreportRadios/testdata.bugreportRadios.<artifact>.casesynthetic_a10.zip` (17 files, 83 KB) | Synthetic Android 10 style bug report text (bugreport-*.txt, CRLF line endings) with the older Bluetooth layout (middle octets masked), the NFC dump without event log, the usb service dump. | See the note above |
| `fixtures/data/bugreportRadios/testdata.bugreportRadios.<artifact>.casesynthetic_a15.zip` (17 files, 93 KB) | Synthetic Android 15 style bug report text (dumpstate.txt) with the usb, telephony.registry, telecom, Bluetooth and NFC service dumps: bonded devices with no class, connection events, a USB event list, registered phone accounts. | See the note above |
| `fixtures/data/bugreportRadios/testdata.bugreportRadios.<artifact>.casesynthetic_a16.zip` (17 files, 89 KB) | Synthetic Android 16 style bug report text (dumpstate.txt) with the Bluetooth manager dump with masked bonded devices, link key types, enable log, adapter state records and scan mode changes, the NFC dump with its event log. | See the note above |
| `fixtures/data/bugreportRadios/testdata.bugreportRadios.<artifact>.casesynthetic_cut.zip` (17 files, 89 KB) | Synthetic bug report text in which the platform stopped waiting for the Bluetooth manager and the NFC service (DUMP TIMEOUT markers) and the USB LOG section has no duration line. Invented values. | See the note above |
| `fixtures/data/bugreportRadios/testdata.bugreportRadios.<artifact>.casesynthetic_empty.zip` (17 files, 3 KB) | Synthetic bug report text with the banner and no sections. Invented values. | See the note above |

Scripts (the generators that build the synthetic files, and the unit tests that use them):

| Name | What it is | How made |
| --- | --- | --- |
| `fixtures/scripts/bugreport_network_fixture.py` | Generator that builds the synthetic fixture data | Written for the pull request |
| `fixtures/scripts/bugreport_radios_fixture.py` | Generator that builds the synthetic fixture data | Written for the pull request |
| `fixtures/scripts/test_bugreport_network.py` | Unit tests for the parser, as added by the pull request | Written for the pull request |
| `fixtures/scripts/test_bugreport_radios.py` | Unit tests for the parser, as added by the pull request | Written for the pull request |

Also not copied: the expected-output snapshots under `admin/test/results/` and the case descriptors `admin/test/cases/testdata.*.json`. They carry upstream commit metadata and are in the upstream pull request; running the parser on a fixture regenerates the output.

## Try it

From a checkout of abrignoni/ALEAPP, run the tool on one of the fixture zips (the output folder must already exist):

```
python aleapp.py -t zip -i <path to a fixture zip> -o <path to an existing output folder>
```

The fixtures are zip files shaped like an extraction, so they are read like any zip extraction. The upstream test harness uses the same files; with the zips in place under `admin/test/cases/data/` it is run per module:

```
python admin/test/scripts/run_test_cases.py --module bugreportNetwork
python admin/test/scripts/run_test_cases.py --module bugreportRadios
```

See the upstream README for current options and for installing the requirements.

## What it does not prove

A row is not shown to mean a person joined a network, paired a device or used a USB connection. No destinations, message bodies or call content are in a bug report. A missing table is not shown to mean a quiet radio.

## Provenance

- Fixtures: copied unchanged from abrignoni/ALEAPP pull request 1817 at commit `f4d6d15a`. They are synthetic with invented values and were checked for e-mail addresses, phone-number-like strings, device identifiers and file paths before copying. Licence: as the upstream repository.
- The pull request was reviewed and merged by the maintainers of ALEAPP, to whom the project belongs. Source: <https://github.com/abrignoni/ALEAPP/pull/1817>.
- Author: Daniel Kwaku Ntiamoah Addai, SectraTEK Lab.
- This README is licensed CC BY 4.0.
