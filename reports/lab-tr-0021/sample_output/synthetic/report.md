# LAB-TR-0021 runner report on invented archives (seed 21)

Invented or measured data as given to the runner; aggregates only. Days = acquisition minus the oldest retained record (bug-report logs: start of the body).

## Sample (Table 3 layout)

| Class | Extractions | Devices | Time source | Clock-checked |
|---|---|---|---|---|
| iOS file system | 16 | 15 | file 3, record 13 | 14 |
| Android file system | 10 | 10 | file 3, record 7 | 10 |
| Android bug report | 6 | 6 | report header 6 | 6 |

## Prevalence: extractions that hold a dated record, of those readable

- iOS file system: Unified log, Persist 16/16, Unified log, Signpost 10/16, Unified log, Special 16/16, Unified log, HighVolume 2/16, Powerlog archives 16/16, Biome App.InFocus 16/16, knowledgeC, all records 16/16, knowledgeC, other streams 16/16, interactionC 16/16
- Android file system: Usage statistics, daily 10/10, Usage statistics, any interval 10/10, Notification history 10/10, DropBox entries 10/10, Network statistics 10/10, Process statistics 10/10, Battery history (vendor files) 10/10
- Android bug report: Bug report, system log (body) 6/6, Bug report, event log (body) 6/6

### iOS horizons in days (Table 4 layout)

| Store | n | Median [95% CI] | Q1 to Q3 | Min to max | >=7 d | >=30 d [CI] |
|---|---|---|---|---|---|---|
| Unified log, Persist | 14 | 4.2 [1.8, 8.6] | 3.6 to 7.4 | 1.4 to 9.8 | 5 | 0 [0%, 22%] |
| Unified log, Signpost | 10 | 5.8 [3.2, 9.2] | 3.9 to 7.2 | 2.5 to 9.3 | 3 | 0 [0%, 28%] |
| Unified log, Special | 14 | 16.6 [9.0, 22.5] | 9.5 to 21.2 | 7.2 to 26.9 | 14 | 0 [0%, 22%] |
| Powerlog archives | 14 | 6.6 [6.0, 7.0] | 6.0 to 7.0 | 6.0 to 8.0 | 7 | 0 [0%, 22%] |
| Biome App.InFocus | 14 | 36.5 [32.1, 46.7] | 32.3 to 44.1 | 31.7 to 53.8 | 14 | 14 [78%, 100%] |
| knowledgeC, all records | 14 | 347.7 [121.5, 616.3] | 139.9 to 567.6 | 26.1 to 657.5 | 14 | 12 [60%, 96%] |
| knowledgeC, other streams | 14 | 26.1 [23.0, 27.8] | 23.6 to 27.1 | 20.0 to 28.6 | 14 | 0 [0%, 22%] |
| interactionC | 14 | 167.4 [167.0, 167.7] | 167.2 to 167.7 | 166.7 to 168.0 | 14 | 14 [78%, 100%] |

### Android horizons in days (Table 5 layout)

| Store | n | Median [95% CI] | Q1 to Q3 | Min to max | >=7 d | >=30 d [CI] |
|---|---|---|---|---|---|---|
| Usage statistics, daily | 10 | 9.5 [9.2, 10.1] | 9.2 to 9.8 | 1.9 to 10.2 | 9 | 0 [0%, 28%] |
| Usage statistics, any interval | 10 | 503.9 [261.3, 654.5] | 332.8 to 634.9 | 244.9 to 689.3 | 10 | 10 [72%, 100%] |
| Notification history | 10 | 1.1 [0.93, 1.4] | 0.95 to 1.4 | 0.90 to 1.5 | 0 | 0 [0%, 28%] |
| DropBox entries | 10 | 2.4 [1.4, 3.0] | 1.7 to 2.8 | 1.3 to 3.0 | 0 | 0 [0%, 28%] |
| Network statistics | 10 | 94.5 [86.6, 102.1] | 88.2 to 101.3 | 81.3 to 105.0 | 10 | 10 [72%, 100%] |
| Process statistics | 10 | 18.3 [7.6, 37.0] | 12.9 to 35.5 | 4.2 to 38.4 | 9 | 4 [17%, 69%] |
| Battery history (vendor files) | 10 | 25.6 [9.6, 52.4] | 19.3 to 38.4 | 8.3 to 53.0 | 10 | 4 [17%, 69%] |

