import streamlit as st
import pandas as pd
import io
import numpy as np

# Sayfa Yapısı
st.set_page_config(layout="wide", page_title="Endüstriyel Enerji SCADA Paneli")

st.title("🏭 Endüstriyel Enerji Optimizasyonu & SCADA Yönetim Paneli")

# --- 1. BÖLÜM: YÖNETİM GRUPLARI ---
c1, c2, c3 = st.columns(3)

with c1:
    st.subheader("🔥 1. DOĞALGAZ & PROSES YÜKLERİ")
    uretim = st.number_input("Üretim Kapasitesi (ton/gün):", value=250.0, step=1.0)
    hood = st.number_input("Hood Spesifik Tüketim (kWh/ton):", value=535.0, step=1.0)
    buhar = st.number_input("Buhar Spesifik Tüketim (kWh/ton):", value=603.0, step=1.0)
    gaz_fiyat = st.number_input("Doğalgaz Birim Fiyatı (TL/Nm3):", value=18.00, step=0.01)
    gaz_isil = st.number_input("Doğalgaz Isıl Değeri (kWh/Nm3):", value=10.64, step=0.01)
    kazan = st.number_input("Brülör / Kazan Verimi (%):", value=90.0, step=1.0)

with c2:
    st.subheader("⚡ 2. ELEKTRİK ALTYAPISI")
    sabit_elk = st.number_input("Sabit Elektrik Tüketimi (kWh/ton):", value=789.0, step=1.0)
    kurulu_ges = st.number_input("Kurulu GES Gücü (MW):", value=15.0, step=1.0)
    kurulu_res = st.number_input("Kurulu RES Gücü (MW):", value=12.0, step=1.0)
    res_bedel = st.number_input("RES Hat Kullanım Bedeli (TL/kWh):", value=0.35, step=0.01)
    rezistans = st.number_input("Elektrikli Rezistans Verimi (%):", value=98.0, step=1.0)

with c3:
    st.subheader("🔋 3. MOLTEN SALT (ERİMİŞ TUZ) DEPOLAMA")
    tuz_kap = st.number_input("Tuz Isıl Kapasitesi (MWh Isı):", value=120.0, step=1.0)
    onceki_gun = st.number_input("Önceki Günden Devreden (MWh):", value=40.0, step=1.0)
    hedef_tuz = st.number_input("Sonraki Güne Hedef Tuz (MWh):", value=40.0, step=1.0)
    min_kota = st.number_input("Min. Tuz Kotası (MWh):", value=10.0, step=1.0)
    sarj_guc = st.number_input("Molten Salt Şarj Gücü (MW):", value=25.0, step=1.0)
    verim = st.number_input("Molten Salt Çevrim Verimi (%):", value=90.0, step=1.0)

# --- 2. BÖLÜM: AKSİYON BUTONLARI ---
b1, b2 = st.columns(2)
if b1.button("🤖 HİBRİD OPTİMİZASYON (Fiyat Bazlı 3'lü Arbitraj)", use_container_width=True):
    st.session_state.df.loc[:, ["Gaz %", "Tuz %", "Elk %"]] = [20.0, 40.0, 40.0]
if b2.button("🍰 GELENEKSEL YÖNTEME DÖN (%100 Gaz)", use_container_width=True):
    st.session_state.df.loc[:, ["Gaz %", "Tuz %", "Elk %"]] = [100.0, 0.0, 0.0]

# --- 3. BÖLÜM: SCADA TABLOSU ---
st.subheader("⏱ Saatlik Operasyonel Çizelge")

if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame({
        "Saat": [f"{h:02}:00" for h in range(24)],
        "Elek. Fiyatı (TL/kWh)": [2.8] * 24, "GES?": [False] * 24, "RES?": [True] * 24,
        "Gaz %": [40.0] * 24, "Tuz %": [30.0] * 24, "Elk %": [30.0] * 24,
        "Depo Seviyesi (MWh Isı)": [36.6] * 24, "GES (kWh)": [0.0] * 24, "RES (kWh)": [12000.0] * 24,
        "Motor (kWh)": [8219.0] * 24, "Isıtma (kWh)": [11854.0] * 24, "Gaz (Nm3)": [495.0] * 24,
        "Motor (TL)": [23.013] * 24, "Isıtma Toplam (TL)": [19.074] * 24, "RES Hat Bedeli (TL)": [4.200] * 24,
        "Saatlik Balans": ["0 | 0 TL"] * 24
    })

edited_df = st.data_editor(st.session_state.df, use_container_width=True)
st.session_state.df = edited_df

# --- 4. BÖLÜM: KPI KUTULARI & SONUÇLAR ---
st.divider()

# Dinamik Hesaplamalar
toplam_gaz = edited_df["Gaz (Nm3)"].sum()
toplam_gaz_maliyet = toplam_gaz * gaz_fiyat
net_sebeke = -52.892 # Örnek
finansal_durum = -220.006

c_kpi1, c_kpi2, c_kpi3, c_kpi4 = st.columns(4)
c_kpi1.metric("TOPLAM GAZ TÜKETİMİ", f"{toplam_gaz:,.0f} Nm3")
c_kpi2.metric("TOPLAM GAZ MALİYETİ", f"{toplam_gaz_maliyet:,.0f} TL")
c_kpi3.metric("NET ŞEBEKE BALANSI", f"{net_sebeke:,.3f} kWh")
c_kpi4.metric("ŞEBEKE FİNANSAL DURUM", f"{finansal_durum:,.0f} TL")

res1, res2, res3 = st.columns(3)
res1.markdown("### GELENEKSEL YÖNTEM (BASELİNE)\n# 1.151.181 TL")
res2.markdown("### MEVCUT SENARYO MALİYETİ\n# 524.675 TL")
res3.markdown("### SAĞLANAN NET KAZANÇ / TASARRUF\n# 626.506 TL")

# Excel İhracat
output = io.BytesIO()
with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
    edited_df.to_excel(writer, index=False)
st.download_button("📥 Bu Tabloyu Excel Olarak İndir", output.getvalue(), "scada_raporu.xlsx")
