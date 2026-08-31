from __future__ import annotations

import streamlit as st

from rag_compliance_assistant.api.dependencies import get_evaluation_service, get_rag_service


def main() -> None:
    st.set_page_config(
        page_title="Enterprise RAG Compliance Assistant",
        page_icon="",
        layout="wide",
    )
    st.title("Enterprise RAG Evaluation & Compliance Assistant")

    rag_service = get_rag_service()
    evaluation_service = get_evaluation_service()

    with st.sidebar:
        st.header("Controls")
        top_k = st.slider("Retrieved chunks", min_value=1, max_value=8, value=4)
        if st.button("Re-index sample documents"):
            ingest_report = rag_service.ingest()
            st.success(
                f"Indexed {ingest_report['chunks_indexed']} chunks "
                f"from {ingest_report['documents_loaded']} docs."
            )
        if st.button("Run evaluation"):
            evaluation_report = evaluation_service.run(top_k=top_k)
            st.session_state["evaluation_report"] = evaluation_report

    query = st.text_input(
        "Question",
        value="Can employees paste confidential customer data into unapproved public AI tools?",
    )
    if st.button("Ask", type="primary"):
        st.session_state["query_result"] = rag_service.ask(query, top_k=top_k)

    result = st.session_state.get("query_result")
    if result is not None:
        st.subheader("Answer")
        st.write(result.answer)
        left, middle, right = st.columns(3)
        left.metric("Confidence", result.confidence)
        middle.metric("Guardrail", result.guardrail.decision)
        right.metric("Trace ID", result.trace_id or 0)

        st.subheader("Citations")
        if result.citations:
            for citation in result.citations:
                with st.expander(f"{citation.source} - {citation.title}"):
                    st.write(citation.quote)
        else:
            st.info("No citations returned for this response.")

        st.subheader("Retrieved chunks")
        for retrieved in result.retrieved_chunks:
            with st.expander(
                f"{retrieved.chunk.source} chunk {retrieved.chunk.chunk_index} "
                f"(score {retrieved.score:.3f}, overlap {retrieved.overlap_terms})"
            ):
                st.write(retrieved.chunk.text)

    report = st.session_state.get("evaluation_report")
    if report is not None:
        st.subheader("Evaluation metrics")
        st.json(report["metrics"])
        with st.expander("Case-level report"):
            st.json(report["cases"])


if __name__ == "__main__":
    main()
