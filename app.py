import streamlit as st
import pandas as pd
import numpy as np

# Arayüz Ayarları
st.set_page_config(layout="wide", page_title="Energy SCADA Pro")

st.title("🔋 Endüstriyel Enerji SCADA Paneli")

# 1. Dashboard Parametreleri (Giriş Kartları)
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Tesis Yükü", "20.0 MW")
with col2:
    st.metric("Anlık Fiyat", "2.85 TL/kWh")
with col3:
    soc_min_limit = st.slider("Min. Depo Seviyesi (%)", 0, 100, 20)
with col4:
    st.metric("Alt Limit", f"%{soc_min_limit}")

st.divider()

# 2. İnteraktif Veri Girişi
st.subheader("⏱ Saatlik Operasyonel Çizelge")
df = pd.DataFrame({
    "Saat": [f"{h:02}:00" for h in range(24)],
    "Şarj_Deşarj_MW": [0.0] * 24,
    "Gaz_Tüketim_MWh": [20.0] * 24
})

edited_df = st.data_editor(df, use_container_width=True)

# 3. Dinamik SOC (Depo Seviyesi) Hesaplama Motoru
def calculate_soc(df, min_limit):
    soc = [40.0] # Başlangıç: %40 dolu
    for i in range(1, len(df)):
        # Denklem: Soc(t) = Soc(t-1) + Şarj - Kayıp
        new_soc = soc[-1] + (edited_df.loc[i-1, "Şarj_Deşarj_MW"]) - 0.5 
        # Kritik Kısıt: Alt limitten aşağı düşmesine izin verme
        soc.append(max(min_limit, min(100, new_soc))) 
    return soc

edited_df["Depo_Seviyesi"] = calculate_soc(edited_df, soc_min_limit)

# 4. Görselleştirme
st.subheader("📊 Operasyonel Analiz")
c1, c2 = st.columns(2)
with c1:
    st.line_chart(edited_df[["Depo_Seviyesi"]])
with c2:
    st.bar_chart(edited_df[["Şarj_Deşarj_MW"]])

if st.button("Sistemi Onayla ve Raporla"):
    st.success("Operasyonel senaryo alt limitler (%"+str(soc_min_limit)+") gözetilerek onaylandı.")
