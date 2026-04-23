# SCADA Engineering Tools — Implementation-Ready Specifications

Twelve implementation-ready engineering specifications for software tools that streamline SCADA engineering workflows. Specs are **platform-agnostic** with **Ignition (Inductive Automation) as the first implementation target**, generalized across industrial SCADA (oil & gas, water/wastewater, manufacturing, power generation) with **utility-scale renewables (PV / BESS / wind / PPC)** notes throughout.

Each spec follows a uniform 14-section structure:

1. Problem Statement
2. User Personas & Stories
3. Functional Requirements
4. Non-Functional Requirements
5. System Architecture (with ASCII diagram)
6. Data Models (YAML / JSON / SQL)
7. API Contracts (REST + gRPC)
8. Tech Stack
9. Key Algorithms / Pseudocode
10. Edge Cases
11. Ignition-Specific Integration
12. Test Plan
13. Phased Rollout
14. Success Metrics

## The Twelve Specs

| # | File | Feature |
|---|---|---|
| 1 | [01_protocol_emulators.md](./01_protocol_emulators.md) | Protocol emulators for automated testing (Modbus, DNP3, IEC 61850, OPC UA, BACnet, EtherNet/IP, MQTT/Sparkplug, SunSpec, S7, IEC 60870-5-104) |
| 2 | [02_screen_building.md](./02_screen_building.md) | Screen building from CAD drawings or pictures (DWG/DXF/PDF/photos → Perspective/Vision) |
| 3 | [03_alarm_generation.md](./03_alarm_generation.md) | Alarm generation from spreadsheets (ISA-18.2 / IEC 62682 compliant) |
| 4 | [04_historian_setup.md](./04_historian_setup.md) | Historian setup from spreadsheets (Ignition Tag Historian, PI, Canary, InfluxDB, TimescaleDB) |
| 5 | [05_io_list_generation.md](./05_io_list_generation.md) | IO list generation from plant design (PlantPredict, PVCase, Helioscope, PVsyst, ETAP) |
| 6 | [06_tag_creation.md](./06_tag_creation.md) | Tag creation from IO list — single-line-diagram-driven, UDT-based |
| 7 | [07_grid_code_compliance.md](./07_grid_code_compliance.md) | Grid code compliance checking (CAISO, ERCOT, PJM, SPP, MISO, NYISO, ISO-NE, NERC PRC, IEEE 2800/1547) |
| 8 | [08_fat_sat_checklists.md](./08_fat_sat_checklists.md) | FAT & SAT checklist generation (IEC 62381/62382, GAMP 5, 21 CFR Part 11) |
| 9 | [09_comms_troubleshooting.md](./09_comms_troubleshooting.md) | Comms troubleshooting (OSI L1-L7 walker with RCA engine) |
| 10 | [10_anomaly_detection.md](./10_anomaly_detection.md) | Anomaly detection on historian data (gaps, outliers, frozen, timestamp issues, fleet) |
| 11 | [11_config_as_code.md](./11_config_as_code.md) | Config-as-code for PLC/RTU programs (PLCopen XML, vendor adapters, Git, signed builds) |
| 12 | [12_plc_emulation.md](./12_plc_emulation.md) | PLC hardware emulation / containerized PLC runtime (OpenPLC, CODESYS, TwinCAT, S7-PLCSIM, Logix Emulate, FMI co-sim) |

## How the specs interconnect

```
                        ┌──────────────────────┐
                        │ Spec 5: IO List      │
                        │ (from plant design)  │
                        └──────────┬───────────┘
                                   ▼
        ┌──────────────┐  ┌──────────────────────┐  ┌──────────────┐
        │ Spec 2:      │  │ Spec 6: Tag DB       │  │ Spec 3:      │
        │ Screens (CAD)│◀─│ (UDTs, hierarchy)    │─▶│ Alarms       │
        └──────────────┘  └──────────┬───────────┘  └──────────────┘
                                     │
                ┌────────────────────┼────────────────────┐
                ▼                    ▼                    ▼
        ┌──────────────┐    ┌──────────────┐     ┌──────────────┐
        │ Spec 4:      │    │ Spec 7: Grid │     │ Spec 9:      │
        │ Historian    │    │ Code (PPC)   │     │ Comms diag   │
        └──────┬───────┘    └──────────────┘     └──────────────┘
               │
               ▼
        ┌──────────────┐
        │ Spec 10:     │
        │ Anomaly det. │
        └──────────────┘

        ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
        │ Spec 11:     │───▶│ Spec 12:     │───▶│ Spec 8:      │
        │ Config-as-   │    │ PLC sim      │    │ FAT/SAT      │
        │ code (PLC)   │    │ (containers) │    │ checklists   │
        └──────────────┘    └──────────────┘    └──────┬───────┘
                                   ▲                   │
                                   │                   │
                                   └───────────────────┘
                            ┌──────────────┐
                            │ Spec 1:      │
                            │ Protocol emu │  ◀── feeds Specs 8 & 12
                            └──────────────┘
```

Key integration points:
- **Spec 5 → Spec 6**: IO list directly drives UDT auto-derivation and tag instantiation.
- **Spec 6 → Specs 2/3/4/7/9/10**: Tag DB is the single source of truth for screens, alarms, historian, grid-code monitoring, comms diagnostics, and anomaly detection.
- **Specs 1 + 12 → Spec 8**: Protocol emulators and containerized PLC runtimes enable virtual FAT before any hardware ships.
- **Spec 11 → Spec 12 → Spec 8**: PLC config-as-code triggers CI builds that run inside containerized PLC sims under FAT/SAT test plans — full automation from PLC commit to verified deploy.

## Standards referenced

- IEC 61131-3 (PLC programming languages), IEC 61499 (function block models)
- IEC 61850 (substation comms; MMS, GOOSE, SV)
- IEC 60870-5-101/104 (telecontrol)
- IEC 62381 (FAT) / IEC 62382 (SAT)
- IEC 62443 (industrial cybersecurity)
- IEC 81346 (industrial systems reference designation)
- ISA-18.2 / IEC 62682 (alarm management)
- ISA-95 (enterprise-control integration)
- ISA-101 (HMI design)
- NERC PRC-024-3, PRC-019, PRC-006, BAL-003, CIP-010
- IEEE 2800-2022 (IBR interconnection), IEEE 1547-2018 (DER interconnection)
- GAMP 5, 21 CFR Part 11 (life sciences validation, electronic records)
- FMI 2.0 / 3.0 (co-simulation)
- PLCopen TC6 XML (vendor-neutral PLC program exchange)
- OPC UA (OPC 10000 series), Sparkplug B, SunSpec
- IEC 61400-25 (wind turbine comms)

## Implementation philosophy

- **Platform-agnostic core, Ignition-first integration**: Each spec defines a vendor-neutral domain model, a generator framework with pluggable backends, and a concrete Ignition module / integration as the day-1 target.
- **Renewables as the first vertical**: Utility-scale PV, BESS, wind, and PPC use cases are first-class examples throughout. Generalization to oil & gas, water, manufacturing, and power generation is explicit in each spec.
- **Specs interlock**: Outputs of one spec are inputs of others; treat the set as a connected toolchain, not isolated point solutions.
- **CI/CD for SCADA**: Specs 1, 8, 11, 12 enable continuous integration for SCADA + PLC systems — a paradigm shift from artisanal commissioning to engineered software delivery.

## File contents

Each spec is approximately 4,000–5,500 words / 8–10 pages of implementation-ready detail. Total: ~50,000 words across the 12 specs.
