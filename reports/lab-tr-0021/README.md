# LAB-TR-0021 artifact: retention horizons of volatile stores

<!-- provenance -->
> **Provenance.** The report behind this package is based on real devices from real cases, submitted to the Lab for the purpose of research. That material is confidential and is not published. The data in this package is synthetic or a fixture, built to reproduce the same structures and behaviors so that no case data is exposed.

Code (MIT, `LICENSE-CODE`) and data and text (CC BY 4.0, `LICENSE-DATA`) for the Lab Technical Report
"Retention Horizons of Volatile Stores in iOS and Android Extractions"
(Lab Technical Report LAB-TR-0021). Python 3.10 or later, standard library only.
**Nothing here contains data from a real device.** The report's corpus tables cannot be reproduced from this package;
the readers that produced them are included, and a generator of invented archives lets them run end to end.

## What is here

| File | What it does |
|---|---|
| `ziputil.py` | Read-only streaming reader of the ZIP central directory (ZIP64, extended-timestamp field); copies single members out. Streams the central directory in chunks, so large archives are indexed without unpacking (the tests here use small archives only). |
| `stores.py` | The store registry (report Table 2) and the readers that date each store: unified-log file headers, the two CoreDuet databases read with and without their write-ahead log (and per stream for knowledgeC), Biome segment names, powerlog archive names, the Android file-name stores, and bug-report log sections. Also the clock rule (Listing 1), the record filter and the body-of-a-log rule (Section 3.1). |
| `stats.py` | Order-statistic interval for the median, Wilson interval, quartiles, Spearman correlation, the cell summary (cells of fewer than five devices are suppressed). |
| `analysis.py` | One device record per archive, the aggregate (prevalence, cells, strata, consistency checks, reach of 30 days, sensitivity, post hoc counts) and the report tables in Markdown. |
| `figures.py` | Report Figures 1, 2 and 3 as SVG, standard library only. |
| `paper_items.py` | Rebuilds the report items that need no corpus, from the values the report prints (`data/paper_tables_4_5.json`). |
| `synth.py` | Generator of invented archives: iOS and Android file-system archives (zip, extended-timestamp field), a hand-built write-ahead log in the documented SQLite format, and bug-report zips (one nested). Seeded; the horizons it builds in are recorded so the readers can be tested against them. |
| `run_corpus.py` | Runs the readers and the analysis on the archives named in a configuration file. |
| `run_all.py` | `--out DIR [--seed N] [--keep-archives]`: everything reproducible without the corpus. |
| `selftest.py` | Runs `run_all.py` twice in clean copies with the fixed seed, compares SHA-256 of every output, checks the documented key outputs and some unit tests. |
| `data/paper_tables_4_5.json` | The medians, quartiles, ranges and counts printed in Tables 4 and 5 and Section 5.6 of the report. |
| `sample_output/` | Output of `run_all.py` with the default seed (21). |

## Run

```
python run_all.py --out out          # about 3 seconds
python selftest.py                   # exit code 0 if two runs are byte-identical and the key outputs hold
python run_corpus.py --config config.json --out results     # on your own archives
```

`out/paper/` holds the items rebuilt from the printed values; `out/synthetic/` holds the full pipeline on invented
archives (`report.md`, `report.json`, `devices/`, three figures, `recovery.json`, and the configuration that names the
invented archives; the archives themselves are written only with `--keep-archives`).

## Expected outputs

* `paper/table2.md`: Table 2. `paper/fig1_pipeline.svg`: Figure 1.
* `paper/table4_reach30.md`: the counts, shares and Wilson intervals of the 30 d column of Table 4 recomputed from the
  printed counts. All eight intervals printed in Table 4 are reproduced (whole percent; the runner rounds to three
  decimals first, which gives the printed 98% for 20 of 22).
* `paper/fig2_horizons.svg`, `paper/fig3_reach30.svg`: Figures 2 and 3 drawn from the printed values. Figure 2 uses the
  rounded values of Tables 4 and 5 (a minimum printed as "<0.01" is entered as 0.005; the log axis starts at 0.01), so
  it can differ from the report's figure by rounding only.
* `paper/printed_checks.json`: the order-statistic intervals of Tables 4 and 5 have an achieved coverage of at least
  0.957 (the report says "at least 95.7%"); the interval of 0 of 19 reaches 17% (Section 1); the clock rule of
  Listing 1 at its boundaries.
