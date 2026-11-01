"""
Tes untuk src/hitung.py. Jalankan:  python -m pytest tests/ -v

Pola tiap tes: SIAPKAN angka kecil yang bisa dihitung di kepala -> PANGGIL fungsi
-> PERIKSA hasilnya.
"""

import math

import pandas as pd
import pytest

from src import hitung


# --- menabung ---------------------------------------------------------------

def test_rasio_harga_gaji():
    # Rumah 120 juta, gaji 1 juta/bulan = 12 juta/tahun -> 10 tahun gaji.
    assert hitung.rasio_harga_gaji(120e6, 1e6) == pytest.approx(10.0)


def test_tahun_menabung_tanpa_kenaikan():
    # Nabung 50% dari 2 juta = 1 juta/bulan. Target 24 juta -> tepat 24 bulan = 2 tahun.
    assert hitung.tahun_menabung(24e6, 2e6, 50) == pytest.approx(2.0)


def test_tahun_menabung_resolusi_bulan():
    # 1 juta/bulan, target 2,5 juta -> bulan ke-3 -> 3/12 tahun.
    assert hitung.tahun_menabung(2.5e6, 2e6, 50) == pytest.approx(3 / 12)


def test_tahun_menabung_gaji_naik_mempercepat():
    lambat = hitung.tahun_menabung(100e6, 2e6, 30, kenaikan_gaji=0)
    cepat = hitung.tahun_menabung(100e6, 2e6, 30, kenaikan_gaji=10)
    assert cepat < lambat


def test_tahun_menabung_harga_naik_memperlambat():
    dasar = hitung.tahun_menabung(100e6, 2e6, 30)
    naik = hitung.tahun_menabung(100e6, 2e6, 30, kenaikan_target=5)
    assert naik > dasar


def test_tahun_menabung_tidak_tercapai_jadi_inf():
    # Harga naik 20%/tahun, gaji diam: tidak akan terkejar.
    assert math.isinf(hitung.tahun_menabung(1e9, 1e6, 10, kenaikan_gaji=0, kenaikan_target=20))


def test_tahun_menabung_input_kosong():
    assert hitung.tahun_menabung(0, 1e6, 10) == 0.0
    assert math.isinf(hitung.tahun_menabung(1e6, 0, 10))
    assert math.isinf(hitung.tahun_menabung(1e6, 1e6, 0))


def test_tabel_tahun_menabung_bentuk():
    df = pd.DataFrame({"kota": ["A", "B"], "gaji": [2e6, 4e6], "rumah": [24e6, 24e6], "apt": [float("nan"), 48e6]})
    t = hitung.tabel_tahun_menabung(df, ["rumah", "apt"], 50)
    assert list(t.columns) == ["kota", "gaji", "tahun_rumah", "rasio_rumah", "tahun_apt", "rasio_apt"]
    assert t["tahun_rumah"].tolist() == pytest.approx([2.0, 1.0])
    assert pd.isna(t["tahun_apt"].iloc[0]) and t["tahun_apt"].iloc[1] == pytest.approx(2.0)
    assert t["rasio_rumah"].iloc[0] == pytest.approx(1.0)


# --- KPR ---------------------------------------------------------------------

def test_cicilan_anuitas_bunga_nol():
    assert hitung.cicilan_anuitas(120e6, 0, 120) == pytest.approx(1e6)


def test_cicilan_anuitas_rumus_standar():
    # 100 juta, 12%/tahun (1%/bulan), 12 bulan -> rumus anuitas = 8.884.879
    assert hitung.cicilan_anuitas(100e6, 12, 12) == pytest.approx(8_884_879, rel=1e-6)


def test_jadwal_kpr_lunas_di_akhir():
    j = hitung.jadwal_kpr(100e6, 10, 2, 6, 1, 10)
    assert len(j) == 24
    assert j["sisa_pokok"].iloc[-1] == pytest.approx(0.0, abs=1)
    assert j["pokok"].sum() == pytest.approx(90e6, rel=1e-9)   # pokok = harga - DP 10%


