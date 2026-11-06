# LAB-TR-0028 artifact: device-life boundary indicators

<!-- provenance -->
> **Provenance.** The report behind this package is based on real devices from real cases, submitted to the Lab for the purpose of research. That material is confidential and is not published. The data in this package is synthetic or a fixture, built to reproduce the same structures and behaviors so that no case data is exposed.

Code (MIT, see `LICENSE-CODE`) and synthetic data (CC BY 4.0, see `LICENSE-DATA`) for the Lab Technical Report *Device-Life Boundary Indicators and the Classification of Restored Versus Native Records on Android*, Lab Technical Report LAB-TR-0028. Python 3.10 or later, standard library only. **Nothing here contains data from a real device.**

## What is here

| File | What it does |
|---|---|
| `fixtures.py` | Fixture generator (a real SQLite table with an AUTOINCREMENT identifier, native records and a restored batch written in one burst), the eleven scenarios of Table 9, the four labelling rules R1 to R4 (Section 3.4), and the evaluation over 200 seeded runs per scenario. |
| `readers.py` | Read-only readers that turn an extraction archive, a bug report or an iOS archive into lists of integers and flags (indicator times, install reasons, message and call dates, media times, marker file times). No names or content are kept. |
| `analyse.py` | The measures of Sections 3.3 and 5.1 to 5.6 and 5.8 on reader output: prevalence of the traces, offsets from the first boot record, shares of records before it, restore signals, the rules against the creator field, how restored batches are written. |
| `tables.py`, `figures.py` | Text tables and hand-written SVG figures. |
| `gen_archives.py` | Generator of **invented** archives in the layout the readers expect (8 Android, 3 bug reports, 4 iOS), so the readers and the analysis can be run end to end. |
| `run_corpus.py` | Runs readers and analysis on archives named in a configuration file you write (no default path). |
| `run_all.py` | Reproduces everything that can be reproduced here (see below). |
| `selftest.py` | Copies the package to two clean temporary directories, runs `run_all.py` in each, compares the SHA-256 of every output file, and checks the documented values. |
| `zipscan.py`, `abx.py` | Streaming reader of a ZIP central directory (file times from the extra fields); reader and writer of Android Binary XML. |
| `sample_output/` | Output of `python run_all.py --out sample_output` with the default seeds. |

## Run

```
python run_all.py --out out          # about 20 seconds
python selftest.py                   # about 25 seconds; exit code 0 if all checks pass
```

Options: `--seed N` (fixture seed, default 2810), `--archive-seed N` (invented archives, default 28), `--reps N` (repetitions per scenario, default 200). Output has no timestamp and no path; the same seeds give the same bytes.

## Expected output

| File in `out/` | Content |
|---|---|
| `table9_fixtures.md`, `.csv` | Table 9: for each scenario and rule, recall of restored records / share of native records flagged, percent, mean of 200 runs, exact boundary. With the default seed the 44 cells equal the report's Table 9 (for example S1: 100.0 / 0.0, 5.0 / 0.0, 100.0 / 0.0, 100.0 / 0.0; S6: 92.1 / 0.0 for R1; S10, R4: 100.0 / 48.5). |
| `boundary_error_statements.csv` | Section 5.7: with no restore (S8) a boundary 3 days too late flags 1.7% of native records and 14 days too late 7.7%; 3 days too early flags none; the same error loses 0.8% of an ascending batch written at setup (recall 99.2%, S1). |
| `fig1_timeline.svg`, `fig4_recall.svg` | Figure 1 (schematic of W, U, R) and Figure 4 (recall of R2 against R1 for the nine scenarios with a restore). |
| `invented_archives/` | The invented archives and their `config.json`. |
| `pipeline/report.md`, `report.json`, `fig2_gap.svg`, `fig3_shares.svg` | Tables 4 to 8, Section 5.6 and 5.8 summaries, Figures 2 and 3, computed from the invented archives. |

