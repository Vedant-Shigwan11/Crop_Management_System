import mysql.connector
import streamlit as st
import pandas as pd
import random
from faker import Faker
from datetime import datetime, timedelta

# Initialize Faker for generating random data
fake = Faker()

# MySQL Database Connection Details
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "vedant",
    "database": "crop_management_system"
}

# Sample data
crop_names = ["Wheat", "Rice", "Corn", "Soybean", "Barley", "Sugarcane", "Cotton", "Potato", "Tomato", "Lettuce"]
growth_stages = ["Seedling", "Vegetative", "Flowering", "Fruiting", "Maturity"]
pest_control_measures_list = [
    "Use of organic pesticides", "Crop rotation", "Neem oil application", 
    "Biological pest control", "Chemical pesticides", "Regular field monitoring"
]

# Database Connection Function
def connect_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as e:
        st.error(f"Error connecting to database: {e}")
        return None

# Function to Insert Manual Crop Record
def insert_manual_record(crop_name, planting_date, harvest_date, growth_stage, pest_control, yield_prediction):
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        values = (crop_name, planting_date, harvest_date, growth_stage, pest_control, yield_prediction)
        
        if any(not v for v in values):
            st.warning("All fields must be filled!")
            return
        
        try:
            cursor.execute("""
                INSERT INTO crops (crop_name, planting_date, harvest_date, growth_stage, pest_control_measures, yield_prediction)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, values)
            conn.commit()
            st.success("Crop record inserted successfully!")
            conn.close()
        except mysql.connector.Error as e:
            st.error(f"Error inserting record: {e}")

# Function to Generate Random Data for Bulk Insert
def generate_data():
    planting_date = fake.date_between(start_date="-2y", end_date="today")
    harvest_date = planting_date + timedelta(days=random.randint(60, 180))
    return (random.choice(crop_names), planting_date, harvest_date, random.choice(growth_stages), 
            random.choice(pest_control_measures_list), random.randint(500, 5000))

# Function to Insert Bulk Records
def insert_bulk_records():
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        batch_size = 10000
        total_records = 100000
        
        for _ in range(0, total_records, batch_size):
            cursor.executemany("""
                INSERT INTO crops (crop_name, planting_date, harvest_date, growth_stage, pest_control_measures, yield_prediction)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, [generate_data() for _ in range(batch_size)])
            conn.commit()
        
        st.success("100,000 records inserted successfully!")
        conn.close()

# Function to Display Records
def display_records():
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM crops ORDER BY id DESC LIMIT 20")
        rows = cursor.fetchall()
        conn.close()
        return pd.DataFrame(rows, columns=["ID", "Crop Name", "Planting Date", "Harvest Date", "Growth Stage", "Pest Control", "Yield Prediction"])
    return pd.DataFrame()

# Streamlit UI Setup
st.set_page_config(page_title="Crop Management System", layout="wide")
st.markdown(""" <style>
    .css-1d391kg {background-color: #121212; color: white;}
    .css-18e3th9 {background-color: #121212; color: white;}
    .css-1aumxhk {background-color: #121212; color: white;}
    .css-10trblm {background-color: #121212; color: white;}
    h1, h2, h3, h4, h5, h6 {color: #17A2B8 !important;}
    .stButton>button {background-color: #17A2B8; color: white; font-weight: bold; border-radius: 5px;}
</style> """, unsafe_allow_html=True)

st.title("🌾 Crop Management System")
st.sidebar.header("Manage Records")

# Input Fields
with st.form("crop_form"):
    crop_name = st.selectbox("Crop Name", crop_names)
    planting_date = st.date_input("Planting Date")
    harvest_date = st.date_input("Harvest Date")
    growth_stage = st.selectbox("Growth Stage", growth_stages)
    pest_control = st.selectbox("Pest Control Measures", pest_control_measures_list)
    yield_prediction = st.number_input("Yield Prediction (kg)", min_value=100, max_value=10000, step=100)
    submit_button = st.form_submit_button("Insert Record")
    
    if submit_button:
        insert_manual_record(crop_name, planting_date, harvest_date, growth_stage, pest_control, yield_prediction)

# Bulk Insert Button
if st.button("Insert 100,000 Random Records", key="bulk_insert", help="This may take some time"):
    insert_bulk_records()

# Display Records Table
st.subheader("📊 Recent Crop Records")
record_df = display_records()
st.dataframe(record_df, use_container_width=True)
