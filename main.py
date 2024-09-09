import streamlit as st
from metaprompt import MetaPrompt

st.set_page_config(page_title="Prompt Generator", page_icon=":brain:")

st.title("Prompt Generator")

metaprompt_generator = MetaPrompt()

if "extracted_prompt_template" not in st.session_state:
    st.session_state.extracted_prompt_template = ""
if "extracted_variables" not in st.session_state:
    st.session_state.extracted_variables = ""

with st.form("prompt_form"):
    task = st.text_area("Describe the task for the prompt:", height=100)
    variables = st.text_area(
        "Enter variables (one per line - optional):", height=100
    )
    submitted = st.form_submit_button("Generate Prompt")

    if submitted:
        (
            st.session_state.extracted_prompt_template,
            st.session_state.extracted_variables,
        ) = metaprompt_generator(task, variables)


if st.session_state.extracted_prompt_template:
    st.subheader("Generated Prompt Template:")
    st.code(st.session_state.extracted_prompt_template, language="text")

if st.session_state.extracted_variables:
    st.subheader("Extracted Variables:")
    st.code(st.session_state.extracted_variables, language="text")