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
