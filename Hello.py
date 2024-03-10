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

st.set_page_config(
    page_title="Interés compuesto | Compound interest",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About":""}
)

alt.themes.enable("dark")

uri = "https://api.binance.com"

##  Fill in your Binance API key and Secret keys:
#binance_api_key = st.secrets["KEY"]
#binance_api_secret = st.secrets["SECRET"]

def get_timestamp_offset():
    url = "{}/api/v3/time".format(uri)
    payload = {}
    headers = {"Content-Type": "application/json"}
    response = requests.request("GET", url, headers=headers, data=payload)
    result = json.loads(response.text)["serverTime"]-int(time.time()*1000)
    return result

st.text(get_timestamp_offset())
