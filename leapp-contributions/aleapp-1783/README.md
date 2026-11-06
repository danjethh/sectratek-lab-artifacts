# Samsung Smart Switch transfer history

Author: Daniel Kwaku Ntiamoah Addai, SectraTEK Lab. Contribution to ALEAPP, pull request 1783. State: Merged on October 25, 2026.

When someone moves to a new Samsung phone, Smart Switch copies their content across and keeps notes about the transfer: what kind of device sent the data, which categories moved and when. ALEAPP did not read those notes. Eight artifacts now do, and each keeps the values as stored.

## Links

- Pull request: <https://github.com/abrignoni/ALEAPP/pull/1783>
- Parser source in the upstream repository (abrignoni/ALEAPP, at the commit of the pull request):
  - [`scripts/artifacts/samsungSmartSwitch.py`](https://github.com/abrignoni/ALEAPP/blob/30ef6b903d18693da31847ff9bc001176566912d/scripts/artifacts/samsungSmartSwitch.py)
- Lab write-up: lab.sectratek.com/open-source/aleapp-1783/ (published with the Lab website)

## What it reads

The Smart Switch app data folder (com.sec.android.easyMover): the History folders (mainDataModel.json, peerDeviceInfo.json, objItems.json), TransferredHistory, and the backup media database (backup_media.db). A session is one history folder, identified by Android user and folder name, which reads as epoch milliseconds and is shown as UTC.

Report artifacts (8):

- Samsung Smart Switch - Transfer Sessions
- Samsung Smart Switch - Transferred Data Categories
- Samsung Smart Switch - Peer App Categories
- Samsung Smart Switch - Peer Accounts
- Samsung Smart Switch - Peer Message Counts
- Samsung Smart Switch - Peer Contact Accounts
- Samsung Smart Switch - Transferred History
- Samsung Smart Switch - Backup Media Table (bkmedia)

## Fixtures

Copied from the pull request at commit `30ef6b90`. All values are synthetic and invented. Licence: as the upstream repository.

How they were made (from the pull request): Built by scripts/smart_switch_fixture.py: a synthetic Smart Switch tree (History folders, TransferredHistory, backup_media.db; user 0, its mirror path and user 10) with invented values.

Data files (zip archives shaped like an extraction, one set per test case):

| Name | What it is | How made |
| --- | --- | --- |
| `fixtures/data/samsungSmartSwitch/testdata.samsungSmartSwitch.<artifact>.synthetic_a16.zip` (8 files, 50 KB) | Synthetic com.sec.android.easyMover tree (Smart Switch History, TransferredHistory and backup_media.db; user 0, its data/user/0 mirror and user 10) built by admin/test/scripts/smart_switch_fixture.py. Invented values, not from a real device. | Built by `smart_switch_fixture.py` |

Scripts (the generators that build the synthetic files, and the unit tests that use them):

| Name | What it is | How made |
| --- | --- | --- |
| `fixtures/scripts/smart_switch_fixture.py` | Generator that builds the synthetic fixture data | Written for the pull request |
| `fixtures/scripts/test_samsung_smart_switch.py` | Unit tests for the parser, as added by the pull request | Written for the pull request |

Also not copied: the expected-output snapshots under `admin/test/results/` and the case descriptors `admin/test/cases/testdata.*.json`. They carry upstream commit metadata and are in the upstream pull request; running the parser on a fixture regenerates the output.

## Try it

From a checkout of abrignoni/ALEAPP, run the tool on one of the fixture zips (the output folder must already exist):

```
python aleapp.py -t zip -i <path to a fixture zip> -o <path to an existing output folder>
```

The fixtures are zip files shaped like an extraction, so they are read like any zip extraction. The upstream test harness uses the same files; with the zips in place under `admin/test/cases/data/` it is run per module:

```
python admin/test/scripts/run_test_cases.py --module samsungSmartSwitch
```

See the upstream README for current options and for installing the requirements.

## What it does not prove

A listed category is not shown to have been transferred in full. A category missing from the list is not shown absent from the other device. The other device's description is not checked against that device.

## Provenance

- Fixtures: copied unchanged from abrignoni/ALEAPP pull request 1783 at commit `30ef6b90`. They are synthetic with invented values and were checked for e-mail addresses, phone-number-like strings, device identifiers and file paths before copying. Licence: as the upstream repository.
- The pull request was reviewed and merged by the maintainers of ALEAPP, to whom the project belongs. Source: <https://github.com/abrignoni/ALEAPP/pull/1783>.
- Author: Daniel Kwaku Ntiamoah Addai, SectraTEK Lab.
- This README is licensed CC BY 4.0.
