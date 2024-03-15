import streamlit as st
import pandas as pd
import json,uuid
from sqlalchemy import create_engine
from collections import OrderedDict

st.set_page_config(layout="wide")

def user_input_tabletype():
    selected_data_type = st.selectbox("select the type of data",["None","Time Series Data","Battery Cycling Data"],key="selected_data_type")
    if selected_data_type =="Time Series Data":
        st.write("For Time series data, the columns you can upload are the Time, voltage & current data to the database table")
        header_rows = st.text_input("Enter the number of header rows in your CSV:",value=0)
        return selected_data_type,header_rows
    elif selected_data_type =="Battery Cycling Data":
        st.write("For Cycling data, the columns you can upload the cycle number, charge capacitance & discharge capacitance data to the database table")
        header_rows = st.text_input("Enter the number of header rows in your CSV:",value=0)
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
        st.text(e)

def check_required_columns(column_match_dict, required_number):
    if len(column_match_dict)==required_number and len(set(column_match_dict.values())) == required_number:
        st.text("Required columns present! Thanks")
        return 1
    else:
        st.text("Columns not mapped uniquely!")


def data_series_select_box(uploaded_df,std_col_list,matched_dict=None):
    database_df=pd.DataFrame()
    column_match={}
    unique_key=0
    if matched_dict is not None:
            for quantity,col_vale in matched_dict.items():
                unique_key+=1
                stcol1, stcol2= st.columns([1, 2])
                if type(col_vale)==str:
                    selected_df_column=stcol1.selectbox("columns from your csv",options=[col_vale],key=f"st1-{unique_key}")                  
                else:
                    st.text(f"unable to find a suitable match for quantity {quantity}, please select the column.")
                    selected_df_column=stcol1.selectbox("columns from your csv",options=col_vale,key=f"st1-{unique_key}")
                selected_match=stcol2.selectbox("Choose quantity",options=[quantity],key=f"st2-{unique_key}")
                column_match[selected_df_column]=selected_match
                database_df[selected_match]=uploaded_df[selected_df_column]
    else:
            for quantity in std_col_list:
                unique_key+=1
                stcol1, stcol2= st.columns([1, 2])
                selected_df_column=stcol1.selectbox("columns from your csv",options=uploaded_df.columns,key=f"st1_std-{unique_key}")
                selected_match=stcol2.selectbox("Choose quantity",options=std_col_list,key=f"st2_std-{unique_key}")
                column_match[selected_df_column]=selected_match
    database_df[selected_match]=uploaded_df[selected_df_column]
    return column_match,database_df

def save_data_match(df, column_match, database_df):
    dump_to_json(r"data\user_data\column_name_user_match.json", column_match)
    dump_df_csv(r"data\user_data\df.csv", database_df)


def load_default_col_names(existing_json,uploaded_df):
    ## to be implemented fuzzy match instead of string match
    with open(existing_json, "r") as file:
        orderedjson_data = json.load(file,object_pairs_hook=OrderedDict)
    matched_dict = {}
    for key, value_list in orderedjson_data.items():
        for value in value_list:
            if value in uploaded_df.columns:
                matched_dict[key] = value
                print("matched_dict",matched_dict)
                break
        else:
               matched_dict[key] = list(uploaded_df.columns) #for those database table columns with no match found
    return matched_dict

def add_uuid_columns(df):
    # Generate UUIDs for each row
    uuids = [uuid.uuid4() for _ in range(len(df))]
    # Add UUIDs as new columns to the DataFrame
    df['test URI'] = [str(uuid_) for uuid_ in uuids]
    df['record URI'] = [str(uuid_) for uuid_ in uuids]
    df['cell URI'] = [str(uuid_) for uuid_ in uuids]
    return df

battery_data_types= {
    "Time Series Data": {"table_columns":["test time","current","voltage","temperature"],"db_table_name":"battery_time_series_data","try_col_name_match_file_path":r"data\user_data\battery_time_series_column_name_try_match.json"},
    "Battery Cycling Data":{"table_columns":["cycle number","charge capacity","discharge capacity","test time"],"db_table_name":"battery_cycling_series_data","try_col_name_match_file_path":r"data\user_data\battery_cycling_series_column_name_try_match.json"} 
}

def main():
    data_table_type,header_rows= user_input_tabletype()
    if data_table_type in battery_data_types :
        uploaded_file=upload_file()
        if uploaded_file:
            df=uploaded_file_df(uploaded_file=uploaded_file,header_row_count=int(header_rows))
            if type(df) == pd.DataFrame:
                database_df=pd.DataFrame()
                matched_dict=load_default_col_names(battery_data_types[data_table_type]["try_col_name_match_file_path"],df)
                column_match, database_df = data_series_select_box(df,battery_data_types[data_table_type]["table_columns"],matched_dict)
                save_data_match(df, column_match, database_df)
                validate_columns_commit_database = st.button("I have matched columns correctly, commit to database!",key="dbase")
                if validate_columns_commit_database:
                    matched_cols=check_required_columns(column_match,4)
                    if matched_cols:
                        uri_updated_database_df = add_uuid_columns(database_df)
                        table_name=battery_data_types[data_table_type]["db_table_name"]
                        connection_string = 'postgresql://sridevik@localhost:5432/HEU-intelligent'
                        send_df_to_sql(uri_updated_database_df, table_name, connection_string)
            else:
                st.text("Check the number of header rows")
    else:
        pass

if __name__ == "__main__":
    main()
