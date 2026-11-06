<div align="center">

# SectraTEK Lab research artifacts

**Reproducible, synthetic-data code for mobile forensics research.**
Analysis code, invented test data and self-tests behind the SectraTEK Lab Technical Reports on Android and iOS evidence.

[![Self-tests](https://github.com/danjethh/sectratek-lab-artifacts/actions/workflows/selftests.yml/badge.svg)](https://github.com/danjethh/sectratek-lab-artifacts/actions/workflows/selftests.yml)
[![Code: MIT](https://img.shields.io/badge/code-MIT-0071e3.svg)](LICENSE)
[![Data and text: CC BY 4.0](https://img.shields.io/badge/data%20and%20text-CC%20BY%204.0-0c1d31.svg)](LICENSE-DATA)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-0071e3.svg)](docs/reproducibility.md)
[![Case data: none published](https://img.shields.io/badge/case%20data-none%20published-0c1d31.svg)](docs/data-policy.md)

[Find a package](#find-a-package) · [Run one in a minute](#run-one-in-a-minute) · [The Lab standard](#the-lab-standard) · [How to cite](#how-to-cite) · [Contribute](CONTRIBUTING.md)

</div>

---

## Why this repository exists

Mobile forensic tools report what they found. They rarely report what they could not read, what a store cannot hold any more, or which clock a timestamp came from. The SectraTEK Lab studies those gaps on research devices and publishes the results as Lab Technical Reports.

This repository is the working half of those reports. Each package holds the code that produces a report's tables and figures, a generator of **synthetic** phones or databases so anyone can run it, and a self-test that proves the run repeats byte for byte.

**Where the research comes from.** The Lab Technical Reports study real devices from real cases, submitted to the Lab for the purpose of research. That material is confidential and is never published. Every file in this repository is synthetic or a fixture, built to reproduce the same structures and behaviors, so you can run and check the methods while no case data is exposed.

Examiners can reuse the readers and decision rules. Tool authors can use the fault injectors and benchmarks to test their own parsers. Researchers can check every number that does not depend on the Lab's private research corpus, and see exactly which numbers do.

## At a glance

| | |
|---|---|
| **Packages** | 7 published reports under [`reports/`](reports/); each further package is added when its paper is published |
| **State** | 0 complete, 0 present, 7 in preparation (see [what the states mean](#package-states)) |
| **Platforms** | Android, iOS and both |
| **Dependencies** | Python 3.10 or later, standard library only |
| **Data** | Synthetic or fixture data that mirrors the structure of the real cases. No case data is published |
| **Checks** | Every code package self-tests; CI runs them on each change |
| **Licences** | Code MIT. Data and text CC BY 4.0 |

## Find a package

### I want to...

| Question | Start here |
|---|---|
| Check whether my parser silently returns nothing | [LAB-TR-0006](reports/lab-tr-0006/) |
| Read the iOS unified log or sysdiagnose | [LAB-TR-0011](reports/lab-tr-0011/) |

### By theme

#### Silent failures and parser validation

A parser that returns nothing has not shown that nothing is there. These reports measure how tools fail quietly and how to catch it.

| Report | Title | Platform | What the package holds | State | Report DOI |
|---|---|---|---|---|---|
| [LAB-TR-0001](reports/lab-tr-0001/) | Making Silent Failures Visible: A Single-Pass Section Reader for Android Bug Reports | Android | Package in preparation | In preparation | [10.5281/zenodo.23717909](https://doi.org/10.5281/zenodo.23717909) |
| [LAB-TR-0006](reports/lab-tr-0006/) | Empty Is Not Absent: Silent Failure Modes in Open-Source Mobile Forensic Parsers on iOS 26 and Android 16 | iOS + Android | Package in preparation | In preparation | [10.5281/zenodo.23717928](https://doi.org/10.5281/zenodo.23717928) |

#### Time, retention and gaps

How far back a store can see, when clocks lie, and what a hole in a log means.

| Report | Title | Platform | What the package holds | State | Report DOI |
|---|---|---|---|---|---|
| [LAB-TR-0004](reports/lab-tr-0004/) | Informative but Individually Unreliable: An Empirical Study of Android Reset Indicators and Their Clocks | Android | Package in preparation | In preparation | [10.5281/zenodo.23717926](https://doi.org/10.5281/zenodo.23717926) |

#### Deleted and removed data

What SQLite, message stores and app removal leave behind, and how many records are gone.

| Report | Title | Platform | What the package holds | State | Report DOI |
|---|---|---|---|---|---|
| [LAB-TR-0008](reports/lab-tr-0008/) | What iMessage Keeps After You Edit, Unsend, React or Delete: Database Evidence from Nine iPhone Databases on iOS 18 to 26 | iOS | Package in preparation | In preparation | [10.5281/zenodo.23717930](https://doi.org/10.5281/zenodo.23717930) |

#### System stores on iOS and Android

Unified log, sysdiagnose, Screen Time, App Ops: what each store keeps and how to read it.

| Report | Title | Platform | What the package holds | State | Report DOI |
|---|---|---|---|---|---|
| [LAB-TR-0003](reports/lab-tr-0003/) | Where Android Records Who Used What: App Ops History in Databases, XML Files and Bug Reports | Android | Package in preparation | In preparation | [10.5281/zenodo.23717924](https://doi.org/10.5281/zenodo.23717924) |
| [LAB-TR-0009](reports/lab-tr-0009/) | Screen Time on iOS 15 to 27: Mostly Empty Usage Tables and Counts That Change Without the Write-Ahead Log | iOS | Package in preparation | In preparation | [10.5281/zenodo.23717932](https://doi.org/10.5281/zenodo.23717932) |
| [LAB-TR-0011](reports/lab-tr-0011/) | Log Compression and Archive Structure in the iOS 27.0 Sysdiagnose: An Early Observation Tested Against Ten Archives | iOS | Package in preparation | In preparation | [10.5281/zenodo.23717934](https://doi.org/10.5281/zenodo.23717934) |

A machine-readable list is in [`catalog.json`](catalog.json).

### More packages are released with their papers

The Lab publishes each report's package together with the report. Further Lab Technical Reports are in preparation; their packages are added here as each paper is published. Nothing is hidden about how: every package follows the [same standard](docs/package-standard.md) before it is released.

### LEAPP contributions

The Lab's pull requests to [ALEAPP](https://github.com/abrignoni/ALEAPP), [iLEAPP](https://github.com/abrignoni/iLEAPP) and the [sysdiagnose framework](https://github.com/EC-DIGIT-CSIRC/sysdiagnose) each have a folder of synthetic test fixtures and a short guide in [`leapp-contributions/`](leapp-contributions/). Use them to try a parser, to test your own, or to see what an artifact looks like before you run it on a case.


## Run one in a minute

```bash
git clone https://github.com/danjethh/sectratek-lab-artifacts.git
cd sectratek-lab-artifacts

# one package: its own self-test (runs the package twice from clean copies and compares outputs)
python tools/run_selftests.py --only lab-tr-0030

# everything
python tools/run_selftests.py
```

No `pip install` is needed. To use a package directly, go into its folder and read its `README.md`; each one lists the files, the commands, what the run reproduces and what it cannot.

## The Lab standard

Every package follows the same contract, so you can trust one the way you trust the next.

1. **Real research, synthetic artifacts.** The reports rest on real devices submitted to the Lab for the purpose of research. The artifacts here are synthesized or fixed from those findings so that no case data is exposed and privacy is protected. See [data policy](docs/data-policy.md).
2. **Repeatable.** A fixed seed, no network, no clock dependence. The self-test runs the package from two clean copies and compares SHA-256 of every output.
3. **Honest scope.** Each README separates *what this package reproduces* from *what needs the Lab's private research corpus*. The second list is never hidden.
4. **Counts, not content.** Where a reader runs on your own files, its output holds counts and flags, not message text, names or identifiers.
5. **Plain tooling.** Python standard library, readable code, no vendored dependencies.
6. **Stated limits.** Results are indicators. Each report says what its numbers do not prove, and so does each package.

More in [`docs/package-standard.md`](docs/package-standard.md) and [`docs/reproducibility.md`](docs/reproducibility.md).

## Package states

| State | Meaning |
|---|---|
| **Complete** | Code, invented data and self-test reproduce the report's tables and figures that do not need the private corpus. The README lists exactly which. |
| **Present** | The package is in the repository and self-tests. The report's own reproduction notes say how much it covers. |
| **In preparation** | The report is published or in review; its package is not ready. The folder holds a README that says so. |

## Repository layout

```text
sectratek-lab-artifacts/
├── README.md                  this file
├── catalog.json               every package, machine-readable
├── CITATION.cff               how to cite the repository
├── LICENSE                    code: MIT
├── LICENSE-DATA               data and text: CC BY 4.0
├── CONTRIBUTING.md            how to report an issue or propose a change
├── SECURITY.md                reporting a privacy or data problem
├── docs/
│   ├── package-standard.md    what every package must contain
│   ├── reproducibility.md     seeds, hashes, versions, how the self-test works
│   ├── data-policy.md         what is and is not published, and why
│   └── how-to-cite.md         citing a report, a package, or the repository
├── reports/
│   └── lab-tr-NNNN/           one folder per published Lab Technical Report: README, code, data/, sample_output/
├── leapp-contributions/       fixtures and guides for the Lab's ALEAPP, iLEAPP and sysdiagnose pull requests
├── tools/
│   ├── run_selftests.py       run one or all self-tests
│   └── check_packages.py      structure and privacy checks used by CI
└── .github/                   CI and issue templates
```

Folder names are the report numbers (or the pull request, for LEAPP contributions) and never change, so a link to `reports/lab-tr-0030/` stays valid.

## Where the reports are

The reports themselves are Lab Technical Reports (preprints, not peer reviewed), published under CC BY 4.0. Seven are on Zenodo and carry DOIs, listed in the tables above. Others are in preparation for the same route. The reports and their write-ups will also appear on the Lab's website, lab.sectratek.com.

Several reports led to merged contributions to the open-source parsers [ALEAPP](https://github.com/abrignoni/ALEAPP) and [iLEAPP](https://github.com/abrignoni/iLEAPP) (for example iLEAPP #2573, #2574, #2576 and ALEAPP #1779 to #1784). Those parsers carry the practical fixes; this repository carries the measurement behind them.

## How to cite

Cite the report for a result, the package for the code. Citation details and a ready BibTeX entry are in [`docs/how-to-cite.md`](docs/how-to-cite.md); GitHub's **Cite this repository** button reads [`CITATION.cff`](CITATION.cff).

## Contribute

Found a wrong number, a package that does not self-test on your Python, or a way to break a decision rule? Open an issue. Pull requests that add a failing case, a clearer README line or a portability fix are welcome. Rules and the checklist are in [CONTRIBUTING.md](CONTRIBUTING.md). Please never attach data from a real device or case; see [SECURITY.md](SECURITY.md).

## About

SectraTEK Lab is the research group of SectraTEK, a product of Prudential Associates. Lead author: Daniel Kwaku Ntiamoah Addai. Co-authors are named on each report.

Contact: daniel@prudentialassociates.com

*Code: MIT licence. Data and text: CC BY 4.0. Copyright (c) 2026 Daniel Kwaku Ntiamoah Addai, SectraTEK Lab, Prudential Associates.*
