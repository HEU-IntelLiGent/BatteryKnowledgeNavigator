from rdflib import Graph, URIRef, Namespace, Literal
from rdflib.namespace import RDF, RDFS, SKOS, OWL, XSD
import streamlit as st
import uuid
import pandas as pd
from SPARQLWrapper import SPARQLWrapper, JSON, POST, DELETE, INSERT
import os

@st.cache_data
def open_blazegraph_endpoint():
    blazegraph_url = "http://localhost:9999/blazegraph/sparql"
    
    # Create a SPARQLWrapper instance and set the endpoint
    sparql = SPARQLWrapper(blazegraph_url)
    
    return sparql

def clear_cache():
    st.cache_data.clear()

@st.cache_data
def sanitize_blazegraph():
    # Step 1: Extract data from Blazegraph
    sparql = SPARQLWrapper("http://localhost:9999/blazegraph/sparql")
    query = "SELECT ?s ?p ?o WHERE { ?s ?p ?o }"
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    
    # Step 1: Extract and delete offending triples from Blazegraph
    sparql = SPARQLWrapper("http://localhost:9999/blazegraph/sparql")
    delete_query = """
    DELETE WHERE {
      ?s ?p ?o .
      FILTER (CONTAINS(?o, "\\r\\n"))
    }
    """
    sparql.setQuery(delete_query)
    sparql.setMethod(DELETE)
    sparql.query()
    
    # Step 2: Process and sanitize the data
    sanitized_data = []
    for result in results["results"]["bindings"]:
        subject = result["s"]["value"]
        predicate = result["p"]["value"]
        object_value = result["o"]["value"].replace("\r\n", " ")  # Replace problematic characters
        sanitized_data.append((subject, predicate, object_value))
    
    # Step 3: Insert the sanitized data back into Blazegraph
    for subject, predicate, object_value in sanitized_data:
        insert_query = f'INSERT DATA {{ <{subject}> <{predicate}> "{object_value}" }}'
        sparql.setQuery(insert_query)
        sparql.method = "POST"
        sparql.query()

