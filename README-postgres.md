# Setting Up PostgreSQL Database on windows

This guide outlines the steps to set up a PostgreSQL database from scratch.

## Step 1: Download and Install PostgreSQL

Download PostgreSQL from the official website and follow the instructions to install it.

## Step 2: Create an Empty Directory for the Database

Create an empty directory where you want to store the PostgreSQL database files.

## Step 3: Initialize the Database Cluster

Open command prompt and run the following command to initialize the database cluster:

"initdb -D path_to_directory_created_in_step_2", this would set up a database cluster and create an initial user.


## Step 4: Start the PostgreSQL Server

To start the PostgreSQL server, run the following command:

"pg_ctl -D path_to_directory_created_in_step_2 start" 

## Step 5: Create a database

Run the following command:

'createdb "HEU-intelligent"'

## Step 6: Create a user and grant a role to the user

Run the following commands:
'psql -U "username" -d HEU-intelligent', username is the initial username that appears in step 3.
"CREATE USER user1 WITH PASSWORD 'root'";
GRANT ALL PRIVILEGES ON DATABASE "HEU-intelligent" TO user1;


#### basic postgres sql commands
1. "psql HEU-intelligent" to enter sql terminal of database
2. "\dt" to see the tables created/existing 
3."CREATE TABLE battery_time_series_data (
    time TIME,
    current FLOAT,
    voltage FLOAT,
    temperature FLOAT,
     test time" TIME,
    "test URI" CHAR(200),
    "record URI" CHAR(200),
    "cell URI" CHAR(200)
);

"
4.CREATE TABLE cycling_series_data (
    "cycle number" INTEGER,
    "charge capacity" FLOAT,
    "discharge capacity" FLOAT,
    "test time" TIME,
    "test URI" CHAR(200),
    "record URI" CHAR(200),
    "cell URI" CHAR(200)
);

"
5. SELECT current_user;








