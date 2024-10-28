from pymongo.mongo_client import MongoClient
import os

def get_database_session():
    mongodb_uri = os.getenv("MONGODB_URI")
    return MongoClient(mongodb_uri)

client = get_database_session()
input_json_db = client["rapid-test-data"]["input-json"] 
mock_json_db = client["rapid-test-data"]["mock-data-json"] 
output_json_db = client["rapid-test-data"]["output-json"] 


def get_and_build_input_json(building_block_name):
    result = list(input_json_db.find({"building_block_name": building_block_name }))
    builder = ""
    for entry in result:
        builder += f'this is the input for scenario {entry["scenario_number"]}: input: {entry["input"]}. '
    return builder

def get_and_build_mock_data_json(building_block_name):
    result = list(mock_json_db.find({"building_block_name": building_block_name }))
    builder = ""
    for entry in result:
        builder += f'this is one of the mock-data for scenario {entry["scenario_number"]}: mock-data: {entry["mock_data"]}. '
    return builder

def get_and_build_output_json(building_block_name):
    result = list(output_json_db.find({"building_block_name": building_block_name }))
    builder = ""
    for entry in result:
        builder += f'this is the output for scenario {entry["scenario_number"]}: output: {entry["output"]}. '
    return builder

def get_scenario_count(building_block_name):
    result = list(input_json_db.find({"building_block_name": building_block_name }))
    seen = set()
    for entry in result:
        if entry["scenario_number"] not in seen:
            seen.add(entry["scenario_number"])
    return len(seen)

def get_next_scenario_id(building_block_name):
    result = list(input_json_db.find({"building_block_name": building_block_name }))
    seen = set()
    for entry in result:
        if entry["scenario_number"] not in seen:
            seen.add(entry["scenario_number"])
    scenario_number = 1
    seen = set(int(x) for x in seen)
    while True:
        if scenario_number not in seen:
            return scenario_number     
        else:
            scenario_number+=1


def add_input_json(building_block_name, scenario_number, ijson):
    data={"scenario_number":scenario_number, "building_block_name": building_block_name, "input": ijson }
    print(f"DATA: {data}")
    input_json_db.insert_one(data)
    
def add_mock_data(building_block_name, scenario_number, mjson):
    data={"scenario_number":scenario_number, "building_block_name": building_block_name, "mock_data": mjson }
    mock_json_db.insert_one(data)
    
def add_output_json(building_block_name, scenario_number, ojson):
    data={"scenario_number":scenario_number, "building_block_name": building_block_name, "output": ojson }
    output_json_db.insert_one(data)

def add_scenario(building_block_name, input, mock_data, output):
    scenario_number = get_next_scenario_id(building_block_name)
    add_input_json(building_block_name, scenario_number, input)
    add_mock_data(building_block_name, scenario_number, mock_data)
    add_output_json(building_block_name, scenario_number, output)