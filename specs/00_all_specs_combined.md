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
-e 

---


# Spec 1 — Protocol Emulators for Automated Testing

## 1. Problem Statement

SCADA engineers spend significant effort testing systems against field devices that are physically unavailable during development: inverters not yet shipped, RTUs at remote substations, third-party meters with proprietary firmware. Traditional approaches — borrowing hardware, scheduling field outages, deferring testing to commissioning — extend project timelines, push defects late in the lifecycle, and prevent CI/CD adoption. A reusable suite of programmable protocol emulators that behave like real devices (Modbus TCP/RTU, DNP3, IEC 61850 MMS/GOOSE/SV, IEC 60870-5-101/104, OPC UA, BACnet, EtherNet/IP, MQTT/Sparkplug B, SunSpec, S7) would let engineers build and validate SCADA logic against virtual fleets at desktop scale, run regression tests in CI, and reproduce field anomalies on demand.

## 2. User Personas & Stories

**SCADA Application Engineer (primary)** — *"As a SCADA engineer, I want to spin up 200 emulated inverters with realistic SunSpec/Modbus register maps so I can validate my Ignition tag database, alarm logic, and power curtailment scripts before any hardware arrives on site."*

**Test Automation Engineer** — *"As a test engineer, I want to script protocol-level fault injection (CRC errors, timeouts, value spikes, comm dropouts) and run my SCADA regression suite in GitHub Actions on every pull request."*

**Commissioning Engineer** — *"As a commissioning engineer, I want to capture the protocol traffic from a misbehaving field device, replay it against the SCADA in the lab, and confirm whether the bug is in the device or our system."*

**Cybersecurity Engineer** — *"As an OT security engineer, I want to use the emulator as a honeypot or as a target for IDS rule validation."*

## 3. Functional Requirements

- **F1**: Emulate at minimum the following protocols at server/slave/outstation role:
  - Modbus TCP, Modbus RTU (over serial or TCP-encapsulated)
  - DNP3 outstation (Level 1–3)
  - IEC 61850 MMS server, GOOSE publisher, Sampled Values publisher
  - IEC 60870-5-104 controlled station (slave)
  - OPC UA server (Nano, Micro, Embedded profiles)
  - BACnet/IP device
  - EtherNet/IP adapter (CIP)
  - MQTT broker + Sparkplug B EoN/Device
  - SunSpec (over Modbus, with full Common + inverter + meter + storage models)
  - Siemens S7 (S7-300/400/1200/1500 ISO-on-TCP)
- **F2**: Configurable register/data maps via YAML, JSON, or CSV — including device identity (vendor name, serial, firmware version) and full point list.
- **F3**: Behavioral scripting — points can be static, ramp, sinusoidal, replay-from-CSV, or driven by a Python/Lua/JavaScript expression that reads other points (e.g., `MW_out = irradiance * derate * efficiency`).
- **F4**: Fault injection — per-point or per-protocol: CRC corruption, dropped responses, increased latency, value freezing, register-not-implemented exceptions, packet truncation, link drops, sequence-number corruption.
- **F5**: Time control — wall-clock, accelerated (10×, 100×), step-mode, and pause; multiple emulator instances must support synchronized time.
- **F6**: Fleet mode — instantiate N copies of a device template with parameter sweeps (e.g., serials, IP/port assignments, geographic position).
- **F7**: REST + gRPC control plane — start/stop devices, set point values, inject faults, query state, subscribe to events.
- **F8**: PCAP record/replay — capture all protocol traffic to PCAP; replay a PCAP back through the emulator to reproduce field scenarios.
- **F9**: CI/CD integration — Docker images, Helm chart, GitHub Actions / GitLab CI examples, JUnit-format test reports.
- **F10**: Web UI — dashboard showing device tree, live values, fault state, traffic stats; allow manual point overrides.
- **F11**: Scenario library — versioned scenarios (e.g., "MISO islanding event," "CT saturation," "GOOSE storm") that can be invoked by name.

## 4. Non-Functional Requirements

- **N1 Performance**: Single host (16 cores, 32 GB RAM) sustains 1,000 simultaneous Modbus TCP slaves at 1-second poll, or 50 IEC 61850 MMS servers with 500 GOOSE messages/sec.
- **N2 Determinism**: Replay of a PCAP must reproduce timing within ±2 ms.
- **N3 Footprint**: Single-device container < 50 MB; idle CPU < 1%.
- **N4 Security**: Emulator's own management plane uses mTLS; no default passwords; runs as non-root in containers; honors NIST 800-82r3 logging recommendations.
- **N5 Portability**: Linux x86_64 + arm64 first-class; macOS and Windows for desktop dev.
- **N6 Observability**: Prometheus metrics (`emulator_pdu_total`, `emulator_fault_active`, etc.), structured JSON logs, OpenTelemetry traces.
- **N7 Standards conformance**: Pass the relevant conformance test where one exists — e.g., DNP3 Level 1 test set, IEC 61850 UCAIug ICT, OPC UA CTT (Compliance Test Tool).

## 5. System Architecture

```
            ┌────────────────────────────────────────────────┐
            │              Web UI / CLI / SDK                │
            └────────────────────────────────────────────────┘
                       │ REST + gRPC (mTLS)
            ┌──────────▼──────────────────────────────────┐
            │         Control Plane API (Go)              │
            │  - Scenario manager   - Fleet orchestrator  │
            │  - Auth (OIDC)        - Audit log           │
            └──────────┬──────────────────────────────────┘
                       │
       ┌───────────────┼─────────────────────────────────┐
       │               │                                 │
 ┌─────▼─────┐   ┌─────▼─────┐                     ┌─────▼─────┐
 │ Modbus    │   │ DNP3      │       ...           │ IEC 61850 │
 │ engine    │   │ engine    │                     │ engine    │
 └─────┬─────┘   └─────┬─────┘                     └─────┬─────┘
       │               │                                 │
       └────────────► Shared point bus (NATS) ◄──────────┘
                       │
               ┌───────▼────────┐
               │ Behavior VM    │  (Python/Lua/JS sandbox)
               │ + Fault engine │
               └───────┬────────┘
                       │
               ┌───────▼────────┐
               │ Time service   │  (wall / accelerated / step)
               └────────────────┘
```

Each protocol engine is a separate process for fault isolation. Devices are virtual entities composed of (a) an identity, (b) a point map, (c) one or more protocol bindings, and (d) optional behavior scripts. The shared point bus (NATS JetStream) lets a value written via the OPC UA face appear on the Modbus face of the same logical device, enabling protocol-bridging tests.

## 6. Data Models

### Device descriptor (YAML)

```yaml
device:
  id: inv-001
  template: sma-sunny-central
  identity:
    vendor: SMA
    model: Sunny Central 2500
    serial: SC2500-001
    firmware: 1.16.4
  bindings:
    - protocol: modbus_tcp
      listen: 0.0.0.0:5020
      unit_id: 1
    - protocol: sunspec
      models: [1, 101, 103, 120, 121, 122, 123, 124, 126]
    - protocol: opcua
      endpoint: opc.tcp://0.0.0.0:4840/inv-001
  points:
    - name: ac_power_kw
      type: float32
      modbus: { addr: 40083, fc: 4, scale: 1 }
      sunspec: { model: 103, point: W }
      opcua: { node: ns=2;s=AC.Power }
      behavior: "irradiance.value * 2500 * derate.value"
    - name: dc_voltage
      type: float32
      modbus: { addr: 40099, fc: 4 }
      behavior: { type: noisy_constant, mean: 1100, stddev: 5 }
  faults: []
```

### Scenario descriptor

```yaml
scenario:
  id: low-voltage-ride-through-test
  description: Simulate grid voltage sag per IEEE 2800 Table 16
  steps:
    - at: 00:00:00
      action: set_point
      target: substation/v_pos_seq
      value: 1.00
    - at: 00:00:10
      action: ramp_point
      target: substation/v_pos_seq
      from: 1.00
      to: 0.50
      duration_ms: 100
    - at: 00:00:10.500
      action: hold
      duration_ms: 500
    - at: 00:00:11
      action: ramp_point
      target: substation/v_pos_seq
      from: 0.50
      to: 1.00
      duration_ms: 200
  asserts:
    - type: tag_value
      tag: ppc/active_power_setpoint
      window: [00:00:11, 00:00:13]
      condition: ">= 0.95 * pre_fault_value"
```

## 7. API Contracts

### REST (OpenAPI excerpt)

```
POST   /api/v1/devices                      # create device from descriptor
GET    /api/v1/devices/{id}
DELETE /api/v1/devices/{id}
POST   /api/v1/devices/{id}/start
POST   /api/v1/devices/{id}/stop
PUT    /api/v1/devices/{id}/points/{name}   # body: {"value": 42.0, "quality": "good"}
POST   /api/v1/devices/{id}/faults          # body: fault descriptor
DELETE /api/v1/devices/{id}/faults/{fid}
POST   /api/v1/scenarios/{id}/run
GET    /api/v1/scenarios/{id}/runs/{run_id}
WS     /api/v1/events                       # stream of point changes & comms events
```

### gRPC (protobuf excerpt)

```protobuf
service Emulator {
  rpc CreateDevice(DeviceDescriptor) returns (Device);
  rpc SetPoint(SetPointRequest) returns (PointState);
  rpc StreamEvents(EventFilter) returns (stream EmulatorEvent);
  rpc InjectFault(FaultRequest) returns (Fault);
  rpc RunScenario(ScenarioRequest) returns (stream ScenarioStep);
}
```

## 8. Tech Stack

- **Core**: Go 1.22+ for protocol engines (concurrency, performance, single-binary deployment)
- **Behavior VM**: Lua (gopher-lua) for low-overhead scripting; Python via embedded gRPC-py worker for complex behaviors
- **Protocols**: leverage well-known libraries where mature: `libiec61850` (LGPL), `pyDNP3 / opendnp3`, `open62541` (OPC UA), `libmodbus`, `libplctag` (CIP/EIP). Where licensing or fit is poor (e.g., DNP3 commercial), build native Go implementations.
- **Control plane**: Go + Connect-RPC + gRPC-gateway → REST
- **Bus**: NATS JetStream (lightweight, embedded mode possible)
- **UI**: React + TypeScript, Vite, Tailwind, TanStack Query
- **Storage**: SQLite for local config, PostgreSQL for multi-user deployments, MinIO/S3 for PCAPs and scenario artifacts
- **Container**: distroless base, multi-arch images
- **Orchestration**: Helm chart targeting Kubernetes 1.27+; docker-compose for desktop

## 9. Key Algorithms / Pseudocode

**Time-accurate scenario runner**

```python
def run_scenario(scenario, time_service):
    t0 = time_service.now()
    pending = sorted(scenario.steps, key=lambda s: s.at)
    while pending:
        step = pending[0]
        target_t = t0 + step.at
        time_service.sleep_until(target_t)
        execute(step)
        if step.action == "ramp_point":
            schedule_ramp_subtasks(step)
        pending.pop(0)
    for assertion in scenario.asserts:
        evaluate(assertion)
```

**Modbus exception fault injection** — wrap the response handler:

```go
func (s *ModbusServer) handleRead(req Request) Response {
    if f := s.faultEngine.Active(req.UnitID, req.Address); f != nil {
        switch f.Kind {
        case "exception":     return ExceptionResponse(f.Code)
        case "timeout":       time.Sleep(f.Duration); return nil
        case "corrupt_value": return s.normalRead(req).WithValue(f.Override)
        case "crc":           return s.normalRead(req).WithBadCRC()
        }
    }
    return s.normalRead(req)
}
```

## 10. Edge Cases

- **Serial port contention** (Modbus RTU): emulator should support virtual serial pairs (socat / com0com on Windows) and arbitrate access.
- **Multicast for GOOSE/SV**: requires raw sockets or `CAP_NET_RAW`; document the privilege requirement and provide a sidecar pattern.
- **Endianness mismatches**: SunSpec is big-endian, but many vendors fudge this. Provide per-binding word-swap and byte-swap toggles.
- **DNP3 unsolicited reporting**: must respect class assignments and event buffering; overflow behavior configurable.
- **Time sync**: in step mode, ensure GOOSE `t` field, IEC 61850 timestamps, and DNP3 timestamps all advance from the same virtual clock.
- **Conformance pitfalls**: OPC UA endpoints must produce valid `EndpointDescription` even when only the None security policy is enabled, or the Compliance Test Tool fails.

## 11. Ignition-Specific Integration

- The emulator runs *outside* Ignition; Ignition connects via its standard drivers (Modbus TCP, DNP3, OPC UA — most commonly via Kepware OPC UA aggregation, but native drivers exist).
- Provide a sample **Ignition project export (.proj)** wired to the emulator's default endpoints so users get a working SCADA in 10 minutes.
- Provide an **Ignition module** (Java, against the SDK 8.1+) that adds a "Connect to Emulator Fleet" gateway action, auto-creating Device Connections and importing UDT instances for every emulated device. Module manifest declares scope `G` (gateway).
- Provide a **Gateway script** (Jython 2.7) example that walks the emulator's `/api/v1/devices` and creates Tag Provider entries via `system.tag.configure`.
- Use the Web Dev module to expose a small in-Ignition UI for triggering scenarios (`POST /api/v1/scenarios/{id}/run`), so test runs can be initiated from a Perspective view.
- Tie into Ignition's Sequential Function Chart module for FAT execution (see Spec 8) — each SFC step can call the emulator REST API to set up preconditions.

## 12. Test Plan

- **Unit**: per-protocol encoder/decoder fuzzing (go-fuzz, AFL++); behavior VM correctness via golden tests.
- **Integration**: each protocol engine validated against a known-good client (libmodbus client, OPC UA Expert, AVEVA System Platform DI Object, real Schweitzer SEL-3530 lab unit for DNP3).
- **Conformance**: automate OPC UA CTT runs in CI; DNP3 conformance test set as nightly job.
- **Performance**: k6/locust scripts driving Modbus poll rates, GOOSE pub rates; SLA gates in CI.
- **Chaos**: Chaos Mesh injecting network loss between emulator pods and a test SCADA, verifying expected SCADA behavior.

## 13. Phased Rollout

| Phase | Duration | Scope |
|---|---|---|
| 0 — MVP | 8 weeks | Modbus TCP, OPC UA server, REST API, web UI, Helm chart, single-host fleet of 100 |
| 1 — Renewables | 8 weeks | SunSpec full models, MQTT/Sparkplug B, scenario library, Ignition sample project |
| 2 — Utility | 12 weeks | DNP3 outstation, IEC 60870-5-104, IEC 61850 MMS server, conformance test pass |
| 3 — Substation real-time | 10 weeks | GOOSE + SV publishers, multicast, time-sync hardening |
| 4 — Discrete/process | 8 weeks | EtherNet/IP, S7, BACnet, HART-IP |
| 5 — Hardening | ongoing | conformance, performance, security |

## 14. Success Metrics

- Time-to-first-test for a new project: from days (acquire/wire hardware) to < 1 hour.
- CI test suite runtime against 50 emulated devices: < 5 minutes.
- Number of field defects caught pre-FAT: tracked per project; target ≥ 30% of total defects shifted left.
- Adoption: % of new projects with emulator-based regression suites ≥ 70% within 18 months.
- Mean conformance test pass rate per supported protocol: ≥ 95%.
-e 

---


# Spec 2 — Screen Building from CAD Drawings or Pictures

## 1. Problem Statement

Building HMI/SCADA screens is one of the most time-consuming tasks in commissioning. A 100-MW solar plant has dozens of single-line diagrams, P&IDs, and mechanical layouts; engineers manually redraw every breaker, transformer, inverter, and combiner box in the SCADA, then bind each graphic to a tag. This work is repetitive, error-prone, and adds weeks to project schedules. A tool that ingests a CAD drawing (DWG/DXF), a P&ID PDF, or even a photograph of a sketched SLD, recognizes the symbols and topology, and generates a SCADA screen with tag bindings already in place would compress weeks of work into hours.

## 2. User Personas & Stories

**SCADA Application Engineer** — *"As a SCADA engineer, I want to drop a DXF of the plant SLD into a tool and get an Ignition Perspective view back with breakers, transformers, and inverters already drawn and bound to my tag database."*

**Project Engineer** — *"As a project engineer, I want to send my P&ID PDFs and have the SCADA screens auto-generated, so I don't have to maintain two parallel sets of drawings."*

**Retrofit/Brownfield Engineer** — *"As a brownfield engineer at a 30-year-old plant with no electronic drawings, I want to take a phone photo of the panel SLD and get a working SCADA screen."*

## 3. Functional Requirements

- **F1**: Ingest formats: DWG (AutoCAD R14 through 2024), DXF (R12 through 2018), PDF (vector-preferred, raster fallback), PNG/JPG/HEIC (photographs and scans), SVG, SLDPRT exports, Visio (.vsdx), Bentley MicroStation (.dgn).
- **F2**: Detect and classify electrical and process symbols using a configurable symbol library: breakers (drawout, fixed), disconnects, transformers (2W, 3W, auto), inverters, combiner boxes, trackers, BESS racks, motors, pumps, valves (gate, ball, butterfly, check), instruments (per ISA 5.1 bubble), tanks, vessels, heat exchangers.
- **F3**: Detect topology — line connections between symbols, with electrical bus identification (medium-voltage, low-voltage, AC vs DC) and process flow direction.
- **F4**: OCR all text labels (equipment tags, ratings, setpoints) using a model fine-tuned on engineering drawing fonts.
- **F5**: Match detected equipment to existing tag database (Spec 6) by tag name; suggest matches when fuzzy.
- **F6**: Generate output as: Ignition Perspective JSON view, Ignition Vision XML window, AVEVA InTouch graphic, generic SVG with metadata, and an editable intermediate format for manual touch-up.
- **F7**: Provide a review/edit web UI where the user accepts/rejects each detected symbol, drags to fix positions, and merges duplicates.
- **F8**: Iterative learning — corrections in the UI are captured as training data for site-specific symbol library improvements.
- **F9**: Maintain bidirectional traceability: each generated screen element links back to the source drawing element (page, layer, handle for DXF, bbox for raster).
- **F10**: Support custom symbol libraries — customers can upload their corporate symbol set as SVG + classification metadata.
- **F11**: Generate not just static graphics but interactive elements: popups for breaker open/close, faceplates for analog values, alarm indication overlays, animations bound to tag values.

## 4. Non-Functional Requirements

- **N1 Accuracy**: ≥ 95% symbol detection precision/recall on vector inputs (DXF/SVG/vector PDF) for standard ANSI/IEC libraries; ≥ 80% on hand-drawn raster.
- **N2 Throughput**: 1 standard SLD page processed in < 60 seconds on a single GPU.
- **N3 Footprint**: Inference can run on a workstation (16 GB GPU); cloud GPU offload optional.
- **N4 Privacy**: Drawings often contain confidential plant data; on-premises deployment supported, no telemetry of drawing content.
- **N5 Reproducibility**: Same input drawing always produces the same screen output for a given tool version.

## 5. System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    Web UI (React + Konva)                    │
│  Upload | Review symbols | Edit | Export | Train             │
└──────────────────────────────────────────────────────────────┘
                          │ REST + WebSocket
┌─────────────────────────▼────────────────────────────────────┐
│                  Orchestration API (Python)                  │
└─────┬───────────────┬────────────────┬───────────────┬──────┘
      │               │                │               │
┌─────▼─────┐  ┌──────▼──────┐  ┌─────▼─────┐  ┌──────▼──────┐
│ Vector    │  │ Raster      │  │ Symbol    │  │ Topology    │
│ ingest    │  │ ingest      │  │ classifier│  │ extractor   │
│ (libdxf,  │  │ (PDF→img,   │  │ (YOLO +   │  │ (graph      │
│  pdf2svg) │  │  upscale)   │  │  ResNet)  │  │  builder)   │
└─────┬─────┘  └──────┬──────┘  └─────┬─────┘  └──────┬──────┘
      │               │                │               │
      └───────────────┴────────┬───────┴───────────────┘
                               │
                    ┌──────────▼──────────┐
                    │ Intermediate Model  │   (canonical JSON
                    │ (DrawingGraph)      │    described below)
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │ Tag binder          │   (queries tag DB,
                    │ (fuzzy match,       │    Spec 6)
                    │  user-confirm)      │
                    └──────────┬──────────┘
                               │
   ┌───────────────────────────┼───────────────────────────┐
   ▼                           ▼                           ▼
┌─────────┐            ┌──────────────┐           ┌────────────┐
│ Ignition│            │ Vision XML   │           │ Generic    │
│ Perspect.│           │ exporter     │           │ SVG+meta   │
│ JSON    │            │              │           │            │
└─────────┘            └──────────────┘           └────────────┘
```

## 6. Data Models

### Canonical DrawingGraph (intermediate, JSON Schema excerpt)

```json
{
  "drawing": {
    "id": "uuid",
    "source": { "type": "dxf", "filename": "PLT-001-SLD.dxf", "sha256": "..." },
    "units": "mm",
    "bounds": { "minX": 0, "minY": 0, "maxX": 1189, "maxY": 841 },
    "pages": [{
      "index": 1,
      "symbols": [
        {
          "id": "sym-0001",
          "class": "circuit_breaker",
          "subclass": "drawout_lv",
          "position": { "x": 320.5, "y": 410.0 },
          "rotation": 0,
          "scale": 1.0,
          "bbox": { "x": 310, "y": 400, "w": 20, "h": 20 },
          "confidence": 0.97,
          "labels": [
            { "text": "52-A1", "role": "tag", "confidence": 0.98 },
            { "text": "1200A", "role": "rating",  "confidence": 0.91 }
          ],
          "ports": [
            { "id": "top", "x": 320.5, "y": 400 },
            { "id": "bottom", "x": 320.5, "y": 420 }
          ],
          "source_handle": "0x7A3F"
        }
      ],
      "connections": [
        {
          "id": "net-0001",
          "type": "electrical",
          "voltage_class": "MV",
          "endpoints": [
            { "symbol": "sym-0001", "port": "bottom" },
            { "symbol": "sym-0007", "port": "top" }
          ],
          "polyline": [[320.5, 420], [320.5, 480], [400, 480]]
        }
      ]
    }]
  }
}
```

### Symbol library entry

```yaml
symbol:
  id: ansi_breaker_drawout_lv
  display_name: Drawout LV Breaker (ANSI)
  class: circuit_breaker
  subclass: drawout_lv
  geometry_svg: <svg>...</svg>
  ports:
    - id: top
      x: 0
      y: -10
    - id: bottom
      x: 0
      y: 10
  default_bindings:
    - role: state
      tag_pattern: "{tag}/Status"
    - role: trip
      tag_pattern: "{tag}/Trip"
  faceplate: ansi_breaker_faceplate.json
```

## 7. API Contracts

```
POST   /api/v1/drawings                      # multipart upload
GET    /api/v1/drawings/{id}
GET    /api/v1/drawings/{id}/graph           # DrawingGraph JSON
POST   /api/v1/drawings/{id}/symbols/{sid}   # accept/edit/reject
POST   /api/v1/drawings/{id}/bind            # body: tag binding overrides
POST   /api/v1/drawings/{id}/export
        ?format=ignition_perspective|ignition_vision|svg|aveva
