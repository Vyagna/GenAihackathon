import streamlit as st
from dotenv import load_dotenv
from app.llm import call_llm
from app.utils import file_to_text

load_dotenv()
st.set_page_config(page_title="AI Compliance Agent", page_icon="🔎", layout="wide")

# Initialize in-session storage
if "records" not in st.session_state:
    st.session_state["records"] = []  # list of dicts: {id, source_type, filename, content, analysis}

st.title("AI Compliance Agent")
st.caption("Analyze communications for potential regulatory risks. Session-only storage, no database.")

with st.form("analyze_form", clear_on_submit=False):
    st.subheader("Input")
    text = st.text_area("Paste email or transcript", height=200, placeholder="Paste here...")
    uploaded = st.file_uploader("Or upload a .txt file", type=["txt"])
    submitted = st.form_submit_button("Analyze")

if submitted:
    content = (text or "").strip()
    source_type = "text"
    filename = None
    if uploaded is not None:
        content = file_to_text(uploaded)
        source_type = "file"
        filename = uploaded.name

    if not content:
        st.error("No content provided.")
    else:
        with st.spinner("Analyzing with LLM..."):
            result = call_llm(content)

        new_id = len(st.session_state["records"]) + 1
        record = {
            "id": new_id,
            "source_type": source_type,
            "filename": filename,
            "content": content,
            "analysis": result
        }
        st.session_state["records"].append(record)

        st.success(f"Analysis complete. Record #{new_id}")
        st.metric("Risk Score", f"{result['risk_score']:.2f}", help=result["summary"])
        st.write(f"Risk Label: {result['risk_label']}")
        st.json({"flagged_items": result["flagged_items"]})
        st.download_button(
            "Download JSON report",
            data=str(result["raw"]).encode("utf-8"),
            file_name=f"report_{new_id}.json",
            mime="application/json"
        )

st.divider()
st.subheader("Recent analyses (this session)")
for rec in reversed(st.session_state["records"][-10:]):
    with st.expander(f"#{rec['id']} — {rec['source_type']} — {rec.get('filename') or ''}"):
        st.code(rec["content"])
        res = rec["analysis"]
        st.metric("Risk Score", f"{res['risk_score']:.2f}")
        st.write(f"Risk Label: {res['risk_label']}")
        st.json({"flagged_items": res["flagged_items"]})
        st.download_button(
            "Download JSON report",
            data=str(res["raw"]).encode("utf-8"),
            file_name=f"report_{rec['id']}.json",
            mime="application/json",
            key=f"dl_{rec['id']}"
        )
