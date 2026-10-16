"""Fungsi pendukung riwayat diagnosis sesi: jam (WIB) dan ekspor CSV."""

import csv
import io
from datetime import datetime, timedelta, timezone

WIB = timezone(timedelta(hours=7))

KOLOM_CSV = [
    "Waktu (WIB)", "Warna Kulit", "Tekstur", "Aroma", "Bercak Kulit",
    "Dugaan Awal", "Kesimpulan", "CF (%)", "Rule Lapis 1", "Rule Lapis 2", "Rekomendasi",
]


def waktu_wib() -> str:
    """Jam saat ini dalam WIB (UTC+7), misalnya 14:05:09."""
    return datetime.now(WIB).strftime("%H:%M:%S")


def riwayat_ke_csv(history: list[dict]) -> bytes:
    """Mengubah riwayat diagnosis menjadi CSV berurutan dari yang terlama.

    Pemisah titik koma dan desimal koma supaya langsung rapi di Excel berbahasa Indonesia.
    Diberi BOM UTF-8 agar Excel membaca karakter dengan benar.
    """
    buffer = io.StringIO()
    penulis = csv.writer(buffer, delimiter=";")
    penulis.writerow(KOLOM_CSV)
    for item in history:
        fakta, hasil = item["fakta"], item["hasil"]
        penulis.writerow([
            item.get("waktu", "-"),
            fakta["warna_kulit"], fakta["tekstur"], fakta["aroma"], fakta["bercak_kulit"],
            hasil["dugaan_awal"], hasil["kesimpulan"],
            f"{hasil['cf'] * 100:.1f}".replace(".", ","),
            hasil["rule_lapis1"], ", ".join(hasil["rule_lapis2"]), hasil["rekomendasi"],
        ])
    return buffer.getvalue().encode("utf-8-sig")