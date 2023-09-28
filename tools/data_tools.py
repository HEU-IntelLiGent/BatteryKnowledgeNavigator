import re
import streamlit as st
from jsonschema import validate, ValidationError
from tools import ontology_tools as ot 
import pandas as pd
from SPARQLWrapper import SPARQLWrapper, JSON, POST, DELETE, INSERT
import datetime
from rdflib import Graph, URIRef, Namespace, Literal
import uuid
from io import StringIO
import psycopg2




@st.cache_data
def camel_to_normal(text):
    words = re.findall(r'[A-Z][a-z]*|[a-z]+', text)
    return ' '.join(words)

def triple_df_label_to_uri(df_label):
    #df_uri = pd.DataFrame(columns=['subj', 'pred', 'obj', 'obj_type', 'obj_lang'])
    data_uri = []
    
    for index, row in df_label.iterrows():
        if row['subj'] in st.session_state.label_uri_dict:
            subject = st.session_state.label_uri_dict.get(row['subj'])
        else:
            subject = row['subj']
        if row['pred'] in st.session_state.label_uri_dict:
            predicate = st.session_state.label_uri_dict.get(row['pred'])
        else:
            predicate = row['pred']
        
        # If obj_type is "literal", keep the same value without looking up in dict
        if row['obj_type'] == 'literal':
            obj = row['obj']
            obj_lang = 'en'
        else:
            obj = st.session_state.label_uri_dict.get(row['obj'], row['obj'])
            obj_lang = None
        
        obj_type = row['obj_type']
        
        data_uri.append({'subj': subject, 'pred': predicate, 'obj': obj, 'obj_type': obj_type, 'obj_lang': obj_lang})
        df_uri = pd.DataFrame(data_uri)
        
    return df_uri

def triple_df_uri_to_label(df_uri):
    #df_label = pd.DataFrame(columns=['subj', 'pred', 'obj', 'obj_type', 'obj_lang'])
    data_label = []
    df_label= pd.DataFrame()
    
    for index, row in df_uri.iterrows():
        if row['subj'] in st.session_state.uri_label_dict:
            subject = st.session_state.uri_label_dict.get(row['subj'])
        else:
            subject = row['subj']
        if row['pred'] in st.session_state.uri_label_dict:
            predicate = st.session_state.uri_label_dict.get(row['pred'])
        else:
            predicate = row['pred']
        
        # If obj_type is "literal", keep the same value without looking up in dict
        if row['obj_type'] == 'literal':
            obj = row['obj']
        else:
            obj = next((label for label, uri in st.session_state.uri_label_dict.items() if uri == row['obj']), row['obj'])
            
        obj_type = row['obj_type']
        obj_lang = row['obj_lang']
        
        data_label.append({'subj': subject, 'pred': predicate, 'obj': obj, 'obj_type': obj_type, 'obj_lang': obj_lang})
        df_label = pd.DataFrame(data_label)
    
    return df_label


def fetch_manufacturers_from_blazegraph():

    #sparql = SPARQLWrapper("http://localhost:9999/blazegraph/sparql")
    sparql = ot.open_blazegraph_endpoint()
    query_text = """
        PREFIX schema: <https://schema.org/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT DISTINCT ?entity WHERE {
            ?class rdfs:subClassOf* schema:Organization .
            ?entity rdf:type ?class .
        }
    """
    sparql.setQuery(query_text)
    sparql.setReturnFormat(JSON)
    
    results = sparql.query().convert()
    subclasses = [result["entity"]["value"] for result in results["results"]["bindings"]]
    
    return subclasses

def fetch_batteries_from_blazegraph():

    #sparql = SPARQLWrapper("http://localhost:9999/blazegraph/sparql")
    sparql = ot.open_blazegraph_endpoint()
    query_text = """
        PREFIX schema: <https://schema.org/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        
        SELECT DISTINCT ?entity WHERE {
            ?class rdfs:subClassOf* <http://emmo.info/battery#battery_74ed2670_657d_4f0b_b0a6_3f13bc2e9c17> .
            ?entity rdf:type ?class .
        }
    """
    sparql.setQuery(query_text)
    sparql.setReturnFormat(JSON)
    
    results = sparql.query().convert()
    subclasses = [result["entity"]["value"] for result in results["results"]["bindings"]]
    
    return subclasses

