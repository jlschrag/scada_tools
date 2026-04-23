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
