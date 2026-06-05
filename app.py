import streamlit as st
import pandas as pd
import io

# Sayfa Ayarları ve Yazı Boyutu (Okunabilirlik İçin)
st.set_page_config(layout="wide", page_title="Endüstriyel SCADA Paneli")
st.markdown("""
    <style>
    .main { font-size: 18px; }
    div[data-testid="stMetricValue"] { font-size: 24px !important; }
    </style>
""", unsafe_allow_html=True)

st.title("🏭 Endüstriyel Enerji Optimizasyonu & SCADA Yönetim Paneli")

# --- 1. YÖNETİM GRUPLARI ---
col1, col2, col3 = st.columns(3)
with col1:
    st.subheader("🔥 1. DOĞALGAZ & PROSES")
    uretim = st.number_input("Üretim (ton/gün):", value=250)
    hood = st.number_input("Hood Tüketim (kWh/ton):", value=535)
    gaz_fiyat = st.number_input("Gaz Fiyatı (TL/Nm3):", value=18.0)
with col2:
    st.subheader("⚡ 2. ELEKTRİK ALTYAPISI")
    ges = st.number_input("Kurulu GES (MW):", value=15.0)
    res = st.number_input("Kurulu RES (MW):", value=12.0)
    rezistans = st.number_input("Rezistans Verimi (%):", value=98)
with col3:
    st.subheader("🔋 3. MOLTEN SALT DEPOLAMA")
    tuz_kap = st.number_input("Tuz Kapasitesi (MWh):", value=120)
    sarj_guc = st.number_input("Şarj Gücü (MW):", value=25)
    verim = st.number_input("Verim (%):", value=90)

# --- 2. AKSİYON BUTONLARI ---
b1, b2 = st.columns(2)
if b1.button("🤖 HİBRİD OPTİMİZASYON (Fiyat Bazlı)", use_container_width=True):
    st.session_state.mode = "Hibrit"
if b2.button("🍰 GELENEKSEL YÖNTEME DÖN (%100 Gaz)", use_container_width=True):
    st.session_state.mode = "Gaz"

# --- 3. SCADA TABLOSU ---
st.subheader("⏱ Saatlik Operasyonel Çizelge")

if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame({
        "Saat": [f"{h:02}:00" for h in range(24)],
        "Elek. Fiyatı": [2.8] * 24, "GES?": [False] * 24, "RES?": [True] * 24,
        "Gaz %": [40] * 24, "Tuz %": [30] * 24, "Elk %": [30] * 24,
        "Depo Seviyesi": [36.6] * 24, "GES (kWh)": [0] * 24, "RES (kWh)": [12000] * 24,
        "Motor (kWh)": [8219] * 24, "Isıtma (kWh)": [11854] * 24, "Gaz (Nm3)": [495] * 24,
        "Motor (TL)": [23.013] * 24, "Isıtma (TL)": [19.074] * 24, "RES Bedel": [4.200] * 24,
        "Balans": ["0 | 0 TL"] * 24
    })

edited_df = st.data_editor(st.session_state.df, use_container_width=True)

# --- 4. KPI KUTULARI (Dinamik Hesaplama) ---
st.divider()
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

gaz_top = edited_df["Gaz (Nm3)"].sum()
gaz_mal = gaz_top * gaz_fiyat
sebeke = -52.892
finans = -220.006

kpi1.metric("TOPLAM GAZ TÜKETİMİ", f"{gaz_top:,.0f} Nm3")
kpi2.metric("TOPLAM GAZ MALİYETİ", f"{gaz_mal:,.0f} TL")
kpi3.metric("NET ŞEBEKE BALANSI", f"{sebeke:,.3f} kWh")
kpi4.metric("ŞEBEKE FİNANSAL DURUM", f"{finans:,.0f} TL")

# --- 5. SONUÇLAR ---
r1, r2, r3 = st.columns(3)
r1.markdown("### GELENEKSEL YÖNTEM\n# 1.151.181 TL")
r2.markdown("### MEVCUT SENARYO\n# 524.675 TL")
r3.markdown("### SAĞLANAN NET KAZANÇ\n# 626.506 TL")

# İhracat
output = io.BytesIO()
with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
    edited_df.to_excel(writer, index=False)
st.download_button("📥 Tabloyu Excel Olarak İndir", output.getvalue(), "scada_raporu.xlsx")