GET    /api/v1/symbol-library
POST   /api/v1/symbol-library/symbols        # upload custom symbol
POST   /api/v1/training/feedback             # capture user corrections
WS     /api/v1/drawings/{id}/events          # stream during processing
```

## 8. Tech Stack

- **Vector ingest**: ezdxf (Python) for DXF; pdfplumber + pikepdf for vector PDF; cairosvg for SVG normalization.
- **Raster ingest**: pdf2image, PIL, Real-ESRGAN for upscaling low-res scans, OpenCV for preprocessing (deskew, denoise, binarize).
- **Symbol detection**: YOLOv8 / YOLO-NAS for bounding-box detection, then a ResNet-50 fine-tune for symbol classification. Use Detectron2 for instance segmentation when symbols overlap.
- **OCR**: PaddleOCR or TrOCR fine-tuned on engineering-drawing text. RapidOCR for Windows-friendly deployment.
- **Topology**: NetworkX for graph operations; Hough transform + custom line-tracing for raster connections.
- **Backend**: Python 3.11 + FastAPI, Celery for async jobs, Redis for queue, MinIO/S3 for artifacts.
- **Frontend**: React 18 + Konva.js (canvas editor), TanStack Query, shadcn/ui.
- **Training**: PyTorch Lightning, Weights & Biases, automated dataset versioning with DVC.
- **Deployment**: Docker, GPU node pool in Kubernetes; CPU-only fallback for vector-only workflows.

## 9. Key Algorithms / Pseudocode

**End-to-end pipeline**

```python
def process_drawing(file: UploadedFile) -> DrawingGraph:
    raw = ingest(file)                       # → vector entities or raster image
    normalized = normalize(raw)              # uniform units, layers cleaned
    symbol_candidates = detect_symbols(normalized)
    symbols = classify(symbol_candidates)    # add subclass + confidence
    text_blocks = ocr(normalized)
    symbols = associate_labels(symbols, text_blocks)  # nearest-neighbor + heuristics
    lines = extract_lines(normalized)
    connections = trace_topology(symbols, lines)
    voltage_classes = infer_voltage_class(connections, symbols)
    return DrawingGraph(symbols, connections, voltage_classes)
```

**Tag binding (fuzzy match against Spec 6 tag DB)**

```python
def bind_tags(graph: DrawingGraph, tag_db: TagDB) -> DrawingGraph:
    for sym in graph.symbols:
        if sym.labels.get("tag"):
            candidates = tag_db.search(sym.labels["tag"], limit=5,
                                       fuzz_threshold=0.85)
            sym.binding = candidates[0] if candidates and candidates[0].score > 0.95 \
                          else PendingBinding(candidates=candidates)
    return graph
```

**Ignition Perspective view generation** — Perspective views are JSON; we emit a tree of `ia.display.svg` and `ia.shapes.*` components with `props.style` for color and `props.binding` for tag binding.

```python
def to_perspective(graph: DrawingGraph, project: str) -> dict:
    root = {"type": "ia.container.coord",
            "version": 0,
            "props": {"viewport": {"w": graph.bounds.w, "h": graph.bounds.h}},
            "children": []}
    for sym in graph.symbols:
        sym_def = library.get(sym.class_)
        comp = sym_def.to_perspective_component(sym)
        if sym.binding and sym.binding.is_resolved():
            comp["propConfig"] = {
                "props.value": {"binding": {"type": "tag",
                                            "config": {"tagPath": sym.binding.path}}}
            }
        root["children"].append(comp)
    for conn in graph.connections:
        root["children"].append(connection_to_polyline(conn))
    return root
```

## 10. Edge Cases

- **Mixed standards**: A drawing with both ANSI and IEC symbols on the same page — symbol classifier must be ANSI/IEC-aware and label each. Provide auto-conversion.
- **Multi-sheet drawings**: Off-sheet connectors (`A1 → sheet 3`) must be resolved; build a cross-sheet graph.
- **Rotated / mirrored symbols**: Detector and symbol library need rotation-invariant matching; store rotation in canonical model so renderers can re-rotate as needed.
- **Hand-drawn sketches**: ≥ 70% target accuracy; surface low-confidence symbols prominently in the review UI; never silently auto-accept low-confidence detections.
- **Layered DXFs**: Many CAD drawings have layers like "ANNOTATION," "TITLE_BLOCK" that should be excluded; provide layer filtering UI and presets per company standard.
- **Coordinate system flips**: DXF uses Y-up, screen coords are Y-down; flip exactly once.
- **Unit ambiguity**: DXF has unitless mode; provide a unit-detection heuristic (compare title block size to page size) and a manual override.
- **Title block / legend pollution**: Detect and exclude title blocks via OCR + bounding-box heuristics.

## 11. Ignition-Specific Integration

- Output Perspective views are written to `<project>/com.inductiveautomation.perspective/views/<view-path>/view.json` with companion `resource.json` and `thumbnail.png`.
- Output Vision windows are .vwin XML written to `<project>/com.inductiveautomation.vision/windows/<window>/window.xml`.
- An **Ignition module** with scope `D` (designer) adds a "Import Drawing" menu under Tools → Drawing Importer; opens a dialog that uploads to the screen-builder service and, when complete, calls the Designer API to write the resulting view files into the open project, then refreshes the project tree.
- Tag bindings use Ignition's tag path syntax — `[default]Plant/Inverter01/AC_Power`. The binder reads tag-provider names from Ignition's GatewayContext and uses the active project's default provider unless overridden.
- For brownfield SCADA migrations, support import of existing Vision windows so the AI symbol classifier can learn the customer's house style.

## 12. Test Plan

- **Dataset**: Curate a held-out test set of 200 representative drawings (vector and raster, ANSI and IEC, SLDs and P&IDs); track precision/recall per symbol class over time.
- **Golden output**: For 30 reference drawings, maintain hand-edited "perfect" Perspective views; CI compares structural diff (symbol count, class distribution, connection count) between generator output and golden.
- **User studies**: Time-to-screen for 5 SCADA engineers building the same plant from a DXF, with vs. without the tool; target ≥ 5× speedup.
- **Round-trip**: Export Perspective → screenshot → re-ingest as raster → expect ≥ 90% symbol recovery (sanity check on output fidelity).

## 13. Phased Rollout

| Phase | Duration | Scope |
|---|---|---|
| 0 — MVP | 10 weeks | DXF + vector PDF ingest, ANSI electrical SLD symbols only, SVG export, web review UI |
| 1 — Ignition export | 6 weeks | Perspective view generator, Ignition Designer module (import), tag-binding |
| 2 — IEC + P&ID | 8 weeks | IEC symbol library, P&ID symbols (ISA 5.1 instruments, valves), Vision export |
| 3 — Raster + photo | 12 weeks | Raster pipeline, hand-drawn support, training feedback loop |
| 4 — Brownfield/AVEVA | 8 weeks | InTouch / System Platform exporters, custom symbol libraries |
| 5 — Continuous | ongoing | model improvement, customer-specific symbol training |

## 14. Success Metrics

- Time to build a 10-page SLD-driven SCADA: from 80 hours to < 8 hours.
- Symbol detection precision ≥ 0.95 / recall ≥ 0.92 on vector benchmark; ≥ 0.85 / 0.80 on raster.
- User review time per page: < 5 minutes after first month of use.
- % of symbols accepted without edit: ≥ 90% target.
- NPS from project engineering teams ≥ 40 within 12 months.
-e 

---


# Spec 3 — Alarm Generation from Spreadsheets

## 1. Problem Statement

Alarm engineering is one of the most safety-critical and most-neglected aspects of SCADA work. ISA-18.2 / IEC 62682 prescribe a full lifecycle (philosophy → identification → rationalization → detailed design → implementation → operation → maintenance), but in practice most alarms are configured by hand, one at a time, in vendor-specific tools, with no rationalization record. The result is "alarm floods" that overwhelm operators and cause incidents like Texas City and Buncefield. Engineers already maintain alarm lists in spreadsheets — but transcribing those into Ignition, AVEVA, or other SCADAs is manual, slow, and lossy. A tool that ingests an ISA-18.2-compliant alarm rationalization spreadsheet and generates fully-configured SCADA alarms — with priority, deadband, delays, suppression logic, operator messages, and historian linkage — closes the gap between alarm engineering and alarm implementation.

## 2. User Personas & Stories

**Alarm Rationalization Lead** — *"As the lead facilitator of a HAZOP-derived alarm rationalization, I want to export the master alarm database to a SCADA configuration with one click, so the rationalization stays the single source of truth."*

**SCADA Application Engineer** — *"As a SCADA engineer, I want to drop a 5,000-row alarm spreadsheet into the tool and have all alarms created in Ignition with consistent priority, message, and grouping."*

**Operations / I&E Manager** — *"As ops management, I want a quarterly KPI report (per ISA-18.2) showing alarms per operator per hour, top 10 bad actors, alarm flood rates — automatically generated from the master alarm database and the historian."*

**Auditor** — *"As an internal/external auditor, I want to verify that every configured alarm in production matches the rationalization record, with full traceability to its rationale and operator response."*

## 3. Functional Requirements

- **F1**: Ingest an alarm rationalization spreadsheet conforming to a documented schema (XLSX, CSV, Google Sheets, ODS) — see §6.
- **F2**: Validate the spreadsheet against ISA-18.2 mandatory fields and customer-defined rules; provide a downloadable validation report with line/column-level errors.
- **F3**: Generate alarm configurations for: Ignition (Tag Alarm Properties via JSON or Designer SDK), AVEVA System Platform (.aaPKG), Wonderware InTouch, GE iFIX, Siemens WinCC, Schneider EcoStruxure Geo SCADA, Honeywell Experion, Emerson DeltaV.
- **F4**: Support all ISA-18.2 alarm attributes: priority (configurable mapping, default 4-tier Low/Med/High/Urgent), source tag, condition (HI/HIHI/LO/LOLO/Discrete/Deviation/Rate), setpoint, deadband, on-delay, off-delay, alarm message, operator action, consequence-of-inaction, time-to-respond.
- **F5**: Support advanced ISA-18.2 features:
  - State-based alarm enablement (suppress when unit is shutdown)
  - Suppression by design (chattering filter, off-delay)
  - Shelving (operator-initiated temporary suppression with timeout)
  - Out-of-service tagging (maintenance mode)
  - Alarm grouping and parent-child relationships (first-out logic)
  - Dynamic alarming (priority changes by mode)
  - Flood suppression (rate-based)
- **F6**: Bidirectional sync — read existing alarm config back from the SCADA into the master spreadsheet, with diff/merge UI for conflict resolution.
- **F7**: Generate ISA-18.2 KPI reports from historian data: alarm rate per hour per operator, peak rate during 10-min windows, top 10 bad actors, % time in flood, stale alarms, chattering alarms, suppressed alarms.
- **F8**: Audit log — every change to the master spreadsheet (who, when, why, before/after) with electronic-signature support per 21 CFR Part 11 for life-sciences customers.
- **F9**: Master Alarm Database (MADB) — central, versioned, queryable; the spreadsheet is an import/export view, not the system of record.
- **F10**: Bulk operations — find/replace, propagate priority changes across a class of equipment, regenerate messages from a Jinja template.
- **F11**: Templating: define alarm sets per equipment template (e.g., "centrifugal pump") and instantiate per-instance with tag substitution. Aligns with UDTs in Spec 6.

## 4. Non-Functional Requirements

- **N1 Scale**: 100,000 alarms in MADB; full export to Ignition in < 5 minutes.
- **N2 Reliability**: All-or-nothing transactional deploy — partial failure rolls back; never leaves SCADA in inconsistent state.
- **N3 Auditability**: Every generated alarm carries a stable identifier traceable back to the MADB row and its history.
- **N4 Standards**: Conform to ISA-18.2-2016 and IEC 62682:2022. Provide a checklist of which clauses are addressed.
- **N5 Security**: RBAC (alarm engineer, reviewer, approver, deployer), separation of duties, signed deployments.
- **N6 Multi-site**: Support multiple plants/sites with shared templates and per-site overrides.

## 5. System Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                     Web UI (React, AG Grid)                    │
│   Editor | Validation | Diff | KPI dashboards | Approvals      │
└────────────────────────────────────────────────────────────────┘
                              │ REST + WebSocket
┌─────────────────────────────▼──────────────────────────────────┐
│                  Master Alarm Database service                 │
│  - Versioning   - RBAC   - Audit log   - Approval workflow     │
└──────┬──────────────────────────────────────────────┬──────────┘
       │                                              │
┌──────▼──────────┐                            ┌──────▼──────────┐
│ Spreadsheet I/O │                            │ Validator       │
│ (XLSX/CSV/ODS)  │                            │ (rules engine)  │
└─────────────────┘                            └─────────────────┘
       │                                              │
       └──────────────────────┬───────────────────────┘
                              │
                  ┌───────────▼──────────┐
                  │ Generator framework  │
                  └─┬────────────┬───────┘
                    │            │
            ┌───────▼───┐  ┌─────▼──────┐  ... per SCADA
            │ Ignition  │  │ AVEVA      │
            │ generator │  │ generator  │
            └─────┬─────┘  └─────┬──────┘
                  │              │
                  ▼              ▼
            ┌──────────────────────────┐
            │   Deploy + Verify        │
            │   (idempotent, rollback) │
            └──────────────────────────┘
                              │
                  ┌───────────▼──────────┐
                  │ KPI engine           │
                  │ (reads historian)    │
                  └──────────────────────┘
```

## 6. Data Models

### Master Alarm Database (PostgreSQL — core tables)

```sql
CREATE TABLE alarm (
  id              UUID PRIMARY KEY,
  tag_path        TEXT NOT NULL,
  alarm_name      TEXT NOT NULL,         -- e.g., "PIT-101.HI"
  condition       alarm_condition NOT NULL, -- HI, HIHI, LO, LOLO, DISC, DEV, ROC
  setpoint        DOUBLE PRECISION,
  deadband        DOUBLE PRECISION,
  on_delay_ms     INT DEFAULT 0,
  off_delay_ms    INT DEFAULT 0,
  priority        SMALLINT NOT NULL,      -- 1 (urgent) .. 4 (low)
  classification  TEXT,                   -- e.g., "Safety", "Environmental", "Process"
  message         TEXT NOT NULL,
  operator_action TEXT NOT NULL,
  consequence     TEXT NOT NULL,
  time_to_respond INTERVAL,               -- e.g., '00:05:00'
  cause           TEXT,                   -- root cause if known
  suppression     JSONB,                  -- expression, state-based rules
  group_id        UUID REFERENCES alarm_group(id),
  parent_alarm    UUID REFERENCES alarm(id),
  rationalized_at TIMESTAMPTZ,
  rationalized_by TEXT,
  status          alarm_status NOT NULL DEFAULT 'draft',
  version         INT NOT NULL,
  CONSTRAINT uniq_per_tag_cond UNIQUE (tag_path, condition, version)
);

CREATE TABLE alarm_history (
  alarm_id        UUID,
  version         INT,
  changed_at      TIMESTAMPTZ,
  changed_by      TEXT,
  change_reason   TEXT,
  diff            JSONB,
  PRIMARY KEY (alarm_id, version)
);

CREATE TABLE deployment (
  id              UUID PRIMARY KEY,
  target_system   TEXT,           -- 'ignition:gateway-prod-01'
  alarm_set       UUID[],
  deployed_at     TIMESTAMPTZ,
  deployed_by     TEXT,
  signature       BYTEA,          -- detached signature of payload
  status          TEXT,
  rollback_of     UUID REFERENCES deployment(id)
);
```

### Spreadsheet schema (canonical worksheet `Alarms`)

| Column | Required | Type | Notes |
|---|---|---|---|
| TagPath | Y | string | Full hierarchical path |
| AlarmName | Y | string | Unique within tag |
| Condition | Y | enum | HI/HIHI/LO/LOLO/DISC/DEV/ROC |
| Setpoint | Conditional | number | Required for analog |
| Deadband | N | number | EU; absolute or % |
| OnDelaySec | N | number | Default 0 |
| OffDelaySec | N | number | Default 0 |
| Priority | Y | int 1–4 | 1 = Urgent |
| Classification | Y | string | Safety/Env/Process/Equip/etc. |
| Message | Y | string | Jinja template allowed |
| OperatorAction | Y | string | What operator must do |
| Consequence | Y | string | If no action |
| TimeToRespond | Y | string | "5m", "1h", etc. |
| EnableExpression | N | string | Tag expression for state-based suppression |
| GroupName | N | string | Logical group for first-out |
| ParentAlarm | N | string | Suppress this when parent active |
| Rationale | N | string | Free text |
| RationalizedBy | N | string | Person/team |
| RationalizedDate | N | date | ISO-8601 |

A second worksheet `Templates` defines reusable per-equipment alarm sets; a third `Sites` lists per-site overrides.

## 7. API Contracts

```
GET    /api/v1/alarms?tag_path=...&priority=1
POST   /api/v1/alarms                              # create or upsert
PUT    /api/v1/alarms/{id}
DELETE /api/v1/alarms/{id}
POST   /api/v1/alarms:bulkUpsert                    # body: array
POST   /api/v1/imports                              # upload spreadsheet
GET    /api/v1/imports/{id}                         # status, validation report
POST   /api/v1/exports                              # body: target system + filter
POST   /api/v1/deployments                          # body: target + alarm IDs
POST   /api/v1/deployments/{id}/rollback
GET    /api/v1/kpis/alarm-rate?from=...&to=...
GET    /api/v1/kpis/bad-actors?window=30d
```

## 8. Tech Stack

- **Backend**: Python 3.11 + FastAPI (alarm domain logic), Go for high-throughput generator workers.
- **DB**: PostgreSQL 15+ with row-level security, pg_audit for audit.
- **Spreadsheet**: openpyxl, pandas, defusedxml for XLSX safety.
- **Templating**: Jinja2 for messages and bulk operations.
- **Frontend**: React + AG Grid Enterprise (for the spreadsheet-like editor) + Recharts for KPIs.
- **Workflow**: Temporal.io for multi-step approvals and idempotent deployments.
- **Auth**: OIDC (Keycloak) with electronic-signature support, FIDO2 second factor for approvals.
- **Generators**: pluggable via a Python entry-point system; each plugin implements `generate(alarms) -> deployable_artifact` and `verify(target) -> diff`.

## 9. Key Algorithms / Pseudocode

**Validator**

```python
def validate_alarm(a: AlarmRow, ctx: Context) -> list[Issue]:
    issues = []
    if a.condition in {HI, HIHI, LO, LOLO} and a.setpoint is None:
        issues.append(Error("setpoint required for analog conditions"))
    if a.priority not in {1,2,3,4}:
        issues.append(Error("priority must be 1..4"))
    if a.deadband is not None and a.deadband < 0:
        issues.append(Error("deadband must be non-negative"))
    if not ctx.tag_db.exists(a.tag_path):
        issues.append(Error(f"tag {a.tag_path} not found in tag database"))
    if a.condition == HIHI and not exists_lower_priority(a, ctx):
        issues.append(Warning("HIHI without HI is unusual"))
    if len(a.message) > 80:
        issues.append(Warning("message > 80 chars may truncate on operator HMI"))
    if a.suppression and not parses_as_expression(a.suppression):
        issues.append(Error("suppression expression invalid"))
    return issues
```

**Ignition generator** — Ignition stores alarm config as properties on tags. Use the Gateway scripting API:

```python
def gen_ignition(alarms: list[Alarm], tag_provider: str) -> list[TagConfig]:
    tag_configs = defaultdict(lambda: {"alarms": []})
    for a in alarms:
        cfg = {
            "name": a.alarm_name,
            "mode": map_condition(a.condition),
            "setpointA": a.setpoint,
            "deadband": a.deadband or 0,
            "onDelay": a.on_delay_ms,
            "offDelay": a.off_delay_ms,
            "priority": a.priority,
            "displayPath": a.tag_path,
            "label": a.alarm_name,
            "notes": a.rationale,
            "associatedData": {
                "Action": a.operator_action,
                "Consequence": a.consequence,
                "TimeToRespond": str(a.time_to_respond),
                "RationalizationId": str(a.id),
            },
            "enabled": True,
        }
        if a.suppression:
            cfg["activePipeline"] = "suppression-router"
            cfg["expression"] = a.suppression["expression"]
        tag_configs[a.tag_path]["alarms"].append(cfg)
    return [{"path": p, **c} for p, c in tag_configs.items()]

def deploy_ignition(configs, gw_url, auth):
    # Use Gateway Web API or system.tag.configure via Gateway script
    return post(f"{gw_url}/data/tag/configure", json=configs, auth=auth)
```

**KPI: Alarms per 10-minute window per operator**

```sql
SELECT date_trunc('hour', occurred_at)
       + (extract(minute FROM occurred_at)::int / 10) * interval '10 min' AS window,
       operator_console,
       count(*) AS alarm_count
FROM   alarm_event
WHERE  occurred_at BETWEEN $1 AND $2
GROUP  BY 1, 2
ORDER  BY 1, 2;
-- Flag rows with alarm_count > 10 as 'flood' per ISA-18.2 5.5.2
```

## 10. Edge Cases

- **Tag-rename cascade**: When a tag is renamed in the tag DB, all alarms must follow; provide a foreign-key-like mechanism with a renamer transaction.
- **Unit changes**: Setpoint in psi vs kPa — record EU per alarm and prevent silent unit drift.
- **Deadband units**: Some SCADAs interpret deadband in EU, others in % of range; generator must convert correctly per platform.
- **Stale alarms** (active > 24h): KPI report must distinguish them from chattering.
- **Race conditions in deploy**: Two engineers deploy overlapping sets — use optimistic locking on alarm version.
- **Operator-shelved alarms during a deploy**: Deploy must preserve the shelve state where possible (Ignition does via tag annotations).
- **Discrete (boolean) alarms**: No setpoint; condition is "active when true" or "active when false." Validator must enforce.
- **Calculated alarms** (Ignition expression alarms): Allow but validate expression syntax server-side via Ignition's expression parser.

## 11. Ignition-Specific Integration

- Ignition stores alarms as JSON properties on tags (8.1+). Use the Gateway Web API endpoint `/data/tag/configure` (or a Module SDK gateway hook for older versions) to apply.
- Ignition's `system.alarm.queryStatus` and `system.alarm.queryJournal` are used by the KPI engine to read live and historical alarm data; we issue these via Gateway Scripting through the Web Dev module or a dedicated module endpoint.
- Provide an **Ignition module** with scope `GD` adding:
  - Designer panel "Alarm Sync" showing diff between MADB and current tag config
  - Gateway scheduled task that periodically pushes MADB state to tags (drift correction)
  - Perspective component "Alarm Rationalization Lookup" — operators see the rationalized message, action, and consequence in the alarm faceplate
- Use Ignition Pipeline notifications for routing: alarm priority maps to a notification pipeline (e.g., Urgent → SMS + voice; Low → email digest).
- Integrate with Ignition's "associated data" feature so KPI dashboards can drill from a bad-actor alarm down to its rationalization record.

## 12. Test Plan

- **Schema**: 200 sample spreadsheets (good and bad) with expected validation outcomes; CI golden tests.
- **Generators**: Round-trip — generate, deploy to test Ignition gateway, read back, compare; tolerate known platform-specific normalizations (e.g., spaces collapsed).
- **Performance**: 100k alarm bulk import < 60 s; deploy of 10k changed alarms < 5 min.
- **KPI accuracy**: Validate against hand-computed ISA-18.2 metrics for a known historian dataset.
- **Compliance**: Map each test to an ISA-18.2 clause; produce a coverage report.

## 13. Phased Rollout

| Phase | Duration | Scope |
|---|---|---|
| 0 — MVP | 6 weeks | XLSX import, MADB, validator, Ignition deploy, basic UI |
| 1 — Lifecycle | 8 weeks | Versioning, audit log, approvals, rollback |
| 2 — Templating | 6 weeks | Equipment templates, multi-site, bulk ops, Jinja messages |
| 3 — KPIs | 8 weeks | KPI engine, dashboards, bad-actor reports |
| 4 — Multi-platform | 12 weeks | AVEVA, iFIX, WinCC, Schneider generators |
| 5 — Advanced | 8 weeks | State-based suppression, shelving sync, Part 11 e-sig |

## 14. Success Metrics

- Time to configure 1,000 alarms: from > 1 week manual to < 1 day.
- Alarm rationalization compliance audit pass rate: ≥ 95%.
- Operator alarm rate (ISA-18.2 target ≤ 1/10 min steady state): show 30% reduction within 6 months for sites using KPIs.
- % of deployed alarms with full ISA-18.2 mandatory fields: 100%.
- Engineering hours saved per project: ≥ 200 hours on average.
-e 

---


# Spec 4 — Historian Setup from Spreadsheets

## 1. Problem Statement

A modern industrial historian (Ignition Tag Historian, AVEVA PI, Canary, InfluxDB, TimescaleDB, AspenTech IP.21, Honeywell Uniformance) typically holds tens of thousands of tags, each with its own scan rate, deadband, compression configuration, retention policy, aggregation rule, and access permission. Configuring this by hand is error-prone and unscalable; misconfiguration leads to either disk-bloat (over-collection) or data loss (under-collection or aggressive compression). Engineers already maintain tag lists in spreadsheets; we want a tool that ingests a spreadsheet, computes optimal storage parameters, configures the chosen historian backend, and provides drift detection between the spreadsheet (system of record) and the live historian.

