import streamlit as st
import pulp
import pandas as pd
import requests
from datetime import datetime

# Arayüz
st.title("Enerji Maliyet Optimizasyon Paneli")
production_load = st.number_input("Sabit Üretim Yükü (MW)", min_value=1.0, value=20.0)

# Solver Fonksiyonu
def solve_energy(prices, prod_load):
    # Fiyat verisinin doğruluğunu kontrol et
    if prices is None: return None
    
    # 24 saatlik periyot
    periods = range(len(prices))
    model = pulp.LpProblem("Cost_Minimization", pulp.LpMinimize)
    
    # Değişkenler
    p_grid = pulp.LpVariable.dicts("Grid", periods, lowBound=0)
    p_charge = pulp.LpVariable.dicts("Charge", periods, lowBound=0, upBound=20)
    p_discharge = pulp.LpVariable.dicts("Discharge", periods, lowBound=0, upBound=20)
    soc = pulp.LpVariable.dicts("SOC", periods, lowBound=0, upBound=100)
    
    # Amaç Fonksiyonu: Toplam maliyeti minimize et
    model += pulp.lpSum([p_grid[t] * prices['price'][t] for t in periods])
    
    # Kısıtlar
    heat_loss_rate = 0.005 # Saatlik kayıp katsayısı
    
    for t in periods:
        # Enerji Dengesi: Şebeke + Deşarj - Şarj = Sabit Üretim Yükü
        model += p_grid[t] + p_discharge[t] - p_charge[t] == prod_load
        
        # SOC Güncelleme
        if t > 0:
            model += soc[t] == soc[t-1] + (p_charge[t] * 0.95) - (p_discharge[t] / 0.95) - (soc[t-1] * heat_loss_rate)
        else:
            model += soc[t] == p_charge[t]
            
    model.solve()
    return {t: p_grid[t].varValue for t in periods}

# Çalıştırma
if st.button("Solver'ı Çalıştır"):
    # Örnek EPİAŞ veri çekimi veya session state'den okuma
    if 'prices' in st.session_state:
        results = solve_energy(st.session_state['prices'], production_load)
        st.success("Maliyet optimize edildi.")
        st.line_chart(pd.DataFrame(results, index=[0]).T)
