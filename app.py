import streamlit as st
import pandas as pd
import io

# --- 1. SAYFA VE GELİŞMİŞ CSS TASARIMI ---
st.set_page_config(layout="wide", page_title="EnerjiOptimizasyon SCADA Paneli", page_icon="🏭")

# Görsel zenginlik için özel CSS (Kartlar, metrikler, butonlar)
st.markdown("""
    <style>
    .kpi-card {
        background-color: #ffffff;
        border-left: 5px solid #1f77b4;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 15px;
    }
    .kpi-title { color: #5c6a7a; font-size: 14px; font-weight: bold; text-transform: uppercase; }
    .kpi-value { color: #2e384d; font-size: 28px; font-weight: 900; margin-top: 5px; }
    .stButton>button { height: 60px; font-weight: 800; font-size: 16px; border-radius: 10px; transition: all 0.3s; }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
    </style>
""", unsafe_allow_html=True)

st.title("🏭 EnerjiOptimizasyon & SCADA Yönetim Paneli")
st.markdown("---")

# --- 2. KONTROL PANELİ (GİRDİLER) ---
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("### 🔥 Doğalgaz & Proses Yükleri")
    uretim = st.number_input("Üretim Kapasitesi (ton/gün):", value=250.0, step=1.0, min_value=0.0)
    hood = st.number_input("Hood Layer Spesifik Tüketim (kWh/ton):", value=535.0, step=1.0, min_value=0.0)
    gaz_fiyat = st.number_input("Doğalgaz Birim Fiyatı (TL/Nm3):", value=18.00, step=0.01, min_value=0.0)
    gaz_isil = st.number_input("Doğalgaz Isıl Değeri (kWh/Nm3):", value=10.64, step=0.01, min_value=0.0)
    kazan_verimi = st.number_input("Brülör / Kazan Verimi (%):", value=90.0, step=1.0, min_value=0.0)

with c2:
    st.markdown("### ⚡ Elektrik Altyapısı")
    sabit_elk = st.number_input("Hamur Kasası & Sabit Hat Tüketimi (kWh/ton):", value=789.0, step=1.0, min_value=0.0)
    ges = st.number_input("Kurulu GES Gücü (MW):", value=15.0, step=1.0, min_value=0.0)
    res = st.number_input("Kurulu RES Gücü (MW):", value=12.0, step=1.0, min_value=0.0)
    res_bedel = st.number_input("RES Hat Kullanım Bedeli (TL/kWh):", value=0.35, step=0.01, min_value=0.0)
    rezistans = st.number_input("Elektrikli Rezistans Verimi (%):", value=98.0, step=1.0, min_value=0.0)

with c3:
    st.markdown("### 🔋 Molten Salt (Erimiş Tuz) Depolama")
    tuz_kap = st.number_input("Tuz Isıl Kapasitesi (MWh):", value=120.0, step=1.0, min_value=0.0)
    devreden = st.number_input("Önceki Günden Devreden (MWh):", value=40.0, step=1.0, min_value=0.0)
    hedef_tuz = st.number_input("Sonraki Güne Hedef Tuz (MWh):", value=40.0, step=1.0, min_value=0.0)
    sarj_guc = st.number_input("Şarj Gücü (MW):", value=25.0, step=1.0, min_value=0.0)
    tuz_verim = st.number_input("Çevrim Verimi (%):", value=90.0, step=1.0, min_value=0.0)

# --- 3. VERİ ALTYAPISI VE GERÇEK ZAMANLI PTF ---
# EPİAŞ benzeri dalgalı gün içi fiyatlandırma profili
ptf_fiyatlari = [1.2, 1.1, 1.1, 1.2, 1.3, 1.4, 1.8, 2.2, 2.8, 3.0, 2.9, 2.5, 2.4, 2.5, 2.8, 3.2, 3.8, 4.2, 4.0, 3.9, 3.5, 2.8, 2.0, 1.5]

if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame({
        "Saat": [f"{h:02}:00" for h in range(24)],
        "PTF Fiyatı": ptf_fiyatlari,
        "Gaz %": [100.0] * 24,
        "Tuz %": [0.0] * 24,
        "Elk %": [0.0] * 24
    })

