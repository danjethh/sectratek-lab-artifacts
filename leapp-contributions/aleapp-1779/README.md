# Gallery rows kept when the address table is gone

Author: Daniel Kwaku Ntiamoah Addai, SectraTEK Lab. Contribution to ALEAPP, pull request 1779. State: Merged on October 25, 2026.

A Samsung Gallery database can keep a view after the table behind it has been removed, and the artifact then reported no images at all. This contribution tests the view first, and when it cannot be used it still reports the image rows with a blank Address and a note that explains the blank.

## Links

- Pull request: <https://github.com/abrignoni/ALEAPP/pull/1779>
- Parser source in the upstream repository (abrignoni/ALEAPP, at the commit of the pull request):
  - [`scripts/artifacts/cmh.py`](https://github.com/abrignoni/ALEAPP/blob/1f9c5a3ece97f1668ff0907eb809e1d78687bd61/scripts/artifacts/cmh.py)
- Lab write-up: lab.sectratek.com/open-source/aleapp-1779/ (published with the Lab website)

## What it reads

cmh.db in the Samsung Gallery provider: the files table, the location table and location_view. The artifact runs a one-row query against the view; if that fails it logs a line and reports the files rows without the join.

Report artifacts (1):

- Samsung_CMH (cmh)

## Fixtures

Copied from the pull request at commit `1f9c5a3e`. All values are synthetic and invented. Licence: as the upstream repository.

How they were made (from the pull request): Two synthetic cmh.db files with invented values: one with the files table, the location table and the view, and one with the view present but the location table dropped.

Data files (zip archives shaped like an extraction, one set per test case):

| Name | What it is | How made |
| --- | --- | --- |
| `fixtures/data/cmh/testdata.cmh.get_cmh.casesynthetic_cmh_location.zip` | Synthetic cmh.db with a files table, a location table and the location_view, invented values. | See the note above |
| `fixtures/data/cmh/testdata.cmh.get_cmh.casesynthetic_cmh_no_location_table.zip` | Synthetic cmh.db with the location_view present but the location table it selects from dropped, as in a Samsung Android 16 database; invented values. | See the note above |

Also not copied: the expected-output snapshots under `admin/test/results/` and the case descriptors `admin/test/cases/testdata.*.json`. They carry upstream commit metadata and are in the upstream pull request; running the parser on a fixture regenerates the output.

## Try it

From a checkout of abrignoni/ALEAPP, run the tool on one of the fixture zips (the output folder must already exist):

```
python aleapp.py -t zip -i <path to a fixture zip> -o <path to an existing output folder>
```

The fixtures are zip files shaped like an extraction, so they are read like any zip extraction. The upstream test harness uses the same files; with the zips in place under `admin/test/cases/data/` it is run per module:

```
python admin/test/scripts/run_test_cases.py --module cmh
```

See the upstream README for current options and for installing the requirements.

## What it does not prove

A blank Address is not shown to mean the photo had no address. Other builds may keep addresses elsewhere; that was not examined.

## Provenance

- Fixtures: copied unchanged from abrignoni/ALEAPP pull request 1779 at commit `1f9c5a3e`. They are synthetic with invented values and were checked for e-mail addresses, phone-number-like strings, device identifiers and file paths before copying. Licence: as the upstream repository.
- The pull request was reviewed and merged by the maintainers of ALEAPP, to whom the project belongs. Source: <https://github.com/abrignoni/ALEAPP/pull/1779>.
- Author: Daniel Kwaku Ntiamoah Addai, SectraTEK Lab.
- This README is licensed CC BY 4.0.
