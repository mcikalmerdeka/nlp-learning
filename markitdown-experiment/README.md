# MarkItDown Experiment

A Jupyter notebook playground for converting documents and images into Markdown with [Microsoft MarkItDown](https://github.com/microsoft/markitdown) — including two LLM-powered routes for visual content:

1. **Built-in LLM image support** — descriptions / transcriptions for standalone image files and images inside PPTX (`llm_client` / `llm_model` on the converter).
2. **`markitdown-ocr` plugin** — OCR for images *embedded* in `pdf / docx / pptx / xlsx` via `MarkItDown(enable_plugins=True, ...)`.

Every LLM call runs with the multimodal model `gpt-6-luna` at `reasoning_effort="none"` (fast and cheap); text-based formats never touch the API.

> Last verified: October 2026 — `markitdown 0.1.8`, `markitdown-ocr 0.1.1`, `openai 3.29.0`, Python 3.14.3.

## Project layout

```
markitdown-experiment/
├── notebook.ipynb          # all experiments
├── pyproject.toml          # uv-managed dependencies
├── uv.lock
├── .env                    # gitignored - holds OPENAI_API_KEY
├── data/
│   ├── doc/                # Word article (docx, no embedded images)
│   ├── images/             # text image, document-like pages, scanned pages (JP)
│   ├── pdfs/               # slide-export PDF, tech report, financial statement, table PDFs
│   ├── powerpoints/        # Gamma-generated deck (pptx)
│   └── spreadsheets/       # data table (xlsx)
└── out/                    # generated markdown + rendered pages (gitignored)
```

## Setup

Requires [uv](https://docs.astral.sh/uv/) and an OpenAI account with a vision-capable model.

```bash
uv sync --all-groups
```

Create a `.env` next to the notebook (never committed — see `.gitignore`):

```
OPENAI_API_KEY=sk-...
# optional: override the multimodal model (default: gpt-6-luna)
OPENAI_MODEL=gpt-6.1-sol
```

Then open `notebook.ipynb` and select the `.venv` kernel (ipykernel is included as a dev dependency).

## Dependencies

| Package | Why |
|---|---|
| `markitdown[docx,pdf,pptx,xlsx] 0.1.8` | core converters (pinned `<0.2.0` by the plugin) |
| `markitdown-ocr 0.1.1` | OCR-enhanced pdf/docx/pptx/xlsx converters |
| `openai` | SDK for the vision calls |
| `python-dotenv` | loads `OPENAI_API_KEY` from `.env` |
| `pymupdf` | renders scanned-PDF pages to PNG |
| `ipykernel` (dev) | notebook kernel for the `.venv` |

## The three converters

The notebook's setup cell builds all three from one client:

```python
client = OpenAI(api_key=api_key, max_retries=3)

md_plain = MarkItDown()                    # text/metadata only, no API calls
md_llm = MarkItDown(llm_client=llm_client, llm_model=MODEL)
md_ocr = MarkItDown(                       # plugin converters register ahead of the built-ins
    enable_plugins=True,
    llm_client=llm_client,
    llm_model=MODEL,
    llm_prompt=OCR_PROMPT,
)
```

`llm_client` is a `ReasoningNoneClient` — a small wrapper that injects
`extra_body={"reasoning_effort": "none"}` into every `chat.completions.create()` call.
MarkItDown and the plugin both call the client through
`llm_client.chat.completions.create(...)`, which the wrapper hooks, so the effort setting
applies automatically. (MarkItDown does not expose `reasoning_effort` natively.)

One shared prompt drives transcription everywhere:

```python
OCR_PROMPT = (
    "Transcribe ALL text visible in this image into clean Markdown. "
    "Preserve headings with # markers, lists with -, and reproduce tables as "
    "GitHub-style Markdown tables. Keep the original language. Return only the Markdown."
)
```

## Notebook tour

| Section | What it does | API cost |
|---|---|---|
| Setup | dotenv, client, effort wrapper, 3 converters, `OCR_PROMPT`, helpers (`convert_and_show`) | — |
| **Doc** | plain docx conversion; plugin cell behind `RUN_DOC_PLUGIN_OCR = False` | 0 (current file has no images) |
| **Image** | plain (metadata-only → near-empty without exiftool) then LLM transcription of `sample_text.jpg`, `sample_image_1.png`, `page_2.png` | 3 calls |
| **PDFs** | all six PDFs through the text-layer converter; close look at `long_table_pdf.pdf` | 0 |
| **Scanned PDF** | PyMuPDF renders each page at 150 DPI → direct vision calls (`vision_to_markdown`) → stitched document | 8 calls |
| PDF plugin | `md_ocr` on the slide-export PDF (**runs by default**) | ~14 calls |
| **PPT** | plain deck conversion; optional `RUN_PPTX_LLM = False` alt-text cell | 0 / opt-in |
| PPT plugin | deck OCR behind `RUN_PPTX_PLUGIN_OCR = False` | ~30 calls (opt-in) |
| **Excel** | plain xlsx → pipe tables + raw view; plugin cell behind `RUN_XLSX_PLUGIN_OCR = False` | 0 (no images yet) |
| Recap | auto-built table (source / converter kind / markdown chars) from `SUMMARY` | — |

Full outputs are written to `out/*.md`; page renders land in `out/scan_pages/`. Cells show a truncated preview and note how many more characters live on disk.

## Data inventory (verified)

| File | Notes | Unique embedded images |
|---|---|---|
| `doc/multi_agent_workflows_ai_article.docx` | 9,108 chars plain | 0 |
| `images/sample_text.jpg` | typed-text image ("The quick brown fox…") | — |
| `images/sample_image_1..4.png` | document-like pages (header/table/figure/checklist) | — |
| `images/page_2/6/9.png` | scanned pages of a Japanese engineering document | — |
| `images/long_table_image.jpg` | dense table image | — |
| `pdfs/sustainable_urban_mobility_trends_2025.pdf` | Gamma slide export, most image-heavy (pseudo-scanned target) | 14 |
| `pdfs/docling_technical_report.pdf` | figures + dense text | 30 |
| `pdfs/FinancialStatement-2025-III-BBRI.pdf` | 34-page financial statement | 0 |
| `pdfs/long_table_pdf.pdf`, `pdfs/pdf_with_tables_example.pdf` | table extraction targets | 0 |
| `powerpoints/sustainable_urban_mobility_trends_2025.pptx` | 8 slides, repeated media (deduped by the plugin) | 30 |
| `spreadsheets/example_table.xlsx` | 21,071 chars plain | 0 |

> All demo PDFs have an extractable text layer (checked with pdfminer and PyMuPDF) — none is truly scanned, so the scanned-PDF pipeline is demoed on the image-heavy slide export. The same code path works for real scans unchanged.

## What we verified (October 2026)

| Check | Result |
|---|---|
| Plain conversions (docx / pptx / xlsx / pdf) | ✅ 9,108 / 4,228 / 21,071 / 3,389 chars |
| Plain image conversion without exiftool | ✅ 0 chars (metadata-only limit — hence the LLM route) |
| Page rendering (`pymupdf`, 150 DPI) | ✅ 8 pages |
| `gpt-6-luna` accepts `reasoning_effort="none"` | ✅ (via `extra_body`) |
| Direct vision transcription | ✅ exact text recovered from `sample_text.jpg` |
| markitdown LLM path (wrapped client) | ✅ output under a `# Description:` heading |
| Plugin discovery / registration | ✅ `ocr → markitdown_ocr`; 4 `*WithOCR` converters ahead of built-ins |
| Plugin fallback (0-image docx/xlsx) | ✅ identical to plain output, zero calls |

## Output formats to expect

- **Built-in LLM images** (`md_llm`): metadata + `# Description:` + the model's Markdown.
- **Plugin OCR** (`md_ocr`): text inserted inline as `*[Image OCR] … [End OCR]*` blocks.
  - PDF: images OCR'd inline in reading order; text-free auto-fall back to a 300 DPI full-page render; malformed PDFs retried with PyMuPDF.
  - PPTX: picture shapes, placeholders, and grouped images; description-first, OCR as fallback.
  - XLSX: images listed under `### Images in this sheet:` after each sheet's table; legacy `.xls` untouched.
  - DOCX: fragments inserted at the image position inside paragraphs/table cells.
- Repeated image bytes are recognized **once per conversion** (cache is per-call, not shared).

## Cost guide

A full top-to-bottom run spends ≈ **25 vision calls** (3 image + 8 scanned pages + 14 PDF-plugin). The doc/xlsx/pptx plugin cells stay behind flags — flip them when you drop in image-bearing file versions. Previews are intentionally short; the full markdown is always saved to `out/`.

## References

- [MarkItDown](https://github.com/microsoft/markitdown) — usage, plugins, `llm_client`/`llm_model` pattern
- [`markitdown-ocr` README](https://github.com/microsoft/markitdown/blob/main/packages/markitdown-ocr/README.md) — plugin contract, OCR insertion formats
- [OpenAI vision docs](https://platform.openai.com/docs/guides/images-vision) — `image_url` message shape, `reasoning_effort`
