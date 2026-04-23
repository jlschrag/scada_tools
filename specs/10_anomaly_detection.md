# Spec 10 — Anomaly Detection on Historian Data

## 1. Problem Statement

Historian data drives every downstream analytic — performance ratios, availability KPIs, regulatory reports, ML models, predictive maintenance. Yet the underlying time-series is full of artifacts: gaps from comms outages, frozen values from failed sensors, statistical outliers from spikes, contextual outliers (a value normal in summer but anomalous in winter), out-of-order or duplicate timestamps, clock drift, quality-code degradations. Most operators don't notice these issues until a downstream report comes out wrong. A continuous anomaly-detection service that watches every historized tag, distinguishes real process events from data-quality issues, and surfaces the root cause without overwhelming operators with false positives — turns the historian from a passive store into an actively-monitored data product.

## 2. User Personas & Stories

**Reliability / Performance Engineer** — *"As a performance engineer, I want to know within an hour when an inverter's irradiance sensor froze so my PR calculations don't silently degrade."*

**Operations** — *"As an operator, I don't want 200 anomaly alerts per day; I want one ranked list of the top issues actually affecting the plant."*

**Data Engineer / Data Scientist** — *"As a data consumer, I want a clean signal — give me an API that says 'this window of this tag is suspect, exclude it' so my models don't poison themselves."*

**Asset Manager (fleet)** — *"As a fleet asset manager, compare anomaly rates across sites and surface the bottom-quartile sites for intervention."*

## 3. Functional Requirements

- **F1**: Detect at least the following anomaly classes:
  - **Gaps**: missing samples vs expected scan rate or vs typical pattern
  - **Frozen values**: identical reading for unusually long periods
  - **Statistical outliers**: |z-score| > k, IQR-based, or modified z-score (MAD)
  - **Contextual outliers**: value abnormal given context tags (irradiance, time-of-day, season, mode)
  - **Trend/ramp anomalies**: rate-of-change outside expected envelope
  - **Out-of-order timestamps**: backwards or non-monotonic time
  - **Duplicate timestamps**: identical timestamp, different values
  - **Clock drift**: systematic offset between device clock and server clock
  - **Quality-code degradation**: tags entering BAD/UNCERTAIN
  - **Communication dropouts**: bursts of gaps tied to a device or gateway
  - **Stuck zero / stuck max**: pinned at limit
  - **Calibration drift**: slow systematic bias
  - **Cross-tag inconsistencies**: e.g., AC power without DC power, breaker state inconsistent with current
- **F2**: 4-layer detection cascade:
  - Layer 1 — deterministic rules (gap, frozen, OOO, dup, quality)
  - Layer 2 — statistical (z-score, MAD, IQR, EWMA control charts)
  - Layer 3 — ML (Isolation Forest, LOF, autoencoder, Prophet/SARIMA residuals, multi-variate VAE)
  - Layer 4 — fleet/peer comparison (this inverter vs its 50 siblings)
- **F3**: Per-tag baselines learned automatically; user can override (manual normal range, mute window).
- **F4**: Suppression: known maintenance windows (read from CMMS), planned outages, manual overrides.
- **F5**: Severity scoring: combine impact (KPI-affected, MWh at risk), persistence, confidence; rank.
- **F6**: Alert routing: per severity → email / Slack / Teams / PagerDuty / SCADA alarm (Spec 3).
- **F7**: Self-tuning: false-positive feedback loop — operator marks "not an issue," tightens thresholds.
- **F8**: Backfill: detect anomalies in historical data; produce a "data quality score" per tag per day.
- **F9**: API for downstream analytics: `GET /tags/{tag}/quality?from=...&to=...` returns time intervals and quality flags.
- **F10**: Multi-historian read support: Ignition Tag Historian, PI Web API, Canary, InfluxDB, TimescaleDB.
- **F11**: UI: anomaly inbox, drill-down trend chart, accept/reject feedback, similar-anomaly search.
- **F12**: Renewables packs: PV-specific (clear-sky model, soiling), wind-specific (power curve), BESS-specific (SoC/SoH, cell voltage divergence) detectors.

