# Reading app containers from the container manager state

Author: Daniel Kwaku Ntiamoah Addai, SectraTEK Lab. Contribution to iLEAPP, pull request 2509. State: Merged on October 19, 2026.

A recent iPhone sysdiagnose can open cleanly and still give the container report nothing, because the text logs the existing reader depends on are not in the archive. The same information now sits in a JSON file. This contribution reads that file into three reports.

## Links

- Pull request: <https://github.com/abrignoni/iLEAPP/pull/2509>
- Parser source in the upstream repository (abrignoni/iLEAPP, at the commit of the pull request):
  - [`scripts/artifacts/containerManagerState.py`](https://github.com/abrignoni/iLEAPP/blob/127d26ac51a0dc65aaf2dfad283a747c89bed714/scripts/artifacts/containerManagerState.py)
- Lab write-up: lab.sectratek.com/open-source/ileapp-2509/ (published with the Lab website)

## What it reads

logs/ContainerManager/state.json in a sysdiagnose archive, folder or as a standalone file. One section per scope (system and user); each container is a record with an identifier, a directory name, a stored generation number and a directory entry that holds four times (birth, change, modify, last seen) or is null. The reports list records with a directory, records without one, and the registrations.

Report artifacts (3):

- Container Manager State
- Container Manager State - No Directory
- Container Manager State - Registrations

## Fixtures

Copied from the pull request at commit `127d26ac`. All values are synthetic and invented. Licence: as the upstream repository.

How they were made (from the pull request): Built by scripts/synthetic_container_state.py: a fabricated state.json with com.example.* identifiers, generated UUIDs and fixed dates, packed in a sysdiagnose-shaped archive. A second fixture set in the pull request is derived from a device and is not copied here.

Data files (zip archives shaped like an extraction, one set per test case):

| Name | What it is | How made |
| --- | --- | --- |
| `fixtures/data/containerManagerState/testdata.containerManagerState.<artifact>.case_synthetic.zip` (3 files, 478 KB) | Synthetic. A fabricated logs/ContainerManager/state.json (com.example.* identifiers, generated UUIDs and fixed dates) built by admin/test/scripts/synthetic_container_state.py in the ISO-8601 UTC string time format with milliseconds and a Z. | Built by `synthetic_container_state.py` |

Scripts (the generators that build the synthetic files, and the unit tests that use them):

| Name | What it is | How made |
| --- | --- | --- |
| `fixtures/scripts/synthetic_container_state.py` | Generator that builds the synthetic fixture data | Written for the pull request |
| `fixtures/scripts/test_container_manager_state.py` | Unit tests for the parser, as added by the pull request | Written for the pull request |

Not copied:

- `testdata.containerManagerState.containerManagerState.case_ios27_sanitized.zip` (3.8 MB): not copied, see the upstream PR (a sanitized set that is not obviously synthetic).
- `testdata.containerManagerState.containerManagerStateNoDirectory.case_ios27_sanitized.zip` (3.8 MB): not copied, see the upstream PR (a sanitized set that is not obviously synthetic).
- `testdata.containerManagerState.containerManagerStateRegistrations.case_ios27_sanitized.zip` (3.8 MB): not copied, see the upstream PR (a sanitized set that is not obviously synthetic).

Also not copied: the expected-output snapshots under `admin/test/results/` and the case descriptors `admin/test/cases/testdata.*.json`. They carry upstream commit metadata and are in the upstream pull request; running the parser on a fixture regenerates the output.

## Try it

From a checkout of abrignoni/iLEAPP, run the tool on one of the fixture zips (the output folder must already exist):

```
python ileapp.py -t zip -i <path to a fixture zip> -o <path to an existing output folder>
```

The fixtures are zip files shaped like an extraction, so they are read like any zip extraction. The upstream test harness uses the same files; with the zips in place under `admin/test/cases/data/` it is run per module:

```
python admin/test/scripts/run_test_cases.py --module containerManagerState
```

See the upstream README for current options and for installing the requirements.

## What it does not prove

An app is not shown to have been installed, opened or removed. An app without a row is not shown never to have been present. The meaning of the generation value is not established; it is reported as stored.

## Provenance

- Fixtures: copied unchanged from abrignoni/iLEAPP pull request 2509 at commit `127d26ac`. They are synthetic with invented values and were checked for e-mail addresses, phone-number-like strings, device identifiers and file paths before copying. Licence: as the upstream repository.
- The pull request was reviewed and merged by the maintainers of iLEAPP, to whom the project belongs. Source: <https://github.com/abrignoni/iLEAPP/pull/2509>.
- Author: Daniel Kwaku Ntiamoah Addai, SectraTEK Lab.
- This README is licensed CC BY 4.0.
