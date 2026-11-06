# A container state parser for the sysdiagnose framework

Author: Daniel Kwaku Ntiamoah Addai, SectraTEK Lab. Contribution to sysdiagnose framework (SAF), pull request 262. State: In review.

The framework's container parsers read text logs that a recent iPhone sysdiagnose no longer holds. This contribution adds a parser for the JSON file that holds the same information. It is the sibling of iLEAPP #2509; the two projects package the same reader differently.

## Links

- Pull request: <https://github.com/EC-DIGIT-CSIRC/sysdiagnose/pull/262>
- Parser source in the upstream repository (EC-DIGIT-CSIRC/sysdiagnose, at the commit of the pull request):
  - [`docs/containermanager_state.md`](https://github.com/EC-DIGIT-CSIRC/sysdiagnose/blob/ff2ba0cdf27c81ccf1a64d352051a4c41d68151e/docs/containermanager_state.md)
  - [`src/sysdiagnose/parsers/containermanager_state.py`](https://github.com/EC-DIGIT-CSIRC/sysdiagnose/blob/ff2ba0cdf27c81ccf1a64d352051a4c41d68151e/src/sysdiagnose/parsers/containermanager_state.py)
  - [`src/sysdiagnose/utils/container_state.py`](https://github.com/EC-DIGIT-CSIRC/sysdiagnose/blob/ff2ba0cdf27c81ccf1a64d352051a4c41d68151e/src/sysdiagnose/utils/container_state.py)
- Lab write-up: lab.sectratek.com/open-source/saf-262/ (published with the Lab website)

## What it reads

logs/ContainerManager/state.json inside a sysdiagnose case: one event per record for app data, app group, extension and system containers with their directory times, the extension-to-app map, the code-signing registration cache, recent callers of the daemon, class paths and personas. The reading is done by a separate module, utils/container_state.py, which never raises, keeps unknown keys in a column named other and rejects bad or out-of-range times.

Report artifacts (1):

- containermanager_state (parser)

## Fixtures

Copied from the pull request at commit `ff2ba0cd`. All values are synthetic and invented. Licence: as the upstream repository.

How they were made (from the pull request): Built by tests/synthetic_container_state.py: a fabricated state.json with com.example.* and group.example.* identifiers and UUIDs derived from a fixed namespace, plus damaged and unusual variants (empty file, truncated JSON, bad timestamps, missing keys). The unit tests build a small case folder around it.

Scripts (the generators that build the synthetic files, and the unit tests that use them):

| Name | What it is | How made |
| --- | --- | --- |
| `fixtures/scripts/synthetic_container_state.py` | Generator that builds the synthetic fixture data | Written for the pull request |
| `fixtures/scripts/test_parsers_containermanager_state.py` | Unit tests for the parser, as added by the pull request | Written for the pull request |
| `fixtures/scripts/test_utils_container_state.py` | Unit tests for the parser, as added by the pull request | Written for the pull request |

## Try it

SAF works on cases built from a sysdiagnose archive. The pull request ships no data archive; it ships a generator (`fixtures/scripts/synthetic_container_state.py`) that writes a fabricated `state.json`, and unit tests that build a small case folder around it. To run the parser on a real case, create a case and parse it:

```
saf create <sysdiagnose archive>
saf -c <case id> parse containermanager_state
```

For how to run the unit tests in a checkout, see the upstream README.

## What it does not prove

An app is not shown to have been installed, opened or removed. A record with no directory is not shown to be removed, replaced or not yet created. Behavior on iOS versions other than 27.0 was not tested.

## Provenance

- Fixtures: copied unchanged from EC-DIGIT-CSIRC/sysdiagnose pull request 262 at commit `ff2ba0cd`. They are synthetic with invented values and were checked for e-mail addresses, phone-number-like strings, device identifiers and file paths before copying. Licence: as the upstream repository.
- The pull request is open with the maintainers of sysdiagnose framework (SAF), to whom the project belongs, and is in review. Source: <https://github.com/EC-DIGIT-CSIRC/sysdiagnose/pull/262>.
- Author: Daniel Kwaku Ntiamoah Addai, SectraTEK Lab.
- This README is licensed CC BY 4.0.
