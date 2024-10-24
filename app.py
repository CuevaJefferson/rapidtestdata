import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
import os
from dotenv import load_dotenv
import mammoth
# from langchain import hub
# prompt = hub.pull("rapidtestdataprompt")

load_dotenv()


os.environ['GROQ_API_KEY']=os.getenv("GROQ_API_KEY")
llm=ChatGroq(model_name="Llama3-8b-8192",streaming=True)

def process_document():
    st.session_state.process = True

st.title("🧪RapidTestData")

question = st.chat_input(placeholder="Generate 3 positive cases", on_submit=process_document)


if 'process' not in st.session_state:
    st.session_state.process = False


st.sidebar.title("📄 Documents")
documentation = st.sidebar.file_uploader("Documentation", accept_multiple_files=False, type="docx")
mock_data = st.sidebar.file_uploader("Mock Data", type="json", accept_multiple_files=True)
input = st.sidebar.file_uploader("Input", type="json", accept_multiple_files=False)
output = st.sidebar.file_uploader("Output", type="json", accept_multiple_files=False)
st.sidebar.button("Process", on_click=process_document)

if st.session_state.process:
    documentation_mkdown = ""
    mock_data_json = ""
    input_json = ""
    output_json = ""
    if documentation is not None:
        documentation_mkdown = mammoth.convert(documentation).value
    if mock_data is not None:
        for mock_data_item in mock_data:
            mock_data_json += mock_data_item.getvalue().decode( "utf-8" )
    if input is not None:
        input_json = input.getvalue().decode( "utf-8" )
    if output is not None:
        output_json = output.getvalue().decode( "utf-8" )
    prompt = PromptTemplate.from_file(template_file="./prompt_template.text")
    chain=prompt|llm
    response=chain.invoke({"documentation":documentation_mkdown, "inputjson":input_json, "outputjson": output_json, "mockdata":mock_data_json, "question": question})
    st.markdown(response.content)
else:
    st.write("Automates the creation of test cases and mock data for Kofax and BDD, significantly enhancing efficiency and reducing manual effort.")
    st.write("upload all documents on the side panel. Documentation, input json, output json, and sample mock data")