@st.cache_data
def build_dict():

    sparql = open_blazegraph_endpoint()
    
    # Set the SPARQL query
    query_prefLabel = """
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    SELECT ?subject ?label
    WHERE {
        ?subject skos:prefLabel ?label .
    }
    """
    sparql.setQuery(query_prefLabel)
    sparql.setReturnFormat(JSON)
    
    # Create a dictionary to hold the mappings
    label_uri_dict = {}
    uri_label_dict = {}
    
    # Execute the query and print the results
    results = sparql.query().convert()
    for result in results["results"]["bindings"]:
        prefLabel = result["label"]["value"]
        uri = result["subject"]["value"]
        label_uri_dict[prefLabel] = uri
        uri_label_dict[str(uri)] = prefLabel
            
    query_label = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?subject ?label
    WHERE {
        ?subject rdfs:label ?label .
    }
    """
    
    sparql.setQuery(query_label)
    sparql.setReturnFormat(JSON)
    
    # Execute the query and print the results
    results = sparql.query().convert()
    
    for result in results["results"]["bindings"]:
        label = result["label"]["value"]
        uri = result["subject"]["value"]
        label_uri_dict[label] = uri
        uri_label_dict[str(uri)] = label
        
    # Construct the SPARQL query
    query = '''
        SELECT DISTINCT ?predicate
        WHERE {
            ?s ?predicate ?o
            FILTER(STRSTARTS(STR(?predicate), "http://www.w3.org/2004/02/skos/core#"))
        }
    '''
    
    # Set the query and response format
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    
    # Execute the query
    results = sparql.query().convert()
    
    # Create a dictionary to store the SKOS predicates
    skos_predicates = {}
    
    # Extract and process the results
    for result in results["results"]["bindings"]:
        predicate_uri = result["predicate"]["value"]
        predicate_label = "skos:" + predicate_uri.split("#")[-1]
        label_uri_dict[predicate_label] = predicate_uri
        uri_label_dict[str(predicate_uri)] = predicate_label
        
    # Construct the SPARQL query
    query = '''
        SELECT DISTINCT ?predicate
        WHERE {
            ?s ?predicate ?o
            FILTER(STRSTARTS(STR(?predicate), "http://purl.org/dc/terms/"))
        }
    '''
    
    # Set the query and response format
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    
    # Execute the query
    results = sparql.query().convert()
    
    # Create a dictionary to store the SKOS predicates
    skos_predicates = {}
    
    # Extract and process the results
    for result in results["results"]["bindings"]:
        predicate_uri = result["predicate"]["value"]
        predicate_label = os.path.basename(predicate_uri)
        label_uri_dict[predicate_label] = predicate_uri
        uri_label_dict[str(predicate_uri)] = predicate_label
        
    # Construct the SPARQL query
    query = '''
        SELECT DISTINCT ?predicate
        WHERE {
            ?s ?predicate ?o
            FILTER(STRSTARTS(STR(?predicate), "http://www.w3.org/2002/07/owl#"))
        }
    '''
    
    # Set the query and response format
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    
    # Execute the query
    results = sparql.query().convert()
    
    # Create a dictionary to store the SKOS predicates
    skos_predicates = {}
    
    # Extract and process the results
    for result in results["results"]["bindings"]:
        predicate_uri = result["predicate"]["value"]
        predicate_label = "owl:" + predicate_uri.split("#")[-1]
        label_uri_dict[predicate_label] = predicate_uri
        uri_label_dict[str(predicate_uri)] = predicate_label
        
    # Construct the SPARQL query
    query = '''
        SELECT DISTINCT ?predicate
        WHERE {
            ?s ?predicate ?o
            FILTER(STRSTARTS(STR(?predicate), "http://www.w3.org/2000/01/rdf-schema#"))
        }
    '''
    
    # Set the query and response format
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    
    # Execute the query
    results = sparql.query().convert()
    
    # Create a dictionary to store the SKOS predicates
    skos_predicates = {}
    
    # Extract and process the results
    for result in results["results"]["bindings"]:
        predicate_uri = result["predicate"]["value"]
        predicate_label = "rdfs:" + predicate_uri.split("#")[-1]
        label_uri_dict[predicate_label] = predicate_uri
        uri_label_dict[str(predicate_uri)] = predicate_label
        
    # Construct the SPARQL query
    query = '''
        SELECT DISTINCT ?predicate
        WHERE {
            ?s ?predicate ?o
            FILTER(STRSTARTS(STR(?predicate), "http://www.w3.org/1999/02/22-rdf-syntax-ns#"))
        }
    '''
    
    # Set the query and response format
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    
    # Execute the query
    results = sparql.query().convert()
    
    # Create a dictionary to store the SKOS predicates
    skos_predicates = {}
    
    # Extract and process the results
    for result in results["results"]["bindings"]:
        predicate_uri = result["predicate"]["value"]
        predicate_label = "rdf:" + predicate_uri.split("#")[-1]
        label_uri_dict[predicate_label] = predicate_uri
        uri_label_dict[str(predicate_uri)] = predicate_label
            
    return label_uri_dict, uri_label_dict
        


def get_prefLabel(sparql, term_uri):

    # Query for the prefLabel of the given term
    query_text = f"""
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    SELECT ?label
    WHERE {{
    <{term_uri}> skos:prefLabel ?label .
    }}
    """
    sparql.setQuery(query_text)
    sparql.setReturnFormat(JSON)
    
    # Execute the query and print the results
    results = sparql.query().convert()
    
    for result in results["results"]["bindings"]:
        label = result["label"]["value"]
        return label
    
def get_elucidation(sparql, term_uri):
    
    # Query for the elucidation of the given term
    query_text = f"""
    PREFIX emmo: <http://emmo.info/emmo#>
    SELECT ?elucidation
    WHERE {{
    <{term_uri}> emmo:EMMO_967080e5_2f42_4eb2_a3a9_c58143e835f9 ?elucidation .
    }}
    """
    sparql.setQuery(query_text)
    sparql.setReturnFormat(JSON)
    
    # Execute the query and print the results
    results = sparql.query().convert()
    
    for result in results["results"]["bindings"]:
        elucidation = result["elucidation"]["value"]
        return elucidation
    
def retrieve_existing_data():
    sparql = open_blazegraph_endpoint()
    query = "SELECT ?subj ?pred ?obj WHERE {?subj ?pred ?obj}"
    
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    query_result = sparql.query().convert()
    
    return query_result["results"]["bindings"]

def filter_new_triples(data_frame, existing_data):
    # Compare triples and filter out existing ones
    new_triples = []
    for index, row in data_frame.iterrows():
        if not triple_exists(row, existing_data):
            new_triples.append(row)
    return new_triples

def triple_exists(triple, existing_data):
    for existing_triple in existing_data:
        existing_subject = existing_triple["subj"]["value"]
        existing_predicate = existing_triple["pred"]["value"]
        existing_object = existing_triple["obj"]["value"]
        if (triple["subj"] == existing_subject and
            triple["pred"] == existing_predicate and
            triple["obj"] == existing_object):
            return True
    return False

def insert_new_data(new_triples):
    st.write(new_triples)
    sparql = open_blazegraph_endpoint()
    for triple in new_triples:
        subject = triple["subj"]
        predicate = triple["pred"]
        obj = triple["obj"]
        obj_type = triple["obj_type"]
        
        # Construct and execute INSERT query
        if obj_type == "literal":
            insert_query = f'''INSERT DATA {{ <{subject}> <{predicate}> "{obj}" }}'''
        else:
            insert_query = f"INSERT DATA {{ <{subject}> <{predicate}> <{obj}> }}"
            
        st.write(insert_query)
        sparql.setMethod(POST)
        sparql.setQuery(insert_query)
        sparql.query()
        
def remove_triples_from_blazegraph(triples_dataframe):
    sparql = open_blazegraph_endpoint()

    for index, row in triples_dataframe.iterrows():
        subject = row["subj"]
        predicate = row["pred"]
        obj = row["obj"]
        obj_type = row["obj_type"]
        
        # Construct DELETE query and execute it
        delete_query = f'''DELETE WHERE {{ <{subject}> <{predicate}> ?o }}'''
        # if obj_type == "literal":
        #     delete_query = f'''DELETE DATA {{ <{subject}> <{predicate}> "{obj}" }}'''
        # else:
        #     delete_query = f'''DELETE DATA {{ <{subject}> <{predicate}> <{obj}> }}'''
        st.write(delete_query)
        sparql.setMethod(DELETE)
        sparql.setQuery(delete_query)
        # Execute the query and check the response
        response = sparql.query()
        response_code = response.response.getcode()
        
        if response_code == 200:
            st.write("Query executed successfully")
        else:
            st.write("Query execution failed")
            
def synchronize_with_blazegraph(existing_df_uri, mod_df_uri):
    sparql = open_blazegraph_endpoint()
    
    #st.write(existing_df_uri)
    
    # Generate SPARQL DELETE queries for triples in existing_df_uri
    delete_queries = []
    for index, row in existing_df_uri.iterrows():
        if row["obj_type"] == "literal":
            if row["obj_lang"] is not None:  # Check if object is a literal with a language tag
                delete_query = f'''DELETE DATA {{ <{row['subj']}> <{row['pred']}> "{row['obj']}" @{row['obj_lang']} }}'''
            else:
                delete_query = f'''DELETE DATA {{ <{row['subj']}> <{row['pred']}> "{row['obj']}" }}'''
        delete_queries.append(delete_query)

    # Generate SPARQL INSERT queries for triples in mod_df_uri
    insert_queries = []
    for index, row in mod_df_uri.iterrows():
        if row["obj_type"] == "literal":
            if row["obj_lang"] is not None:  # Check if object is a literal with a language tag
                insert_query = f'''INSERT DATA {{ <{row['subj']}> <{row['pred']}> "{row['obj']}" @{row['obj_lang']} }}'''
            else:
                insert_query = f'''INSERT DATA {{ <{row['subj']}> <{row['pred']}> "{row['obj']}" }}'''
        insert_queries.append(insert_query)

    # Execute DELETE queries
    for delete_query in delete_queries:
        sparql.setMethod(DELETE)
        sparql.setQuery(delete_query)
        #st.write(delete_query)
        # Execute the query and check the response
        response = sparql.query()
        response_code = response.response.getcode()
        
        # if response_code == 200:
        #     st.write("Query executed successfully")
        # else:
        #     st.write("Query execution failed")

    # Execute INSERT queries
    for insert_query in insert_queries:
        sparql.setQuery(insert_query)
        #st.write(insert_query)
        sparql.method = INSERT
        response = sparql.query()
        response_code = response.response.getcode()
        
        # if response_code == 200:
        #     st.write("Query executed successfully")
        # else:
        #     st.write("Query execution failed")
    
def get_annotation_properties(term_uri):
    
    sparql = open_blazegraph_endpoint()
    
    # Query for the elucidation of the given term
    query_text = f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    
    SELECT ?pred ?obj
    WHERE {{
        <{term_uri}> ?pred ?obj .
        ?pred rdf:type owl:AnnotationProperty .
    }}
    """
    sparql.setQuery(query_text)
    sparql.setReturnFormat(JSON)
    
    # Execute the query and print the results
    results = sparql.query().convert()
    
    return results

