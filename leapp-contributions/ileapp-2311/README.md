# Reading URL opens from the unified log

Author: Daniel Kwaku Ntiamoah Addai, SectraTEK Lab. Contribution to iLEAPP, pull request 2311. State: Merged on October 14, 2026.

iOS writes a line to the unified log when something opens a link, but it withholds the link itself. This contribution lists those lines in iLEAPP so an examiner can say that a link was opened, when, and which process wrote the line.

## Links

- Pull request: <https://github.com/abrignoni/iLEAPP/pull/2311>
- Parser source in the upstream repository (abrignoni/iLEAPP, at the commit of the pull request):
  - [`scripts/artifacts/logarchive.py`](https://github.com/abrignoni/iLEAPP/blob/04bda2ecb7bc5c729008698353c2196f1a9b8719/scripts/artifacts/logarchive.py)
- Lab write-up: lab.sectratek.com/open-source/ileapp-2311/ (published with the Lab website)

## What it reads

The unified log, through the existing logarchive module: log lines that contain one of three literal markers (UIOpenURLAction, openURLContexts and no registered handler for URL scheme). The standard log columns are copied; no URL and no inference are added. Lines that check whether a scheme could be opened are deliberately not matched.

Report artifacts (1):

- logarchive URL and link opens

## Fixtures

This pull request added no test fixtures, so there is nothing to copy. The change was checked as described in the pull request; see the upstream pull request for details.

## Try it

There is no data fixture for this change. The artifacts read the table that the logarchive module builds from a unified log, so they need an iOS unified log (a sysdiagnose or a log archive) as input; see the upstream README for how iLEAPP is run on such input.

## What it does not prove

A person is not shown to have tapped a link. The URL that was opened is not shown. A page load or an app handling the link is not shown.

## Provenance

- Fixtures: none added by this pull request.
- The pull request was reviewed and merged by the maintainers of iLEAPP, to whom the project belongs. Source: <https://github.com/abrignoni/iLEAPP/pull/2311>.
- Author: Daniel Kwaku Ntiamoah Addai, SectraTEK Lab.
- This README is licensed CC BY 4.0.
