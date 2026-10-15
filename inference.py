"""Mesin inferensi forward chaining 2 lapis untuk diagnosis kematangan pisang.

Sebuah rule hanya menyala bila SEMUA kondisinya terpenuhi. CF sebuah rule dihitung
sebagai min(CF premis) x CF rule. Ciri hasil pengamatan langsung dianggap CF 1, sehingga
pada lapis 2 nilai min() ditentukan oleh CF dugaan awal dari lapis 1.
"""


def hitung_kecocokan(rule: dict, fakta: dict[str, str]) -> int:
    """Menghitung berapa banyak kondisi rule yang cocok dengan fakta."""
    jumlah_cocok = 0
    for nama_atribut, nilai_dibutuhkan in rule["kondisi"].items():
        if fakta.get(nama_atribut) == nilai_dibutuhkan:
            jumlah_cocok += 1
    return jumlah_cocok


def cari_rule_cocok(rules: dict[str, dict], fakta: dict[str, str]) -> list[tuple[str, dict]]:
    """Mencari semua rule yang seluruh kondisinya terpenuhi oleh fakta."""
    return [
        (kode_rule, rule)
        for kode_rule, rule in rules.items()
        if hitung_kecocokan(rule, fakta) == len(rule["kondisi"])
    ]


def gabungkan_cf(cf_lama: float, cf_baru: float) -> float:
    """Menggabungkan dua nilai Certainty Factor positif (rumus MYCIN)."""
    return cf_lama + cf_baru * (1 - cf_lama)


def diagnosis(rules: dict[str, dict], fakta: dict[str, str], cf_premis: float = 1.0) -> dict | None:
    """Menjalankan rule yang seluruh kondisinya terpenuhi dan mengembalikan kesimpulannya.

    cf_premis adalah CF terkecil di antara premis. Premis hasil pengamatan bernilai 1,
    jadi nilainya hanya berubah bila ada premis hasil inferensi (dugaan awal).
    """
    rule_cocok = cari_rule_cocok(rules, fakta)
    if not rule_cocok:
        return None

    hasil_per_kesimpulan: dict[str, dict] = {}

    for kode_rule, rule in rule_cocok:
        cf_rule = cf_premis * rule["nilai_cf"]
        kesimpulan = rule["kesimpulan"]

        if kesimpulan not in hasil_per_kesimpulan:
            hasil_per_kesimpulan[kesimpulan] = {
                "cf": cf_rule,
                "rekomendasi": rule["rekomendasi"],
                "rule_codes": [kode_rule],
            }
        else:
            cf_lama = hasil_per_kesimpulan[kesimpulan]["cf"]
            hasil_per_kesimpulan[kesimpulan]["cf"] = gabungkan_cf(cf_lama, cf_rule)
            hasil_per_kesimpulan[kesimpulan]["rule_codes"].append(kode_rule)

    kesimpulan_terpilih = max(hasil_per_kesimpulan, key=lambda k: hasil_per_kesimpulan[k]["cf"])
    data_terpilih = hasil_per_kesimpulan[kesimpulan_terpilih]

    return {
        "kesimpulan": kesimpulan_terpilih,
        "rekomendasi": data_terpilih["rekomendasi"],
        "cf": round(data_terpilih["cf"], 3),
        "rule_codes": data_terpilih["rule_codes"],
    }


def diagnosis_dua_lapis(rules: dict[str, dict], fakta_user: dict[str, str]) -> dict | None:
    """Menjalankan forward chaining 2 lapis: warna kulit -> dugaan awal -> kesimpulan akhir.

    Mengembalikan None bila tidak ada rule yang seluruh kondisinya terpenuhi.
    """
    rules_lapis1 = {k: v for k, v in rules.items() if v["layer"] == 1}
    rules_lapis2 = {k: v for k, v in rules.items() if v["layer"] == 2}

    hasil_lapis1 = diagnosis(rules_lapis1, {"warna_kulit": fakta_user["warna_kulit"]})
    if hasil_lapis1 is None:
        return None

    dugaan_awal = hasil_lapis1["kesimpulan"]
    cf_lapis1 = hasil_lapis1["cf"]

    fakta_lengkap = {
        "dugaan_awal": dugaan_awal,
        "tekstur": fakta_user["tekstur"],
        "aroma": fakta_user["aroma"],
        "bercak_kulit": fakta_user["bercak_kulit"],
    }

    hasil_lapis2 = diagnosis(rules_lapis2, fakta_lengkap, cf_premis=cf_lapis1)
    if hasil_lapis2 is None:
        return None

    return {
        "dugaan_awal": dugaan_awal,
        "kesimpulan": hasil_lapis2["kesimpulan"],
        "rekomendasi": hasil_lapis2["rekomendasi"],
        "cf": hasil_lapis2["cf"],
        "cf_lapis1": cf_lapis1,
        "rule_lapis1": hasil_lapis1["rule_codes"][0],
        "rule_lapis2": hasil_lapis2["rule_codes"],
    }


def contoh_kasus(rules: dict[str, dict]) -> dict[str, dict[str, str]]:
    """Contoh input tiap kelas akhir, diambil dari rule lapis 2 ber-CF 1,0 (profil khas) dan warna lapis 1."""
    warna_per_dugaan = {
        rule["kesimpulan"]: rule["kondisi"]["warna_kulit"]
        for rule in rules.values()
        if rule["layer"] == 1
    }
    contoh: dict[str, dict[str, str]] = {}
    for rule in rules.values():
        if rule["layer"] == 2 and rule["nilai_cf"] == 1.0 and rule["kesimpulan"] not in contoh:
            ciri = dict(rule["kondisi"])
            dugaan_awal = ciri.pop("dugaan_awal")
            contoh[rule["kesimpulan"]] = {"warna_kulit": warna_per_dugaan[dugaan_awal], **ciri}
    return contoh


def jelaskan_tidak_cocok(rules: dict[str, dict], fakta_user: dict[str, str]) -> dict | None:
    """Untuk input tanpa rule lapis 2: mengembalikan dugaan awal dan profil khas fasenya.

    Profil khas = rule lapis 2 ber-CF tertinggi untuk dugaan awal tersebut.
    """
    rules_lapis1 = {k: v for k, v in rules.items() if v["layer"] == 1}
    hasil_lapis1 = diagnosis(rules_lapis1, {"warna_kulit": fakta_user["warna_kulit"]})
    if hasil_lapis1 is None:
        return None

    dugaan_awal = hasil_lapis1["kesimpulan"]
    kandidat = [
        (kode_rule, rule)
        for kode_rule, rule in rules.items()
        if rule["layer"] == 2 and rule["kondisi"].get("dugaan_awal") == dugaan_awal
    ]
    cf_tertinggi = max((rule["nilai_cf"] for _, rule in kandidat), default=0)

    profil_khas = [
        {
            "kode": kode_rule,
            "kesimpulan": rule["kesimpulan"],
            "kondisi": {k: v for k, v in rule["kondisi"].items() if k != "dugaan_awal"},
        }
        for kode_rule, rule in kandidat
        if rule["nilai_cf"] == cf_tertinggi
    ]
    return {"dugaan_awal": dugaan_awal, "profil_khas": profil_khas}