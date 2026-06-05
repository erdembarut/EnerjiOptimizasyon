import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="Endüstriyel SCADA")

st.title("🏭 Endüstriyel Enerji Optimizasyonu & SCADA Yönetim Paneli")

# 1. BÖLÜM: ÜST PANEL (Giriş Değerleri)
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("🔥 Doğalgaz & Proses")
    uretim = st.number_input("Üretim (ton/gün):", value=250)
    gaz_fiyat = st.number_input("Doğalgaz Fiyatı (TL):", value=18.0)

with col2:
    st.subheader("⚡ Elektrik Altyapısı")
    ges_gucu = st.number_input("GES Gücü (MW):", value=15.0)
    res_gucu = st.number_input("RES Gücü (MW):", value=12.0)

with col3:
    st.subheader("🔋 Molten Salt Depolama")
    salt_kapasite = st.number_input("Tuz Kapasitesi (MWh):", value=120)
    soc_limit = st.slider("Min. Depo Seviyesi (%)", 0, 100, 20)

st.divider()

# 2. BÖLÜM: HİBRİT OPTİMİZASYON BUTONLARI
c_btn1, c_btn2 = st.columns(2)
with c_btn1:
    st.button("🤖 HİBRİT OPTİMİZASYON", use_container_width=True)
with c_btn2:
    st.button("🍰 GELENEKSEL YÖNTEM", use_container_width=True)

# 3. BÖLÜM: SCADA TABLOSU (Matematiksel Modelimiz)
st.subheader("⏱ Saatlik Operasyonel Çizelge")
df = pd.DataFrame({
    "Saat": [f"{h:02}:00" for h in range(24)],
    "Elek. Fiyatı": [2.8] * 24,
    "Şarj_Deşarj_MW": [0.0] * 24,
    "Depo Seviyesi": [40.0] * 24
})

# Matematiksel motorumuzu buraya entegre edebiliriz
edited_df = st.data_editor(df, use_container_width=True)
