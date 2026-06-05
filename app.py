import streamlit as st
import pandas as pd
import io

st.set_page_config(layout="wide", page_title="Endüstriyel SCADA Paneli")

# Modern Kurumsal Stil
st.markdown("""
    <style>
    .card { background-color: #f8f9fa; border: 1px solid #dee2e6; padding: 20px; border-radius: 10px; }
    .stMetric { background-color: #ffffff; border: 1px solid #dee2e6; padding: 10px; border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

st.title("🏭 Endüstriyel Enerji Optimizasyonu & SCADA Yönetim Paneli")

# --- 1. BÖLÜM: ÜST YÖNETİM GRUPLARI ---
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("🔥 1. DOĞALGAZ & PROSES YÜKLERİ")
    uretim = st.number_input("Üretim Kapasitesi (ton/gün):", value=250)
    hood = st.number_input("Hood Spesifik Tüketim (kWh/ton):", value=535)
    buhar = st.number_input("Buhar Spesifik Tüketim (kWh/ton):", value=603)
    gaz_fiyat = st.number_input("Doğalgaz Birim Fiyatı (TL/Nm3):", value=18.0)
    gaz_isil = st.number_input("Doğalgaz Isıl Değeri (kWh/Nm3):", value=10.64)
    kazan = st.number_input("Brülör / Kazan Verimi (%):", value=90)

with col2:
    st.subheader("⚡ 2. ELEKTRİK ALTYAPISI")
    sabit = st.number_input("Sabit Elektrik Tüketimi (kWh/ton):", value=789)
    ges = st.number_input("Kurulu GES Gücü (MW):", value=15.0)
    res = st.number_input("Kurulu RES Gücü (MW):", value=12.0)
    res_bedel = st.number_input("RES Hat Kullanım Bedeli (TL/kWh):", value=0.35)
    rezistans = st.number_input("Elektrikli Rezistans Verimi (%):", value=98)

with col3:
    st.subheader("🔋 3. MOLTEN SALT (ERİMİŞ TUZ) DEPOLAMA")
    tuz_kap = st.number_input("Tuz Isıl Kapasitesi (MWh Isı):", value=120)
    devreden = st.number_input("Önceki Günden Devreden (MWh):", value=40)
    hedef = st.number_input("Sonraki Güne Hedef Tuz (MWh):", value=40)
    min_kotas = st.number_input("Min. Tuz Kotası (MWh):", value=10)
    sarj_guc = st.number_input("Molten Salt Şarj Gücü (MW):", value=25)
    verim = st.number_input("Molten Salt Çevrim Verimi (%):", value=90)

st.divider()

# --- 2. BÖLÜM: AKSİYON BUTONLARI ---
b1, b2 = st.columns(2)
with b1:
    st.button("🤖 HİBRİD OPTİMİZASYON (Fiyat Bazlı 3'lü Arbitraj)", use_container_width=True)
with b2:
    st.button("🍰 GELENEKSEL YÖNTEME DÖN (%100 Gaz)", use_container_width=True)

# --- 3. BÖLÜM: SCADA TABLOSU ---
st.subheader("⏱ Saatlik Operasyonel Çizelge")

# Tablo Verisi (Görseldeki tüm sütun yapısı)
data = {
    "Saat": [f"{h:02}:00" for h in range(24)],
    "Elek. Fiyatı": [2.8] * 24, "GES?": [False] * 24, "RES?": [True] * 24,
    "Gaz %": [40] * 24, "Tuz %": [30] * 24, "Elk %": [30] * 24,
    "Depo Seviyesi": [36.6] * 24, "GES (kWh)": [0] * 24, "RES (kWh)": [12000] * 24,
    "Motor (kWh)": [8219] * 24, "Isıtma (kWh)": [11854] * 24, "Gaz (Nm3)": [495] * 24,
    "Motor (TL)": [23.013] * 24, "Isıtma (TL)": [19.074] * 24, "RES Bedel": [4.200] * 24,
    "Balans": ["0 | 0 TL"] * 24
}

edited_df = st.data_editor(pd.DataFrame(data), use_container_width=True)

# --- 4. BÖLÜM: ALT ÖZET KUTULARI (KPI) ---
st.divider()
c_kpi1, c_kpi2, c_kpi3, c_kpi4 = st.columns(4)
c_kpi1.metric("TOPLAM GAZ TÜKETİMİ", "13.659 Nm3")
c_kpi2.metric("TOPLAM GAZ MALİYETİ", "245.869 TL")
c_kpi3.metric("NET ŞEBEKE BALANSI", "-52.892 kWh")
c_kpi4.metric("ŞEBEKE FİNANSAL DURUM", "-220.006 TL")

# --- 5. BÖLÜM: SONUÇ KARTLARI ---
res1, res2, res3 = st.columns(3)
res1.markdown("### GELENEKSEL YÖNTEM\n# 1.151.181 TL")
res2.markdown("### MEVCUT SENARYO\n# 524.675 TL")
res3.markdown("### SAĞLANAN NET KAZANÇ\n# 626.506 TL")

# İhracat
output = io.BytesIO()
with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
    edited_df.to_excel(writer, index=False)
st.download_button("📥 Bu Tabloyu Excel Olarak İndir", output.getvalue(), "scada_raporu.xlsx")
