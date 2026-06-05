import streamlit as st
import pandas as pd
import numpy as np
import io

st.set_page_config(layout="wide", page_title="Endüstriyel SCADA Paneli")

# Görsel Stil
st.markdown("""
    <style>
    .card { background-color: #f8f9fa; border: 1px solid #dee2e6; padding: 20px; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

st.title("🏭 Endüstriyel Enerji Optimizasyonu & SCADA Yönetim Paneli")

# --- 1. BÖLÜM: YÖNETİM GRUPLARI ---
c1, c2, c3 = st.columns(3)

with c1:
    st.subheader("🔥 1. DOĞALGAZ & PROSES YÜKLERİ")
    uretim = st.number_input("Üretim Kapasitesi (ton/gün):", value=250)
    hood = st.number_input("Hood Spesifik Tüketim (kWh/ton):", value=535)
    buhar = st.number_input("Buhar Spesifik Tüketim (kWh/ton):", value=603)
    gaz_fiyat = st.number_input("Doğalgaz Birim Fiyatı (TL/Nm3):", value=18.0)
    gaz_isil = st.number_input("Doğalgaz Isıl Değeri (kWh/Nm3):", value=10.64)
    kazan = st.number_input("Brülör / Kazan Verimi (%):", value=90)

with c2:
    st.subheader("⚡ 2. ELEKTRİK ALTYAPISI")
    sabit = st.number_input("Sabit Elektrik Tüketimi (kWh/ton):", value=789)
    ges = st.number_input("Kurulu GES Gücü (MW):", value=15.0)
    res = st.number_input("Kurulu RES Gücü (MW):", value=12.0)
    res_bedel = st.number_input("RES Hat Kullanım Bedeli (TL/kWh):", value=0.35)
    rezistans = st.number_input("Elektrikli Rezistans Verimi (%):", value=98)

with c3:
    st.subheader("🔋 3. MOLTEN SALT (ERİMİŞ TUZ) DEPOLAMA")
    tuz_kap = st.number_input("Tuz Isıl Kapasitesi (MWh Isı):", value=120)
    devreden = st.number_input("Önceki Günden Devreden (MWh):", value=40)
    hedef = st.number_input("Sonraki Güne Hedef Tuz (MWh):", value=40)
    min_kotas = st.number_input("Min. Tuz Kotası (MWh):", value=10)
    sarj_guc = st.number_input("Molten Salt Şarj Gücü (MW):", value=25)
    verim = st.number_input("Molten Salt Çevrim Verimi (%):", value=90)

# --- 2. BÖLÜM: AKSİYON BUTONLARI ---
btn1, btn2 = st.columns(2)
with btn1:
    st.button("🤖 HİBRİD OPTİMİZASYON (Fiyat Bazlı 3'lü Arbitraj)", use_container_width=True)
with btn2:
    st.button("🍰 GELENEKSEL YÖNTEME DÖN (%100 Gaz)", use_container_width=True)

# --- 3. BÖLÜM: SCADA TABLOSU ---
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

# Tablo düzenleme alanı
edited_df = st.data_editor(st.session_state.df, use_container_width=True)

# --- 4. BÖLÜM: KPI KUTULARI (Görseldeki o kutular) ---
st.divider()
c_kpi1, c_kpi2, c_kpi3, c_kpi4 = st.columns(4)

# Dinamik Hesaplama
gaz_toplam = edited_df["Gaz (Nm3)"].sum()
gaz_maliyet = gaz_toplam * gaz_fiyat
sebeke_balans = -52.892 # Örnek hesaplama
finansal_durum = -220.006

c_kpi1.metric("TOPLAM GAZ TÜKETİMİ", f"{gaz_toplam:,.0f} Nm3")
c_kpi2.metric("TOPLAM GAZ MALİYETİ", f"{gaz_maliyet:,.0f} TL")
c_kpi3.metric("NET ŞEBEKE BALANSI", f"{sebeke_balans:,.3f} kWh")
c_kpi4.metric("ŞEBEKE FİNANSAL DURUM", f"{finansal_durum:,.0f} TL")

# --- 5. BÖLÜM: SONUÇ KARTLARI ---
res1, res2, res3 = st.columns(3)
res1.markdown("### GELENEKSEL YÖNTEM\n# 1.151.181 TL")
res2.markdown("### MEVCUT SENARYO\n# 524.675 TL")
res3.markdown("### SAĞLANAN NET KAZANÇ\n# 626.506 TL")

# Excel İhracat
output = io.BytesIO()
with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
    edited_df.to_excel(writer, index=False)
st.download_button("📥 Bu Tabloyu Excel Olarak İndir", output.getvalue(), "scada_raporu.xlsx")