The `pipeline/` output shows that the readers and the analysis run; **it is not a result of the report**. The archives are built from a table of eight invented devices (for example gaps of 0.5, 2, 30, 60, 100, 120, 200 and 400 days between first boot and setup); the numbers in the pipeline report are those invented values read back, and they say nothing about real phones.

## Report item, produced by, reproducible here

| Report item | Produced by | Reproducible here |
|---|---|---|
| Table 1 (research questions) | text | no (summary of the other items) |
| Table 2 (candidate traces) | list of traces in `readers.py` (patterns) and `analyse.py` (definitions) | pipeline only |
| Table 3 (evidence classes) | counts in the configuration | no for the corpus rows; yes for "200 per case" |
| Tables 4, 5, 6, 7 | `readers.py`, `analyse.py`, `tables.py` | pipeline only (invented archives) |
| Table 8 (rules against the creator field) | `analyse.py` using the rules of `fixtures.py` | pipeline only |
| **Table 9 (fixture scenarios)** | `fixtures.py`, `run_all.py` | **yes, exactly** |
| Table 10 (ladder of claims) | text | no code |
| Section 5.7 boundary-error statements (1.7%, 7.7%, 0.8%) | `fixtures.py` | **yes, exactly** |
| Section 5.6 (how batches are written), Section 5.8 (bug reports, iOS probe) | `analyse.py` | pipeline only |
| Figure 1 | `figures.fig1_timeline` | yes (schematic) |
| Figure 2, Figure 3 | `figures.py` | pipeline only |
| **Figure 4** | `figures.fig4_recall` | **yes** (same scenarios and rule results) |

## What needs the private corpus and cannot be reproduced

Every number of Tables 2 to 8, of Sections 5.1 to 5.6 and 5.8, and Figures 2 and 3 rests on the Lab's research corpus of extractions, bug reports and iOS archives, which cannot be released. The readers are released so that the measures can be repeated on other archives. Two parts of the original runner are **not** released because they depend on vendor-specific stores: a recovery-history log (the "recovery history" row of Tables 2 and 4) and an app-store state database (the sentence on first-download times in Section 5.3). The names of the migration-tool message creators are not built in; you supply them in the configuration.

### Configuration of `run_corpus.py`

```
{"migration_creator_prefixes": ["package.name.prefix"],
 "android":     [{"id": "a1", "path": "device_a1.zip"}],
 "bug_reports": [{"id": "b1", "path": "report_b1.zip"}],
 "ios":         [{"id": "i1", "path": "device_i1.zip"}]}

python run_corpus.py config.json --out results
```

Paths are relative to the configuration file or absolute. An Android or iOS archive is a ZIP file whose member names are the paths of the device file system, with the original file times in the extended-timestamp field; a bug report is a ZIP file with one large text member. `--keep-raw` also writes the integer lists that the readers return. A store that cannot be parsed is listed under `errors` of its item and printed, not read as empty.

## Limits

- The invented archives follow the documented table and column names (AOSP provider sources, the SQLite documentation); real builds may store these files differently, and the readers were written for the layout described above.
- The fixtures encode the documented write behaviour of Section 2.1 of the report; they test the logic of the rules, not any restore tool.
- A package counts as system when its flags say so or its code path lies in one of the AOSP partitions (`/system`, `/product`, `/vendor`, `/system_ext`, `/apex`, `/odm`, `/oem`); a build that keeps system packages elsewhere would count them as non-system.
- Databases are read whole into memory before they are copied to a scratch directory; very large databases need that much memory.
- The reader of the iOS probe depends on marker files whose meaning the platform does not document (see Section 5.8 of the report).

## Licences and citation

Code: MIT (`LICENSE-CODE`). Data, sample output and text: CC BY 4.0 (`LICENSE-DATA`).

Cite the report as: Daniel Kwaku Ntiamoah Addai et al. 2026. *Device-Life Boundary Indicators and the Classification of Restored Versus Native Records on Android.* Lab Technical Report LAB-TR-0028, version 1.0. SectraTEK Lab, Prudential Associates. This package is available at https://github.com/danjethh/sectratek-lab-artifacts/tree/main/reports/lab-tr-0028.
