import streamlit as st
import pandas as pd
import io

# Sayfa Yapılandırması
st.set_page_config(layout="wide", page_title="Endüstriyel SCADA Paneli")

# Görsel Stil (Kurumsal Panel Görünümü)
st.markdown("""
    <style>
    .stNumberInput, .stTextInput { margin-bottom: -15px; }
    .css-1544g2n { padding: 1rem 1rem; }
    </style>
""", unsafe_allow_html=True)

st.title("🏭 Endüstriyel Enerji Optimizasyonu & SCADA Yönetim Paneli")

# --- 1. BÖLÜM: YÖNETİM GRUPLARI ---
c1, c2, c3 = st.columns(3)

with c1:
    st.subheader("🔥 1. DOĞALGAZ & PROSES YÜKLERİ")
    uretim = st.number_input("Üretim Kapasitesi (ton/gün):", value=250)
    hood = st.number_input("Hood Spesifik Tüketim (kWh/ton):", value=535)
    buhar = st.number_input("Buhar Spesifik Tüketim (kWh/ton):", value=603)
    gaz_fiyat = st.number_input("Doğalgaz Birim Fiyatı (TL/Nm3):", value=18.0)
    gaz_isil = st.number_input("Doğalgaz Isıl Değeri (kWh/Nm3):", value=10.64)
    kazan = st.number_input("Brülör / Kazan Verimi (%):", value=90)

with c2:
    st.subheader("⚡ 2. ELEKTRİK ALTYAPISI")
    sabit = st.number_input("Sabit Elektrik Tüketimi (kWh/ton):", value=789)
    ges = st.number_input("Kurulu GES Gücü (MW):", value=15.0)
    res = st.number_input("Kurulu RES Gücü (MW):", value=12.0)
    res_bedel = st.number_input("RES Hat Kullanım Bedeli (TL/kWh):", value=0.35)
    rezistans = st.number_input("Elektrikli Rezistans Verimi (%):", value=98)

with c3:
    st.subheader("🔋 3. MOLTEN SALT (ERİMİŞ TUZ) DEPOLAMA")
    tuz_kap = st.number_input("Tuz Isıl Kapasitesi (MWh Isı):", value=120)
    devreden = st.number_input("Önceki Günden Devreden (MWh):", value=40)
    hedef = st.number_input("Sonraki Güne Hedef Tuz (MWh):", value=40)
    min_kotas = st.number_input("Min. Tuz Kotası (MWh):", value=10)
    sarj_guc = st.number_input("Molten Salt Şarj Gücü (MW):", value=25)
    verim = st.number_input("Molten Salt Çevrim Verimi (%):", value=90)

st.divider()

# --- 2. BÖLÜM: AKSİYON BUTONLARI ---
btn1, btn2 = st.columns(2)
with btn1:
    st.button("🤖 HİBRİD OPTİMİZASYON (Fiyat Bazlı 3'lü Arbitraj)", use_container_width=True)
with btn2:
    st.button("🍰 GELENEKSEL YÖNTEME DÖN (%100 Gaz)", use_container_width=True)

# --- 3. BÖLÜM: SCADA TABLOSU ---
st.subheader("⏱ Saatlik Operasyonel Çizelge")

# Tablo Verisi (Görseldeki tüm sütunlar)
data = {
    "Saat": [f"{h:02}:00" for h in range(24)],
    "Elek. Fiyatı (TL/kWh)": [2.8] * 24,
    "GES?": [False] * 24, 
    "RES?": [True] * 24,
    "Gaz %": [40] * 24, 
    "Tuz %": [30] * 24, 
    "Elk %": [30] * 24,
    "Depo Seviyesi (MWh)": [36.6] * 24,
    "GES (kWh)": [0] * 24, 
    "RES (kWh)": [12000] * 24,
    "Motor (kWh)": [8219] * 24, 
    "Isıtma (kWh)": [11854] * 24,
    "Gaz (Nm3)": [495] * 24,
    "Motor Maliyet (TL)": [23.013] * 24,
    "Isıtma Toplam (TL)": [19.074] * 24,
    "RES Hat Bedeli (TL)": [4.200] * 24,
    "Saatlik Balans": ["0 | 0 TL"] * 24
}

edited_df = st.data_editor(pd.DataFrame(data), use_container_width=True)

# İhracat
output = io.BytesIO()
with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
    edited_df.to_excel(writer, index=False)
st.download_button("📥 Planı Excel Olarak İndir", output.getvalue(), "scada_raporu.xlsx")
