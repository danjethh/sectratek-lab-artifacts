# Fixtures and guides for the Lab's contributions to ALEAPP, iLEAPP and the sysdiagnose framework

Author: Daniel Kwaku Ntiamoah Addai, SectraTEK Lab.

This folder collects the synthetic test fixtures and a short guide for each of the Lab's 30 pull requests to three open-source forensic projects: ALEAPP, iLEAPP and the sysdiagnose analysis framework (SAF). The fixtures are the synthetic ones that were submitted upstream with each pull request, made with invented values. The parsers themselves live in the upstream projects, and each guide links to the pull request and to the parser source there. Each contribution has its own Lab write-up on the Lab website, which links back to its folder here.

## ALEAPP (Android)

| Pull request | Plain title | State | What it reads | Folder |
| --- | --- | --- | --- | --- |
| [ALEAPP #1795](https://github.com/abrignoni/ALEAPP/pull/1795) | Reading Android bug reports in a single pass | Merged on October 26, 2026 | Bug report text: device facts, section index, installed packages, package times | [aleapp-1795](./aleapp-1795/) |
| [ALEAPP #1796](https://github.com/abrignoni/ALEAPP/pull/1796) | Usage, settings and boot history from bug reports | Merged on October 26, 2026 | Bug report text: usage events, process exit info, settings, settings changes, boot reasons | [aleapp-1796](./aleapp-1796/) |
| [ALEAPP #1809](https://github.com/abrignoni/ALEAPP/pull/1809) | Bug report artifact groups and invented fixture values | Merged on October 27, 2026 | Bug report artifact groups, Device Identifiers table, invented fixture values | [aleapp-1809](./aleapp-1809/) |
| [ALEAPP #1816](https://github.com/abrignoni/ALEAPP/pull/1816) | Permissions, usage, alarms and notifications from bug reports | Merged on October 27, 2026 | Bug report text: permissions, app ops, usage, alarms, jobs, notifications (15 tables) | [aleapp-1816](./aleapp-1816/) |
| [ALEAPP #1817](https://github.com/abrignoni/ALEAPP/pull/1817) | Network, radio and telephony state from bug reports | Merged on October 27, 2026 | Bug report text: Wi-Fi, network usage, Bluetooth, NFC, USB, telephony (37 tables) | [aleapp-1817](./aleapp-1817/) |
| [ALEAPP #1818](https://github.com/abrignoni/ALEAPP/pull/1818) | Accounts, power, location and media from bug reports | Merged on October 27, 2026 | Bug report text: accounts, sync, backup, power, processes, location, sensors, camera, media (59 tables) | [aleapp-1818](./aleapp-1818/) |
| [ALEAPP #1819](https://github.com/abrignoni/ALEAPP/pull/1819) | Security, storage, logs and crash records from bug reports | Merged on October 27, 2026 | Bug report text: security, device policy, storage, system and kernel logs, crash records (38 tables) | [aleapp-1819](./aleapp-1819/) |
| [ALEAPP #1834](https://github.com/abrignoni/ALEAPP/pull/1834) | Samsung recovery history, read in full | Merged on October 28, 2026 | Samsung recovery history (every file that holds it) and a bug report recovery table | [aleapp-1834](./aleapp-1834/) |
| [ALEAPP #1835](https://github.com/abrignoni/ALEAPP/pull/1835) | Boot reasons and setup flags, decoded | Merged on October 28, 2026 | Android boot reason history from persistent properties, and a Setup Flags table | [aleapp-1835](./aleapp-1835/) |
| [ALEAPP #1779](https://github.com/abrignoni/ALEAPP/pull/1779) | Gallery rows kept when the address table is gone | Merged on October 25, 2026 | Samsung Gallery database: image rows kept when the address table is missing | [aleapp-1779](./aleapp-1779/) |
| [ALEAPP #1782](https://github.com/abrignoni/ALEAPP/pull/1782) | Reading every Android user's database | Merged on October 25, 2026 | Four artifacts now read one database per Android user and add an Android User column | [aleapp-1782](./aleapp-1782/) |
| [ALEAPP #1780](https://github.com/abrignoni/ALEAPP/pull/1780) | Blocked numbers and Android Auto rejected cars | Merged on October 25, 2026 | Blocked numbers table, and Android Auto rejected cars, read for every Android user | [aleapp-1780](./aleapp-1780/) |
| [ALEAPP #1781](https://github.com/abrignoni/ALEAPP/pull/1781) | Bluetooth file transfers from btopp.db | Merged on October 25, 2026 | Bluetooth file transfers from btopp.db | [aleapp-1781](./aleapp-1781/) |
| [ALEAPP #1783](https://github.com/abrignoni/ALEAPP/pull/1783) | Samsung Smart Switch transfer history | Merged on October 25, 2026 | Samsung Smart Switch transfer history (8 artifacts) | [aleapp-1783](./aleapp-1783/) |
| [ALEAPP #1784](https://github.com/abrignoni/ALEAPP/pull/1784) | Reading the Android Health Connect store | Merged on October 25, 2026 | Android Health Connect store (13 artifacts) | [aleapp-1784](./aleapp-1784/) |
| [ALEAPP #1785](https://github.com/abrignoni/ALEAPP/pull/1785) | Reading WhatsApp Business stores in ALEAPP | In review | WhatsApp Business stores (a thin layer over the existing WhatsApp artifacts) | [aleapp-1785](./aleapp-1785/) |
| [ALEAPP #1786](https://github.com/abrignoni/ALEAPP/pull/1786) | Reading App Ops history databases in ALEAPP | In review | Android App Ops history databases (camera, microphone, location accesses) | [aleapp-1786](./aleapp-1786/) |
| [ALEAPP #1787](https://github.com/abrignoni/ALEAPP/pull/1787) | Reading SIM slot logs and network lookups | In review | Android phone app SIM slot log (uicc_log.db) and network lookups (trafficstats) | [aleapp-1787](./aleapp-1787/) |

## iLEAPP (iOS)

| Pull request | Plain title | State | What it reads | Folder |
| --- | --- | --- | --- | --- |
| [iLEAPP #2311](https://github.com/abrignoni/iLEAPP/pull/2311) | Reading URL opens from the unified log | Merged on October 14, 2026 | Unified log lines for URL opens (logarchive) | [ileapp-2311](./ileapp-2311/) |
| [iLEAPP #2509](https://github.com/abrignoni/iLEAPP/pull/2509) | Reading app containers from the container manager state | Merged on October 19, 2026 | iOS 27 container manager state file (3 reports) | [ileapp-2509](./ileapp-2509/) |
| [iLEAPP #2517](https://github.com/abrignoni/iLEAPP/pull/2517) | Camera and microphone sessions in the unified log | Merged on October 20, 2026 | Camera and microphone sessions in the unified log (logarchive) | [ileapp-2517](./ileapp-2517/) |
| [iLEAPP #2518](https://github.com/abrignoni/iLEAPP/pull/2518) | Permission cache and location state dumps | Merged on October 20, 2026 | Permission cache and location manager state dumps in the unified log | [ileapp-2518](./ileapp-2518/) |
| [iLEAPP #2521](https://github.com/abrignoni/iLEAPP/pull/2521) | Per-app runtime from the BatteryUI property lists | Merged on October 20, 2026 | Per-app runtime from the BatteryUI property lists in a sysdiagnose (3 artifacts) | [ileapp-2521](./ileapp-2521/) |
| [iLEAPP #2522](https://github.com/abrignoni/iLEAPP/pull/2522) | Reading ManagedSettings Stores in a Sysdiagnose | Merged on October 20, 2026 | ManagedSettings stores in a sysdiagnose (2 artifacts) | [ileapp-2522](./ileapp-2522/) |
| [iLEAPP #2573](https://github.com/abrignoni/iLEAPP/pull/2573) | Reading the Screen Time Store Databases | Merged on October 25, 2026 | Screen Time remote management stores (8 artifacts) | [ileapp-2573](./ileapp-2573/) |
| [iLEAPP #2574](https://github.com/abrignoni/iLEAPP/pull/2574) | Three Parser Fixes for Empty and Failed Reports | Merged on October 25, 2026 | Three parser fixes: calendar dates, location services list, Waze database lookup | [ileapp-2574](./ileapp-2574/) |
| [iLEAPP #2575](https://github.com/abrignoni/iLEAPP/pull/2575) | Reading five more sysdiagnose files | Merged on October 25, 2026 | Five more sysdiagnose files: iCloud Drive, MC events, Network Extension, swcutil, taskinfo (10 artifacts) | [ileapp-2575](./ileapp-2575/) |
| [iLEAPP #2576](https://github.com/abrignoni/iLEAPP/pull/2576) | What Messages Keeps After Edits, Unsends and Deletes | Merged on October 25, 2026 | Messages database: reactions, edits, unsent parts, replies, Recently Deleted, previews, app messages (8 tables) | [ileapp-2576](./ileapp-2576/) |
| [iLEAPP #2577](https://github.com/abrignoni/iLEAPP/pull/2577) | Lockdown Mode, passkey, shortcut and VPN log lines | Merged on October 25, 2026 | Unified log lines: Lockdown Mode flag, passkey record loads, background shortcut actions, VPN state | [ileapp-2577](./ileapp-2577/) |

## Sysdiagnose analysis framework (SAF)

| Pull request | Plain title | State | What it reads | Folder |
| --- | --- | --- | --- | --- |
| [SAF #262](https://github.com/EC-DIGIT-CSIRC/sysdiagnose/pull/262) | A container state parser for the sysdiagnose framework | In review | iOS 27 container manager state parser (containermanager_state) | [saf-262](./saf-262/) |

## How to use a fixture

1. Check out the upstream project named in the guide and install its requirements as its README describes.
2. Run the tool on a fixture zip from the contribution's `fixtures/data/` folder, for example `python aleapp.py -t zip -i <fixture zip> -o <existing output folder>` (the iLEAPP command has the same form). The output folder must already exist.
3. Compare the report with the artifact notes in the parser source. To rerun the upstream tests, use the harness the project documents (`admin/test/scripts/run_test_cases.py` in ALEAPP and iLEAPP).

Commands and options change between releases. Follow each upstream README, and treat the commands in the guides as patterns rather than a promise. Some contributions ship generator scripts instead of, or beside, data files; the guide says where that is the case.

## Provenance

The Lab's research reports are based on real devices from real cases submitted to the Lab for the purpose of research. Those images are confidential and are never published. The fixtures here are synthetic: they were built by script or by hand with invented names, numbers, identifiers and dates. Fixture files keep the licence of the upstream project they were submitted to (licence: as the upstream repository). The guides in this folder are licensed CC BY 4.0.
