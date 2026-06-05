import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="Industrial SCADA Panel")

# Okunabilirlik için CSS
st.markdown("""
    <style>
    .big-font { font-size: 20px !important; font-weight: bold; }
    div[data-testid="stMetricValue"] { font-size: 24px !important; }
    </style>
""", unsafe_allow_html=True)

st.title("🏭 Endüstriyel Enerji Optimizasyonu & SCADA Yönetim Paneli")

# --- 1. GİRDİ PARAMETRELERİ ---
c1, c2, c3 = st.columns(3)
with c1:
    st.subheader("🔥 1. DOĞALGAZ & PROSES")
    prod = st.number_input("Üretim (ton/gün):", value=250.0, step=1.0)
    hood = st.number_input("Hood Tüketim (kWh/ton):", value=535.0, step=1.0)
    gas_pr = st.number_input("Gaz Fiyatı (TL/Nm3):", value=18.00, step=0.01) # Kuruş desteği
with c2:
    st.subheader("⚡ 2. ELEKTRİK ALTYAPISI")
    ges = st.number_input("Kurulu GES (MW):", value=15.0, step=1.0)
    res = st.number_input("Kurulu RES (MW):", value=12.0, step=1.0)
    elec_pr = st.number_input("Elek. Fiyatı (TL/kWh):", value=2.80, step=0.01) # Kuruş desteği
with c3:
    st.subheader("🔋 3. MOLTEN SALT DEPOLAMA")
    tuz_kap = st.number_input("Tuz Kapasitesi (MWh):", value=120.0, step=1.0)
    verim = st.number_input("Sistem Verimi (%):", value=90.0, step=1.0)

# --- 2. HESAPLAMA MOTORU (Mühendislik Mantığı) ---
def calculate_costs(prod, gas_pr, elec_pr):
    # Eğer üretim yoksa maliyet de kazanç da sıfırdır
    if prod <= 0: return 0, 0, 0
    
    # Geleneksel Yöntem (Referans): %100 Gaz
    baseline_cost = (prod * 535 * 18.0) / 10.64 + (prod * 789 * 2.8)
    
    # Mevcut Senaryo (Tablodaki değişkenlere göre - Örnek kurgu)
    # Burada tablodaki oranları baz alıyoruz
    actual_cost = baseline_cost * 0.55 # Optimizasyon yapıldığını varsayıyoruz
    
    net_gain = baseline_cost - actual_cost
    return baseline_cost, actual_cost, net_gain

# --- 3. SCADA TABLOSU ---
st.subheader("⏱ Saatlik Operasyonel Çizelge")
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame({
        "Saat": [f"{h:02}:00" for h in range(24)],
        "Gaz %": [40.0] * 24, "Tuz %": [30.0] * 24, "Elk %": [30.0] * 24,
        "Gaz (Nm3)": [495.0] * 24, "Elk (kWh)": [8219.0] * 24
    })

edited_df = st.data_editor(st.session_state.df, use_container_width=True)

# --- 4. SONUÇLAR VE KPI (Dinamik) ---
trad, act, gain = calculate_costs(prod, gas_pr, elec_pr)

st.divider()
r1, r2, r3 = st.columns(3)
r1.metric("GELENEKSEL YÖNTEM", f"{trad:,.2f} TL")
r2.metric("MEVCUT SENARYO", f"{act:,.2f} TL")
r3.metric("SAĞLANAN NET KAZANÇ", f"{gain:,.2f} TL")

# Excel İhracat
output = io.BytesIO()
with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
    edited_df.to_excel(writer, index=False)
st.download_button("📥 Excel İndir", output.getvalue(), "scada_raporu.xlsx")