## 2. User Personas & Stories

**SCADA / Historian Engineer** — *"Give me a spreadsheet-driven workflow to provision 30,000 tags into Ignition Tag Historian or PI with the right compression and retention for each measurement type."*

**Reliability Engineer / Data Scientist** — *"As a data consumer, I want to know that the data I'm analyzing was actually captured at the rate I think it was, with the compression I expect — and that retention won't expire before my study window."*

**Storage / Infra Engineer** — *"Tell me how much disk and IOPS my historian will need before I provision the storage; let me model the impact of changing scan rates."*

**Data Governance Officer** — *"Each tag should have an owner, a classification (PII/non-PII, ITAR, regulated), and access controls — and I need a report of who can see what."*

## 3. Functional Requirements

- **F1**: Ingest spreadsheet (XLSX/CSV) with the historian configuration schema (§6).
- **F2**: Validate against schema and against the upstream tag DB (Spec 6) — no orphan tags, no type mismatches.
- **F3**: Compute recommended scan rate, deadband, compression deviation, and retention based on:
  - Measurement type (temperature, pressure, flow, electrical, position, status, totalizer)
  - Process dynamics (slow/medium/fast/event)
  - Required analytics use cases (trending, MPC, regulatory reporting)
  - Storage cost model
- **F4**: Generate provisioning artifacts for: Ignition Tag Historian (history-enabled tag config + retention partition policy), PI System (PI Module Database + PI ICU configuration via PI Web API), Canary (CSV import format), InfluxDB 2.x (line-protocol seed + bucket/retention policy), TimescaleDB (table + hypertable + continuous aggregate DDL).
- **F5**: Compute and report storage forecast: bytes/day, partition sizing, growth over 1/3/5/10 years.
- **F6**: Aggregation rules: define continuous aggregates (1m, 5m, 1h, 1d) with min/max/avg/sum/stddev/count and downsampling/retention per tier.
- **F7**: Access control: per-tag or per-tag-group RBAC, integrated with the customer's IdP (LDAP/AD/OIDC), reflected into the historian's native ACLs where supported.
- **F8**: Drift detection: scheduled comparison of spreadsheet config vs live historian; surface diffs with a remediation workflow.
- **F9**: Bulk migration: read existing historian config and reverse-engineer the spreadsheet (brownfield onboarding).
- **F10**: Backfill orchestration: when scan rate or compression changes, optionally backfill from another data source (raw OPC UA log, parallel historian, lab data) and re-run aggregations.
- **F11**: Multi-site / federated historian topology: one master spreadsheet, generators per site historian, with site-prefixed namespaces.

## 4. Non-Functional Requirements

- **N1 Scale**: 200,000 tag config; provision in < 10 minutes; storage forecasts in < 30 s.
- **N2 Idempotent**: Running the same config twice is a no-op; differential application only changes what's changed.
- **N3 Safe**: Destructive changes (retention shorten, drop aggregate, change compression that loses data) require explicit confirmation and audit log entry.
- **N4 Fidelity**: Storage forecast within ±15% of actual measured 30 days post-deploy.
- **N5 Observability**: Emit metrics on actual storage growth per tag group; alert on deviation from forecast.

## 5. System Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                    Web UI (React, AG Grid)                     │
│  Editor | Forecast | Diff | Backfill | Governance              │
└────────────────────────────────────────────────────────────────┘
                              │ REST
┌─────────────────────────────▼──────────────────────────────────┐
│                       Configuration Service                    │
│  - Versioned config store   - RBAC   - Approval workflow       │
└──┬───────────────────────────────────────────────┬────────────┘
   │                                               │
┌──▼─────────────┐    ┌──────────────┐    ┌──────▼──────────┐
│ Validator       │    │ Optimizer    │    │ Forecast engine │
│ (schema + cross-│    │ (recommends  │    │ (storage / IOPS │
│  ref tag DB)    │    │  scan/comp)  │    │  modeling)      │
└────────────────┘    └──────────────┘    └─────────────────┘
                              │
                  ┌───────────▼──────────┐
                  │ Generator framework  │
                  └───┬──────────────┬───┘
                      │              │
        ┌─────────────▼──┐  ┌────────▼─────────┐ ... per backend
        │ Ignition       │  │ PI System        │
        │ Tag Historian  │  │ (PI Web API)     │
        │ generator      │  │ generator        │
        └────────────────┘  └──────────────────┘
                              │
                  ┌───────────▼──────────┐
                  │ Drift detector       │
                  │ (scheduled, cron)    │
                  └──────────────────────┘
                              │
                  ┌───────────▼──────────┐
                  │ Backfill orchestrator│
                  │ (Temporal workflow)  │
                  └──────────────────────┘
```

## 6. Data Models

### Spreadsheet (worksheet `Tags`)

| Column | Required | Type | Notes |
|---|---|---|---|
| TagPath | Y | string | Hierarchical, matches tag DB |
| DataType | Y | enum | Float / Int / Bool / String / Enum |
| EngineeringUnits | Conditional | string | For analog |
| MeasurementClass | Y | enum | Temperature / Pressure / Flow / Electrical / Position / Status / Totalizer / Counter / Custom |
| ProcessDynamics | Y | enum | Slow / Medium / Fast / Event |
| ScanRateMs | N | int | Override; otherwise computed |
| DeadbandMode | N | enum | Off / Absolute / Percent / SmartCompression |
| DeadbandValue | N | number | EU or % |
| CompressionDeviation | N | number | PI-style; otherwise computed |
| CompressionMaxTimeSec | N | int | Force a sample at least this often |
| Retention | Y | string | "30d","2y","forever" |
| AggregationLevels | N | string | Comma-separated, e.g., "1m,5m,1h,1d" |
| AggregateRetention | N | string | Per-level, e.g., "1m:90d,5m:1y,1h:5y,1d:forever" |
| Owner | Y | string | Responsible person/team |
| Classification | Y | enum | Public / Internal / Restricted / Regulated |
| AccessGroup | Y | string | RBAC group(s), comma-separated |
| Description | Y | string | Human-readable |
| Backfill | N | string | Source URI for backfill |

A second worksheet `Profiles` predefines combinations (e.g., `electrical_power`: scan 1s, deadband 0.5%, retention 5y, aggregates 1m/1h/1d).

### Storage forecast model (per tag)

```
samples_per_day = 86_400_000 / scan_rate_ms
compressed_factor = expected compression ratio per measurement_class & deadband
                    (lookup table built from empirical study; 5–50× typical)
bytes_per_sample = 16 (PI), 24 (Ignition default), 18 (TimescaleDB), …
bytes_per_day = samples_per_day * bytes_per_sample / compressed_factor
```

Roll up by tag group; show p50/p90 forecast bands.

## 7. API Contracts

```
GET    /api/v1/tags?provider=...
POST   /api/v1/tags:bulkUpsert
POST   /api/v1/imports                # upload spreadsheet
POST   /api/v1/forecasts              # body: filter or full-config
POST   /api/v1/deployments            # body: target backend + filter
POST   /api/v1/deployments/{id}/dryRun
GET    /api/v1/deployments/{id}/diff
POST   /api/v1/backfills              # body: tag(s), source, time-range
GET    /api/v1/drift?provider=...
POST   /api/v1/aggregates             # body: hierarchy of CAGGs
```

## 8. Tech Stack

- **Backend**: Python (FastAPI) for orchestration; Go for PI Web API and Ignition deploy workers.
- **DB**: PostgreSQL for config and audit; the tool itself does *not* store time-series.
- **Workflow**: Temporal.io (long-running deploys, backfills).
- **Forecasting**: numpy + a small empirical compression model (per measurement class) maintained as a versioned dataset.
- **Backfill**: Apache Arrow Flight for fast tag-data transfer; per-historian connectors for read.
- **Frontend**: React + AG Grid + Plotly (forecast charts).
- **Auth/IdP**: OIDC; bridge to LDAP/AD for group sync.

## 9. Key Algorithms / Pseudocode

**Scan-rate optimizer (heuristic)**

```python
DEFAULTS = {
    ("Temperature","Slow"):   {"scan":  5000, "deadband": 0.1,  "comp_dev": 0.2},
    ("Temperature","Medium"): {"scan":  1000, "deadband": 0.05, "comp_dev": 0.1},
    ("Pressure","Fast"):      {"scan":   200, "deadband": 0.5,  "comp_dev": 1.0},
    ("Flow","Medium"):        {"scan":   500, "deadband": 0.5,  "comp_dev": 1.0},
    ("Electrical","Fast"):    {"scan":   100, "deadband": 0.25, "comp_dev": 0.5},
    ("Status","Event"):       {"scan":     0, "deadband": None, "comp_dev": None}, # change-driven
    ("Totalizer","Slow"):     {"scan": 60000, "deadband": 1.0,  "comp_dev": None}, # always store
    # ...
}

def recommend(row: TagRow) -> StorageParams:
    profile = DEFAULTS[(row.measurement_class, row.process_dynamics)]
    if row.scan_rate_ms is not None: profile["scan"] = row.scan_rate_ms
    if row.deadband_value is not None:
        profile["deadband"] = (row.deadband_value, row.deadband_mode)
    return StorageParams(**profile)
```

**Storage forecast**

```python
def forecast(tags: list[TagRow], horizon_days: int) -> dict:
    total = 0
    per_class = defaultdict(int)
    for t in tags:
        p = recommend(t)
        if p.scan == 0:
            samples = estimate_event_rate(t)  # 100/day default if unknown
        else:
            samples = 86_400_000 / p.scan
        cf = COMPRESSION_TABLE[(t.measurement_class, p.deadband)]
        bpd = samples * BYTES_PER_SAMPLE[t.target_backend] / cf
        total += bpd * horizon_days
        per_class[t.measurement_class] += bpd * horizon_days
    return {"total_bytes": total, "by_class": per_class}
```

**Ignition Tag Historian deploy** — set `historyEnabled` and history-related properties on tags via Gateway API:

```python
def deploy_ignition_history(tags, gw_url, provider):
    config = []
    for t in tags:
        config.append({
            "path": t.tag_path,
            "valueSource": "memory",  # preserved; we only patch history props
            "historyEnabled": True,
            "historyProvider": provider,           # e.g. "PI Hist Provider"
            "historyTagGroup": map_group(t.scan_rate_ms),
            "deadbandMode": map_deadband(t.deadband_mode),
            "deadband": t.deadband_value or 0,
            "deadbandEvalRate": "10s",
            "historicalDeadband": t.compression_deviation or 0,
            "historicalDeadbandStyle": "Auto",
            "historicalDeadbandMode": map_deadband(t.deadband_mode),
            "historicalSampleRate": t.scan_rate_ms,
            "tagGroup": map_group(t.scan_rate_ms),
            "documentation": t.description,
            "tooltip": t.description,
            "engUnit": t.eu,
            "permissions": map_acl(t.access_group),
        })
    return post(f"{gw_url}/data/tag/configure", json=config)
```

**TimescaleDB DDL generator**

```sql
-- per measurement-class hypertable
CREATE TABLE ts_pressure (time TIMESTAMPTZ, tag TEXT, value DOUBLE PRECISION,
                           quality SMALLINT);
SELECT create_hypertable('ts_pressure','time', chunk_time_interval => interval '1 day');

-- continuous aggregates per AggregationLevels
CREATE MATERIALIZED VIEW ts_pressure_1m
WITH (timescaledb.continuous) AS
SELECT time_bucket('1 minute', time) AS bucket, tag,
       avg(value) AS avg, min(value) AS min, max(value) AS max,
       count(*)   AS n
FROM   ts_pressure
GROUP  BY bucket, tag;

SELECT add_retention_policy('ts_pressure',     interval '90 days');
SELECT add_retention_policy('ts_pressure_1m',  interval '1 year');
SELECT add_retention_policy('ts_pressure_1h',  interval '5 years');
```

## 10. Edge Cases

- **Boolean / string tags**: No deadband; force change-driven storage; warn on attempts to set deadband.
- **Wrap-around totalizers**: Special compression — never lose a wrap event; force store on counter rollover.
- **Quality codes**: Some historians (PI) treat bad-quality as null; ensure forecasts and aggregates handle null.
- **Time-zone drift**: Always store UTC internally; UI converts on read.
- **Renamed tags**: Provide rename support that preserves history continuity (alias mapping in the historian where supported).
- **Out-of-order data**: Configure backend tolerance windows (PI: out-of-order interval; Influx: precision; Timescale: chunk reorder).
- **Multi-master conflicts**: If two engineers deploy overlapping changes, use deployment optimistic locking.
- **Deletion semantics**: Removing a tag from spreadsheet does NOT delete history by default; require an explicit "purge" operation that is logged.

## 11. Ignition-Specific Integration

- Ignition Tag Historian uses tag groups for scan rates. Generator maps spreadsheet `ScanRateMs` to existing or auto-created tag groups (e.g., "Default100ms", "Slow5s").
- Provide an **Ignition module** (scope GD) that adds:
  - Designer panel "Historian Sync" — diff, deploy, drift
  - Gateway scheduled drift-detection task
  - Perspective component "Tag Health" — visualizes actual vs configured scan rate
- Use Ignition's `system.tag.configure` (Gateway scope) for atomic bulk apply; for very large batches, use the Web API with chunking and a transaction wrapper so partial failures roll back via a compensating "undo" config snapshot.
- Integrate with Ignition Tag Provider model: the spreadsheet can specify a per-tag provider, supporting the realistic case of multiple providers (e.g., default + edge providers).
- For storage forecasting, query `system.tag.queryTagHistory` and the underlying historian's storage stats (Postgres/MySQL `pg_relation_size`, MSSQL DMVs) to ground the empirical model in customer data.

## 12. Test Plan

- **Schema**: 100 sample spreadsheets covering all measurement classes + edge cases.
- **Forecast accuracy**: Deploy a 1,000-tag pilot, measure storage growth for 30 days, compute forecast error, target ≤ 15%.
- **Round-trip**: Deploy → read back from historian → diff against spreadsheet → expect zero diff except for documented platform normalizations.
- **Drift**: Manually mutate config in Ignition / PI; verify drift detector flags within next scheduled run.
- **Backfill**: Verify backfilled data preserves correct timestamps and quality.
- **Performance**: 200k tag deploy < 10 min on a single gateway; < 30 min federated across 10.

## 13. Phased Rollout

| Phase | Duration | Scope |
|---|---|---|
| 0 — MVP | 6 weeks | Spreadsheet I/O, validator, Ignition Tag Historian generator, basic forecast |
| 1 — Lifecycle | 6 weeks | Versioning, audit, drift detection, RBAC |
| 2 — Multi-backend | 12 weeks | PI, Canary, InfluxDB, TimescaleDB generators |
| 3 — Aggregation | 6 weeks | Continuous aggregates, retention tiers, queries |
| 4 — Backfill & migration | 8 weeks | Cross-historian backfill, brownfield read-back |
| 5 — Governance | 6 weeks | Classification reports, IdP integration, automated audits |

## 14. Success Metrics

- Time to provision 10,000 historian tags: from > 1 week to < 1 day.
- Storage forecast error (at 30 days): ≤ 15% on average.
- Zero unplanned data loss incidents in pilot deployments (no inadvertent retention shortening).
- % of historian tags with documented owner & classification: 100% on managed sites.
- Drift incidents auto-detected within 24 hours: ≥ 95%.
-e 

---


# Spec 5 — IO List Generation from Plant Design (PlantPredict / PVCase)

## 1. Problem Statement

For utility-scale renewable projects, the design topology — inverter count and arrangement, combiner box assignments, tracker rows, met stations, transformers, BESS containers, the substation single-line — lives in design tools like PlantPredict (DNV), PVCase (now part of Trimble), Helioscope, Aurora, OpenSolar, and PVsyst, plus electrical CAD (AutoCAD Electrical, ETAP, EasyPower). The SCADA team then re-derives an IO list by hand: for every device, every signal, with every modbus address (when known), every scaling factor, every alarm threshold. This handoff is repeated multiple times as the design evolves, with errors flowing into the SCADA, the PLC, and the commissioning checklist. A tool that ingests the design tool output, applies device templates per make/model, and emits a consistent IO list — wired into the rest of this toolchain (tag DB, alarms, screens, FAT) — eliminates this friction.

## 2. User Personas & Stories

**Renewable SCADA Engineer** — *"As a SCADA engineer, I want to drop the PlantPredict / PVCase project export and get a complete IO list with all inverter, tracker, met, BESS, and substation signals — already mapped to the device's actual Modbus or SunSpec address — so I can move directly into tag DB and screen generation."*

**Project Engineering Manager** — *"As a PEM, I want the design-to-IO-list workflow to be reproducible and auditable so design revisions don't trigger weeks of rework."*

**Procurement / Commissioning** — *"I want to know early which signals require additional cards or sensors not provided by the inverter natively — for example, irradiance pyranometers and back-of-module temperature for performance ratio."*

## 3. Functional Requirements

- **F1**: Ingest design tool exports:
  - PlantPredict project export (JSON via API + report PDF + CSV BOM)
  - PVCase: AutoCAD DWG with PVCase blocks, plus BOM CSV
  - Helioscope: project export (CSV / JSON via API)
  - PVsyst: .PRJ + .CSV reports
  - ETAP: ETAPS project export (XML)
  - Generic: structured plant topology spreadsheet for non-PV designs
- **F2**: Build a normalized **Plant Topology Model** (PTM) — see §6.
- **F3**: Apply per-device-make-and-model templates from a curated library (e.g., SMA Sunny Central 2500-EV, Power Electronics FS3530K, Sungrow SG3125HV-MV-30, Tesla Megapack 2 XL, Nextracker NX Horizon, Array Technologies DuraTrack, Soltec SF7, Kipp & Zonen pyranometers) — each template enumerates every IO signal, scaling, EU, alarm class.
- **F4**: Resolve per-instance addressing:
  - Modbus base address per device (assigned by gateway, sometimes vendor-fixed)
  - SunSpec model auto-discovery (where supported) or static override
  - DNP3 point indices for utility-grade devices
  - IEC 61850 logical node mapping for substation devices
- **F5**: Derive aggregations: per combiner box (sum of strings), per inverter block (sum of inverters), per AC harness (sum of inverters into a step-up), plant-level totals.
- **F6**: Output formats: standardized IO list XLSX (per the chosen company convention), JSON, CSV, and direct push to tag DB (Spec 6).
- **F7**: Highlight gaps: signals required by the SCADA spec that the device does not natively provide; flag for additional sensor or signal.
- **F8**: Versioned & diff-able: design revisions produce a new IO list version with a clear diff (what changed, what added, what removed).
- **F9**: Multi-make support: a project may mix vendors (e.g., two inverter brands, three tracker brands); template library handles all without manual reconciliation.
- **F10**: Substation IO: integrate with single-line (Spec 2 & 6) so substation device IO (relays, RTUs, transformers, breakers) is derived consistently with PV-side IO.
- **F11**: Library management — add new device templates via UI; community contribution model with optional vendor verification.
- **F12**: Generate companion artifacts: Modbus map document (PDF), comms architecture diagram, BoM-with-signals report.

## 4. Non-Functional Requirements

- **N1 Coverage**: Day-1 device template library covers ≥ 80% of utility-scale PV/BESS market by units shipped (top 10 inverter OEMs, top 5 tracker OEMs, top 3 BESS OEMs, top 5 met-station vendors, common substation relays).
- **N2 Accuracy**: 100% match to the device manufacturer's published register map for templated devices (verified by automated tests against vendor PDFs / register CSVs).
- **N3 Throughput**: A 200-MW plant (~80 inverters, ~3,000 strings, full BESS, met & substation) generates a complete IO list in < 60 seconds.
- **N4 Versioning**: Every IO list run is reproducible from inputs + tool version + template library version.
- **N5 Standards conformance**: Output naming aligns with IEC 61400-25 (wind), IEC 61850 (substation), SunSpec (PV), IEC 81346 (general) where applicable.

## 5. System Architecture

```
┌────────────────────────────────────────────────────────────────┐
│   Web UI (React) — project, topology, devices, IO viewer       │
└────────────────────────────────────────────────────────────────┘
                              │ REST
┌─────────────────────────────▼──────────────────────────────────┐
│                       IO List Service                          │
└──┬───────────────────┬─────────────────────────────┬──────────┘
   │                   │                             │
┌──▼─────────────┐  ┌──▼──────────────┐    ┌────────▼─────────┐
│ Importers      │  │ Topology builder│    │ Address resolver │
│ - PlantPredict │  │ (graph)         │    │ (Modbus/SunSpec/ │
│ - PVCase DWG   │  │                 │    │  DNP3/IEC 61850) │
│ - Helioscope   │  └─────────────────┘    └──────────────────┘
│ - PVsyst       │           │                       │
│ - ETAP         │           └─────────┬─────────────┘
│ - Generic XLSX │                     │
└────────────────┘            ┌────────▼────────┐
                              │ Template engine │
                              │ (device library)│
                              └────────┬────────┘
                                       │
                   ┌───────────────────┼─────────────────────┐
                   ▼                   ▼                     ▼
            ┌────────────┐     ┌──────────────┐     ┌──────────────┐
            │ XLSX/CSV   │     │ Tag DB push  │     │ Companion    │
            │ output     │     │ (Spec 6)     │     │ artifacts    │
            └────────────┘     └──────────────┘     └──────────────┘
```

## 6. Data Models

### Plant Topology Model (JSON Schema excerpt)

```json
{
  "project": {
    "id": "uuid", "name": "Sunny Acres 200 MW",
    "site": {"lat": 35.0, "lon": -106.6, "tz": "America/Denver"},
    "ac_capacity_mw": 200, "dc_capacity_mwdc": 280,
    "interconnection": "PJM-XYZ-2024-001"
  },
  "devices": [
    {
      "id": "INV-001", "type": "inverter", "make": "SMA",
      "model": "Sunny Central 2500-EV", "firmware": "1.16.4",
      "rating_kva": 2500, "ac_voltage_v": 690,
      "comms": {"protocol": "modbus_tcp", "ip": "10.10.10.11",
                "unit_id": 3, "sunspec": true},
      "parent": "BLK-01",   "children": ["CB-001-01", "CB-001-02", ...]
    },
    {
      "id": "CB-001-01", "type": "combiner_box", "make": "Shoals",
      "string_count": 24, "ratings": {"input_v": 1500, "input_a": 20},
      "comms": {"protocol": "modbus_rtu", "bus": "RS485-1", "unit_id": 11},
      "parent": "INV-001",  "children": ["STR-...x24"]
    },
    {
      "id": "TRK-ROW-0001", "type": "tracker", "make": "Nextracker",
      "model": "NX Horizon", "rows": 1, "modules_per_row": 90,
      "comms": {"protocol": "modbus_rtu", "bus": "RS485-2", "unit_id": 1},
      "parent": "BLK-01"
    },
    {
      "id": "MET-01", "type": "met_station",
      "components": [
        {"type": "pyranometer_poa", "model": "Kipp&Zonen SMP10"},
        {"type": "pyranometer_ghi", "model": "Kipp&Zonen SMP10"},
        {"type": "back_of_module_temp", "model": "PT-1000"},
        {"type": "ambient_temp_rh", "model": "Vaisala HMP155"},
        {"type": "wind_speed_dir", "model": "Gill WindSonic"}
      ],
      "comms": {"protocol": "modbus_rtu", "unit_id": 50}
    },
    {
      "id": "BESS-01", "type": "bess_container", "make": "Tesla",
      "model": "Megapack 2 XL", "rating_mwh": 3.9, "rating_mw": 1.9,
      "comms": {"protocol": "modbus_tcp", "ip": "10.10.20.21"}
    },
    {
      "id": "T-MAIN", "type": "power_transformer",
      "rating_mva": 230, "ratio": "34.5kV/230kV",
      "monitors": ["dga", "winding_temp", "oil_temp", "tap_position"],
      "comms": {"protocol": "iec61850_mms", "ied_name": "T_MAIN"}
    },
    {
      "id": "POI", "type": "interconnection_point",
      "voltage_kv": 230, "isorto": "PJM"
    }
  ],
  "edges": [
    {"from": "INV-001",  "to": "T-PAD-01",  "type": "AC_LV",  "voltage_v": 690},
    {"from": "T-PAD-01", "to": "BUS-MV",    "type": "AC_MV",  "voltage_v": 34500},
    {"from": "BUS-MV",   "to": "T-MAIN",    "type": "AC_MV"},
    {"from": "T-MAIN",   "to": "POI",       "type": "AC_HV",  "voltage_v": 230000}
  ]
}
```

### Device template (YAML)

```yaml
template:
  id: sma_sunny_central_2500_ev
  make: SMA
  model: Sunny Central 2500-EV
  protocol_defaults:
    modbus_tcp: {unit_id: 3}
    sunspec: {model_ids: [1, 11, 101, 103, 120, 121, 122, 123, 124, 126, 127, 128, 129]}
  signals:
    - name: AC_Power
      type: float32
      eu: kW
      direction: read
      sources:
        modbus: {addr: 40083, fc: 4, scale: 0.1, swap: BE}
        sunspec: {model: 103, point: W}
      class: electrical
      criticality: critical
    - name: AC_PowerFactor
      type: float32
      eu: pu
      direction: read
      sources:
        modbus: {addr: 40087, fc: 4, scale: 0.001}
    - name: SetPoint_PMax
      type: uint16
      eu: kW
      direction: write
      sources:
        modbus: {addr: 41000, fc: 6}
    # ... ~120 signals for a typical Sunny Central
  alarms:
    - name: GridUnderVolt
      condition: AC_Voltage < 0.85 * V_nom
      priority: 1
    # ...
  derived:
    - name: PerformanceRatio
      expression: "AC_Power / (POA_Irradiance * DC_Capacity)"
