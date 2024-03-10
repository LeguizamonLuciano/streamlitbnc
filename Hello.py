import hmac
import hashlib
import requests
import json
import time
import datetime
import pandas as pd
import streamlit as st
import altair as alt
import sys
import numpy as np
import plotly.graph_objects as go
import os

st.set_page_config(
    page_title="Interés compuesto | Compound interest",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About":""}
)

alt.themes.enable("dark")

def compound_interest(principal, annual_rate, years, monthly_contribution):
    annual_rate /= 100  # converting percentage to decimal
    monthly_rate = annual_rate / 12
    total_months = years * 12
    values = []
    value = principal
    yearly_values = []

    for month in range(total_months):
        value += value * monthly_rate
        value += monthly_contribution
        if (month + 1) % 12 == 0:  # Check if it's the end of the year
            yearly_values.append(int(value))  # Append the value at the end of each year
    return yearly_values

uri = "https://api.binance.com"

##  Fill in your Binance API key and Secret keys:
binance_api_key = os.environ.get('KEY')
binance_api_secret = os.environ.get('SECRET')

def get_timestamp_offset():
    url = "{}/api/v3/time".format(uri)
    payload = {}
    headers = {"Content-Type": "application/json"}
    response = requests.request("GET", url, headers=headers, data=payload)
    result = json.loads(response.text)["serverTime"] - int(time.time() * 1000)

    return result

def generate_signature(query_string):
    m = hmac.new(binance_api_secret.encode("utf-8"), 
                 query_string.encode("utf-8"), 
                 hashlib.sha256)
    return m.hexdigest()

def get_flexible_savings_balance(asset):
    timestamp = int(time.time() * 1000 + get_timestamp_offset())
    query_string = "asset={}&timestamp={}".format(asset, timestamp)
    signature = generate_signature(query_string)

    url = "{}/sapi/v1/simple-earn/flexible/position?{}&signature={}".format(uri, query_string, signature)

    payload = {}
    headers = {
      "Content-Type": "application/json",
      "X-MBX-APIKEY": binance_api_key
    }

    return json.loads(requests.request("GET", url, headers=headers, data=payload).text)

data = get_flexible_savings_balance('USDT')

rows_data = data['rows']

# Display the DataFrame
df = df[['totalAmount','latestAnnualPercentageRate','yesterdayRealTimeRewards','cumulativeBonusRewards','cumulativeRealTimeRewards','cumulativeTotalRewards']]
    
def main():
    st.sidebar.header('📈 Parámetros', divider="rainbow")
    st.sidebar.caption('se estima que el interés se agrega mensualmente al monto')

    # Define placeholders for initial values
    principal_input = st.sidebar.number_input('Monto inicial', value=1550)
    annual_rate_input = st.sidebar.number_input('Interés (%)', value=5)
    monthly_contribution = st.sidebar.number_input('Contribución mensual', value=100)
    years = st.sidebar.number_input('Años', value=5)
    
    # Create text input fields for dynamic updates
    st.sidebar.markdown("<h3 style='text-align: center;'>Monto Binance</h3>", unsafe_allow_html=True)
    st.sidebar.markdown("<p style='text-align: center;'>" + str(int(float(df['totalAmount']))) + "</p>", unsafe_allow_html=True)
    principal_text = float(df['totalAmount'])
    st.sidebar.markdown("<h3 style='text-align: center;'>APY% Binance</h3>", unsafe_allow_html=True)
    st.sidebar.markdown("<p style='text-align: center;'>" + str(round(float(df['latestAnnualPercentageRate']) * 100, 2)) + "</p>", unsafe_allow_html=True)
    annual_rate_text = float(df['latestAnnualPercentageRate'])*100
        
    # Create a container to hold the button
    container = st.container()
    
    # Center the container
    with container:
        col1, col2, col3 = st.sidebar.columns([1, 1, 1])
        with col2:
            if st.button("Binance 💰"):
                # If the text input is not empty, update the respective value
                if principal_text != "":
                    principal_input = float(principal_text)
                if annual_rate_text != "":
                    annual_rate_input = float(annual_rate_text)
    
    values = compound_interest(principal_input, annual_rate_input, years, monthly_contribution)
    years_list = [f'Año {i+1}' for i in range(years)]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=years_list, y=values, mode='lines+markers', name='Valor acumulado'))
    fig.update_layout(title='Interés Compuesto',
                      xaxis_title='Años',
                      yaxis_title='Valor acumulado',
                      height=700,
                      width=1000,
                      title_x=0.5)
    
    st.plotly_chart(fig)

if __name__ == "__main__":
    main()
