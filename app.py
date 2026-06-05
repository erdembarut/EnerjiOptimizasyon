import streamlit as st
import pulp
import pandas as pd
import requests
import numpy as np
from datetime import datetime

# --- Arayüz Yapılandırması ---
st.set_page_config(page_title="Enerji Optimizasyon Paneli", layout="wide")
st.title("🏭 Enerji Maliyet & Üretim Optimizasyon Paneli")

# --- Veri Çekme / Simülasyon ---
def get_epias_data():
    url = "https://seffaflik.epias.com.tr/v1/market/day-ahead-market/market-clearing-price"
    today = datetime.now().strftime("%Y-%m-%dT00:00:00+03:00")
    try:
        response = requests.get(url, params={"startDate": today, "endDate": today}, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
        if response.status_code == 200:
            return pd.DataFrame(response.json()['body']['mcpList'])
        raise Exception()
    except:
        st.warning("Canlı veri alınamadı, simülasyon verisi kullanılıyor.")
        return pd.DataFrame({'date': [f"{h:02}:00" for h in range(24)], 'price': [500 + (100 * np.sin(h/24 * 2 * np.pi)) for h in range(24)]})

# --- Solver Motoru ---
def solve_energy(prices_df, prod_load, max_grid, manual_mode, manual_mw):
    periods = range(len(prices_df))
    model = pulp.LpProblem("Cost_Minimization", pulp.LpMinimize)
    
    p_grid = pulp.LpVariable.dicts("Grid", periods, lowBound=0)
    p_charge = pulp.LpVariable.dicts("Charge", periods, lowBound=0, upBound=20)
    p_discharge = pulp.LpVariable.dicts("Discharge", periods, lowBound=0, upBound=20)
    soc = pulp.LpVariable.dicts("SOC", periods, lowBound=0, upBound=100)
    
    model += pulp.lpSum([p_grid[t] * prices_df['price'][t] for t in periods])
    
    for t in periods:
        model += p_grid[t] <= max_grid
        if manual_mode: model += p_charge[t] == manual_mw
        model += p_grid[t] + p_discharge[t] == prod_load + p_charge[t]
        
        if t > 0:
            model += soc[t] == soc[t-1] + (p_charge[t] * 0.95) - (p_discharge[t] / 0.95) - (soc[t-1] * 0.005)
        else:
            model += soc[t] == p_charge[t]
            
    model.solve(pulp.PULP_CBC_CMD(msg=0))
    
    return {
        "Grid_MW": [p_grid[t].varValue for t in periods],
        "Şarj_MW": [p_charge[t].varValue for t in periods],
        "Deşarj_MW": [p_discharge[t].varValue for t in periods]
    }

# --- Dashboard Layout ---
col1, col2, col3 = st.columns(3)
with col1:
    prod_load = st.number_input("Üretim Yükü (MW)", value=20.0)
with col2:
    max_grid = st.number_input("Şebeke Limit (MW)", value=25.0)
with col3:
    manual_mode = st.checkbox("Manuel Şarj")
    manual_mw = st.number_input("Manuel Şarj (MW)", value=10.0, disabled=not manual_mode)

if st.button("🚀 Optimizasyonu Başlat"):
    prices = get_epias_prices()
    results = solve_energy(prices, prod_load, max_grid, manual_mode, manual_mw)
    
    # Görselleştirme
    res_df = pd.DataFrame(results, index=range(len(results["Grid_MW"])))
    st.line_chart(res_df)
    
    # Metrikler ve Tablo
    base_cost = sum(prod_load * p for p in prices['price'])
    opt_cost = sum(results["Grid_MW"][t] * prices['price'][t] for t in range(len(prices)))
    
    st.metric("Tahmini Günlük Tasarruf (TL)", f"{base_cost - opt_cost:,.2f} TL")
    st.subheader("Saatlik Aksiyon Planı")
    st.dataframe(res_df.style.highlight_max(axis=0))
