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
- **AI-Powered Recommendations:** Powered by Google Gemini. The engine cross-references your natural language constraints (e.g., "I need a lightweight, high-yield material for a drone frame") with a localized database of materials.
- **Dynamic Cost Engine:** Estimates material costs using historical CSV data, AI market estimations, or Live MetalPrice API fetching. Calculates final part costs based on target volume and density.
- **Premium Enterprise SaaS UI:** Built with a clean, modern SaaS design using Inter typography, subtle grey borders, and a visually matched side panel.
- **PDF Dossier Exports:** Instantly generate and download professional PDF reports for recommended materials, including engineering reasoning and cost breakdowns.
- **Interactive Telemetry (Charts):** Radar charts, scatter plots, and property heatmaps built with Plotly to visually compare yield strength, density, cost, and machinability.
- **Custom Template Vectors:** Save frequently used engineering prompts into the local database for rapid reuse.

## 🛠️ Tech Stack
- **Frontend / Framework:** Streamlit
- **AI / LLM:** Google `google-genai` (Gemini Flash & Pro)
- **Data Processing:** Pandas
- **Data Visualization:** Plotly
- **PDF Generation:** FPDF2

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
   Upon launching, enter your **Google Gemini API Key** in the left sidebar to activate the AI engine.

## 📁 Project Architecture
- `app.py`: Main application entry point and UI orchestrator.
- `modules/ai_engine.py`: Handles interactions with Google Gemini, including prompt structuring and chat history.
- `modules/cost_engine.py`: Calculates material part costs based on density, volume, and APIs.
- `modules/data_loader.py`: Ingests and processes the `materials.csv` database, handling metric/imperial unit conversions.
- `modules/filters.py`: Renders the dynamic slider constraints for Yield Strength, Density, and Temperature.
- `modules/charts.py`: Plotly visualization engine.
- `modules/pdf_report.py`: FPDF2 generator for downloadable engineering dossiers.
- `modules/templates.py`: Manages the reading and writing of `templates.json` for custom prompts.

---
*made with ❤️ by sanjay bp*