### Bug-report horizons in days (Table 5 layout)

| Store | n | Median [95% CI] | Q1 to Q3 | Min to max | >=7 d | >=30 d [CI] |
|---|---|---|---|---|---|---|
| Bug report, system log (body) | 6 | 0.05 [0.02, 0.12] | 0.04 to 0.08 | 0.02 to 0.12 | 0 | 0 [0%, 39%] |
| Bug report, event log (body) | 6 | 0.06 [0.02, 0.11] | 0.03 to 0.10 | 0.02 to 0.11 | 0 | 0 [0%, 39%] |

## Strata of at least five devices (Table 6 layout)

| Stratum | Store | n | Median | Q1 to Q3 | Min to max |
|---|---|---|---|---|---|
| ios os_major=17 | Unified log, Persist | 5 | 3.6 | 1.8 to 3.6 | 1.4 to 9.3 |
| ios os_major=26 | Unified log, Persist | 9 | 4.5 | 4.1 to 7.5 | 1.6 to 9.8 |
| ios device_class=phone | Unified log, Persist | 12 | 4.0 | 3.1 to 7.2 | 1.4 to 9.8 |
| ios os_major=26 | Unified log, Signpost | 6 | 6.1 | 5.7 to 8.5 | 2.5 to 9.3 |
| ios device_class=phone | Unified log, Signpost | 8 | 6.1 | 4.2 to 8.0 | 2.5 to 9.3 |
| ios os_major=17 | Unified log, Special | 5 | 22.5 | 16.2 to 22.7 | 9.6 to 26.9 |
| ios os_major=26 | Unified log, Special | 9 | 15.9 | 9.0 to 18.6 | 7.2 to 21.5 |
| ios device_class=phone | Unified log, Special | 12 | 16.6 | 9.4 to 20.7 | 7.2 to 26.9 |
| ios os_major=17 | Powerlog archives | 5 | 7.0 | 7.0 to 7.0 | 6.0 to 7.0 |
| ios os_major=26 | Powerlog archives | 9 | 6.0 | 6.0 to 7.0 | 6.0 to 8.0 |
| ios device_class=phone | Powerlog archives | 12 | 6.1 | 6.0 to 7.0 | 6.0 to 8.0 |
| ios os_major=17 | Biome App.InFocus | 5 | 32.2 | 31.7 to 39.7 | 31.7 to 43.0 |
| ios os_major=26 | Biome App.InFocus | 9 | 39.6 | 32.5 to 46.7 | 32.1 to 53.8 |
| ios device_class=phone | Biome App.InFocus | 12 | 36.5 | 32.3 to 43.4 | 31.7 to 53.8 |
| ios os_major=17 | knowledgeC, all records | 5 | 477.6 | 292.4 to 616.3 | 26.1 to 657.5 |
| ios os_major=26 | knowledgeC, all records | 9 | 227.8 | 132.8 to 426.4 | 26.2 to 654.7 |
| ios device_class=phone | knowledgeC, all records | 12 | 414.7 | 130.0 to 602.3 | 26.1 to 657.5 |
| ios os_major=17 | knowledgeC, other streams | 5 | 26.1 | 21.0 to 26.2 | 20.0 to 27.4 |
| ios os_major=26 | knowledgeC, other streams | 9 | 26.1 | 23.9 to 27.8 | 23.0 to 28.6 |
| ios device_class=phone | knowledgeC, other streams | 12 | 26.1 | 23.8 to 26.5 | 20.0 to 28.6 |
| ios os_major=17 | interactionC | 5 | 167.2 | 167.2 to 167.3 | 166.7 to 168.0 |
| ios os_major=26 | interactionC | 9 | 167.6 | 167.2 to 167.7 | 166.8 to 167.8 |
| ios device_class=phone | interactionC | 12 | 167.4 | 167.1 to 167.7 | 166.7 to 168.0 |
| android os_major=16 | Usage statistics, daily | 7 | 9.6 | 9.3 to 9.8 | 9.2 to 10.2 |
| android vendor_group=group1 | Usage statistics, daily | 8 | 9.5 | 9.2 to 9.7 | 1.9 to 10.2 |
| android os_major=16 | Usage statistics, any interval | 7 | 535.1 | 391.1 to 630.5 | 244.9 to 689.3 |
| android vendor_group=group1 | Usage statistics, any interval | 8 | 503.9 | 379.3 to 618.4 | 244.9 to 689.3 |
| android os_major=16 | Notification history | 7 | 1.2 | 0.95 to 1.3 | 0.90 to 1.5 |
| android vendor_group=group1 | Notification history | 8 | 1.1 | 0.96 to 1.3 | 0.90 to 1.5 |
| android os_major=16 | DropBox entries | 7 | 2.5 | 1.4 to 2.9 | 1.3 to 3.0 |
| android vendor_group=group1 | DropBox entries | 8 | 2.4 | 1.5 to 2.8 | 1.3 to 3.0 |
| android os_major=16 | Network statistics | 7 | 96.2 | 90.7 to 102.0 | 86.6 to 105.0 |
| android vendor_group=group1 | Network statistics | 8 | 94.5 | 88.5 to 102.0 | 86.6 to 105.0 |
| android os_major=16 | Process statistics | 7 | 14.8 | 9.9 to 28.1 | 4.2 to 38.4 |
| android vendor_group=group1 | Process statistics | 8 | 18.3 | 11.1 to 34.7 | 4.2 to 38.4 |
| android os_major=16 | Battery history (vendor files) | 7 | 23.3 | 14.5 to 31.3 | 8.3 to 53.0 |
| android vendor_group=group1 | Battery history (vendor files) | 8 | 25.6 | 16.9 to 39.1 | 8.3 to 53.0 |

