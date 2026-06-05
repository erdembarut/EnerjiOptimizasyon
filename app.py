import streamlit as st
import pandas as pd
import io

# --- 1. SAYFA VE GELİŞMİŞ CSS TASARIMI ---
st.set_page_config(layout="wide", page_title="EnerjiOptimizasyon SCADA Paneli", page_icon="🏭")

# Görsel zenginlik için özel CSS
st.markdown("""
    <style>
    .kpi-card {
        background-color: #ffffff;
        border-left: 5px solid #1f77b4;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 15px;
    }
    .kpi-title { color: #5c6a7a; font-size: 14px; font-weight: bold; text-transform: uppercase; }
    .kpi-value { color: #2e384d; font-size: 28px; font-weight: 900; margin-top: 5px; }
    .stButton>button { height: 60px; font-weight: 800; font-size: 16px; border-radius: 10px; transition: all 0.3s; }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
    </style>
""", unsafe_allow_html=True)

st.title("🏭 EnerjiOptimizasyon & SCADA Yönetim Paneli")
st.markdown("---")

# --- 2. KONTROL PANELİ (GİRDİLER) ---
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("### 🔥 Doğalgaz & Proses Yükleri")
    uretim = st.number_input("Üretim Kapasitesi (ton/gün):", value=250.0, step=1.0, min_value=0.0)
    hood = st.number_input("Hood Layer Spesifik Tüketim (kWh/ton):", value=535.0, step=1.0, min_value=0.0)
    gaz_fiyat = st.number_input("Doğalgaz Birim Fiyatı (TL/Nm3):", value=18.00, step=0.01, min_value=0.0)
    gaz_isil = st.number_input("Doğalgaz Isıl Değeri (kWh/Nm3):", value=10.64, step=0.01, min_value=0.0)
    kazan_verimi = st.number_input("Brülör / Kazan Verimi (%):", value=90.0, step=1.0, min_value=0.0)

with c2:
    st.markdown("### ⚡ Elektrik Altyapısı")
    sabit_elk = st.number_input("Hamur Kasası & Sabit Hat Tüketimi (kWh/ton):", value=789.0, step=1.0, min_value=0.0)
    ges = st.number_input("Kurulu GES Gücü (MW):", value=15.0, step=1.0, min_value=0.0)
    res = st.number_input("Kurulu RES Gücü (MW):", value=12.0, step=1.0, min_value=0.0)
    res_bedel = st.number_input("RES Hat Kullanım Bedeli (TL/kWh):", value=0.35, step=0.01, min_value=0.0)
    rezistans = st.number_input("Elektrikli Rezistans Verimi (%):", value=98.0, step=1.0, min_value=0.0)

with c3:
    st.markdown("### 🔋 Molten Salt (Erimiş Tuz) Depolama")
    tuz_kap = st.number_input("Tuz Isıl Kapasitesi (MWh):", value=120.0, step=1.0, min_value=0.0)
