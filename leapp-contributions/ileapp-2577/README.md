# Lockdown Mode, passkey, shortcut and VPN log lines

Author: Daniel Kwaku Ntiamoah Addai, SectraTEK Lab. Contribution to iLEAPP, pull request 2577. State: Merged on October 25, 2026.

Most iOS security controls leave a trace in the unified log, and few record a change. This contribution reads four of those traces, each as a restated status, and says in plain words what a line does not establish.

## Links

- Pull request: <https://github.com/abrignoni/iLEAPP/pull/2577>
- Parser source in the upstream repository (abrignoni/iLEAPP, at the commit of the pull request):
  - [`scripts/artifacts/logarchive.py`](https://github.com/abrignoni/iLEAPP/blob/c2333e338e81aece948ded5017fa990eb1ce6a20/scripts/artifacts/logarchive.py)
- Lab write-up: lab.sectratek.com/open-source/ileapp-2577/ (published with the Lab website)

## What it reads

Unified log entries, through the collected logarchive table: the Photos backend isLockdownMode value, Safari passkey record loads, background shortcut runner lines that name an actionID, and Network Extension VPN connectivity state. Each row is a log line with its standard columns and nothing is interpreted.

Report artifacts (4):

- logarchive Lockdown Mode flag in Photos
- logarchive Safari passkey record loads
- logarchive background shortcut actions
- logarchive VPN connectivity state

## Fixtures

Copied from the pull request at commit `c2333e33`. All values are synthetic and invented. Licence: as the upstream repository.

How they were made (from the pull request): The pull request adds one test script, scripts/test_logarchive_wave3.py, which builds an invented log show export in code. It adds no data files.

Scripts (the generators that build the synthetic files, and the unit tests that use them):

| Name | What it is | How made |
| --- | --- | --- |
| `fixtures/scripts/test_logarchive_wave3.py` | Unit tests for the parser, as added by the pull request | Written for the pull request |

## Try it

There is no data fixture for this change. The artifacts read the table that the logarchive module builds from a unified log, so they need an iOS unified log (a sysdiagnose or a log archive) as input; see the upstream README for how iLEAPP is run on such input.

The test script `fixtures/scripts/test_logarchive_wave3.py` builds an invented log export in code and drives the real two-stage chain; it expects to sit under `admin/test/scripts/` in an iLEAPP checkout.

## What it does not prove

Lockdown Mode is not shown to be off at any time but the moment a line was written. The number of passkeys is not shown. A shortcut is not shown to have run to completion. The VPN involved is not identified.

## Provenance

- Fixtures: copied unchanged from abrignoni/iLEAPP pull request 2577 at commit `c2333e33`. They are synthetic with invented values and were checked for e-mail addresses, phone-number-like strings, device identifiers and file paths before copying. Licence: as the upstream repository.
- The pull request was reviewed and merged by the maintainers of iLEAPP, to whom the project belongs. Source: <https://github.com/abrignoni/iLEAPP/pull/2577>.
- Author: Daniel Kwaku Ntiamoah Addai, SectraTEK Lab.
- This README is licensed CC BY 4.0.
