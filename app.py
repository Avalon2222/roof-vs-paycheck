"""
app.py - Dashboard Roof vs Paycheck (Streamlit).

Jalankan:  streamlit run app.py

File ini hanya mengurus TAMPILAN. Semua rumus ada di src/hitung.py,
pembacaan data ada di src/muat_data.py.
"""

from __future__ import annotations

import math

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src import hitung, muat_data

st.set_page_config(page_title="Roof vs Paycheck", page_icon="🏠", layout="wide")

WARNA = {
    "rumah_subsidi": "#1baf7a",
    "rumah_seken": "#2a78d6",
    "apartemen": "#eb6834",
    "sewa": "#8a5cd6",
    "kpr": "#2a78d6",
    "bersih": "#eb6834",
    "abu": "#8b8a86",
}
LABEL_HUNIAN = {
    "rumah_subsidi": "Subsidised house (FLPP cap)",
    "rumah_seken": "Small second-hand house (≤60 m²)",
    "apartemen": "Studio apartment",
}
LABEL_SEWA = {"kos": "Kos (room)", "kontrakan": "Kontrakan (small house)"}


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

@st.cache_data(show_spinner=False)
def muat_semua():
    return muat_data.muat_kota(), muat_data.muat_asumsi()


def rp(x: float, satuan: bool = True) -> str:
    """Format rupiah ringkas: Rp1,2 M / Rp850 jt / Rp1,5 jt."""
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "-"
    if abs(x) >= 1e9:
        s = f"{x / 1e9:,.2f} M"
    elif abs(x) >= 1e6:
        s = f"{x / 1e6:,.1f} jt"
    else:
        s = f"{x:,.0f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"Rp{s}" if satuan else s


def tahun_str(t: float) -> str:
    if t is None or (isinstance(t, float) and (math.isnan(t) or math.isinf(t))):
        return "> 100 tahun"
    return f"{t:.1f} tahun".replace(".", ",")


kota_df, asumsi = muat_semua()
kota_df["apartemen"] = muat_data.harga_apartemen(kota_df, asumsi["luas_studio"])

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.title("🏠 Roof vs Paycheck")
    st.caption("*Count the years before the key turns.*")

    halaman = st.segmented_control(
        "Page", ["Years to own", "Buy vs rent", "City table", "How it works"],
        default="Years to own", label_visibility="collapsed",
    )
    mode_belajar = st.toggle("Learning mode", value=False,
                             help="Tampilkan penjelasan konsep dan potongan kode di tiap bagian.")

    st.subheader("Income")
    sumber_gaji = st.radio("Salary basis", ["UMK 2026 per city", "Custom salary"], horizontal=True)
    gaji_kustom = None
    if sumber_gaji == "Custom salary":
        gaji_kustom = st.number_input("Monthly take-home (Rp)", min_value=1_000_000, max_value=200_000_000,
                                      value=8_000_000, step=500_000)
    porsi_nabung = st.slider("Saving rate (% of salary)", 5, 70, int(asumsi["porsi_nabung"]), 5,
                             help="Bagian gaji yang disisihkan tiap bulan untuk hunian.")

    st.subheader("Growth assumptions (% per year)")
    kenaikan_gaji = st.slider("Salary growth", 0.0, 15.0, asumsi["kenaikan_gaji"], 0.5)
    kenaikan_harga = st.slider("House price growth", -5.0, 15.0, asumsi["kenaikan_harga_rumah"], 0.5)
    kenaikan_sewa = st.slider("Rent growth", 0.0, 15.0, asumsi["kenaikan_sewa"], 0.5)

    st.subheader("Mortgage (KPR)")
    dp_persen = st.slider("Down payment (%)", 0, 50, int(asumsi["kpr_dp"]), 5)
    tenor = st.slider("Tenor (years)", 5, 30, int(asumsi["kpr_tenor"]), 1)
    bunga_tetap = st.slider("Fixed rate (%)", 0.0, 15.0, asumsi["kpr_bunga_tetap"], 0.25)
    tahun_tetap = st.slider("Fixed period (years)", 0, 10, int(asumsi["kpr_tahun_tetap"]), 1)
    bunga_mengambang = st.slider("Floating rate (%)", 0.0, 20.0, asumsi["kpr_bunga_mengambang"], 0.25)

    st.caption("Data: UMK 2026, Rumah123 Flash Report, Colliers, Kepmen PUPR, artikel properti. "
               "Rincian dan tingkat keyakinan tiap angka ada di tab City table.")

