# What Messages Keeps After Edits, Unsends and Deletes

Author: Daniel Kwaku Ntiamoah Addai, SectraTEK Lab. Contribution to iLEAPP, pull request 2576. State: Merged on October 25, 2026.

A message list shows rows. It does not show that a row is a reaction, an earlier version, a message taken back or an answer to another message. This contribution reads those fields from the Messages database and states exactly what was stored.

## Links

- Pull request: <https://github.com/abrignoni/iLEAPP/pull/2576>
- Parser source in the upstream repository (abrignoni/iLEAPP, at the commit of the pull request):
  - [`scripts/artifacts/smsAppPayloads.py`](https://github.com/abrignoni/iLEAPP/blob/5b5b7e3d7eb4db6057cc01c1f0de9bad28bdcc40/scripts/artifacts/smsAppPayloads.py)
  - [`scripts/artifacts/smsEdits.py`](https://github.com/abrignoni/iLEAPP/blob/5b5b7e3d7eb4db6057cc01c1f0de9bad28bdcc40/scripts/artifacts/smsEdits.py)
  - [`scripts/artifacts/smsReactions.py`](https://github.com/abrignoni/iLEAPP/blob/5b5b7e3d7eb4db6057cc01c1f0de9bad28bdcc40/scripts/artifacts/smsReactions.py)
  - [`scripts/artifacts/smsRecentlyDeleted.py`](https://github.com/abrignoni/iLEAPP/blob/5b5b7e3d7eb4db6057cc01c1f0de9bad28bdcc40/scripts/artifacts/smsRecentlyDeleted.py)
  - [`scripts/artifacts/smsReplies.py`](https://github.com/abrignoni/iLEAPP/blob/5b5b7e3d7eb4db6057cc01c1f0de9bad28bdcc40/scripts/artifacts/smsReplies.py)
  - [`scripts/sms_deep.py`](https://github.com/abrignoni/iLEAPP/blob/5b5b7e3d7eb4db6057cc01c1f0de9bad28bdcc40/scripts/sms_deep.py)
- Lab write-up: lab.sectratek.com/open-source/ileapp-2576/ (published with the Lab website)

## What it reads

sms.db (Library/SMS): reactions, edit history, unsent message parts, inline replies, Recently Deleted messages and message parts, link previews and iMessage app messages. The existing messages module is untouched, and each table says what the database stored and nothing about who acted.

Report artifacts (8):

- SMS & iMessage - Link Previews
- SMS & iMessage - iMessage App Messages
- SMS & iMessage - Edit History
- SMS & iMessage - Unsent Message Parts
- SMS & iMessage - Reactions
- SMS & iMessage - Recently Deleted Messages
- SMS & iMessage - Recently Deleted Message Parts
- SMS & iMessage - Inline Replies

## Fixtures

Copied from the pull request at commit `5b5b7e3d`. All values are synthetic and invented. Licence: as the upstream repository.

How they were made (from the pull request): Built by scripts/synthetic_sms_deep.py: a fabricated sms.db in the iOS 26 layout with reserved 555-01xx handles, fixed sentences and fixed dates.

Data files (zip archives shaped like an extraction, one set per test case):

| Name | What it is | How made |
| --- | --- | --- |
| `fixtures/data/smsAppPayloads/testdata.smsAppPayloads.<artifact>.case_synthetic.zip` (2 files, 136 KB) | Synthetic. A fabricated Messages database (sms.db, iOS 26 layout) built by admin/test/scripts/synthetic_sms_deep.py with 555-01xx handles, fixed sentences and fixed dates, cut with make_test_data.py. | Built by `synthetic_sms_deep.py` |
| `fixtures/data/smsEdits/testdata.smsEdits.<artifact>.case_synthetic.zip` (2 files, 136 KB) | Synthetic. A fabricated Messages database (sms.db, iOS 26 layout) built by admin/test/scripts/synthetic_sms_deep.py with 555-01xx handles, fixed sentences and fixed dates, cut with make_test_data.py. | Built by `synthetic_sms_deep.py` |
| `fixtures/data/smsReactions/testdata.smsReactions.smsReactions.case_synthetic.zip` | Synthetic. A fabricated Messages database (sms.db, iOS 26 layout) built by admin/test/scripts/synthetic_sms_deep.py with 555-01xx handles, fixed sentences and fixed dates, cut with make_test_data.py. | Built by `synthetic_sms_deep.py` |
| `fixtures/data/smsRecentlyDeleted/testdata.smsRecentlyDeleted.<artifact>.case_synthetic.zip` (2 files, 136 KB) | Synthetic. A fabricated Messages database (sms.db, iOS 26 layout) built by admin/test/scripts/synthetic_sms_deep.py with 555-01xx handles, fixed sentences and fixed dates, cut with make_test_data.py. | Built by `synthetic_sms_deep.py` |
| `fixtures/data/smsReplies/testdata.smsReplies.smsReplies.case_synthetic.zip` | Synthetic. A fabricated Messages database (sms.db, iOS 26 layout) built by admin/test/scripts/synthetic_sms_deep.py with 555-01xx handles, fixed sentences and fixed dates, cut with make_test_data.py. | Built by `synthetic_sms_deep.py` |

Scripts (the generators that build the synthetic files, and the unit tests that use them):

| Name | What it is | How made |
| --- | --- | --- |
| `fixtures/scripts/synthetic_sms_deep.py` | Generator that builds the synthetic fixture data | Written for the pull request |
| `fixtures/scripts/test_sms_deep_fields.py` | Unit tests for the parser, as added by the pull request | Written for the pull request |

Also not copied: the expected-output snapshots under `admin/test/results/` and the case descriptors `admin/test/cases/testdata.*.json`. They carry upstream commit metadata and are in the upstream pull request; running the parser on a fixture regenerates the output.

## Try it

From a checkout of abrignoni/iLEAPP, run the tool on one of the fixture zips (the output folder must already exist):

```
python ileapp.py -t zip -i <path to a fixture zip> -o <path to an existing output folder>
```

The fixtures are zip files shaped like an extraction, so they are read like any zip extraction. The upstream test harness uses the same files; with the zips in place under `admin/test/cases/data/` it is run per module:

```
python admin/test/scripts/run_test_cases.py --module smsAppPayloads
python admin/test/scripts/run_test_cases.py --module smsEdits
python admin/test/scripts/run_test_cases.py --module smsReactions
python admin/test/scripts/run_test_cases.py --module smsRecentlyDeleted
python admin/test/scripts/run_test_cases.py --module smsReplies
```

See the upstream README for current options and for installing the requirements.

## What it does not prove

Who edited, unsent, reacted or deleted a message, or from which device, is not shown. An opened link is not shown. An empty table is not shown to mean nothing happened.

## Provenance

- Fixtures: copied unchanged from abrignoni/iLEAPP pull request 2576 at commit `5b5b7e3d`. They are synthetic with invented values and were checked for e-mail addresses, phone-number-like strings, device identifiers and file paths before copying. Licence: as the upstream repository.
- The pull request was reviewed and merged by the maintainers of iLEAPP, to whom the project belongs. Source: <https://github.com/abrignoni/iLEAPP/pull/2576>.
- Author: Daniel Kwaku Ntiamoah Addai, SectraTEK Lab.
- This README is licensed CC BY 4.0.
