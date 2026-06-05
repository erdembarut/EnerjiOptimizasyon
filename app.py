import streamlit as st
import pandas as pd
import io

# --- SAYFA VE TASARIM AYARLARI ---
st.set_page_config(layout="wide", page_title="Endüstriyel Enerji SCADA")
st.markdown("""
    <style>
    .stMetricValue { font-size: 26px !important; font-weight: bold; }
    .stButton>button { height: 55px; font-weight: bold; font-size: 16px; border-radius: 8px; }
    div[data-testid="stDataFrame"] { font-size: 15px !important; }
    </style>
""", unsafe_allow_html=True)

# --- DİL DESTEĞİ ---
lang = st.sidebar.radio("Dil / Language", ["Türkçe", "English"])
def t(tr, en): return tr if lang == "Türkçe" else en

st.title(t("🏭 Endüstriyel Enerji Optimizasyonu & SCADA Yönetim Paneli", "🏭 Industrial Energy Optimization & SCADA Panel"))

# --- 1. PARAMETRE GİRİŞLERİ ---
c1, c2, c3 = st.columns(3)
with c1:
    st.subheader(t("🔥 1. DOĞALGAZ & PROSES YÜKLERİ", "🔥 1. GAS & PROCESS LOADS"))
    uretim = st.number_input(t("Üretim Kapasitesi (ton/gün):", "Production Capacity (t/day):"), value=250.0, step=1.0, min_value=0.0)
    hood = st.number_input(t("Hood Layer Spesifik Tüketim (kWh/ton):", "Hood Layer Specific Cons. (kWh/ton):"), value=535.0, step=1.0, min_value=0.0)
    buhar = st.number_input(t("Buhar Spesifik Tüketim (kWh/ton):", "Steam Specific Cons. (kWh/ton):"), value=603.0, step=1.0, min_value=0.0)
    gaz_fiyat = st.number_input(t("Doğalgaz Birim Fiyatı (TL/Nm3):", "Gas Price (TL/Nm3):"), value=18.00, step=0.01, min_value=0.0)
    gaz_isil = st.number_input(t("Doğalgaz Isıl Değeri (kWh/Nm3):", "Gas Calorific Value (kWh/Nm3):"), value=10.64, step=0.01, min_value=0.0)
    kazan_verimi = st.number_input(t("Brülör / Kazan Verimi (%):", "Boiler Efficiency (%):"), value=90.0, step=1.0, min_value=0.0)

with c2:
    st.subheader(t("⚡ 2. ELEKTRİK ALTYAPISI", "⚡ 2. ELECTRICITY INFRASTRUCTURE"))
    sabit_elk = st.number_input(t("Sabit Elektrik Tüketimi (kWh/ton):", "Fixed Electricity Cons. (kWh/ton):"), value=789.0, step=1.0, min_value=0.0)
    ges = st.number_input(t("Kurulu GES Gücü (MW):", "Installed GES Power (MW):"), value=15.0, step=1.0, min_value=0.0)
    res = st.number_input(t("Kurulu RES Gücü (MW):", "Installed RES Power (MW):"), value=12.0, step=1.0, min_value=0.0)
    res_bedel = st.number_input(t("RES Hat Kullanım Bedeli (TL/kWh):", "RES Grid Usage Fee (TL/kWh):"), value=0.35, step=0.01, min_value=0.0)
    rezistans = st.number_input(t("Elektrikli Rezistans Verimi (%):", "Electric Resistance Eff. (%):"), value=98.0, step=1.0, min_value=0.0)

