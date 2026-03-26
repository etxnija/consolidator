"""Streamlit dashboard for North Star Consolidator."""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import requests
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="North Star Consolidator", layout="wide")
st.title("North Star Consolidator")
st.caption("IFRS 10 Group Consolidation Dashboard")


# ---------------------------------------------------------------------------
# Helper: API calls
# ---------------------------------------------------------------------------

def api_get(path: str) -> Optional[Any]:
    try:
        resp = requests.get(f"{BACKEND_URL}{path}", timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:
        st.error(f"GET {path} failed: {exc}")
        return None


def api_post(path: str, payload: dict) -> Optional[Any]:
    try:
        resp = requests.post(f"{BACKEND_URL}{path}", json=payload, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.HTTPError as exc:
        st.error(f"Error: {exc.response.text}")
        return None
    except Exception as exc:
        st.error(str(exc))
        return None


# ---------------------------------------------------------------------------
# Data loaders (cached per rerun)
# ---------------------------------------------------------------------------

@st.cache_data(ttl=5)
def load_entities() -> List[dict]:
    return api_get("/entities") or []


@st.cache_data(ttl=5)
def load_entity_tree() -> List[dict]:
    return api_get("/entities/tree") or []


@st.cache_data(ttl=5)
def load_periods() -> List[dict]:
    return api_get("/periods") or []


# ---------------------------------------------------------------------------
# Period selector (top of sidebar — used by all operations)
# ---------------------------------------------------------------------------

st.sidebar.header("Reporting Period")

periods = load_periods()
period_labels = [p["label"] for p in periods]

if period_labels:
    selected_period_label = st.sidebar.selectbox("Active period", period_labels)
    selected_period = next((p for p in periods if p["label"] == selected_period_label), None)
else:
    st.sidebar.info("No periods yet — create one below.")
    selected_period = None

if selected_period:
    st.sidebar.caption(
        f"{selected_period['period_start']} → {selected_period['period_end']}  "
        f"[{selected_period['status']}]"
    )

# Store in session state so other sections can use it
st.session_state["active_period"] = selected_period

st.sidebar.divider()

# ---------------------------------------------------------------------------
# Sidebar: Create Entity
# ---------------------------------------------------------------------------

st.sidebar.header("Create Entity")

with st.sidebar.form("create_entity_form"):
    entity_name = st.text_input("Entity name", placeholder="e.g. Acme Holdings")

    entities = load_entities()
    parent_options = {"— none (top-level) —": None}
    for e in entities:
        parent_options[e["name"]] = e["entity_id"]

    parent_label = st.selectbox("Parent entity", list(parent_options.keys()))
    parent_id = parent_options[parent_label]

    ownership_pct = st.number_input(
        "Ownership % (parent → this entity)",
        min_value=0.0,
        max_value=100.0,
        value=100.0,
        step=0.5,
        disabled=(parent_id is None),
        help="Leave at 100 for wholly-owned; ignored if no parent.",
    )

    submitted = st.form_submit_button("Create entity")
    if submitted:
        if not entity_name.strip():
            st.error("Entity name is required.")
        else:
            payload: dict = {"name": entity_name.strip()}
            if parent_id is not None:
                payload["parent_entity_id"] = parent_id
                payload["ownership_pct"] = ownership_pct
            result = api_post("/entities", payload)
            if result:
                st.success(f"Created: {result['name']} ({result['entity_id'][:8]}…)")
                st.cache_data.clear()

st.sidebar.divider()

# ---------------------------------------------------------------------------
# Sidebar: Create Reporting Period
# ---------------------------------------------------------------------------

st.sidebar.header("Create Reporting Period")

with st.sidebar.form("create_period_form"):
    period_label = st.text_input("Label", placeholder="e.g. FY-2024")
    period_start = st.date_input("Period start")
    period_end = st.date_input("Period end")

    period_submitted = st.form_submit_button("Create period")
    if period_submitted:
        if not period_label.strip():
            st.error("Label is required.")
        elif period_end < period_start:
            st.error("End date must be on or after start date.")
        else:
            result = api_post(
                "/periods",
                {
                    "label": period_label.strip(),
                    "period_start": str(period_start),
                    "period_end": str(period_end),
                },
            )
            if result:
                st.success(f"Period '{result['label']}' created.")
                st.cache_data.clear()

st.sidebar.divider()

# ---------------------------------------------------------------------------
# Sidebar: Ingest Trial Balance
# ---------------------------------------------------------------------------

st.sidebar.header("Ingest Trial Balance")

entity_options = {e["name"]: e["entity_id"] for e in load_entities()}

if entity_options:
    ingest_entity_label = st.sidebar.selectbox("Subsidiary", list(entity_options.keys()), key="ingest_entity")
    ingest_entity_id = entity_options[ingest_entity_label]
else:
    st.sidebar.info("Create entities first.")
    ingest_entity_id = None

uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])

if st.sidebar.button("Upload") and uploaded_file and ingest_entity_id:
    with st.spinner(f"Ingesting {ingest_entity_label}..."):
        try:
            resp = requests.post(
                f"{BACKEND_URL}/ingest/{ingest_entity_id}",
                files={"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")},
                timeout=30,
            )
            resp.raise_for_status()
            summary = resp.json()
            st.sidebar.success(
                f"Committed {summary['entries_committed']} entries "
                f"({summary['unmapped_count']} unmapped)"
            )
            if summary.get("unmapped_codes"):
                st.sidebar.warning("Unmapped codes: " + ", ".join(summary["unmapped_codes"]))
        except requests.HTTPError as exc:
            st.sidebar.error(f"Upload failed: {exc.response.text}")
        except Exception as exc:
            st.sidebar.error(str(exc))


# ---------------------------------------------------------------------------
# Main: Service Status
# ---------------------------------------------------------------------------

st.subheader("Service Status")

try:
    health = requests.get(f"{BACKEND_URL}/health", timeout=5)
    if health.ok:
        st.success("Backend: online")
    else:
        st.error("Backend: unhealthy")
except Exception:
    st.error("Backend: unreachable")

st.divider()


# ---------------------------------------------------------------------------
# Main: Ownership Tree
# ---------------------------------------------------------------------------

def render_tree_node(node: Dict[str, Any], depth: int = 0) -> None:
    indent = "  " * depth
    pct = f" ({node['ownership_pct']}%)" if node.get("ownership_pct") else ""
    icon = "🏢" if depth == 0 else ("└─ " if depth > 0 else "")
    st.markdown(f"{indent}{icon} **{node['name']}**{pct}")
    for child in node.get("children", []):
        render_tree_node(child, depth + 1)


st.subheader("Ownership Tree")

tree = load_entity_tree()
if tree:
    for root in tree:
        render_tree_node(root)
else:
    st.info("No entities yet. Create entities using the sidebar.")

st.divider()


# ---------------------------------------------------------------------------
# Main: Active Period Summary
# ---------------------------------------------------------------------------

st.subheader("Active Period")

active = st.session_state.get("active_period")
if active:
    col1, col2, col3 = st.columns(3)
    col1.metric("Label", active["label"])
    col2.metric("Start", active["period_start"])
    col3.metric("End", active["period_end"])
    st.caption(f"Status: {active['status']}  ·  ID: {active['period_id']}")
else:
    st.info("No reporting period selected. Create and select a period using the sidebar.")