def get_object_properties(term_uri):
    
    sparql = open_blazegraph_endpoint()
    
    # Query for the elucidation of the given term
    query_text = f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    
    SELECT ?pred ?obj
    WHERE {{
        <{term_uri}> ?pred ?obj .
        ?pred rdf:type owl:ObjectProperty .
    }}
    """
    sparql.setQuery(query_text)
    sparql.setReturnFormat(JSON)
    
    # Execute the query and print the results
    results = sparql.query().convert()
    
    return results

def get_named_individuals(term_uri):
    
    sparql = open_blazegraph_endpoint()
    
    # Query for the elucidation of the given term
    query_text = f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    
    SELECT ?subj
    WHERE {{
        ?subj rdf:type <{term_uri}> .
        ?subj rdf:type owl:NamedIndividual .
    }}
    """
    sparql.setQuery(query_text)
    sparql.setReturnFormat(JSON)
    
    # Execute the query and print the results
    results = sparql.query().convert()
    
    return results

    
def form_data_to_graph(form_data, schema):
    
    namespace = "http://w3id.org/heu-intelligent#"
    subject_uri = create_uri(namespace)
    #label_uri_dict, uri_label_dict = build_dict()
    
    # Load the JSON Schema
    schema_definitions = schema.get("definitions", {})
    properties = schema.get("properties", {})
    
    
    # Define the global type of the data
    for ids in schema.get("rdf_id", {}):
        add_triple(subject_uri, RDF.type, URIRef(ids))
        st.write("Added Type")
    
    # Iterate through the properties and create RDF triples
    for property_name, property_details in properties.items():
        rdf_type = property_details.get("rdf_type")
        rdf_id = property_details.get("rdf_id")
        unit_id = property_details.get("unit_id")
        
        if property_details.get('type') == 'array':
            # Handle array properties
            for item in form_data.get(property_name, []):
                #st.write(item)
                rdf_type = property_details.get("rdf_type")
                rdf_id = property_details.get("rdf_id")
                unit_id = property_details.get("unit_id")
                # Each item in the array can be treated as an entity
                # Create a new URI for this entity
                entity_uri = create_uri(namespace)
                
                # Add triple linking main subject to this entity
                add_triple(subject_uri, URIRef(rdf_id), entity_uri)
                
                for key, value in item.items():
                    # For simplicity, let's handle only two known keys: compound and amount
                    st.write(key)
                    if properties[property_name]["items"]["properties"][key]["rdf_type"] == "owl:ObjectProperty":
                        subject = URIRef(entity_uri)
                        predicate = URIRef(properties[property_name]["items"]["properties"][key]["rdf_id"])
                        compound_rdf_id = properties[property_name]["items"]["properties"][key]["rdf_id"]
                        object_value = item[key]
                        add_triple(subject, predicate, object_value)
                    elif properties[property_name]["items"]["properties"][key]["rdf_type"] == "emmo:QuantitativeProperty":
                        quantity_value = item[key]
                        if quantity_value is not None:
                            rdf_id = properties[property_name]["items"]["properties"][key]["rdf_id"]
                            label = key #property_details.get("skos:prefLabel")
                            unit_id = properties[property_name]["items"]["properties"][key]["unit_id"]
                            
                            hasObjectiveProperty = URIRef("http://emmo.info/emmo#EMMO_0aa934ee_1ad4_4345_8a7f_bc73ec67c7e5")
                            hasNumericPart = URIRef("http://emmo.info/emmo#EMMO_8ef3cd6d_ae58_4a8d_9fc0_ad8f49015cd0")
                            hasNumericalValue = URIRef("http://emmo.info/emmo#EMMO_faf79f53_749d_40b2_807c_d34244c192f4")
                            hasReferencePart = URIRef("http://emmo.info/emmo#EMMO_eeb06032_dd4f_476e_9da6_aa24302b7588")
                            Real = URIRef("http://emmo.info/emmo#EMMO_18d180e4_5e3e_42f7_820c_e08951223486")
                            
                            # Generate new URIs
                            new_property_id = create_uri(namespace)
                            new_numeric_part_id = create_uri(namespace)
                                            
                            # Add triples for QuantitativeProperty
                            add_triple(entity_uri, hasObjectiveProperty, new_property_id)
                            add_triple(new_property_id, RDF.type, URIRef(rdf_id))
                            add_triple(new_property_id, SKOS.prefLabel, Literal(label))
                            add_triple(new_property_id, hasNumericPart, new_numeric_part_id)
                            add_triple(new_numeric_part_id, RDF.type, Real)
                            add_triple(new_numeric_part_id, hasNumericalValue, Literal(quantity_value["value"], datatype=XSD.float))
                            add_triple(new_property_id, hasReferencePart, URIRef(unit_id))
        
        elif rdf_type == "owl:ObjectProperty" or rdf_type == "owl:DatatypeProperty":
            value = form_data.get(property_name)
            if value is not None:
                if rdf_id:
                    subject = URIRef(subject_uri)
                    predicate = URIRef(rdf_id)
                    if rdf_type == "owl:DatatypeProperty":
                        object_value = Literal(value)
                    else:
                        object_value = st.session_state.label_uri_dict.get(value, URIRef(value))#URIRef(value)  # Assuming value is a valid URI
                    
                    if predicate == SKOS.prefLabel:
                        st.session_state.uri_label_dict[str(subject)] = str(object_value)
                        st.session_state.label_uri_dict[str(object_value)] = str(subject)
                    
                    add_triple(subject, predicate, object_value)
                    
        elif rdf_type == "emmo:QuantitativeProperty":
            quantity_value = form_data.get(property_name)
            if quantity_value is not None:
                rdf_id = property_details.get("rdf_id")
                label = property_name #property_details.get("skos:prefLabel")
                
                hasObjectiveProperty = URIRef("http://emmo.info/emmo#EMMO_0aa934ee_1ad4_4345_8a7f_bc73ec67c7e5")
                hasNumericPart = URIRef("http://emmo.info/emmo#EMMO_8ef3cd6d_ae58_4a8d_9fc0_ad8f49015cd0")
                hasNumericalValue = URIRef("http://emmo.info/emmo#EMMO_faf79f53_749d_40b2_807c_d34244c192f4")
                hasReferencePart = URIRef("http://emmo.info/emmo#EMMO_eeb06032_dd4f_476e_9da6_aa24302b7588")
                Real = URIRef("http://emmo.info/emmo#EMMO_18d180e4_5e3e_42f7_820c_e08951223486")
                
                # Generate new URIs
                new_property_id = create_uri(namespace)
                new_numeric_part_id = create_uri(namespace)
                                
                # Add triples for QuantitativeProperty
                add_triple(subject_uri, hasObjectiveProperty, new_property_id)
                add_triple(new_property_id, RDF.type, URIRef(rdf_id))
                add_triple(new_property_id, SKOS.prefLabel, Literal(label))
                add_triple(new_property_id, hasNumericPart, new_numeric_part_id)
                add_triple(new_numeric_part_id, RDF.type, Real)
                add_triple(new_numeric_part_id, hasNumericalValue, Literal(quantity_value["value"], datatype=XSD.float))
                add_triple(new_property_id, hasReferencePart, URIRef(unit_id))
                
    st.cache_data.clear()
    st.session_state.label_uri_dict, st.session_state.uri_label_dict = build_dict()
        