if gaji_kustom:
    kota_df["gaji"] = float(gaji_kustom)


def kotak_belajar(judul: str, isi: str, kode: str | None = None):
    if not mode_belajar:
        return
    with st.expander(f"🎓 {judul}", expanded=False):
        st.markdown(isi)
        if kode:
            st.code(kode, language="python")


# ---------------------------------------------------------------------------
# Halaman 1: Years to own
# ---------------------------------------------------------------------------

def halaman_tahun():
    st.title("How many years of saving is a roof?")
    st.markdown(
        "Kalau seluruh **{:.0f}% gaji** disisihkan tiap bulan, gaji naik {:.1f}% per tahun dan harga naik "
        "{:.1f}% per tahun, berapa tahun sampai uangnya cukup untuk membeli tunai? "
        "Angka ini bukan rencana keuangan, melainkan ukuran jarak antara gaji dan harga.".format(
            porsi_nabung, kenaikan_gaji, kenaikan_harga)
    )

    jenis = st.multiselect("Housing type", list(LABEL_HUNIAN), default=list(LABEL_HUNIAN),
                           format_func=LABEL_HUNIAN.get)
    if not jenis:
        st.info("Pilih setidaknya satu jenis hunian.")
        return

    tabel = hitung.tabel_tahun_menabung(kota_df, jenis, porsi_nabung, kenaikan_gaji, kenaikan_harga)
    urut_kolom = f"tahun_{jenis[0]}"
    tabel = tabel.sort_values(urut_kolom, ascending=False)  # Plotly menggambar baris pertama di bawah

    fig = go.Figure()
    for j in jenis:
        nilai = tabel[f"tahun_{j}"].replace(math.inf, float("nan"))
        fig.add_bar(
            y=tabel["kota"], x=nilai, orientation="h", name=LABEL_HUNIAN[j],
            marker_color=WARNA[j],
            text=[tahun_str(v) if pd.notna(v) else "no data" for v in nilai],
            textposition="outside",
            customdata=kota_df.set_index("kota").loc[tabel["kota"], j].values,
            hovertemplate="<b>%{y}</b><br>" + LABEL_HUNIAN[j] +
                          "<br>Harga: Rp%{customdata:,.0f}<br>Tahun menabung: %{x:.1f}<extra></extra>",
        )
    fig.update_layout(
        barmode="group", height=max(420, 24 * len(tabel) * max(1, len(jenis))),
        xaxis_title="Tahun menabung sampai bisa beli tunai", yaxis_title=None,
        legend=dict(orientation="h", y=1.08), margin=dict(l=10, r=10, t=30, b=10),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_xaxes(gridcolor="#e8e7e3", zeroline=False)
    st.plotly_chart(fig, width="stretch")

    kotak_belajar(
        "Kenapa tahun menabung dihitung bulan per bulan, bukan harga ÷ tabungan?",
        "Kalau gaji dan harga sama-sama diam, `tahun = harga / (gaji × porsi × 12)` sudah cukup. "
        "Tetapi gaji naik tiap tahun, dan harga rumah juga. Dua laju yang berbeda membuat rumus tertutupnya "
        "berantakan, jadi lebih jujur disimulasikan: tiap bulan setor, tiap awal tahun naikkan gaji dan harga, "
        "berhenti saat tabungan ≥ harga. Fungsi `tahun_menabung` di `src/hitung.py` melakukan itu, dan "
        "menyerah di 100 tahun supaya tidak berputar selamanya.",
        "for tahun in range(BATAS_TAHUN):\n    setoran = gaji * porsi_nabung / 100\n    for bulan in range(1, 13):\n"
        "        tabungan += setoran\n        if tabungan >= target:\n            return tahun + bulan / 12\n"
        "    gaji *= 1 + kenaikan_gaji / 100\n    target *= 1 + kenaikan_target / 100",
    )

    st.subheader("Price-to-income ratio")
    st.markdown(
        "Berapa **tahun gaji penuh** (tanpa makan, tanpa transport) yang setara dengan harga hunian. "
        "Ukuran ini dipakai di banyak negara untuk membandingkan keterjangkauan; di atas 5 biasanya "
        "disebut 'sangat tidak terjangkau'."
    )
    rasio = tabel[["kota"] + [f"rasio_{j}" for j in jenis]].set_index("kota")
    rasio.columns = [LABEL_HUNIAN[j] for j in jenis]
    fig2 = go.Figure()
    for j in jenis:
        fig2.add_bar(x=rasio.index, y=rasio[LABEL_HUNIAN[j]], name=LABEL_HUNIAN[j], marker_color=WARNA[j],
                     hovertemplate="<b>%{x}</b><br>%{y:.1f}× gaji setahun<extra></extra>")
    fig2.add_hline(y=5, line_dash="dot", line_color=WARNA["abu"],
                   annotation_text="5× = sangat tidak terjangkau", annotation_position="top left")
    fig2.update_layout(barmode="group", height=380, yaxis_title="Harga ÷ gaji setahun",
                       legend=dict(orientation="h", y=1.1), margin=dict(l=10, r=10, t=30, b=10),
                       plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    fig2.update_yaxes(gridcolor="#e8e7e3")
    st.plotly_chart(fig2, width="stretch")

    kotak_belajar(
        "Price-to-income ratio",
        "Rasio harga terhadap pendapatan setahun adalah ukuran paling sederhana dan paling sering dikutip "
        "(Demographia, UN-Habitat). Kelebihannya: tidak perlu asumsi bunga atau tabungan. Kekurangannya: "
        "mengabaikan KPR, DP, dan kenaikan gaji. Karena itu dashboard ini menampilkan keduanya.",
        "rasio = harga / (gaji_bulanan * 12)",
    )


# ---------------------------------------------------------------------------
# Halaman 2: Buy vs rent
# ---------------------------------------------------------------------------

def halaman_beli_sewa():
    st.title("Buy with a mortgage, or keep renting?")
    k1, k2, k3, k4 = st.columns([1.2, 1.4, 1.1, 1])
    kota = k1.selectbox("City", kota_df["kota"].tolist(), index=int((kota_df["kota"] == "Jakarta").idxmax()))
    baris = kota_df.set_index("kota").loc[kota]
    jenis = k2.selectbox("Housing to buy", list(LABEL_HUNIAN), format_func=LABEL_HUNIAN.get, index=1)
    harga_default = baris[jenis]
    if pd.isna(harga_default):
        st.warning(f"Belum ada data {LABEL_HUNIAN[jenis].lower()} untuk {kota}. Masukkan harga sendiri di bawah.")
        harga_default = baris["rumah_seken"]
    sewa_jenis = k3.selectbox("Rent to compare", list(LABEL_SEWA), format_func=LABEL_SEWA.get, index=1)
    horizon = k4.slider("Years to compare", 1, 30, 10)

    c1, c2 = st.columns(2)
    harga = c1.number_input("House price (Rp)", min_value=50_000_000, max_value=50_000_000_000,
                            value=int(round(harga_default, -6)), step=10_000_000)
    sewa = c2.number_input("Monthly rent (Rp)", min_value=100_000, max_value=100_000_000,
                           value=int(baris[sewa_jenis]), step=50_000)
    gaji = float(baris["gaji"])

    hasil = hitung.banding_beli_sewa(
        harga, sewa, horizon, dp_persen, tenor, bunga_tetap, tahun_tetap, bunga_mengambang,
        kenaikan_sewa, kenaikan_harga, gaji,
    )
    r, deret = hasil["ringkas"], hasil["deret"]

    st.markdown(f"Gaji acuan **{rp(gaji)}/bulan** ({baris['umk_dasar'] if gaji_kustom is None else 'custom'}).")
    m = st.columns(5)
    m[0].metric("Down payment", rp(r["dp"]), f"{dp_persen}% dari harga")
    m[1].metric("First instalment", rp(r["cicilan_awal"]), f"{r['porsi_cicilan_awal']:.0f}% of salary",
                delta_color="inverse" if r["porsi_cicilan_awal"] > 35 else "normal")
    m[2].metric("Highest instalment", rp(r["cicilan_tertinggi"]),
                f"{r['porsi_cicilan_tertinggi']:.0f}% of salary (floating)",
                delta_color="inverse" if r["porsi_cicilan_tertinggi"] > 35 else "normal")
    m[3].metric("Rent now", rp(sewa), f"{r['porsi_sewa']:.0f}% of salary",
                delta_color="inverse" if r["porsi_sewa"] > 35 else "normal")
    impas = hitung.titik_impas(deret)
    m[4].metric("Break-even", f"year {impas}" if impas else "none yet",
                "beli lebih murah setelah ini" if impas else f"sewa lebih murah selama {horizon} th",
                delta_color="normal" if impas else "inverse")

    if r["porsi_cicilan_awal"] > 35:
        st.error(f"Bank biasanya menolak KPR kalau cicilan melewati sekitar 30–35% penghasilan. "
                 f"Di sini cicilan pertama {r['porsi_cicilan_awal']:.0f}% dari gaji. Dengan gaji ini, KPR untuk "
                 f"harga {rp(harga)} tidak akan disetujui tanpa penghasilan tambahan atau DP lebih besar.")

    st.subheader(f"{horizon} years side by side")
    a, b, c = st.columns(3)
    a.metric("Total rent paid", rp(r["total_sewa"]))
    b.metric("Total paid for the house", rp(r["total_keluar_beli"]), "DP + semua cicilan")
    c.metric("Net cost of buying", rp(r["biaya_bersih_beli"]),
             f"setelah dikurangi ekuitas {rp(r['ekuitas_akhir'])}")

    fig = go.Figure()
    fig.add_scatter(x=deret["tahun"], y=deret["sewa_kumulatif"], name="Rent paid (cumulative)",
                    line=dict(color=WARNA["sewa"], width=3))
    fig.add_scatter(x=deret["tahun"], y=deret["kpr_kumulatif"], name="Cash out for the house (DP + instalments)",
                    line=dict(color=WARNA["kpr"], width=3))
    fig.add_scatter(x=deret["tahun"], y=deret["biaya_bersih_beli"], name="Net cost of buying (cash out − equity)",
                    line=dict(color=WARNA["bersih"], width=3, dash="dash"))
    fig.update_layout(height=420, xaxis_title="Tahun ke-", yaxis_title="Rupiah kumulatif",
                      legend=dict(orientation="h", y=1.1), margin=dict(l=10, r=10, t=30, b=10),
                      plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", hovermode="x unified")
    fig.update_yaxes(gridcolor="#e8e7e3", tickformat=",.0f")
    st.plotly_chart(fig, width="stretch")

    kotak_belajar(
        "Kenapa ada garis 'net cost', bukan hanya uang keluar?",
        "Orang yang menyewa tidak punya apa-apa di akhir; orang yang mencicil punya rumah (dikurangi utang yang "
        "belum lunas). Membandingkan total sewa dengan total cicilan saja berarti menganggap rumah tidak bernilai. "
        "Maka biaya bersih membeli = (DP + cicilan) − (nilai rumah saat itu − sisa pokok). Garis putus-putus "
        "inilah yang adil dibandingkan dengan garis sewa. Catatan: biaya notaris, pajak, perawatan dan hasil "
        "investasi alternatif dari DP belum dimasukkan; itu Latihan 6 di docs/LATIHAN.md.",
        "ekuitas = nilai_rumah - sisa_pokok\nbiaya_bersih_beli = kpr_kumulatif - ekuitas",
    )

    st.subheader("Where each instalment goes")
    jadwal = hasil["jadwal"].copy()
    jadwal["tahun"] = (jadwal["bulan"] - 1) // 12 + 1
    per_tahun = jadwal.groupby("tahun")[["bunga", "pokok"]].sum().reset_index()
    fig3 = go.Figure()
    fig3.add_bar(x=per_tahun["tahun"], y=per_tahun["bunga"], name="Interest", marker_color=WARNA["bersih"])
    fig3.add_bar(x=per_tahun["tahun"], y=per_tahun["pokok"], name="Principal", marker_color=WARNA["kpr"])
    if tahun_tetap and tahun_tetap < tenor:
        fig3.add_vline(x=tahun_tetap + 0.5, line_dash="dot", line_color=WARNA["abu"],
                       annotation_text="fixed → floating", annotation_position="top right")
    fig3.update_layout(barmode="stack", height=340, xaxis_title="Tahun ke-", yaxis_title="Rupiah per tahun",
                       legend=dict(orientation="h", y=1.12), margin=dict(l=10, r=10, t=30, b=10),
                       plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    fig3.update_yaxes(gridcolor="#e8e7e3", tickformat=",.0f")
    st.plotly_chart(fig3, width="stretch")
    st.caption(f"Total bunga sepanjang tenor {tenor} tahun: **{rp(r['total_bunga'])}**, "
               f"total yang dibayar (DP + cicilan): **{rp(r['total_bayar'])}** untuk rumah seharga {rp(harga)}.")

    kotak_belajar(
        "Anuitas dan lompatan setelah masa bunga tetap",
        "Cicilan anuitas dihitung supaya jumlahnya sama tiap bulan sepanjang sisa tenor. Di awal, sebagian "
        "besar cicilan adalah bunga, karena pokoknya masih besar. Saat bunga tetap berakhir, bank menghitung "
        "ulang cicilan dari sisa pokok dan sisa tenor dengan bunga mengambang; itulah lonjakan yang sering "
        "mengejutkan debitur di tahun ke-4.",
        "def cicilan_anuitas(pokok, bunga_tahunan, sisa_bulan):\n    r = bunga_tahunan / 100 / 12\n"
        "    return pokok * r / (1 - (1 + r) ** (-sisa_bulan))",
    )


# ---------------------------------------------------------------------------
# Halaman 3: City table
# ---------------------------------------------------------------------------

def halaman_tabel():
    st.title("The numbers behind every bar")
    st.markdown(
        "Semua angka diambil **sekali** dari laporan dan artikel yang dipublikasikan, lalu disimpan di "
        "`data/kota.csv`. Tidak ada scraping. Tiap angka membawa **kode mutu** supaya pembaca tahu seberapa "
        "jauh ia boleh dipercaya:"
    )
    for kode, label in muat_data.LABEL_MUTU.items():
        st.markdown(f"- **{label}**")

    tampil = pd.DataFrame({
        "City": kota_df["kota"],
        "Province": kota_df["provinsi"],
        "Minimum wage 2026 (Rp/month)": kota_df["umk_2026"],
        "Wage basis": kota_df["umk_dasar"],
        "Subsidised house cap (Rp)": kota_df["rumah_subsidi"],
        "Small second-hand house (Rp)": kota_df["rumah_seken"],
        "House grade": kota_df["rumah_seken_mutu"],
        "House period": kota_df["rumah_seken_periode"],
        f"Studio {asumsi['luas_studio']:.0f} m² (Rp)": kota_df["apartemen"],
        "Apartment grade": kota_df["apartemen_mutu"],
        "Kos (Rp/month, midpoint)": kota_df["kos"],
        "Kos grade": kota_df["kos_mutu"],
        "Kontrakan (Rp/month)": kota_df["kontrakan"],
        "Kontrakan grade": kota_df["kontrakan_mutu"],
    })
    st.dataframe(
        tampil, hide_index=True, width="stretch", height=520,
        column_config={c: st.column_config.NumberColumn(format="localized") for c in tampil.columns
                       if tampil[c].dtype.kind in "fi"},
    )

    st.subheader("Notes per city")
    kota = st.selectbox("City", kota_df["kota"].tolist(), key="catatan_kota")
    b = kota_df.set_index("kota").loc[kota]
    st.markdown(
        f"- **Gaji:** {rp(b['gaji'])}/bulan, {b['umk_dasar']}. Sumber: {b['umk_sumber']}.\n"
        f"- **Rumah subsidi:** batas harga FLPP zona {b['zona_flpp']} = {rp(b['rumah_subsidi'])} "
        f"(Kepmen PUPR 689/KPTS/M/2023, masih dipakai 2025).\n"
        f"- **Rumah seken ≤60 m²:** {rp(b['rumah_seken'])} [{b['rumah_seken_mutu']}], periode "
        f"{b['rumah_seken_periode']}. {b['rumah_seken_catatan']}.\n"
        f"- **Apartemen:** {('Rp' + format(b['apartemen_per_m2'] / 1e6, '.1f') + ' jt/m² [' + str(b['apartemen_mutu']) + ']') if pd.notna(b['apartemen_per_m2']) else 'tidak ada data'}. "
        f"{b['apartemen_catatan']}.\n"
        f"- **Kos:** {rp(b['kos_min'])}–{rp(b['kos_max'])} [{b['kos_mutu']}], sumber {b['kos_sumber']}.\n"
        f"- **Kontrakan:** {rp(b['kontrakan'])}/bulan [{b['kontrakan_mutu']}]. {b['kontrakan_catatan']}."
    )
    st.download_button("Download data (CSV)", kota_df.to_csv(index=False).encode("utf-8"),
                       "roof_vs_paycheck_kota.csv", "text/csv")
    st.caption("Rincian metodologi dan tautan tiap sumber ada di data/SUMBER_DATA.md di repo.")


# ---------------------------------------------------------------------------
# Halaman 4: How it works
# ---------------------------------------------------------------------------

def halaman_cara_kerja():
    st.title("How it works")
    st.markdown(
        """
**Pertanyaan yang dijawab dashboard ini:** seberapa jauh jarak antara upah minimum di sebuah kota
dan harga atap di kota yang sama, dan apakah mencicil lebih masuk akal daripada menyewa.

**Alur data**

```
laporan & SK (dibaca manual, sekali)  →  data/kota.csv + data/asumsi.csv
        →  src/muat_data.py (validasi, konversi satuan)
        →  src/hitung.py   (tahun menabung, rasio, KPR anuitas, beli vs sewa)
        →  app.py          (Streamlit + Plotly)
```

**Definisi**

| Istilah | Arti di dashboard ini |
|---|---|
| Gaji | UMK 2026 kota (atau UMP kalau kota tidak punya UMK), atau angka yang kamu masukkan sendiri |
| Subsidised house | Batas harga rumah subsidi FLPP per zona (Kepmen PUPR 689/2023). Rumah tapak baru tipe 30-36 di pinggir kota |
| Small second-hand house | Median harga iklan rumah seken ≤60 m² bangunan di kota itu (Rumah123 Flash Report) atau perkiraannya |
| Studio apartment | Harga rata-rata per m² × 25 m² |
| Kos | Titik tengah rentang kos standar di kota itu |
| Kontrakan | Rumah petak/kontrakan 1-2 kamar sederhana, kisaran bawah pasar |
| Years to own | Tahun menabung sampai bisa beli tunai dengan porsi gaji yang dipilih |
| Net cost of buying | (DP + cicilan) − (nilai rumah − sisa pokok); yang adil dibandingkan dengan total sewa |

**Keterbatasan yang perlu kamu tahu**

- Harga rumah adalah **harga iklan**, bukan harga transaksi; biasanya 5-10% lebih tinggi dari harga deal.
- Beberapa angka rumah (kode E) **diperkirakan dari segmen lain** karena laporan publik tidak memuat
  segmen ≤60 m² untuk kota itu. Rasio yang dipakai berasal dari kota-kota Bodetabek yang punya semua segmen.
- Angka kos dan kontrakan berasal dari artikel dan simulasi biaya hidup, bukan survei resmi.
- UMK adalah **upah minimum**. Pekerja berpengalaman biasanya di atas itu; gunakan *Custom salary*.
- Biaya notaris, BPHTB, asuransi, perawatan, dan imbal hasil kalau DP diinvestasikan belum dihitung.
- Semua laju pertumbuhan adalah asumsi yang bisa digeser; jangan percaya satu angka, geser dan lihat rentangnya.
"""
    )
    st.subheader("Default assumptions")
    a = pd.read_csv(muat_data.FOLDER_DATA / "asumsi.csv")
    st.dataframe(a, hide_index=True, width="stretch")


HALAMAN = {
    "Years to own": halaman_tahun,
    "Buy vs rent": halaman_beli_sewa,
    "City table": halaman_tabel,
    "How it works": halaman_cara_kerja,
}
HALAMAN.get(halaman or "Years to own", halaman_tahun)()
