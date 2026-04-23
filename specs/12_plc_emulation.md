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
