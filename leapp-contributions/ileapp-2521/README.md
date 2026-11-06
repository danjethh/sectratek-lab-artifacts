# Per-app runtime from the BatteryUI property lists

Author: Daniel Kwaku Ntiamoah Addai, SectraTEK Lab. Contribution to iLEAPP, pull request 2521. State: Merged on October 20, 2026.

A sysdiagnose keeps per-app battery runtime in property lists that no iLEAPP artifact read. The numbers carry no units and the bucket width changes between files, so the unit was tested against the data and the width is reported as stored.

## Links

- Pull request: <https://github.com/abrignoni/iLEAPP/pull/2521>
- Parser source in the upstream repository (abrignoni/iLEAPP, at the commit of the pull request):
  - [`scripts/artifacts/batteryUISysdiagnose.py`](https://github.com/abrignoni/iLEAPP/blob/5498487077255967e285a8fd9cd415edb9b36ff2/scripts/artifacts/batteryUISysdiagnose.py)
- Lab write-up: lab.sectratek.com/open-source/ileapp-2521/ (published with the Lab website)

## What it reads

logs/BatteryUIPlist/BatteryUISysdiagnose.plist and any BatteryUIUpgrade property list. The first artifact has a row for each app entry in each bucket, with the bucket start and end in UTC in the first columns; the second has a row per bucket; the third has a row per file.

Report artifacts (3):

- Battery UI - Per-App Runtime
- Battery UI - Time Buckets
- Battery UI - Snapshots and Upgrade Marker

## Fixtures

Copied from the pull request at commit `54984870`. All values are synthetic and invented. Licence: as the upstream repository.

How they were made (from the pull request): Built by scripts/synthetic_battery_ui.py: fabricated property lists with com.example.* apps and formula-built numbers, in the shape where buckets are one day wide and in the shape with hourly and ten-day buckets. Two further fixture sets in the pull request are derived from devices and are not copied here.

Data files (zip archives shaped like an extraction, one set per test case):

| Name | What it is | How made |
| --- | --- | --- |
| `fixtures/data/batteryUISysdiagnose/testdata.batteryUISysdiagnose.<artifact>.case_synthetic_ios26.zip` (3 files, 34 KB) | Synthetic. A fabricated logs/BatteryUIPlist/BatteryUISysdiagnose.plist (com.example.* apps, formula-built numbers) in the shape where the DayTapKey buckets are one hour wide and the WeekKey bucket ten days wide. | Built by `synthetic_battery_ui.py` |
| `fixtures/data/batteryUISysdiagnose/testdata.batteryUISysdiagnose.<artifact>.case_synthetic_ios27.zip` (3 files, 56 KB) | Synthetic. Fabricated logs/BatteryUIPlist property lists (com.example.* apps, formula-built numbers) in the shape where every bucket is stored one day wide, with a BatteryUIUpgrade file, built by admin/test/scripts/synthetic_battery_ui.py. | Built by `synthetic_battery_ui.py` |

Scripts (the generators that build the synthetic files, and the unit tests that use them):

| Name | What it is | How made |
| --- | --- | --- |
| `fixtures/scripts/synthetic_battery_ui.py` | Generator that builds the synthetic fixture data | Written for the pull request |
| `fixtures/scripts/test_battery_ui_sysdiagnose.py` | Unit tests for the parser, as added by the pull request | Written for the pull request |

Not copied:

- `testdata.batteryUISysdiagnose.batteryUISysdiagnoseApps.case_ios26_sanitized.zip` (85 KB): not copied, see the upstream PR (a sanitized set that is not obviously synthetic).
- `testdata.batteryUISysdiagnose.batteryUISysdiagnoseApps.case_ios27_sanitized.zip` (325 KB): not copied, see the upstream PR (a sanitized set that is not obviously synthetic).
- `testdata.batteryUISysdiagnose.batteryUISysdiagnoseBuckets.case_ios26_sanitized.zip` (85 KB): not copied, see the upstream PR (a sanitized set that is not obviously synthetic).
- `testdata.batteryUISysdiagnose.batteryUISysdiagnoseBuckets.case_ios27_sanitized.zip` (325 KB): not copied, see the upstream PR (a sanitized set that is not obviously synthetic).
- `testdata.batteryUISysdiagnose.batteryUISysdiagnoseSnapshots.case_ios26_sanitized.zip` (85 KB): not copied, see the upstream PR (a sanitized set that is not obviously synthetic).
- `testdata.batteryUISysdiagnose.batteryUISysdiagnoseSnapshots.case_ios27_sanitized.zip` (325 KB): not copied, see the upstream PR (a sanitized set that is not obviously synthetic).

Also not copied: the expected-output snapshots under `admin/test/results/` and the case descriptors `admin/test/cases/testdata.*.json`. They carry upstream commit metadata and are in the upstream pull request; running the parser on a fixture regenerates the output.

## Try it

From a checkout of abrignoni/iLEAPP, run the tool on one of the fixture zips (the output folder must already exist):

```
python ileapp.py -t zip -i <path to a fixture zip> -o <path to an existing output folder>
```

The fixtures are zip files shaped like an extraction, so they are read like any zip extraction. The upstream test harness uses the same files; with the zips in place under `admin/test/cases/data/` it is run per module:

```
python admin/test/scripts/run_test_cases.py --module batteryUISysdiagnose
```

See the upstream README for current options and for installing the requirements.

## What it does not prove

An app is not shown to have been opened or used. An app without a row is not shown not to have run. The meaning of the energy values and qualifiers, and what the stored data duration covers, is not established.

## Provenance

- Fixtures: copied unchanged from abrignoni/iLEAPP pull request 2521 at commit `54984870`. They are synthetic with invented values and were checked for e-mail addresses, phone-number-like strings, device identifiers and file paths before copying. Licence: as the upstream repository.
- The pull request was reviewed and merged by the maintainers of iLEAPP, to whom the project belongs. Source: <https://github.com/abrignoni/iLEAPP/pull/2521>.
- Author: Daniel Kwaku Ntiamoah Addai, SectraTEK Lab.
- This README is licensed CC BY 4.0.
