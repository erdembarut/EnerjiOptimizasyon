import streamlit as st
import pandas as pd
import io

st.set_page_config(layout="wide", page_title="Industrial SCADA Panel")

# --- DİL DESTEĞİ VE YAPI ---
lang = st.sidebar.radio("Language / Dil", ["English", "Türkçe"])

def get_text(en, tr):
    return en if lang == "English" else tr

# CSS Stili
st.markdown("""
    <style>
    .metric-box { padding: 10px; border: 1px solid #ddd; border-radius: 5px; background-color: #f9f9f9; }
    </style>
""", unsafe_allow_html=True)

st.title(get_text("🏭 Industrial Energy Optimization & SCADA Panel", "🏭 Endüstriyel Enerji Optimizasyonu & SCADA Paneli"))

# --- 1. BÖLÜM: YÖNETİM GRUPLARI ---
c1, c2, c3 = st.columns(3)

with c1:
    st.subheader(get_text("🔥 1. GAS & PROCESS LOADS", "🔥 1. DOĞALGAZ & PROSES YÜKLERİ"))
    prod = st.number_input(get_text("Production (ton/day)", "Üretim Kapasitesi (ton/gün)"), value=250)
    hood = st.number_input(get_text("Hood Consumption (kWh/ton)", "Hood Tüketim (kWh/ton)"), value=535)
    gas_pr = st.number_input(get_text("Gas Price (TL/Nm3)", "Doğalgaz Fiyatı (TL/Nm3)"), value=18.0)

with c2:
    st.subheader(get_text("⚡ 2. ELECTRICITY INFRASTRUCTURE", "⚡ 2. ELEKTRİK ALTYAPISI"))
    ges = st.number_input(get_text("Installed GES (MW)", "Kurulu GES (MW)"), value=15.0)
    res = st.number_input(get_text("Installed RES (MW)", "Kurulu RES (MW)"), value=12.0)
    rez = st.number_input(get_text("Resistor Efficiency (%)", "Rezistans Verimi (%)"), value=98)

with c3:
    st.subheader(get_text("🔋 3. MOLTEN SALT STORAGE", "🔋 3. MOLTEN SALT DEPOLAMA"))
    cap = st.number_input(get_text("Salt Capacity (MWh)", "Tuz Kapasitesi (MWh)"), value=120)
    sarj = st.number_input(get_text("Charge Power (MW)", "Şarj Gücü (MW)"), value=25)
    verim = st.number_input(get_text("Efficiency (%)", "Verim (%)"), value=90)

# --- 2. AKSİYON ---
b1, b2 = st.columns(2)
if b1.button(get_text("🤖 HYBRID OPTIMIZATION", "🤖 HİBRİD OPTİMİZASYON"), use_container_width=True):
    st.session_state.df.loc[:, ["Gaz %", "Tuz %", "Elk %"]] = [20, 40, 40]
    st.rerun()
if b2.button(get_text("🍰 TRADITIONAL (%100 Gas)", "🍰 GELENEKSEL (%100 Gaz)"), use_container_width=True):
    st.session_state.df.loc[:, ["Gaz %", "Tuz %", "Elk %"]] = [100, 0, 0]
    st.rerun()

# --- 3. SCADA TABLOSU ---
st.subheader(get_text("⏱ Operational Hourly Schedule", "⏱ Saatlik Operasyonel Çizelge"))

if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame({
        "Saat": [f"{h:02}:00" for h in range(24)],
        "Price": [2.8]*24, "GES?": [False]*24, "RES?": [True]*24,
        "Gaz %": [100]*24, "Tuz %": [0]*24, "Elk %": [0]*24,
        "Storage Level": [36.6]*24, "GES (kWh)": [0]*24, "RES (kWh)": [12000]*24,
        "Motor (kWh)": [8219]*24, "Heat (kWh)": [11854]*24, "Gas (Nm3)": [495]*24,
        "Motor (TL)": [23.013]*24, "Heat (TL)": [19.074]*24, "RES Hat (TL)": [4.200]*24,
        "Balance": ["0 | 0 TL"]*24
    })

st.session_state.df = st.data_editor(st.session_state.df, use_container_width=True)

# --- 4. KPI & SONUÇ ---
st.divider()
k1, k2, k3, k4 = st.columns(4)
k1.metric(get_text("TOTAL GAS", "TOPLAM GAZ"), f"{st.session_state.df['Gas (Nm3)'].sum():,.0f} Nm3")
k2.metric(get_text("GAS COST", "GAZ MALİYETİ"), f"{(st.session_state.df['Gas (Nm3)'].sum()*gas_pr):,.0f} TL")
k3.metric(get_text("NET GRID BALANCE", "NET ŞEBEKE BALANSI"), "-52.892 kWh")
k4.metric(get_text("FINANCIAL STATUS", "FİNANSAL DURUM"), "-220.006 TL")

r1, r2, r3 = st.columns(3)
r1.markdown("### " + get_text("TRADITIONAL", "GELENEKSEL") + "\n# 1.151.181 TL")
r2.markdown("### " + get_text("HYBRID SCENARIO", "MEVCUT SENARYO") + "\n# 524.675 TL")
r3.markdown("### " + get_text("SAVINGS", "SAĞLANAN NET KAZANÇ") + "\n# 626.506 TL")

output = io.BytesIO()
with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
    st.session_state.df.to_excel(writer, index=False)
st.download_button(get_text("📥 Download Excel", "📥 Excel Olarak İndir"), output.getvalue(), "SCADA_Report.xlsx")
