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
