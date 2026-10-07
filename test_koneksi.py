# from database import get_connection

# conn = get_connection()
# print("Berhasil connect ke database!")
# conn.close()

# from database import fetch_attributes

# data = fetch_attributes()
# print(data)

# from database import fetch_rules

# data = fetch_rules()
# print(data["R7"])  # cek satu rule aja dulu biar gak kepanjangan

# from database import fetch_rules
# from inference import hitung_kecocokan

# rules = fetch_rules()
# r7 = rules["R7"]

# fakta_user = {
#     "warna_kulit": "Kuning penuh",
#     "tekstur": "Lunak",
#     "aroma": "Beraroma kuat",
#     "bercak_kulit": "Tidak ada",
# }

# print(hitung_kecocokan(r7, fakta_user))

# from database import fetch_rules
# from inference import cari_rule_terbaik

# rules = fetch_rules()

# fakta_user = {
#     "warna_kulit": "Kuning penuh",
#     "tekstur": "Lunak",
#     "aroma": "Beraroma kuat",
#     "bercak_kulit": "Tidak ada",
# }

# hasil, skor = cari_rule_terbaik(rules, fakta_user)
# print("Skor:", skor)
# print("Jumlah rule yang menang:", len(hasil))
# print("Kode rule:", [r for r in rules if rules[r] in hasil])

# from database import fetch_rules
# from inference import diagnosis

# rules = fetch_rules()

# fakta_user = {
#     "warna_kulit": "Kuning penuh",
#     "tekstur": "Lunak",
#     "aroma": "Beraroma kuat",
#     "bercak_kulit": "Tidak ada",
# }

# print(diagnosis(rules, fakta_user))

# from database import fetch_rules
# from inference import diagnosis_dua_lapis

# rules = fetch_rules()

# fakta_user = {
#     "warna_kulit": "Kuning penuh",
#     "tekstur": "Lunak",
#     "aroma": "Beraroma kuat",
#     "bercak_kulit": "Tidak ada",
# }

# print(diagnosis_dua_lapis(rules, fakta_user))

from database import fetch_rules
from inference import diagnosis_dua_lapis

rules = fetch_rules()
fakta_user = {
    "warna_kulit": "Kuning penuh",
    "tekstur": "Lunak",
    "aroma": "Beraroma kuat",
    "bercak_kulit": "Tidak ada",
}
print(diagnosis_dua_lapis(rules, fakta_user))