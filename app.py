import streamlit as st
import pulp
import pandas as pd
import requests
import numpy as np
from datetime import datetime

st.set_page_config(layout="wide")
st.title("Enerji Maliyet Optimizasyon Paneli")

# 1. Veri Hazırlama
def get_epias_prices():
    url = "https://seffaflik.epias.com.tr/v1/market/day-ahead-market/market-clearing-price"
    headers = {'User-Agent': 'Mozilla/5.0'}
    today = datetime.now().strftime("%Y-%m-%dT00:00:00+03:00")
    try:
        response = requests.get(url, params={"startDate": today, "endDate": today}, headers=headers, timeout=5)
        if response.status_code == 200:
            return pd.DataFrame(response.json()['body']['mcpList'])
        else:
            raise Exception()
    except:
        st.warning("Canlı veri alınamadı, simülasyon verisi kullanılıyor.")
        return pd.DataFrame({'date': [f"{h}:00" for h in range(24)], 'price': [500 + (100 * np.sin(h/24 * 2 * np.pi)) for h in range(24)]})

# 2. Solver (Üst Sınır Kısıtlı)
def solve_energy(prices_df, prod_load, max_grid_limit, manual_mode, manual_mw):
    periods = range(len(prices_df))
    model = pulp.LpProblem("Cost_Minimization", pulp.LpMinimize)
    
    p_grid = pulp.LpVariable.dicts("Grid", periods, lowBound=0)
    p_charge = pulp.LpVariable.dicts("Charge", periods, lowBound=0, upBound=20)
    p_discharge = pulp.LpVariable.dicts("Discharge", periods, lowBound=0, upBound=20)
    soc = pulp.LpVariable.dicts("SOC", periods, lowBound=0, upBound=100)
    
    model += pulp.lpSum([p_grid[t] * prices_df['price'][t] for t in periods])
    
    for t in periods:
        # ÜST SINIR KISITI: Şebekeden çekilen güç, belirlenen limiti aşamaz
        model += p_grid[t] <= max_grid_limit
        
        if manual_mode: model += p_charge[t] == manual_mw
        model += p_grid[t] + p_discharge[t] == prod_load + p_charge[t]
        
        if t > 0:
            model += soc[t] == soc[t-1] + (p_charge[t] * 0.95) - (p_discharge[t] / 0.95) - (soc[t-1] * 0.005)
        else:
            model += soc[t] == p_charge[t]
            
    model.solve(pulp.PULP_CBC_CMD(msg=0))
    return {"Grid_Alımı": [p_grid[t].varValue for t in periods], "Şarj_Gücü": [p_charge[t].varValue for t in periods], "Deşarj_Gücü": [p_discharge[t].varValue for t in periods]}

# 3. Arayüz
col1, col2 = st.columns(2)
with col1:
    production_load = st.number_input("Sabit Üretim Yükü (MW)", value=20.0)
    max_grid_limit = st.number_input("Maksimum Şebeke Gücü Sınırı (MW)", value=25.0, help="Şebekeden çekebileceğiniz maksimum güç limiti.")
with col2:
    manual_mode = st.checkbox("Manuel Tuz Şarjı")
    manual_mw = st.number_input("Manuel Şarj Gücü (MW)", value=10.0, disabled=not manual_mode)

if st.button("Verileri Hazırla / Güncelle"):
    st.session_state['prices'] = get_epias_prices()
    st.success("Veriler hazır!")

if st.button("Solver'ı Çalıştır"):
    if 'prices' in st.session_state:
        results = solve_energy(st.session_state['prices'], production_load, max_grid_limit, manual_mode, manual_mw)
        st.line_chart(pd.DataFrame(results))
    else:
        st.warning("Lütfen önce verileri hazırlayın.")
