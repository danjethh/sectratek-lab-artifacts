# Reading WhatsApp Business stores in ALEAPP

Author: Daniel Kwaku Ntiamoah Addai, SectraTEK Lab. Contribution to ALEAPP, pull request 1785. State: In review.

WhatsApp Business keeps its data in its own package folder, which the standard WhatsApp artifacts do not open. This contribution adds artifacts that read it by calling the existing WhatsApp artifacts on the Business paths. It is stated openly that no real Business store has been parsed yet; the fixtures are synthetic.

## Links

- Pull request: <https://github.com/abrignoni/ALEAPP/pull/1785>
- Parser source in the upstream repository (abrignoni/ALEAPP, at the commit of the pull request):
  - [`scripts/artifacts/WhatsApp.py`](https://github.com/abrignoni/ALEAPP/blob/28b0d39ada4aaa4a67eeb793084f869c1cd3127a/scripts/artifacts/WhatsApp.py)
  - [`scripts/artifacts/WhatsAppBusiness.py`](https://github.com/abrignoni/ALEAPP/blob/28b0d39ada4aaa4a67eeb793084f869c1cd3127a/scripts/artifacts/WhatsAppBusiness.py)
- Lab write-up: lab.sectratek.com/open-source/aleapp-1785/ (published with the Lab website)

## What it reads

com.whatsapp.w4b: wa.db and msgstore.db (modern schema with jid_map, and the legacy messages and group_participants layout), plus avatar and media folders and preferences. Nine Business artifacts mirror the nine WhatsApp artifacts of the same name.

Report artifacts (9):

- WhatsApp Business - Contacts
- WhatsApp Business - Call Logs
- WhatsApp Business - Messages
- WhatsApp Business - One To One Messages
- WhatsApp Business - Group Messages
- WhatsApp Business - Group Details
- WhatsApp Business - Channels
- WhatsApp Business - Channel Messages
- WhatsApp Business - User Profile

## Fixtures

Copied from the pull request at commit `28b0d39a`. All values are synthetic and invented. Licence: as the upstream repository.

How they were made (from the pull request): Built by hand with invented values: reserved 555-01xx phone numbers, example identifiers, one avatar file, one media file and preferences, in a modern and a legacy layout.

Data files (zip archives shaped like an extraction, one set per test case):

| Name | What it is | How made |
| --- | --- | --- |
| `fixtures/data/WhatsAppBusiness/testdata.WhatsAppBusiness.<artifact>.casesynthetic_w4b_legacy.zip` (9 files, 187 KB) | Synthetic com.whatsapp.w4b stores (legacy msgstore.db schema: messages and group_participants tables, no jid_map). Built by hand with invented values. | Built by hand |
| `fixtures/data/WhatsAppBusiness/testdata.WhatsAppBusiness.<artifact>.casesynthetic_w4b_modern.zip` (9 files, 385 KB) | Synthetic com.whatsapp.w4b stores (modern msgstore.db schema with jid_map, wa.db, one Avatars file, one media file, preferences). Built by hand with invented values. | Built by hand |

Scripts (the generators that build the synthetic files, and the unit tests that use them):

| Name | What it is | How made |
| --- | --- | --- |
| `fixtures/scripts/test_whatsapp_business.py` | Unit tests for the parser, as added by the pull request | Written for the pull request |

Also not copied: the expected-output snapshots under `admin/test/results/` and the case descriptors `admin/test/cases/testdata.*.json`. They carry upstream commit metadata and are in the upstream pull request; running the parser on a fixture regenerates the output.

## Try it

From a checkout of abrignoni/ALEAPP, run the tool on one of the fixture zips (the output folder must already exist):

```
python aleapp.py -t zip -i <path to a fixture zip> -o <path to an existing output folder>
```

The fixtures are zip files shaped like an extraction, so they are read like any zip extraction. The upstream test harness uses the same files; with the zips in place under `admin/test/cases/data/` it is run per module:

```
python admin/test/scripts/run_test_cases.py --module WhatsAppBusiness
```

See the upstream README for current options and for installing the requirements.

## What it does not prove

Whether WhatsApp Business writes the same files, tables, columns and preference keys as WhatsApp is not shown. Nothing here describes a message in a real case.

## Provenance

- Fixtures: copied unchanged from abrignoni/ALEAPP pull request 1785 at commit `28b0d39a`. They are synthetic with invented values and were checked for e-mail addresses, phone-number-like strings, device identifiers and file paths before copying. Licence: as the upstream repository.
- The pull request is open with the maintainers of ALEAPP, to whom the project belongs, and is in review. Source: <https://github.com/abrignoni/ALEAPP/pull/1785>.
- Author: Daniel Kwaku Ntiamoah Addai, SectraTEK Lab.
- This README is licensed CC BY 4.0.
