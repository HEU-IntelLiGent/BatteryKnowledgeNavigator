import streamlit as st
import json
from pathlib import Path
from tools import data_tools as dt
from tools import ontology_tools as ot

st.set_page_config(layout="wide")


st.markdown("# New Entry")
st.sidebar.markdown("# New Entry")

if "uri_label_dict" not in st.session_state:
    st.session_state.label_uri_dict, st.session_state.uri_label_dict = ot.build_dict()

schema_directory = Path(__file__).resolve().parent.parent / "data" / "schema"

# Entry types whose form is generated from a JSON schema
schema_files = {
    "Active Material": "ActiveMaterial.schema.json",
    "Binder": "Binder.schema.json",
    "Conductive Additive": "ConductiveAdditive.schema.json",
    "Current Collector": "CurrentCollector.schema.json",
    "Electrode": "Electrode.schema.json",
    "Electrolyte": "Electrolyte.schema.json",
    "Separator": "Separator.schema.json",
    "Pouch Cell": "PouchCell.schema.json",
}

entry_type = st.selectbox(
    'What type of entry would you like to add?',
    ('Active Material', 'Binder', 'Conductive Additive', 'Current Collector',
     'Electrode', 'Electrolyte', 'Separator', 'Pouch Cell',
     'Coin Cell', 'Test Procedure', 'Dataset'))

if entry_type in schema_files:
    with open(schema_directory / schema_files[entry_type]) as schema_file:
        schema = json.load(schema_file)

    form_data = dt.schema_to_form(schema)

elif entry_type == "Coin Cell":
    st.info("Coin cell entries are not implemented yet.")

elif entry_type == "Dataset":
    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None:
        dt.csv_to_sql(uploaded_file)

elif entry_type == "Test Procedure":
    with open(schema_directory / "TestProtocol.schema.json") as schema_file:
        protocol_schema = json.load(schema_file)

    if 'num_steps' not in st.session_state:
        st.session_state.num_steps = 1
    st.session_state.num_steps = st.number_input("Number of steps", min_value=1, value=st.session_state.num_steps, step=1)

    if st.button("Setup Steps"):
        st.experimental_rerun()

    with st.form("protocol_form"):
        form_data = {}

        form_data["protocol_name"] = st.text_input("Protocol Name", "")
        form_data["steps"] = []

        for i in range(st.session_state.num_steps):
            with st.expander(f"Step {i+1}"):
                step_data = {}
                # Add a unique key for the selectbox
                step_data["type"] = st.selectbox("Step Type", ["constant current", "constant voltage", "linear voltage sweep"], key=f"step_type_{i}")
                step_data["parameters"] = {}

                if step_data["type"] == "constant current":
                    # Add a unique key for the number_input
                    step_data["parameters"]["current"] = st.number_input("Current", key=f"current_{i}")

                elif step_data["type"] == "constant voltage":
                    # Add unique keys for the number_inputs
                    step_data["parameters"]["upper_cutoff_voltage"] = st.number_input("Upper Cutoff Voltage", key=f"upper_cutoff_voltage_{i}")
                    step_data["parameters"]["lower_cutoff_voltage"] = st.number_input("Lower Cutoff Voltage", key=f"lower_cutoff_voltage_{i}")

                elif step_data["type"] == "linear voltage sweep":
                    # Add a unique key for the number_input
                    step_data["parameters"]["sweep_rate"] = st.number_input("Sweep Rate", key=f"sweep_rate_{i}")

                # Add a unique key for the number_input
                step_data["parameters"]["duration"] = st.number_input("Duration", key=f"duration_{i}")

                form_data["steps"].append(step_data)

        if st.form_submit_button("Submit"):
            # Process and validate the form data
            st.write(form_data)
            # You can also validate the form_data against the schema
