"""Akses data ke database MySQL untuk sistem pakar kematangan pisang."""

import mysql.connector
from mysql.connector import MySQLConnection
import streamlit as st
from config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, DB_PORT


def _ada_secrets() -> bool:
    """True bila konfigurasi database tersedia di st.secrets (Streamlit Cloud)."""
    try:
        return "DB_HOST" in st.secrets
    except Exception:
        return False


def get_connection() -> MySQLConnection:
    """Membuka koneksi baru ke database MySQL (Auto-detect Streamlit Cloud / Local)."""
    # Jika berjalan di Streamlit Cloud, gunakan st.secrets
    if _ada_secrets():
        return mysql.connector.connect(
            host=st.secrets["DB_HOST"],
            user=st.secrets["DB_USER"],
            password=st.secrets["DB_PASSWORD"],
            database=st.secrets["DB_NAME"],
            port=int(st.secrets.get("DB_PORT", 4000)),
        )
    # Jika berjalan di lokal, gunakan variabel dari config.py / .env
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=int(DB_PORT),
    )


@st.cache_data(ttl=600, show_spinner=False)
def fetch_attributes() -> dict[str, list[str]]:
    """Mengambil atribut input beserta daftar nilai/levelnya dari database."""
    query = """
        SELECT a.nama_atribut, av.nilai
        FROM attributes a
        JOIN attribute_values av ON av.attribute_id = a.id
        WHERE a.jenis = 'input'
        ORDER BY a.id, av.urutan
    """
    hasil: dict[str, list[str]] = {}
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        for nama_atribut, nilai in cursor.fetchall():
            if nama_atribut not in hasil:
                hasil[nama_atribut] = []
            hasil[nama_atribut].append(nilai)
        cursor.close()
    finally:
        conn.close()
    return hasil


@st.cache_data(ttl=600, show_spinner=False)
def fetch_rules() -> dict[str, dict]:
    """Mengambil semua rule beserta kondisi IF-nya dari database."""
    query = """
        SELECT r.kode_rule, r.kesimpulan, r.rekomendasi, r.nilai_cf, r.layer, r.sumber,
            a.nama_atribut, av.nilai
        FROM rules r
        JOIN rule_conditions rc ON rc.rule_id = r.id
        JOIN attribute_values av ON av.id = rc.attribute_value_id
        JOIN attributes a ON a.id = av.attribute_id
        ORDER BY r.id, rc.id
    """
    rules_by_code: dict[str, dict] = {}
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        for kode_rule, kesimpulan, rekomendasi, nilai_cf, layer, sumber, nama_atribut, nilai in cursor.fetchall():
            if kode_rule not in rules_by_code:
                rules_by_code[kode_rule] = {
                    "kesimpulan": kesimpulan,
                    "rekomendasi": rekomendasi,
                    "nilai_cf": float(nilai_cf),
                    "layer": layer,
                    "sumber": sumber,
                    "kondisi": {},
                }
            rules_by_code[kode_rule]["kondisi"][nama_atribut] = nilai
        cursor.close()
    finally:
        conn.close()
    return rules_by_code