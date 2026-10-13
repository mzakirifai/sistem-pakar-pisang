"""Uji manual: koneksi database dan satu contoh diagnosis.

Perlu database yang sudah diimpor dan file .env yang terisi.
Jalankan dengan: python test_koneksi.py
"""

from database import fetch_attributes, fetch_rules
from inference import diagnosis_dua_lapis

attributes = fetch_attributes()
rules = fetch_rules()
print("Atribut input :", {nama: len(nilai) for nama, nilai in attributes.items()})
print("Jumlah rule   :", len(rules))

fakta_user = {
    "warna_kulit": "Kuning penuh",
    "tekstur": "Lunak",
    "aroma": "Beraroma kuat",
    "bercak_kulit": "Tidak ada",
}
print("Hasil diagnosis:", diagnosis_dua_lapis(rules, fakta_user))