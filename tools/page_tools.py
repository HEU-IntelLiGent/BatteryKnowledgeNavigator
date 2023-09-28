from rdflib import Graph, URIRef, Namespace, Literal
from rdflib.namespace import RDF, RDFS, SKOS, OWL
import streamlit as st
import uuid
import pandas as pd
from SPARQLWrapper import SPARQLWrapper, JSON
from tools import ontology_tools as ot
from tools import data_tools as dt

def show_entry(uri):
    
    sparql = ot.open_blazegraph_endpoint()
    
    prefLabel = ot.get_prefLabel(sparql, uri)
    elucidation = ot.get_elucidation(sparql, uri)
    
    st.header(f"{prefLabel}")
    st.write(f"IRI: {uri}")
    st.write(f"{elucidation}")
    
    with st.expander("Annotation Properties", expanded = True):
                
        annotations = ot.get_annotation_properties(uri)
        data = []
        for binding in annotations["results"]["bindings"]:
            pred = binding["pred"]["value"]
            obj = binding["obj"]["value"]
            obj_type = binding["obj"]["type"]
            
            if binding["obj"].get("xml:lang"):
                xml_lang = binding["obj"]["xml:lang"]
            else:
                xml_lang = None
            data.append({"subj": uri, "pred": pred, "obj": obj, "obj_type": obj_type, "obj_lang": xml_lang})
            
        existing_df_uri = pd.DataFrame(data)
        
        edit_disable = not st.toggle('Edit', key = f"edit_{str(uri)}")
        existing_df_labels = dt.triple_df_uri_to_label(existing_df_uri)
        annotation_property_labels = ot.list_annotation_properties()
        mod_df_labels = st.data_editor( existing_df_labels[["pred", "obj"]], 
                                       num_rows = "dynamic", 
                                       disabled = edit_disable, 
                                       use_container_width = True,
                                       column_config={
                                        "pred": st.column_config.SelectboxColumn(
                                            "pred",
                                            help="The category of the app",
                                            options=annotation_property_labels,
                                            required=True)
                                        }
                                       )

        # Create new columns based on conditions
        mod_df_labels['subj'] = mod_df_labels['pred'].apply(lambda x: st.session_state.uri_label_dict[str(uri)]  if pd.notnull(x) else None)
        mod_df_labels['obj_type'] = mod_df_labels['pred'].apply(lambda x: 'literal'  if pd.notnull(x) else None)
        mod_df_labels['obj_lang'] = mod_df_labels['pred'].apply(lambda x: 'en'  if pd.notnull(x) else None)
        
        # Rearrange columns
        mod_df_labels = mod_df_labels[['subj', 'pred', 'obj', 'obj_type', 'obj_lang']]
        
        mod_df_uri= dt.triple_df_label_to_uri(mod_df_labels)
        
        if not edit_disable:
            ot.synchronize_with_blazegraph(existing_df_uri, mod_df_uri)
            
    with st.expander("Named Individuals", expanded = True):
                
        individuals = ot.get_named_individuals(uri)
        data = []
        for binding in individuals["results"]["bindings"]:
            subj = binding["subj"]["value"]
            pred = str(RDF.type)
            obj = str(uri)
            obj_type = "uri"
            xml_lang = None

            data.append({"subj": subj, "pred": pred, "obj": obj, "obj_type": obj_type, "obj_lang": xml_lang})
            
        existing_df_uri = pd.DataFrame(data)
        
        edit_disable = not st.toggle('Edit', key = f"edit_individuals_{str(uri)}")
        existing_df_labels = dt.triple_df_uri_to_label(existing_df_uri)
        annotation_property_labels = ot.list_annotation_properties()
        mod_df_labels = st.data_editor( existing_df_labels[["subj"]], 
                                       num_rows = "dynamic", 
                                       disabled = edit_disable, 
                                       use_container_width = True)

        # Create new columns based on conditions
        mod_df_labels['pred'] = mod_df_labels['subj'].apply(lambda x: st.session_state.uri_label_dict[str(RDF.type)]  if pd.notnull(x) else None)
        mod_df_labels['obj'] = mod_df_labels['subj'].apply(lambda x: st.session_state.uri_label_dict[str(uri)]  if pd.notnull(x) else None)
        mod_df_labels['obj_type'] = mod_df_labels['subj'].apply(lambda x: 'literal'  if pd.notnull(x) else None)
        mod_df_labels['obj_lang'] = mod_df_labels['subj'].apply(lambda x: 'en'  if pd.notnull(x) else None)
        
        # Rearrange columns
        mod_df_labels = mod_df_labels[['subj', 'pred', 'obj', 'obj_type', 'obj_lang']]
        
        mod_df_uri= dt.triple_df_label_to_uri(mod_df_labels)
        
        if not edit_disable:
            ot.synchronize_with_blazegraph(existing_df_uri, mod_df_uri)
            
            
        
def toggle_change():
    st.write("toggle")
    
@st.cache_data
def display_dataframe(df, edit_disable):
    df_new = st.data_editor(st.session_state.df[["pred", "obj"]], num_rows = "dynamic", disabled = edit_disable, use_container_width = True)
    return df_new
                
def display_triples(query_result, incl_subj = False):
    pred_col, obj_col = st.columns([1,2])
    for result in query_result["results"]["bindings"]:
        pred = result["pred"]["value"]
        if str(pred) in st.session_state.uri_label_dict:
            pred_col.write(st.session_state.uri_label_dict[str(pred)])
        else: 
            pred_col.write(str(pred))
        obj = result["obj"]["value"]
        if str(obj) in st.session_state.uri_label_dict:
            obj_col.write(st.session_state.uri_label_dict[str(obj)])
        else: 
            obj_col.write(str(obj))