def test_jadwal_kpr_cicilan_naik_setelah_masa_tetap():
    j = hitung.jadwal_kpr(500e6, 0, 20, 5, 3, 11)
    cicilan_tetap = j.loc[j["bulan"] == 36, "cicilan"].iloc[0]
    cicilan_mengambang = j.loc[j["bulan"] == 37, "cicilan"].iloc[0]
    assert cicilan_mengambang > cicilan_tetap
    # Sepanjang masa tetap cicilan konstan.
    assert j.loc[j["bulan"] <= 36, "cicilan"].nunique() == 1


def test_jadwal_kpr_tanpa_masa_tetap_sama_dengan_satu_bunga():
    a = hitung.jadwal_kpr(300e6, 10, 10, 7, 0, 7)
    b = hitung.jadwal_kpr(300e6, 10, 10, 9, 0, 7)   # bunga tetap tak terpakai karena tahun_tetap=0
    assert a["cicilan"].iloc[0] == pytest.approx(b["cicilan"].iloc[0])


def test_ringkasan_kpr_konsisten():
    j = hitung.jadwal_kpr(200e6, 20, 5, 8, 2, 12)
    r = hitung.ringkasan_kpr(j, 40e6)
    assert r["dp"] == 40e6
    assert r["total_bayar"] == pytest.approx(j["cicilan"].sum() + 40e6)
    assert r["total_bunga"] == pytest.approx(j["cicilan"].sum() - 160e6, rel=1e-6)


# --- beli vs sewa -----------------------------------------------------------

def test_total_sewa_tanpa_kenaikan():
    assert hitung.total_sewa(1e6, 3) == pytest.approx(36e6)


def test_total_sewa_dengan_kenaikan():
    # 1 juta/bulan, naik 10%: tahun1 12 jt, tahun2 13,2 jt -> 25,2 jt
    assert hitung.total_sewa(1e6, 2, 10) == pytest.approx(25.2e6)


def test_deret_kumulatif_sewa():
    d = hitung.deret_kumulatif_sewa(1e6, 3)
    assert d.tolist() == pytest.approx([12e6, 24e6, 36e6])


def test_deret_kumulatif_kpr_setelah_lunas_tetap():
    j = hitung.jadwal_kpr(100e6, 0, 2, 0, 0, 0)   # bunga nol: 24 cicilan x 4.166.667
    d = hitung.deret_kumulatif_kpr(j, 0, 4)
    assert d.loc[2] == pytest.approx(100e6)
    assert d.loc[4] == pytest.approx(100e6)        # tidak bertambah setelah lunas


def test_banding_beli_sewa_bunga_nol_tanpa_kenaikan():
    # Rumah 120 jt, DP 0, bunga 0, tenor 10 th -> cicilan 1 jt/bulan.
    # Sewa 1 jt/bulan. Setelah 5 tahun: sewa 60 jt, keluar 60 jt, sisa pokok 60 jt,
    # ekuitas 120 - 60 = 60 jt, biaya bersih 0.
    h = hitung.banding_beli_sewa(120e6, 1e6, 5, 0, 10, 0, 0, 0, gaji_bulanan=4e6)
    r = h["ringkas"]
    assert r["total_sewa"] == pytest.approx(60e6)
    assert r["total_keluar_beli"] == pytest.approx(60e6)
    assert r["ekuitas_akhir"] == pytest.approx(60e6)
    assert r["biaya_bersih_beli"] == pytest.approx(0.0, abs=1)
    assert r["porsi_cicilan_awal"] == pytest.approx(25.0)
    assert r["porsi_sewa"] == pytest.approx(25.0)
    assert hitung.titik_impas(h["deret"]) == 1


def test_banding_beli_sewa_sewa_murah_tidak_impas():
    # Bunga tinggi, sewa sangat murah: membeli tidak pernah lebih murah dalam 5 tahun.
    h = hitung.banding_beli_sewa(1e9, 100_000, 5, 10, 20, 12, 0, 12)
    assert hitung.titik_impas(h["deret"]) is None


def test_banding_beli_sewa_deret_panjang_sesuai_horizon():
    h = hitung.banding_beli_sewa(500e6, 2e6, 7, 10, 20, 6, 3, 11, 3, 1)
    assert len(h["deret"]) == 7
    assert h["deret"]["tahun"].tolist() == list(range(1, 8))
    assert h["deret"]["sewa_kumulatif"].is_monotonic_increasing
