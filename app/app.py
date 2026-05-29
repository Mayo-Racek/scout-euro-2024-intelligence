"""
Scout — Euro 2024 Football Intelligence (conversational web app)
================================================================
A local web app that wraps the published Scout agent (Conversational
Analytics API) in a friendly interface, and renders the agent's data
answers as football-native pitch visuals.

WHY LOCAL-ONLY (and not a public website):
  The Conversational Analytics API bills the calling project per query.
  Running locally with your personal gcloud credentials means YOU pay for
  YOUR own usage. There is no way for a stranger to ring up charges
  against you. This mirrors how internal analytics tools at real clubs
  are actually deployed: on the analyst's machine, against the team's GCP
  project, authenticated with their normal Google identity. The same
  architecture would deploy to a team-internal Cloud Run instance for the
  analyst staff with SSO — that is a separate project, not a portfolio concern.

WHAT THIS APP ADDS ON TOP OF THE AGENT:
  1. A chat input in plain language (English or Slovak).
  2. Multilingual: prepends a language hint so the agent answers in Slovak
     when selected. The data and reasoning are unchanged.
  3. Football-native pitch visuals chosen by the SHAPE of the agent's data:
     zone columns -> 18-zone pitch heatmap; passer/receiver -> pass network;
     start_x/start_y + xg -> shot map.
  4. Transparency: shows the SQL the agent ran (collapsible).

ARCHITECTURE:
    User -> Streamlit -> Conversational Analytics API -> Scout agent
                                  |
                          returns text + data + SQL
                                  |
    Streamlit inspects the data shape -> picks the right pitch visual
                                      -> renders with mplsoccer.

RUN LOCALLY:
    pip install -r requirements.txt
    gcloud auth application-default login
    streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mplsoccer import Pitch
from google.auth import default as get_default_credentials
import google.auth.transport.requests
import requests

# ============================================================================
# CONFIG
# ============================================================================
PROJECT_ID = "statsbomb-football-iq"
LOCATION = "europe-west1"
AGENT_ID = "agent_cf71801c-6182-4945-8ce8-839a14efb1ac"

st.set_page_config(page_title="Scout — Euro 2024 Intelligence",
                   page_icon="⚽", layout="wide")


# ============================================================================
# AUTH — uses your local gcloud Application Default Credentials.
# One-time setup:  gcloud auth application-default login
# ============================================================================
@st.cache_resource
def get_creds():
    creds, _ = get_default_credentials(scopes=[
        "https://www.googleapis.com/auth/cloud-platform"
    ])
    return creds


# ============================================================================
# CONVERSATIONAL ANALYTICS API CALL
# Single thin wrapper so we adjust in one place if the API shape evolves.
# ============================================================================
def ask_scout(question: str, language: str = "English") -> dict:
    """POST to the Conversational Analytics API. Returns {text, data, sql, raw}."""
    if language == "Slovak":
        question = "Odpoveď napíš po slovensky.\n\n" + question

    creds = get_creds()
    creds.refresh(google.auth.transport.requests.Request())

    url = (f"https://geminidataanalytics.googleapis.com/v1beta/"
           f"projects/{PROJECT_ID}/locations/{LOCATION}:chat")

    payload = {
        "parent": f"projects/{PROJECT_ID}/locations/{LOCATION}",
        "messages": [{"userMessage": {"text": question}}],
        "dataAgentContext": {
            "dataAgent": (f"projects/{PROJECT_ID}/locations/{LOCATION}"
                          f"/dataAgents/{AGENT_ID}")
        },
    }

    resp = requests.post(
        url,
        headers={"Authorization": f"Bearer {creds.token}",
                 "Content-Type": "application/json"},
        json=payload, timeout=60,
    )
    resp.raise_for_status()
    raw = resp.json()

    out = {"text": "", "data": pd.DataFrame(), "sql": "", "raw": raw}
    for msg in raw.get("messages", []):
        sys = msg.get("systemMessage", {})
        if "text" in sys:
            out["text"] += "\n".join(sys["text"].get("parts", [])) + "\n"
        elif "data" in sys:
            d = sys["data"]
            if "generatedSql" in d:
                out["sql"] = d["generatedSql"]
            if "result" in d:
                rows = d["result"].get("data", [])
                if rows:
                    out["data"] = pd.DataFrame(rows)
    return out


# ============================================================================
# VISUAL ROUTING — pick the right pitch visual from the agent's data shape
# ============================================================================
def infer_visual(df: pd.DataFrame) -> str:
    if df is None or df.empty:
        return "none"
    cols = set(c.lower() for c in df.columns)
    if "zone" in cols:
        return "zone_heatmap"
    if "passer_name" in cols and "receiver_name" in cols:
        return "pass_network"
    if {"start_x", "start_y"}.issubset(cols) and "xg" in cols:
        return "shot_map"
    return "table"


# 18-zone grid (mirrors includes/zones.js)
THIRDS = {"Def": 0, "Mid": 1, "Att": 2}
CHANS = {"LW": 0, "LHS": 1, "LC": 2, "RC": 3, "RHS": 4, "RW": 5}


def render_zone_heatmap(df: pd.DataFrame):
    numeric_cols = [c for c in df.columns
                    if c.lower() != "zone" and pd.api.types.is_numeric_dtype(df[c])]
    if not numeric_cols:
        return None
    value_col = numeric_cols[0]

    grid = np.zeros((6, 3))
    for _, r in df.iterrows():
        z = str(r["zone"])
        if "-" in z:
            t, c = z.split("-")
            if t in THIRDS and c in CHANS:
                grid[CHANS[c], THIRDS[t]] = r[value_col]

    pitch = Pitch(pitch_type="statsbomb", line_color="#888", pitch_color="#1a1a2e")
    fig, ax = pitch.draw(figsize=(9, 6))
    fig.set_facecolor("#1a1a2e")
    vmin, vmax = grid.min(), grid.max()
    rng = max(abs(vmin), abs(vmax)) or 1
    cmap = plt.cm.RdYlGn if vmin < 0 else plt.cm.inferno

    for ci, c in enumerate(["LW", "LHS", "LC", "RC", "RHS", "RW"]):
        for ti, t in enumerate(["Def", "Mid", "Att"]):
            v = grid[ci, ti]
            colour_val = 0.5 + (v / (2 * rng)) if vmin < 0 else v / (rng or 1)
            ax.add_patch(plt.Rectangle((ti * 40, ci * 13.33), 40, 13.33,
                         color=cmap(colour_val), alpha=0.75, zorder=0))
            ax.text(ti * 40 + 20, ci * 13.33 + 6.6, f"{v:.2f}",
                    color="white", ha="center", fontsize=8, zorder=2)
    ax.set_title(f"By zone ({value_col}) — attacking →", color="white", fontsize=12)
    return fig


def render_pass_network(df: pd.DataFrame):
    if "passes" not in df.columns:
        return None
    use_pos = "avg_start_x" in df.columns and "avg_start_y" in df.columns
    pos = df.groupby("passer_name").agg(
        x=("avg_start_x", "mean") if use_pos else ("passes", "count"),
        y=("avg_start_y", "mean") if use_pos else ("passes", "count"),
        vol=("passes", "sum"),
    ).reset_index()
    pitch = Pitch(pitch_type="statsbomb", pitch_color="#1a1a2e", line_color="#888")
    fig, ax = pitch.draw(figsize=(10, 7)); fig.set_facecolor("#1a1a2e")
    for _, e in df.iterrows():
        a = pos[pos.passer_name == e.passer_name]
        b = pos[pos.passer_name == e.receiver_name]
        if len(a) and len(b) and e.passes >= 3:
            pitch.lines(a.x.values[0], a.y.values[0],
                        b.x.values[0], b.y.values[0],
                        lw=e.passes * 0.25, color="#4cc9f0", alpha=.5, ax=ax)
    pitch.scatter(pos.x, pos.y, s=pos.vol * 3, color="#f72585",
                  edgecolors="white", ax=ax)
    for _, p in pos.iterrows():
        ax.text(p.x, p.y + 2, str(p.passer_name).split()[-1],
                color="white", ha="center", fontsize=8)
    ax.set_title("Pass network", color="white")
    return fig


def render_shot_map(df: pd.DataFrame):
    pitch = Pitch(pitch_type="statsbomb", half=True,
                  pitch_color="#1a1a2e", line_color="#888")
    fig, ax = pitch.draw(figsize=(8, 7)); fig.set_facecolor("#1a1a2e")
    is_goal = df["is_goal"] if "is_goal" in df.columns else pd.Series([False]*len(df))
    pitch.scatter(df.start_x, df.start_y, s=df.xg * 600 + 20,
                  c=is_goal.map({True: "#f72585", False: "#4cc9f0"}),
                  edgecolors="white", ax=ax)
    ax.set_title("Shots (size = xG, pink = goal)", color="white")
    return fig


# ============================================================================
# UI
# ============================================================================
st.title("⚽ Scout — Euro 2024 Football Intelligence")
st.caption("Ask a tactical question in plain language. Scout queries verified "
           "BigQuery marts and shows the answer on the pitch.")

with st.sidebar:
    st.header("Settings")
    language = st.radio("Answer language", ["English", "Slovak"], index=0,
                        help="Slovak: the agent answers in Slovak. "
                             "Data and reasoning are unchanged.")
    st.markdown("---")
    st.subheader("Try a question")
    examples = [
        "How did Spain start their games?",
        "Where is England most vulnerable?",
        "Where did Slovakia lose the ball?",
        "Who drove Spain's possession?",
        "Which teams pressed highest?",
    ]
    for ex in examples:
        if st.button(ex, key=f"ex_{ex[:16]}", use_container_width=True):
            st.session_state["pending_question"] = ex
    st.markdown("---")
    st.caption(f"Project: `{PROJECT_ID}`")
    st.caption("Data: StatsBomb / Hudl Open Data")

default = st.session_state.pop("pending_question", "")
question = st.chat_input("Ask Scout a tactical question…") or default

if question:
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        with st.spinner("Scout is thinking…"):
            try:
                answer = ask_scout(question, language=language)
            except Exception as e:
                st.error(f"API call failed: {e}")
                st.caption("Run `gcloud auth application-default login` if you "
                           "haven't, and confirm the agent ID/region are correct.")
                st.stop()

        if answer["text"]:
            st.markdown(answer["text"])

        df = answer["data"]
        if not df.empty:
            kind = infer_visual(df)
            col1, col2 = st.columns([3, 2])
            with col2:
                st.subheader("Data")
                st.dataframe(df, use_container_width=True, hide_index=True)
            with col1:
                if kind == "zone_heatmap":
                    fig = render_zone_heatmap(df)
                    if fig: st.pyplot(fig)
                elif kind == "pass_network":
                    fig = render_pass_network(df)
                    if fig: st.pyplot(fig)
                elif kind == "shot_map":
                    fig = render_shot_map(df)
                    if fig: st.pyplot(fig)
                else:
                    st.caption("No pitch visual for this answer shape — "
                               "data table is on the right.")

        if answer["sql"]:
            with st.expander("See the SQL Scout ran"):
                st.code(answer["sql"], language="sql")

st.markdown("---")
st.caption("Scout reads only verified marts — built and quality-checked in "
           "Dataform. Answers are grounded in real data with honest caveats.")