def fetch_materials(category):
    
    if category == "active_material":
        materials_dict = {
            "Graphite": "http://emmo.info/emmo#material_d53259a7_0d9c_48b9_a6c1_4418169df303",
            "LNMO": "http://emmo.info/emmo#material_f3e7979a_e3ef_450a_8762_7d8778afe478",
            "NMC": "http://emmo.info/emmo#material_3ac62305_acd6_4312_9e31_4f824bd2530d",
            }
        
    elif category == "solvent":
        materials_dict = {
            "EC": "http://emmo.info/emmo#material_57339d90_0553_4a96_8da9_ff6c3684e226",
            "DMC": "http://emmo.info/emmo#material_c4a7d7bd_497e_457e_b858_ff73254266d0",
            "DEC": "http://emmo.info/emmo#material_b8baff0d_7163_4ef1_ac3b_7694b59e500a",
            "EMC": "http://emmo.info/emmo#material_bb20bdea_343c_4911_8c45_37fc1077d22f",
            "PC": "http://emmo.info/emmo#material_46e9f253_40cb_4b48_b8d0_0b976ea4e156",
            "VC": "http://emmo.info/emmo#material_31d0d139_7b45_4d1e_8603_92cc12da2fad",
            "FEC": "http://emmo.info/emmo#material_20004d19_02cf_4667_a09f_b5c595b44b1f",
            }
        
    elif category == "solute":
        materials_dict = {
            "LiPF6": "http://emmo.info/emmo#material_0deb4fe8_b0c0_4e3f_8848_64435e5c0771",
            "LiBOB": "http://emmo.info/emmo#material_4c01eadc_81a0_4ad7_a72f_4d5f72f60f04",
            "VC": "http://emmo.info/emmo#material_31d0d139_7b45_4d1e_8603_92cc12da2fad",
            "FEC": "http://emmo.info/emmo#material_20004d19_02cf_4667_a09f_b5c595b44b1f",
            }
        
    elif category == "binder":
        materials_dict = {
            "PVDF": "http://emmo.info/emmo#material_f2e48e9e_f774_4f42_939f_1fe522efb7c8",
            "CMC": "http://emmo.info/emmo#material_d36fbe2f_6b0a_4178_b6ca_7373bdefcb51"
            }
        
    elif category == "conductive_additive":
        materials_dict = {
            "Carbon Black": "http://emmo.info/emmo#material_0a5cb747_60cf_4929_a54a_712c54b49f3b"
            }
        
    elif category == "current_collector":
        materials_dict = {
            "Copper": "http://emmo.info/emmo#material_0993cbab_ff7f_4ec3_8a6c_cd67497d54d9",
            "Aluminium": "http://emmo.info/emmo#material_8f7dd877_5ad0_48f1_bbec_84153d8215f4"
            }
    
    return materials_dict


def fetch_materials_from_blazegraph(category):

    category_uri_dict = {
        "active_material": "http://emmo.info/electrochemistry#electrochemistry_79d1b273-58cd-4be6-a250-434817f7c261",
        "binder": "http://emmo.info/electrochemistry#electrochemistry_68eb5e35_5bd8_47b1_9b7f_f67224fa291e",
        "conductive_additive": "http://emmo.info/electrochemistry#electrochemistry_82fef384_8eec_4765_b707_5397054df594",
        "current_collector": "http://emmo.info/electrochemistry#electrochemistry_212af058_3bbb_419f_a9c6_90ba9ebb3706"
        }
    
    material_uri = URIRef(category_uri_dict[category])
    
    sparql = ot.open_blazegraph_endpoint()
    query_text = f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    SELECT ?material
    WHERE {{
    ?material rdf:type <{material_uri}> .
    }}
    """
    sparql.setQuery(query_text)
    sparql.setReturnFormat(JSON)
    
    results = sparql.query().convert()
    materials = [result["material"]["value"] for result in results["results"]["bindings"]]
    
    return materials

def fetch_components_from_blazegraph(category):

    category_uri_dict = {
        "electrode": "http://emmo.info/electrochemistry#electrochemistry_0f007072-a8dd-4798-b865-1bf9363be627",
        "separator": "http://emmo.info/electrochemistry#electrochemistry_331e6cca_f260_4bf8_af55_35304fe1bbe0",
        "electrolyte": "http://emmo.info/electrochemistry#electrochemistry_fb0d9eef_92af_4628_8814_e065ca255d59",
        "case": "http://emmo.info/electrochemistry#electrochemistry_1aec4cc0_82d5_4042_a657_ed7fe291c3d8"
        }
    
    material_uri = URIRef(category_uri_dict[category])
    
    sparql = ot.open_blazegraph_endpoint()
    query_text = f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    SELECT ?component
    WHERE {{
    ?component rdf:type <{material_uri}> .
    }}
    """
    sparql.setQuery(query_text)
    sparql.setReturnFormat(JSON)
    
    results = sparql.query().convert()
    components = [result["component"]["value"] for result in results["results"]["bindings"]]
    
    return components

