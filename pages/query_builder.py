import streamlit as st
from tools import ontology_tools as ot
from SPARQLWrapper import SPARQLWrapper, JSON

st.markdown("# Page 2 ❄️")
st.sidebar.markdown("# Page 2 ❄️")



# Define the endpoint
sparql = SPARQLWrapper("https://query.wikidata.org/sparql")

def get_classes():
    query = """
    SELECT DISTINCT ?class ?label WHERE {
      ?class a owl:Class .
      ?class rdfs:label ?label .
      FILTER(LANG(?label) = "en")
    }
    LIMIT 100
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return {result["label"]["value"]: result["class"]["value"] for result in results["results"]["bindings"]}

def get_properties(class_uri):
    query = f"""
    SELECT DISTINCT ?property ?label WHERE {{
      ?property a owl:ObjectProperty .
      ?subject ?property ?object .
      ?subject a <{class_uri}> .
      ?property rdfs:label ?label .
      FILTER(LANG(?label) = "en")
    }}
    LIMIT 100
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return {result["label"]["value"]: result["property"]["value"] for result in results["results"]["bindings"]}

# Streamlit UI
class_choice = st.selectbox("Choose a class:", list(get_classes().keys()))
chosen_class_uri = get_classes()[class_choice]

property_choice = st.selectbox("Choose a property:", list(get_properties(chosen_class_uri).keys()))
chosen_property_uri = get_properties(chosen_class_uri)[property_choice]

value_input = st.text_input("Specify a value:")

if st.button("Build Query"):
    constructed_query = f"""
    SELECT ?item ?itemLabel WHERE {{
      ?item a <{chosen_class_uri}> .
      ?item <{chosen_property_uri}> "{value_input}" .
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
    }}
    """
    st.text_area("Constructed SPARQL Query:", constructed_query)
