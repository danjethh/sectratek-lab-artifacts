# Reading ManagedSettings Stores in a Sysdiagnose

Author: Daniel Kwaku Ntiamoah Addai, SectraTEK Lab. Contribution to iLEAPP, pull request 2522. State: Merged on October 20, 2026.

A sysdiagnose holds the stores behind Screen Time and Family Controls restrictions, and nothing read them. These two artifacts report each stored key, the directory of stores and the version, and state what the files cannot show.

## Links

- Pull request: <https://github.com/abrignoni/iLEAPP/pull/2522>
- Parser source in the upstream repository (abrignoni/iLEAPP, at the commit of the pull request):
  - [`scripts/artifacts/managedSettings.py`](https://github.com/abrignoni/iLEAPP/blob/5b4ecf512798a728ee1f3e4dc64023a9c312dcdd/scripts/artifacts/managedSettings.py)
- Lab write-up: lab.sectratek.com/open-source/ileapp-2522/ (published with the Lab website)

## What it reads

logs/ManagedSettings/*.plist: ManagedSettings - Settings gives one row per top-level key of each store file, each component effective-settings file and the user effective-settings file; ManagedSettings - Store Directory gives the entries of SettingRecords.plist and the values of DataVersion.plist.

Report artifacts (2):

- ManagedSettings - Settings
- ManagedSettings - Store Directory

## Fixtures

Copied from the pull request at commit `5b4ecf51`. All values are synthetic and invented. Licence: as the upstream repository.

How they were made (from the pull request): Built by scripts/synthetic_managed_settings.py: fabricated ManagedSettings trees with com.example.* identifiers, generated UUIDs and fabricated key material, in the iOS 27 and iOS 26 store naming. Two further fixture sets in the pull request are derived from devices and are not copied here.

Data files (zip archives shaped like an extraction, one set per test case):

| Name | What it is | How made |
| --- | --- | --- |
| `fixtures/data/managedSettings/testdata.managedSettings.<artifact>.case_synthetic_ios26.zip` (2 files, 31 KB) | Synthetic. A fabricated logs/ManagedSettings tree (com.example.* identifiers, generated UUIDs) with the iOS 26.6 store names (Default, SafariStore, UserSafetyStore, UserSafety, DeviceActivityStore), built by admin/test/scripts/synthetic_managed_settings.py. | Built by `synthetic_managed_settings.py` |
| `fixtures/data/managedSettings/testdata.managedSettings.<artifact>.case_synthetic_ios27.zip` (2 files, 40 KB) | Synthetic. A fabricated logs/ManagedSettings tree (com.example.* identifiers, SYNTH-CAT-* categories, generated UUIDs, fabricated key material) with the iOS 27.0 store names (ContentAndPrivacy, Restrictions, defaultGroup, downtime, scheduleDowntime, bedtime. | Built by `synthetic_managed_settings.py` |

Scripts (the generators that build the synthetic files, and the unit tests that use them):

| Name | What it is | How made |
| --- | --- | --- |
| `fixtures/scripts/synthetic_managed_settings.py` | Generator that builds the synthetic fixture data | Written for the pull request |
| `fixtures/scripts/test_managed_settings.py` | Unit tests for the parser, as added by the pull request | Written for the pull request |

Not copied:

- `testdata.managedSettings.managedSettings.case_ios26_sanitized.zip` (10 KB): not copied, see the upstream PR (a sanitized set that is not obviously synthetic).
- `testdata.managedSettings.managedSettings.case_ios27_sanitized.zip` (23 KB): not copied, see the upstream PR (a sanitized set that is not obviously synthetic).
- `testdata.managedSettings.managedSettingsStores.case_ios26_sanitized.zip` (10 KB): not copied, see the upstream PR (a sanitized set that is not obviously synthetic).
- `testdata.managedSettings.managedSettingsStores.case_ios27_sanitized.zip` (23 KB): not copied, see the upstream PR (a sanitized set that is not obviously synthetic).

Also not copied: the expected-output snapshots under `admin/test/results/` and the case descriptors `admin/test/cases/testdata.*.json`. They carry upstream commit metadata and are in the upstream pull request; running the parser on a fixture regenerates the output.

## Try it

From a checkout of abrignoni/iLEAPP, run the tool on one of the fixture zips (the output folder must already exist):

```
python ileapp.py -t zip -i <path to a fixture zip> -o <path to an existing output folder>
```

The fixtures are zip files shaped like an extraction, so they are read like any zip extraction. The upstream test harness uses the same files; with the zips in place under `admin/test/cases/data/` it is run per module:

```
python admin/test/scripts/run_test_cases.py --module managedSettings
```

See the upstream README for current options and for installing the requirements.

## What it does not prove

A person is not shown to have set a restriction, who set it, or when. A feature is not shown to be off because a key is false or absent.

## Provenance

- Fixtures: copied unchanged from abrignoni/iLEAPP pull request 2522 at commit `5b4ecf51`. They are synthetic with invented values and were checked for e-mail addresses, phone-number-like strings, device identifiers and file paths before copying. Licence: as the upstream repository.
- The pull request was reviewed and merged by the maintainers of iLEAPP, to whom the project belongs. Source: <https://github.com/abrignoni/iLEAPP/pull/2522>.
- Author: Daniel Kwaku Ntiamoah Addai, SectraTEK Lab.
- This README is licensed CC BY 4.0.