def schema_to_form(schema):
    
    #label_uri_dict, uri_label_dict = ot.build_dict()

    is_electrolyte = "solvent" in schema["properties"] or "solute" in schema["properties"]
    is_test_protocol = "steps" in schema["properties"]

    # Initializing Streamlit session state if not already
    if is_electrolyte:
        if 'num_solvent' not in st.session_state:
            st.session_state.num_solvent = 1

        if 'num_solute' not in st.session_state:
            st.session_state.num_solute = 1
    elif is_test_protocol:
        if 'num_steps' not in st.session_state:
            st.session_state.num_steps = 1

    if is_electrolyte:

        # Creating columns for the solvents and solutes
        col_solvent, col_solute = st.columns(2)
        with col_solvent:
            st.session_state.num_solvent = st.number_input("Number of solvents", min_value=0, value=st.session_state.num_solvent, step=1)
        with col_solute:
            st.session_state.num_solute = st.number_input("Number of solutes", min_value=0, value=st.session_state.num_solute, step=1)
        
            
    elif is_test_protocol:
        st.session_state.num_steps = st.number_input("Number of steps", min_value=1, value=st.session_state.num_steps, step=1)


    with st.form("active_material_form"):

        form_data = {}  # Store user input data
        #form_data = process_form_data(schema, form_data)
        header = st.expander("Header", expanded=True)
        quantities = st.expander("Quantities", expanded=True)
        with quantities:
            col1, col2, col3 = st.columns(3)
        
        for property_name, property_details in schema["properties"].items():
            
            if property_name == "manufacturer":
                # Fetch manufacturers from Blazegraph
                manufacturers = fetch_manufacturers_from_blazegraph()
                manufacturer_names = [st.session_state.uri_label_dict[uri] for uri in manufacturers if uri in st.session_state.uri_label_dict]
                selected_manufacturer = header.selectbox("Select Manufacturer", manufacturer_names)
                form_data[property_name] = selected_manufacturer
                continue
            
            if property_name == "comment":
                # Add a bigger field for comments
                comment = header.text_area("Comment")
                form_data[property_name] = comment
                continue
            
            if property_name == "active_material":
                # Fetch manufacturers from Blazegraph
                materials = fetch_materials_from_blazegraph("active_material")
                material_names = [st.session_state.uri_label_dict[uri] for uri in materials if uri in st.session_state.uri_label_dict]
                selected_material = header.selectbox("Select Active Material", material_names)
                form_data[property_name] = selected_material
                continue
            
            if property_name == "binder":
                # Fetch manufacturers from Blazegraph
                materials = fetch_materials_from_blazegraph("binder")
                material_names = [st.session_state.uri_label_dict[uri] for uri in materials if uri in st.session_state.uri_label_dict]
                selected_material = header.selectbox("Select Binder", material_names)
                form_data[property_name] = selected_material
                continue
            
            if property_name == "conductive_additive":
                # Fetch manufacturers from Blazegraph
                materials = fetch_materials_from_blazegraph("conductive_additive")
                material_names = [st.session_state.uri_label_dict[uri] for uri in materials if uri in st.session_state.uri_label_dict]
                selected_material = header.selectbox("Select Conductive Additive", material_names)
                form_data[property_name] = selected_material
                continue
            
            if property_name == "current_collector":
                # Fetch manufacturers from Blazegraph
                materials = fetch_materials_from_blazegraph("current_collector")
                material_names = [st.session_state.uri_label_dict[uri] for uri in materials if uri in st.session_state.uri_label_dict]
                selected_material = header.selectbox("Select Current Collector", material_names)
                form_data[property_name] = selected_material
                continue
            
            if property_name == "positive_electrode":
                # Fetch manufacturers from Blazegraph
                components = fetch_components_from_blazegraph("electrode")
                component_names = [st.session_state.uri_label_dict[uri] for uri in components if uri in st.session_state.uri_label_dict]
                selected_component = header.selectbox("Select Positive Electrode", component_names)
                form_data[property_name] = selected_component
                continue
            
            if property_name == "negative_electrode":
                # Fetch manufacturers from Blazegraph
                components = fetch_components_from_blazegraph("electrode")
                component_names = [st.session_state.uri_label_dict[uri] for uri in components if uri in st.session_state.uri_label_dict]
                selected_component = header.selectbox("Select Negative Electrode", component_names)
                form_data[property_name] = selected_component
                continue
            
            if property_name == "electrolyte":
                # Fetch manufacturers from Blazegraph
                components = fetch_components_from_blazegraph("electrolyte")
                component_names = [st.session_state.uri_label_dict[uri] for uri in components if uri in st.session_state.uri_label_dict]
                selected_component = header.selectbox("Select Electrolyte", component_names)
                form_data[property_name] = selected_component
                continue
            
            if property_name == "separator":
                # Fetch manufacturers from Blazegraph
                components = fetch_components_from_blazegraph("separator")
                component_names = [st.session_state.uri_label_dict[uri] for uri in components if uri in st.session_state.uri_label_dict]
                selected_component = header.selectbox("Select Separator", component_names)
                form_data[property_name] = selected_component
                continue
            
            if schema["name"] == "Active Material" and property_name == "material":
                # Fetch manufacturers from Blazegraph
                materials = fetch_materials("active_material")
                selected_material = header.selectbox("Select Material", materials.keys())
                form_data[property_name] = materials[selected_material]
                continue
            
            if "date" in property_name.lower():
                # Use Streamlit's date input widget
                selected_date = header.date_input(property_name, datetime.date.today())
                form_data[property_name] = selected_date.strftime('%Y-%m-%d')  # store it as a string, you can adjust the format
                continue
            
            if schema["name"] == "Binder" and property_name == "material":
                materials = fetch_materials("binder")
                selected_material = header.selectbox("Select Material", materials.keys())
                form_data[property_name] = materials[selected_material]
                continue
            
            if schema["name"] == "Conductive Additive" and property_name == "material":
                materials = fetch_materials("conductive_additive")
                selected_material = header.selectbox("Select Material", materials.keys())
                form_data[property_name] = materials[selected_material]
                continue
            
            if schema["name"] == "Current Collector" and property_name == "material":
                materials = fetch_materials("current_collector")
                selected_material = header.selectbox("Select Material", materials.keys())
                form_data[property_name] = materials[selected_material]
                continue
            
            if property_name in ["solvent", "solute"]:  # Skip rendering solvents and solutes here, they're already handled above
                continue

            if "type" in property_details:
                property_type = property_details["type"]
            else:
                property_type = None
            
            if "$ref" in property_details:
                ref = property_details["$ref"]
            else:
                ref = None
                
            if "unit_label" in property_details:
                unit_label = property_details["unit_label"]
            else:
                unit_label = None
            
            if property_type == "string":
                with header:
                    form_data[property_name] = st.text_input(property_name, "")
            elif property_type == "number":
                with header:
                    form_data[property_name] = st.number_input(property_name, 0.0)
            elif ref == "#/definitions/quantity":
                with quantities:
                    col1.text_input('quantity', property_name, disabled=True)
                    value = col2.number_input('value', key=f"{property_name} - Value", value=0.0)
                    unit = col3.text_input('unit', f"{unit_label}", key=f"{property_name} - Unit", disabled=True)
                    form_data[property_name] = {"value": value, "unit": unit}

        if is_electrolyte:
            # Solvent Expander
            if 'solvent' not in form_data:
                form_data['solvent'] = []
            if 'solute' not in form_data:
                form_data['solute'] = []

            with st.expander("Solvents"):
                for i in range(st.session_state.num_solvent):
                    # form_data = process_form_data(schema["properties"]["solvent"]["items"], form_data)
                    cols = st.columns(4)
                    materials = fetch_materials("solvent")
                    selected_material = cols[0].selectbox(f"Solvent {i+1} Name", materials.keys())
                    solvent_type = materials[selected_material]
                    solvent_quantity = cols[1].selectbox(f"Solvent {i+1} Quantity", ["VolumeFraction", "MassFraction"])
                    solvent_value = cols[2].number_input(f"Solvent {i+1} Value", value=1.0)
                    solvent_unit = cols[3].text_input(f"Solvent {i+1} Unit", value="UnitOne", disabled=True)
            
                    # Create a dictionary for this solvent and append it to the 'solvent' list in form_data
                    solvent_data = {
                        "compound": solvent_type,
                        f"{solvent_quantity}": {
                            "value": solvent_value,
                            "unit": solvent_unit
                        }
                    }
                    form_data["solvent"].append(solvent_data)

            # Solute Expander
            with st.expander("Solutes"):
                for i in range(st.session_state.num_solute):
                    # form_data = process_form_data(schema["properties"]["solvent"]["items"], form_data)
                    cols = st.columns(4)
                    materials = fetch_materials("solute")
                    selected_material = cols[0].selectbox(f"Solute {i+1} Name", materials.keys())
                    solute_type = materials[selected_material]
                    solute_quantity = cols[1].selectbox(f"Solute {i+1} Quantity", ["Concentration", "MassFraction"])
                    solute_value = cols[2].number_input(f"Solute {i+1} Value", value=1.0)
                    if solute_quantity == "Concentration":
                        unit = "mol/L"
                    else:
                        unit = "UnitOne"
                    solute_unit = cols[3].text_input(f"Solute {i+1} Unit", value=unit, disabled=True)
            
                    # Create a dictionary for this solvent and append it to the 'solvent' list in form_data
                    solute_data = {
                        "compound": solute_type,
                        f"{solute_quantity}": {
                            "value": solute_value,
                            "unit": solute_unit
                        }
                    }
                    form_data["solute"].append(solute_data)
        
        # Test Protocol form logic
        elif is_test_protocol:
            for i in range(st.session_state.num_steps):
                with st.expander(f"Step {i+1}"):
                    step_type = st.selectbox("Step Type", ["constant current", "constant voltage", "linear voltage sweep"], key=f"step_type_{i}")
                    if step_type == "constant current":
                        current = st.number_input("Current", key=f"current_{i}")
                    elif step_type == "constant voltage":
                        upper_cutoff_voltage = st.number_input("Upper Cutoff Voltage", key=f"upper_cutoff_voltage_{i}")
                        lower_cutoff_voltage = st.number_input("Lower Cutoff Voltage", key=f"lower_cutoff_voltage_{i}")
                    elif step_type == "linear voltage sweep":
                        sweep_rate = st.number_input("Sweep Rate", key=f"sweep_rate_{i}")
                    duration = st.number_input("Duration", key=f"duration_{i}")


