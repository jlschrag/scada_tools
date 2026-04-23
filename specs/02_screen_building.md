# Spec 2 — Screen Building from CAD Drawings or Pictures

## 1. Problem Statement

Building HMI/SCADA screens is one of the most time-consuming tasks in commissioning. A 100-MW solar plant has dozens of single-line diagrams, P&IDs, and mechanical layouts; engineers manually redraw every breaker, transformer, inverter, and combiner box in the SCADA, then bind each graphic to a tag. This work is repetitive, error-prone, and adds weeks to project schedules. A tool that ingests a CAD drawing (DWG/DXF), a P&ID PDF, or even a photograph of a sketched SLD, recognizes the symbols and topology, and generates a SCADA screen with tag bindings already in place would compress weeks of work into hours.

## 2. User Personas & Stories

**SCADA Application Engineer** — *"As a SCADA engineer, I want to drop a DXF of the plant SLD into a tool and get an Ignition Perspective view back with breakers, transformers, and inverters already drawn and bound to my tag database."*

**Project Engineer** — *"As a project engineer, I want to send my P&ID PDFs and have the SCADA screens auto-generated, so I don't have to maintain two parallel sets of drawings."*

**Retrofit/Brownfield Engineer** — *"As a brownfield engineer at a 30-year-old plant with no electronic drawings, I want to take a phone photo of the panel SLD and get a working SCADA screen."*

## 3. Functional Requirements

- **F1**: Ingest formats: DWG (AutoCAD R14 through 2024), DXF (R12 through 2018), PDF (vector-preferred, raster fallback), PNG/JPG/HEIC (photographs and scans), SVG, SLDPRT exports, Visio (.vsdx), Bentley MicroStation (.dgn).
- **F2**: Detect and classify electrical and process symbols using a configurable symbol library: breakers (drawout, fixed), disconnects, transformers (2W, 3W, auto), inverters, combiner boxes, trackers, BESS racks, motors, pumps, valves (gate, ball, butterfly, check), instruments (per ISA 5.1 bubble), tanks, vessels, heat exchangers.
- **F3**: Detect topology — line connections between symbols, with electrical bus identification (medium-voltage, low-voltage, AC vs DC) and process flow direction.
- **F4**: OCR all text labels (equipment tags, ratings, setpoints) using a model fine-tuned on engineering drawing fonts.
- **F5**: Match detected equipment to existing tag database (Spec 6) by tag name; suggest matches when fuzzy.
- **F6**: Generate output as: Ignition Perspective JSON view, Ignition Vision XML window, AVEVA InTouch graphic, generic SVG with metadata, and an editable intermediate format for manual touch-up.
- **F7**: Provide a review/edit web UI where the user accepts/rejects each detected symbol, drags to fix positions, and merges duplicates.
- **F8**: Iterative learning — corrections in the UI are captured as training data for site-specific symbol library improvements.
- **F9**: Maintain bidirectional traceability: each generated screen element links back to the source drawing element (page, layer, handle for DXF, bbox for raster).
- **F10**: Support custom symbol libraries — customers can upload their corporate symbol set as SVG + classification metadata.
- **F11**: Generate not just static graphics but interactive elements: popups for breaker open/close, faceplates for analog values, alarm indication overlays, animations bound to tag values.

## 4. Non-Functional Requirements

- **N1 Accuracy**: ≥ 95% symbol detection precision/recall on vector inputs (DXF/SVG/vector PDF) for standard ANSI/IEC libraries; ≥ 80% on hand-drawn raster.
- **N2 Throughput**: 1 standard SLD page processed in < 60 seconds on a single GPU.
- **N3 Footprint**: Inference can run on a workstation (16 GB GPU); cloud GPU offload optional.
- **N4 Privacy**: Drawings often contain confidential plant data; on-premises deployment supported, no telemetry of drawing content.
- **N5 Reproducibility**: Same input drawing always produces the same screen output for a given tool version.

