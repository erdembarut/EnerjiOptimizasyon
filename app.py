import streamlit as st
import pulp
import pandas as pd
import requests

# 1. DİL AYARLARI
translations = {
    "TR": {"title": "Enerji Optimizasyon Paneli", "manual": "Manuel Tuz Şarjı (MW)", "run": "Solver'ı Çalıştır", "success": "Optimizasyon Tamamlandı!", "price_fetch": "EPİAŞ Verileri Alınıyor..."},
    "EN": {"title": "Energy Optimization Panel", "manual": "Manual Salt Charge (MW)", "run": "Run Solver", "success": "Optimization Completed!", "price_fetch": "Fetching EPİAŞ Data..."}
}

st.set_page_config(layout="wide")
lang = st.sidebar.selectbox("Dil / Language", ["TR", "EN"])
t = translations[lang]

st.title(t["title"])

# 2. GİRDİLER
col1, col2 = st.columns(2)
with col1:
    manual_mode = st.checkbox(t["manual"])
    manual_mw = st.number_input(t["manual"], min_value=0.0, max_value=50.0, value=10.0, disabled=not manual_mode)

with col2:
    if st.button("EPİAŞ Verilerini Güncelle"):
        st.info(t["price_fetch"])
        # EPİAŞ API entegrasyonu için buraya veri çekme kodu eklenecek
        st.success("Fiyatlar güncel.")

# 3. OPTİMİZASYON MANTIĞI
def solve_energy(manual_val, is_manual):
    model = pulp.LpProblem("Energy_Optimization", pulp.LpMinimize)
    periods = range(288) # 24 saat * 12 (5 dakikalık periyotlar)
    charge_power = pulp.LpVariable.dicts("Charge", periods, lowBound=0, upBound=20)
    soc = pulp.LpVariable.dicts("SOC", periods, lowBound=0)
    
    heat_loss_rate = 0.005 / 12 # Saatlik %0.5 kayıp, 12'ye bölündü
    
    for i in periods:
        if is_manual:
            model += charge_power[i] == manual_val
        
        # Heat Loss Denklem (SOCt = SOCt-1 + Şarj - Kayıp)
        if i > 0:
            model += soc[i] == soc[i-1] + charge_power[i] - (soc[i-1] * heat_loss_rate)
        else:
            model += soc[i] == charge_power[i]
            
    model.solve()
    return {i: charge_power[i].varValue for i in periods}

# 4. ÇALIŞTIRMA
if st.button(t["run"]):
    results = solve_energy(manual_mw, manual_mode)
    st.success(t["success"])
    st.line_chart(list(results.values()))