## Reach of 30 days: at least one store (clock-checked devices; k, n, share, Wilson 95%)

```
{
 "android": [
  10,
  10,
  1.0,
  0.722,
  1.0
 ],
 "bugreport": [
  0,
  6,
  0.0,
  0.0,
  0.39
 ],
 "ios": [
  14,
  14,
  1.0,
  0.785,
  1.0
 ]
}
```

## Consistency and clock checks (Table 7 layout; k of n)

```
{
 "android|dropbox_name_le_mtime": [
  40,
  40
 ],
 "android|netstats_name_le_mtime": [
  50,
  50
 ],
 "android|notif_history_name_le_mtime": [
  30,
  30
 ],
 "android|procstats_name_le_mtime": [
  80,
  80
 ],
 "android|usage_name_le_mtime": [
  117,
  125
 ],
 "android|vendor_battery_hist_name_le_mtime": [
  40,
  40
 ],
 "bugreport|logcat_events_backward_steps_over_hour": [
  0,
  6
 ],
 "bugreport|logcat_system_backward_steps_over_hour": [
  0,
  6
 ],
 "ios|biome_name_le_mtime": [
  128,
  128
 ],
 "ios|interactionc|wal_changes_oldest": [
  9,
  14
 ],
 "ios|knowledgec|wal_changes_oldest": [
  0,
  14
 ],
 "ios|ul_highvolume_hdr_le_mtime": [
  4,
  4
 ],
 "ios|ul_persist_hdr_le_mtime": [
  80,
  80
 ],
 "ios|ul_signpost_hdr_le_mtime": [
  30,
  30
 ],
 "ios|ul_special_hdr_le_mtime": [
  64,
  64
 ]
}
```

## Clock

```
{
 "android": {
  "anchor_lag_h_median_min_max_n": [
   16.62,
   3.54,
   29.77,
   10
  ],
  "clock_failed": 0,
  "records_after_acq": 0,
  "records_before_floor": 0
 },
 "bugreport": {
  "clock_failed": 0,
  "records_after_acq": 0,
  "records_before_floor": 0
 },
 "ios": {
  "anchor_lag_h_median_min_max_n": [
   27.36,
   2.0,
   37.63,
   14
  ],
  "clock_failed": 1,
  "records_after_acq": 0,
  "records_before_floor": 0
 }
}
```

