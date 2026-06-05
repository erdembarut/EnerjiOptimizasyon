import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(layout="wide", page_title="Endüstriyel Enerji Paneli")

# 1. Başlık ve Üst Kartlar (Input Parametreleri)
st.title("🏭 Endüstriyel Enerji Optimizasyonu & SCADA Yönetim Paneli")

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
    salt_kapasite = st.number_input("Tuz Isıl Kapasitesi (MWh Isı):", value=120)
    salt_verim = st.number_input("Molten Salt Çevrim Verimi (%):", value=90)
    st.metric("Gün Sonu Gerçekleşen Bakiye", "120.0 MWh")

st.divider()

# 2. Hibrit Optimizasyon ve Geleneksel Yöntem Butonları
b1, b2 = st.columns(2)
with b1:
    st.button("🤖 HİBRİT OPTİMİZASYON (Fiyat Bazlı 3'lü Arbitraj)", use_container_width=True)
with b2:
    st.button("🍰 GELENEKSEL YÖNTEME DÖN (%100 Gaz)", use_container_width=True)

# 3. İnteraktif Tablo (SCADA Yönetim Ekranı)
st.subheader("Saatlik Operasyonel Çizelge")

# Örnek veri seti (Sizin tablonuzun yapısı)
data = {
    "Saat": [f"{h:02}:00" for h in range(24)],
    "Elek. Fiyatı": [2.8] * 24,
    "GES?": [True] * 24,
    "RES?": [True] * 24,
    "Gaz %": [100] * 24,
    "Tuz %": [0] * 24,
    "Depo Seviyesi": [43.3] * 24
}
df = pd.DataFrame(data)

# Data Editor: Kullanıcının hücreleri düzenlemesini sağlar
edited_df = st.data_editor(
    df, 
    column_config={
        "GES?": st.column_config.CheckboxColumn(),
        "RES?": st.column_config.CheckboxColumn(),
    },
    use_container_width=True
)

# 4. Hesaplama Mantığı (Örnek)
if st.button("Günlük Maliyeti Hesapla"):
    # Burada editlenen tablodan gelen verilerle toplam maliyet hesaplanacak
    st.success("Toplam Maliyet: 450.000 TL")