## 4. Non-Functional Requirements

- **N1 Scale**: 1 M tags continuously monitored at 1-min effective rate per tag; 100k tags at 1-second rate.
- **N2 Latency**: Detect within ≤ 1 minute of event for high-rate tags; ≤ 15 min for slow tags.
- **N3 False-positive rate**: < 5% after 60 days of feedback (per tenant).
- **N4 Footprint**: Inference runs on commodity CPUs; GPUs optional for training only.
- **N5 Privacy**: On-prem deployable; no telemetry of customer data.
- **N6 Reproducibility**: A detection at time T can be re-evaluated against the same data and same model version → same outcome.

## 5. System Architecture

```
┌────────────────────────────────────────────────────────────────┐
│  Web UI: anomaly inbox, trend, fleet view, feedback            │
└────────────────────────────────────────────────────────────────┘
                              │ REST + WS
┌─────────────────────────────▼──────────────────────────────────┐
│                       Anomaly Service                          │
│  - Tag registry      - Models registry      - Alert router     │
└──┬───────────────────────────────────────────────────────────┬─┘
   │                                                           │
┌──▼─────────────┐   ┌─────────────────┐   ┌──────────────┐ ┌──▼──────┐
│ Historian      │   │ Layer 1 rules   │   │ Layer 2 stats│ │ Storage │
│ readers        │──▶│ (always-on)     │──▶│ (always-on)  │ │ of      │
│ (PI/Ig/etc.)   │   └─────────────────┘   └──────────────┘ │ events  │
└────────────────┘             │                  │         └─────────┘
                               │                  │
                       ┌───────▼────────┐  ┌──────▼─────────┐
                       │ Layer 3 ML     │  │ Layer 4 fleet  │
                       │ (per tag)      │  │ comparison     │
                       └────────────────┘  └────────────────┘
                                   │
                       ┌───────────▼────────────┐
                       │ Severity scoring +     │
                       │ deduplication +        │
                       │ suppression            │
                       └───────────┬────────────┘
                                   │
                       ┌───────────▼────────────┐
                       │ Alert routing + UI     │
                       └────────────────────────┘
```

## 6. Data Models

### Anomaly event (Postgres)

```sql
CREATE TABLE anomaly_event (
  id              UUID PRIMARY KEY,
  tag_path        TEXT NOT NULL,
  detector        TEXT NOT NULL,        -- 'rule:gap', 'stat:zscore', 'ml:iforest', 'fleet:peer'
  detector_ver    TEXT NOT NULL,
  started_at      TIMESTAMPTZ NOT NULL,
  ended_at        TIMESTAMPTZ,
  severity        SMALLINT NOT NULL,    -- 1=critical .. 4=info
  confidence      REAL NOT NULL,        -- 0..1
  details         JSONB NOT NULL,       -- detector-specific
  context_tags    JSONB,                -- snapshots of related tags
  status          anomaly_status NOT NULL DEFAULT 'open',
  feedback        JSONB                 -- operator feedback if any
);

CREATE INDEX ON anomaly_event (tag_path, started_at DESC);
CREATE INDEX ON anomaly_event (status, severity, started_at DESC);
```

### Detector config (YAML)

```yaml
detector:
  id: pv_irradiance_clearsky
  applies_to:
    measurement_class: irradiance
    plant_type: PV
  layer: 4              # contextual / fleet
  parameters:
    clearsky_model: ineichen
    deviation_pct_threshold: 25
    persistence_min_minutes: 15
  severity:
    base: 3
    upgrade_when:
      duration_minutes: 60   # → severity 2
      duration_minutes: 240  # → severity 1
```

### Quality flag API response

```json
{
  "tag": "Plant/Block01/INV-001/AC_Power",
  "from": "2025-12-15T00:00:00Z",
  "to":   "2025-12-15T23:59:59Z",
  "intervals": [
    {"start":"00:00","end":"06:30","quality":"good"},
    {"start":"06:30","end":"06:45","quality":"suspect","reason":"gap_during_sunrise"},
    {"start":"06:45","end":"23:59","quality":"good"}
  ],
  "events": [{"event_id":"...","detector":"rule:gap"}]
}
```