# Every form must have a submit button.
        submitted = st.form_submit_button("Submit")
        if submitted:
            try:
                validate(form_data, schema)  # Validate form data against the schema
                st.success("Form data is valid!")
                # Assuming you have a function ot.form_data_to_graph()
                ot.form_data_to_graph(form_data, schema)
            except ValidationError as e:
                st.error(f"Validation error: {e.message}")
                
        st.write(form_data)
            
        return form_data
    
def is_numeric_content(s):
    """Checks if the string has numeric content."""
    try:
        float(s)
        return True
    except ValueError:
        return False

def detect_header_lines(file_like_object):
    lines = file_like_object.readlines()
    
    header_end_line = None
    for index, line in enumerate(lines):
        decoded_line = line.decode('utf-8').strip()

        if not decoded_line or all(c in [',', ' '] for c in decoded_line):  # If line is empty or only commas/spaces
            header_end_line = index  # Still consider it as part of the header
            continue
        
        values = [value.strip() for value in decoded_line.split(",")]

        # Technique 1: Check for typical header keywords
        if any(keyword in decoded_line for keyword in ["TesterID", "Channel Number", "TestName", "StartDateTime", "Comment", "Volt", "Amp", "Time"]):
            header_end_line = index

        # Technique 2: Check if majority of values in a row are numeric or not
        elif sum([is_numeric_content(value) for value in values]) > len(values) / 2:
            return header_end_line + 1 if header_end_line is not None else index  # Return the next line after the last header keyword or empty line
    
    # In case no data lines were detected, return the total line count
    return len(lines)