```

## 7. API Contracts

```
POST   /api/v1/projects                        # create project
POST   /api/v1/projects/{id}/imports           # upload PlantPredict / DWG / etc.
GET    /api/v1/projects/{id}/topology
PUT    /api/v1/projects/{id}/devices/{did}     # manual edit / template assign
POST   /api/v1/projects/{id}/io-list/generate  # body: options
GET    /api/v1/projects/{id}/io-list           # JSON
GET    /api/v1/projects/{id}/io-list/export?format=xlsx|csv|json|tags
GET    /api/v1/projects/{id}/io-list/diff?from=v3&to=v4
GET    /api/v1/templates                       # browse library
POST   /api/v1/templates                       # add new template
```

## 8. Tech Stack

- **Backend**: Python 3.11 + FastAPI (PlantPredict & generic Excel ingest are Python-native).
- **DWG parsing**: ODA File Converter or Teigha for DWG→DXF; ezdxf for DXF block extraction; PVCase blocks have a published attribute schema.
- **Topology graph**: NetworkX for graph operations; PostGIS if geospatial layout matters.
- **Templates**: YAML in a versioned Git repo (the device library); CI validates each template against vendor source documents.
- **PlantPredict**: Use DNV's PlantPredict REST API (OAuth2 client credentials) to fetch project + result.
- **Frontend**: React + Tailwind + react-flow for topology visualization, AG Grid for IO list.
- **Output**: openpyxl with company-template stylesheets (so output looks "native" to each customer).

## 9. Key Algorithms / Pseudocode

**End-to-end generation**

```python
def generate_io_list(project_id):
    proj = ProjectRepo.get(project_id)
    topology = build_topology(proj.imports)        # → PTM
    topology = resolve_templates(topology)         # attach device template
    topology = resolve_addresses(topology)         # Modbus / SunSpec / etc.
    signals = []
    for dev in topology.devices:
        tmpl = template_lib.get(dev.template_id)
        for sig in tmpl.signals:
            signals.append(IOPoint(
                tag = f"{dev.id}.{sig.name}",
                device = dev.id, signal = sig.name,
                type = sig.type, eu = sig.eu,
                direction = sig.direction,
                addressing = resolve_address(dev, sig),
                class_ = sig.class_,
                alarm_class = sig.criticality,
                source_template = tmpl.id,
                template_version = tmpl.version,
            ))
    signals += derive_aggregates(topology)
    signals = apply_naming_convention(signals, proj.naming)
    gaps = find_gaps(signals, proj.spec_required_signals)
    return IOList(version=next_version(proj),
                  points=signals, gaps=gaps, topology=topology)
```

**Modbus address allocation** when not vendor-fixed (e.g., a third-party gateway aggregating multiple devices):

```python
def allocate_modbus_addresses(devices, base=40000, gap=200):
    addr = base
    for dev in sorted(devices, key=lambda d: d.id):
        dev.modbus_base = addr
        addr += max(gap, len(dev.template.signals)) 
```

**Diff between IO list versions**

```python
def diff(v_old, v_new):
    by_tag_old = {p.tag: p for p in v_old.points}
    by_tag_new = {p.tag: p for p in v_new.points}
    added = [p for t,p in by_tag_new.items() if t not in by_tag_old]
    removed = [p for t,p in by_tag_old.items() if t not in by_tag_new]
    changed = []
    for t in by_tag_old.keys() & by_tag_new.keys():
        if by_tag_old[t] != by_tag_new[t]:
            changed.append((by_tag_old[t], by_tag_new[t]))
    return Diff(added, removed, changed)
```

## 10. Edge Cases

- **PlantPredict authentication & rate limits**: Use OAuth2 client credentials, cache tokens, respect rate limits, support proxy.
- **DWG block variants**: PVCase block attributes evolve across releases — the importer must accept multiple block schemas and tolerate missing/extra attributes.
- **Mixed inverter fleets**: Two inverter makes in one block — ensure addressing per make-specific gateway, not global.
- **Master-of-masters** (Modbus on inverter + sub-Modbus on combiner): Build a hierarchical comms map, not a flat address space.
- **Tracker grouping**: Trackers are often on RS-485 multi-drop with up to 247 slaves; allocate buses and IDs.
- **String-level monitoring** opt-in/opt-out: customer chooses per project; tool must skip string IO when not licensed.
- **Met-station redundancy**: 2+ pyranometers per station; ensure aggregation logic (median, weighted avg) is captured in derived signals.
- **BESS — multiple containers per inverter**: Hierarchies can be deep (Megapack → BMS → rack → module → cell). Stop at level customer requires (typically rack).
- **POI metering**: utility revenue meter and protection relay both at POI; both produce overlapping signals; flag and reconcile.

## 11. Ignition-Specific Integration

- The IO list directly drives Spec 6 (tag DB) — IOList JSON is the input to tag-DB UDT instantiation.
- An **Ignition module** (scope GD) adds:
  - "Import IO List" wizard in Designer
  - Designer view of the topology graph
  - One-click "Provision Driver Connections" — for each device-comms entry, create the corresponding Ignition Device Connection (Modbus TCP, EtherNet/IP, OPC UA, DNP3 via the appropriate module). Provisioning uses Gateway Web API.
- Provide a **starter Perspective project** with a topology-tree navigation view auto-generated from the IO list.
- For renewables, integrate with the **Solar Industries module ecosystem** (some customers already have Inductive Automation Solar templates) — generated tags use the same naming convention so the templates work out of the box.

## 12. Test Plan

- **Library coverage tests**: For each templated device, an automated test parses the vendor's published register CSV and asserts our template matches.
- **End-to-end golden projects**: 5 reference plants (small PV, mid PV+BESS, large utility PV, wind, hybrid) with known-good IO lists; CI regenerates and diffs.
- **Round-trip**: PlantPredict project → IO list → Modbus emulator (Spec 1) instantiated from IO list → Ignition reads it → expected data flows.
- **Performance**: 200 MW project < 60 s.
- **Address allocator**: property-based test (Hypothesis) — no overlaps, all in valid ranges.
- **Regression**: Customer-reported issues become permanent test cases.

## 13. Phased Rollout

| Phase | Duration | Scope |
|---|---|---|
| 0 — MVP | 8 weeks | Generic XLSX importer, top-3 inverter templates, XLSX export |
| 1 — PV design tool | 8 weeks | PlantPredict + PVCase importers, top-10 inverter templates, top-3 tracker, top-3 met |
| 2 — Tag DB + UI | 6 weeks | Direct tag-DB push, topology UI, diff UI, gap reports |
| 3 — BESS & substation | 8 weeks | BESS templates (Megapack, FlexGen, Sungrow), substation relays (SEL, ABB, GE Multilin), IEC 61850 mapping |
| 4 — Wind & hybrid | 10 weeks | Wind turbine templates (IEC 61400-25), hybrid plant aggregation |
| 5 — Library scale | ongoing | Continuous template library expansion, vendor-verified marketplace |

## 14. Success Metrics

- IO-list generation time for a 200 MW PV+BESS plant: from 100+ hours to < 4 hours (including review).
- IO list defects found in FAT/SAT: ≥ 70% reduction.
- % of devices in a project served by library templates (vs hand-built): ≥ 90% within 18 months.
- Time to incorporate a design revision: from weeks to < 1 day.
- Library size: ≥ 200 device templates within 12 months.
-e 

---


# Spec 6 — Tag Creation from IO List (Single-Line-Diagram-Driven)

## 1. Problem Statement

A SCADA tag database is the spine of every other artifact: alarms (Spec 3), historian config (Spec 4), screens (Spec 2), FAT/SAT (Spec 8), comms (Spec 9), anomaly detection (Spec 10), grid code logic (Spec 7). When tags are created ad hoc, naming drifts, hierarchies become inconsistent, and templates can't be reused. The cure is a generator that takes a structured IO list (Spec 5) and the plant single-line / topology, and produces a fully-templated, hierarchical tag database where every device on the SLD is a node — with consistent naming (per IEC 81346 / ISA-95 / company convention), reusable User Defined Types (UDTs), and well-defined parent-child relationships. The same generator targets Ignition, AVEVA, OSI/AVEVA PI AF, Schneider EcoStruxure Geo SCADA, Honeywell Experion, Siemens WinCC OA, etc., from a single canonical model.

## 2. User Personas & Stories

**SCADA Application Engineer** — *"Give me a tag database that mirrors the SLD: every breaker, transformer, inverter, BESS, and combiner is a node, instantiated from a UDT, with all signals from the IO list bound and a place for derived/computed signals."*

**Standards Engineer** — *"As a corporate standards owner, I want every project to follow our naming convention (e.g., `<Plant>/<Block>/<Equipment>/<Signal>`) automatically, with linting that flags deviations."*

**Asset Performance Team** — *"As an APM/data-science user, I want PI AF / asset hierarchy that mirrors the SLD so my queries and dashboards are equipment-centric, not point-centric."*

**Brownfield Engineer** — *"Take my legacy flat tag list and re-organize it into a clean hierarchy following the SLD I just digitized."*

## 3. Functional Requirements

- **F1**: Ingest IO list from Spec 5 (JSON or XLSX) and SLD topology from Spec 2 (DrawingGraph) or Spec 5 (PTM).
- **F2**: Build canonical hierarchy `Plant → Area → Unit → Equipment → Sub-equipment → Signal`, configurable per company convention.
- **F3**: Auto-generate UDTs from the IO list — one UDT per (device template × use-case). UDT includes: parameters, member tags (one per signal), nested UDTs (e.g., a "PowerFlow" UDT inside "Inverter").
- **F4**: Instantiate UDTs per device — generates per-instance member tag bindings (Modbus address, OPC UA node, etc.) using template parameters.
- **F5**: Naming linter — pluggable rule sets (IEC 81346, ISA-95, custom regex). Reports violations with suggested fixes.
- **F6**: Bidirectional sync with the live tag DB (read existing, generate diff, deploy diff with rollback).
- **F7**: Multi-target generators: Ignition (UDT + Tag JSON via system.tag.configure), AVEVA System Platform (Galaxy import), PI Asset Framework (XML), Schneider EcoStruxure Geo SCADA (CSV import), WinCC OA (DPL/CTRL), Honeywell Experion (CB import), generic OPC UA address space (NodeSet2.xml).
- **F8**: Derived/computed tags — expressions that reference other tags (e.g., `PerformanceRatio = AC_Power / (POA * DC_capacity)`). Generator emits in the target SCADA's native expression dialect.
- **F9**: Tag aliasing for cross-system integration: maintain stable external names (e.g., for IT/OT integration to a data lake) even when internal names refactor.
- **F10**: Versioning and migration: when UDTs evolve, migrate existing instances safely; never break tag bindings used by alarms, screens, or history.
- **F11**: Bulk operations: rename equipment everywhere, swap a UDT version, change a hierarchy level — all transactionally.
- **F12**: Provide tag-browse APIs and a tree UI; support full-text search across tags and equipment.

## 4. Non-Functional Requirements

- **N1 Scale**: 1,000,000 tags per tag database; bulk operations < 60 s.
- **N2 Idempotency**: All deploys are idempotent; reruns are no-ops.
- **N3 Refactoring safety**: Renames preserve all downstream bindings (history, alarms, screens) — no broken references.
- **N4 Standards**: Out-of-the-box rule sets for IEC 81346 / ISA-95 / KKS / Equipment Identification System (EIS).
- **N5 Performance**: Tag-tree browse over 1 M tags is virtual-paged, p95 < 200 ms.
- **N6 Auditability**: Every change is recorded with who/when/why; sign-off workflow optional.

## 5. System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│  Web UI: tag tree, UDT editor, naming linter, diff           │
└──────────────────────────────────────────────────────────────┘
                              │ REST + WS
┌─────────────────────────────▼────────────────────────────────┐
│                     Tag Catalog Service                      │
│  (canonical model, versioned)                                │
└──┬───────────────────────────────────────┬──────────────────┘
   │                                       │
┌──▼─────────────┐                  ┌──────▼──────────┐
│ Importers      │                  │ Naming linter   │
│ - IOList JSON  │                  │ + autofixers    │
│ - Spec 2 graph │                  └─────────────────┘
│ - Brownfield   │                          │
└────────────────┘                          │
                              ┌─────────────▼──────────────┐
                              │ Generator framework         │
                              └─┬──────────────┬──────────┬─┘
                                │              │          │
                       ┌────────▼─┐   ┌────────▼─┐   ┌────▼─────┐
                       │ Ignition │   │ AVEVA    │   │ PI AF    │
                       │ (UDT+Tag)│   │ Galaxy   │   │ NodeSet  │
                       └────────┬─┘   └──────────┘   └──────────┘
                                │
                       ┌────────▼────────┐
                       │ Deploy / Diff /  │
                       │ Rollback         │
                       └─────────────────┘
```

## 6. Data Models

### Canonical tag catalog (PostgreSQL)

```sql
CREATE TABLE udt (
  id           UUID PRIMARY KEY,
  name         TEXT NOT NULL,
  version      INT NOT NULL,
  description  TEXT,
  parameters   JSONB NOT NULL DEFAULT '{}'::jsonb,
  members      JSONB NOT NULL,                -- array of member specs
  parent_udt   UUID REFERENCES udt(id),       -- inheritance
  UNIQUE (name, version)
);

CREATE TABLE equipment (
  id           UUID PRIMARY KEY,
  external_id  TEXT NOT NULL UNIQUE,          -- stable, used in IO list
  parent_id    UUID REFERENCES equipment(id),
  hierarchy_level TEXT,                       -- Plant, Area, Unit, Equipment, ...
  type         TEXT NOT NULL,
  udt_id       UUID REFERENCES udt(id),
  parameters   JSONB NOT NULL DEFAULT '{}'::jsonb,
  geo          GEOGRAPHY(POINT,4326),
  attributes   JSONB
);

CREATE TABLE tag (
  id           UUID PRIMARY KEY,
  equipment_id UUID REFERENCES equipment(id),
  member_path  TEXT NOT NULL,                 -- relative path within UDT
  full_path    TEXT NOT NULL UNIQUE,          -- materialized tag path
  data_type    TEXT,
  value_source TEXT,                          -- 'opc','modbus','memory','expression'
  source_config JSONB,
  expression   TEXT,                          -- if value_source='expression'
  metadata     JSONB                          -- EU, description, etc.
);
```

### UDT (YAML, for hand-edit)

```yaml
udt:
  name: Inverter_PV
  version: 3
  parameters:
    DeviceTemplateId: {type: string, required: true}
    Capacity_kW:      {type: float,  required: true}
    Bay:              {type: string}
  members:
    - name: AC_Power
      data_type: float32
      value_source: opc
      source_config: {opc_path: "ns=2;s=Inverter/{ID}/AC_Power"}
      eu: kW
      description: "AC active power"
      historize: true
    - name: AC_PowerFactor
      data_type: float32
      value_source: opc
      source_config: {opc_path: "ns=2;s=Inverter/{ID}/AC_PF"}
      eu: pu
    - name: Status
      data_type: int16
      enum: {0: "Off", 1: "Running", 2: "Fault", 3: "Standby"}
    - name: PerformanceRatio
      data_type: float32
      value_source: expression
      expression: "{AC_Power} / ({Capacity_kW} * {Plant.POA_kWm2})"
    - name: Setpoints
      type: nested_udt
      udt: SetpointBlock
      version: 1
```

### Equipment hierarchy (example fragment)

```
Plant: SunnyAcres
  Area: Block_01
    Unit: PVBlock_01
      Equipment: INV-001 (UDT Inverter_PV v3, Capacity_kW=2500)
        Sub: CB-001-01 (UDT CombinerBox v2, strings=24)
        Sub: CB-001-02
      Equipment: T-PAD-01 (UDT PadTransformer v1)
    Unit: BESSBlock_01
      Equipment: BESS-01 (UDT BESS_Container v2)
  Area: Substation
    Unit: HV_Switchgear
      Equipment: BR-MAIN (UDT HV_Breaker v1)
      Equipment: T-MAIN  (UDT PowerXfmr v1)
    Unit: POI
      Equipment: POI-METER (UDT RevenueMeter v1)
```

## 7. API Contracts

```
GET    /api/v1/equipment?search=...&parent=...
POST   /api/v1/equipment
PATCH  /api/v1/equipment/{id}
GET    /api/v1/equipment/{id}/tags
GET    /api/v1/udts
POST   /api/v1/udts
PUT    /api/v1/udts/{id}
POST   /api/v1/udts/{id}/instantiate         # body: equipment + parameters
POST   /api/v1/imports/iolist                # body: IO list JSON
POST   /api/v1/lint                          # body: tag list + ruleset
POST   /api/v1/deployments                   # body: target + selection
POST   /api/v1/deployments/{id}/dryRun
GET    /api/v1/deployments/{id}/diff
POST   /api/v1/refactor:rename               # body: from→to, scope
GET    /api/v1/tags?path_prefix=...&page=...
```

## 8. Tech Stack

- **Backend**: Python (FastAPI) for catalog and lint; Go for high-throughput Ignition Gateway API client.
- **DB**: PostgreSQL with `ltree` for hierarchy, `pg_trgm` for full-text search.
- **Workflow**: Temporal (long-running migrations / refactors).
- **Frontend**: React + virtualized tree (TanStack Virtual / react-arborist), Monaco editor for expressions.
- **Lint**: small DSL on top of Python regex / pydantic; built-in rule sets shipped as YAML.
- **Diff**: Custom semantic differ (not raw JSON) so reordered members don't show as changes.

## 9. Key Algorithms / Pseudocode

**UDT auto-derivation from IO list**

```python
def derive_udts(iolist):
    grouped = defaultdict(list)
    for p in iolist.points:
        grouped[(p.device_template, p.device_template_version)].append(p)

    udts = []
    for (tmpl, ver), points in grouped.items():
        members = []
        for sig in unique_signals(points):
            members.append({
                "name": sig.name,
                "data_type": sig.type,
                "value_source": map_source(sig),
                "source_config": parameterize(sig.address),  # parameterized by {ID}/{ip}
                "eu": sig.eu,
                "historize": sig.criticality in {"critical","high"},
            })
        udts.append(UDT(name=tmpl, version=ver, members=members))
    return udts
```

**Instantiation**

```python
def instantiate(equipment, udt, params):
    tags = []
    for m in udt.members:
        full = f"{equipment.full_path}/{m['name']}"
        cfg  = render_template(m["source_config"], {**params, "ID": equipment.external_id})
        tags.append(Tag(equipment_id=equipment.id, member_path=m["name"],
                        full_path=full, data_type=m["data_type"],
                        value_source=m["value_source"], source_config=cfg))
    return tags
```

**Naming linter rule example (IEC 81346-style)**

```yaml
rule:
  id: iec_81346_levels
  description: "Equipment paths must follow =Plant+Area-Unit-Equipment-Signal"
  severity: error
  pattern: "^=([A-Z0-9]{3,})\\+([A-Z0-9]{2,})\\-([A-Z]{2,5}-\\d{2,})(\\-[A-Z]{2,4})?$"
  autofix:
    when: regex_close_match
    transform: normalize_separators
```

**Refactor: rename equipment**

```python
def rename_equipment(old, new, scope):
    with txn():
        eq = Equipment.find_by_external_id(old)
        eq.external_id = new
        # update materialized tag full_paths
        Tag.update().where(equipment_id=eq.id).set(full_path=expr_replace_prefix())
        # propagate to dependent artifacts via change-event bus
        publish(EquipmentRenamed(old=old, new=new, equipment_id=eq.id, scope=scope))
        record_audit(actor=ctx.user, change="rename", before=old, after=new)
    # subscribers (alarm gen, history gen, screens) consume and update bindings
```

## 10. Edge Cases

- **UDT inheritance with parameter overrides**: ensure child overrides only valid parameters, with type checks.
- **Circular references in expressions**: detect cycles at lint time (DAG check).
- **Long tag paths**: many SCADAs limit path length (Ignition: 255 chars; PI: 1024). Lint per target.
- **Reserved characters**: per platform — Ignition disallows `/[]{}`; PI disallows `' " ;`. Lint.
- **Member type changes** (e.g., float to int): break all instances; require migration plan.
- **Concurrent refactors**: optimistic concurrency on equipment versions; reject conflicting refactors.
- **Brownfield import**: many existing flat tag DBs have inconsistent naming — provide a clustering tool that groups likely-related tags into proposed equipment.
- **Multi-language descriptions**: Some customers maintain English + Spanish/Portuguese/Chinese descriptions; UDT members support i18n maps.

## 11. Ignition-Specific Integration

- Ignition UDTs are first-class. Generator emits UDT JSON to `system.tag.configure(["[default]_types_/<UDT>"], baseTagPath, configs)`. Instantiation creates UDT instances and binds parameters.
- Use Ignition's parameterized OPC paths in member tag definitions (`ns=2;s=Inverter/{ID}/AC_Power`); the parameter `{ID}` resolves at instance time.
- Provide an **Ignition module** (scope GD) that:
  - Adds a Designer "Tag Catalog" panel: browse the canonical catalog, drag UDTs onto the project, deploy diffs.
  - Adds a Gateway scheduled drift detector that compares Ignition tag config to canonical, surfaces drift, and offers one-click reconciliation.
  - Hooks tag rename events: when a user renames a UDT or instance in Designer, prompt to push the change back to the catalog.
- For tag history, the catalog's `historize` flag drives the historian-deploy generator (Spec 4) — single source of truth.
- Tag aliases support: maintain `[default]Aliases/External/<external_name>` redirect tags for stable external integration paths.

## 12. Test Plan

- **Round-trip**: Catalog → deploy to Ignition → read back via system.tag.browse → diff against catalog → expect zero diff.
- **Refactor safety**: Rename equipment in catalog → expect alarms/history/screens (Specs 3/4/2) to update to new path with no orphans.
- **Performance**: 100k tag deploy < 5 min; 1 M tag tree browse < 200 ms p95.
- **Standards**: For each rule set (IEC 81346, ISA-95, KKS), ship sample compliant and non-compliant catalogs with expected lint outputs.
- **UDT migrations**: Migrate UDT v1 → v2 → v3 with member additions/removals; verify dependent tag bindings stay correct.

## 13. Phased Rollout

