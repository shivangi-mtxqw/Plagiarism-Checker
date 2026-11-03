"""Streamlit UI: Plagiarism Checker using KMP and Rabin-Karp (DAA PBL)."""
import html

import pandas as pd
import streamlit as st

from similarity import analyze, compare_algorithms, verdict

st.set_page_config(page_title="Plagiarism Checker", page_icon="📄", layout="wide")
st.title("📄 Plagiarism Checker")
st.caption("String matching with KMP and Rabin-Karp  |  DAA PBL")


def get_input(label, key):
    """Offer paste or .txt upload for one document."""
    st.subheader(label)
    tab_paste, tab_upload = st.tabs(["Paste text", "Upload .txt"])
    with tab_paste:
        pasted = st.text_area("Text", height=250, key=f"{key}_paste",
                              label_visibility="collapsed")
    with tab_upload:
        file = st.file_uploader("Choose a .txt file", type=["txt"], key=f"{key}_file")
    if file is not None:
        return file.read().decode("utf-8", errors="ignore")
    return pasted


with st.sidebar:
    st.header("Settings")
    algorithm = st.radio("Algorithm", ["KMP", "Rabin-Karp"])
    min_words = st.slider("Minimum words per sentence", 2, 10, 4,
                          help="Shorter sentences are skipped to avoid trivial matches.")

col1, col2 = st.columns(2)
with col1:
    doc_a = get_input("Document A (suspected)", "a")
with col2:
    doc_b = get_input("Document B (source)", "b")

if st.button("Check similarity", type="primary"):
    if not doc_a.strip() or not doc_b.strip():
        st.warning("Please provide both documents.")
        st.stop()

    res = analyze(doc_a, doc_b, algorithm, min_words)

    st.divider()
    st.header("Result")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Similarity", f"{res['similarity']}%")
    m2.metric("Matched sentences", f"{res['matched_sentences']} / {res['checked_sentences']}")
    m3.metric("Time", f"{res['time_ms']:.3f} ms")
    m4.metric("Comparisons", res["comparisons"])
    st.info(verdict(res["similarity"]))

    st.subheader("Document A with matches highlighted")
    parts = []
    for r in res["results"]:
        text = html.escape(r["sentence"])
        if r["matched"]:
            parts.append(f"<mark style='background:#ff9b9b;color:#000'>{text}</mark>")
        else:
            parts.append(text)
    st.markdown(" ".join(parts), unsafe_allow_html=True)

    st.subheader("Performance comparison: KMP vs Rabin-Karp")
    both = compare_algorithms(doc_a, doc_b, min_words)
    df = pd.DataFrame([{
        "Algorithm": name,
        "Similarity (%)": r["similarity"],
        "Avg time (ms)": round(r["time_ms"], 4),
        "Comparisons": r["comparisons"],
        "Spurious hits": r["spurious_hits"],
    } for name, r in both.items()])
    st.dataframe(df, hide_index=True, use_container_width=True)
    c1, c2 = st.columns(2)
    c1.bar_chart(df.set_index("Algorithm")["Avg time (ms)"])
    c2.bar_chart(df.set_index("Algorithm")["Comparisons"])
    