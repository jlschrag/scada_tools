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