## 7. API Contracts

```
GET    /api/v1/anomalies?tag=...&since=...&severity=...&status=open
PATCH  /api/v1/anomalies/{id}                     # acknowledge / mute / mark-not-anomaly
POST   /api/v1/feedback                           # bulk feedback for retraining
GET    /api/v1/tags/{tag}/quality?from=...&to=...
GET    /api/v1/tags/{tag}/baseline
PUT    /api/v1/tags/{tag}/overrides               # manual normal range
POST   /api/v1/suppressions                       # body: tag(s), window, reason
POST   /api/v1/detectors                          # body: detector config
GET    /api/v1/fleet/quality-score?asset=Plant/Block01
```

## 8. Tech Stack

- **Backend**: Python 3.11 + FastAPI (orchestration), Go workers for high-throughput rule layer.
- **Stream processing**: Apache Flink or Bytewax for windowed stats; Materialize for SQL-style continuous queries.
- **ML**: scikit-learn (IF, LOF), PyTorch (autoencoder, VAE), Prophet for seasonality.
- **Time-series storage**: detection results in TimescaleDB; raw reads streamed (not duplicated).
- **Workflow**: Temporal for backfills.
- **Frontend**: React + Plotly + AG Grid.
- **Alert routers**: pluggable (email, Slack, Teams, PagerDuty, Webhook, Spec 3 alarm DB).

## 9. Key Algorithms / Pseudocode

**Layer 1: Gap detector**

```python
def detect_gaps(samples, expected_interval_ms, max_consecutive_missing=3):
    gaps = []
    for s_prev, s_curr in pairwise(samples):
        dt = (s_curr.t - s_prev.t).total_seconds() * 1000
        missing = round(dt / expected_interval_ms) - 1
        if missing >= max_consecutive_missing:
            gaps.append(Gap(start=s_prev.t, end=s_curr.t, missing=missing))
    return gaps
```

**Layer 1: Frozen value detector**

```python
def detect_frozen(samples, max_identical_seconds, eps=1e-9):
    runs, current = [], []
    for s in samples:
        if not current or abs(s.v - current[0].v) <= eps:
            current.append(s)
        else:
            if (current[-1].t - current[0].t).total_seconds() > max_identical_seconds:
                runs.append(FrozenRun(current[0].t, current[-1].t, current[0].v))
            current = [s]
    return runs
```

**Layer 2: Robust z-score (MAD-based)**

```python
def detect_outliers_mad(samples, k=3.5, window=100):
    out = []
    for i, s in enumerate(samples[window:], start=window):
        win = [x.v for x in samples[i-window:i]]
        med = median(win)
        mad = median([abs(x - med) for x in win]) or 1e-9
        z = 0.6745 * (s.v - med) / mad
        if abs(z) > k:
            out.append(Outlier(s.t, s.v, z))
    return out
```

**Layer 3: Per-tag autoencoder anomaly score**

```python
class TagAutoencoder(nn.Module):
    def __init__(self, window=64, hidden=16):
        super().__init__()
        self.enc = nn.Sequential(nn.Linear(window, 32), nn.ReLU(), nn.Linear(32, hidden))
        self.dec = nn.Sequential(nn.Linear(hidden, 32), nn.ReLU(), nn.Linear(32, window))
    def forward(self, x): return self.dec(self.enc(x))

def score(model, window):
    recon = model(window)
    return float(((recon - window) ** 2).mean())

# Anomaly when score > p99 of training-set scores
```

**Layer 4: Fleet/peer comparison** (e.g., one inverter vs 50 sister inverters)

```python
def detect_peer_outliers(target_series, peer_series_list, robust_k=3.5):
    # at each timestamp, target value vs distribution of peers
    out = []
    for t, v_target in target_series.items():
        peers = [s[t] for s in peer_series_list if t in s]
        if len(peers) < 5: continue
        med = median(peers); mad = median([abs(p - med) for p in peers]) or 1e-9
        z = 0.6745 * (v_target - med) / mad
        if abs(z) > robust_k:
            out.append(PeerOutlier(t, v_target, z, len(peers)))
    return out
```

