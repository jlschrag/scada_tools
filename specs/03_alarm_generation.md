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