with c3:
    st.subheader(t("🔋 3. MOLTEN SALT DEPOLAMA", "🔋 3. MOLTEN SALT STORAGE"))
    tuz_kap = st.number_input(t("Tuz Isıl Kapasitesi (MWh):", "Salt Thermal Capacity (MWh):"), value=120.0, step=1.0, min_value=0.0)
    devreden = st.number_input(t("Önceki Günden Devreden (MWh):", "Carryover (MWh):"), value=40.0, step=1.0, min_value=0.0)
    hedef_tuz = st.number_input(t("Sonraki Güne Hedef Tuz (MWh):", "Target Salt (MWh):"), value=40.0, step=1.0, min_value=0.0)
    sarj_guc = st.number_input(t("Molten Salt Şarj Gücü (MW):", "Charge Power (MW):"), value=25.0, step=1.0, min_value=0.0)
    tuz_verim = st.number_input(t("Molten Salt Çevrim Verimi (%):", "Cycle Eff. (%):"), value=90.0, step=1.0, min_value=0.0)

# --- 2. VERİ TABLOSU VE GERÇEK ZAMANLI PTF ---
# Gerçekçi Saatlik Elektrik Fiyatları (Gece ucuz, Gündüz normal, Akşam puant)
ptf_fiyatlari = [1.2, 1.1, 1.1, 1.2, 1.3, 1.4, 1.8, 2.2, 2.8, 3.0, 2.9, 2.5, 2.4, 2.5, 2.8, 3.2, 3.8, 4.2, 4.0, 3.9, 3.5, 2.8, 2.0, 1.5]

if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame({
        t("Saat", "Hour"): [f"{h:02}:00" for h in range(24)],
        t("Elk Fiyatı", "Elec Price"): ptf_fiyatlari,
        t("Gaz %", "Gas %"): [100.0] * 24,
        t("Tuz %", "Salt %"): [0.0] * 24,
        t("Elk %", "Elec %"): [0.0] * 24
    })

b1, b2 = st.columns(2)

# ALGORİTMİK HİBRİD OPTİMİZASYON (Fiyata Duyarlı Arbitraj)
if b1.button(t("🤖 HİBRİD OPTİMİZASYON (Fiyat Bazlı Arbitraj)", "🤖 HYBRID OPTIMIZATION (Arbitrage)")):
    df = st.session_state.df
    for i in range(24):
        fiyat = df.loc[i, t("Elk Fiyatı", "Elec Price")]
        if fiyat <= 1.5:  # Gece / Ucuz Tarife -> Tamamen Elektriğe yüklen
            df.loc[i, [t("Gaz %", "Gas %"), t("Tuz %", "Salt %"), t("Elk %", "Elec %")]] = [0.0, 0.0, 100.0]
        elif fiyat >= 3.5: # Puant / Pahalı Tarife -> Elektriği kes, Tuz ve Gaza geç
            df.loc[i, [t("Gaz %", "Gas %"), t("Tuz %", "Salt %"), t("Elk %", "Elec %")]] = [20.0, 80.0, 0.0]
        else: # Normal Tarife -> Gaza devam
            df.loc[i, [t("Gaz %", "Gas %"), t("Tuz %", "Salt %"), t("Elk %", "Elec %")]] = [100.0, 0.0, 0.0]
    st.session_state.df = df
    st.rerun()

if b2.button(t("🍰 GELENEKSEL YÖNTEME DÖN (%100 Gaz)", "🍰 TRADITIONAL METHOD (%100 Gas)")):
    st.session_state.df[t("Gaz %", "Gas %")] = 100.0
    st.session_state.df[t("Tuz %", "Salt %")] = 0.0
    st.session_state.df[t("Elk %", "Elec %")] = 0.0
    st.rerun()

st.subheader(t("⏱ Saatlik Operasyonel Çizelge", "⏱ Hourly Operational Schedule"))
# Tabloyu düzenlenebilir yap (kullanıcı elk fiyatını veya yüzdeleri kendi de değiştirebilir)
edited_df = st.data_editor(st.session_state.df, use_container_width=True, hide_index=True)
st.session_state.df = edited_df

