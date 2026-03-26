"""Streamlit dashboard for North Star Consolidator."""

import os

import pandas as pd
import requests
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="North Star Consolidator", layout="wide")
st.title("North Star Consolidator")
st.caption("IFRS 10 Group Consolidation Dashboard")

# --- Sidebar: Upload Trial Balance ---
st.sidebar.header("Ingest Trial Balance")

entity_id = st.sidebar.selectbox(
    "Subsidiary",
    [f"SUBS_{i:02d}" for i in range(1, 11)],
)

uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])

if st.sidebar.button("Upload") and uploaded_file:
    with st.spinner(f"Ingesting {entity_id}..."):
        try:
            resp = requests.post(
                f"{BACKEND_URL}/ingest/{entity_id}",
                files={"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")},
                timeout=30,
            )
            resp.raise_for_status()
            summary = resp.json()
            st.sidebar.success(
                f"Committed {summary['entries_committed']} entries "
                f"({summary['unmapped_count']} unmapped)"
            )
            if summary["unmapped_codes"]:
                st.sidebar.warning("Unmapped codes: " + ", ".join(summary["unmapped_codes"]))
        except requests.HTTPError as exc:
            st.sidebar.error(f"Upload failed: {exc.response.text}")
        except Exception as exc:
            st.sidebar.error(str(exc))

# --- Main: Backend health check ---
st.subheader("Service Status")

try:
    health = requests.get(f"{BACKEND_URL}/health", timeout=5)
    if health.ok:
        st.success("Backend: online")
    else:
        st.error("Backend: unhealthy")
except Exception:
    st.error("Backend: unreachable")

st.info("Upload a subsidiary Trial Balance CSV using the sidebar to begin consolidation.")
