---
title: AI Material Selector
emoji: ⚙️
colorFrom: blue
colorTo: indigo
sdk: streamlit
sdk_version: 1.41.0
app_file: app.py
pinned: false
license: mit
---

# ⚙️ AI Material Selector

**AI Material Selector** is a tactical, engineering-focused Streamlit application that leverages the Google Gemini AI engine to help engineers, designers, and manufacturers find the optimal materials for their projects based on physical constraints, cost limits, and natural language requirements.

---

## 🚀 Features

- **Dual Modes (Lite & Advanced):**
  - **Lite Mode:** A stripped-down, distraction-free interface that instantly returns the single best material recommendation based on a prompt.
  - **Advanced Mode:** A full-featured tactical dashboard with engineering constraint sliders, multi-material comparisons, interactive data matrices, and chat-based follow-ups.
- **AI-Powered Recommendations:** Powered by Google Gemini. The engine cross-references your natural language constraints (e.g., "I need a lightweight, high-yield material for a drone frame") with a localized database of materials, and returns a ranked, reasoned recommendation with a self-reported confidence score.
- **Dynamic Cost Engine:** Estimates material costs using historical CSV data, AI market estimations, or Live MetalPrice API fetching. Calculates final part costs based on target volume and density, with full Metric/Imperial unit conversion.
- **CAD Studio:** Generate a parametric specimen (cube always available; custom L×W×H with the optional `cadquery` geometry engine) or upload your own STEP file, embed the selected material's properties directly into the CAD metadata, preview it in an in-browser 3D viewer, and export a STEP/STL file ready for SolidWorks, FreeCAD, ANSYS, or SpaceClaim.
- **Search History & Custom Templates:** Save and revisit past searches, or save frequently used engineering prompts as reusable templates — both private to your own browser session (see **Privacy & Security** below).
- **Interactive Telemetry (Charts):** Radar charts, scatter plots, and property heatmaps built with Plotly to visually compare yield strength, density, cost, and machinability.
- **PDF Dossier Exports:** Instantly generate and download professional PDF reports for recommended materials, including engineering reasoning and cost breakdowns.
- **Premium Enterprise SaaS UI:** Built with a clean, modern dark-theme design using Inter typography and a consistent design-token system.

## 🔒 Privacy & Security

This app serves every visitor from one shared server process — a common source of accidental cross-user data leaks in Streamlit apps if state isn't handled deliberately. This project treats that as a first-class design constraint, not an afterthought:

- **Nothing is written to shared server-side files.** Your API key, filters, search history, and custom templates all live in Streamlit's per-session state (`st.session_state`) — private to your own browser session, never visible to other visitors, and never persisted on the server's disk.
- **API keys are validated, not just accepted.** The sidebar status only ever shows "Connected" after Google's own API confirms the key actually authenticates — not just because *something* was typed into the box.
- **AI-generated and error text is sanitized before rendering**, closing a real cross-site-scripting (XSS) class of vulnerability that indirect prompt injection can otherwise open in LLM-backed apps.
- **CSV import is sanitized against spreadsheet formula injection**, so an imported history file can't smuggle in a live formula that executes later when re-exported and opened in Excel/Sheets.

These weren't theoretical hardening exercises — each one started as a real bug found through live testing and was fixed and verified end-to-end. See `TECHNICAL_PAPER_AND_RELEASE_NOTES.md` for the full history.

## 🛠️ Tech Stack
- **Frontend / Framework:** Streamlit
- **AI / LLM:** Google `google-genai` (Gemini Flash & Pro)
- **Data Processing:** Pandas
- **Data Visualization:** Plotly
- **PDF Generation:** FPDF2
- **Spreadsheet Export:** openpyxl
- **Secrets Management:** python-dotenv (local `.env`, never committed)
- **CAD / Geometry:** Dependency-free ISO-10303-21 (STEP) generation and property injection by default; optional `cadquery` geometry engine for non-cube dimensions and full mesh tessellation

## 📦 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/sanjaybp02/AI-material-selector.git
   cd AI-material-selector
   ```

2. **Install dependencies:**
   Make sure you have Python 3.8+ installed.
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   streamlit run app.py
   ```

4. **Authentication:**
   Enter your **Google Gemini API Key** in the left sidebar to activate the AI engine (get one free at [Google AI Studio](https://aistudio.google.com/)). For local development, you can instead set `GEMINI_API_KEY` in a `.env` file (already gitignored) so it's pre-filled automatically.

5. **Optional: enable full CAD Studio geometry.**
   CAD Studio always works out of the box for cube specimens and STEP property injection. To unlock custom L×W×H box dimensions and true mesh tessellation for uploaded files, install the optional geometry engine:
   ```bash
   pip install cadquery
   ```
   No app configuration is needed — `cadquery_available()` detects it automatically and enables the extra options.

## 📁 Project Architecture
- `app.py`: Main application entry point and UI orchestrator.
- `modules/ai_engine.py`: Handles interactions with Google Gemini — prompt structuring, chat history, retry/fallback across model versions, and live API-key validation.
- `modules/cost_engine.py`: Calculates material part costs based on density, volume, and APIs.
- `modules/data_loader.py`: Ingests and processes the `materials.csv` database, handling metric/imperial unit conversions.
- `modules/filters.py`: Renders the dynamic slider constraints (Yield Strength, Density, Temperature, and more), clamped to the dataset's valid range.
- `modules/charts.py`: Plotly visualization engine.
- `modules/pdf_report.py`: FPDF2 generator for downloadable engineering dossiers.
- `modules/cad_engine.py`: CAD Studio orchestration — generates parametric specimens or ingests uploaded STEP files, applies material properties, builds the 3D preview mesh, and exports STEP/STL.
- `modules/cad_export.py`: Low-level STEP (ISO-10303-21) file generation and format-agnostic material-property injection.
- `modules/history.py`: Search history — save, edit, import/export as CSV/Excel. Private per browser session (`st.session_state`), never written to a server file.
- `modules/templates.py`: Custom prompt templates. Private per browser session (`st.session_state`), never written to a server file.
- `modules/ui.py`: Shared design system, theming, and reusable presentation components (including the CAD Studio 3D viewer).

---
*made with ❤️ by sanjay bp*