## 5. System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    Web UI (React + Konva)                    │
│  Upload | Review symbols | Edit | Export | Train             │
└──────────────────────────────────────────────────────────────┘
                          │ REST + WebSocket
┌─────────────────────────▼────────────────────────────────────┐
│                  Orchestration API (Python)                  │
└─────┬───────────────┬────────────────┬───────────────┬──────┘
      │               │                │               │
┌─────▼─────┐  ┌──────▼──────┐  ┌─────▼─────┐  ┌──────▼──────┐
│ Vector    │  │ Raster      │  │ Symbol    │  │ Topology    │
│ ingest    │  │ ingest      │  │ classifier│  │ extractor   │
│ (libdxf,  │  │ (PDF→img,   │  │ (YOLO +   │  │ (graph      │
│  pdf2svg) │  │  upscale)   │  │  ResNet)  │  │  builder)   │
└─────┬─────┘  └──────┬──────┘  └─────┬─────┘  └──────┬──────┘
      │               │                │               │
      └───────────────┴────────┬───────┴───────────────┘
                               │
                    ┌──────────▼──────────┐
                    │ Intermediate Model  │   (canonical JSON
                    │ (DrawingGraph)      │    described below)
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │ Tag binder          │   (queries tag DB,
                    │ (fuzzy match,       │    Spec 6)
                    │  user-confirm)      │
                    └──────────┬──────────┘
                               │
   ┌───────────────────────────┼───────────────────────────┐
   ▼                           ▼                           ▼
┌─────────┐            ┌──────────────┐           ┌────────────┐
│ Ignition│            │ Vision XML   │           │ Generic    │
│ Perspect.│           │ exporter     │           │ SVG+meta   │
│ JSON    │            │              │           │            │
└─────────┘            └──────────────┘           └────────────┘
```

## 6. Data Models

### Canonical DrawingGraph (intermediate, JSON Schema excerpt)

```json
{
  "drawing": {
    "id": "uuid",
    "source": { "type": "dxf", "filename": "PLT-001-SLD.dxf", "sha256": "..." },
    "units": "mm",
    "bounds": { "minX": 0, "minY": 0, "maxX": 1189, "maxY": 841 },
    "pages": [{
      "index": 1,
      "symbols": [
        {
          "id": "sym-0001",
          "class": "circuit_breaker",
          "subclass": "drawout_lv",
          "position": { "x": 320.5, "y": 410.0 },
          "rotation": 0,
          "scale": 1.0,
          "bbox": { "x": 310, "y": 400, "w": 20, "h": 20 },
          "confidence": 0.97,
          "labels": [
            { "text": "52-A1", "role": "tag", "confidence": 0.98 },
            { "text": "1200A", "role": "rating",  "confidence": 0.91 }
          ],
          "ports": [
            { "id": "top", "x": 320.5, "y": 400 },
            { "id": "bottom", "x": 320.5, "y": 420 }
          ],
          "source_handle": "0x7A3F"
        }
      ],
      "connections": [
        {
          "id": "net-0001",
          "type": "electrical",
          "voltage_class": "MV",
          "endpoints": [
            { "symbol": "sym-0001", "port": "bottom" },
            { "symbol": "sym-0007", "port": "top" }
          ],
          "polyline": [[320.5, 420], [320.5, 480], [400, 480]]
        }
      ]
    }]
  }
}
```

### Symbol library entry

```yaml
symbol:
  id: ansi_breaker_drawout_lv
  display_name: Drawout LV Breaker (ANSI)
  class: circuit_breaker
  subclass: drawout_lv
  geometry_svg: <svg>...</svg>
  ports:
    - id: top
      x: 0
      y: -10
    - id: bottom
      x: 0
      y: 10
  default_bindings:
    - role: state
      tag_pattern: "{tag}/Status"
    - role: trip
      tag_pattern: "{tag}/Trip"
  faceplate: ansi_breaker_faceplate.json
