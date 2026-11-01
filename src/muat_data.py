"""
muat_data.py - membaca dan memvalidasi CSV di folder data/.

Semua angka rupiah di CSV disimpan dalam satuan aslinya: gaji, kos dan kontrakan
dalam rupiah per bulan; harga rumah dalam JUTA rupiah; apartemen dalam JUTA rupiah
per m². Fungsi di sini mengubah semuanya ke rupiah penuh supaya modul hitung
tidak perlu tahu soal satuan.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

FOLDER_DATA = Path(__file__).resolve().parent.parent / "data"

KOLOM_WAJIB = [
    "kota", "provinsi", "umk_2026", "rumah_subsidi_juta", "rumah_seken_juta",
    "kos_min", "kos_max", "kontrakan",
]
MUTU_VALID = {"A", "B", "C", "E"}
LABEL_MUTU = {
    "A": "A · angka langsung dari laporan atau SK",
    "B": "B · rentang dari artikel atau simulasi, dipakai titik tengah",
    "C": "C · dihitung dari listing atau artikel tanpa metode",
    "E": "E · perkiraan dari segmen lain atau rasio",
}


def muat_kota(path: Path | None = None) -> pd.DataFrame:
    """Baca data/kota.csv dan tambahkan kolom harga dalam rupiah penuh."""
    df = pd.read_csv(path or FOLDER_DATA / "kota.csv")
    hilang = [k for k in KOLOM_WAJIB if k not in df.columns]
    if hilang:
        raise ValueError(f"Kolom hilang di kota.csv: {hilang}")
    if df["kota"].duplicated().any():
        raise ValueError("Ada nama kota ganda di kota.csv")

    df["gaji"] = df["umk_2026"].astype(float)
    df["rumah_subsidi"] = df["rumah_subsidi_juta"].astype(float) * 1e6
    df["rumah_seken"] = df["rumah_seken_juta"].astype(float) * 1e6
    df["kos"] = (df["kos_min"].astype(float) + df["kos_max"].astype(float)) / 2
    df["kontrakan"] = df["kontrakan"].astype(float)
    df["apartemen_per_m2"] = pd.to_numeric(df["apartemen_per_m2_juta"], errors="coerce") * 1e6

    for kolom in ["rumah_seken_mutu", "apartemen_mutu", "kos_mutu", "kontrakan_mutu"]:
        nilai = set(df[kolom].dropna().unique())
        if not nilai <= MUTU_VALID:
            raise ValueError(f"Kode mutu tidak dikenal di {kolom}: {nilai - MUTU_VALID}")

    if (df["gaji"] <= 0).any() or (df["rumah_seken"] <= 0).any():
        raise ValueError("Gaji dan harga rumah harus positif")
    return df.sort_values("kota").reset_index(drop=True)


def muat_asumsi(path: Path | None = None) -> dict[str, float]:
    """Baca data/asumsi.csv menjadi dict {parameter: nilai}."""
    df = pd.read_csv(path or FOLDER_DATA / "asumsi.csv")
    return {str(k): float(v) for k, v in zip(df["parameter"], df["nilai"])}


def harga_apartemen(df: pd.DataFrame, luas_m2: float) -> pd.Series:
    """Harga studio = harga per m² × luas. NaN untuk kota tanpa data apartemen."""
    return df["apartemen_per_m2"] * luas_m2
