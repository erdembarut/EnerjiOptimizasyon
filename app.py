import streamlit as st
import pulp
import pandas as pd
import requests
from datetime import datetime

# Arayüz Ayarları
st.set_page_config(layout="wide")
st.title("Enerji Maliyet Optimizasyon Paneli")

# 1. EPİAŞ Veri Çekme (Güncellenmiş: Header eklendi)
def get_epias_prices():
    url = "https://seffaflik.epias.com.tr/v1/market/day-ahead-market/market-clearing-price"
    # Tarih formatını API'nin istediği ISO formatına uygun yapıyoruz
    today = datetime.now().strftime("%Y-%m-%dT00:00:00+03:00")
    params = {"startDate": today, "endDate": today}
    
    # API'yi tarayıcı gibi kandırmak için headers ekliyoruz
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            data = response.json()['body']['mcpList']
            return pd.DataFrame(data)
        else:
            return None
    except Exception as e:
        return None

# 2. Solver Optimizasyon Fonksiyonu
def solve_energy(prices_df, prod_load, manual_mode, manual_mw):
    periods = range(len(prices_df))
    model = pulp.LpProblem("Cost_Minimization", pulp.LpMinimize)
    
    p_grid = pulp.LpVariable.dicts("Grid", periods, lowBound=0)
    p_charge = pulp.LpVariable.dicts("Charge", periods, lowBound=0, upBound=20)
    p_discharge = pulp.LpVariable.dicts("Discharge", periods, lowBound=0, upBound=20)
    soc = pulp.LpVariable.dicts("SOC", periods, lowBound=0, upBound=100)
    
    model += pulp.lpSum([p_grid[t] * prices_df['price'][t] for t in periods])
    
    heat_loss_rate = 0.005
    for t in periods:
        if manual_mode:
            model += p_charge[t] == manual_mw
        model += p_grid[t] + p_discharge[t] == prod_load + p_charge[t]
        if t > 0:
            model += soc[t] == soc[t-1] + (p_charge[t] * 0.95) - (p_discharge[t] / 0.95) - (soc[t-1] * heat_loss_rate)
        else:
            model += soc[t] == p_charge[t]
            
    model.solve(pulp.PULP_CBC_CMD(msg=0))
    return {"grid": [p_grid[t].varValue for t in periods], "charge": [p_charge[t].varValue for t in periods], "discharge": [p_discharge[t].varValue for t in periods]}

# 3. Arayüz
production_load = st.number_input("Sabit Üretim Yükü (MW)", min_value=1.0, value=20.0)
manual_mode = st.checkbox("Manuel Tuz Şarjı")
manual_mw = st.number_input("Manuel Şarj Gücü (MW)", min_value=0.0, max_value=20.0, value=10.0, disabled=not manual_mode)

if st.button("EPİAŞ Verilerini Güncelle"):
    df = get_epias_prices()
    if df is not None:
        st.session_state['prices'] = df
        st.success("Veriler başarıyla alındı!")
        st.dataframe(df.head(5))
    else:
        st.error("Veri alınamadı. Lütfen tekrar deneyin.")

if st.button("Solver'ı Çalıştır"):
    if 'prices' in st.session_state:
        results = solve_energy(st.session_state['prices'], production_load, manual_mode, manual_mw)
        st.success("Optimizasyon tamamlandı!")
        st.line_chart(pd.DataFrame(results, index=range(len(results["grid"]))))
    else:
        st.warning("Önce EPİAŞ verilerini güncelleyin.")