```

## 7. API Contracts

```
POST   /api/v1/drawings                      # multipart upload
GET    /api/v1/drawings/{id}
GET    /api/v1/drawings/{id}/graph           # DrawingGraph JSON
POST   /api/v1/drawings/{id}/symbols/{sid}   # accept/edit/reject
POST   /api/v1/drawings/{id}/bind            # body: tag binding overrides
POST   /api/v1/drawings/{id}/export
        ?format=ignition_perspective|ignition_vision|svg|aveva
GET    /api/v1/symbol-library
POST   /api/v1/symbol-library/symbols        # upload custom symbol
POST   /api/v1/training/feedback             # capture user corrections
WS     /api/v1/drawings/{id}/events          # stream during processing
```

## 8. Tech Stack

- **Vector ingest**: ezdxf (Python) for DXF; pdfplumber + pikepdf for vector PDF; cairosvg for SVG normalization.
- **Raster ingest**: pdf2image, PIL, Real-ESRGAN for upscaling low-res scans, OpenCV for preprocessing (deskew, denoise, binarize).
- **Symbol detection**: YOLOv8 / YOLO-NAS for bounding-box detection, then a ResNet-50 fine-tune for symbol classification. Use Detectron2 for instance segmentation when symbols overlap.
- **OCR**: PaddleOCR or TrOCR fine-tuned on engineering-drawing text. RapidOCR for Windows-friendly deployment.
- **Topology**: NetworkX for graph operations; Hough transform + custom line-tracing for raster connections.
- **Backend**: Python 3.11 + FastAPI, Celery for async jobs, Redis for queue, MinIO/S3 for artifacts.
- **Frontend**: React 18 + Konva.js (canvas editor), TanStack Query, shadcn/ui.
- **Training**: PyTorch Lightning, Weights & Biases, automated dataset versioning with DVC.
- **Deployment**: Docker, GPU node pool in Kubernetes; CPU-only fallback for vector-only workflows.

## 9. Key Algorithms / Pseudocode

**End-to-end pipeline**

```python
def process_drawing(file: UploadedFile) -> DrawingGraph:
    raw = ingest(file)                       # → vector entities or raster image
    normalized = normalize(raw)              # uniform units, layers cleaned
    symbol_candidates = detect_symbols(normalized)
    symbols = classify(symbol_candidates)    # add subclass + confidence
    text_blocks = ocr(normalized)
    symbols = associate_labels(symbols, text_blocks)  # nearest-neighbor + heuristics
    lines = extract_lines(normalized)
    connections = trace_topology(symbols, lines)
    voltage_classes = infer_voltage_class(connections, symbols)
    return DrawingGraph(symbols, connections, voltage_classes)
```

**Tag binding (fuzzy match against Spec 6 tag DB)**

```python
def bind_tags(graph: DrawingGraph, tag_db: TagDB) -> DrawingGraph:
    for sym in graph.symbols:
        if sym.labels.get("tag"):
            candidates = tag_db.search(sym.labels["tag"], limit=5,
                                       fuzz_threshold=0.85)
            sym.binding = candidates[0] if candidates and candidates[0].score > 0.95 \
                          else PendingBinding(candidates=candidates)
    return graph
```

**Ignition Perspective view generation** — Perspective views are JSON; we emit a tree of `ia.display.svg` and `ia.shapes.*` components with `props.style` for color and `props.binding` for tag binding.

```python
def to_perspective(graph: DrawingGraph, project: str) -> dict:
    root = {"type": "ia.container.coord",
            "version": 0,
            "props": {"viewport": {"w": graph.bounds.w, "h": graph.bounds.h}},
            "children": []}
    for sym in graph.symbols:
        sym_def = library.get(sym.class_)
        comp = sym_def.to_perspective_component(sym)
        if sym.binding and sym.binding.is_resolved():
            comp["propConfig"] = {
                "props.value": {"binding": {"type": "tag",
                                            "config": {"tagPath": sym.binding.path}}}
            }
        root["children"].append(comp)
    for conn in graph.connections:
        root["children"].append(connection_to_polyline(conn))
    return root
