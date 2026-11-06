# Reading five more sysdiagnose files

Author: Daniel Kwaku Ntiamoah Addai, SectraTEK Lab. Contribution to iLEAPP, pull request 2575. State: Merged on October 25, 2026.

A sysdiagnose holds many small files that answer real questions, such as which apps pair with which websites and which processes were running. Five of them are now read, with ten artifacts, and the notes of each artifact record what the file does not establish.

## Links

- Pull request: <https://github.com/abrignoni/iLEAPP/pull/2575>
- Parser source in the upstream repository (abrignoni/iLEAPP, at the commit of the pull request):
  - [`scripts/artifacts/sdl_brctl.py`](https://github.com/abrignoni/iLEAPP/blob/6a23b076defff32a8d04a5b48f0f25a577923dce/scripts/artifacts/sdl_brctl.py)
  - [`scripts/artifacts/sdl_mc_events.py`](https://github.com/abrignoni/iLEAPP/blob/6a23b076defff32a8d04a5b48f0f25a577923dce/scripts/artifacts/sdl_mc_events.py)
  - [`scripts/artifacts/sdl_network_extension.py`](https://github.com/abrignoni/iLEAPP/blob/6a23b076defff32a8d04a5b48f0f25a577923dce/scripts/artifacts/sdl_network_extension.py)
  - [`scripts/artifacts/sdl_swcutil.py`](https://github.com/abrignoni/iLEAPP/blob/6a23b076defff32a8d04a5b48f0f25a577923dce/scripts/artifacts/sdl_swcutil.py)
  - [`scripts/artifacts/sdl_taskinfo.py`](https://github.com/abrignoni/iLEAPP/blob/6a23b076defff32a8d04a5b48f0f25a577923dce/scripts/artifacts/sdl_taskinfo.py)
- Lab write-up: lab.sectratek.com/open-source/ileapp-2575/ (published with the Lab website)

## What it reads

brctl-container-list.txt and brctl-dump.txt (iCloud Drive containers, version history, sync state), MCSettingsEvents.plist and MCProfileEvents.plist, com.apple.networkextension.plist, swcutil_show.txt (associated domains and settings) and taskinfo.txt. Times are parsed to UTC only where the file states them in UTC.

Report artifacts (10):

- Sysdiagnose - iCloud Drive Containers (brctl)
- Sysdiagnose - iCloud Drive Version History (brctl)
- Sysdiagnose - iCloud Drive Sync State (brctl)
- Sysdiagnose - Managed Configuration Settings Events
- Sysdiagnose - Managed Configuration Profile Events
- Sysdiagnose - Network Extension Configurations
- Sysdiagnose - Network Extension Path Rule Groups
- Sysdiagnose - Associated Domains (swcutil)
- Sysdiagnose - Associated Domains Settings (swcutil)
- Sysdiagnose - Process Task Info

## Fixtures

Copied from the pull request at commit `6a23b076`. All values are synthetic and invented. Licence: as the upstream repository.

How they were made (from the pull request): Built by scripts/synthetic_sysdiagnose_family2.py: fabricated sysdiagnose files with com.example.* identifiers, derived UUIDs and fixed dates, in the printed or property list layout of the tools, packed in a sysdiagnose-shaped archive.

Data files (zip archives shaped like an extraction, one set per test case):

| Name | What it is | How made |
| --- | --- | --- |
| `fixtures/data/sdl_brctl/testdata.sdl_brctl.<artifact>.case_synthetic.zip` (3 files, 9 KB) | Synthetic. Fabricated sysdiagnose files (com.example.* identifiers, derived UUIDs, fixed dates) built by admin/test/scripts/synthetic_sysdiagnose_family2.py in the printed or property list layout of the tools. | Built by `synthetic_sysdiagnose_family2.py` |
| `fixtures/data/sdl_mc_events/testdata.sdl_mc_events.<artifact>.case_synthetic.zip` (2 files, 2 KB) | Synthetic. Fabricated sysdiagnose files (com.example.* identifiers, derived UUIDs, fixed dates) built by admin/test/scripts/synthetic_sysdiagnose_family2.py in the printed or property list layout of the tools. | Built by `synthetic_sysdiagnose_family2.py` |
| `fixtures/data/sdl_network_extension/testdata.sdl_network_extension.<artifact>.case_synthetic.zip` (2 files, 15 KB) | Synthetic. Fabricated sysdiagnose files (com.example.* identifiers, derived UUIDs, fixed dates) built by admin/test/scripts/synthetic_sysdiagnose_family2.py in the printed or property list layout of the tools. | Built by `synthetic_sysdiagnose_family2.py` |
| `fixtures/data/sdl_swcutil/testdata.sdl_swcutil.<artifact>.case_synthetic.zip` (2 files, 6 KB) | Synthetic. Fabricated sysdiagnose files (com.example.* identifiers, derived UUIDs, fixed dates) built by admin/test/scripts/synthetic_sysdiagnose_family2.py in the printed or property list layout of the tools. | Built by `synthetic_sysdiagnose_family2.py` |
| `fixtures/data/sdl_taskinfo/testdata.sdl_taskinfo.taskinfo_processes.case_synthetic.zip` | Synthetic. Fabricated sysdiagnose files (com.example.* identifiers, derived UUIDs, fixed dates) built by admin/test/scripts/synthetic_sysdiagnose_family2.py in the printed or property list layout of the tools. | Built by `synthetic_sysdiagnose_family2.py` |

Scripts (the generators that build the synthetic files, and the unit tests that use them):

| Name | What it is | How made |
| --- | --- | --- |
| `fixtures/scripts/synthetic_sysdiagnose_family2.py` | Generator that builds the synthetic fixture data | Written for the pull request |
| `fixtures/scripts/test_sysdiagnose_family2.py` | Unit tests for the parser, as added by the pull request | Written for the pull request |

Also not copied: the expected-output snapshots under `admin/test/results/` and the case descriptors `admin/test/cases/testdata.*.json`. They carry upstream commit metadata and are in the upstream pull request; running the parser on a fixture regenerates the output.

## Try it

From a checkout of abrignoni/iLEAPP, run the tool on one of the fixture zips (the output folder must already exist):

```
python ileapp.py -t zip -i <path to a fixture zip> -o <path to an existing output folder>
```

The fixtures are zip files shaped like an extraction, so they are read like any zip extraction. The upstream test harness uses the same files; with the zips in place under `admin/test/cases/data/` it is run per module:

```
python admin/test/scripts/run_test_cases.py --module sdl_brctl
python admin/test/scripts/run_test_cases.py --module sdl_mc_events
python admin/test/scripts/run_test_cases.py --module sdl_network_extension
python admin/test/scripts/run_test_cases.py --module sdl_swcutil
python admin/test/scripts/run_test_cases.py --module sdl_taskinfo
```

See the upstream README for current options and for installing the requirements.

## What it does not prove

An app is not shown to be installed now, or anything to have been opened from a domain. A listed process is not shown to have been opened by a person. An iCloud Drive container is not shown to hold files.

## Provenance

- Fixtures: copied unchanged from abrignoni/iLEAPP pull request 2575 at commit `6a23b076`. They are synthetic with invented values and were checked for e-mail addresses, phone-number-like strings, device identifiers and file paths before copying. Licence: as the upstream repository.
- The pull request was reviewed and merged by the maintainers of iLEAPP, to whom the project belongs. Source: <https://github.com/abrignoni/iLEAPP/pull/2575>.
- Author: Daniel Kwaku Ntiamoah Addai, SectraTEK Lab.
- This README is licensed CC BY 4.0.