| Phase | Duration | Scope |
|---|---|---|
| 0 — MVP | 8 weeks | Canonical catalog, UDT model, Ignition generator (single-target), basic UI |
| 1 — Lifecycle | 6 weeks | Versioning, audit, refactor, drift detection, lint |
| 2 — IO list integration | 4 weeks | Auto-derive UDTs from Spec 5 IO lists |
| 3 — Multi-target | 12 weeks | AVEVA Galaxy, PI AF, Geo SCADA, WinCC OA generators |
| 4 — Brownfield | 8 weeks | Read-back & re-organize for legacy tag DBs |
| 5 — Standards | 6 weeks | Rule set library, autofixers, multi-language i18n |

## 14. Success Metrics

- Time to provision a 100k-tag project: from > 2 weeks manual to < 1 day.
- % of projects using UDT instantiation (vs hand-built tags) within 12 months: ≥ 90%.
- Naming compliance rate against company standard: ≥ 99%.
- Refactor incidents that broke downstream bindings: 0.
- Adoption: ≥ 80% of new SCADA projects start from the catalog.
-e 

---


# Spec 7 — Grid Code Compliance Checking

## 1. Problem Statement

Every ISO/RTO and large utility has different interconnection (LGIA / SGIA) requirements for utility-scale generation: voltage regulation, reactive-power capability, low- and high-voltage ride-through (LVRT/HVRT), frequency response (primary frequency response and fast frequency response), ramp rates, active-power curtailment, anti-islanding (per IEEE 1547 for distribution-level), and per-IBR rules now governed federally by IEEE 2800-2022 / NERC PRC-024-3 / PRC-019 / FERC Order 901. PPC (Power Plant Controller) configuration must mirror the applicable rule set exactly. Today this is verified manually by cross-referencing 50–500 page interconnection agreements against PPC parameter screens — slow, error-prone, and difficult to keep current as rules evolve. A rules engine that takes (a) target POI / ISO-RTO / interconnection agreement, (b) PPC configuration, and (c) optional IBR-specific capabilities, then validates compliance — and can auto-generate compliant setpoints — closes the loop and dramatically reduces compliance risk.

## 2. User Personas & Stories

**PPC Engineer** — *"Tell me whether my Megapack/Sungrow PPC config will pass the CAISO/PJM interconnection compliance test before I drive to site."*

**Interconnection Engineer** — *"Generate a default PPC parameter set for a new 200 MW PV plant interconnecting at 230 kV in PJM, conforming to PJM Manual 14H and IEEE 2800."*

**NERC Compliance Officer** — *"Produce an evidence pack for our PRC-024 / PRC-019 / PRC-006 attestation — every parameter, its source rule, and the configuration value as deployed."*

**Lawyer / Regulatory** — *"When the ISO updates its tariff, surface every plant whose PPC config would no longer comply, with required changes."*

## 3. Functional Requirements

- **F1**: Maintain a versioned **Rules Library** keyed by (jurisdiction, applicable standard, version, effective date). Initial coverage:
  - **NERC**: PRC-024-3 (frequency/voltage ride-through), PRC-019 (reactive coordination), PRC-006 (UFLS), BAL-003 (frequency response), MOD-026/027 (model verification)
  - **IEEE**: 2800-2022 (IBR interconnection), 1547-2018 (DER interconnection)
  - **CAISO**: GIDAP, GIA standard pro-forma + LGIP, RIMS data
  - **ERCOT**: Nodal Operating Guide, Section 6 (Performance Monitoring), DC tie / PCRR rules
  - **PJM**: Manual 14H (Generator Operational Requirements), Manual 14E (Upgrade and Transmission Interconnection Requests)
  - **MISO**: BPM-015 (Generator Interconnection), Tariff Schedules
  - **SPP**: GI Procedures and OATT
  - **NYISO**: SGIP, OATT Attachment X
  - **ISO-NE**: Schedule 22, Source Code 22 minimum interconnection standard
  - **NRCAN/AESO/IESO**: Canadian provincial codes (later phase)
  - **ENTSO-E NC RfG / NC HVDC**: European (later phase)
- **F2**: Map a project to applicable rule sets via POI metadata: ISO/RTO, BES (yes/no), nameplate, voltage class, interconnection date, generator type (PV, BESS, Wind, Hybrid).
- **F3**: Capability profiles: ingest IBR/PPC capability descriptors (max ramp, reactive capability curve, voltage range, response times) — enables both validation and synthesis.
- **F4**: Validation engine: evaluate every applicable rule against the PPC configuration, produce PASS/WARN/FAIL with citations to the source clause.
- **F5**: Auto-synthesis: given POI + capability + applicable rules, generate a default-compliant PPC parameter set.
- **F6**: Vendor-aware emitters: translate the generic compliant setpoint set into vendor-specific PPC parameters (Power Electronics PPC, FlexGen, AGM AGC/PPC, GE WindControl, Tesla, Sungrow PPC, SMA Hybrid Controller).
- **F7**: Continuous monitoring mode: subscribe to live PPC values via OPC UA / Modbus and re-evaluate on parameter changes; alert on drift.
- **F8**: Evidence pack export: PDF + JSON, for regulatory submission, including the rule citations, parameter values, and timestamps.
- **F9**: Rule update workflow: when a rule changes (e.g., FERC Order 901 implementation), automatically re-evaluate every project and surface impacted plants.
- **F10**: Sandbox / what-if: change a parameter and instantly see all rule outcomes change.
- **F11**: Integration with grid model: optional ingest of PSS/E, PSCAD, or DIgSILENT case (small-signal stability, fault duty) to validate dynamic-performance rules.

## 4. Non-Functional Requirements

- **N1 Authority**: Rule library is versioned, signed, and traceable to its source document.
- **N2 Latency**: Validate a single project (≤ 500 parameters, ≤ 200 rules) in < 1 second.
- **N3 Reproducibility**: Same inputs + same rule library version always produce same outputs.
- **N4 Coverage**: Day-1 rule library covers all 7 US ISO/RTOs + IEEE 2800 + IEEE 1547 + relevant NERC PRC standards.
- **N5 Update cadence**: Rule library SLA: critical rule updates published within 30 days of effective date.
- **N6 Auditability**: Every validation run is preserved; cannot be modified after the fact.

## 5. System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│   Web UI: project, rules, capability, validation, evidence      │
└─────────────────────────────────────────────────────────────────┘
                              │ REST + WS
┌─────────────────────────────▼───────────────────────────────────┐
│                       Compliance Service                        │
│  - Project store    - Capability store    - Audit log           │
└──┬─────────────┬─────────────┬─────────────┬──────────────────┬─┘
   │             │             │             │                  │
┌──▼──────┐  ┌───▼─────┐  ┌───▼──────┐  ┌───▼──────┐    ┌──────▼──┐
│ Rule    │  │ Rule    │  │ Validator│  │ Synthesizer│  │ Vendor  │
│ store   │  │ engine  │  │          │  │            │  │ emitters│
│ (Git +  │  │ (Rego/  │  │          │  │            │  │         │
│  signed)│  │ CEL)    │  │          │  │            │  │         │
└─────────┘  └─────────┘  └──────────┘  └────────────┘  └─────────┘
                                                              │
                              ┌───────────────────────────────┘
                              ▼
                       ┌─────────────────┐
                       │ Live monitor    │  (OPC UA/Modbus poll
                       │ (drift detect)  │   of deployed PPCs)
                       └─────────────────┘
                              │
                       ┌──────▼──────────┐
                       │ Evidence pack   │  (PDF + JSON)
                       │ generator       │
                       └─────────────────┘
```

## 6. Data Models

### Rule (YAML)

```yaml
rule:
  id: NERC_PRC_024_3_VRT_HV_LV_2024
  authority: NERC
  document: "PRC-024-3 Generator Frequency and Voltage Protective Relay Settings"
  version: "3"
  effective_date: 2024-07-01
  applies_when:
    bes: true
    generator_type: [PV, BESS, Wind, Hybrid]
    nameplate_min_mw: 20
  inputs:
    - voltage_pu_at_poi
    - duration_s
  parameters:
    - name: V_lo_must_remain_connected
      type: piecewise
      table:
        - {duration_s: 0.150, v_pu_min: 0.45}
        - {duration_s: 0.300, v_pu_min: 0.65}
        - {duration_s: 2.000, v_pu_min: 0.75}
        - {duration_s: 3.000, v_pu_min: 0.90}
    - name: V_hi_must_remain_connected
      type: piecewise
      table:
        - {duration_s: 1.000, v_pu_max: 1.20}
        - {duration_s: 2.000, v_pu_max: 1.175}
        - {duration_s: 3.000, v_pu_max: 1.15}
        - {duration_s: 1e9,   v_pu_max: 1.10}
  validation:
    expression: |
      ride_through_envelope_inside(
        config.lvrt_curve, V_lo_must_remain_connected) and
      ride_through_envelope_inside(
        config.hvrt_curve, V_hi_must_remain_connected)
  evidence:
    must_capture: [config.lvrt_curve, config.hvrt_curve, source_doc_url]
```

```yaml
rule:
  id: PJM_M14H_PFR_2025
  authority: PJM
  document: "PJM Manual 14H Section 5.3"
  version: "Rev 36"
  effective_date: 2025-01-01
  applies_when:
    iso_rto: PJM
    generator_type: [PV, BESS, Wind, Hybrid]
    nameplate_min_mw: 20
  parameters:
    - name: droop_pct
      type: range
      min: 4.0
      max: 5.0
      typical: 5.0
    - name: deadband_hz
      type: range
      min: 0.017
      max: 0.036
      typical: 0.036
    - name: response_time_s
      type: max
      max: 30
  validation:
    expression: |
      config.frequency_response_enabled and
      config.droop_pct in [4.0, 5.0] and
      config.deadband_hz <= 0.036 and
      config.response_time_s <= 30
```

### PPC Configuration (canonical)

```yaml
ppc_config:
  project_id: uuid
  poi:
    iso_rto: PJM
    voltage_kv: 230
    bes: true
    interconnection_date: 2025-09-01
  capabilities:
    nameplate_mw: 200
    reactive_capability:
      type: D-curve
      curve: [...]                 # MW vs MVAr corner points
    ramp_capability_mw_per_min: 50
  setpoints:
    voltage_setpoint_pu: 1.00
    voltage_deadband_pu: 0.005
    voltage_droop_pct: 4.0         # for V control mode
    pf_target: 1.0
    q_setpoint_mvar: 0
    control_mode: V                # V | PF | Q | mixed
    frequency_response_enabled: true
    droop_pct: 5.0
    deadband_hz: 0.036
    response_time_s: 30
    ramp_up_mw_per_min: 50
    ramp_down_mw_per_min: 50
    curtailment_setpoint_mw: 200
  ride_through:
    lvrt_curve: [...]
    hvrt_curve: [...]
    underfrequency_curve: [...]
    overfrequency_curve: [...]
```

### Validation result

```json
{
  "project_id": "...",
  "rule_set_version": "2025.10",
  "evaluated_at": "2025-12-15T18:22:01Z",
  "results": [
    {"rule_id": "NERC_PRC_024_3_VRT_HV_LV_2024", "status": "PASS"},
    {"rule_id": "PJM_M14H_PFR_2025", "status": "WARN",
     "details": "droop_pct=5.0 within range; deadband_hz=0.036 at maximum"},
    {"rule_id": "IEEE_2800_2022_5_4_Q_PRIORITY", "status": "FAIL",
     "details": "config.q_priority=disabled; rule requires Q-priority during voltage events",
     "remediation": "set q_priority=enabled and q_priority_threshold_pu=0.90"}
  ],
  "summary": {"pass": 47, "warn": 8, "fail": 2}
}
```

## 7. API Contracts

```
GET    /api/v1/rules?jurisdiction=PJM&effective_on=2025-12-01
POST   /api/v1/rules                              # add/update rule (signed)
GET    /api/v1/projects/{id}/config
PUT    /api/v1/projects/{id}/config
POST   /api/v1/projects/{id}/validate             # one-shot validation
POST   /api/v1/projects/{id}/synthesize           # generate compliant config
POST   /api/v1/projects/{id}/evidence             # produce evidence pack
POST   /api/v1/monitor                            # body: project + endpoint
GET    /api/v1/monitor/{id}/events                # SSE/WS drift events
POST   /api/v1/emitters/{vendor}                  # body: canonical → vendor params
```

## 8. Tech Stack

- **Backend**: Go for the rule engine and API; Python for the synthesizer (numerical work).
- **Rule engine**: Open Policy Agent (Rego) for declarative rules, with a small CEL-based extension for numeric expressions; rules ship as a signed bundle (cosign).
- **Storage**: PostgreSQL for projects/configs; Git for rule library (with semantic versioning).
- **Live monitor**: OPC UA client (open62541) and Modbus TCP (libmodbus) for poll-based drift detection.
- **Evidence**: WeasyPrint or LaTeX for PDFs; JSON-LD for machine-readable evidence.
- **Frontend**: React + Tailwind; Recharts for capability curves; Monaco for parameter editing.

## 9. Key Algorithms / Pseudocode

**Rule application**

```python
def validate(project_config: PPCConfig, rule_set_version: str):
    rules = RuleStore.load(rule_set_version)
    applicable = [r for r in rules if applies(r, project_config)]
    results = []
    for r in applicable:
        outcome = engine.eval(r, project_config)
        results.append(outcome)
    return ValidationReport(rule_set_version, results, summarize(results))
```

**Synthesizer**

```python
def synthesize(poi: POIMeta, caps: Capabilities, target_rules):
    cfg = default_config(caps)
    for r in target_rules:
        for p in r.parameters:
            if hasattr(p, "typical"):
                set_path(cfg, r.parameter_path(p), p.typical)
            elif hasattr(p, "max"):
                set_path(cfg, r.parameter_path(p), p.max)
            elif hasattr(p, "table"):
                set_path(cfg, r.parameter_path(p), p.table)
    cfg = enforce_capability_envelope(cfg, caps)  # never exceed device capability
    val = validate(cfg, current_rule_set())
    if any(r.status == "FAIL" for r in val.results):
        raise InfeasibleSynthesis(val)
    return cfg, val
```

**Live drift detection**

```python
def monitor(project, opc_endpoint, poll_interval=10):
    last = None
    while True:
        live = read_ppc_config(opc_endpoint)
        if live != last:
            outcome = validate(live, current_rule_set())
            if outcome.has_regression(last_outcome):
                emit_drift_alert(project, outcome)
        last, last_outcome = live, outcome
        sleep(poll_interval)
```

## 10. Edge Cases

- **Conflicting rules**: PJM and NERC rules sometimes overlap; engine flags both; documentation establishes precedence (typically the more restrictive).
- **Grandfathered plants**: Some rules apply only to new interconnections; `applies_when.interconnection_date` predicate handles this.
- **Mode-dependent setpoints**: V vs Q vs PF control mode — only validate parameters relevant to active mode.
- **IBR capability limits**: Synthesizer must clamp to device capability (e.g., can't ask for ±0.95 PF if inverter only supports ±0.90); fail synthesis with clear remediation if rule is infeasible.
- **Hybrid plants** (PV + BESS): Coordinate combined response; capability is sum minus losses; reactive capability may differ between PV and BESS.
- **Mixed inverter fleets**: Take min of per-inverter capabilities for plant-wide synthesis.
- **Metric rounding**: Some PPCs only accept integer percent; rule's `min/max` must accommodate platform precision.
- **Future rules**: Allow rules with `effective_date` in the future; evaluation can run "as-of" any date.

## 11. Ignition-Specific Integration

- The compliance tool runs as an external service. Ignition is one consumer among many.
- Provide an **Ignition module** (scope GD) that:
  - Reads PPC tags from the canonical hierarchy (Spec 6) — no manual config mapping.
  - Adds a Designer panel "Grid Code Compliance" showing live PASS/WARN/FAIL for the active project.
  - Adds a Perspective component "Compliance Status" for operators (high-level traffic light + drill-down).
  - Schedules drift evaluation (Gateway scheduled task) and writes results back as tags so they can be alarmed via Spec 3.
- Use Spec 1 (protocol emulators) to exercise PPC behavior in CI: synthesize a config, deploy to emulated PPC, run a simulated grid event, confirm response satisfies rule.
- Generate an Ignition Perspective dashboard auto-populated with: capability curve overlay, ride-through envelope vs configured curves, frequency response setpoints.

## 12. Test Plan

- **Rule library**: For every rule, golden test cases (known PASS / known FAIL configurations).
- **Synthesizer**: For each (ISO, generator type, voltage class) combination, generate a config and re-validate; expect PASS for default capabilities.
- **Document traceability**: Each rule's `document` field links to the source doc; CI verifies link is reachable and the document version matches.
- **Live monitor**: Inject parameter changes via emulated PPC and verify drift alerts within 1 monitor cycle.
- **What-if**: Property-based tests on synthesizer (Hypothesis) — vary inputs, check invariants (no rule violated, no capability exceeded).
- **Regression**: Each customer-reported compliance defect becomes a permanent test case.

## 13. Phased Rollout

| Phase | Duration | Scope |
|---|---|---|
| 0 — MVP | 8 weeks | Rule engine + Rule library v1 (NERC PRC-024-3, PJM M14H, CAISO GIA, IEEE 2800), validator UI |
| 1 — Synthesis | 6 weeks | Auto-generate compliant config from POI + capability |
| 2 — Coverage | 12 weeks | All 7 US ISO/RTOs, IEEE 1547-2018, NERC PRC-019/006/BAL-003 |
| 3 — Live monitoring | 6 weeks | OPC UA / Modbus pollers, drift detection, Ignition module |
| 4 — Vendor emitters | 8 weeks | Power Electronics, FlexGen, GE, Tesla, Sungrow, SMA |
| 5 — International | 12 weeks | NC RfG (EU), AESO/IESO (CA), AEMO (AU), CEA (IN) |
| 6 — Dynamic models | 12 weeks | Optional PSS/E / PSCAD / DIgSILENT integration for dynamic compliance |

## 14. Success Metrics

- Time to evaluate compliance for a new plant: from days to seconds.
- Time to produce evidence pack for NERC attestation: from weeks to hours.
- Plants with continuous compliance monitoring: ≥ 50 within 18 months.
- Compliance-related interconnection denials prevented (tracked via customer report): ≥ 10/yr.
- Rule library: ≥ 1,500 rules within 12 months; SLA-met update cadence ≥ 95%.
- False-positive rate on drift detection: < 1%.
-e 

---


# Spec 8 — FAT & SAT Checklist Generation

## 1. Problem Statement

Factory Acceptance Tests (FAT) and Site Acceptance Tests (SAT) per IEC 62381 are mandatory deliverables for industrial automation projects but are produced manually as Word/Excel documents — pages of "open valve V-101, observe TI-101 reads 25 °C ± 2, sign here" — derived from IO lists, P&IDs, functional design specs (FDS), and control narratives. This is duplicative work, prone to falling out of sync with design changes, and difficult to execute (you end up with paper checklists, hand-collected screenshots, and after-the-fact PDF reports). A tool that auto-generates FAT and SAT checklists from the project artifacts (Spec 5 IO list, Spec 6 tag DB, control narratives, Spec 3 alarm DB), executes them interactively, captures evidence automatically (screenshots, historian extracts, signed statements), and outputs a formal IEC 62381 / GAMP 5 compliant report — closes the testing gap end-to-end.

## 2. User Personas & Stories

**Test Engineer** — *"As a test engineer, I want every IO point and every alarm to have an auto-generated test step, so I don't miss anything during FAT."*

**Commissioning Engineer** — *"As a commissioning engineer, I want to execute SAT on a tablet on the plant floor, capturing screenshots and operator signatures as I go, with the report printing itself."*

**Customer's Owner Engineer** — *"As an owner's representative, I want to witness FAT against a verifiable, complete checklist, with deterministic pass/fail criteria and digital signatures."*

**QA / Validation (life sciences)** — *"As a QA lead, I want execution evidence and electronic signatures meeting 21 CFR Part 11 and GAMP 5 expectations."*

## 3. Functional Requirements

- **F1**: Inputs: IO list (Spec 5), tag DB (Spec 6), alarm DB (Spec 3), control narratives (free text or structured), FDS, P&ID, plus a **test profile** indicating coverage rules.
- **F2**: Auto-generate test cases by category:
  - **IO loop tests**: per signal, simulate a value at the source (using Spec 1 emulator or Spec 12 PLC sim), verify the SCADA tag reads expected.
  - **Alarm tests**: per alarm in Spec 3, drive the underlying tag past the setpoint, verify alarm triggers with correct priority/message, then clears.
  - **Interlock tests**: per interlock in FDS, exercise the conditions, verify outputs.
  - **Sequence tests**: per batch/SFC sequence (where applicable), step through and verify each phase.
  - **HMI navigation tests**: every screen reachable from home, no broken bindings.
  - **Historian tests**: per historized tag, verify a sample is logged and retrievable.
  - **Comms tests**: per device, verify online status and round-trip data exchange.
  - **Failover/redundancy tests**: per redundant pair, simulate failure, verify failover.
  - **Performance tests**: tag scan rate, screen open time, alarm flood handling.
- **F3**: Test execution UI: web + mobile; user steps through, marks pass/fail, captures evidence; integration with screen-recording, screenshot, historian.
- **F4**: Auto-evidence: where possible, the test runs itself (drives emulator, samples historian, queries tag value) and captures evidence without operator action.
- **F5**: Electronic signatures: pluggable identity (OIDC, smart card, FIDO2); meaning-of-signature recorded; tamper-evident.
- **F6**: Punch list: Failed tests roll into a punch list, assignable to engineers, tracked to closure with retest evidence.
- **F7**: Reports: IEC 62381-format FAT report, IEC 62382 SAT report, GAMP 5 IQ/OQ/PQ-style reports, customer-template Word/PDF outputs.
- **F8**: Versioning & traceability: re-run a prior FAT pack against new code; show what changed; preserve every historical run forever.
- **F9**: Coverage reports: % of IO points, alarms, interlocks, sequences, HMI screens covered.
- **F10**: Multi-target: Ignition first, then AVEVA, Honeywell Experion, Emerson DeltaV, Rockwell FactoryTalk; the test runner uses each platform's tag-read/write API.
- **F11**: Risk-based prioritization: tests can be tagged with risk (safety/environmental/financial), runner can present in priority order, reports highlight high-risk failures.
- **F12**: Offline mode: SAT tablet can execute tests offline at remote sites, sync evidence on reconnection.

## 4. Non-Functional Requirements

- **N1 Coverage**: From inputs alone, generate ≥ 95% of typical IO/alarm/HMI tests with no manual authoring.
- **N2 Throughput**: Execute 10,000 auto-tests overnight with emulator-driven IO; manual phase covers only what cannot be automated.
- **N3 Compliance**: Output reports satisfy IEC 62381/62382, GAMP 5, 21 CFR Part 11.
- **N4 Tamper-evidence**: Append-only event log; cryptographically signed reports.
- **N5 Reliability**: Mobile app works offline ≥ 12 hours; sync resumes seamlessly.
- **N6 Auditability**: Every test, evidence file, and signature is attributable to a specific user, time, and project version.

## 5. System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│  Web App (test author, executor) + Mobile App (SAT)          │
└──────────────────────────────────────────────────────────────┘
                              │ REST + WS
┌─────────────────────────────▼────────────────────────────────┐
│                      Test Plan Service                       │
│   (test cases, runs, evidence, signatures, coverage)         │
└──┬───────────┬───────────────┬──────────────────┬──────────┬─┘
   │           │               │                  │          │
┌──▼─────┐ ┌──▼──────┐ ┌──────▼──────┐ ┌─────────▼────┐ ┌───▼───┐
│Generators│ │Executor │ │Evidence    │ │ Signatures  │ │Reports│
│from IO/ │ │(per     │ │capture     │ │ (e-sig)     │ │       │
│alarm/   │ │target)  │ │(historian, │ │             │ │       │
│FDS/P&ID │ │         │ │screens, ...)│ │             │ │       │
└─────────┘ └─────────┘ └─────────────┘ └─────────────┘ └───────┘
                              │
                  ┌───────────▼──────────┐
                  │ Drives:               │
                  │ - Spec 1 emulators    │
                  │ - Spec 12 PLC sim     │
                  │ - Live SCADA APIs     │
                  └──────────────────────┘
```

