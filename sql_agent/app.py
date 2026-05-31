import streamlit as st
import pandas as pd
from graph.agent import agent
from evaluation.langfuse_tracker import langfuse

st.set_page_config(
    page_title="Text to SQL Agent",
    page_icon="🤖",
    layout="wide"
)


st.title("🤖 Text to SQL Agent")
# st.markdown("Ask questions in plain English and get data from the database.")

if "messages" not in st.session_state:
    st.session_state.messages = []

if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.markdown("👋 Hello! Ask me anything about your data in plain English.")

for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if "sql" in message:
            with st.expander("🔎 View Generated Query", expanded=False):
                st.code(message["sql"], language="sql")

        if "dataframe" in message:
            df = message["dataframe"]
            if not df.empty:
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Rows Found", len(df))
                with col2:
                    st.metric("Columns", len(df.columns))
                st.dataframe(df, use_container_width=True)

        if message["role"] == "assistant" and message.get("trace_id"):
            trace_id = message["trace_id"]
            feedback_key = f"feedback_{trace_id}"

            if feedback_key not in st.session_state:
                st.markdown("**Was this result helpful?**")
                col_up, col_down, _ = st.columns([1, 1, 8])
                with col_up:
                    if st.button("👍", key=f"up_{i}_{trace_id}"):
                        langfuse.score(
                            trace_id=trace_id,
                            name="user_feedback",
                            value=1,
                            comment="User marked as helpful"
                        )
                        langfuse.flush()
                        st.session_state[feedback_key] = "positive"
                        st.rerun()
                with col_down:
                    if st.button("👎", key=f"down_{i}_{trace_id}"):
                        langfuse.score(
                            trace_id=trace_id,
                            name="user_feedback",
                            value=0,
                            comment="User marked as not helpful"
                        )
                        langfuse.flush()
                        st.session_state[feedback_key] = "negative"
                        st.rerun()
            else:
                if st.session_state[feedback_key] == "positive":
                    st.success("✅ Thanks for your feedback!")
                else:
                    st.warning("⚠️ Thanks for your feedback! We'll improve.")

if user_query := st.chat_input("Ask something... e.g. show me all customers from Delhi"):

    with st.chat_message("user"):
        st.markdown(user_query)

    st.session_state.messages.append({
        "role": "user",
        "content": user_query
    })

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            result = agent.invoke({
                "user_query": user_query,
                "relevant_tables": None,
                "generated_sql": None,
                "is_valid": None,
                "validation_error": None,
                "query_result": None,
                "error": None,
                "db_type": None,
                "trace": None
            })

        if result.get("error"):
            error_msg = result["error"]

            if "SCHEMA_INFO:" in error_msg:
                clean_msg = error_msg.replace("SCHEMA_INFO:", "").strip()
                st.info(clean_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": clean_msg
                })

            elif "GUARDRAIL:" in error_msg:
                clean_msg = error_msg.replace("GUARDRAIL:", "").strip()
                st.warning(f"⚠️ {clean_msg}")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"⚠️ {clean_msg}"
                })

            elif "IRRELEVANT:" in error_msg:
                clean_msg = error_msg.replace("IRRELEVANT:", "").strip()
                st.info(f"ℹ️ {clean_msg}")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"ℹ️ {clean_msg}"
                })

            elif "UNCLEAR:" in error_msg:
                clean_msg = error_msg.replace("UNCLEAR:", "").strip()
                st.warning(f"🤔 {clean_msg}")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"🤔 {clean_msg}"
                })

            else:
                st.error("❌ Something went wrong. Please rephrase your question and try again.")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "❌ Something went wrong. Please rephrase your question and try again."
                })

        elif result.get("validation_error"):
            msg = result["validation_error"]
            st.warning(f"⚠️ {msg}")
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"⚠️ {msg}"
            })

        elif result.get("query_result"):
            sql = result["generated_sql"]
            df = pd.DataFrame(
                result["query_result"]["rows"],
                columns=result["query_result"]["columns"]
            )
            trace_id = result.get("trace").id if result.get("trace") else None

            if df.empty:
                st.info("🔍 No results found. Try rephrasing your question.")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "🔍 No results found.",
                    "sql": sql,
                    "dataframe": df
                })
            else:
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Rows Found", len(df))
                with col2:
                    st.metric("Columns", len(df.columns))

                st.dataframe(df, use_container_width=True)

                with st.expander("🔎 View Generated Query", expanded=False):
                    st.code(sql, language="sql")

                st.success(f"Query completed — {len(df)} result(s) found.")

                if trace_id:
                    feedback_key = f"feedback_{trace_id}"
                    if feedback_key not in st.session_state:
                        st.markdown("**Was this result helpful?**")
                        col_up, col_down, _ = st.columns([1, 1, 8])
                        with col_up:
                            if st.button("👍", key=f"up_current_{trace_id}"):
                                langfuse.score(
                                    trace_id=trace_id,
                                    name="user_feedback",
                                    value=1,
                                    comment="User marked as helpful"
                                )
                                langfuse.flush()
                                st.session_state[feedback_key] = "positive"
                                st.rerun()
                        with col_down:
                            if st.button("👎", key=f"down_current_{trace_id}"):
                                langfuse.score(
                                    trace_id=trace_id,
                                    name="user_feedback",
                                    value=0,
                                    comment="User marked as not helpful"
                                )
                                langfuse.flush()
                                st.session_state[feedback_key] = "negative"
                                st.rerun()

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"{len(df)} result(s) found.",
                    "sql": sql,
                    "dataframe": df,
                    "trace_id": trace_id
                })