def triples_to_df(g, uri):
    object_properties = []
    annotation_properties = []
    datatype_properties = []
    
    # Query the graph for triples where the given URI is the subject
    triples = list(g.triples((uri, None, None)))
    
    # Convert triples to a Pandas DataFrame
    for triple in triples:
    
        subject, predicate, obj = triple
        predicate_type = g.value(predicate, URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"))
        
        if predicate_type == URIRef("http://www.w3.org/2002/07/owl#ObjectProperty"):
            object_properties.append({"subject": subject, "predicate": predicate, "object": obj})
        elif predicate_type == URIRef("http://www.w3.org/2002/07/owl#AnnotationProperty"):
            annotation_properties.append({"subject": subject, "predicate": predicate, "object": obj})
        elif predicate_type == URIRef("http://www.w3.org/2002/07/owl#DatatypeProperty"):
            datatype_properties.append({"subject": subject, "predicate": predicate, "object": obj})
    
    # Convert categorized triples to Pandas DataFrames
    object_properties_df = pd.DataFrame(object_properties)
    annotation_properties_df = pd.DataFrame(annotation_properties)
    datatype_properties_df = pd.DataFrame(datatype_properties)
    
    return object_properties_df, annotation_properties_df, datatype_properties_df

def is_numeric_literal(lit):
    if not isinstance(lit, Literal):
        return False

    numeric_datatypes = {XSD.int, XSD.float, XSD.decimal, XSD.integer,
                         XSD.nonPositiveInteger, XSD.positiveInteger, 
                         XSD.nonNegativeInteger, XSD.negativeInteger}

    return lit.datatype in numeric_datatypes

def add_triple(subj, pred, obj):
    sparql = open_blazegraph_endpoint()
    
    # SPARQL INSERT query to add the new triple
    if isinstance(obj, Literal):
        if is_numeric_literal(obj):
            datatype = obj.datatype
            insert_query = f"""
                INSERT DATA {{
                    <{subj}> <{pred}> "{obj}"^^<{datatype}> .
                }}
            """
        else:
            insert_query = f"""
                INSERT DATA {{
                    <{subj}> <{pred}> "{obj}" @en .
                }}
            """
        
    else:
        insert_query = f"""
            INSERT DATA {{
                <{subj}> <{pred}> <{obj}> .
            }}
        """
    
    sparql.setQuery(insert_query)
    sparql.setMethod(INSERT)
    
    st.write(insert_query)
    
    # Execute the insert query
    response = sparql.query()
    if response.response.status == 200:
        st.write("Triple inserted successfully.")
    else:
        st.write("Error:", response.response.status)
        
def list_annotation_properties():
    sparql = open_blazegraph_endpoint()
    # SPARQL query to retrieve owl:AnnotationProperty predicate types
    query = """
    SELECT DISTINCT ?predicate
    WHERE {
      ?predicate a <http://www.w3.org/2002/07/owl#AnnotationProperty> .
    }
    """
    
    # Initialize SPARQLWrapper
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    
    # Execute the query and retrieve predicate types
    results = sparql.query().convert()
    predicate_uri = [result["predicate"]["value"] for result in results["results"]["bindings"]]
    predicate_label = []
    for uri in predicate_uri:
        if str(uri) in st.session_state.uri_label_dict:
            label = st.session_state.uri_label_dict[str(uri)]
            if label not in predicate_label:
                predicate_label.append(label)
            
    # Construct the SPARQL query
    query = '''
        SELECT DISTINCT ?predicate
        WHERE {
            ?s ?predicate ?o
            FILTER(STRSTARTS(STR(?predicate), "http://www.w3.org/2004/02/skos/core#"))
        }
    '''
    
    # Set the query and response format
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    
    # Execute the query
    results = sparql.query().convert()
    
    # Create a dictionary to store the SKOS predicates
    skos_predicates = {}
    
    # Extract and process the results
    for result in results["results"]["bindings"]:
        predicate_uri = result["predicate"]["value"]
        label = "skos:" + predicate_uri.split("#")[-1]
        if label not in predicate_label:
            predicate_label.append(label)
        
    # Construct the SPARQL query
    query = '''
        SELECT DISTINCT ?predicate
        WHERE {
            ?s ?predicate ?o
            FILTER(STRSTARTS(STR(?predicate), "http://purl.org/dc/terms/"))
        }
    '''
    
    # Set the query and response format
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    
    # Execute the query
    results = sparql.query().convert()
    
    # Extract and process the results
    for result in results["results"]["bindings"]:
        predicate_uri = result["predicate"]["value"]
        label = os.path.basename(predicate_uri)
        if label not in predicate_label:
            predicate_label.append(label)
        
    # Construct the SPARQL query
    query = '''
        SELECT DISTINCT ?predicate
        WHERE {
            ?s ?predicate ?o
            FILTER(STRSTARTS(STR(?predicate), "http://www.w3.org/2000/01/rdf-schema#"))
        }
    '''
    
    # Set the query and response format
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    
    # Execute the query
    results = sparql.query().convert()
    
    # Extract and process the results
    for result in results["results"]["bindings"]:
        predicate_uri = result["predicate"]["value"]
        label = "rdfs:" + predicate_uri.split("#")[-1]
        if label not in predicate_label:
            predicate_label.append(label)
        
    return predicate_label

@st.cache_data
def get_classes():
    sparql = open_blazegraph_endpoint()
    sparql.setQuery("""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT DISTINCT ?subj WHERE {
            ?subj rdf:type owl:Class .
        }
    """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    classes = []
    for result in results["results"]["bindings"]:
        classes.append(result["subj"]["value"])

    return classes

def create_uri(namespace):
    uri = namespace + str(uuid.uuid4())
    return uri

def how_many_temps():
    sparql = open_blazegraph_endpoint()
    query = """
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    
    SELECT (COUNT(?label) as ?count)
    WHERE {
      ?individual skos:prefLabel ?label .
      FILTER(STRSTARTS(str(?label), "TempPrefLabel"))
    }
    """
    
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    
    count = results['results']['bindings'][0]['count']['value']
    
    return count

def create_template_triple(namespace):
    count= how_many_temps()
    
    subj = create_uri(namespace)
    pred = 'http://www.w3.org/2004/02/skos/core#prefLabel'
    obj = 'TempPrefLabel'+ f'_{count}'
    obj_type = 'literal'
    obj_lang = 'en'
    
    sparql = open_blazegraph_endpoint()
    insert_query = f'''INSERT DATA {{ 
    <{subj}> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#NamedIndividual> .
    <{subj}> <{pred}> "{obj}" @{obj_lang} }}'''

    sparql.setQuery(insert_query)
    #st.write(insert_query)
    sparql.method = INSERT
    response = sparql.query()
    response_code = response.response.getcode()
    
    return subj, obj

