import streamlit as st
from pathlib import Path
import json
import uuid
import datetime
import pandas as pd
from tools import ontology_tools as ot
from tools import data_tools as dt
from tools import page_tools as pt

import streamlit as st
from rdflib import Graph, Namespace, RDF

import psutil
import os

def get_memory_usage():
    pid = os.getpid()  # Get process ID of the current process
    py = psutil.Process(pid)
    memory_use = py.memory_info()[0] / 2. ** 30  # Convert bytes to GB
    return memory_use



# Set the page configuration to wide view
st.set_page_config(layout="wide")
#ot.sanitize_blazegraph()


namespace = "https://w3id.org/heu-intelligent#"

st.markdown("# Explorer")
st.sidebar.markdown("# Explorer")

st.session_state.label_uri_dict, st.session_state.uri_label_dict = ot.build_dict()
#st.session_state.choices = list(st.session_state.label_uri_dict.keys())
#st.write(f"Current memory usage: {get_memory_usage():.2f} GB")


options = st.multiselect(
    'What are you searching for?',
    list(st.session_state.label_uri_dict.keys()), 'Battery')

# if st.button("Create new entry"):
#     subj, temp_label = ot.create_template_triple(namespace)
#     st.session_state.options.append(temp_label)
#     st.write(options)
    

tabs = st.tabs(options)

for index, tab in enumerate(tabs):
    with tab:
        uri = st.session_state.label_uri_dict[options[index]]
        pt.show_entry(uri)


#st.write('You selected:', uri)

# # Streamlit app
# def main():
#     g, st.session_state.label_uri_dict, st.session_state.uri_label_dict = ot.load_battinfo()
    
#     st.title("RDF Graph Search App")

#     # Initialize session state if it doesn't exist
#     if 'search_term' not in st.session_state:
#         st.session_state.search_term = []
    
#     search_term = st.multiselect(
#         'What are you looking for?',
#         st.session_state.label_uri_dict.keys()
#     )
    
#     # Update session state with selected search terms
#     st.session_state.search_term = search_term
    
#     # Use the selected search terms from session state
#     if st.session_state.search_term:
#         st.write("Selected search terms:", st.session_state.search_term)

#     # st.title("RDF Graph Search App")
    
#     # search_term = st.multiselect(
#     # 'What are you looking for?',
#     # st.session_state.label_uri_dict.keys())
#     # if search_term:
#     #     uri = st.session_state.label_uri_dict[search_term]
#     #     st.write(f"URI: {uri}")


# if __name__ == "__main__":
#     main()