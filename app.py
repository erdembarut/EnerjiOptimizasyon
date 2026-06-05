import streamlit as st
import pandas as pd
import io

# --- 1. SAYFA VE GELİŞMİŞ CSS TASARIMI ---
st.set_page_config(layout="wide", page_title="Endüstriyel Enerji SCADA", page_icon="🏭")

st.markdown("""
    <style>
    .kpi-card { background-color: #ffffff; border-left: 5px solid #1f77b4; padding: 15px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 15px; }
    .kpi-title { color: #5c6a7a; font-size: 14px; font-weight: bold; text-transform: uppercase; }
    .kpi-value { color: #2e384d; font-size: 28px; font-weight: 900; margin-top: 5px; }
    .stButton>button { height: 50px; font-weight: bold; font-size: 16px; border-radius: 8px; }
    div[data-testid="stDataFrame"] { font-size: 14px !important; }
    </style>
""", unsafe_allow_html=True)

st.title("🏭 Endüstriyel Enerji Optimizasyonu & SCADA Yönetim Paneli")
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
    sabit_elk = st.number_input("Hamur Kasası & Sabit Tüketim (kWh/ton):", value=789.0, step=1.0, min_value=0.0)
    ges = st.number_input("Kurulu GES Gücü (MW):", value=15.0, step=1.0, min_value=0.0)
    res = st.number_input("Kurulu RES Gücü (MW):", value=12.0, step=1.0, min_value=0.0)
    res_bedel = st.number_input("RES Hat Kullanım Bedeli (TL/kWh):", value=0.35, step=0.01, min_value=0.0)
    rezistans = st.number_input("Elektrikli Rezistans Verimi (%):", value=98.0, step=1.0, min_value=0.0)

with c3:
    st.markdown("### 🔋 Molten Salt (Erimiş Tuz)")
    tuz_kap = st.number_input("Tuz Isıl Kapasitesi (MWh):", value=120.0, step=1.0, min_value=0.0)
    devreden = st.number_input("Önceki Günden Devreden (MWh):", value=40.0, step=1.0, min_value=0.0)
    hedef_tuz = st.number_input("Sonraki Güne Hedef Tuz (MWh):", value=40.0, step=1.0, min_value=0.0)
    sarj_guc = st.number_input("Şarj Gücü (MW):", value=25.0, step=1.0, min_value=0.0)
    tuz_verim = st.number_input("Çevrim Verimi (%):", value=90.0, step=1.0, min_value=0.0)

# --- 3. DETAYLI TABLO ALTYAPISI (Görseldeki Birebir Sütunlar) ---
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame({
        "Saat": [f"{h:02}:00" for h in range(24)],
        "Elek. Fiyatı (TL/kWh)": [2.8] * 24,
        "GES?": [False] * 24,
        "RES?": [False] * 24,
        "Tuz Şarj?": [False] * 24,
        "Hood Layer Seçimi": ["Doğalgaz"] * 24,
        "Buhar Seçimi": ["Doğalgaz"] * 24,
        "Depo Seviyesi (MWh Isı)": [40.0] * 24,
        "GES (kWh)": [0.0] * 24,
        "RES (kWh)": [0.0] * 24,
        "Motor (kWh)": [8219.0] * 24,
        "Isıtma (kWh)": [0.0] * 24,
        "Gaz (Nm3)": [1238.0] * 24,
        "Motor (TL)": [23013.0] * 24,
        "Hood (TL)": [10475.0] * 24,
        "Buhar (TL)": [11807.0] * 24,
        "Şarj (TL)": [0.0] * 24,
        "RES Hat Bedeli (TL)": [0.0] * 24,
        "Saatlik Balans": ["-8.219 | -23.012 TL"] * 24
    })

# --- 4. AKSİYON BUTONLARI ---
st.markdown("<br>", unsafe_allow_html=True)
b1, b2 = st.columns(2)

if b1.button("🤖 AKILLI HİBRİD OPTİMİZASYON", use_container_width=True):
    df = st.session_state.df
    for i in range(24):
        fiyat = df.loc[i, "Elek. Fiyatı (TL/kWh)"]
        if fiyat <= 1.5:  
            df.loc[i, ["Hood Layer Seçimi", "Buhar Seçimi", "Tuz Şarj?"]] = ["Molten Salt", "Molten Salt", True]
        elif fiyat >= 3.5: 
            df.loc[i, ["Hood Layer Seçimi", "Buhar Seçimi", "Tuz Şarj?"]] = ["Doğalgaz", "Doğalgaz", False]
    st.session_state.df = df
    st.rerun()

if b2.button("🏭 GELENEKSEL YÖNTEM (%100 Doğalgaz)", use_container_width=True):
    st.session_state.df["Hood Layer Seçimi"] = "Doğalgaz"
    st.session_state.df["Buhar Seçimi"] = "Doğalgaz"
    st.session_state.df["Tuz Şarj?"] = False
    st.rerun()

# --- 5. DATA EDITOR (GELİŞMİŞ SÜTUN KONFİGÜRASYONU) ---
st.markdown("### ⏱ Saatlik Operasyonel SCADA Çizelgesi")

kaynak_opsiyonlari = ["Doğalgaz", "Elektrik", "Molten Salt"]