## Sensitivity (first percentile, newest lag, in-focus stream, oldest line)

```
{
 "android|dropbox|newest_lag": {
  "cell": "newest_lag",
  "ci_cov": 0.979,
  "ci_hi": 0.99,
  "ci_lo": 0.16,
  "ge1d": [
   1,
   10,
   0.1,
   0.018,
   0.404
  ],
  "ge30d": [
   0,
   10,
   0.0,
   0.0,
   0.278
  ],
  "ge7d": [
   0,
   10,
   0.0,
   0.0,
   0.278
  ],
  "max": 1.24,
  "median_d": 0.67,
  "min": 0.15,
  "n": 10,
  "q1": 0.24,
  "q3": 0.92
 },
 "android|netstats|newest_lag": {
  "cell": "newest_lag",
  "ci_cov": 0.979,
  "ci_hi": 15.99,
  "ci_lo": 15.16,
  "ge1d": [
   10,
   10,
   1.0,
   0.722,
   1.0
  ],
  "ge30d": [
   0,
   10,
   0.0,
   0.0,
   0.278
  ],
  "ge7d": [
   10,
   10,
   1.0,
   0.722,
   1.0
  ],
  "max": 16.24,
  "median_d": 15.67,
  "min": 15.15,
  "n": 10,
  "q1": 15.24,
  "q3": 15.92
 },
 "android|notif_history|newest_lag": {
  "cell": "newest_lag",
  "ci_cov": 0.979,
  "ci_hi": 0.99,
  "ci_lo": 0.16,
  "ge1d": [
   1,
   10,
   0.1,
   0.018,
   0.404
  ],
  "ge30d": [
   0,
   10,
   0.0,
   0.0,
   0.278
  ],
  "ge7d": [
   0,
   10,
   0.0,
   0.0,
   0.278
  ],
  "max": 1.24,
  "median_d": 0.67,
  "min": 0.15,
  "n": 10,
  "q1": 0.24,
  "q3": 0.92
 },
 "android|procstats|newest_lag": {
  "cell": "newest_lag",
  "ci_cov": 0.979,
  "ci_hi": 0.99,
  "ci_lo": 0.16,
  "ge1d": [
   1,
   10,
   0.1,
   0.018,
   0.404
  ],
  "ge30d": [
   0,
   10,
   0.0,
   0.0,
   0.278
  ],
  "ge7d": [
   0,
   10,
   0.0,
   0.0,
   0.278
  ],
  "max": 1.24,
  "median_d": 0.67,
  "min": 0.15,
  "n": 10,
  "q1": 0.24,
  "q3": 0.92
 },
 "android|usage_any|newest_lag": {
  "cell": "newest_lag",
  "ci_cov": 0.979,
  "ci_hi": 0.86,
  "ci_lo": 0.15,
  "ge1d": [
   0,
   10,
   0.0,
   0.0,
   0.278
  ],
  "ge30d": [
   0,
   10,
   0.0,
   0.0,
   0.278
  ],
  "ge7d": [
   0,
   10,
   0.0,
   0.0,
   0.278
  ],
  "max": 0.88,
  "median_d": 0.31,
  "min": 0.06,
  "n": 10,
  "q1": 0.16,
  "q3": 0.68
 },
 "android|usage_daily|newest_lag": {
  "cell": "newest_lag",
  "ci_cov": 0.979,
  "ci_hi": 0.86,
  "ci_lo": 0.15,
  "ge1d": [
   0,
   10,
   0.0,
   0.0,
   0.278
  ],
  "ge30d": [
   0,
   10,
   0.0,
   0.0,
   0.278
  ],
  "ge7d": [
   0,
   10,
   0.0,
   0.0,
   0.278
  ],
  "max": 0.88,
  "median_d": 0.31,
  "min": 0.06,
  "n": 10,
  "q1": 0.16,
  "q3": 0.68
 },
 "android|vendor_battery_hist|newest_lag": {
  "cell": "newest_lag",
  "ci_cov": 0.979,
  "ci_hi": 0.99,
  "ci_lo": 0.16,
  "ge1d": [
   1,
   10,
   0.1,
   0.018,
   0.404
  ],
  "ge30d": [
   0,
   10,
   0.0,
   0.0,
   0.278
  ],
  "ge7d": [
   0,
   10,
   0.0,
   0.0,
   0.278
  ],
  "max": 1.24,
  "median_d": 0.67,
  "min": 0.15,
  "n": 10,
  "q1": 0.24,
  "q3": 0.92
 },
 "bugreport|logcat_events|newest_lag": {
  "cell": "newest_lag",
  "ci_cov": 0.969,
  "ci_hi": 0.0,
  "ci_lo": 0.0,
  "ge1d": [
   0,
   6,
   0.0,
   0.0,
   0.39
  ],
  "ge30d": [
   0,
   6,
   0.0,
   0.0,
   0.39
  ],
  "ge7d": [
   0,
   6,
   0.0,
   0.0,
   0.39
  ],
  "max": 0.0,
  "median_d": 0.0,
  "min": 0.0,
  "n": 6,
  "q1": 0.0,
  "q3": 0.0
 },
 "bugreport|logcat_events|oldest_line": {
  "cell": "oldest_line",
  "ci_cov": 0.969,
  "ci_hi": 0.11,
  "ci_lo": 0.02,
  "ge1d": [
   0,
   6,
   0.0,
   0.0,
   0.39
  ],
  "ge30d": [
   0,
   6,
   0.0,
   0.0,
   0.39
  ],
  "ge7d": [
   0,
   6,
   0.0,
   0.0,
   0.39
  ],
  "max": 0.11,
  "median_d": 0.06,
  "min": 0.02,
  "n": 6,
  "q1": 0.03,
  "q3": 0.1
 },
 "bugreport|logcat_system|newest_lag": {
  "cell": "newest_lag",
  "ci_cov": 0.969,
  "ci_hi": 0.0,
  "ci_lo": 0.0,
  "ge1d": [
   0,
   6,
   0.0,
   0.0,
   0.39
  ],
  "ge30d": [
   0,
   6,
   0.0,
   0.0,
   0.39
  ],
  "ge7d": [
   0,
   6,
   0.0,
   0.0,
   0.39
  ],
  "max": 0.0,
  "median_d": 0.0,
  "min": 0.0,
  "n": 6,
  "q1": 0.0,
  "q3": 0.0
 },
 "bugreport|logcat_system|oldest_line": {
  "cell": "oldest_line",
  "ci_cov": 0.969,
  "ci_hi": 14.96,
  "ci_lo": 0.02,
  "ge1d": [
   4,
   6,
   0.667,
   0.3,
   0.903
  ],
  "ge30d": [
   0,
   6,
   0.0,
   0.0,
   0.39
  ],
  "ge7d": [
   4,
   6,
   0.667,
   0.3,
   0.903
  ],
  "max": 14.96,
  "median_d": 11.27,
  "min": 0.02,
  "n": 6,
  "q1": 2.82,
  "q3": 12.67
 },
 "ios|biome_appinfocus|newest_lag": {
  "cell": "newest_lag",
  "ci_cov": 0.987,
  "ci_hi": 9.0,
  "ci_lo": 9.0,
  "ge1d": [
   14,
   14,
   1.0,
   0.785,
   1.0
  ],
  "ge30d": [
   0,
   14,
   0.0,
   0.0,
   0.215
  ],
  "ge7d": [
   14,
   14,
   1.0,
   0.785,
   1.0
  ],
  "max": 9.0,
  "median_d": 9.0,
  "min": 9.0,
  "n": 14,
  "q1": 9.0,
  "q3": 9.0
 },
 "ios|interactionc|newest_lag": {
  "cell": "newest_lag",
  "ci_cov": 0.987,
  "ci_hi": 1.44,
  "ci_lo": 0.43,
  "ge1d": [
   8,
   14,
   0.571,
   0.326,
   0.786
  ],
  "ge30d": [
   0,
   14,
   0.0,
   0.0,
   0.215
  ],
  "ge7d": [
   0,
   14,
   0.0,
   0.0,
   0.215
  ],
  "max": 1.57,
  "median_d": 1.13,
  "min": 0.08,
  "n": 14,
  "q1": 0.59,
  "q3": 1.37
 },
 "ios|interactionc|p01": {
  "cell": "p01",
  "ci_cov": 0.987,
  "ci_hi": 167.26,
  "ci_lo": 165.6,
  "ge1d": [
   14,
   14,
   1.0,
   0.785,
   1.0
  ],
  "ge30d": [
   14,
   14,
   1.0,
   0.785,
   1.0
  ],
  "ge7d": [
   14,
   14,
   1.0,
   0.785,
   1.0
  ],
  "max": 167.62,
  "median_d": 166.56,
  "min": 162.66,
  "n": 14,
  "q1": 166.01,
  "q3": 167.06
 },
 "ios|knowledgec_other|newest_lag": {
  "cell": "newest_lag",
  "ci_cov": 0.987,
  "ci_hi": 1.44,
  "ci_lo": 0.43,
  "ge1d": [
   8,
   14,
   0.571,
   0.326,
   0.786
  ],
  "ge30d": [
   0,
   14,
   0.0,
   0.0,
   0.215
  ],
  "ge7d": [
   0,
   14,
   0.0,
   0.0,
   0.215
  ],
  "max": 1.57,
  "median_d": 1.13,
  "min": 0.08,
  "n": 14,
  "q1": 0.59,
  "q3": 1.37
 },
 "ios|knowledgec|infocus": {
  "cell": "infocus",
  "ci_cov": 0.987,
  "ci_hi": 27.81,
  "ci_lo": 23.04,
  "ge1d": [
   14,
   14,
   1.0,
   0.785,
   1.0
  ],
  "ge30d": [
   0,
   14,
   0.0,
   0.0,
   0.215
  ],
  "ge7d": [
   14,
   14,
   1.0,
   0.785,
   1.0
  ],
  "max": 28.61,
  "median_d": 26.06,
  "min": 20.02,
  "n": 14,
  "q1": 23.61,
  "q3": 27.06
 },
 "ios|knowledgec|newest_lag": {
  "cell": "newest_lag",
  "ci_cov": 0.987,
  "ci_hi": 1.44,
  "ci_lo": 0.43,
  "ge1d": [
   8,
   14,
   0.571,
   0.326,
   0.786
  ],
  "ge30d": [
   0,
   14,
   0.0,
   0.0,
   0.215
  ],
  "ge7d": [
   0,
   14,
   0.0,
   0.0,
   0.215
  ],
  "max": 1.57,
  "median_d": 1.13,
  "min": 0.08,
  "n": 14,
  "q1": 0.59,
  "q3": 1.37
 },
 "ios|knowledgec|p01": {
  "cell": "p01",
  "ci_cov": 0.987,
  "ci_hi": 616.26,
  "ci_lo": 121.48,
  "ge1d": [
   14,
   14,
   1.0,
   0.785,
   1.0
  ],
  "ge30d": [
   12,
   14,
   0.857,
   0.601,
   0.96
  ],
  "ge7d": [
   14,
   14,
   1.0,
   0.785,
   1.0
  ],
  "max": 657.47,
  "median_d": 347.7,
  "min": 26.06,
  "n": 14,
  "q1": 139.9,
  "q3": 567.6
 },
 "ios|powerlog_archives|newest_lag": {
  "cell": "newest_lag",
  "ci_cov": 0.987,
  "ci_hi": 2.0,
  "ci_lo": 1.0,
  "ge1d": [
   14,
   14,
   1.0,
   0.785,
   1.0
  ],
  "ge30d": [
   0,
   14,
   0.0,
   0.0,
   0.215
  ],
  "ge7d": [
   0,
   14,
   0.0,
   0.0,
   0.215
  ],
  "max": 2.0,
  "median_d": 1.0,
  "min": 1.0,
  "n": 14,
  "q1": 1.0,
  "q3": 1.81
 },
 "ios|ul_persist|newest_lag": {
  "cell": "newest_lag",
  "ci_cov": 0.987,
  "ci_hi": 1.44,
  "ci_lo": 0.43,
  "ge1d": [
   8,
   14,
   0.571,
   0.326,
   0.786
  ],
  "ge30d": [
   0,
   14,
   0.0,
   0.0,
   0.215
  ],
  "ge7d": [
   0,
   14,
   0.0,
   0.0,
   0.215
  ],
  "max": 1.57,
  "median_d": 1.13,
  "min": 0.08,
  "n": 14,
  "q1": 0.59,
  "q3": 1.37
 },
 "ios|ul_signpost|newest_lag": {
  "cell": "newest_lag",
  "ci_cov": 0.979,
  "ci_hi": 1.47,
  "ci_lo": 0.5,
  "ge1d": [
   6,
   10,
   0.6,
   0.313,
   0.832
  ],
  "ge30d": [
   0,
   10,
   0.0,
   0.0,
   0.278
  ],
  "ge7d": [
   0,
   10,
   0.0,
   0.0,
   0.278
  ],
  "max": 1.57,
  "median_d": 1.13,
  "min": 0.43,
  "n": 10,
  "q1": 0.85,
  "q3": 1.37
 },
 "ios|ul_special|newest_lag": {
  "cell": "newest_lag",
  "ci_cov": 0.987,
  "ci_hi": 1.44,
  "ci_lo": 0.43,
  "ge1d": [
   8,
   14,
   0.571,
   0.326,
   0.786
  ],
  "ge30d": [
   0,
   14,
   0.0,
   0.0,
   0.215
  ],
  "ge7d": [
   0,
   14,
   0.0,
   0.0,
   0.215
  ],
  "max": 1.57,
  "median_d": 1.13,
  "min": 0.08,
  "n": 14,
  "q1": 0.59,
  "q3": 1.37
 }
}
```

