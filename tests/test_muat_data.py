"""Tes untuk src/muat_data.py dan isi data/kota.csv yang dipakai dashboard."""

import pandas as pd
import pytest

from src import muat_data


@pytest.fixture(scope="module")
def kota():
    return muat_data.muat_kota()


def test_semua_kota_unik_dan_terurut(kota):
    assert kota["kota"].is_unique
    assert kota["kota"].tolist() == sorted(kota["kota"].tolist())
    assert len(kota) >= 10


def test_konversi_satuan(kota):
    jakarta = kota.set_index("kota").loc["Jakarta"]
    assert jakarta["gaji"] == 5_729_876
    assert jakarta["rumah_subsidi"] == 185e6
    assert jakarta["rumah_seken"] == jakarta["rumah_seken_juta"] * 1e6
    assert jakarta["kos"] == (jakarta["kos_min"] + jakarta["kos_max"]) / 2


def test_angka_masuk_akal(kota):
    assert kota["gaji"].between(2e6, 8e6).all()                 # UMK 2026 di kisaran ini
    assert kota["rumah_subsidi"].between(150e6, 300e6).all()
    assert kota["rumah_seken"].between(300e6, 2e9).all()
    assert kota["kos"].between(300_000, 5_000_000).all()
    assert kota["kontrakan"].between(500_000, 10_000_000).all()
    assert (kota["kos_min"] < kota["kos_max"]).all()


def test_kode_mutu_valid(kota):
    for kolom in ["rumah_seken_mutu", "kos_mutu", "kontrakan_mutu"]:
        assert set(kota[kolom]) <= muat_data.MUTU_VALID
    assert set(kota["apartemen_mutu"].dropna()) <= muat_data.MUTU_VALID


def test_apartemen_nan_untuk_kota_tanpa_data(kota):
    harga = muat_data.harga_apartemen(kota, 25)
    k = kota.set_index("kota")
    assert pd.isna(harga[kota["kota"] == "Bogor"].iloc[0])
    assert harga[kota["kota"] == "Jakarta"].iloc[0] == pytest.approx(35.9e6 * 25)
    assert pd.isna(k.loc["Bogor", "apartemen_per_m2"])


def test_asumsi_terbaca():
    a = muat_data.muat_asumsi()
    for kunci in ["kpr_bunga_tetap", "kpr_bunga_mengambang", "kpr_dp", "kpr_tenor",
                  "kenaikan_harga_rumah", "kenaikan_sewa", "kenaikan_gaji", "porsi_nabung", "luas_studio"]:
        assert kunci in a
    assert 0 < a["kpr_bunga_tetap"] < a["kpr_bunga_mengambang"] < 25


def test_kolom_hilang_ditolak(tmp_path):
    p = tmp_path / "kota.csv"
    pd.DataFrame({"kota": ["X"], "provinsi": ["Y"]}).to_csv(p, index=False)
    with pytest.raises(ValueError, match="Kolom hilang"):
        muat_data.muat_kota(p)


def test_kode_mutu_asing_ditolak(tmp_path):
    df = muat_data.muat_kota()
    sumber = pd.read_csv(muat_data.FOLDER_DATA / "kota.csv")
    sumber.loc[0, "kos_mutu"] = "Z"
    p = tmp_path / "kota.csv"
    sumber.to_csv(p, index=False)
    with pytest.raises(ValueError, match="mutu"):
        muat_data.muat_kota(p)
    assert len(df) == len(sumber)
