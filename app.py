import streamlit as st
import pandas as pd
import numpy as np
import io

# --- Arayüz Ayarları ---
st.set_page_config(page_title="Endüstriyel Enerji SCADA", layout="wide")

# Modern Dashboard Stili
st.markdown("""
    <style>
    .stMetric { background-color: #f0f2f6; padding: 15px; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

st.title("🔋 Endüstriyel Enerji SCADA Paneli")

# --- Dashboard Parametreleri (Giriş Kartları) ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Tesis Yükü", "20.0 MW")
with col2:
    st.metric("Anlık Fiyat", "2.85 TL/kWh")
with col3:
    soc_min_limit = st.slider("Min. Depo Seviyesi (%)", 0, 100, 20)
with col4:
    st.metric("Alt Limit Güvenliği", f"%{soc_min_limit}")

st.divider()

# --- Veri Giriş Tablosu ---
st.subheader("⏱ Saatlik Operasyonel Çizelge")
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame({
        "Saat": [f"{h:02}:00" for h in range(24)],
        "Şarj_Deşarj_MW": [0.0] * 24,
        "Gaz_Tüketim_MWh": [20.0] * 24
    })

edited_df = st.data_editor(st.session_state.data, use_container_width=True, num_rows="fixed")

# --- Dinamik SOC (Depo Seviyesi) Hesaplama Motoru ---
def calculate_soc(df, min_limit):
    soc = [40.0] # Başlangıç: %40 dolu
    for i in range(1, len(df)):
        # Denklem: Soc(t) = Soc(t-1) + Şarj - Kayıp
        new_soc = soc[-1] + (df.loc[i-1, "Şarj_Deşarj_MW"]) - 0.5 
        # Kritik Kısıt: Alt limitten aşağı düşmesine izin verme
        soc.append(max(min_limit, min(100, new_soc))) 
    return soc

edited_df["Depo_Seviyesi"] = calculate_soc(edited_df, soc_min_limit)

# --- Görselleştirme ---
st.subheader("📊 Operasyonel Analiz")
c1, c2 = st.columns(2)
with c1:
    st.line_chart(edited_df[["Depo_Seviyesi"]])
with c2:
    st.bar_chart(edited_df[["Şarj_Deşarj_MW"]])

# --- Excel İhracat Fonksiyonu ---
def to_excel(df):
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Enerji_Plani')
    writer.close()
    return output.getvalue()

# --- Onay ve İndirme Butonları ---
col_btn1, col_btn2 = st.columns([1, 4])
with col_btn1:
    if st.button("Sistemi Onayla"):
        st.success("Senaryo onaylandı!")

with col_btn2:
    excel_data = to_excel(edited_df)
    st.download_button(
        label="📥 Planı Excel Olarak İndir",
        data=excel_data,
        file_name='Enerji_Optimizasyon_Plani.xlsx',
        mime='application/vnd.ms-excel'
    )
