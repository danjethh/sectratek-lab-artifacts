# Boot reasons and setup flags, decoded

Author: Daniel Kwaku Ntiamoah Addai, SectraTEK Lab. Contribution to ALEAPP, pull request 1835. State: Merged on October 28, 2026.

The boot reason history of an Android phone sits in a binary property store that a text scan cannot walk, and its setup flags are spread over several files. This contribution decodes the first and gathers the second into one table.

## Links

- Pull request: <https://github.com/abrignoni/ALEAPP/pull/1835>
- Parser source in the upstream repository (abrignoni/ALEAPP, at the commit of the pull request):
  - [`scripts/android_boot_reason.py`](https://github.com/abrignoni/ALEAPP/blob/3463144870a5585efdecc133b80eb50851420546/scripts/android_boot_reason.py)
  - [`scripts/android_setup_flags.py`](https://github.com/abrignoni/ALEAPP/blob/3463144870a5585efdecc133b80eb50851420546/scripts/android_setup_flags.py)
  - [`scripts/artifacts/androidSetupFlags.py`](https://github.com/abrignoni/ALEAPP/blob/3463144870a5585efdecc133b80eb50851420546/scripts/artifacts/androidSetupFlags.py)
  - [`scripts/artifacts/persistentProp.py`](https://github.com/abrignoni/ALEAPP/blob/3463144870a5585efdecc133b80eb50851420546/scripts/artifacts/persistentProp.py)
- Lab write-up: lab.sectratek.com/open-source/aleapp-1835/ (published with the Lab website)

## What it reads

The persistent property store (property/persistent_properties): it is decoded directly, with no protobuf library, into one row per boot reason history line and one for a non-empty persist.sys.boot.reason. Setup Flags reads settings_secure.xml (or its binary ABX form), the settings history JSON files for each user, and the setup properties.

Report artifacts (2):

- Setup Flags (new)
- Persistent Properties - Matched Text Observations (changed)

## Fixtures

Copied from the pull request at commit `34631448`. All values are synthetic and invented. Licence: as the upstream repository.

How they were made (from the pull request): Built by scripts/reset_boot_setup_fixture.py: synthetic settings XML, binary ABX settings, history JSON and a persistent property store with invented values, including a second user and an empty store.

Data files (zip archives shaped like an extraction, one set per test case):

| Name | What it is | How made |
| --- | --- | --- |
| `fixtures/data/androidSetupFlags/testdata.androidSetupFlags.android_setup_flags.casesynthetic_abx.zip` | Synthetic settings files of user 0 in the binary ABX form. Invented values. | Built by `reset_boot_setup_fixture.py` |
| `fixtures/data/androidSetupFlags/testdata.androidSetupFlags.android_setup_flags.casesynthetic_malformed_settings.zip` | Synthetic settings files that cannot be read: cut XML, cut ABX, cut JSON, JSON that is not an object, binary junk. Invented values. | Built by `reset_boot_setup_fixture.py` |
| `fixtures/data/androidSetupFlags/testdata.androidSetupFlags.android_setup_flags.casesynthetic_no_flags.zip` | Synthetic settings files (XML and ABX) without any setup flag and a property store without setup properties. Invented values. | Built by `reset_boot_setup_fixture.py` |
| `fixtures/data/androidSetupFlags/testdata.androidSetupFlags.android_setup_flags.casesynthetic_xml_two_users.zip` | Synthetic settings XML and history JSON of user 0, a second user with the flag set to 0, and a persistent property store with the setup properties. Invented values. | Built by `reset_boot_setup_fixture.py` |
| `fixtures/data/persistentProp/testdata.persistentProp.get_persistentProp.casesynthetic_empty_store.zip` | An empty persistent_properties file. Invented values. | Built by `reset_boot_setup_fixture.py` |
| `fixtures/data/persistentProp/testdata.persistentProp.get_persistentProp.casesynthetic_factory_reset.zip` | Synthetic persistent_properties (protobuf) with a boot reason history that holds a factory_reset entry, a persist.sys.boot.reason value and other properties. Invented values. | Built by `reset_boot_setup_fixture.py` |
| `fixtures/data/persistentProp/testdata.persistentProp.get_persistentProp.casesynthetic_no_factory_reset.zip` | Synthetic persistent_properties with a boot reason history without a factory_reset entry and an empty persist.sys.boot.reason. Invented values. | Built by `reset_boot_setup_fixture.py` |
| `fixtures/data/persistentProp/testdata.persistentProp.get_persistentProp.casesynthetic_not_a_store.zip` | A text file in place of persistent_properties, with no line the text rules select. Invented values. | Built by `reset_boot_setup_fixture.py` |
| `fixtures/data/persistentProp/testdata.persistentProp.get_persistentProp.casesynthetic_odd_entries.zip` | Synthetic boot reason history with entries that have no epoch, a text epoch, a small epoch, a huge epoch, an empty line, a lower case and an upper case factory_reset word, a subreason with commas and CRLF line ends. Invented values. | Built by `reset_boot_setup_fixture.py` |
| `fixtures/data/persistentProp/testdata.persistentProp.get_persistentProp.casesynthetic_text_lines.zip` | A text file in place of persistent_properties with lines the text rules select (a history prefix line, two-part reboot lines, a factory_reset line). Invented values. | Built by `reset_boot_setup_fixture.py` |
| `fixtures/data/persistentProp/testdata.persistentProp.get_persistentProp.casesynthetic_truncated.zip` | Synthetic persistent_properties cut in the middle of its last record. Invented values. | Built by `reset_boot_setup_fixture.py` |

Scripts (the generators that build the synthetic files, and the unit tests that use them):

| Name | What it is | How made |
| --- | --- | --- |
| `fixtures/scripts/reset_boot_setup_fixture.py` | Generator that builds the synthetic fixture data | Written for the pull request |
| `fixtures/scripts/test_reset_boot_setup.py` | Unit tests for the parser, as added by the pull request | Written for the pull request |

Also not copied: the expected-output snapshots under `admin/test/results/` and the case descriptors `admin/test/cases/testdata.*.json`. They carry upstream commit metadata and are in the upstream pull request; running the parser on a fixture regenerates the output.

## Try it

From a checkout of abrignoni/ALEAPP, run the tool on one of the fixture zips (the output folder must already exist):

```
python aleapp.py -t zip -i <path to a fixture zip> -o <path to an existing output folder>
```

The fixtures are zip files shaped like an extraction, so they are read like any zip extraction. The upstream test harness uses the same files; with the zips in place under `admin/test/cases/data/` it is run per module:

```
python admin/test/scripts/run_test_cases.py --module androidSetupFlags
python admin/test/scripts/run_test_cases.py --module persistentProp
```

See the upstream README for current options and for installing the requirements.

## What it does not prove

A reboot or a wipe is not shown to have taken place. An older reset is not shown absent when a stored entry does not contain the word, because the history keeps only a few entries. A setting with no row is not shown to be unset.

## Provenance

- Fixtures: copied unchanged from abrignoni/ALEAPP pull request 1835 at commit `34631448`. They are synthetic with invented values and were checked for e-mail addresses, phone-number-like strings, device identifiers and file paths before copying. Licence: as the upstream repository.
- The pull request was reviewed and merged by the maintainers of ALEAPP, to whom the project belongs. Source: <https://github.com/abrignoni/ALEAPP/pull/1835>.
- Author: Daniel Kwaku Ntiamoah Addai, SectraTEK Lab.
- This README is licensed CC BY 4.0.
