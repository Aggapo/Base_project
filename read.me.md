GDSC Database System – Implementation Guide
==========================================

This project implements a relational database system for selected GDSC1000 data
as part of the Database Systems course.

The repository contains:
- SQL schema definition (DDL)
- A Python ETL pipeline
- Preprocessed input data files

--------------------------------------------------------------------
1. Requirements
--------------------------------------------------------------------

Software:
- PostgreSQL (tested with version 15+)
- Python 3.14.2
- pgAdmin 4 (recommended)

Python libraries:
- pandas
- sqlalchemy
- psycopg2-binary
- openpyxl

--------------------------------------------------------------------
2. Database Setup
--------------------------------------------------------------------

1. Create a PostgreSQL database named:

   gdsc

2. Execute the schema definition:

   schema.sql

This script:
- Drops existing tables if present
- Creates all tables in 3rd Normal Form (3NF)
- Defines primary keys, foreign keys, and indices

--------------------------------------------------------------------
3. Data Loading (ETL)
--------------------------------------------------------------------

Input files:
- GDSC2_fitted_dose_response_27Oct23.xlsx  (Experiment data – Table A)
- TableS1E.xlsx                           (Cell line & tissue metadata – Table B)
- C_Preprocessed.xlsx                    (Cleaned drug metadata – Table C)

Database connection (defined in etl_load.py):

postgresql+psycopg2://postgres:postgres@localhost:5432/gdsc

Default credentials:
- user: postgres
- password: postgres

Run the ETL pipeline from the project directory:

   python etl_load.py

The script:
1. Clears all tables
2. Loads tissue subtype data
3. Loads cell line metadata
4. Loads and normalizes drug metadata
5. Loads experiment data with referential integrity checks

Successful execution ends with:

   ETL complete

--------------------------------------------------------------------
4. Reproducibility
--------------------------------------------------------------------

Each team member can reproduce the database locally by:
1. Installing PostgreSQL
2. Creating the gdsc database
3. Running schema.sql
4. Installing Python 3.14.2 and required libraries
5. Running etl_load.py


