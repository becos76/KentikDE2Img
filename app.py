import streamlit as st
import httpx
import os
import json
import base64
from dotenv import load_dotenv
from streamlit_ace import st_ace

# Load credentials from .env
load_dotenv()

# App Layout
st.set_page_config(layout="wide")
st.title("KentikDE2Img: Kentik Data Explorer Chart to Image")

# Configuration
KENTIK_EMAIL = os.getenv("KENTIK_EMAIL")
KENTIK_TOKEN = os.getenv("KENTIK_TOKEN")
KENTIK_REGION = os.getenv("KENTIK_REGION", "US").upper()

# Sidebar for credentials if they aren't in .env
with st.sidebar:
    st.header("Configuration")
    if not KENTIK_EMAIL or not KENTIK_TOKEN:
        st.warning("Credentials not found in .env. Please provide them here.")
        KENTIK_EMAIL = st.text_input("Kentik Auth Email", value=KENTIK_EMAIL or "")
        KENTIK_TOKEN = st.text_input("Kentik API Token", type="password", value=KENTIK_TOKEN or "")
    
    # Region Selection
    KENTIK_REGION = st.selectbox("Kentik Region", options=["US", "EU"], index=0 if KENTIK_REGION == "US" else 1)
    
    # Map region to URL
    KENTIK_CLUSTER = "api.kentik.com" if KENTIK_REGION == "US" else "api.kentik.eu"
    
    if KENTIK_EMAIL and KENTIK_TOKEN:
        st.success(f"Connected to {KENTIK_REGION} Cluster")
    
    st.header("Editor Settings")
    editor_height = st.slider("Editor Height", min_value=300, max_value=2000, value=800, step=50)

# Two-pane layout - Give more space to the preview
col_left, col_right = st.columns([1, 2])

# Functions
if "editor_version" not in st.session_state:
    st.session_state["editor_version"] = 0

def format_json():
    try:
        # Get the current key based on version
        current_key = f"query_editor_{st.session_state['editor_version']}"
        current_val = st.session_state.get(current_key, "")
        
        if current_val:
            parsed = json.loads(current_val)
            formatted = json.dumps(parsed, indent=2)
            
            # Increment version to force a widget refresh
            st.session_state["editor_version"] += 1
            new_key = f"query_editor_{st.session_state['editor_version']}"
            
            # Initialize the new key with the formatted value
            st.session_state[new_key] = formatted
    except json.JSONDecodeError:
        st.error("Invalid JSON. Cannot format.")

# Left Pane: JSON Editor
with col_left:
    st.subheader("Data Explorer Query JSON")
    
    # Move buttons to the top
    col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
    
    # Format Button with callback
    col_btn1.button("Format JSON", on_click=format_json)

    action = None
    if col_btn2.button("Get SVG"):
        action = "svg"
    if col_btn3.button("Get PNG"):
        action = "png"
    if col_btn4.button("Get PDF"):
        action = "pdf"

    # Professional Ace Editor for JSON
    # Use a dynamic key to force refresh when formatting
    editor_key = f"query_editor_{st.session_state['editor_version']}"
    
    # If the key is not in session state (first run or just incremented), 
    # we can provide a default value if needed, but the key initialization 
    # in format_json or here handles it.
    if editor_key not in st.session_state:
        st.session_state[editor_key] = ""

    query_json = st_ace(
        value=st.session_state[editor_key],
        language="json",
        height=editor_height,
        font_size=14,
        key=editor_key,
        auto_update=True
    )

# Function to fetch image from Kentik
async def fetch_kentik_image(queries_json, format_type):
    url = f"https://{KENTIK_CLUSTER}/api/v5/query/topxchart"
    headers = {
        "X-CH-Auth-Email": KENTIK_EMAIL,
        "X-CH-Auth-API-Token": KENTIK_TOKEN,
        "Content-Type": "application/json"
    }
    
    # Construct the full payload
    payload = {
        "version": 4,
        "queries": queries_json,
        "imageType": format_type
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=payload, timeout=30.0)
            response.raise_for_status()
            result = response.json()
            if "dataUri" in result:
                return result["dataUri"]
            else:
                st.error("Invalid response from Kentik API: 'dataUri' not found.")
                return None
        except httpx.HTTPStatusError as e:
            st.error(f"Kentik API Error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            st.error(f"Request Error: {str(e)}")
    return None

# Handle Actions
if action and query_json:
    try:
        data = json.loads(query_json)
        
        # Flexibly handle both full JSON and just the queries list
        queries = None
        if isinstance(data, list):
            queries = data
        elif isinstance(data, dict):
            # If they pasted a full object, we only want the 'queries' part
            queries = data.get("queries")
            if queries is None:
                st.error("JSON object found, but no 'queries' key present.")
        
        if queries:
            import asyncio
            # fetch_kentik_image will wrap these queries in a fresh payload 
            # with version=4 and the correct imageType from 'action'
            data_uri = asyncio.run(fetch_kentik_image(queries, action))
            
            if data_uri:
                st.session_state['data_uri'] = data_uri
                st.session_state['format'] = action
        else:
            st.error("Could not identify the queries list in the provided JSON.")
            
    except json.JSONDecodeError:
        st.error("Invalid JSON format. Please check your query.")

# Right Pane: Preview
with col_right:
    st.subheader("Preview")
    if 'data_uri' in st.session_state:
        data_uri = st.session_state['data_uri']
        fmt = st.session_state['format']
        
        # Split dataUri to get base64 part
        # Format: data:image/png;base64,iVBOR...
        header, encoded = data_uri.split(",", 1)
        data = base64.b64decode(encoded)
        
        if fmt == "svg":
            st.download_button("Download SVG", data, file_name="kentik_chart.svg", mime="image/svg+xml")
            # SVG needs to be rendered as HTML because PIL (used by st.image) doesn't support it
            try:
                svg_content = data.decode("utf-8")
                st.markdown(svg_content, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error rendering SVG: {e}")
        elif fmt == "png":
            st.download_button("Download PNG", data, file_name="kentik_chart.png", mime="image/png")
            st.image(data)
        elif fmt == "pdf":
            # Provide a download link and preview for PDF
            st.download_button("Download PDF", data, file_name="kentik_chart.pdf", mime="application/pdf")
            pdf_display = f'<iframe src="{data_uri}" width="100%" height="800" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)
    else:
        st.info("Your chart preview will appear here.")