## 6. Data Models

### Test case (YAML)

```yaml
test_case:
  id: TC-IO-INV001-AC_POWER
  category: io_loop
  generated_from: iolist:INV-001:AC_Power
  description: "Verify INV-001 AC Power signal end-to-end"
  preconditions:
    - "Emulator INV-001 running"
    - "SCADA INV-001 device shows 'connected'"
  steps:
    - id: 1
      action: emulator_set
      target: emulator://INV-001/ac_power_kw
      value: 1500
    - id: 2
      action: wait
      ms: 2000
    - id: 3
      action: read_tag
      tag: "Plant/Block01/INV-001/AC_Power"
      assert:
        operator: within
        target: 1500
        tolerance: 5    # ±5 kW
        unit: kW
    - id: 4
      action: capture_screenshot
      view: "Plant/Block01/INV-001"
    - id: 5
      action: query_history
      tag: "Plant/Block01/INV-001/AC_Power"
      window: [-30s, +5s]
      assert:
        last_value:
          within: [1495, 1505]
  pass_criteria: "All asserts pass and screenshot captured"
  risk: high
  required_signatures: [test_engineer, witness]
```

### Test run (Postgres)

```sql
CREATE TABLE test_run (
  id           UUID PRIMARY KEY,
  test_case_id TEXT NOT NULL,
  project_ver  TEXT NOT NULL,
  started_at   TIMESTAMPTZ,
  ended_at     TIMESTAMPTZ,
  status       run_status,            -- 'pending','running','passed','failed','skipped'
  executor     TEXT,                  -- user or 'auto'
  step_results JSONB,
  evidence_ids UUID[]
);

CREATE TABLE evidence (
  id           UUID PRIMARY KEY,
  type         TEXT,                  -- 'screenshot','historian','log','file'
  uri          TEXT,                  -- S3 location
  hash_sha256  BYTEA,
  captured_at  TIMESTAMPTZ
);

CREATE TABLE signature (
  id           UUID PRIMARY KEY,
  signed_by    TEXT,
  signed_at    TIMESTAMPTZ,
  scope        TEXT,                  -- 'test_run' | 'punch_item' | 'final_report'
  scope_id     UUID,
  meaning      TEXT,                  -- 'I have witnessed and approve'
  signature    BYTEA,                 -- detached signature
  cert_chain   BYTEA[]
);
```

## 7. API Contracts

```
POST   /api/v1/projects/{id}/test-plans:generate     # body: profile
GET    /api/v1/projects/{id}/test-plans/{plan_id}
POST   /api/v1/test-plans/{plan_id}/runs             # start a run
GET    /api/v1/runs/{run_id}
PATCH  /api/v1/runs/{run_id}/steps/{n}               # mark pass/fail, attach evidence
POST   /api/v1/runs/{run_id}/sign
GET    /api/v1/runs/{run_id}/coverage
POST   /api/v1/punch-items                           # body: failed step → punch
PATCH  /api/v1/punch-items/{id}                      # close-out
POST   /api/v1/reports                               # body: scope + format
```

## 8. Tech Stack

- **Backend**: Python (FastAPI) for orchestration; Go for the high-throughput executor and integration shims.
- **Mobile**: React Native + offline-first storage (WatermelonDB) → sync via REST.
- **Web**: React + TanStack Router + offline support.
- **Workflow**: Temporal (long, resumable runs).
- **Evidence storage**: S3/MinIO with object lock for tamper-evidence; SHA-256 + timestamp via TSA (RFC 3161).
- **Signatures**: PKCS#7/CMS with X.509 certs; FIDO2/WebAuthn for browser-based signing; smart-card support via WebUSB / native.
- **Reports**: WeasyPrint for HTML→PDF; docx-templater for Word; per-customer templates.
- **Auth**: OIDC + OAuth2; full audit log to append-only WORM storage.

## 9. Key Algorithms / Pseudocode

**Auto-generation from inputs**

```python
def generate_plan(project, profile):
    cases = []
    # IO loop tests
    for p in project.iolist.points:
        cases.append(make_io_loop_case(p, profile))
    # Alarm tests
    for a in project.alarms:
        cases.append(make_alarm_case(a, profile))
    # Interlock tests (parsed from FDS)
    for il in project.interlocks:
        cases.append(make_interlock_case(il, profile))
    # HMI navigation
    for v in project.views:
        cases.append(make_hmi_navigation_case(v, profile))
    # Historian tests
    for t in project.tags.where(historize=True):
        cases.append(make_history_case(t, profile))
    # Comms tests
    for d in project.devices:
        cases.append(make_comms_case(d, profile))
    plan = TestPlan(project=project.id, version=project.ver, cases=cases)
    plan.coverage = compute_coverage(plan, project)
    return plan
```

**Auto-executor**

```python
async def execute(case, ctx):
    run = ctx.start_run(case)
    try:
        for step in case.steps:
            r = await dispatch_step(step, ctx)        # set tag, drive emu, etc.
            run.record_step(step.id, r)
            if step.assert_:
                ok = evaluate_assert(step.assert_, r)
                if not ok and step.required:
                    run.fail(step.id, r); break
            if step.action == "capture_screenshot":
                await ctx.capture_screenshot(step.view, run)
        run.finalize()
    except Exception as e:
        run.error(e)
    return run
```

**HMI screenshot (Ignition Perspective)** — drive a headless browser:

```python
async def capture_perspective_screenshot(view_path, run):
    async with playwright.async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width":1920,"height":1080})
        await page.goto(f"{IGNITION_URL}/data/perspective/client/{PROJECT}/{view_path}",
                        wait_until="networkidle")
        png = await page.screenshot(full_page=True)
        await browser.close()
    return store_evidence(png, "image/png", run)
```

## 10. Edge Cases

- **Tag not yet wired** during early FAT: use Spec 1 emulator to provide values; mark test as "FAT-only, repeat at SAT."
- **Alarm with state-based suppression**: test must establish enabling state before driving setpoint; tool must understand suppression conditions.
- **Time-delayed alarms** (long on-delay): test runner must wait or skip with explicit operator override.
- **Destructive tests** (e.g., breaker trip): require multi-party approval before execution.
- **Signature revocation**: if a signer's cert is revoked, mark all signed runs for review (don't auto-invalidate).
- **Mobile device clock drift**: All timestamps reconciled with server time; mark questionable evidence.
- **Network outage during SAT**: queue evidence locally; sync on reconnect; handle conflicts via last-writer-wins with manual review.
- **Customer-specific report templates**: never lose customer-required sections; provide template validator.

## 11. Ignition-Specific Integration

- Test executor talks to Ignition Gateway via Web API (`system.tag.readBlocking`, `system.tag.writeBlocking`, `system.alarm.queryStatus`, `system.tag.queryTagHistory`).
- Provide an **Ignition module** (scope GD) that:
  - Adds a Designer panel "Test Plans" — generate, browse, attach to project.
  - Adds a Perspective component "Test Runner" — operator-friendly UI for in-Ignition execution.
  - Hooks Sequential Function Chart module: each SFC step maps to a test step with auto-evidence capture.
  - Provides Gateway scripts for headless Perspective screenshotting via embedded headless browser.
- Drives Spec 1 emulator and Spec 12 PLC sim from the same plan to enable end-to-end virtual FAT before any hardware ships.
- Spec 9 comms checks become test steps automatically.
- Spec 3 alarm DB and Spec 6 tag DB are direct inputs — no manual intermediate file.

## 12. Test Plan (for the test tool itself)

- **Generation**: Golden projects (Specs 3/5/6 fixtures) → expected test plan → diff.
- **Executor**: Run plans against Spec 1 emulator + a known-good Ignition gateway; expect all pass.
- **Mobile offline**: Disconnect network mid-run, complete on device, reconnect, verify clean sync.
- **Compliance**: For each report format, validate against IEC 62381/62382/Part 11 checklists.
- **Performance**: 10k auto-tests overnight on a single beefy worker.
- **Security**: Tamper-evidence — modify a stored evidence blob, verify report signature fails verification.

## 13. Phased Rollout

| Phase | Duration | Scope |
|---|---|---|
| 0 — MVP | 8 weeks | IO loop & alarm test generation, basic web executor, Ignition target, PDF report |
| 1 — Auto-execution | 6 weeks | Spec 1 / Spec 12 integration; auto-evidence (history, screenshots) |
| 2 — Mobile / SAT | 8 weeks | Mobile app, offline mode, signatures, punch list |
| 3 — Compliance | 6 weeks | IEC 62381/62382 templates, GAMP 5, 21 CFR Part 11 features |
| 4 — Multi-platform | 12 weeks | AVEVA, Experion, DeltaV, FactoryTalk targets |
| 5 — Advanced tests | 8 weeks | Interlock, sequence, redundancy, performance test generators |

## 14. Success Metrics

- Time to author FAT plan: from 200 hours to < 8 hours.
- Time to execute FAT for a 5,000-IO project: from 3 weeks to 5 days (with emulator-driven auto-tests overnight).
- Coverage of generated tests against deliverables: ≥ 95%.
- Punch items closed per week: tracked; expect ≥ 3× improvement vs paper.
- Customer audit findings on FAT/SAT documentation: ≥ 80% reduction.
- Adoption: ≥ 60% of new projects within 12 months.
-e 

---


# Spec 9 — Comms Troubleshooting

## 1. Problem Statement

When a SCADA tag goes "stale" or a device disappears, the engineer faces a layered problem: is it the network (cable/switch/firewall), the modem, the gateway, the protocol (wrong unit ID, register out of range, exception code), the device itself, the time source, the SCADA driver, or a combination? Today this is debugged by hand: ping → traceroute → telnet → packet capture → vendor tool → Ignition diagnostics — across multiple panes of glass. A unified, OSI-layered diagnostics tool that automatically walks the stack from L1 to L7, runs protocol handshakes against the device, captures and decodes packets, samples tag values, correlates with historian gaps, and produces a root-cause analysis with remediation suggestions — would compress hours of debug to minutes and let less-senior engineers triage effectively.

## 2. User Personas & Stories

**Field Service Engineer** — *"I'm at a remote substation; the SCADA shows the recloser offline; let the tool walk the OSI stack and tell me whether it's the cell modem, the serial converter, the wrong unit ID, or a dead radio."*

**SCADA Application Engineer (in NOC)** — *"From my desk, let me run a comprehensive diagnostic on a misbehaving device, get a report I can hand to the field tech."*

**Network / OT Security** — *"Show me which devices are reachable from which gateways, with current latency, packet loss, and TLS health."*

**On-call Operations** — *"Acknowledge the alarm, run the diagnostic from a button on the alarm faceplate, get a remediation suggestion."*

## 3. Functional Requirements

- **F1**: Per-device diagnostic that walks the OSI stack:
  - **L1/L2**: Layer 1 link state (where measurable via SNMP from switch); ARP probe.
  - **L3**: Ping (ICMP), traceroute, MTU discovery; jitter and packet loss over a window.
  - **L4**: TCP/UDP port reachability, TLS handshake, cert validity & chain.
  - **L5/L6**: Protocol-aware handshake — Modbus identification (FC 43), DNP3 link layer + application layer test, OPC UA `GetEndpoints` and channel open, IEC 61850 MMS associate, EtherNet/IP List Identity, S7 ISO-on-TCP setup, SNMPv2/v3 walk, BACnet `Who-Is`/`I-Am`.
  - **L7**: Read a representative tag/object/register; verify timestamp, value range, and quality.
- **F2**: Multi-step diagnostics with branching: if ping fails → check switch port; if TCP open but Modbus fails → check unit ID; if value reads but is stale → check device clock vs server.
- **F3**: Live tag sampling: poll N seconds at high rate, plot value, latency, quality.
- **F4**: Packet capture: optional tcpdump on the SCADA host (interface configurable), filtered to device IP/port; auto-decode with built-in dissectors; downloadable PCAP for Wireshark.
- **F5**: Correlate with historian: when a device went stale historically, surface what else was happening (other devices, network events, gateway restarts).
- **F6**: Root-cause analysis: rule-based + ML-assisted classifier suggests the most likely root cause with confidence; ranked remediation list.
- **F7**: One-click run from Ignition alarm faceplate, Perspective view, mobile app, or CLI.
- **F8**: Bulk diagnostics: run against a fleet (e.g., all devices in Block 03) and rank by severity.
- **F9**: Remote-agent mode: small footprint agent runs at remote sites where the SCADA gateway is, performing local probes; results sent to central UI.
- **F10**: Read-only by default; never write to a device; explicit privileged mode for "send a benign read to confirm liveness."
- **F11**: Reports: shareable PDF/markdown with full timeline and recommendations.
- **F12**: Knowledge base of past diagnostics: each remediated case becomes a pattern future diagnostics learn from.

## 4. Non-Functional Requirements

- **N1 Latency**: Single-device full diagnostic: < 30 seconds typical.
- **N2 Footprint**: Remote agent < 50 MB RAM, < 5% CPU; runs in container or as a Windows service.
- **N3 Security**: Read-only by default; mTLS between agent and central; per-device credentials encrypted at rest with KMS.
- **N4 Resilience**: If central is unreachable, agent caches results and reports later.
- **N5 Auditability**: Every diagnostic recorded; who ran what when.
- **N6 Multi-tenant**: One central instance can manage many sites and customers.

## 5. System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│  Web UI (NOC) + Mobile App (field) + CLI                     │
└──────────────────────────────────────────────────────────────┘
                              │ REST + WS
┌─────────────────────────────▼────────────────────────────────┐
│                       Diagnostic Service                     │
│   - Job dispatcher    - Knowledge base    - RCA engine       │
└──┬──────────────────────────────────────────────────────────┬─┘
   │                                                          │
   │ mTLS over WireGuard                                      │
   │                                                          │
┌──▼──────────────────┐    ... per remote site         ┌──────▼──────────┐
│ Remote Agent (site) │                                │ Remote Agent    │
│  - L1-L7 probes     │                                │                 │
│  - tcpdump          │                                │                 │
│  - protocol clients │                                │                 │
└─────────────────────┘                                └─────────────────┘
```

The remote agent is the unit of work; it has direct visibility to plant network and devices. The central service orchestrates jobs and persists results.

## 6. Data Models

### Diagnostic job

```yaml
job:
  id: uuid
  scope:
    device_id: INV-001
    project_id: SunnyAcres
  steps:
    - id: l3_ping
      probe: icmp
      target: 10.10.10.11
      iterations: 10
      interval_ms: 200
    - id: l4_tcp
      probe: tcp_connect
      target: 10.10.10.11
      port: 502
      timeout_ms: 1000
    - id: l7_modbus_id
      probe: modbus_device_id
      target: 10.10.10.11:502
      unit_id: 3
    - id: l7_modbus_read
      probe: modbus_read
      target: 10.10.10.11:502
      unit_id: 3
      function: 4
      address: 40083
      count: 2
      expected: { type: float32, range: [0, 2500] }
    - id: l7_history_check
      probe: historian_recent
      tag: "Plant/Block01/INV-001/AC_Power"
      window: -1h
  branching:
    - on_fail: l3_ping
      goto: l2_switch_port
    - on_fail: l7_modbus_read
      goto: rca_unit_id_check
```

### Diagnostic result

```json
{
  "job_id": "...",
  "device_id": "INV-001",
  "started_at": "...",
  "ended_at": "...",
  "overall": "fail",
  "steps": [
    {"id": "l3_ping", "status": "pass",
     "metrics": {"loss_pct": 0, "rtt_ms_avg": 1.4, "rtt_ms_p99": 2.1}},
    {"id": "l4_tcp", "status": "pass",
     "metrics": {"connect_ms": 8}},
    {"id": "l7_modbus_id", "status": "fail",
     "error": "exception code 02 (illegal data address)"},
    {"id": "l7_modbus_read", "status": "skipped"}
  ],
  "rca": {
    "primary_cause": "wrong_modbus_unit_id_or_register_map",
    "confidence": 0.78,
    "supporting_evidence": ["l7_modbus_id returned exception 02 with unit_id=3"],
    "remediation": [
      "Try unit IDs 1, 2, 4 — vendors sometimes ship with default 1.",
      "Verify register map for firmware 1.16.4 against IO list (Spec 5).",
      "If recently upgraded device, refresh device template in tag DB."
    ]
  },
  "evidence": [
    {"type":"pcap","uri":"s3://.../job-uuid.pcap","sha256":"..."}
  ]
}
```

## 7. API Contracts

```
POST   /api/v1/diagnostics                      # body: scope + optional custom plan
GET    /api/v1/diagnostics/{id}
WS     /api/v1/diagnostics/{id}/events
POST   /api/v1/diagnostics:bulk                 # body: scope filter
GET    /api/v1/agents                           # registered remote agents
GET    /api/v1/devices/{id}/comms-health        # rolling KPI
POST   /api/v1/captures                         # ad-hoc PCAP request
POST   /api/v1/rca/feedback                     # learn from operator confirmation
```

## 8. Tech Stack

- **Agent**: Go (single static binary, easy cross-compile, low footprint).
- **Probes**: native Go for ICMP, TCP, TLS; libpcap (cgo) for capture; gopacket for decode; per-protocol libs (gomodbus, go-snmp, gopcua).
- **Central**: Python FastAPI for API, Postgres for jobs/results, ClickHouse for metric retention.
- **RCA engine**: rule-based first (Drools-style), upgrade to ML classifier (gradient-boosted decision tree) using historical labelled cases.
- **Frontend**: React + TanStack Query; embedded mini terminal for live results.
- **Transport**: gRPC over WireGuard between central and agents; agent registration via mTLS.
- **Knowledge base**: vector-DB (Qdrant) of (symptom, root cause, remediation) for RAG suggestions.

## 9. Key Algorithms / Pseudocode

**OSI walker (per device)**

```python
def walk_osi(device, agent):
    results = []
    # L3 ping
    p = agent.icmp(device.ip, count=10)
    results.append(("l3_ping", p))
    if p.loss_pct == 100: return finalize(results, "device_unreachable")
    # L4 TCP
    t = agent.tcp_connect(device.ip, device.port, timeout=1000)
    results.append(("l4_tcp", t))
    if not t.ok: return finalize(results, "port_closed_or_filtered")
    # L7 protocol handshake
    h = agent.protocol_handshake(device)
    results.append(("l7_handshake", h))
    if not h.ok: return finalize(results, classify_handshake_error(h))
    # L7 representative read
    r = agent.protocol_read(device, sample_register(device))
    results.append(("l7_read", r))
    # Historian sanity
    hh = central.history_recent(device.tag, hours=1)
    results.append(("historian", hh))
    # Clock drift
    if device.supports_time:
        cd = agent.read_device_time(device)
        results.append(("clock", cd))
    return finalize(results, classify(results))
```

**Modbus exception decoding**

```python
def classify_modbus_error(resp):
    if resp.exception_code == 0x01: return "illegal_function_likely_wrong_fc"
    if resp.exception_code == 0x02: return "illegal_data_address_likely_wrong_register_or_unit"
    if resp.exception_code == 0x03: return "illegal_data_value_likely_unsupported_value"
    if resp.exception_code == 0x04: return "slave_device_failure"
    if resp.exception_code == 0x05: return "acknowledge_long_processing"
    if resp.exception_code == 0x06: return "slave_busy"
    if resp.exception_code == 0x0B: return "gateway_target_no_response"
    return "unknown_modbus_exception"
```

**RCA engine (rule + similarity)**

```python
def rca(results, kb):
    rules_hits = run_rules(RULES_DB, results)             # deterministic rules first
    if rules_hits: return rules_hits[0]                    # high-precision
    # similarity search over knowledge base
    embedding = embed_diagnostic_results(results)
    similar = kb.search(embedding, k=5)
    return aggregate(similar)
```

## 10. Edge Cases

- **Cell-modem APN switching** — repeated TCP-RST patterns indicate carrier-side NAT timeout; tool flags and recommends connection keep-alive tuning.
- **Asymmetric paths** — ping passes but TCP fails — usually firewall; flag and direct user to specific firewall rule.
- **Slow serial RTU** — `Modbus exception 0x05 (acknowledge)` is not failure; tool must wait per spec.
- **Devices that drop ICMP but accept TCP** — never short-circuit on ping fail; always try TCP/protocol next.
- **Devices behind a Modbus gateway** — gateway exception code 0x0B; classify clearly.
- **Conflicting unit IDs** on the same RS-485 bus — tool can suggest scanning IDs 1–247 (read-only, slow) with explicit user consent.
- **Encrypted protocols** (OPC UA with security): ensure cert chain validation; clearly distinguish "device unreachable" from "cert untrusted."
- **Tcpdump privilege** — agent needs `CAP_NET_RAW`; document; provide capability-only privileged container pattern.

## 11. Ignition-Specific Integration

- An **Ignition module** (scope GD) provides:
  - Designer "Diagnostics" panel with one-click runs against a selected device connection.
  - Perspective component "Run Diagnostic" embedded in alarm faceplates and the device-detail screen.
  - A Gateway script `system.comms.runDiagnostic(deviceId)` for use in alarm pipelines (auto-run on stale-data alarm).
  - Periodic "comms health" KPI written back to tags so it can be alarmed/historized like any other tag.
- Reads the Spec 6 tag DB for device metadata; reads Spec 5 IO list for expected register maps; writes results to Spec 8 evidence store when run during FAT/SAT.
- Uses Ignition's built-in driver diagnostic endpoints (Modbus driver status page, OPC UA channel diagnostics) where richer data is available than raw protocol probes.

## 12. Test Plan

- **Probe correctness**: test each probe against a known-good emulator (Spec 1) and verify expected results.
- **RCA precision**: labeled corpus of 200 historical comms incidents; measure top-1 RCA accuracy; target ≥ 70% in v1, ≥ 85% in v3.
- **Performance**: 1,000 devices bulk diagnostic in < 5 minutes.
- **Resilience**: kill agent mid-run; verify clean recovery; kill central; verify agent caches.
- **Security**: pen-test the agent endpoint; verify read-only enforcement; mTLS fuzz.

## 13. Phased Rollout

| Phase | Duration | Scope |
|---|---|---|
| 0 — MVP | 6 weeks | Agent (Linux), L3/L4 + Modbus probes, single-device UI, central API |
| 1 — Multi-protocol | 6 weeks | DNP3, OPC UA, EtherNet/IP, S7, BACnet probes |
| 2 — RCA | 6 weeks | Rule-based RCA, knowledge base, remediation suggestions |
| 3 — Ignition module | 4 weeks | Designer + Perspective integration |
| 4 — Bulk + KPI | 4 weeks | Fleet diagnostics, comms-health KPI tags |
| 5 — Mobile + remote | 6 weeks | Mobile app, WireGuard tunnels, multi-site |
| 6 — ML RCA | 8 weeks | Train classifier, feedback loop |

## 14. Success Metrics

- Time-to-RCA for a typical comms issue: from 1–4 hours to < 5 minutes.
- % of comms incidents resolved without dispatching a tech: ≥ 30% increase.
- RCA top-1 accuracy: ≥ 85% within 12 months.
- False-positive comms alarms reduced by ≥ 40% via continuous comms-health KPI feedback.
- Adoption: deployed at ≥ 50 sites within 12 months.
-e 

---


# Spec 10 — Anomaly Detection on Historian Data

## 1. Problem Statement

Historian data drives every downstream analytic — performance ratios, availability KPIs, regulatory reports, ML models, predictive maintenance. Yet the underlying time-series is full of artifacts: gaps from comms outages, frozen values from failed sensors, statistical outliers from spikes, contextual outliers (a value normal in summer but anomalous in winter), out-of-order or duplicate timestamps, clock drift, quality-code degradations. Most operators don't notice these issues until a downstream report comes out wrong. A continuous anomaly-detection service that watches every historized tag, distinguishes real process events from data-quality issues, and surfaces the root cause without overwhelming operators with false positives — turns the historian from a passive store into an actively-monitored data product.

## 2. User Personas & Stories

**Reliability / Performance Engineer** — *"As a performance engineer, I want to know within an hour when an inverter's irradiance sensor froze so my PR calculations don't silently degrade."*

**Operations** — *"As an operator, I don't want 200 anomaly alerts per day; I want one ranked list of the top issues actually affecting the plant."*

**Data Engineer / Data Scientist** — *"As a data consumer, I want a clean signal — give me an API that says 'this window of this tag is suspect, exclude it' so my models don't poison themselves."*

**Asset Manager (fleet)** — *"As a fleet asset manager, compare anomaly rates across sites and surface the bottom-quartile sites for intervention."*

## 3. Functional Requirements

- **F1**: Detect at least the following anomaly classes:
  - **Gaps**: missing samples vs expected scan rate or vs typical pattern
  - **Frozen values**: identical reading for unusually long periods
  - **Statistical outliers**: |z-score| > k, IQR-based, or modified z-score (MAD)
  - **Contextual outliers**: value abnormal given context tags (irradiance, time-of-day, season, mode)
  - **Trend/ramp anomalies**: rate-of-change outside expected envelope
  - **Out-of-order timestamps**: backwards or non-monotonic time
  - **Duplicate timestamps**: identical timestamp, different values
  - **Clock drift**: systematic offset between device clock and server clock
  - **Quality-code degradation**: tags entering BAD/UNCERTAIN
  - **Communication dropouts**: bursts of gaps tied to a device or gateway
  - **Stuck zero / stuck max**: pinned at limit
  - **Calibration drift**: slow systematic bias
  - **Cross-tag inconsistencies**: e.g., AC power without DC power, breaker state inconsistent with current
- **F2**: 4-layer detection cascade:
  - Layer 1 — deterministic rules (gap, frozen, OOO, dup, quality)
  - Layer 2 — statistical (z-score, MAD, IQR, EWMA control charts)
  - Layer 3 — ML (Isolation Forest, LOF, autoencoder, Prophet/SARIMA residuals, multi-variate VAE)
  - Layer 4 — fleet/peer comparison (this inverter vs its 50 siblings)
- **F3**: Per-tag baselines learned automatically; user can override (manual normal range, mute window).
- **F4**: Suppression: known maintenance windows (read from CMMS), planned outages, manual overrides.
- **F5**: Severity scoring: combine impact (KPI-affected, MWh at risk), persistence, confidence; rank.
- **F6**: Alert routing: per severity → email / Slack / Teams / PagerDuty / SCADA alarm (Spec 3).
- **F7**: Self-tuning: false-positive feedback loop — operator marks "not an issue," tightens thresholds.
- **F8**: Backfill: detect anomalies in historical data; produce a "data quality score" per tag per day.
- **F9**: API for downstream analytics: `GET /tags/{tag}/quality?from=...&to=...` returns time intervals and quality flags.
- **F10**: Multi-historian read support: Ignition Tag Historian, PI Web API, Canary, InfluxDB, TimescaleDB.
- **F11**: UI: anomaly inbox, drill-down trend chart, accept/reject feedback, similar-anomaly search.
- **F12**: Renewables packs: PV-specific (clear-sky model, soiling), wind-specific (power curve), BESS-specific (SoC/SoH, cell voltage divergence) detectors.

## 4. Non-Functional Requirements

- **N1 Scale**: 1 M tags continuously monitored at 1-min effective rate per tag; 100k tags at 1-second rate.
- **N2 Latency**: Detect within ≤ 1 minute of event for high-rate tags; ≤ 15 min for slow tags.
- **N3 False-positive rate**: < 5% after 60 days of feedback (per tenant).
- **N4 Footprint**: Inference runs on commodity CPUs; GPUs optional for training only.
- **N5 Privacy**: On-prem deployable; no telemetry of customer data.
- **N6 Reproducibility**: A detection at time T can be re-evaluated against the same data and same model version → same outcome.

## 5. System Architecture

```
┌────────────────────────────────────────────────────────────────┐
│  Web UI: anomaly inbox, trend, fleet view, feedback            │
└────────────────────────────────────────────────────────────────┘
                              │ REST + WS
