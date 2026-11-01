"""
hitung.py - semua rumus keuangan di satu tempat, tanpa Streamlit, tanpa file.

Setiap fungsi menerima angka atau DataFrame dan mengembalikan angka atau
DataFrame. Dengan begitu semuanya bisa diuji dengan contoh kecil yang
hasilnya bisa dihitung di kepala (lihat tests/test_hitung.py).

Satuan: semua rupiah penuh, semua laju dalam persen per tahun (6.5 berarti 6,5%).
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

BATAS_TAHUN = 100  # kalau lebih dari ini, dianggap "tidak akan tercapai"


# ---------------------------------------------------------------------------
# Menabung
# ---------------------------------------------------------------------------

def rasio_harga_gaji(harga: float, gaji_bulanan: float) -> float:
    """Berapa tahun gaji penuh (12 bulan) yang setara dengan harga ini."""
    return harga / (gaji_bulanan * 12)


def tahun_menabung(
    target: float,
    gaji_bulanan: float,
    porsi_nabung: float,
    kenaikan_gaji: float = 0.0,
    kenaikan_target: float = 0.0,
) -> float:
    """
    Berapa tahun sampai tabungan >= target, kalau tiap bulan menyisihkan
    porsi_nabung % dari gaji. Gaji naik kenaikan_gaji % tiap awal tahun,
    target naik kenaikan_target % tiap awal tahun (harga rumah ikut naik).

    Mengembalikan tahun dalam pecahan (resolusi bulan). Kalau tidak tercapai
    dalam BATAS_TAHUN tahun, mengembalikan math.inf.
    """
    if target <= 0:
        return 0.0
    if gaji_bulanan <= 0 or porsi_nabung <= 0:
        return math.inf

    tabungan = 0.0
    gaji = gaji_bulanan
    for tahun in range(BATAS_TAHUN):
        setoran = gaji * porsi_nabung / 100
        for bulan in range(1, 13):
            tabungan += setoran
            if tabungan >= target:
                return tahun + bulan / 12
        gaji *= 1 + kenaikan_gaji / 100
        target *= 1 + kenaikan_target / 100
    return math.inf


def tabel_tahun_menabung(
    df: pd.DataFrame,
    kolom_harga: list[str],
    porsi_nabung: float,
    kenaikan_gaji: float = 0.0,
    kenaikan_harga: float = 0.0,
    kolom_gaji: str = "gaji",
) -> pd.DataFrame:
    """Satu baris per kota, kolom tahun_<nama> dan rasio_<nama> per jenis hunian."""
    hasil = df[["kota", kolom_gaji]].copy()
    for kolom in kolom_harga:
        hasil[f"tahun_{kolom}"] = [
            tahun_menabung(h, g, porsi_nabung, kenaikan_gaji, kenaikan_harga) if pd.notna(h) else np.nan
            for h, g in zip(df[kolom], df[kolom_gaji])
        ]
        hasil[f"rasio_{kolom}"] = df[kolom] / (df[kolom_gaji] * 12)
    return hasil


# ---------------------------------------------------------------------------
# KPR
# ---------------------------------------------------------------------------

def cicilan_anuitas(pokok: float, bunga_tahunan: float, sisa_bulan: int) -> float:
    """Cicilan bulanan tetap (anuitas) untuk melunasi pokok dalam sisa_bulan."""
    if sisa_bulan <= 0:
        return 0.0
    r = bunga_tahunan / 100 / 12
    if r == 0:
        return pokok / sisa_bulan
    return pokok * r / (1 - (1 + r) ** (-sisa_bulan))


def jadwal_kpr(
    harga: float,
    dp_persen: float,
    tenor_tahun: int,
    bunga_tetap: float,
    tahun_tetap: int,
    bunga_mengambang: float,
) -> pd.DataFrame:
    """
    Jadwal bulanan KPR dua tahap: bunga tetap selama tahun_tetap, lalu
    bunga mengambang sampai lunas. Saat bunga berubah, cicilan dihitung ulang
    dari sisa pokok dan sisa tenor (cara bank pada umumnya).

    Kolom: bulan, cicilan, bunga, pokok, sisa_pokok.
    """
    pokok = harga * (1 - dp_persen / 100)
    total_bulan = tenor_tahun * 12
    bulan_tetap = min(tahun_tetap * 12, total_bulan)

    baris = []
    sisa = pokok
    cicilan = cicilan_anuitas(sisa, bunga_tetap, total_bulan)
    for b in range(1, total_bulan + 1):
        if b == bulan_tetap + 1:
            cicilan = cicilan_anuitas(sisa, bunga_mengambang, total_bulan - bulan_tetap)
        laju = bunga_tetap if b <= bulan_tetap else bunga_mengambang
        bunga = sisa * laju / 100 / 12
        angsuran_pokok = min(cicilan - bunga, sisa)
        sisa -= angsuran_pokok
        baris.append((b, cicilan, bunga, angsuran_pokok, max(sisa, 0.0)))
    return pd.DataFrame(baris, columns=["bulan", "cicilan", "bunga", "pokok", "sisa_pokok"])


def ringkasan_kpr(jadwal: pd.DataFrame, dp: float) -> dict[str, float]:
    """Angka-angka yang biasanya ingin diketahui orang sebelum tanda tangan."""
    return {
        "dp": dp,
        "cicilan_awal": float(jadwal["cicilan"].iloc[0]),
        "cicilan_tertinggi": float(jadwal["cicilan"].max()),
        "total_bunga": float(jadwal["bunga"].sum()),
        "total_bayar": float(jadwal["cicilan"].sum() + dp),
    }


# ---------------------------------------------------------------------------
# Beli vs sewa
# ---------------------------------------------------------------------------

def total_sewa(sewa_bulanan: float, tahun: int, kenaikan_sewa: float = 0.0) -> float:
    """Total sewa selama `tahun` tahun; sewa naik kenaikan_sewa % tiap awal tahun."""
    total = 0.0
    sewa = sewa_bulanan
    for _ in range(tahun):
        total += sewa * 12
        sewa *= 1 + kenaikan_sewa / 100
    return total


def deret_kumulatif_sewa(sewa_bulanan: float, tahun: int, kenaikan_sewa: float = 0.0) -> pd.Series:
    """Total sewa yang sudah dibayar di akhir tiap tahun (indeks 1..tahun)."""
    return pd.Series([total_sewa(sewa_bulanan, t, kenaikan_sewa) for t in range(1, tahun + 1)],
                     index=range(1, tahun + 1), name="sewa_kumulatif")


def deret_kumulatif_kpr(jadwal: pd.DataFrame, dp: float, tahun: int) -> pd.Series:
    """Total uang keluar untuk rumah (DP + cicilan) di akhir tiap tahun 1..tahun."""
    cicilan_tahunan = jadwal.groupby((jadwal["bulan"] - 1) // 12)["cicilan"].sum()
    kumulatif = cicilan_tahunan.cumsum() + dp
    kumulatif.index = kumulatif.index + 1
    kumulatif = kumulatif.reindex(range(1, tahun + 1)).ffill().fillna(dp)
    kumulatif.name = "kpr_kumulatif"
    return kumulatif


def banding_beli_sewa(
    harga: float,
    sewa_bulanan: float,
    tahun: int,
    dp_persen: float,
    tenor_tahun: int,
    bunga_tetap: float,
    tahun_tetap: int,
    bunga_mengambang: float,
    kenaikan_sewa: float = 0.0,
    kenaikan_harga: float = 0.0,
    gaji_bulanan: float | None = None,
) -> dict:
    """
    Bandingkan dua jalan selama `tahun` tahun:
    - menyewa: total sewa yang dibayar;
    - membeli lewat KPR: DP + semua cicilan sampai tahun ke-`tahun`,
      dikurangi "kekayaan" yang terbentuk (nilai rumah saat itu − sisa pokok).

    Mengembalikan dict dengan deret per tahun, jadwal KPR dan angka ringkas.
    """
    dp = harga * dp_persen / 100
    jadwal = jadwal_kpr(harga, dp_persen, tenor_tahun, bunga_tetap, tahun_tetap, bunga_mengambang)
    kpr_kum = deret_kumulatif_kpr(jadwal, dp, tahun)
    sewa_kum = deret_kumulatif_sewa(sewa_bulanan, tahun, kenaikan_sewa)

    tahun_idx = pd.Index(range(1, tahun + 1))
    nilai_rumah = pd.Series([harga * (1 + kenaikan_harga / 100) ** t for t in tahun_idx], index=tahun_idx)
    sisa_pokok = pd.Series(
        [float(jadwal.loc[jadwal["bulan"] == min(t * 12, len(jadwal)), "sisa_pokok"].iloc[0]) for t in tahun_idx],
        index=tahun_idx,
    )
    ekuitas = nilai_rumah - sisa_pokok
    biaya_bersih_beli = kpr_kum - ekuitas  # uang keluar dikurangi aset yang dipegang

    ringkas = ringkasan_kpr(jadwal, dp)
    ringkas.update({
        "total_sewa": float(sewa_kum.iloc[-1]),
        "total_keluar_beli": float(kpr_kum.iloc[-1]),
        "ekuitas_akhir": float(ekuitas.iloc[-1]),
        "biaya_bersih_beli": float(biaya_bersih_beli.iloc[-1]),
        "sewa_awal": sewa_bulanan,
    })
    if gaji_bulanan:
        ringkas["porsi_cicilan_awal"] = ringkas["cicilan_awal"] / gaji_bulanan * 100
        ringkas["porsi_cicilan_tertinggi"] = ringkas["cicilan_tertinggi"] / gaji_bulanan * 100
        ringkas["porsi_sewa"] = sewa_bulanan / gaji_bulanan * 100

    deret = pd.DataFrame({
        "tahun": tahun_idx,
        "sewa_kumulatif": sewa_kum.values,
        "kpr_kumulatif": kpr_kum.values,
        "nilai_rumah": nilai_rumah.values,
        "sisa_pokok": sisa_pokok.values,
        "ekuitas": ekuitas.values,
        "biaya_bersih_beli": biaya_bersih_beli.values,
    })
    return {"ringkas": ringkas, "deret": deret, "jadwal": jadwal}


def titik_impas(deret: pd.DataFrame) -> int | None:
    """Tahun pertama ketika biaya bersih membeli <= total sewa (None kalau tidak ada)."""
    cocok = deret.loc[deret["biaya_bersih_beli"] <= deret["sewa_kumulatif"], "tahun"]
    return int(cocok.iloc[0]) if len(cocok) else None
