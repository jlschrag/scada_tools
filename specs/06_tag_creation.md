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