┌─────────────────────────────▼──────────────────────────────────┐
│                       Anomaly Service                          │
│  - Tag registry      - Models registry      - Alert router     │
└──┬───────────────────────────────────────────────────────────┬─┘
   │                                                           │
┌──▼─────────────┐   ┌─────────────────┐   ┌──────────────┐ ┌──▼──────┐
│ Historian      │   │ Layer 1 rules   │   │ Layer 2 stats│ │ Storage │
│ readers        │──▶│ (always-on)     │──▶│ (always-on)  │ │ of      │
│ (PI/Ig/etc.)   │   └─────────────────┘   └──────────────┘ │ events  │
└────────────────┘             │                  │         └─────────┘
                               │                  │
                       ┌───────▼────────┐  ┌──────▼─────────┐
                       │ Layer 3 ML     │  │ Layer 4 fleet  │
                       │ (per tag)      │  │ comparison     │
                       └────────────────┘  └────────────────┘
                                   │
                       ┌───────────▼────────────┐
                       │ Severity scoring +     │
                       │ deduplication +        │
                       │ suppression            │
                       └───────────┬────────────┘
                                   │
                       ┌───────────▼────────────┐
                       │ Alert routing + UI     │
                       └────────────────────────┘
```

## 6. Data Models

### Anomaly event (Postgres)

```sql
CREATE TABLE anomaly_event (
  id              UUID PRIMARY KEY,
  tag_path        TEXT NOT NULL,
  detector        TEXT NOT NULL,        -- 'rule:gap', 'stat:zscore', 'ml:iforest', 'fleet:peer'
  detector_ver    TEXT NOT NULL,
  started_at      TIMESTAMPTZ NOT NULL,
  ended_at        TIMESTAMPTZ,
  severity        SMALLINT NOT NULL,    -- 1=critical .. 4=info
  confidence      REAL NOT NULL,        -- 0..1
  details         JSONB NOT NULL,       -- detector-specific
  context_tags    JSONB,                -- snapshots of related tags
  status          anomaly_status NOT NULL DEFAULT 'open',
  feedback        JSONB                 -- operator feedback if any
);

CREATE INDEX ON anomaly_event (tag_path, started_at DESC);
CREATE INDEX ON anomaly_event (status, severity, started_at DESC);
```

### Detector config (YAML)

```yaml
detector:
  id: pv_irradiance_clearsky
  applies_to:
    measurement_class: irradiance
    plant_type: PV
  layer: 4              # contextual / fleet
  parameters:
    clearsky_model: ineichen
    deviation_pct_threshold: 25
    persistence_min_minutes: 15
  severity:
    base: 3
    upgrade_when:
      duration_minutes: 60   # → severity 2
      duration_minutes: 240  # → severity 1
```

### Quality flag API response

```json
{
  "tag": "Plant/Block01/INV-001/AC_Power",
  "from": "2025-12-15T00:00:00Z",
  "to":   "2025-12-15T23:59:59Z",
  "intervals": [
    {"start":"00:00","end":"06:30","quality":"good"},
    {"start":"06:30","end":"06:45","quality":"suspect","reason":"gap_during_sunrise"},
    {"start":"06:45","end":"23:59","quality":"good"}
  ],
  "events": [{"event_id":"...","detector":"rule:gap"}]
}
```

## 7. API Contracts

```
GET    /api/v1/anomalies?tag=...&since=...&severity=...&status=open
PATCH  /api/v1/anomalies/{id}                     # acknowledge / mute / mark-not-anomaly
POST   /api/v1/feedback                           # bulk feedback for retraining
GET    /api/v1/tags/{tag}/quality?from=...&to=...
GET    /api/v1/tags/{tag}/baseline
PUT    /api/v1/tags/{tag}/overrides               # manual normal range
POST   /api/v1/suppressions                       # body: tag(s), window, reason
POST   /api/v1/detectors                          # body: detector config
GET    /api/v1/fleet/quality-score?asset=Plant/Block01
```

## 8. Tech Stack

- **Backend**: Python 3.11 + FastAPI (orchestration), Go workers for high-throughput rule layer.
- **Stream processing**: Apache Flink or Bytewax for windowed stats; Materialize for SQL-style continuous queries.
- **ML**: scikit-learn (IF, LOF), PyTorch (autoencoder, VAE), Prophet for seasonality.
- **Time-series storage**: detection results in TimescaleDB; raw reads streamed (not duplicated).
- **Workflow**: Temporal for backfills.
- **Frontend**: React + Plotly + AG Grid.
- **Alert routers**: pluggable (email, Slack, Teams, PagerDuty, Webhook, Spec 3 alarm DB).

## 9. Key Algorithms / Pseudocode

**Layer 1: Gap detector**

```python
def detect_gaps(samples, expected_interval_ms, max_consecutive_missing=3):
    gaps = []
    for s_prev, s_curr in pairwise(samples):
        dt = (s_curr.t - s_prev.t).total_seconds() * 1000
        missing = round(dt / expected_interval_ms) - 1
        if missing >= max_consecutive_missing:
            gaps.append(Gap(start=s_prev.t, end=s_curr.t, missing=missing))
    return gaps
```

**Layer 1: Frozen value detector**

```python
def detect_frozen(samples, max_identical_seconds, eps=1e-9):
    runs, current = [], []
    for s in samples:
        if not current or abs(s.v - current[0].v) <= eps:
            current.append(s)
        else:
            if (current[-1].t - current[0].t).total_seconds() > max_identical_seconds:
                runs.append(FrozenRun(current[0].t, current[-1].t, current[0].v))
            current = [s]
    return runs
```

**Layer 2: Robust z-score (MAD-based)**

```python
def detect_outliers_mad(samples, k=3.5, window=100):
    out = []
    for i, s in enumerate(samples[window:], start=window):
        win = [x.v for x in samples[i-window:i]]
        med = median(win)
        mad = median([abs(x - med) for x in win]) or 1e-9
        z = 0.6745 * (s.v - med) / mad
        if abs(z) > k:
            out.append(Outlier(s.t, s.v, z))
    return out
```

**Layer 3: Per-tag autoencoder anomaly score**

```python
class TagAutoencoder(nn.Module):
    def __init__(self, window=64, hidden=16):
        super().__init__()
        self.enc = nn.Sequential(nn.Linear(window, 32), nn.ReLU(), nn.Linear(32, hidden))
        self.dec = nn.Sequential(nn.Linear(hidden, 32), nn.ReLU(), nn.Linear(32, window))
    def forward(self, x): return self.dec(self.enc(x))

def score(model, window):
    recon = model(window)
    return float(((recon - window) ** 2).mean())

# Anomaly when score > p99 of training-set scores
```

**Layer 4: Fleet/peer comparison** (e.g., one inverter vs 50 sister inverters)

```python
def detect_peer_outliers(target_series, peer_series_list, robust_k=3.5):
    # at each timestamp, target value vs distribution of peers
    out = []
    for t, v_target in target_series.items():
        peers = [s[t] for s in peer_series_list if t in s]
        if len(peers) < 5: continue
        med = median(peers); mad = median([abs(p - med) for p in peers]) or 1e-9
        z = 0.6745 * (v_target - med) / mad
        if abs(z) > robust_k:
            out.append(PeerOutlier(t, v_target, z, len(peers)))
    return out
```

**Severity scoring**

```python
def severity(event, ctx):
    base = DETECTOR_BASE_SEVERITY[event.detector]
    if ctx.tag_role == 'critical_kpi':       base = max(1, base - 1)
    if event.duration_minutes > 240:         base = max(1, base - 1)
    if ctx.suppressed:                       return 4   # info-only
    if ctx.feedback_history.false_positive_rate > 0.5:
        base = min(4, base + 1)
    return base
```

## 10. Edge Cases

- **Sparse / event-driven tags**: don't apply gap detection unless an expected event rate is set; otherwise frozen detection on event tags is also misleading.
- **Calibrated zero**: A tag legitimately at zero (e.g., inverter at night) is not "frozen"; require context (POA > threshold) before flagging.
- **Mode-aware**: Plant in shutdown vs running — different baselines per mode; encode mode tag.
- **Operator-initiated changes**: Manual setpoint changes can look anomalous; suppress when operator-action tag changes.
- **Daylight savings**: Avoid spurious clock-drift alerts at DST transitions.
- **Backfill jitter**: Backfilled batch loads can produce out-of-order timestamps; whitelist known backfill jobs.
- **Cold-start**: For new tags, rely on rule + statistical layers until ML has 14+ days of training data.
- **Concept drift**: Periodic model retraining (weekly); detect distribution shift to trigger early retrain.

## 11. Ignition-Specific Integration

- An **Ignition module** (scope GD) provides:
  - Designer panel "Anomaly Inbox" — review, ack, mute.
  - Perspective component "Tag Health Card" — embed on equipment views to show recent anomaly count and current quality.
  - Gateway scripted task that periodically writes per-tag quality flags back to companion tags (`<tag>/Quality_Flag`) so they can be alarmed (Spec 3) or used in expressions.
  - Link from Ignition alarm to anomaly drill-down (open inbox filtered to that tag).
- For Ignition Tag Historian, use the gateway query API (`system.tag.queryTagHistory`) for backfill reads; for live, subscribe via OPC UA companion publishing.
- Renewables-specific: include a clear-sky overlay component in Perspective (driven by solar position library) so operators visually see why irradiance was flagged.

## 12. Test Plan

- **Synthetic dataset**: generate time-series with injected anomalies (gaps, frozen, outliers, clock drift) — measure precision/recall per detector.
- **Real-data benchmark**: 10 historical incidents from customer sites, labeled; compute end-to-end recall and time-to-detect.
- **False-positive tracking**: per tenant per week dashboards; CI alert if FPR rises above target.
- **Backfill correctness**: Run backfill on a known dataset; compare against ground truth.
- **Performance**: 100k tags, 1-min detection latency, sustain for 24h continuous on commodity hardware.
- **A/B model tests**: Shadow-run new model versions against production for 14 days; compare metrics.

## 13. Phased Rollout

| Phase | Duration | Scope |
|---|---|---|
| 0 — MVP | 6 weeks | Layer 1 + 2 (rules, stats), Postgres event store, basic UI, Ignition reader |
| 1 — ML | 8 weeks | Layer 3 (IF, autoencoder), per-tag baselines, automated retraining |
| 2 — Fleet | 4 weeks | Layer 4 peer comparison, fleet quality scores |
| 3 — Renewables packs | 6 weeks | PV (clear-sky, soiling), wind (power curve), BESS (SoC/SoH) |
| 4 — Multi-historian | 8 weeks | PI / Canary / Influx / Timescale readers |
| 5 — Feedback loop | 4 weeks | Operator feedback, FPR auto-tuning |
| 6 — Backfill | 6 weeks | Historical scoring, daily quality reports |

## 14. Success Metrics

- Time-to-detect data quality issues: from > 24 hours (often a downstream report) to < 15 minutes.
- False-positive rate after 60-day tuning: < 5%.
- Recall on labeled benchmark: ≥ 90%.
- % of historian-driven analytics using the quality API to mask suspect data: ≥ 50% of pipelines within 12 months.
- MWh recovered per year via faster sensor/comm fault detection (renewables): tracked per site, target ≥ 0.2% of generation.
-e 

---


# Spec 11 — Config-as-Code for PLC/RTU Programs

## 1. Problem Statement

PLC and RTU programs are software, but they are rarely treated as such. Engineers edit them in vendor-specific IDEs (Studio 5000, TIA Portal, EcoStruxure Control Expert, TwinCAT, Concept, ISaGRAF), save proprietary binary projects to network drives or USB sticks, and deploy by walking up to the panel with a laptop. There is typically no version control, no peer review, no automated build, no signed deploys, no rollback, no audit trail. NERC CIP-010 (configuration change management) is met with screenshots and PDFs. The result is operational risk (the wrong code runs in production), security risk (no integrity verification), and engineering inefficiency (every site is a snowflake). A config-as-code platform that uses **PLCopen TC6 XML** as the canonical exchange format, provides per-vendor adapters for round-trip with the IDEs, integrates with Git for versioning/branching/review, and adds signed builds, automated CI testing (using Spec 12 PLC sim), gated deploys, and rollback — gives PLC programs the same engineering rigor as the rest of the software stack.

## 2. User Personas & Stories

**Controls Engineer** — *"Let me edit my Rockwell ACD or Siemens AP file in my favorite IDE, but back it with Git so I can branch for site variants, do PRs, and roll back if I screw up."*

**OT Cybersecurity / Compliance** — *"NERC CIP-010 evidence should be the Git history, signed builds, and gated deployment logs — not screenshots."*

**Engineering Manager** — *"Show me a dashboard of every PLC across our fleet: code version, last deploy, who deployed, signature valid? — at a glance."*

**Field / Commissioning** — *"From the panel, let me deploy the approved version, with an offline workflow that still produces a tamper-evident record."*

## 3. Functional Requirements

- **F1**: **Canonical format**: PLCopen TC6 XML for portable program representation; vendor-specific binary projects round-trip via adapters.
- **F2**: **Vendor adapters** for at least:
  - Rockwell Studio 5000 (.ACD, .L5K, .L5X)
  - Siemens TIA Portal (.ap16/17/18, .zap, .scl, .udt)
  - Schneider EcoStruxure Control Expert / Unity (.STU, .XEF)
  - Beckhoff TwinCAT (.tsproj, .tmc, .tpy)
  - CODESYS (.project, .library, native PLCopen export)
  - Emerson DeltaV (Module Class, Composite, FFB)
  - ABB AC500 (.pro)
  - GE PACSystems (Proficy)
  - OpenPLC (.st, .xml)
- **F3**: **Git workflows**: push/pull, branch, merge, PR, code review; uses customer's GitHub Enterprise / GitLab / Azure DevOps / Bitbucket.
- **F4**: **Semantic diff**: not just text — diff at the level of POU, rung, tag, address; render side-by-side LD/FBD/ST visualizations for review.
- **F5**: **Build pipeline**: validate against PLCopen schema; lint per coding standards (PLCopen Coding Guidelines, customer's house rules); compile via vendor toolchain in CI; emit signed artifact (cosign / PGP).
- **F6**: **CI tests**: build → deploy to Spec 12 PLC simulator → run Spec 8-style FAT/SAT → assert pass.
- **F7**: **Gated deploys**: require N approvals, time-of-day windows, change-control ticket linkage, MFA confirmation; explicit "production" vs "lab" environments.
- **F8**: **Online deploy**: vendor-native online edit and download with verify; for CIP-010 compliance, capture before/after CRC/signature.
- **F9**: **Rollback**: one command reverts to previous signed build; full audit entry.
- **F10**: **Drift detection**: scheduled task reads installed program from PLC, compares to canonical; alert on drift.
- **F11**: **Variant management**: branch per site or per equipment variant; merge in upstream improvements with conflict resolution.
- **F12**: **Audit/forensics**: every change attributable; every deployed binary preserves provenance back to source commits.

## 4. Non-Functional Requirements

- **N1 Coverage**: Day-1 vendor adapters for Rockwell, Siemens, Schneider, Beckhoff, CODESYS (≥ 80% of installed base for our customer focus).
- **N2 Round-trip fidelity**: Vendor binary → PLCopen XML → vendor binary produces functionally identical project (verified by simulator behavior); cosmetic loss (e.g., comments) explicitly tracked.
- **N3 Compliance**: Workflow + audit log satisfies NERC CIP-010, IEC 62443-2-4, GAMP 5 change control.
- **N4 Security**: Signed builds (cosign), code-signing certs in HSM/KMS; SBOM per build (CycloneDX).
- **N5 Performance**: Build + sim test cycle in CI: < 10 minutes for typical 5,000-rung program.
- **N6 Operability**: Engineers can keep using their vendor IDE day-to-day; the tool is a layer on top, not a replacement.

## 5. System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│ Web UI: project, diff, review, build, deploy, drift, audit   │
└──────────────────────────────────────────────────────────────┘
                              │ REST + Git
┌─────────────────────────────▼────────────────────────────────┐
│                 Config-as-Code Service                       │
│  - Project registry  - Build orchestrator  - Approvals       │
└──┬──────────┬──────────────┬───────────────┬──────────────┬─┘
   │          │              │               │              │
┌──▼─────┐ ┌──▼──────┐ ┌────▼──────┐ ┌──────▼─────┐ ┌──────▼─────┐
│Vendor  │ │PLCopen  │ │ CI runner │ │ Signing /  │ │ Deploy     │
│adapters│ │canonical│ │ (sim test │ │ KMS / HSM  │ │ agents     │
│(round- │ │XML +    │ │ via Spec  │ │            │ │ (per site) │
│trip)   │ │semantic │ │ 12)       │ │            │ │            │
└────────┘ │diff     │ └───────────┘ └────────────┘ └────────────┘
           └─────────┘
                              │
                  ┌───────────▼──────────┐
                  │ Git host (GH/GL/etc.)│
                  └──────────────────────┘
```

## 6. Data Models

### Project (Git repo layout)

```
plc-project-pumpstation-23/
├── README.md
├── plcopen/                    # canonical XML
│   ├── main.xml
│   ├── pous/
│   │   ├── PUMP_CTRL.xml
│   │   └── INTERLOCK.xml
│   └── data_types/
│       └── pump_status.xml
├── vendor/                     # original vendor projects
│   ├── rockwell/Pump23.ACD
│   └── siemens/Pump23.zap
├── tests/
│   ├── fat.yaml                # Spec 8 test plan
│   └── unit/
├── .plcops/
│   ├── manifest.yaml
│   └── deploy/
│       ├── lab.yaml
│       └── prod.yaml
└── .github/workflows/build.yml
```

### Manifest (.plcops/manifest.yaml)

```yaml
project:
  id: pumpstation-23
  name: "Pump Station 23"
  vendor_primary: rockwell
  controllers:
    - id: PLC-01
      vendor: rockwell
      family: ControlLogix
      cpu: 1756-L85E
      firmware: ">=33.011"
  build:
    plcopen_dir: plcopen/
    vendor_dir: vendor/
    sign: true
    sign_key_ref: "kms://aws/keys/plc-signing"
  deploy:
    environments:
      - name: lab
        agent: agent-lab-bench
        approvals: 1
      - name: prod
        agent: agent-pump-station-23
        approvals: 2
        windows:
          - mon-fri 02:00-04:00 America/Denver
        change_control: required
  tests:
    fat: tests/fat.yaml
    coverage_min_pct: 90
```

### Build artifact

```json
{
  "build_id": "b-2025-12-15-1342",
  "project": "pumpstation-23",
  "git_commit": "a1b2c3d...",
  "vendor_artifacts": [
    {"vendor": "rockwell", "path": "Pump23.ACD", "sha256": "...", "size": 1234567}
  ],
  "plcopen_xml_sha256": "...",
  "sbom": "cyclonedx-1.5.json",
  "signature": "MEUCIQ..." 
}
```

## 7. API Contracts

```
POST   /api/v1/projects                       # register a new project (Git URL + manifest)
GET    /api/v1/projects/{id}/builds
POST   /api/v1/projects/{id}/builds           # trigger build for a ref
GET    /api/v1/builds/{id}
POST   /api/v1/builds/{id}/sign
POST   /api/v1/deployments                    # body: build_id + env
GET    /api/v1/deployments/{id}
POST   /api/v1/deployments/{id}/approve
POST   /api/v1/deployments/{id}/rollback
GET    /api/v1/controllers/{id}/drift
POST   /api/v1/diff                           # body: 2 refs/builds
GET    /api/v1/audit?project=...&from=...
```

## 8. Tech Stack

