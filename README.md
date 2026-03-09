# Base_project
GDSC Database System – Implementation Guide

This project implements a relational database system for selected GDSC1000 data as part of the Database Systems course.

The repository contains:

    SQL schema definition (DDL)
    A Python ETL pipeline
    Preprocessed input data files

    Requirements

Software:

    PostgreSQL (tested with version 15+)
    Python 3.14.2
    pgAdmin 4 (recommended)

Python libraries:

    pandas
    sqlalchemy
    psycopg2-binary
    openpyxl

    Database Setup

    Create a PostgreSQL database named:

    gdsc

    Execute the schema definition:

    schema.sql

This script:

    Drops existing tables if present
    Creates all tables in 3rd Normal Form (3NF)
    Defines primary keys, foreign keys, and indices

    Data Loading (ETL)

Input files:

    GDSC2_fitted_dose_response_27Oct23.xlsx (Experiment data – Table A)
    TableS1E.xlsx (Cell line & tissue metadata – Table B)
    C_Preprocessed.xlsx (Cleaned drug metadata – Table C)

Database connection (defined in etl_load.py):

postgresql+psycopg2://postgres:postgres@localhost:5432/gdsc

Run the ETL pipeline from the project directory:

python etl_load.py

The script:

    Clears all tables
    Loads tissue subtype data
    Loads cell line metadata
    Loads and normalizes drug metadata
    Loads experiment data with referential integrity checks

Successful execution ends with:

ETL complete

    Reproducibility

Each team member can reproduce the database locally by:

    Installing PostgreSQL
    Creating the gdsc database
    Running schema.sql
    Installing Python 3.14.2 and required libraries
    Running etl_load.py