edited_df = st.data_editor(
    st.session_state.df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Saat": st.column_config.TextColumn("Saat", disabled=True),
        "Elek. Fiyatı (TL/kWh)": st.column_config.NumberColumn("Elek. Fiyatı (TL/kWh)", format="%.2f"),
        "GES?": st.column_config.CheckboxColumn("GES?"),
        "RES?": st.column_config.CheckboxColumn("RES?"),
        "Tuz Şarj?": st.column_config.CheckboxColumn("Tuz Şarj?"),
        "Hood Layer Seçimi": st.column_config.SelectboxColumn("Hood Seçimi", options=kaynak_opsiyonlari),
        "Buhar Seçimi": st.column_config.SelectboxColumn("Buhar Seçimi", options=kaynak_opsiyonlari),
        "Depo Seviyesi (MWh Isı)": st.column_config.NumberColumn("Depo Seviyesi (MWh Isı)", format="%.1f"),
        "GES (kWh)": st.column_config.NumberColumn("GES (kWh)", format="%.0f"),
        "RES (kWh)": st.column_config.NumberColumn("RES (kWh)", format="%.0f"),
        "Motor (kWh)": st.column_config.NumberColumn("Motor (kWh)", format="%.3f"),
        "Isıtma (kWh)": st.column_config.NumberColumn("Isıtma (kWh)", format="%.0f"),
        "Gaz (Nm3)": st.column_config.NumberColumn("Gaz (Nm3)", format="%.3f"),
        "Motor (TL)": st.column_config.NumberColumn("Motor (TL)", format="%.3f"),
        "Hood (TL)": st.column_config.NumberColumn("Hood (TL)", format="%.3f"),
        "Buhar (TL)": st.column_config.NumberColumn("Buhar (TL)", format="%.3f"),
        "Şarj (TL)": st.column_config.NumberColumn("Şarj (TL)", format="%.0f"),
        "RES Hat Bedeli (TL)": st.column_config.NumberColumn("RES Hat Bedeli", format="%.0f"),
        "Saatlik Balans": st.column_config.TextColumn("Saatlik Balans (Fiziksel | Finansal)", disabled=True)
    }
)
st.session_state.df = edited_df

# --- 6. KPI HESAPLAMALARI ---
toplam_gaz_nm3 = edited_df["Gaz (Nm3)"].sum()
toplam_elk_kwh = edited_df["Motor (kWh)"].sum() + edited_df["Isıtma (kWh)"].sum()
toplam_gaz_maliyet = edited_df["Hood (TL)"].sum() + edited_df["Buhar (TL)"].sum() # Örnek toplama
toplam_elk_maliyet = edited_df["Motor (TL)"].sum() + edited_df["Şarj (TL)"].sum() + edited_df["RES Hat Bedeli (TL)"].sum()
mevcut_maliyet = toplam_gaz_maliyet + toplam_elk_maliyet

# Geleneksel Baseline
geleneksel_maliyet = 0.0
if uretim > 0:
    baseline_gaz_nm3 = (uretim * hood) / (gaz_isil * (kazan_verimi / 100))
    ort_elk_fiyat = edited_df["Elek. Fiyatı (TL/kWh)"].mean()
    geleneksel_maliyet = (baseline_gaz_nm3 * gaz_fiyat) + ((uretim * sabit_elk) * ort_elk_fiyat)

# --- 7. PROFESYONEL KPI GÖSTERGELERİ ---
st.markdown("---")
k1, k2, k3, k4 = st.columns(4)

k1.markdown(f'<div class="kpi-card" style="border-color: #f6c23e;"><div class="kpi-title">Toplam Gaz Tüketimi</div><div class="kpi-value">{toplam_gaz_nm3:,.0f} Nm³</div></div>', unsafe_allow_html=True)
k2.markdown(f'<div class="kpi-card" style="border-color: #e74a3b;"><div class="kpi-title">Toplam Gaz Maliyeti</div><div class="kpi-value">₺ {toplam_gaz_maliyet:,.0f}</div></div>', unsafe_allow_html=True)
k3.markdown(f'<div class="kpi-card" style="border-color: #36b9cc;"><div class="kpi-title">Net Şebeke Balansı</div><div class="kpi-value">{toplam_elk_kwh:,.0f} kWh</div></div>', unsafe_allow_html=True)
k4.markdown(f'<div class="kpi-card" style="border-color: #858796;"><div class="kpi-title">Şebeke Finansal Durum</div><div class="kpi-value">₺ {-toplam_elk_maliyet:,.0f}</div></div>', unsafe_allow_html=True)

# --- 8. SONUÇ VE OPTİMİZASYON KAZANCI ---
st.markdown("### 📊 Optimizasyon Finansal Özeti")
r1, r2, r3 = st.columns(3)

net_kazanc = geleneksel_maliyet - mevcut_maliyet if uretim > 0 else 0.0

r1.metric("Geleneksel Yöntem (Baseline)", f"₺ {geleneksel_maliyet:,.2f}")
r2.metric("Mevcut Senaryo (Optimize)", f"₺ {mevcut_maliyet:,.2f}")
r3.metric("Sağlanan Net Kazanç", f"₺ {net_kazanc:,.2f}", delta=f"{net_kazanc:,.2f} TL Tasarruf", delta_color="normal")

# --- 9. EXCEL İHRACAT ---
st.markdown("<br>", unsafe_allow_html=True)
output = io.BytesIO()
with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
    edited_df.to_excel(writer, index=False)
st.download_button("📥 Planı Excel Olarak İndir", output.getvalue(), "SCADA_Optimizasyon_Raporu.xlsx", type="primary")
