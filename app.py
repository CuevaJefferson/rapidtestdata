import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langsmith.wrappers import wrap_openai
from langsmith import traceable
import os
from dotenv import load_dotenv
import mammoth
import json
from pymongo.mongo_client import MongoClient
from langchain.agents import Tool
from langchain.tools import BaseTool, StructuredTool, tool
import helpers.pymongo_helper as pymongo_helper


load_dotenv()


@st.cache_resource
def get_database_session():
    mongodb_uri = os.getenv("MONGODB_URI")
    return MongoClient(mongodb_uri)


@st.cache_resource
def get_model():
    return ChatGroq(model_name="Llama3-8b-8192", streaming=True, verbose=True)


llm = get_model()
prompt = PromptTemplate.from_file(template_file="./prompt_template.text")


def process_document():
    st.session_state.process = True


def add_scenarios():
    st.session_state.add_scenario = True


def update_key():
    st.session_state.uploader_key += 1


if "process" not in st.session_state:
    st.session_state.process = False

if "add_scenario" not in st.session_state:
    st.session_state.add_scenario = False

if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

path = "Documentations"

st.title("🧪RapidTestData")
question = st.chat_input(
    placeholder="Generate 3 positive cases", on_submit=process_document
)
st.sidebar.title("📄 Documents")
building_block_name = st.sidebar.selectbox(
    options=[x.split(".")[0] for x in os.listdir(path)], label="Building Block"
)
# st.sidebar.text(f"uploaded scenarios: {}")
mock_data = st.sidebar.file_uploader(
    "Mock Data",
    type="json",
    accept_multiple_files=True,
    key=f"mock_uploader_{st.session_state.uploader_key}",
)
input = st.sidebar.file_uploader(
    "Input",
    type="json",
    accept_multiple_files=False,
    key=f"input_uploader_{st.session_state.uploader_key}",
)
output = st.sidebar.file_uploader(
    "Output",
    type="json",
    accept_multiple_files=False,
    key=f"output_uploader_{st.session_state.uploader_key}",
)
st.sidebar.button("Generate Scenarios", on_click=process_document)


def add_scenario():
    pymongo_helper.add_scenario()


st.sidebar.button("Add Scenarios", on_click=add_scenario)

documentation_mkdown = ""
add_mock_data_json = ""
input_json = ""
output_json = ""
mock_data_json = ""


chain = prompt | llm

if st.session_state.add_scenario:
    print(f"BB NAME:{building_block_name}")
    print(f"BB NAME TYPE:{type(building_block_name)}")
    if mock_data is not None:
        for mock_data_item in mock_data:
            add_mock_data_json += mock_data_item.getvalue().decode("utf-8")
    if input is not None:
        add_input_json = input.getvalue().decode("utf-8")
    if output is not None:
        add_output_json = output.getvalue().decode("utf-8")
    add_scenario(
        building_block_name.lower(), add_input_json, add_mock_data_json, add_output_json
    )
    st.session_state.add_scenario = False
    st.write(f"Scenario Added for {building_block_name.lower()}")
    update_key()
    st.rerun()

elif st.session_state.process:
    with open(f"{path}/{building_block_name}.docx", "rb") as docx_file:
        documentation_mkdown = mammoth.convert_to_html(docx_file).value
    if mock_data is not None:
        for mock_data_item in mock_data:
            add_mock_data_json += mock_data_item.getvalue().decode("utf-8")
    if input is not None:
        add_input_json = input.getvalue().decode("utf-8")
    if output is not None:
        add_output_json = output.getvalue().decode("utf-8")

    input_json = pymongo_helper.get_and_build_input_json(building_block_name)
    output_json = pymongo_helper.get_and_build_output_json(building_block_name)
    mock_data_json = pymongo_helper.get_and_build_mock_data_json(building_block_name)

    response = chain.stream(
        {
            "documentation": documentation_mkdown,
            "inputjson": input_json,
            "outputjson": output_json,
            "mockdata": mock_data_json,
            "question": question,
        }
    )
    st.write_stream(response)

else:
    st.write(
        "Automates the creation of test cases and mock data for Kofax and BDD, significantly enhancing efficiency and reducing manual effort."
    )
    st.write("Add isntructions here")
