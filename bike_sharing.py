import streamlit as st
import pandas as pd
import numpy as np

st.title("Bike sharing")

DAY_PATH = 'dataset/day.csv'
HOUR_PATH  = 'dataset/hour.csv'

@st.cache_data
def load_data(nrows):
    data = pd.read_csv(DAY_PATH, nrows=nrows)
    return data

st.text('Bike Sharing Day per Day')
day_data = load_data(10)
st.table(data=day_data)

st.text('Bike Sharing Data per Hour')
hour_data = load_data(10)
st.table(data=hour_data)