- **Backend**: Go for orchestration; vendor adapters in whatever the vendor SDK supports (often C# / .NET for Rockwell/Siemens, Python for OpenPLC).
- **Adapters**: Rockwell Logix Designer SDK / L5X parsing libraries; Siemens TIA Openness API (Windows-only, we run on a dedicated build agent); Schneider Unity Pro SDK; CODESYS Automation Server API; Beckhoff TwinCAT Automation Interface.
- **PLCopen XML**: Internal canonical model, validated against the official XSD; conversion uses the relevant SDK.
- **Git**: native libgit2 + delegated push to customer Git host.
- **CI**: GitHub Actions / GitLab CI runners that we ship as Helm chart + agent images; one runner pool per vendor (because vendor toolchains often require Windows).
- **Signing**: cosign with KMS keys (AWS KMS, Azure Key Vault, HashiCorp Vault, on-prem HSM).
- **SBOM**: Syft for SBOM generation.
- **Frontend**: React + Monaco (text diff) + custom canvas renderer for ladder/FBD diffs.
- **Deploy agents**: Go binary running at sites; mTLS to central; deploys via vendor-native mechanisms (Logix RSLinx, Siemens TIA, Schneider Modicon UMAS, CODESYS Edge Gateway).

## 9. Key Algorithms / Pseudocode

**Round-trip integrity**

```python
def roundtrip_check(vendor_file):
    canonical = vendor_to_plcopen(vendor_file)
    rebuilt = plcopen_to_vendor(canonical, vendor=detect_vendor(vendor_file))
    sim_a = run_in_sim(vendor_file, fat_plan)   # Spec 12
    sim_b = run_in_sim(rebuilt,    fat_plan)
    return behavior_equivalent(sim_a, sim_b)
```

**Semantic diff**

```python
def semantic_diff(plcopen_a, plcopen_b):
    a = parse(plcopen_a); b = parse(plcopen_b)
    diffs = []
    for pou_name in a.pou_names | b.pou_names:
        ap, bp = a.pou(pou_name), b.pou(pou_name)
        if ap and not bp: diffs.append(("removed_pou", pou_name)); continue
        if bp and not ap: diffs.append(("added_pou",   pou_name)); continue
        if ap.language == bp.language == "LD":
            diffs += diff_ladder(ap.body, bp.body)
        elif ap.language == bp.language == "ST":
            diffs += diff_st(ap.body, bp.body)
        elif ap.language == bp.language == "FBD":
            diffs += diff_fbd(ap.body, bp.body)
        diffs += diff_tags(ap.vars, bp.vars)
    return diffs
```

**Gated deploy workflow (Temporal)**

```python
@workflow.defn
class DeployWorkflow:
    @workflow.run
    async def run(self, build_id, env):
        build = await activity.fetch_build(build_id)
        await activity.verify_signature(build)
        await activity.precheck_change_control(build_id, env)
        approvals_needed = env.approvals
        approvers = []
        while len(approvers) < approvals_needed:
            sig = await workflow.wait_condition(self.next_approval, timeout=24*3600)
            approvers.append(sig)
        if not in_window(env.windows): await workflow.wait_until_window(env.windows)
        agent = await activity.select_agent(env.agent)
        snapshot = await activity.snapshot_current(agent)   # for rollback
        result = await activity.deploy(agent, build)
        verify = await activity.post_deploy_verify(agent, build)
        if not verify.ok:
            await activity.deploy(agent, snapshot)           # auto rollback
            raise DeployFailed(verify)
        await activity.audit_log(build_id, env, approvers, agent, verify)
```

**Drift detection**

```python
def check_drift(controller):
    installed = controller.read_program_signature()  # vendor-specific
    expected  = registry.expected_signature(controller.id)
    return Drift(controller.id, installed, expected) if installed != expected else None
```

## 10. Edge Cases

- **Vendor toolchain on Windows only**: provide Windows build agents in the runner pool; document costs.
- **TIA Openness license**: Siemens charges for the API; surface this requirement in onboarding docs.
- **Online edits**: Some sites do live edits; capture them as commits via "Commit installed program" workflow that pulls from device.
- **Comments / formatting loss**: PLCopen XML doesn't preserve every cosmetic detail; canonical model retains comments where possible; differences flagged.
- **Tags vs program separation**: Rockwell allows separate program-scoped vs controller-scoped tags; canonical model preserves scope.
- **Add-on Instructions / Function Blocks**: Vendor-specific encrypted blocks may not round-trip; treat as opaque, sign as binary, never transform.
- **Multi-controller projects**: One Git project may target multiple controllers; manifest defines deploy targets independently.
- **Air-gapped sites**: Deploy agent supports offline mode — sneakernet a signed bundle, agent verifies signature offline, deploys, syncs audit log on next connection.

## 11. Ignition-Specific Integration

- The PLC config-as-code system is **upstream** of Ignition: the same Git repo can hold PLC code and Ignition project export (.proj or .gwbk).
- Provide a CI step that re-imports the Ignition project export against the new PLC tag database, runs lint (Spec 6), regenerates alarms (Spec 3) and screens (Spec 2) where downstream artifacts depend on PLC tag changes.
- Provide an **Ignition module** (scope GD) that:
  - Adds a Designer panel "PLC Program Versions" — show installed version per device, link to Git commit, drift warning.
  - Adds a Perspective component "Controller Health" — current code version, signature valid, last deploy.
  - Hooks into Spec 9 comms diagnostics — if a controller fails comms, also report its expected vs installed code version.
- Integrate with Spec 12 PLC simulator: CI for the PLC project builds and runs against simulator before any approval gate; Ignition can be configured against the simulator for pre-deploy SCADA validation.

## 12. Test Plan

- **Round-trip**: For every supported vendor, a corpus of representative projects → round-trip → simulator behavior equivalence.
- **Diff**: Golden diff samples (e.g., add rung, change tag type, rename POU); CI verifies the diff renderer captures intent.
- **Gated deploy**: End-to-end test with mocked approvers; verify approvals enforced, windows enforced, rollback fires on verify failure.
- **Drift**: Deliberately deploy a different program directly via vendor tool; verify drift detector flags within 1 cycle.
- **Compliance**: NERC CIP-010 audit checklist mapped to features; produce sample evidence pack.
- **Performance**: Full build + sim test cycle for 5,000-rung program: < 10 min.

## 13. Phased Rollout

| Phase | Duration | Scope |
|---|---|---|
| 0 — MVP | 10 weeks | Manifest + Git registration, Rockwell adapter (L5X), basic build, semantic ST/LD diff, lab deploy |
| 1 — Compliance | 8 weeks | Signing, KMS, audit, gated deploy with approvals |
| 2 — More vendors | 12 weeks | Siemens TIA, Schneider Unity, CODESYS, Beckhoff |
| 3 — CI sim | 8 weeks | Spec 12 integration; auto FAT in CI |
| 4 — Drift / fleet | 6 weeks | Drift detection, fleet dashboard, Ignition module |
| 5 — Variants | 6 weeks | Branch-per-site workflows, upstream merge with conflict resolution |
| 6 — Long tail | ongoing | Emerson, ABB, GE, OpenPLC, vendor adapters as needed |

## 14. Success Metrics

- % of PLC projects under version control: from < 20% to > 90% within 18 months.
- Time to deploy a tested change to production: from days/weeks to hours, with full audit.
- NERC CIP-010 audit findings on configuration management: ≥ 80% reduction.
- Mean lead time for a hotfix (lab to field): < 4 hours including approvals.
- Drift incidents detected vs found post-hoc: ≥ 95% caught within 24h.
- Rollback success rate when invoked: 100%.
-e 

---


# Spec 12 — PLC Hardware Emulation / Containerized PLC Runtime

## 1. Problem Statement

End-to-end testing of a SCADA → PLC system requires the PLC. Today this means physical hardware: rented bench units, borrowed shop demos, "sim racks" hand-wired by a controls engineer. This blocks engineering teams behind hardware logistics, prevents true CI, and means SCADA logic, alarms, and HMI screens are first exercised against the real thing only at FAT — late and costly. The market does offer simulators — OpenPLC, CODESYS Virtual Control SL, Beckhoff TwinCAT 3 XAR for Linux, Siemens S7-PLCSIM Advanced, Rockwell Studio 5000 Logix Emulate — but they are deployed ad hoc, on engineer laptops, behind vendor licensing, with no standard programmatic interface for I/O injection or CI integration. A platform that wraps these emulators as **containerized PLC runtimes**, exposes a uniform programmatic I/O / state / time API, supports protocol exposure (so SCADA talks to the emulator over real Modbus/EtherNet-IP/etc.), enables time acceleration and scenario replay, and integrates with Spec 1 (protocol emulators), Spec 8 (FAT/SAT), and Spec 11 (config-as-code) — turns the "no PLC available" problem into a non-issue.

## 2. User Personas & Stories

**Controls Engineer** — *"Spin up an emulated ControlLogix or S7-1500 with my code loaded, talk to it from Ignition over EtherNet/IP or PROFINET, prove my code works before I drive to the panel."*

**SCADA Test Engineer** — *"In CI, build a fleet of 20 emulated PLCs running the production code, run the SCADA test suite against them, fail the build if anything regresses."*

**Trainer / OEM** — *"Provide each trainee a personal containerized PLC sandbox they can break and reset without affecting others."*

**Process / Plant Simulation Engineer** — *"Co-simulate the PLC with a process model (e.g., FMU from a chemical or thermal model) so I can validate control loops with realistic dynamics."*

## 3. Functional Requirements

- **F1**: Support runtime engines:
  - OpenPLC v3 (open source, IEC 61131-3 ST/LD/FBD/SFC/IL)
  - CODESYS Virtual Control SL (license-tied)
  - Beckhoff TwinCAT 3 XAR for Linux (license-tied)
  - Siemens S7-PLCSIM Advanced (Windows, license-tied; dockerizable via Windows containers)
  - Rockwell Studio 5000 Logix Emulate (Windows; bring-your-own-license)
  - Schneider EcoStruxure Machine SCADA Expert / SoMachine simulator
  - Mitsubishi GX Works simulator (later)
  - GE PACSystems simulator (later)
- **F2**: **Containerization**: each runtime packaged as an OCI image; orchestrated by Kubernetes (Helm charts) or Docker Compose for desktop.
- **F3**: **Program loading**: ingest a build artifact from Spec 11 and load it into the emulator (vendor-specific mechanism abstracted by adapter).
- **F4**: **Programmatic I/O injection**: REST + gRPC API to read/write any I/O point, internal variable, or memory address; bulk operations.
- **F5**: **Protocol exposure**: SCADA-facing protocols on configurable ports — Modbus TCP/RTU, EtherNet/IP (CIP), PROFINET (where supported), OPC UA, S7 ISO-on-TCP, BACnet, IEC 60870-5-104.
- **F6**: **Time control**: real-time, fixed step, accelerated (10×, 100×), pause, single-step, jump-to-event.
- **F7**: **Scenario / replay**: record an execution (I/O timeline + state); replay; assert on timing.
- **F8**: **Co-simulation**: FMI 2.0/3.0 master so a process model FMU can be coupled to the emulated PLC; supports synchronous and asynchronous modes.
- **F9**: **Snapshot / restore**: save full state (variables, retentive data, timers); restore to start of a scenario in < 1 second.
- **F10**: **Fault injection**: simulate I/O card failures, comms loss, scan-time spikes, retentive memory loss.
- **F11**: **Multi-controller systems**: orchestrate fleets where multiple emulated PLCs interconnect (e.g., producer/consumer, peer-to-peer EtherNet/IP, GOOSE between IEDs).
- **F12**: **Observability**: per-emulator metrics (scan time, CPU, memory, comm stats), structured logs, OpenTelemetry traces.

## 4. Non-Functional Requirements

- **N1 Footprint**: Single OpenPLC instance < 100 MB RAM idle; CODESYS < 500 MB; Logix Emulate ~2 GB.
- **N2 Determinism**: In step mode, scan time deterministic; replay reproduces state exactly.
- **N3 Throughput**: Single host (16 cores, 64 GB) supports ≥ 50 OpenPLC + 10 CODESYS instances concurrently with real-time scans.
- **N4 Licensing compliance**: Vendor-license-tied runtimes (CODESYS, Siemens, Rockwell) bring-your-own-license; the platform enforces license checks and reports usage.
- **N5 Security**: Runtimes run in least-privilege containers; gNMI/gRPC management plane uses mTLS; no secrets baked into images.
- **N6 Portability**: Linux first; Windows containers supported for Siemens/Rockwell on appropriate hosts.

## 5. System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│  Web UI / CLI / SDK                                          │
└──────────────────────────────────────────────────────────────┘
                              │ REST + gRPC (mTLS)
┌─────────────────────────────▼────────────────────────────────┐
│                 PLC Sim Control Plane (Go)                   │
│  - Fleet orchestrator   - License manager   - Audit          │
└──┬──────────┬──────────────┬───────────────┬──────────────┬─┘
   │          │              │               │              │
┌──▼─────┐ ┌──▼──────┐ ┌────▼──────┐ ┌──────▼─────┐ ┌──────▼─────┐
│OpenPLC │ │CODESYS  │ │S7-PLCSIM  │ │Logix       │ │TwinCAT     │
│runtime │ │Virtual  │ │Advanced   │ │Emulate     │ │XAR         │
│adapter │ │Control  │ │adapter    │ │adapter     │ │adapter     │
│        │ │adapter  │ │           │ │            │ │            │
└────────┘ └─────────┘ └───────────┘ └────────────┘ └────────────┘
                              │
                  ┌───────────▼──────────┐
                  │ I/O bus (NATS)        │  ← shared with Spec 1
                  └───────────────────────┘
                              │
                  ┌───────────▼──────────┐
                  │ FMI co-sim master     │
                  │ (FMU loader)          │
                  └───────────────────────┘
                              │
                  ┌───────────▼──────────┐
                  │ Time service / step   │
                  │ scheduler             │
                  └───────────────────────┘
```

Each runtime is a pod (or container) with:
- the runtime engine
- an adapter sidecar exposing the uniform API
- protocol endpoints exposed as Service ports

The control plane exposes the fleet through a single API and brokers I/O via NATS so Spec 1 protocol emulators and Spec 12 PLCs can interoperate (e.g., a virtual flow meter from Spec 1 supplies values to an emulated PLC's input).

## 6. Data Models

### Emulator instance (Kubernetes CRD-style)

```yaml
apiVersion: plcsim.io/v1
kind: PLCInstance
metadata:
  name: plc-pump-23
spec:
  runtime: openplc                  # | codesys | s7-plcsim | logix-emulate | twincat
  version: "3.2.0"
  programArtifact:
    buildId: b-2025-12-15-1342      # from Spec 11
    blobRef: s3://plc-builds/b-2025-12-15-1342/openplc.st
  resources:
    cpu: "500m"
    memory: "256Mi"
  protocols:
    - kind: modbus_tcp
      port: 502
    - kind: opcua
      port: 4840
      endpoint: opc.tcp://0.0.0.0:4840/plc-pump-23
  io:
    inputs:
      - name: pump_running_fb
        address: "%IX0.0"
        type: bool
      - name: flow_lpm
        address: "%IW0"
        type: int
        scale: 0.1
        eu: lpm
    outputs:
      - name: pump_run_cmd
        address: "%QX0.0"
        type: bool
  time:
    mode: realtime                  # | fixed_step | accelerated | step
    step_us: 10000                  # 10ms scan if fixed_step
status:
  phase: Running
  scanTimeUs: 9740
  uptimeSec: 1337
```

### Scenario

```yaml
scenario:
  id: pump-startup-with-low-flow-trip
  fleet: [plc-pump-23]
  steps:
    - at: 0s
      io_set: { plc-pump-23/inputs/start_pb: true }
    - at: 1s
      io_set: { plc-pump-23/inputs/flow_lpm: 50 }     # below trip
    - at: 2s
      assert:
        plc-pump-23/outputs/pump_run_cmd: false
        plc-pump-23/internal/alarm_low_flow: true
    - at: 3s
      io_set: { plc-pump-23/inputs/flow_lpm: 200 }
    - at: 4s
      io_set: { plc-pump-23/inputs/reset_pb: true }
    - at: 5s
      io_set: { plc-pump-23/inputs/start_pb: true }
    - at: 6s
      assert:
        plc-pump-23/outputs/pump_run_cmd: true
```

## 7. API Contracts

### REST

```
POST   /api/v1/instances                    # create instance from spec
GET    /api/v1/instances/{name}
DELETE /api/v1/instances/{name}
POST   /api/v1/instances/{name}/start
POST   /api/v1/instances/{name}/stop
POST   /api/v1/instances/{name}/load        # load build artifact
GET    /api/v1/instances/{name}/io
PUT    /api/v1/instances/{name}/io/{point}  # body: {"value": ...}
POST   /api/v1/instances/{name}/snapshot
POST   /api/v1/instances/{name}/restore     # body: snapshot id
POST   /api/v1/instances/{name}/time        # body: {"mode":"step","step_us":1000}
POST   /api/v1/scenarios/{id}/run
GET    /api/v1/scenarios/{id}/runs/{run_id}
POST   /api/v1/cosim/fmu                     # body: FMU + binding
```

### gRPC (excerpt)

```protobuf
service PLCSim {
  rpc CreateInstance(InstanceSpec) returns (Instance);
  rpc StreamIO(StreamIORequest) returns (stream IOEvent);
  rpc SetIO(SetIORequest) returns (IOState);
  rpc Step(StepRequest) returns (StepResponse);
  rpc Snapshot(SnapshotRequest) returns (Snapshot);
  rpc Restore(RestoreRequest) returns (Instance);
}
```

## 8. Tech Stack

- **Control plane**: Go + Connect-RPC + gRPC-gateway → REST.
- **Adapters**: per-runtime adapter sidecars; Go for OpenPLC; C# for CODESYS (its API is .NET); .NET for Siemens S7-PLCSIM Advanced (uses S7-PLCSIM Advanced .NET API on Windows hosts); .NET for Logix Emulate.
- **Containers**: distroless / minimal base; multi-arch; for Windows-only runtimes, Windows Server Core base.
- **Orchestration**: Kubernetes 1.27+ via Helm chart and a custom operator that reconciles `PLCInstance` CRs; Docker Compose for desktop dev.
- **I/O bus**: NATS JetStream — shared with Spec 1 emulators so SCADA → emulated field device → PLC tag pipelines work end-to-end.
- **Co-sim**: PyFMI or FMPy for FMU loading; custom master-algorithm loop for sync.
- **Storage**: PostgreSQL for instance metadata; MinIO/S3 for snapshots and FMUs.
- **Observability**: OpenTelemetry, Prometheus, Loki.

## 9. Key Algorithms / Pseudocode

**Fixed-step scheduler with FMI co-sim**

```python
def cosim_loop(plc, fmu, step_us):
    t = 0
    while True:
        # 1. write PLC outputs to FMU inputs
        for binding in bindings_plc_to_fmu:
            fmu.set(binding.fmu_var, plc.read(binding.plc_var))
        # 2. step FMU
        fmu.do_step(t * 1e-6, step_us * 1e-6)
        # 3. write FMU outputs to PLC inputs
        for binding in bindings_fmu_to_plc:
            plc.write(binding.plc_var, fmu.get(binding.fmu_var))
        # 4. step PLC one scan
        plc.scan(step_us)
        t += step_us
        if accelerated:
            pass  # don't sleep
        else:
            time.sleep_until(start + t * 1e-6)
```

**Snapshot for OpenPLC**

```python
def snapshot_openplc(instance):
    # OpenPLC stores state in glueVars / retain file; snapshot the runtime image
    state = {
        "retain": fs.read(f"/openplc/{instance}/retain.bin"),
        "io_image": runtime_api.dump_io(instance),
        "internal": runtime_api.dump_internal(instance),
        "scan_time_us": runtime_api.scan_time(instance),
    }
    return store_snapshot(state)
```

**SCADA-protocol exposure** — adapter embeds a Modbus TCP server that maps `%MW0..%MW100` to register 40001..40101 etc. Reuse Spec 1 protocol engines as a library.

```python
def expose_modbus(instance, mapping):
    server = ModbusTcpServer(port=mapping.port)
    @server.on_read
    def read(unit, fc, addr, count):
        plc_addr = mapping.modbus_to_plc(addr)
        return [instance.read_word(plc_addr + i) for i in range(count)]
    @server.on_write
    def write(unit, fc, addr, values):
        for i, v in enumerate(values):
            instance.write_word(mapping.modbus_to_plc(addr) + i, v)
    server.start()
```

## 10. Edge Cases

- **Vendor-licensed runtimes** require a license server reachable from the pod; plan for license-server failure (fail closed, clear error).
- **Real-time on Linux** — without RT kernel, scan jitter increases; for deterministic tests, use `PREEMPT_RT` nodes or accept jitter and use replay in step mode for asserts.
- **Windows containers** — running Logix Emulate / S7-PLCSIM in Windows containers requires Windows-host Kubernetes nodes; document; provide hybrid-cluster Helm chart.
- **PROFINET emulation** is rare in pure software; for Siemens, S7-PLCSIM Advanced emulates PROFINET; document support per runtime.
- **Network namespace** — multiple emulators on one host may want unique IPs; use macvlan or a dedicated per-pod network namespace + Service.
- **Memory growth** — long-running emulators with large retentive areas can grow; periodic snapshot + restart pattern.
- **GOOSE/SV multicast** in pod networking requires an overlay that supports multicast (Calico+IPVS often doesn't); document the supported CNIs.

## 11. Ignition-Specific Integration

- Ignition connects to emulated PLCs over their exposed protocols using its standard drivers — no special integration required for basic use.
- Provide a sample **Ignition project export** wired to an OpenPLC sample (Modbus TCP) and a CODESYS sample (OPC UA) so users get an end-to-end SCADA-to-PLC demo in 15 minutes.
- Provide an **Ignition module** (scope GD) that:
  - Adds a Designer wizard "Connect to PLC Sim Fleet" — discovers emulators via the control plane API, auto-creates Device Connections in Ignition.
  - Adds a Perspective dashboard showing emulator fleet status (scan time, CPU, comms count).
  - Hooks Spec 8 FAT/SAT execution: a test step can call `POST /api/v1/instances/{name}/io/{point}` to drive a PLC input; the SCADA reads the resulting tag; assertion verifies behavior.
- Tight integration with Spec 11 (config-as-code): in CI, the build pipeline launches an ephemeral emulator from the build artifact, runs Spec 8 tests, tears down — all inside GitHub Actions / GitLab CI.

## 12. Test Plan

- **Per-runtime smoke**: For each supported runtime, a known-good program loads, runs, and exposes I/O reachable via Modbus/OPC UA.
- **Round-trip with Spec 11**: Build artifact loads, runs same scenario as on real hardware (where possible), behavior matches.
- **Determinism**: Step mode scenarios produce identical outputs across 100 runs.
- **Performance**: 50 OpenPLC instances on a single 16-core host sustain real-time 10 ms scans for 24 hours.
- **Co-sim**: FMU + PLC closed-loop control test; system stable; control performance within tolerance.
- **Fault injection**: Drop comms to half the fleet; verify SCADA detects, alarms via Spec 3; restoration recovers.
- **Hybrid cluster**: Linux + Windows nodes; deploy mixed runtimes; verify scheduling, networking.

## 13. Phased Rollout

| Phase | Duration | Scope |
|---|---|---|
| 0 — MVP | 8 weeks | OpenPLC adapter, control plane API, Modbus TCP exposure, single-host Docker Compose, basic UI |
| 1 — Kubernetes | 4 weeks | Helm chart, operator with `PLCInstance` CRD, multi-instance fleets |
| 2 — CODESYS | 6 weeks | CODESYS Virtual Control SL adapter, license integration, OPC UA exposure |
| 3 — Siemens | 8 weeks | S7-PLCSIM Advanced adapter, Windows container support, S7 ISO-on-TCP exposure |
| 4 — Rockwell | 8 weeks | Studio 5000 Logix Emulate adapter, EtherNet/IP CIP exposure |
| 5 — Co-sim | 6 weeks | FMI 2.0/3.0 master, sample FMUs (tank, motor, pipe), tutorials |
| 6 — Time control + replay | 4 weeks | Step mode, accelerated time, snapshot/restore, scenario record/replay |
| 7 — Beckhoff & long tail | ongoing | TwinCAT XAR, Schneider, Mitsubishi, GE |

## 14. Success Metrics

- % of new SCADA + PLC projects with end-to-end CI tests against emulated PLCs: ≥ 60% within 18 months.
- Field defects attributable to PLC-SCADA integration found pre-FAT: ≥ 40% increase (shifted left).
- Emulator-driven training environments deployed: ≥ 100 within 12 months.
- Mean time from PLC code commit to running in CI: < 5 minutes.
- Fleet density: ≥ 50 emulators per commodity host sustained.
- Snapshot/restore time for a typical instance: < 1 second p95.
-e 

---