def time_string_to_seconds(value):
    if isinstance(value, str):
        try:
            # Initialize days to 0
            days = 0
            
            # Check if there's a day term in the string
            if 'd' in value:
                days_str, time_str = value.split('d')
                days = float(days_str.strip())
            else:
                time_str = value
            
            # Extract hours, minutes, and seconds
            hours, minutes, seconds = map(float, time_str.split(':'))
            
            # Calculate total time in seconds
            total_seconds = days * 86400 + hours * 3600 + minutes * 60 + seconds
            
            return total_seconds
        except ValueError:
            return value  # return original value if not a time string
    else:
        return value  # return original value if not a string

def csv_to_sql(uploaded_file):
    
    df_form = pd.DataFrame()
    df_cycle = pd.DataFrame()
    df_stats = pd.DataFrame()
    
    namespace = "http://w3id.org/heu-intelligent#"

    # Create a dictionary to hold 3-digit labels to TestURIs mappings
    testURI_dict = {}
    
    filename= uploaded_file.name
    
    match = re.search(r'- (\d{3})', filename)
    if match:
        three_digit_label = match.group(1)
    else:
        three_digit_label = None
   
    # Check if this three-digit label already has a test_uri
    if three_digit_label in testURI_dict:
        test_uri = testURI_dict[three_digit_label]
    else:
        test_uri = namespace + str(uuid.uuid4())
        if three_digit_label is not None:
            testURI_dict[three_digit_label] = test_uri
    
    maccor_dict = {
        "Cycle": "Cycle",
        "Test Time": "TestTime",
        "Current": "Current",
        "Voltage": "CellVoltage",
        "AH-IN": "ChargeCapacity",
        "AH-OUT": "DischargeCapacity",
        "WH-IN": "ChargeEnergy",
        "WH-OUT": "DischargeEnergy",
        "Rec#": "Record",
        "Cyc#": "Cycle",
        "Amp-hr": "Capacity",
        "Watt-hr": "Energy",
        "Amps": "Current",
        "Volts": "CellVoltage"
        }
    
    cell_dict = {
        "3": "https://rdf.heuintelligent.eu/efd9fb3d-0f04-510b-98ca-2007996c44eb",
        "4": "https://rdf.heuintelligent.eu/cdea972f-8db1-074d-2d52-2fabd59c0cdd",
        "5": "https://rdf.heuintelligent.eu/a013ae7f-212e-9202-9bdb-3cd3716d9962",
        "6": "https://rdf.heuintelligent.eu/91d05731-9de1-830e-4bf2-cfc424d78306",
        "7": "https://rdf.heuintelligent.eu/dd8bfe62-2e67-5d68-0836-6089df8215af",
        "8": "https://rdf.heuintelligent.eu/3a0cae34-4f53-7de1-6ece-bb16fba760b1"
        }
    
    cycle_series_names = ["Filename", "TestURI", "CellURI", "RecordURI", 
                          "Cycle", "ChargeCapacity", "DischargeCapacity", 
                          "SpecificChargeCapacity", "SpecificDischargeCapacity",
                          "CoulombicEfficiency", "ChargeEnergy", "DischargeEnergy",
                          "SpecificChargeEnergy", "SpecificDischargeEnergy",
                          "ConstantCurrentChargeCapacity", "ConstantCurrentChargePercentage", 
                          "ConstantCurrentDischargeCapacity", "ConstantCurrentDischargePercentage"]
    
    time_series_names = ["Filename", "TestURI", "CellURI", "RecordURI", 
                          "Cycle", "Step", "Record", "StepDuration", "StepTime",
                          "TestTime", "CellVoltage", "Current",
                          "Capacity", "SpecificCapacity", "Energy", "SpecificEnergy"]
    
    batteries = fetch_batteries_from_blazegraph()
    battery_names = [st.session_state.uri_label_dict[uri] for uri in batteries if uri in st.session_state.uri_label_dict]
    selected_battery = st.selectbox("Select Battery", battery_names)
    cell_uri = st.session_state.label_uri_dict[selected_battery]
    
    
    # Perform actions based on the filename
    if '[STATS]' in filename:
        nothing = True
        print(f"Performing '[STATS]' action on {filename}")
        TABLE_NAME = 'stats'
        # Your '[STATS]' action code here
        # Load the file into a Pandas DataFrame
        df = pd.read_csv(uploaded_file, skiprows=8, usecols=range(9))
        df = df.applymap(time_string_to_seconds)
        df.rename(columns=maccor_dict, inplace=True)
        #cell_number = filename.split("#")[-1].split("_")[0]

        df['Filename'] = filename
        df["TestURI"] = test_uri
        df['RecordURI'] = df.apply(lambda x: namespace + str(uuid.uuid4()), axis=1)
        df['CellURI'] = cell_uri
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        df.drop('Cycle Type', axis=1, inplace=True)

        # Define the new order of columns
        cols_to_move = ['Filename', 'TestURI', 'RecordURI', 'CellURI']
        new_cols = cols_to_move + [col for col in df.columns if col not in cols_to_move]
        
        # Reorder the columns
        df = df[new_cols]
        
    elif 'cycle' in filename:
        TABLE_NAME = 'cycle'
        print(f"Performing 'cycle' action on {filename}")
        # Your 'cycle' action code heret
        # Load the file into a Pandas DataFrame
        df = pd.read_csv(uploaded_file, skiprows=2)
        df = df.applymap(time_string_to_seconds)
        df.rename(columns=maccor_dict, inplace=True)
        cell_number = filename.split("#")[-1].split("_")[0]

        df['Filename'] = filename
        df["TestURI"] = test_uri
        df['RecordURI'] = df.apply(lambda x: namespace + str(uuid.uuid4()), axis=1)
        df['CellURI'] = cell_uri
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]


        # Define the new order of columns
        cols_to_move = ['Filename', 'TestURI', 'RecordURI', 'CellURI']
        new_cols = cols_to_move + [col for col in df.columns if col not in cols_to_move]
        
        # Reorder the columns
        df = df[new_cols]

        
    elif 'form' in filename:
        TABLE_NAME = 'form'
        #print(f"Performing 'form' action on {filename}")
        # Your 'form' action code here
        # Load the file into a Pandas DataFrame
        df = pd.read_csv(uploaded_file, skiprows=2)
        df = df.applymap(time_string_to_seconds)
        df.rename(columns=maccor_dict, inplace=True)
        cell_number = filename.split("#")[-1].split("_")[0]
        
        df['Filename'] = filename
        df["TestURI"] = test_uri
        df['RecordURI'] = df.apply(lambda x: namespace + str(uuid.uuid4()), axis=1)
        df['CellURI'] = cell_dict[cell_number]
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

        # Define the new order of columns
        cols_to_move = ['Filename', 'TestURI', 'RecordURI', 'CellURI']
        new_cols = cols_to_move + [col for col in df.columns if col not in cols_to_move]
        
        # Reorder the columns
        df = df[new_cols]

    else:
        print(f"No specific action for {filename}")
        
    # Optionally, save the modified DataFrame back to a CSV file
    # df.to_csv(file_path, index=False)
    pause = 1
    
    if '[STATS]' in filename:
        df_stats = pd.concat([df_stats, df], ignore_index=True)
    elif 'cycle' in filename:
        df_cycle = pd.concat([df_cycle, df], ignore_index=True)
    elif 'form' in filename:
        df_form = pd.concat([df_form, df], ignore_index=True)
        
    df.columns = df.columns.str.lower()
    st.write(df)
    
    if st.button("Send to SQL"):
        db_params = {
            "dbname": "heu-intelligent",
            "user": "postgres",
            "password": "battery2023",
            "host": "localhost",
            "port": "5432"
        }
        
        # Create a PostgreSQL connection
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        
        # Use StringIO to simulate a file object
        sio = StringIO()
        sio.write(df.to_csv(index=False, header=False))
        sio.seek(0)
        
        # Copy data into the database
        try:
            # Copy data into the database
            with conn.cursor() as cur:
                cur.copy_from(sio, TABLE_NAME, columns=df.columns, sep=',')
                conn.commit()
            st.success("Data successfully committed to the database!")
        except Exception as e:
            st.error(f"An error occurred: {e}")
        finally:
            conn.close()
    
    

    
