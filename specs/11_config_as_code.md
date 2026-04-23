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
