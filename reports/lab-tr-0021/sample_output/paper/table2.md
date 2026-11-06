Table 2 (store registry of stores.py)

| Store | Where kept | Dating field and clock | Stated retention |
|---|---|---|---|
| **iOS full file system** | | | |
| Unified log: Persist, Special, Signpost, HighVolume | db/diagnostics/<stream>/*.tracev3 | File header start time, UTC [14] | Hours to about 10 days [4]; a few days [11] |
| knowledgeC | CoreDuet/Knowledge/knowledgeC.db | ZOBJECT.ZSTARTDATE, seconds since 2001 | About 4 weeks [10]; 28 to 30 days [13] |
| interactionC | CoreDuet/People/interactionC.db | ZINTERACTIONS.ZSTARTDATE | None found |
| Biome App.InFocus | Biome/streams/restricted/App.InFocus/local/ | Segment name, microseconds since 2001 | 28 to 30 days (Biome data) [13] |
| Powerlog archives | BatteryLife/Archives/powerlog_<date>_* | Calendar date in name (day, +-1 d) | None found |
| **Android full file system (user 0)** | | | |
| Usage statistics | usagestats/{daily, weekly, monthly, yearly}/ | Name, epoch ms | Source: daily 10 d, weekly 4 wk, monthly 6 mo, yearly 2 y [9] |
| Notification history | notification_history/history/ | Name, epoch ms | Source: 1 d [7] |
| DropBox entries | system/dropbox/<tag>@<ms>.* | Name, epoch ms | Source default: 3 d, 1,000 files, a size quota [5] |
| Network statistics | netstats/{xt, uid, uid_tag}.<start>-<end> | Name (start), epoch ms | Source: files of 15 d, deleted after 90 d (device and per-app) [6] |
| Process statistics | procstats/state-v2-<date>.bin | Name, device local time (+-14 h) | Source: 8 files [8] |
| Battery history (vendor files) | data/log/batterystats/ | Name, device local time (+-14 h) | None found |
| **Android bug report** | | | |
| System log, event log | SYSTEM LOG, EVENT LOG sections | Line time, counted from the start of the body of the section (Section 3.1), against the report's header time; one device clock | None found |
