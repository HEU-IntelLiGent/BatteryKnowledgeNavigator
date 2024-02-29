import streamlit as st
import pandas as pd
import json
from sqlalchemy import create_engine

st.set_page_config(layout="wide")
    
def user_input_tabletype():
    selected_data_type = st.selectbox("select the type of data",["None","Time Series Data","Battery Cycling Data"],key="selected_data_type")
    if selected_data_type =="Time Series Data":
        st.write("For Time series data, the columns you can upload are the Time, voltage & current data to the database table")
        header_rows = st.text_input("Enter the number of header rows in your CSV:")
        return selected_data_type,header_rows
    elif selected_data_type =="Battery Cycling Data":
        st.write("For Cycling data, the columns you can upload the cycle number, charge capacitance & discharge capacitance data to the database table")
        header_rows = st.text_input("Enter the number of header rows in your CSV:")
        return selected_data_type,header_rows
    else:
        return None,None
    
def preview_file(df):
    st.dataframe(df.head()) 

def upload_file():
    uploaded_file=st.file_uploader("upload a csv file",type=["csv"])
    if uploaded_file is not None:
        return uploaded_file
    else:
        return None
    
def uploaded_file_df(uploaded_file=None,header_row_count=None):
        try:
            df = pd.read_csv(uploaded_file,skiprows=header_row_count)
            preview_file(df)
            return df
        except pd.errors.ParserError as e:
            st.text(e)
        return None
    
def column_names(df):
    return df.columns

def dump_to_json(file_path, json_file):
    with open(file_path, "w") as file:
        json.dump(json_file, file, indent=4)

def dump_df_csv(file_path, df):
    df.to_csv(file_path, index=False)

def send_df_to_sql(df, table_name, connection_string):
    engine = create_engine(connection_string)
    try:
        df.to_sql(table_name, con=engine, if_exists='append', index=False)
        st.text("Data successfully added to the '{}' table.".format(table_name))
    except Exception as e:
        st.text("Error:", e)

def check_required_columns(column_match_dict, required_number):
    if len(column_match_dict)==required_number and len(set(column_match_dict.values())) == required_number:
        st.text("Required columns present! Thanks")
        return 1
    else:
        st.text("Time, voltage, current are not mapped uniquely! please check again.!")

def data_series_select_box(uploaded_df,std_col_list):
    database_df=pd.DataFrame()
    column_match={}
    time_series_list=["Time","Current","Voltage","Temperature"]
    unique_key=0
    for quantity in std_col_list:
        unique_key+=1
        stcol1, stcol2= st.columns([1, 2])
        selected_df_column=stcol1.selectbox("columns from your csv",options=uploaded_df.columns,key=f"{quantity}_{unique_key}")
        selected_match=stcol2.selectbox("Choose quantity",options=std_col_list,key=unique_key)
        column_match[selected_df_column]=selected_match
        database_df[selected_match]=uploaded_df[selected_df_column]
    return column_match,database_df

def save_data_match(df, column_match, database_df):
    dump_to_json(r"data\user_data\column_name_match.json", column_match)
    dump_df_csv(r"data\user_data\df.csv", database_df)

battery_data_types= {
    "Time Series Data": {"table_columns":["Time","Current","Voltage","Temperature"],"db_table_name":"battery_time_series_data"},
    "Battery Cycling Data":{"table_columns":["Cycle no","Charge Capacitance","Dischareg Capacitance","Test Time"],"db_table_name":"battery_cycling_series_data"} 
}

def main():
    data_table_type,header_rows= user_input_tabletype()
    if data_table_type in battery_data_types :
        uploaded_file=upload_file()
        if uploaded_file:
            df=uploaded_file_df(uploaded_file=uploaded_file,header_row_count=int(header_rows))
            if type(df) == pd.DataFrame:
                database_df=pd.DataFrame()
                column_match, database_df = data_series_select_box(df,battery_data_types[data_table_type]["table_columns"])
                save_data_match(df, column_match, database_df)
                validate_columns_commit_database = st.button("I have matched columns correctly, commit to database!",key=f"d_")
                if validate_columns_commit_database:
                    matched_cols=check_required_columns(column_match,4)
                    if matched_cols:
                        table_name=battery_data_types[data_table_type]["db_table_name"]
                        connection_string = 'postgresql://sridevik@localhost:5432/HEU-intelligent'
                        send_df_to_sql(database_df, table_name, connection_string)
            else:
                st.text("Check the number of header rows")
    else:
        pass

if __name__ == "__main__":
    main()
