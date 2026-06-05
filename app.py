import streamlit as st
import pandas as pd
import io

# 1. Sayfa Ayarları
st.set_page_config(page_title="Endüstriyel SCADA Paneli", layout="wide")

# Modern Dashboard Stilleri
st.markdown("""
    <style>
    .card { background-color: #f8f9fa; border: 1px solid #e9ecef; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #dee2e6; }
    </style>
""", unsafe_allow_html=True)

st.title("🏭 Endüstriyel Enerji Optimizasyonu & SCADA Yönetim Paneli")

# 2. ÜST METRİK KARTLARI (Kutucuklu Görünüm)
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
col_m1.metric("Tesis Yükü", "20.0 MW", "0.0")
col_m2.metric("Güncel Fiyat", "2.85 TL", "0.05")
col_m3.metric("Depo Durumu", "43.3 MWh", "-1.2")
col_m4.metric("Güvenlik Limiti", "%20", "Sabit")

st.divider()

# 3. KONTROL PANELİ (Giriş Parametreleri)
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("⚙️ Kontrol Paneli: Parametre Girişi")
col1, col2, col3 = st.columns(3)

with col1:
    st.write("**Proses Yükleri**")
    uretim = st.number_input("Üretim (ton/gün):", value=250)
    gaz_fiyat = st.number_input("Gaz Fiyatı (TL/Nm3):", value=18.0)

with col2:
    st.write("**Enerji Kaynakları**")
    ges_gucu = st.number_input("GES Gücü (MW):", value=15.0)
    res_gucu = st.number_input("RES Gücü (MW):", value=12.0)

with col3:
    st.write("**Depolama Kısıtları**")
    salt_kapasite = st.number_input("Tuz Kapasitesi (MWh):", value=120)
    soc_min = st.slider("Min. Depo Seviyesi (%)", 0, 100, 20)
st.markdown('</div>', unsafe_allow_html=True)

# 4. SCADA TABLOSU (Matematiksel Modelimiz)
st.subheader("⏱ Saatlik Operasyonel Çizelge")
if 'scada_data' not in st.session_state:
    st.session_state.scada_data = pd.DataFrame({
        "Saat": [f"{h:02}:00" for h in range(24)],
        "Şarj_Deşarj_MW": [0.0] * 24,
        "Gaz_Tüketim_MWh": [20.0] * 24
    })

# İnteraktif Tablo
edited_df = st.data_editor(st.session_state.scada_data, use_container_width=True)

# 5. HESAPLAMA & AKSİYON
if st.button("🚀 Senaryoyu Hesapla ve Onayla"):
    # Basit SOC motoru
    soc = [40.0]
    for i in range(1, len(edited_df)):
        new_soc = soc[-1] + (edited_df.loc[i-1, "Şarj_Deşarj_MW"]) - 0.5
        soc.append(max(soc_min, min(100, new_soc)))
    
    edited_df["Depo_Seviyesi"] = soc
    st.success("Senaryo başarıyla işlendi ve grafikler güncellendi.")
    
    # Görselleştirme
    st.line_chart(edited_df[["Depo_Seviyesi"]])

# Excel İhracat
def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

st.download_button("📥 Planı Excel Olarak İndir", to_excel(edited_df), "scada_raporu.xlsx")