# --- 3. MÜHENDİSLİK HESAPLAMALARI (Maliyetler) ---
toplam_gaz_nm3 = 0.0
toplam_elk_kwh = 0.0
mevcut_senaryo_maliyet = 0.0
geleneksel_maliyet = 0.0

if uretim > 0:
    toplam_isi_enerjisi = uretim * hood
    toplam_sabit_elk = uretim * sabit_elk

    # Mevcut Senaryo Gerçekleşen Tüketim ve Maliyet (Satır satır hesaplama)
    for i in range(24):
        gaz_orani = edited_df.loc[i, t("Gaz %", "Gas %")] / 100.0
        elk_orani = edited_df.loc[i, t("Elk %", "Elec %")] / 100.0
        saatlik_fiyat = edited_df.loc[i, t("Elk Fiyatı", "Elec Price")]

        # Saatlik enerji ihtiyaçları (Günlük toplam / 24)
        saatlik_isi = toplam_isi_enerjisi / 24
        saatlik_sabit = toplam_sabit_elk / 24

        saatlik_gaz_nm3 = (saatlik_isi * gaz_orani) / (gaz_isil * (kazan_verimi / 100))
        saatlik_elk_kwh = saatlik_sabit + (saatlik_isi * elk_orani)

        toplam_gaz_nm3 += saatlik_gaz_nm3
        toplam_elk_kwh += saatlik_elk_kwh
        mevcut_senaryo_maliyet += (saatlik_gaz_nm3 * gaz_fiyat) + (saatlik_elk_kwh * saatlik_fiyat)

    # Geleneksel Baseline (%100 Doğalgaz) Maliyeti (Saatlik fiyatların ortalaması ile sabit elk maliyeti)
    baseline_gaz_nm3 = toplam_isi_enerjisi / (gaz_isil * (kazan_verimi / 100))
    ort_elk_fiyat = edited_df[t("Elk Fiyatı", "Elec Price")].mean()
    geleneksel_maliyet = (baseline_gaz_nm3 * gaz_fiyat) + (toplam_sabit_elk * ort_elk_fiyat)

# --- 4. ARA KPI KUTULARI ---
st.divider()
k1, k2, k3, k4 = st.columns(4)
k1.metric(t("TOPLAM GAZ TÜKETİMİ", "TOTAL GAS CONS."), f"{toplam_gaz_nm3:,.0f} Nm3")
k2.metric(t("TOPLAM GAZ MALİYETİ", "TOTAL GAS COST"), f"{toplam_gaz_nm3 * gaz_fiyat:,.0f} TL")
k3.metric(t("NET ŞEBEKE BALANSI", "NET GRID BALANCE"), f"{toplam_elk_kwh:,.0f} kWh")
k4.metric(t("ŞEBEKE FİNANSAL DURUM", "GRID FINANCIAL STATUS"), f"{-mevcut_senaryo_maliyet:,.0f} TL")

# --- 5. ANA SONUÇ KARTLARI ---
st.divider()
r1, r2, r3 = st.columns(3)
r1.metric(t("GELENEKSEL YÖNTEM MALİYETİ", "TRADITIONAL BASELINE COST"), f"{geleneksel_maliyet:,.2f} TL")
r2.metric(t("MEVCUT SENARYO MALİYETİ", "CURRENT SCENARIO COST"), f"{mevcut_senaryo_maliyet:,.2f} TL")

net_kazanc = geleneksel_maliyet - mevcut_senaryo_maliyet if uretim > 0 else 0.0
r3.metric(t("SAĞLANAN NET KAZANÇ / TASARRUF", "NET GAIN / SAVINGS"), f"{net_kazanc:,.2f} TL")

# --- 6. EXCEL EXPORT ---
output = io.BytesIO()
with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
    edited_df.to_excel(writer, index=False)
st.download_button(t("📥 Tabloyu Excel Olarak İndir", "📥 Download as Excel"), output.getvalue(), "SCADA_Raporu.xlsx")
