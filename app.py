import streamlit as st
import pandas as pd
import io

st.set_page_config(layout="wide", page_title="Endüstriyel Enerji SCADA")

st.title("🏭 Endüstriyel Enerji Optimizasyonu & SCADA Yönetim Paneli")

# --- 1. GİRDİ PARAMETRELERİ ---
c1, c2, c3 = st.columns(3)
with c1:
    st.subheader("🔥 1. DOĞALGAZ & PROSES")
    uretim = st.number_input("Üretim (ton/gün):", value=250.0, step=1.0, min_value=0.0)
    hood = st.number_input("Hood Tüketim (kWh/ton):", value=535.0, step=1.0, min_value=0.0)
    gaz_fiyat = st.number_input("Gaz Fiyatı (TL/Nm3):", value=18.00, step=0.01, min_value=0.0)
with c2:
    st.subheader("⚡ 2. ELEKTRİK ALTYAPISI")
    ges = st.number_input("Kurulu GES (MW):", value=15.0, step=1.0, min_value=0.0)
    res = st.number_input("Kurulu RES (MW):", value=12.0, step=1.0, min_value=0.0)
    elec_fiyat = st.number_input("Elek. Fiyatı (TL/kWh):", value=2.80, step=0.01, min_value=0.0)
with c3:
    st.subheader("🔋 3. MOLTEN SALT DEPOLAMA")
    tuz_kap = st.number_input("Tuz Kapasitesi (MWh):", value=120.0, step=1.0, min_value=0.0)
    verim = st.number_input("Sistem Verimi (%):", value=90.0, step=1.0, min_value=0.0)

# --- 2. HESAPLAMA MOTORU (Fiziksel Tutarlılık) ---
# Geleneksel Yöntem (Baseline): %100 Gaz
def calculate_baseline(prod, hood, gas_fiyat):
    if prod <= 0: return 0.0
    return (prod * hood * gas_fiyat) / 10.64  # Basitleştirilmiş Baz Maliyet

baseline_cost = calculate_baseline(uretim, hood, gaz_fiyat)

# --- 3. SCADA TABLOSU ---
st.subheader("⏱ Saatlik Operasyonel Çizelge")
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame({
        "Saat": [f"{h:02}:00" for h in range(24)],
        "Gaz %": [100.0] * 24, "Tuz %": [0.0] * 24, "Elk %": [0.0] * 24,
        "Gaz (Nm3)": [0.0] * 24, "Elk (kWh)": [0.0] * 24
    })

# Butonlar
b1, b2 = st.columns(2)
if b1.button("🤖 HİBRİD OPTİMİZASYON"):
    st.session_state.df.loc[:, ["Gaz %", "Tuz %", "Elk %"]] = [20.0, 40.0, 40.0]
    st.rerun()
if b2.button("🍰 GELENEKSEL YÖNTEM (%100 Gaz)"):
    st.session_state.df.loc[:, ["Gaz %", "Tuz %", "Elk %"]] = [100.0, 0.0, 0.0]
    st.rerun()

edited_df = st.data_editor(st.session_state.df, use_container_width=True)
st.session_state.df = edited_df

# --- 4. SONUÇLAR VE KAZANÇ (Dinamik) ---
# Mevcut maliyet tablodan hesaplanır
current_gas_cost = (edited_df["Gaz (Nm3)"].sum() * gaz_fiyat)
current_elec_cost = (edited_df["Elk (kWh)"].sum() * elec_fiyat)
current_cost = current_gas_cost + current_elec_cost

if uretim <= 0: current_cost = 0.0

st.divider()
k1, k2, k3 = st.columns(3)
k1.metric("GELENEKSEL YÖNTEM", f"{baseline_cost:,.2f} TL")
k2.metric("MEVCUT SENARYO", f"{current_cost:,.2f} TL")
k3.metric("SAĞLANAN NET KAZANÇ", f"{max(0, baseline_cost - current_cost):,.2f} TL")

# Excel
output = io.BytesIO()
with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
    edited_df.to_excel(writer, index=False)
st.download_button("📥 Excel İndir", output.getvalue(), "scada_raporu.xlsx")
