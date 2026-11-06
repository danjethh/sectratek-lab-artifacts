# Bluetooth file transfers from btopp.db

Author: Daniel Kwaku Ntiamoah Addai, SectraTEK Lab. Contribution to ALEAPP, pull request 1781. State: Merged on October 25, 2026.

When a phone sends or receives a file over Bluetooth, the Bluetooth app can leave a record in a small database. ALEAPP had no reader for it. This contribution adds one and states plainly that most databases examined held no rows.

## Links

- Pull request: <https://github.com/abrignoni/ALEAPP/pull/1781>
- Parser source in the upstream repository (abrignoni/ALEAPP, at the commit of the pull request):
  - [`scripts/artifacts/bluetoothOpp.py`](https://github.com/abrignoni/ALEAPP/blob/340bf959a5686f652ab2a3bcd2bc6e20a719b68d/scripts/artifacts/bluetoothOpp.py)
- Lab write-up: lab.sectratek.com/open-source/aleapp-1781/ (published with the Lab website)

## What it reads

btopp.db in the Bluetooth app folder, under either Bluetooth package name, in device encrypted storage: one report row per row of the btopp table. The timestamp is converted to UTC; every other column is shown as stored, and the notes record what the Android source says the codes mean.

Report artifacts (1):

- Bluetooth File Transfers

## Fixtures

Copied from the pull request at commit `340bf959`. All values are synthetic and invented. Licence: as the upstream repository.

How they were made (from the pull request): Synthetic btopp.db files with invented values: two Android users plus a second storage view, a database under the Google Bluetooth module package, and an empty table.

Data files (zip archives shaped like an extraction, one set per test case):

| Name | What it is | How made |
| --- | --- | --- |
| `fixtures/data/bluetoothOpp/testdata.bluetoothOpp.get_bluetooth_opp.casesynthetic_btopp_empty.zip` | Synthetic btopp.db with an empty btopp table. | See the note above |
| `fixtures/data/bluetoothOpp/testdata.bluetoothOpp.get_bluetooth_opp.casesynthetic_btopp_google_module.zip` | Synthetic btopp.db under com.google.android.bluetooth, one row, invented values. | See the note above |
| `fixtures/data/bluetoothOpp/testdata.bluetoothOpp.get_bluetooth_opp.casesynthetic_btopp_users.zip` | Synthetic btopp.db for Android users 0 and 150 plus a second storage view of user 0 (data_mirror), invented values. | See the note above |

Also not copied: the expected-output snapshots under `admin/test/results/` and the case descriptors `admin/test/cases/testdata.*.json`. They carry upstream commit metadata and are in the upstream pull request; running the parser on a fixture regenerates the output.

## Try it

From a checkout of abrignoni/ALEAPP, run the tool on one of the fixture zips (the output folder must already exist):

```
python aleapp.py -t zip -i <path to a fixture zip> -o <path to an existing output folder>
```

The fixtures are zip files shaped like an extraction, so they are read like any zip extraction. The upstream test harness uses the same files; with the zips in place under `admin/test/cases/data/` it is run per module:

```
python admin/test/scripts/run_test_cases.py --module bluetoothOpp
```

See the upstream README for current options and for installing the requirements.

## What it does not prove

A row is not shown to mean the file reached the other device. An empty table is not shown to mean no file was ever sent. Quick Share, Nearby Share and messaging apps are not covered.

## Provenance

- Fixtures: copied unchanged from abrignoni/ALEAPP pull request 1781 at commit `340bf959`. They are synthetic with invented values and were checked for e-mail addresses, phone-number-like strings, device identifiers and file paths before copying. Licence: as the upstream repository.
- The pull request was reviewed and merged by the maintainers of ALEAPP, to whom the project belongs. Source: <https://github.com/abrignoni/ALEAPP/pull/1781>.
- Author: Daniel Kwaku Ntiamoah Addai, SectraTEK Lab.
- This README is licensed CC BY 4.0.