# --- 4. AKSİYON BUTONLARI (ALGORİTMİK) ---
st.markdown("<br>", unsafe_allow_html=True)
b1, b2 = st.columns(2)

if b1.button("🤖 AKILLI HİBRİD OPTİMİZASYON (PTF Arbitrajı)", use_container_width=True):
    df = st.session_state.df
    for i in range(24):
        fiyat = df.loc[i, "PTF Fiyatı"]
        if fiyat <= 1.5:  # Gece ucuz tarifede elektriğe yüklen, depolamayı şarj et
            df.loc[i, ["Gaz %", "Tuz %", "Elk %"]] = [0.0, 0.0, 100.0]
        elif fiyat >= 3.5: # Puant saatlerde şebekeden çekilmeyi durdur, Tuza ve Gaza dön
            df.loc[i, ["Gaz %", "Tuz %", "Elk %"]] = [20.0, 80.0, 0.0]
        else: # Normal saatlerde baz yüke (Gaz) geç
            df.loc[i, ["Gaz %", "Tuz %", "Elk %"]] = [100.0, 0.0, 0.0]
    st.session_state.df = df
    st.rerun()

if b2.button("🏭 GELENEKSEL YÖNTEM (%100 Doğalgaz)", use_container_width=True):
    st.session_state.df["Gaz %"] = 100.0
    st.session_state.df["Tuz %"] = 0.0
    st.session_state.df["Elk %"] = 0.0
    st.rerun()

# --- 5. GÖRSEL TABLO (DATA EDITOR YÜKSELTMESİ) ---
st.markdown("### ⏱ Saatlik Operasyonel SCADA Çizelgesi")

# Sütunları görsel barlara dönüştürerek "SCADA Paneli" hissi yaratma
edited_df = st.data_editor(
    st.session_state.df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Saat": st.column_config.TextColumn("Zaman Dilimi", disabled=True),
        "PTF Fiyatı": st.column_config.NumberColumn("Elektrik (TL/kWh)", format="₺ %.2f"),
        "Gaz %": st.column_config.ProgressColumn("Doğalgaz Yükü", format="%d%%", min_value=0, max_value=100),
        "Tuz %": st.column_config.ProgressColumn("Molten Salt Yükü", format="%d%%", min_value=0, max_value=100),
        "Elk %": st.column_config.ProgressColumn("Şebeke Yükü", format="%d%%", min_value=0, max_value=100)
    }
)
st.session_state.df = edited_df

# --- 6. FİZİKSEL & FİNANSAL HESAPLAMALAR ---
toplam_gaz_nm3 = 0.0
toplam_elk_kwh = 0.0
mevcut_maliyet = 0.0
geleneksel_maliyet = 0.0

if uretim > 0:
    # 24 Saate dağıtılmış enerji ihtiyacı (Kapasite başına)
    saatlik_isi_kwh = (uretim * hood) / 24
    saatlik_sabit_elk_kwh = (uretim * sabit_elk) / 24

    for i in range(24):
        g_yuzde = edited_df.loc[i, "Gaz %"] / 100.0
        e_yuzde = edited_df.loc[i, "Elk %"] / 100.0
        saat_fiyat = edited_df.loc[i, "PTF Fiyatı"]

        saat_gaz_nm3 = (saatlik_isi_kwh * g_yuzde) / (gaz_isil * (kazan_verimi / 100))
        saat_elk_kwh = saatlik_sabit_elk_kwh + (saatlik_isi_kwh * e_yuzde)

        toplam_gaz_nm3 += saat_gaz_nm3
        toplam_elk_kwh += saat_elk_kwh
        mevcut_maliyet += (saat_gaz_nm3 * gaz_fiyat) + (saat_elk_kwh * saat_fiyat)

    # Geleneksel Baseline (%100 Gaz)
    baseline_gaz_nm3 = (uretim * hood) / (gaz_isil * (kazan_verimi / 100))
    ort_elk_fiyat = edited_df["PTF Fiyatı"].mean()
    geleneksel_maliyet = (baseline_gaz_nm3 * gaz_fiyat) + ((uretim * sabit_elk) * ort_elk_fiyat)

# --- 7. PROFESYONEL KPI GÖSTERGELERİ (Görsel Kartlar) ---
st.markdown("---")
k1, k2, k3, k4 = st
