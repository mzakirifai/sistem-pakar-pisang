"""Mesin inferensi forward chaining 2 lapis untuk diagnosis kematangan pisang."""


def hitung_kecocokan(rule: dict, fakta: dict[str, str]) -> int:
    """Menghitung berapa banyak kondisi rule yang cocok dengan fakta."""
    jumlah_cocok = 0
    for nama_atribut, nilai_dibutuhkan in rule["kondisi"].items():
        if fakta.get(nama_atribut) == nilai_dibutuhkan:
            jumlah_cocok += 1
    return jumlah_cocok


def cari_rule_terbaik(rules: dict[str, dict], fakta: dict[str, str]) -> tuple[list[tuple[str, dict]], int]:
    """Mencari rule dengan skor kecocokan tertinggi terhadap fakta."""
    skor_tertinggi = 0
    rule_terbaik: list[tuple[str, dict]] = []

    for kode_rule, rule in rules.items():
        skor = hitung_kecocokan(rule, fakta)
        if skor > skor_tertinggi:
            skor_tertinggi = skor
            rule_terbaik = [(kode_rule, rule)]
        elif skor == skor_tertinggi and skor > 0:
            rule_terbaik.append((kode_rule, rule))

    return rule_terbaik, skor_tertinggi


def gabungkan_cf(cf_lama: float, cf_baru: float) -> float:
    """Menggabungkan dua nilai Certainty Factor positif (rumus MYCIN)."""
    return cf_lama + cf_baru * (1 - cf_lama)


def diagnosis(rules: dict[str, dict], fakta: dict[str, str], min_skor: int = 1) -> dict | None:
    """Mencocokkan fakta ke satu set rule dan mengembalikan kesimpulannya."""
    rule_terbaik, skor_tertinggi = cari_rule_terbaik(rules, fakta)

    # Jika tidak ada yang cocok atau di bawah threshold minimal
    if not rule_terbaik or skor_tertinggi < min_skor:
        return None

    hasil_per_kesimpulan: dict[str, dict] = {}

    for kode_rule, rule in rule_terbaik:
        jumlah_kondisi = len(rule["kondisi"])
        # Hitung CF terbobot berdasarkan rasio kecocokan kondisi
        rasio_cocok = skor_tertinggi / jumlah_kondisi
        cf_rule_terbobot = rule["nilai_cf"] * rasio_cocok
        kesimpulan = rule["kesimpulan"]

        if kesimpulan not in hasil_per_kesimpulan:
            hasil_per_kesimpulan[kesimpulan] = {
                "cf": cf_rule_terbobot,
                "rekomendasi": rule["rekomendasi"],
                "rule_codes": [kode_rule],
                "jumlah_kondisi": jumlah_kondisi
            }
        else:
            cf_lama = hasil_per_kesimpulan[kesimpulan]["cf"]
            hasil_per_kesimpulan[kesimpulan]["cf"] = gabungkan_cf(cf_lama, cf_rule_terbobot)
            hasil_per_kesimpulan[kesimpulan]["rule_codes"].append(kode_rule)

    kesimpulan_terpilih = max(hasil_per_kesimpulan, key=lambda k: hasil_per_kesimpulan[k]["cf"])
    data_terpilih = hasil_per_kesimpulan[kesimpulan_terpilih]

    is_partial = skor_tertinggi < data_terpilih["jumlah_kondisi"]

    return {
        "kesimpulan": kesimpulan_terpilih,
        "rekomendasi": data_terpilih["rekomendasi"],
        "cf": round(data_terpilih["cf"], 3),
        "is_partial_match": is_partial,
        "rule_codes": data_terpilih["rule_codes"],
    }


def diagnosis_dua_lapis(rules: dict[str, dict], fakta_user: dict[str, str]) -> dict | None:
    """Menjalankan forward chaining 2 lapis: warna kulit -> dugaan awal -> kesimpulan akhir."""
    rules_lapis1 = {k: v for k, v in rules.items() if v["layer"] == 1}
    rules_lapis2 = {k: v for k, v in rules.items() if v["layer"] == 2}

    fakta_warna = {"warna_kulit": fakta_user["warna_kulit"]}
    rule_menang_1, _ = cari_rule_terbaik(rules_lapis1, fakta_warna)

    if not rule_menang_1:
        return None

    kode_rule_1, rule_l1 = rule_menang_1[0]
    dugaan_awal = rule_l1["kesimpulan"]
    cf_lapis1 = rule_l1["nilai_cf"]

    fakta_lengkap = {
        "dugaan_awal": dugaan_awal,
        "tekstur": fakta_user["tekstur"],
        "aroma": fakta_user["aroma"],
        "bercak_kulit": fakta_user["bercak_kulit"],
    }
    
    # Berikan min_skor=2 agar tidak asal tebak jika hanya 1 ciri yang pas
    hasil_lapis2 = diagnosis(rules_lapis2, fakta_lengkap, min_skor=2)

    if hasil_lapis2 is None:
        return None

    cf_final = cf_lapis1 * hasil_lapis2["cf"]

    return {
        "dugaan_awal": dugaan_awal,
        "kesimpulan": hasil_lapis2["kesimpulan"],
        "rekomendasi": hasil_lapis2["rekomendasi"],
        "cf": round(cf_final, 3),
        "is_partial_match": hasil_lapis2["is_partial_match"],
        "rule_lapis1": kode_rule_1,
        "rule_lapis2": hasil_lapis2["rule_codes"],
    }