import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from scipy import stats
from pptx import Presentation
from pptx.util import Inches
from pptx.util import Pt
from io import BytesIO
import tempfile
import os


st.markdown("# IntelLiGent Data Dashboard")

current_directory = os.getcwd()
parent_directory = os.path.dirname(current_directory)
ppt_directory = os.path.join(current_directory, 'data', 'ppt')
ppt_template_directory = os.path.join(ppt_directory, 'templates')

# PostgreSQL connection parameters
db_params = {
    "dbname": "xxxx",
    "user": "xxxx",
    "password": "xxxx",
    "host": "xxxx",
    "port": "xxxx"
}

# Create a PostgreSQL connection
conn = psycopg2.connect(**db_params)
cursor = conn.cursor()

# Function to fetch valid combinations of CellURI and TestURI
@st.cache_data
def fetch_valid_combinations(table_name):
    with conn.cursor() as cur:
        cur.execute(f"SELECT DISTINCT CellURI, TestURI FROM {table_name};")
        valid_combinations = [(row[0], row[1]) for row in cur.fetchall()]
    return valid_combinations

def fetch_unique_celluris(table_name):
    with conn.cursor() as cur:
        cur.execute(f"SELECT DISTINCT CellURI FROM {table_name};")
        cell_uris = [row[0] for row in cur.fetchall()]
    return cell_uris

cell_uri_label = {
    "https://rdf.heuintelligent.eu/efd9fb3d-0f04-510b-98ca-2007996c44eb": "IntelLiGent 3",
    "https://rdf.heuintelligent.eu/cdea972f-8db1-074d-2d52-2fabd59c0cdd": "IntelLiGent 4",
    "https://rdf.heuintelligent.eu/a013ae7f-212e-9202-9bdb-3cd3716d9962": "IntelLiGent 5",
    "https://rdf.heuintelligent.eu/91d05731-9de1-830e-4bf2-cfc424d78306": "IntelLiGent 6",
    "https://rdf.heuintelligent.eu/dd8bfe62-2e67-5d68-0836-6089df8215af": "IntelLiGent 7",
    "https://rdf.heuintelligent.eu/3a0cae34-4f53-7de1-6ece-bb16fba760b1": "IntelLiGent 8"}

cell_label_uri = {
    "IntelLiGent 3": "https://rdf.heuintelligent.eu/efd9fb3d-0f04-510b-98ca-2007996c44eb",
    "IntelLiGent 4": "https://rdf.heuintelligent.eu/cdea972f-8db1-074d-2d52-2fabd59c0cdd",
    "IntelLiGent 5": "https://rdf.heuintelligent.eu/a013ae7f-212e-9202-9bdb-3cd3716d9962",
    "IntelLiGent 6": "https://rdf.heuintelligent.eu/91d05731-9de1-830e-4bf2-cfc424d78306",
    "IntelLiGent 7": "https://rdf.heuintelligent.eu/dd8bfe62-2e67-5d68-0836-6089df8215af",
    "IntelLiGent 8": "https://rdf.heuintelligent.eu/3a0cae34-4f53-7de1-6ece-bb16fba760b1"}

# # Streamlit multi-select for selecting CellURI
cell_col1, cell_col2 = st.columns([1,8])
cell_col1.markdown("Cell", help="Cell identified by its unique name")
selected_cell_label = cell_col2.multiselect("# Cell", 
                                     list(cell_uri_label.values()),
                                     placeholder="Select a cell ID", 
                                    label_visibility="collapsed")

data_col1, data_col2 = st.columns([1,8])
data_col1.markdown("Data",
                    help="""cycle: Time series | form: Time series for formation cycles |   stats: Statistics per cycle""")
selected_table = data_col2.radio('Data', ('cycle', 'form', 'stats'), 
                          horizontal=True, 
                        label_visibility="collapsed")



# Fetch and display unique CellURIs for selection
unique_cell_uris = fetch_unique_celluris(selected_table)



selected_cell_uri = []


with st.expander("Pre-processing options"):

    col1, col2 = st.columns(2)
    eol_limit = col1.toggle('EOL', 
                        help="Calculate end of life (80\% initial capacity) and overlay in capacity plot")
    
    outliers = col2.toggle('Filter outliers',
                           help="Remove outliers: datapoints 3 standard deviations away from mean")

    
selected_cell_uri = [cell_label_uri.get(label, label) for label in selected_cell_label]

# SQL query to fetch data
if selected_cell_uri:  # Make sure something is selected
    sql_query = f"""SELECT * FROM {selected_table}
                    WHERE CellURI = ANY(%s);"""  # Using ANY to match any item in the list
                    
    if selected_table == 'stats':
        show_columns = ["cycle", "chargecapacity", "dischargecapacity",
                        "chargeenergy", "dischargeenergy"]
    else:
        show_columns = ["testtime", "cellvoltage", "current",
                        "capacity", "energy"]

    df = pd.read_sql(sql_query, conn, params=(selected_cell_uri,))
    df['celllabel'] = df['celluri'].map(cell_uri_label).fillna(df['celluri'])


    # Plot data using Plotly
    st.sidebar.header("Plot Options")
    
    x_column = st.sidebar.selectbox("Select X-axis column", show_columns, key='x')
    y_column = st.sidebar.selectbox("Select Y-axis column", show_columns, key='y', index = 1)
    
    df[x_column] = pd.to_numeric(df[x_column], errors='coerce')
    df[y_column] = pd.to_numeric(df[y_column], errors='coerce')
    
    if outliers:
        # Calculate Z-score
        z_scores = np.abs(stats.zscore(df[y_column]))
        mask = z_scores < 3
        #mask = (df[y_column] >= df[y_column].quantile(0.1)) & (df[y_column] <= df[y_column].quantile(0.9))
        df = df[mask]
    else:
        df = df
    
    # Create a plot
    if not df.empty:
                
        if (selected_table=="cycle") and (x_column=="capacity"):            

            cycle_num = st.sidebar.multiselect("Select cycle numbers", df["cycle"].unique(), key='cycle', default=["1"])
            df = df[df["cycle"].isin(cycle_num)]



        fig = px.scatter(df, 
                        x=x_column, 
                        y=y_column, 
                        title=f"{y_column} vs. {x_column}", 
                        color='celllabel')


            
        if eol_limit and (selected_table=="stats") and (x_column=="cycle"):
            if y_column in ["chargecapacity", "dischargecapacity"]:

                plot_colors = [dict_element["marker"]["color"] for dict_element in fig.to_dict()["data"]]

                for n, celllabel in enumerate(df['celllabel'].unique()):

                    initial_capacity = np.amin(df[(df['celllabel']==celllabel) & (df["cycle"]==1)][y_column].values)

                    fig.add_hline(y=initial_capacity*0.8,
                                line_color=plot_colors[n], 
                                opacity=0.5)
                    

        st.plotly_chart(fig, use_container_width=True)

# Close the connection
conn.close()

