# Reading SIM slot logs and network lookups

Author: Daniel Kwaku Ntiamoah Addai, SectraTEK Lab. Contribution to ALEAPP, pull request 1787. State: In review.

Two files of the Android phone app record SIM slot events and network lookups, and neither had a reader. This contribution reads them as stored and names what is not known, such as the meaning of the SIM state names, the response codes and the time zone of the SIM log.

## Links

- Pull request: <https://github.com/abrignoni/ALEAPP/pull/1787>
- Parser source in the upstream repository (abrignoni/ALEAPP, at the commit of the pull request):
  - [`scripts/artifacts/telephonyTrafficStats.py`](https://github.com/abrignoni/ALEAPP/blob/6ccc8682968166ae5d69553f84aa94640f09e91a/scripts/artifacts/telephonyTrafficStats.py)
  - [`scripts/artifacts/uiccLog.py`](https://github.com/abrignoni/ALEAPP/blob/6ccc8682968166ae5d69553f84aa94640f09e91a/scripts/artifacts/uiccLog.py)
- Lab write-up: lab.sectratek.com/open-source/aleapp-1787/ (published with the Lab website)

## What it reads

uicc_log.db (the uicclog table, split into index, state, subscription id and card fields, with the raw line kept; a second artifact joins subscription ids to the siminfo table of telephony.db) and echolocate_system_network_db (the trafficstats table, read by column name because two column orders exist, with a second view grouped by cell).

Report artifacts (4):

- Telephony Network Lookups (trafficstats)
- Telephony Network Lookups, Cells Seen
- UICC Log (SIM Slot Events)
- SIM Subscriptions Seen in UICC Log

## Fixtures

Copied from the pull request at commit `6ccc8682`. All values are synthetic and invented. Licence: as the upstream repository.

How they were made (from the pull request): Synthetic databases with invented values built to the observed schemas: trafficstats databases in both column orders (40 and 30 rows, including odd timestamps), and uicc_log.db and telephony.db combinations with one SIM, two SIMs, an older siminfo layout and no telephony database.

Data files (zip archives shaped like an extraction, one set per test case):

| Name | What it is | How made |
| --- | --- | --- |
| `fixtures/data/telephonyTrafficStats/testdata.telephonyTrafficStats.<artifact>.casesynthetic_trafficstats_a.zip` (2 files, 40 KB) | Synthetic echolocate_system_network_db with networkDetail as the fifth column (NOT NULL), 40 invented rows including no-cell and Wi-Fi-like rows and invented 32-digit address items. | See the note above |
| `fixtures/data/telephonyTrafficStats/testdata.telephonyTrafficStats.<artifact>.casesynthetic_trafficstats_b.zip` (2 files, 24 KB) | Synthetic echolocate_system_network_db with networkDetail as the last, nullable column, 30 invented rows plus a seconds-valued timestamp, a non-numeric timestamp, a zero timestamp, an unparsable address text and an empty one. | See the note above |
| `fixtures/data/telephonyTrafficStats/testdata.telephonyTrafficStats.<artifact>.casesynthetic_trafficstats_data_data.zip` (2 files, 40 KB) | Synthetic echolocate_system_network_db under data/data, the layout the storage-views run restages to check that a second storage view of one file is read once and a second Android user is read as well, invented values. | See the note above |
| `fixtures/data/telephonyTrafficStats/testdata.telephonyTrafficStats.<artifact>.casesynthetic_trafficstats_empty.zip` (2 files, 24 KB) | Synthetic echolocate_system_network_db with an empty trafficstats table; no rows expected. | See the note above |
| `fixtures/data/telephonyTrafficStats/testdata.telephonyTrafficStats.<artifact>.casesynthetic_trafficstats_users.zip` (2 files, 105 KB) | Synthetic echolocate_system_network_db for Android user 0 plus a second storage view of user 0 (data_mirror) and a smaller copy for user 150, invented values. | See the note above |
| `fixtures/data/uiccLog/testdata.uiccLog.<artifact>.casesynthetic_uicc_data_data.zip` (2 files, 37 KB) | Synthetic uicc_log.db and telephony.db under data/data, the layout the storage-views run restages to check that a second storage view of one file is read once and a second Android user is read as well, invented values. | See the note above |
| `fixtures/data/uiccLog/testdata.uiccLog.<artifact>.casesynthetic_uicc_empty.zip` (2 files, 37 KB) | Synthetic uicc_log.db with an empty uicclog table and a telephony.db; no rows expected. | See the note above |
| `fixtures/data/uiccLog/testdata.uiccLog.<artifact>.casesynthetic_uicc_no_telephony_db.zip` (2 files, 24 KB) | Synthetic uicc_log.db with no telephony.db: the log artifact is complete and the SIM details are blank, invented values. | See the note above |
| `fixtures/data/uiccLog/testdata.uiccLog.<artifact>.casesynthetic_uicc_old_siminfo.zip` (2 files, 37 KB) | Synthetic uicc_log.db and a telephony.db whose siminfo table lacks imsi, carrier_id, is_embedded and port columns; the missing columns must read as blank, invented values. | See the note above |
| `fixtures/data/uiccLog/testdata.uiccLog.<artifact>.casesynthetic_uicc_two_sims.zip` (2 files, 37 KB) | Synthetic uicc_log.db (every line format seen, a SIM swap on phone index 0, a subscription id with no siminfo row, an unknown line, a backwards stored time) and a telephony.db with a full siminfo table, invented values. | See the note above |
| `fixtures/data/uiccLog/testdata.uiccLog.<artifact>.casesynthetic_uicc_users.zip` (2 files, 98 KB) | Synthetic uicc_log.db for Android user 0 plus a second storage view of user 0 (data_mirror) and a smaller copy for user 150, with a telephony.db for user 0 only, invented values. | See the note above |

Scripts (the generators that build the synthetic files, and the unit tests that use them):

| Name | What it is | How made |
| --- | --- | --- |
| `fixtures/scripts/test_telephony_trafficstats_uicc.py` | Unit tests for the parser, as added by the pull request | Written for the pull request |

Also not copied: the expected-output snapshots under `admin/test/results/` and the case descriptors `admin/test/cases/testdata.*.json`. They carry upstream commit metadata and are in the upstream pull request; running the parser on a fixture regenerates the output.

## Try it

From a checkout of abrignoni/ALEAPP, run the tool on one of the fixture zips (the output folder must already exist):

```
python aleapp.py -t zip -i <path to a fixture zip> -o <path to an existing output folder>
```

The fixtures are zip files shaped like an extraction, so they are read like any zip extraction. The upstream test harness uses the same files; with the zips in place under `admin/test/cases/data/` it is run per module:

```
python admin/test/scripts/run_test_cases.py --module telephonyTrafficStats
python admin/test/scripts/run_test_cases.py --module uiccLog
```

See the upstream README for current options and for installing the requirements.

## What it does not prove

The SIM state names, the null token, the response codes and the signal value -999 are not given a meaning. The time zone of the SIM log is not established. Address items are not shown to be IP addresses. No data volume or device location is shown.

## Provenance

- Fixtures: copied unchanged from abrignoni/ALEAPP pull request 1787 at commit `6ccc8682`. They are synthetic with invented values and were checked for e-mail addresses, phone-number-like strings, device identifiers and file paths before copying. Licence: as the upstream repository.
- The pull request is open with the maintainers of ALEAPP, to whom the project belongs, and is in review. Source: <https://github.com/abrignoni/ALEAPP/pull/1787>.
- Author: Daniel Kwaku Ntiamoah Addai, SectraTEK Lab.
- This README is licensed CC BY 4.0.