**Severity scoring**

```python
def severity(event, ctx):
    base = DETECTOR_BASE_SEVERITY[event.detector]
    if ctx.tag_role == 'critical_kpi':       base = max(1, base - 1)
    if event.duration_minutes > 240:         base = max(1, base - 1)
    if ctx.suppressed:                       return 4   # info-only
    if ctx.feedback_history.false_positive_rate > 0.5:
        base = min(4, base + 1)
    return base
```

## 10. Edge Cases

- **Sparse / event-driven tags**: don't apply gap detection unless an expected event rate is set; otherwise frozen detection on event tags is also misleading.
- **Calibrated zero**: A tag legitimately at zero (e.g., inverter at night) is not "frozen"; require context (POA > threshold) before flagging.
- **Mode-aware**: Plant in shutdown vs running — different baselines per mode; encode mode tag.
- **Operator-initiated changes**: Manual setpoint changes can look anomalous; suppress when operator-action tag changes.
- **Daylight savings**: Avoid spurious clock-drift alerts at DST transitions.
- **Backfill jitter**: Backfilled batch loads can produce out-of-order timestamps; whitelist known backfill jobs.
- **Cold-start**: For new tags, rely on rule + statistical layers until ML has 14+ days of training data.
- **Concept drift**: Periodic model retraining (weekly); detect distribution shift to trigger early retrain.

## 11. Ignition-Specific Integration

- An **Ignition module** (scope GD) provides:
  - Designer panel "Anomaly Inbox" — review, ack, mute.
  - Perspective component "Tag Health Card" — embed on equipment views to show recent anomaly count and current quality.
  - Gateway scripted task that periodically writes per-tag quality flags back to companion tags (`<tag>/Quality_Flag`) so they can be alarmed (Spec 3) or used in expressions.
  - Link from Ignition alarm to anomaly drill-down (open inbox filtered to that tag).
- For Ignition Tag Historian, use the gateway query API (`system.tag.queryTagHistory`) for backfill reads; for live, subscribe via OPC UA companion publishing.
- Renewables-specific: include a clear-sky overlay component in Perspective (driven by solar position library) so operators visually see why irradiance was flagged.

## 12. Test Plan

- **Synthetic dataset**: generate time-series with injected anomalies (gaps, frozen, outliers, clock drift) — measure precision/recall per detector.
- **Real-data benchmark**: 10 historical incidents from customer sites, labeled; compute end-to-end recall and time-to-detect.
- **False-positive tracking**: per tenant per week dashboards; CI alert if FPR rises above target.
- **Backfill correctness**: Run backfill on a known dataset; compare against ground truth.
- **Performance**: 100k tags, 1-min detection latency, sustain for 24h continuous on commodity hardware.
- **A/B model tests**: Shadow-run new model versions against production for 14 days; compare metrics.

## 13. Phased Rollout

| Phase | Duration | Scope |
|---|---|---|
| 0 — MVP | 6 weeks | Layer 1 + 2 (rules, stats), Postgres event store, basic UI, Ignition reader |
| 1 — ML | 8 weeks | Layer 3 (IF, autoencoder), per-tag baselines, automated retraining |
| 2 — Fleet | 4 weeks | Layer 4 peer comparison, fleet quality scores |
| 3 — Renewables packs | 6 weeks | PV (clear-sky, soiling), wind (power curve), BESS (SoC/SoH) |
| 4 — Multi-historian | 8 weeks | PI / Canary / Influx / Timescale readers |
| 5 — Feedback loop | 4 weeks | Operator feedback, FPR auto-tuning |
| 6 — Backfill | 6 weeks | Historical scoring, daily quality reports |

## 14. Success Metrics

- Time-to-detect data quality issues: from > 24 hours (often a downstream report) to < 15 minutes.
- False-positive rate after 60-day tuning: < 5%.
- Recall on labeled benchmark: ≥ 90%.
- % of historian-driven analytics using the quality API to mask suspect data: ≥ 50% of pipelines within 12 months.
- MWh recovered per year via faster sensor/comm fault detection (renewables): tracked per site, target ≥ 0.2% of generation.
