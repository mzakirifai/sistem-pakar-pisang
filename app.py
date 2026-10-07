"""Antarmuka Streamlit untuk sistem pakar diagnosis kematangan pisang (Gaya Dashboard Modern)."""

import streamlit as st
import pandas as pd
from database import fetch_attributes, fetch_rules
from inference import diagnosis_dua_lapis, cari_rule_terbaik, gabungkan_cf

# Konfigurasi Halaman
st.set_page_config(
    page_title="Diagnosis Kematangan Pisang",
    page_icon="🍌",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown("""
    <style>
    .stApp {
        background-color: #F8FAFC;
    }
    .stat-card {
        background: #1E293B;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 10px 20px;
        text-align: center;
        min-width: 90px;
    }
    .stat-number {
        font-size: 1.5rem;
        font-weight: 700;
        color: #38BDF8;
    }
    .stat-label {
        font-size: 0.7rem;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .badge-rule {
        background-color: #0284C7;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8em;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Inisialisasi Session State
if "history" not in st.session_state:
    st.session_state.history = []

# Fetch Data dari Database
try:
    attributes = fetch_attributes()
    rules = fetch_rules()
except Exception as e:
    st.error(f"❌ Gagal terhubung ke database: {e}")
    st.stop()

# Sidebar - Referensi Akademis (5 Jurnal) & Informasi System
with st.sidebar:
    st.markdown("### 🍌 Sistem Pakar Pisang")
    st.write("Aplikasi mendiagnosis kematangan pisang berdasarkan 4 indikator fisik pascapanen.")
    
    st.markdown("---")
    st.markdown("**Metode Penalaran:**")
    st.markdown("• Forward Chaining 2 Lapis")
    st.markdown("• Certainty Factor (CF)")
    
    st.markdown("---")
    st.markdown("**📚 Referensi 5 Jurnal Ilmiah:**")
    st.caption("1. *Sutowijoyo & Widodo (2013)* — Kriteria Kematangan Pascapanen Pisang (IPB)")
    st.caption("2. *Sularida et al. (2018)* — Identifikasi Kematangan Pisang Ekstraksi Ciri Warna (UHO)")
    st.caption("3. *Kosasih (2021)* — Klasifikasi Kematangan Pisang Ekstraksi Tekstur & KNN")
    st.caption("4. *Lende et al. (2023)* — Penerapan Sistem Pakar Diagnosa Penyakit Pisang (JATI)")
    st.caption("5. *Dayan et al. (2026)* — Image Processing Histogram Warna Kematangan Pisang (IPB)")

# Hitung statistik untuk top banner
total_atribut = len([k for k in attributes.keys() if k != "dugaan_awal"])
total_kesimpulan = len(attributes.get("dugaan_awal", []))
total_rules = len(rules)

# Header & Top Stat Counter
col_head, col_stats = st.columns([2, 1])
with col_head:
    st.markdown("### 🍌 SISTEM PAKAR • FORWARD CHAINING & CF")
    st.markdown("## **Diagnosis Kematangan Buah Pisang**")
    st.caption("Pilih karakteristik fisik pisang yang diamati, sistem akan menelusuri aturan secara bertahap dan menghitung kepastiannya.")

with col_stats:
    st.markdown(f"""
        <div style="display: flex; gap: 10px; justify-content: flex-end; margin-top: 15px;">
            <div class="stat-card">
                <div class="stat-number">{total_atribut}</div>
                <div class="stat-label">INDIKATOR</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{total_kesimpulan}</div>
                <div class="stat-label">DIAGNOSIS</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{total_rules}</div>
                <div class="stat-label">ATURAN</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Tab Utama
tab1, tab2 = st.tabs(["🔍 Diagnosa", "📚 Basis Pengetahuan"])

# TAB 1: DIAGNOSA
with tab1:
    col_input, col_output = st.columns([1, 1])

    with col_input:
        st.markdown("#### 1. Pilih Ciri Fisik Pisang")
        
        label_atribut = {
            "warna_kulit": "🎨 Warna Kulit",
            "tekstur": "🖐️ Tekstur Buah",
            "aroma": "👃 Aroma",
            "bercak_kulit": "🟤 Bercak Cokelat",
        }
        
        fakta_user: dict[str, str] = {}
        atribut_input = {k: v for k, v in attributes.items() if k != "dugaan_awal"}

        for nama_atribut, pilihan in atribut_input.items():
            fakta_user[nama_atribut] = st.selectbox(
                label_atribut.get(nama_atribut, nama_atribut),
                options=pilihan,
                key=f"input_{nama_atribut}"
            )
            
        st.markdown("<br>", unsafe_allow_html=True)
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            btn_diagnosa = st.button("🚀 Jalankan Diagnosa", type="primary", use_container_width=True)
        with col_b2:
            if st.button("🔄 Reset Form", use_container_width=True):
                st.rerun()

    with col_output:
        st.markdown("#### 2. Hasil Diagnosa & Peringkat Kecocokan")
        
        if btn_diagnosa:
            hasil = diagnosis_dua_lapis(rules, fakta_user)

            if hasil is None:
                st.error("⚠️ Tidak dapat menentukan diagnosis dari kombinasi ciri fisik ini.")
            else:
                # Simpan ke Riwayat
                st.session_state.history.append({
                    "fakta": fakta_user.copy(),
                    "hasil": hasil,
                })

                # Ringkasan Diagnosa Utama
                st.success(f"### 🎯 Kesimpulan Utama: **{hasil['kesimpulan']}**")
                st.markdown(f"**Rekomendasi Penanganan:** {hasil['rekomendasi']}")
                st.markdown(f"**Tingkat Kepastian (CF Final):** `{hasil['cf']*100:.1f}%` ({hasil['cf']} CF)")
                
                if hasil["is_partial_match"]:
                    st.warning("⚠️ **Pendekatan Parsial:** Ciri fisik tidak cocok 100% dengan aturan baku, angka di atas adalah perkiraan terdekat.")

                # Fitur Download Laporan Hasil Diagnosa
                laporan_txt = (
                    f"=== LAPORAN HASIL DIAGNOSIS KEMATANGAN PISANG ===\n\n"
                    f"1. OBSERVASIFISIK:\n"
                    f"   - Warna Kulit : {fakta_user['warna_kulit']}\n"
                    f"   - Tekstur Buah: {fakta_user['tekstur']}\n"
                    f"   - Aroma       : {fakta_user['aroma']}\n"
                    f"   - Bercak Kulit: {fakta_user['bercak_kulit']}\n\n"
                    f"2. HASIL PENALARAN (FORWARD CHAINING):\n"
                    f"   - Dugaan Awal (Lapis 1) : {hasil['dugaan_awal']} (Rule: {hasil['rule_lapis1']})\n"
                    f"   - Kesimpulan Final (Lapis 2): {hasil['kesimpulan']} (Rule: {', '.join(hasil['rule_lapis2'])})\n"
                    f"   - Certainty Factor (CF) : {hasil['cf']} ({hasil['cf']*100:.1f}%)\n\n"
                    f"3. REKOMENDASI:\n"
                    f"   {hasil['rekomendasi']}\n"
                )
                st.download_button(
                    label="📥 Unduh Laporan Diagnosis (.txt)",
                    data=laporan_txt,
                    file_name=f"Diagnosis_Pisang_{hasil['kesimpulan'].replace(' ', '_')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )

                st.markdown("---")
                st.markdown("##### 📊 Peringkat Kecocokan Semua Kategori")
                
                rules_lapis2 = {k: v for k, v in rules.items() if v["layer"] == 2}
                kategori_scores = {}
                
                for r_code, r_data in rules_lapis2.items():
                    kes = r_data["kesimpulan"]
                    cocok = sum(1 for k, v in r_data["kondisi"].items() if fakta_user.get(k) == v or k == "dugaan_awal")
                    total_k = len(r_data["kondisi"])
                    ratio = cocok / total_k
                    
                    if kes not in kategori_scores or ratio > kategori_scores[kes]:
                        kategori_scores[kes] = ratio

                for kes_name, score in sorted(kategori_scores.items(), key=lambda x: x[1], reverse=True):
                    c_col1, c_col2 = st.columns([3, 1])
                    with c_col1:
                        st.caption(f"**{kes_name}**")
                        st.progress(float(score))
                    with c_col2:
                        st.markdown(f"**{score*100:.1f}%**")

                with st.expander("🔍 Detail Transparansi Penalaran & Diagram Alur (Explainable AI)"):
                    st.write(f"• **Lapis 1:** Rule `{hasil['rule_lapis1']}` ➔ Dugaan Awal: **{hasil['dugaan_awal']}**")
                    st.write(f"• **Lapis 2:** Rule `{', '.join(hasil['rule_lapis2'])}` ➔ Hasil Akhir: **{hasil['kesimpulan']}**")
                    st.latex(r"CF_{final} = CF_{Lapis1} \times CF_{Lapis2} = " + f"{hasil['cf']}")
                    
                    st.markdown("---")
                    st.markdown("**Diagram Alur Penalaran Berhierarki:**")
                    st.code(
                        f"[🎨 Warna Kulit: {fakta_user['warna_kulit']}]\n"
                        f"       │\n"
                        f"       ▼ (Rule {hasil['rule_lapis1']})\n"
                        f"[Dugaan Awal: {hasil['dugaan_awal']}]\n"
                        f"       │\n"
                        f"       ├─► Tekstur: {fakta_user['tekstur']}\n"
                        f"       ├─► Aroma: {fakta_user['aroma']}\n"
                        f"       └─► Bercak: {fakta_user['bercak_kulit']}\n"
                        f"       │\n"
                        f"       ▼ (Rule {', '.join(hasil['rule_lapis2'])})\n"
                        f"🎯 [Final: {hasil['kesimpulan']}] (CF: {hasil['cf']})",
                        language="text"
                    )

    # Bagian Riwayat Diagnosis di Bawah Tab 1
    if st.session_state.history:
        st.markdown("---")
        col_h1, col_h2 = st.columns([4, 1])
        with col_h1:
            st.markdown("### 📜 Riwayat Diagnosis Sesi Ini")
        with col_h2:
            if st.button("🗑️ Hapus Riwayat", use_container_width=True):
                st.session_state.history = []
                st.rerun()

        for item in reversed(st.session_state.history):
            f = item["fakta"]
            h = item["hasil"]
            st.markdown(f"""
            <div style="
                background-color: #FFFFFF;
                border-left: 5px solid #0284C7;
                border-radius: 8px;
                padding: 12px 18px;
                margin-bottom: 10px;
                box-shadow: 0 2px 6px rgba(0,0,0,0.04);
            ">
                <span style="font-weight: bold; font-size: 1.05em; color: #0284C7;">
                    🍌 {h['kesimpulan']}
                </span> 
                <span style="color: #64748B; font-size: 0.9em;">(CF: {h['cf']*100:.1f}%)</span>
                <br>
                <span style="color: #475569; font-size: 0.88em;">
                    📍 <b>Kondisi:</b> {f['warna_kulit']} | {f['tekstur']} | {f['aroma']} | {f['bercak_kulit']}
                </span>
            </div>
            """, unsafe_allow_html=True)

# TAB 2: BASIS PENGETAHUAN
with tab2:
    st.markdown("### 📋 Basis Pengetahuan (Knowledge Base)")
    st.caption("Berikut adalah tabel aturan (Rule Base) dan daftar indikator yang tersimpan di basis data.")
    
    st.markdown("#### 1. Tabel Aturan (Rule Base)")
    rules_data = []
    for r_code, r_val in rules.items():
        kondisi_str = " DAN ".join([f"{k} = '{v}'" for k, v in r_val["kondisi"].items()])
        rules_data.append({
            "Kode Rule": r_code,
            "Layer": f"Lapis {r_val['layer']}",
            "JIKA (Kondisi)": kondisi_str,
            "MAKA (Kesimpulan)": r_val["kesimpulan"],
            "Nilai CF": r_val["nilai_cf"],
            "Rekomendasi": r_val["rekomendasi"]
        })
    df_rules = pd.DataFrame(rules_data)
    st.dataframe(df_rules, use_container_width=True, hide_index=True)

    st.markdown("---")
    
    col_tb1, col_tb2 = st.columns(2)
    
    with col_tb1:
        st.markdown("#### 2. Daftar Indikator Fisik")
        attr_data = []
        for a_name, a_vals in attributes.items():
            if a_name != "dugaan_awal":
                attr_data.append({
                    "Indikator": a_name.replace("_", " ").title(),
                    "Pilihan Nilai Observation": ", ".join(a_vals)
                })
        st.dataframe(pd.DataFrame(attr_data), use_container_width=True, hide_index=True)

    with col_tb2:
        st.markdown("#### 3. Daftar Hasil Diagnosis & Solusi")
        kes_data = []
        seen = set()
        for r_val in rules.values():
            if r_val["kesimpulan"] not in seen:
                seen.add(r_val["kesimpulan"])
                kes_data.append({
                    "Kategori Kematangan": r_val["kesimpulan"],
                    "Rekomendasi Penanganan": r_val["rekomendasi"]
                })
        st.dataframe(pd.DataFrame(kes_data), use_container_width=True, hide_index=True)