```

## 10. Edge Cases

- **Mixed standards**: A drawing with both ANSI and IEC symbols on the same page — symbol classifier must be ANSI/IEC-aware and label each. Provide auto-conversion.
- **Multi-sheet drawings**: Off-sheet connectors (`A1 → sheet 3`) must be resolved; build a cross-sheet graph.
- **Rotated / mirrored symbols**: Detector and symbol library need rotation-invariant matching; store rotation in canonical model so renderers can re-rotate as needed.
- **Hand-drawn sketches**: ≥ 70% target accuracy; surface low-confidence symbols prominently in the review UI; never silently auto-accept low-confidence detections.
- **Layered DXFs**: Many CAD drawings have layers like "ANNOTATION," "TITLE_BLOCK" that should be excluded; provide layer filtering UI and presets per company standard.
- **Coordinate system flips**: DXF uses Y-up, screen coords are Y-down; flip exactly once.
- **Unit ambiguity**: DXF has unitless mode; provide a unit-detection heuristic (compare title block size to page size) and a manual override.
- **Title block / legend pollution**: Detect and exclude title blocks via OCR + bounding-box heuristics.

## 11. Ignition-Specific Integration

- Output Perspective views are written to `<project>/com.inductiveautomation.perspective/views/<view-path>/view.json` with companion `resource.json` and `thumbnail.png`.
- Output Vision windows are .vwin XML written to `<project>/com.inductiveautomation.vision/windows/<window>/window.xml`.
- An **Ignition module** with scope `D` (designer) adds a "Import Drawing" menu under Tools → Drawing Importer; opens a dialog that uploads to the screen-builder service and, when complete, calls the Designer API to write the resulting view files into the open project, then refreshes the project tree.
- Tag bindings use Ignition's tag path syntax — `[default]Plant/Inverter01/AC_Power`. The binder reads tag-provider names from Ignition's GatewayContext and uses the active project's default provider unless overridden.
- For brownfield SCADA migrations, support import of existing Vision windows so the AI symbol classifier can learn the customer's house style.

## 12. Test Plan

- **Dataset**: Curate a held-out test set of 200 representative drawings (vector and raster, ANSI and IEC, SLDs and P&IDs); track precision/recall per symbol class over time.
- **Golden output**: For 30 reference drawings, maintain hand-edited "perfect" Perspective views; CI compares structural diff (symbol count, class distribution, connection count) between generator output and golden.
- **User studies**: Time-to-screen for 5 SCADA engineers building the same plant from a DXF, with vs. without the tool; target ≥ 5× speedup.
- **Round-trip**: Export Perspective → screenshot → re-ingest as raster → expect ≥ 90% symbol recovery (sanity check on output fidelity).

## 13. Phased Rollout

| Phase | Duration | Scope |
|---|---|---|
| 0 — MVP | 10 weeks | DXF + vector PDF ingest, ANSI electrical SLD symbols only, SVG export, web review UI |
| 1 — Ignition export | 6 weeks | Perspective view generator, Ignition Designer module (import), tag-binding |
| 2 — IEC + P&ID | 8 weeks | IEC symbol library, P&ID symbols (ISA 5.1 instruments, valves), Vision export |
| 3 — Raster + photo | 12 weeks | Raster pipeline, hand-drawn support, training feedback loop |
| 4 — Brownfield/AVEVA | 8 weeks | InTouch / System Platform exporters, custom symbol libraries |
| 5 — Continuous | ongoing | model improvement, customer-specific symbol training |

## 14. Success Metrics

- Time to build a 10-page SLD-driven SCADA: from 80 hours to < 8 hours.
- Symbol detection precision ≥ 0.95 / recall ≥ 0.92 on vector benchmark; ≥ 0.85 / 0.80 on raster.
- User review time per page: < 5 minutes after first month of use.
- % of symbols accepted without edit: ≥ 90% target.
- NPS from project engineering teams ≥ 40 within 12 months.
