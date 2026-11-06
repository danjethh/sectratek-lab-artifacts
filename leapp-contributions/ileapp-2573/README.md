# Reading the Screen Time Store Databases

Author: Daniel Kwaku Ntiamoah Addai, SectraTEK Lab. Contribution to iLEAPP, pull request 2573. State: Merged on October 25, 2026.

Common advice treats the Screen Time database as a record of app usage. On current iPhones the usage tables are mostly empty, and what the stores hold is configuration, an app list and a history of deleted rows. This contribution reads all of it and says what each row is.

## Links

- Pull request: <https://github.com/abrignoni/iLEAPP/pull/2573>
- Parser source in the upstream repository (abrignoni/iLEAPP, at the commit of the pull request):
  - [`scripts/artifacts/screenTimeStore.py`](https://github.com/abrignoni/iLEAPP/blob/f9dae7586a0a8959a2904e329ec4ce0ee46dd141/scripts/artifacts/screenTimeStore.py)
- Lab write-up: lab.sectratek.com/open-source/ileapp-2573/ (published with the Lab website)

## What it reads

RMAdminStore-Local.sqlite and RMAdminStore-Cloud.sqlite (com.apple.remotemanagementd): store and organization settings, users and devices, blueprints with their declaration payloads decoded, the installed-app list, usage tallies, the Core Data change history, and deleted-row entries that keep an identifier after the row is gone. The passcode is reported as present or absent.

Report artifacts (8):

- Screen Time Store - Settings
- Screen Time Store - Organization Settings
- Screen Time Store - Users and Devices
- Screen Time Store - Blueprints and Configurations
- Screen Time Store - Installed Apps
- Screen Time Store - Usage
- Screen Time Store - Change History
- Screen Time Store - Deleted Rows

## Fixtures

Copied from the pull request at commit `f9dae758`. All values are synthetic and invented. Licence: as the upstream repository.

How they were made (from the pull request): Built by scripts/synthetic_screen_time_store.py: a fabricated Local and Cloud store pair for a managed child profile (populated usage blocks, an undecodable payload, deleted-row entries) and an unmanaged pair, with com.example.* identifiers and example.invalid addresses.

Data files (zip archives shaped like an extraction, one set per test case):

| Name | What it is | How made |
| --- | --- | --- |
| `fixtures/data/screenTimeStore/testdata.screenTimeStore.<artifact>.case_synthetic_managed_child.zip` (8 files, 1.3 MB) | Synthetic. A fabricated RMAdminStore-Local.sqlite and RMAdminStore-Cloud.sqlite pair (com.example.* identifiers, an example.invalid account, SYNTH-CAT-* categories) for a managed child profile: populated usage blocks. | Built by `synthetic_screen_time_store.py` |
| `fixtures/data/screenTimeStore/testdata.screenTimeStore.<artifact>.case_synthetic_plain_unmanaged.zip` (8 files, 1.3 MB) | Synthetic. The same generator with the unmanaged shape seen on real iOS 26 stores: one user with no account, Screen Time off, no usage rows, no installed-app list and an empty cloud store. | Built by `synthetic_screen_time_store.py` |

Scripts (the generators that build the synthetic files, and the unit tests that use them):

| Name | What it is | How made |
| --- | --- | --- |
| `fixtures/scripts/synthetic_screen_time_store.py` | Generator that builds the synthetic fixture data | Written for the pull request |
| `fixtures/scripts/test_screen_time_store.py` | Unit tests for the parser, as added by the pull request | Written for the pull request |

Also not copied: the expected-output snapshots under `admin/test/results/` and the case descriptors `admin/test/cases/testdata.*.json`. They carry upstream commit metadata and are in the upstream pull request; running the parser on a fixture regenerates the output.

## Try it

From a checkout of abrignoni/iLEAPP, run the tool on one of the fixture zips (the output folder must already exist):

```
python ileapp.py -t zip -i <path to a fixture zip> -o <path to an existing output folder>
```

The fixtures are zip files shaped like an extraction, so they are read like any zip extraction. The upstream test harness uses the same files; with the zips in place under `admin/test/cases/data/` it is run per module:

```
python admin/test/scripts/run_test_cases.py --module screenTimeStore
```

See the upstream README for current options and for installing the requirements.

## What it does not prove

A person is not shown to have used a device, set a limit or removed an app. An empty usage table is not shown to mean Screen Time was off.

## Provenance

- Fixtures: copied unchanged from abrignoni/iLEAPP pull request 2573 at commit `f9dae758`. They are synthetic with invented values and were checked for e-mail addresses, phone-number-like strings, device identifiers and file paths before copying. Licence: as the upstream repository.
- The pull request was reviewed and merged by the maintainers of iLEAPP, to whom the project belongs. Source: <https://github.com/abrignoni/iLEAPP/pull/2573>.
- Author: Daniel Kwaku Ntiamoah Addai, SectraTEK Lab.
- This README is licensed CC BY 4.0.
