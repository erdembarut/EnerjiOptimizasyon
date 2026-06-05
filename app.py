import streamlit as st
import pulp
import pandas as pd
import requests
from datetime import datetime

# Arayüz Ayarları
st.set_page_config(layout="wide")
lang = st.sidebar.selectbox("Dil / Language", ["TR", "EN"])

# EPİAŞ Verisi Çekme Fonksiyonu
def get_epias_prices():
    # Günlük PTF verisi için API çağrısı
    url = "https://seffaflik.epias.com.tr/v1/market/day-ahead-market/market-clearing-price"
    params = {"startDate": datetime.now().strftime("%Y-%m-%dT00:00:00+03:00"), 
              "endDate": datetime.now().strftime("%Y-%m-%dT23:59:59+03:00")}
    try:
        response = requests.get(url, params=params)
        data = response.json()['body']['mcpList']
        return pd.DataFrame(data)
    except:
        return None

# Panel
st.title("Enerji Optimizasyon Paneli")
if st.button("EPİAŞ Verilerini Güncelle"):
    df = get_epias_prices()
    if df is not None:
        st.session_state['prices'] = df
        st.success("Veriler güncellendi!")
        st.dataframe(df.head(10))
    else:
        st.error("Veri alınamadı.")

manual_mode = st.checkbox("Manuel Tuz Şarjı")
manual_mw = st.number_input("Şarj Gücü (MW)", 0.0, 50.0, 10.0, disabled=not manual_mode)

if st.button("Solver'ı Çalıştır"):
    if 'prices' not in st.session_state:
        st.warning("Lütfen önce EPİAŞ verilerini güncelleyin.")
    else:
        st.write("Optimizasyon hesaplanıyor...")
        # Burada maliyet minimizasyonu yapan solver kurgusu devam edecek...
        st.success("Planlama hazır!")
