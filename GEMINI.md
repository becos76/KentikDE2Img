# KentikDE2Img - Project Context

A specialized Streamlit-based web application designed to interface with the Kentik TopXChart API. It allows users to paste Kentik Data Explorer (DE) JSON queries, preview the resulting charts in multiple formats, and download them.

## 🚀 Project Overview

- **Core Purpose**: Simplifies the process of exporting Kentik Data Explorer time-series charts into SVG, PNG, and PDF formats.
- **Architecture**: Single-pane Python application using Streamlit for the UI and `httpx` for asynchronous communication with Kentik's API.
- **Key Features**:
    - Dual-pane layout (JSON Editor vs. Live Preview).
    - Professional JSON editor with syntax highlighting (`streamlit-ace`).
    - Automatic payload wrapping (wraps raw query lists into the required Kentik API structure).
    - Multi-region support (US/EU Kentik clusters).
    - Credentials management via `.env` or sidebar UI.

## 🛠 Tech Stack

- **Language**: Python 3.11
- **UI Framework**: Streamlit
- **API Client**: `httpx` (Asynchronous)
- **Editor Component**: `streamlit-ace`
- **Environment Management**: `python-dotenv`
- **Containerization**: Docker & Docker Compose

## 🏃 Building and Running

### Local Development
1. **Setup Environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Or .venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```
2. **Configuration**:
   Copy `.env.example` to `.env` and fill in your Kentik credentials.
3. **Run App**:
   ```bash
   streamlit run app.py
   ```

### Docker Deployment
The app is configured to run on port **8080** by default.
```bash
docker-compose up --build
```

## 📝 Development Conventions

- **State Management**: Uses `st.session_state` to persist JSON input and API responses (images/PDFs) across re-runs.
- **API Handling**: Logic is encapsulated in `fetch_kentik_image`. It handles `dataUri` responses from Kentik and decodes them for display.
- **UI Logic**:
    - The JSON editor height is user-adjustable via a sidebar slider.
    - Buttons at the top of the editor pane trigger specific API actions (SVG, PNG, PDF).
    - SVG rendering is handled via `st.markdown` with raw HTML to bypass PIL limitations.

## 📂 Key Files

- `app.py`: The main application entry point containing all UI and API logic.
- `requirements.txt`: List of Python dependencies.
- `Dockerfile` / `docker-compose.yml`: Containerization configuration.
- `.env.example`: Template for required Kentik authentication variables.
