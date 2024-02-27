import streamlit as st
import pandas as pd
import json
import os
import psycopg2

# st.set_page_config(layout="wide")
# st.selectbox("select the type of data",["Time Series Data","Battery Cycling Data"])
# st.file_uploader("Choose a file")
db_params = {
            "dbname": "mydb",
            "user": "admin",
            "host": "localhost",
            "port": "5432"
        }
conn = psycopg2.connect(**db_params)