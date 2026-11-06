# Samsung recovery history, read in full

Author: Daniel Kwaku Ntiamoah Addai, SectraTEK Lab. Contribution to ALEAPP, pull request 1834. State: Merged on October 28, 2026.

A Samsung phone keeps a short text log of every start of its recovery program. This contribution makes ALEAPP read every file that holds the log, show the recovery options as printed, and keep a damaged text out of the Build column. It also adds a Recovery History table for bug reports.

## Links

- Pull request: <https://github.com/abrignoni/ALEAPP/pull/1834>
- Parser source in the upstream repository (abrignoni/ALEAPP, at the commit of the pull request):
  - [`scripts/android_recovery_history.py`](https://github.com/abrignoni/ALEAPP/blob/6fbaf8543dce8381f4f5e6d4c41db910b9e96664/scripts/android_recovery_history.py)
  - [`scripts/artifacts/bugreportRecovery.py`](https://github.com/abrignoni/ALEAPP/blob/6fbaf8543dce8381f4f5e6d4c41db910b9e96664/scripts/artifacts/bugreportRecovery.py)
  - [`scripts/artifacts/sRecoveryhist.py`](https://github.com/abrignoni/ALEAPP/blob/6fbaf8543dce8381f4f5e6d4c41db910b9e96664/scripts/artifacts/sRecoveryhist.py)
- Lab write-up: lab.sectratek.com/open-source/aleapp-1834/ (published with the Lab website)

## What it reads

The recovery history files under efs/recovery and cache/recovery (history, extra_history, last_history, last_all_history and related files) in a file system extraction, and the same folder inside a bug report zip. Eight columns are appended before Source File; the twelve earlier columns keep their order.

Report artifacts (2):

- Bug Report - Recovery History (new)
- sRecoveryhist (changed)

## Fixtures

Copied from the pull request at commit `6fbaf854`. All values are synthetic and invented. Licence: as the upstream repository.

How they were made (from the pull request): Built by scripts/reset_recovery_fixture.py: synthetic bug report zips and extraction trees with a recovery folder (wipe, SIM-based CSC change and update entries, an extra history file) and without one, using invented values.

Data files (zip archives shaped like an extraction, one set per test case):

| Name | What it is | How made |
| --- | --- | --- |
| `fixtures/data/bugreportRecovery/testdata.bugreportRecovery.bugreport_recovery_history.casesynthetic_zip_no_recovery.zip` | Synthetic bug report zip without a recovery folder. Invented values. | Built by `reset_recovery_fixture.py` |
| `fixtures/data/bugreportRecovery/testdata.bugreportRecovery.bugreport_recovery_history.casesynthetic_zip_recovery.zip` | Synthetic bug report zip with the cache recovery folder: history files with wipe, SIM-based CSC change and update entries and an extra history file. Invented values. | Built by `reset_recovery_fixture.py` |
| `fixtures/data/bugreportRecovery/testdata.bugreportRecovery.bugreport_recovery_history.casesynthetic_zip_unset_clock.zip` | Synthetic bug report zip whose recovery history shows header dates near 1970 and 2010 and no requested time. Invented values. | Built by `reset_recovery_fixture.py` |
| `fixtures/data/sRecoveryhist/testdata.sRecoveryhist.get_sRecoveryhist.casesynthetic_cache_recovery.zip` | Synthetic cache recovery folder (last_history, last_all_history, last_extra_history) and an efs history in which one code is used twice. Invented values. | Built by `reset_recovery_fixture.py` |
| `fixtures/data/sRecoveryhist/testdata.sRecoveryhist.get_sRecoveryhist.casesynthetic_empty.zip` | Synthetic empty history and extra history files. Invented values. | Built by `reset_recovery_fixture.py` |
| `fixtures/data/sRecoveryhist/testdata.sRecoveryhist.get_sRecoveryhist.casesynthetic_extra_only.zip` | Synthetic extra history file with no history file next to it. Invented values. | Built by `reset_recovery_fixture.py` |
| `fixtures/data/sRecoveryhist/testdata.sRecoveryhist.get_sRecoveryhist.casesynthetic_malformed.zip` | Synthetic recovery files that are not clean: a stray line, a header without pipes, a bad date, a bad requested time, a control character, the spaced reboot reason form, and an extra file with lines in other forms. Invented values. | Built by `reset_recovery_fixture.py` |
| `fixtures/data/sRecoveryhist/testdata.sRecoveryhist.get_sRecoveryhist.casesynthetic_no_wipe.zip` | Synthetic recovery history with header dates after 2012: SIM-based CSC change and update entries and one prompt-and-wipe entry without a requested time, and an extra history file with no lines. Invented values. | Built by `reset_recovery_fixture.py` |
| `fixtures/data/sRecoveryhist/testdata.sRecoveryhist.get_sRecoveryhist.casesynthetic_unset_clock.zip` | Synthetic recovery history with header dates near 1970 and 2010 and no requested time. Invented values. | Built by `reset_recovery_fixture.py` |
| `fixtures/data/sRecoveryhist/testdata.sRecoveryhist.get_sRecoveryhist.casesynthetic_wipe_and_sim.zip` | Synthetic recovery history: two wipe entries with requested times and header dates in 1970, SIM-based CSC change and update entries between and after them, one entry with a header date after 2012. | Built by `reset_recovery_fixture.py` |

Scripts (the generators that build the synthetic files, and the unit tests that use them):

| Name | What it is | How made |
| --- | --- | --- |
| `fixtures/scripts/reset_recovery_fixture.py` | Generator that builds the synthetic fixture data | Written for the pull request |
| `fixtures/scripts/test_reset_recovery.py` | Unit tests for the parser, as added by the pull request | Written for the pull request |

Also not copied: the expected-output snapshots under `admin/test/results/` and the case descriptors `admin/test/cases/testdata.*.json`. They carry upstream commit metadata and are in the upstream pull request; running the parser on a fixture regenerates the output.

## Try it

From a checkout of abrignoni/ALEAPP, run the tool on one of the fixture zips (the output folder must already exist):

```
python aleapp.py -t zip -i <path to a fixture zip> -o <path to an existing output folder>
```

The fixtures are zip files shaped like an extraction, so they are read like any zip extraction. The upstream test harness uses the same files; with the zips in place under `admin/test/cases/data/` it is run per module:

```
python admin/test/scripts/run_test_cases.py --module bugreportRecovery
python admin/test/scripts/run_test_cases.py --module sRecoveryhist
```

See the upstream README for current options and for installing the requirements.

## What it does not prove

A wipe or update is not shown to have run or finished, or when, or who asked for it. An entry that is not listed is not shown never to have happened: a history file is a short log.

## Provenance

- Fixtures: copied unchanged from abrignoni/ALEAPP pull request 1834 at commit `6fbaf854`. They are synthetic with invented values and were checked for e-mail addresses, phone-number-like strings, device identifiers and file paths before copying. Licence: as the upstream repository.
- The pull request was reviewed and merged by the maintainers of ALEAPP, to whom the project belongs. Source: <https://github.com/abrignoni/ALEAPP/pull/1834>.
- Author: Daniel Kwaku Ntiamoah Addai, SectraTEK Lab.
- This README is licensed CC BY 4.0.
