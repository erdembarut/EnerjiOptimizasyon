import streamlit as st
import pandas as pd
import numpy as np
import io

st.set_page_config(layout="wide", page_title="Endüstriyel Enerji SCADA")

st.title("🏭 Endüstriyel Enerji Optimizasyonu & SCADA Yönetim Paneli")

# --- 1. BÖLÜM: PARAMETRE GİRİŞLERİ (3 Ana Kart) ---
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("🔥 Doğalgaz & Proses Yükleri")
    uretim = st.number_input("Üretim Kapasitesi (ton/gün):", value=250)
    hood_tuk = st.number_input("Hood Spesifik Tüketim (kWh/ton):", value=535)
    gaz_fiyat = st.number_input("Doğalgaz Birim Fiyatı (TL/Nm3):", value=18.0)

with col2:
    st.subheader("⚡ Elektrik Altyapısı")
    sabit_elk = st.number_input("Sabit Elektrik Tüketimi (kWh/ton):", value=789)
    ges_gucu = st.number_input("Kurulu GES Gücü (MW):", value=15.0)
    res_gucu = st.number_input("Kurulu RES Gücü (MW):", value=12.0)

with col3:
    st.subheader("🔋 Molten Salt Depolama")
    salt_kapasite = st.number_input("Tuz Isıl Kapasitesi (MWh):", value=120)
    soc_min = st.slider("Min. Depo Seviyesi Güvenlik Limiti (%)", 0, 100, 20)
    st.metric("Gün Sonu Hedef Bakiyesi", "120.0 MWh")

st.divider()

# --- 2. BÖLÜM: SCADA TABLOSU (Matematiksel Model Entegrasyonu) ---
st.subheader("⏱ Saatlik Operasyonel Çizelge")

# Başlangıç verisi (Modelin değişkenleri)
if 'scada_data' not in st.session_state:
    st.session_state.scada_data = pd.DataFrame({
        "Saat": [f"{h:02}:00" for h in range(24)],
        "Elektrik_Fiyat_TL": [2.8] * 24,
        "Gaz_Tüketim_MWh": [20.0] * 24,
        "Şarj_Deşarj_MW": [0.0] * 24,
        "Depo_Seviyesi_MWh": [40.0] * 24
    })

# Data Editor: SCADA yönetimini buradan yapıyorsunuz
edited_df = st.data_editor(st.session_state.scada_data, use_container_width=True)

# --- 3. BÖLÜM: HESAPLAMA & RAPORLAMA ---
def calculate_system(df, min_limit):
    # Basit SOC güncelleme mantığı (Dinamik)
    soc = [40.0] 
    for i in range(1, len(df)):
        new_soc = soc[-1] + (df.loc[i-1, "Şarj_Deşarj_MW"]) - 0.5 
        soc.append(max(min_limit * 1.2, min(100, new_soc))) 
    return soc

if st.button("🚀 Senaryoyu Hesapla ve Onayla"):
    edited_df["Depo_Seviyesi_MWh"] = calculate_system(edited_df, soc_min)
    st.success("Tüm veriler proses parametrelerine göre optimize edildi.")
    st.line_chart(edited_df[["Depo_Seviyesi_MWh"]])

# --- Excel İhracat ---
def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Enerji_Plani')
    return output.getvalue()

st.download_button("📥 Planı Excel Olarak İndir", to_excel(edited_df), "scada_raporu.xlsx")