## Correlations

```
{
 "persist_bytes_per_day_median_min_max": [
  861.1,
  259.6,
  2607.0
 ],
 "persist_bytes_vs_horizon_spearman_n": [
  -0.398,
  14
 ]
}
```

## Post hoc counts

```
{
 "android_dropbox_within_0_to_3.1_d": [
  10,
  10
 ],
 "android_netstats_within_75_to_105_d": [
  10,
  10
 ],
 "android_notif_history_within_0_to_1.5_d": [
  10,
  10
 ],
 "android_usage_daily_within_0_to_10.2_d": [
  10,
  10
 ],
 "bugreport_body_changes_on_grid": [
  3,
  6
 ],
 "bugreport_body_stable_to_2pct": [
  3,
  6
 ],
 "bugreport_head_strays_system": [
  0,
  0,
  1,
  2,
  3,
  4
 ],
 "bugreport_oldest_over_body_ratio": [
  105,
  184,
  331,
  359
 ],
 "bugreport_reports_with_head_strays": [
  4,
  6
 ],
 "bugreport_spearman_lines_vs_body_horizon": 0.829,
 "bugreport_system_body_ge_1d": [
  0,
  6
 ],
 "bugreport_system_lines_min_median_max": [
  900,
  1501,
  2403
 ],
 "bugreport_system_oldest_line_ge_1d": [
  4,
  6
 ],
 "interactionc_nowal_minus_wal_d_min_median_max": [
  0.0,
  6.52,
  25.61
 ],
 "interactionc_wal_direction": {
  "nowal_older": 9,
  "same": 5,
  "wal_older": 0
 },
 "ios_devices_every_store_under_1d": 0,
 "ios_interactionc_166_to_170_d": [
  14,
  14
 ],
 "ios_knowledgec_gt_365_d": [
  7,
  14
 ],
 "knowledgec_oldest_stream_is_signals": [
  12,
  14
 ],
 "knowledgec_share_records_older_30d_median_min_max": [
  0.073,
  0.0,
  0.073
 ]
}
```

## Errors

```
[]
```
