# -*- coding: utf-8 -*-
"""automated_dashboard.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1tHZEWW2ho5U3wMRQ69PeTG4KDgNj7--0
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# ====== LOAD DATA ======
actual_data = pd.read_csv("usd_idr_actual.csv", parse_dates=["date"])
forecast_yesterday = pd.read_csv("usd_idr_pred_yesterday.csv", parse_dates=["date"])
forecast_latest = pd.read_csv("usd_idr_pred_latest.csv", parse_dates=["date"])

# Gabungkan prediksi terbaru ke satu dataframe
forecast_data = forecast_latest.copy()
forecast_data.rename(columns={"predicted_usd_idr": "value"}, inplace=True)
forecast_data["type"] = "forecast"

# Data aktual
actual_data = actual_data.rename(columns={"usd_idr": "value"})
actual_data["type"] = "actual"

# Gabungkan prediksi terbaru ke satu dataframe
forecast_data = forecast_latest.copy()
forecast_data.rename(columns={"predicted_usd_idr": "value"}, inplace=True)
forecast_data["type"] = "forecast"

# ❗ Filter hanya hari kerja
forecast_data = forecast_data[forecast_data['date'].dt.weekday < 5]
forecast_yesterday = forecast_yesterday[forecast_yesterday['date'].dt.weekday < 5]

# Gabungkan semua
data = pd.concat([actual_data, forecast_data], ignore_index=True)

# ====== SET PAGE ======
st.set_page_config(page_title="Prediksi USD/IDR", layout="wide")
st.title("📈 Dashboard Prediksi Nilai Tukar USD/IDR")
st.caption("Prediksi nilai tukar untuk 7 hari ke depan berdasarkan data 30 hari terakhir")

# ====== GRAFIK UTAMA ======
fig = px.line(data, x='date', y='value', color='type',
              line_dash='type',
              labels={'value': 'Nilai Tukar (Rp)', 'date': 'Tanggal'},
              title='Nilai Tukar USD/IDR - Aktual dan Prediksi')

fig.update_traces(mode="lines+markers", hovertemplate='Tanggal: %{x|%d %b %Y}<br>Nilai: Rp %{y:,.2f}')
st.plotly_chart(fig, use_container_width=True)

# ====== INFO PREDIKSI KEMARIN ======
try:
    yesterday = datetime.today().date() - pd.Timedelta(days=1)
    pred_yest_val = forecast_yesterday.loc[forecast_yesterday['date'].dt.date == yesterday, 'predicted_usd_idr'].values[0]
    actual_today_val = actual_data.loc[actual_data['date'].dt.date == datetime.today().date(), 'value'].values[0]
    error = actual_today_val - pred_yest_val
    delta_str = f"selisih {error:+,.2f} dari data aktual"

    st.metric("Prediksi Kemarin", f"Rp {pred_yest_val:,.2f}", delta=delta_str)
except:
    st.warning("📌 Belum ada data aktual hari ini untuk membandingkan dengan prediksi kemarin.")

# ====== NOTIFIKASI ======
today = datetime.today().date()
if today not in actual_data['date'].dt.date.values:
    st.warning("📅 Hari ini perdagangan libur")

# Tren naik/turun
if forecast_data['value'].mean() > actual_data['value'].mean():
    st.info("📈 Tren USD/IDR diperkirakan akan naik")
elif forecast_data['value'].mean() < actual_data['value'].mean():
    st.info("📉 Tren USD/IDR diperkirakan akan turun")
else:
    st.info("📊 Nilai tukar diperkirakan stabil")

# ====== SLIDER UNTUK RANGE WAKTU ======
min_date = data['date'].min().date()
max_date = data['date'].max().date()

date_range = st.slider("Pilih rentang tanggal", min_value=min_date, max_value=max_date, value=(min_date, max_date))
filtered = data[(data['date'].dt.date >= date_range[0]) & (data['date'].dt.date <= date_range[1])]

fig2 = px.line(filtered, x='date', y='value', color='type', line_dash='type',
               title="Rentang Waktu yang Dipilih")
st.plotly_chart(fig2, use_container_width=True)