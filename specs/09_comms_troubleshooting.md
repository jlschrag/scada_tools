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