* `synthetic/report.md`: tables in the layout of Tables 3 to 7 for 16 invented iOS archives (15 devices, 14 pass the
  clock rule), 10 invented Android archives and 6 invented bug reports. `synthetic/recovery.json`: the horizons the
  readers found against the horizons the generator built in, maximum absolute error under one second (0.005 d for the
  one store reported to two decimals). The invented sample shows, for example, the main file of interactionC holding
  older rows than the database with its log on 9 of 14 devices, and stray lines above the body of the system log in 4
  of 6 reports. These are properties of the generator's parameters, not findings.

## Report item, produced by, reproducible here

| Report item | Produced by | Reproducible here |
|---|---|---|
| Table 1 (questions and answers) | text | no (summary of corpus results) |
| Table 2 (stores, dating fields, stated retention) | `stores.table2_markdown` | yes |
| Listing 1 (clock rule and record filter) | `stores.clock_rule`, `stores.summarise_times` | yes (boundaries tested) |
| Section 3.1 (body of a log section) | `stores.body_start` | yes (the rule, unit-tested); its values and its sensitivity grid (Section 5.4) on the corpus: pipeline only (`stores.body_grid`) |
| Figure 1 (pipeline) | `figures.fig1_pipeline` | yes |
| Table 3 (sample, time source, clock rule) | `analysis.build_report` | pipeline only |
| Table 4 (iOS horizons) | `analysis`, `run_corpus.py` | the 30 d column from printed counts: yes; all other columns: pipeline only |
| Table 5 (Android and bug-report horizons) | same | pipeline only |
| Figure 2 (horizons per store) | `figures.fig2_horizons` | yes, from the printed (rounded) table values; pipeline version on invented data |
| Figure 3 (reach of 30 days) | `figures.fig3_reach` | yes, from the printed counts; pipeline version on invented data |
| Table 6 (within one release) | `analysis` strata | pipeline only |
| Table 7 (consistency and clock checks) | `analysis` checks | pipeline only |
| Sections 5.4, 5.5, 5.7, 5.8 (bug-report body, size and horizon, one knowledgeC stream, log changes the oldest record) | `analysis` post hoc and sensitivity blocks | pipeline only |

"Pipeline only" means that the code produces the same kind of table or figure from the invented archives; the values
show how the code works, not what the report found.

## What needs the private corpus

All corpus values (every cell of Tables 3 to 7 and the numbers of Sections 5.1 to 5.8) come from the Lab's research
corpus, which cannot be released. The readers are included: to run them on your own archives, write a configuration file
(`run_corpus.py` documents the schema):

```
{"devices": [
   {"id": "a1", "kind": "ios_ffs", "path": "image.zip", "acq_time": "2026-01-31T12:00:00Z", "acq_source": "record",
    "os_major": 26, "device_class": "phone", "vendor_group": "g1"},
   {"id": "b1", "kind": "bugreport", "path": "bugreport.zip"}],
 "exclude_path_patterns": []}
```

`kind` is `ios_ffs` (a zip of an iOS file system), `android_ffs` (a zip of an Android `/data` tree) or `bugreport`.
`acq_time` is the acquisition time (epoch seconds or ISO 8601); without it the modification time of the archive is used
and labelled "file". Extractions of one device share a `same_device_group`; only the latest counts for distributions.
Paths are relative to the configuration file. Nothing in the code names a location.

Not included: the Lab's orchestration (per-extraction processes with time limits), the census that defined the sample
frame, the reader of the acquisition tool's extraction record (the acquisition time comes from the configuration), the
per-device rows, and the list of devices used for the deep check. The report's runner computed bug-report horizons from
the oldest line in its first version and from the start of the body in the version reported; this package implements
the rule of Section 3.1 and keeps the oldest-line horizon alongside.

## Limits

The readers assume the layouts described in the report (paths in Table 2, the tracev3 header with the start time at
offset 32 of the header chunk, Cocoa times in the CoreDuet tables, bug-report line formats without a year). Other
releases may store these files differently; a store that cannot be parsed is reported as an error, not as empty. The
invented archives use round parameters and no calibration; the generator makes no claim to realism, and its output is
not evidence about any phone.

## Licences and citation

Code: MIT (`LICENSE-CODE`). Data and text: CC BY 4.0 (`LICENSE-DATA`).
Cite the report as: Daniel Kwaku Ntiamoah Addai et al. 2026. Retention Horizons of Volatile Stores in iOS and Android Extractions. Lab Technical Report LAB-TR-0021. SectraTEK Lab, Prudential Associates.
Public address: https://github.com/danjethh/sectratek-lab-artifacts/tree/main/reports/lab-tr-0021
