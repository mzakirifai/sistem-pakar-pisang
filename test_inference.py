"""Uji mesin inferensi v2 tanpa database (basis pengetahuan ditulis ulang di sini)."""

import itertools

from inference import contoh_kasus, diagnosis_dua_lapis, jelaskan_tidak_cocok


def _l2(kode, kes, cf, dugaan, tekstur, aroma, bercak):
    return kode, {
        "kesimpulan": kes, "rekomendasi": "-", "nilai_cf": cf, "layer": 2,
        "kondisi": {"dugaan_awal": dugaan, "tekstur": tekstur, "aroma": aroma, "bercak_kulit": bercak},
    }


def _l1(kode, kes, cf, warna):
    return kode, {"kesimpulan": kes, "rekomendasi": "-", "nilai_cf": cf, "layer": 1,
                  "kondisi": {"warna_kulit": warna}}


RULES = dict([
    _l1("L1", "Mentah", 0.8, "Hijau penuh"),
    _l1("L2", "Mengkal", 0.6, "Hijau kekuningan"),
    _l1("L3", "Matang", 0.8, "Kuning penuh"),
    _l2("M1", "Mentah", 1.0, "Mentah", "Keras", "Tidak beraroma", "Tidak ada"),
    _l2("M2", "Mentah", 0.8, "Mentah", "Agak lunak", "Tidak beraroma", "Tidak ada"),
    _l2("M3", "Mentah", 0.8, "Mentah", "Keras", "Beraroma ringan", "Tidak ada"),
    _l2("K1", "Mengkal", 1.0, "Mengkal", "Agak lunak", "Beraroma ringan", "Tidak ada"),
    _l2("K2", "Mengkal", 0.8, "Mengkal", "Keras", "Beraroma ringan", "Tidak ada"),
    _l2("K3", "Mengkal", 0.8, "Mengkal", "Agak lunak", "Tidak beraroma", "Tidak ada"),
    _l2("O1", "Matang Optimal", 1.0, "Matang", "Lunak", "Beraroma kuat", "Tidak ada"),
    _l2("O2", "Matang Optimal", 1.0, "Matang", "Lunak", "Beraroma kuat", "Sedikit"),
    _l2("O3", "Matang Optimal", 0.8, "Matang", "Agak lunak", "Beraroma kuat", "Tidak ada"),
    _l2("O4", "Matang Optimal", 0.8, "Matang", "Agak lunak", "Beraroma kuat", "Sedikit"),
    _l2("O5", "Matang Optimal", 0.8, "Matang", "Lunak", "Beraroma ringan", "Tidak ada"),
    _l2("O6", "Matang Optimal", 0.8, "Matang", "Lunak", "Beraroma ringan", "Sedikit"),
    _l2("T1", "Terlalu Matang", 1.0, "Matang", "Lunak", "Beraroma kuat", "Banyak"),
    _l2("T2", "Terlalu Matang", 0.8, "Matang", "Agak lunak", "Beraroma kuat", "Banyak"),
    _l2("T3", "Terlalu Matang", 0.8, "Matang", "Lunak", "Beraroma ringan", "Banyak"),
])

WARNA = ["Hijau penuh", "Hijau kekuningan", "Kuning penuh"]
TEKSTUR = ["Keras", "Agak lunak", "Lunak"]
AROMA = ["Tidak beraroma", "Beraroma ringan", "Beraroma kuat"]
BERCAK = ["Tidak ada", "Sedikit", "Banyak"]


def _fakta(warna, tekstur, aroma, bercak):
    return {"warna_kulit": warna, "tekstur": tekstur, "aroma": aroma, "bercak_kulit": bercak}


def test_cakupan_15_dari_81_kombinasi_dan_tanpa_rule_ganda():
    menyala = 0
    for kombinasi in itertools.product(WARNA, TEKSTUR, AROMA, BERCAK):
        hasil = diagnosis_dua_lapis(RULES, _fakta(*kombinasi))
        if hasil is not None:
            menyala += 1
            assert len(hasil["rule_lapis2"]) == 1
    assert menyala == 15


def test_profil_khas_tiap_fase_cf_penuh():
    kasus = [
        (("Hijau penuh", "Keras", "Tidak beraroma", "Tidak ada"), "Mentah", 0.8),
        (("Hijau kekuningan", "Agak lunak", "Beraroma ringan", "Tidak ada"), "Mengkal", 0.6),
        (("Kuning penuh", "Lunak", "Beraroma kuat", "Tidak ada"), "Matang Optimal", 0.8),
        (("Kuning penuh", "Lunak", "Beraroma kuat", "Banyak"), "Terlalu Matang", 0.8),
    ]
    for kombinasi, kelas, cf in kasus:
        hasil = diagnosis_dua_lapis(RULES, _fakta(*kombinasi))
        assert hasil["kesimpulan"] == kelas
        assert hasil["cf"] == cf


def test_penyimpangan_satu_tingkat_menurunkan_cf():
    hasil = diagnosis_dua_lapis(RULES, _fakta("Kuning penuh", "Agak lunak", "Beraroma kuat", "Sedikit"))
    assert hasil["kesimpulan"] == "Matang Optimal"
    assert hasil["cf"] == 0.64  # 0,8 x 0,8


def test_bercak_sedikit_tidak_pernah_terlalu_matang():
    for tekstur, aroma in itertools.product(TEKSTUR, AROMA):
        hasil = diagnosis_dua_lapis(RULES, _fakta("Kuning penuh", tekstur, aroma, "Sedikit"))
        assert hasil is None or hasil["kesimpulan"] == "Matang Optimal"


def test_input_kontradiktif_ditolak():
    assert diagnosis_dua_lapis(RULES, _fakta("Hijau penuh", "Lunak", "Beraroma kuat", "Banyak")) is None
    assert diagnosis_dua_lapis(RULES, _fakta("Hijau penuh", "Keras", "Tidak beraroma", "Banyak")) is None


def test_jelaskan_tidak_cocok_memberi_profil_khas():
    info = jelaskan_tidak_cocok(RULES, _fakta("Hijau kekuningan", "Lunak", "Beraroma kuat", "Banyak"))
    assert info["dugaan_awal"] == "Mengkal"
    assert [p["kode"] for p in info["profil_khas"]] == ["K1"]
    info = jelaskan_tidak_cocok(RULES, _fakta("Kuning penuh", "Keras", "Tidak beraroma", "Tidak ada"))
    assert [p["kode"] for p in info["profil_khas"]] == ["O1", "O2", "T1"]


def test_contoh_kasus_tiap_kelas_menghasilkan_kelasnya_sendiri():
    contoh = contoh_kasus(RULES)
    assert set(contoh) == {"Mentah", "Mengkal", "Matang Optimal", "Terlalu Matang"}
    for kelas, fakta in contoh.items():
        assert diagnosis_dua_lapis(RULES, fakta)["kesimpulan"] == kelas