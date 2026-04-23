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
