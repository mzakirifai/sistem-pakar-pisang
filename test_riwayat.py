"""Uji ekspor riwayat ke CSV (tanpa database)."""

import csv
import io

from inference import diagnosis_dua_lapis
from riwayat import KOLOM_CSV, riwayat_ke_csv
from test_inference import RULES, _fakta


def _item(waktu, *ciri):
    fakta = _fakta(*ciri)
    return {"waktu": waktu, "fakta": fakta, "hasil": diagnosis_dua_lapis(RULES, fakta)}


def _baca(data: bytes) -> list[list[str]]:
    return list(csv.reader(io.StringIO(data.decode("utf-8-sig")), delimiter=";"))


def test_csv_berisi_judul_dan_satu_baris_per_entri():
    riwayat = [
        _item("14:05:09", "Hijau penuh", "Keras", "Tidak beraroma", "Tidak ada"),
        _item("14:06:30", "Kuning penuh", "Agak lunak", "Beraroma kuat", "Sedikit"),
    ]
    baris = _baca(riwayat_ke_csv(riwayat))
    assert baris[0] == KOLOM_CSV
    assert len(baris) == 3
    assert baris[1][0] == "14:05:09" and baris[1][6] == "Mentah"
    assert baris[2][6] == "Matang Optimal"


def test_cf_memakai_koma_desimal_dan_kolom_rule_terisi():
    baris = _baca(riwayat_ke_csv([_item("14:06:30", "Kuning penuh", "Agak lunak", "Beraroma kuat", "Sedikit")]))
    assert baris[1][7] == "64,0"
    assert (baris[1][8], baris[1][9]) == ("L3", "O4")


def test_tanda_titik_koma_di_dalam_teks_tidak_memecah_kolom():
    item = _item("14:07:00", "Kuning penuh", "Lunak", "Beraroma kuat", "Banyak")
    item["hasil"]["rekomendasi"] = "Sudah lewat masak, tetapi masih layak; segera konsumsi"
    baris = _baca(riwayat_ke_csv([item]))
    assert len(baris[1]) == len(KOLOM_CSV)
    assert baris[1][10] == "Sudah lewat masak, tetapi masih layak; segera konsumsi"


def test_riwayat_kosong_hanya_judul_dan_ada_bom_utf8():
    data = riwayat_ke_csv([])
    assert data.startswith(b"\xef\xbb\xbf")
    assert len(_baca(data)) == 1