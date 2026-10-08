import streamlit as st
from tools import ontology_tools as ot
from tools import page_tools as pt


# Set the page configuration to wide view
st.set_page_config(layout="wide")

st.markdown("# Explorer")
st.sidebar.markdown("# Explorer")

st.session_state.label_uri_dict, st.session_state.uri_label_dict = ot.build_dict()

options = st.multiselect(
    'What are you searching for?',
    list(st.session_state.label_uri_dict.keys()), 'Battery')

# st.tabs needs at least one label
if options:
    tabs = st.tabs(options)

    for index, tab in enumerate(tabs):
        with tab:
            uri = st.session_state.label_uri_dict[options[index]]
            pt.show_entry(uri)
