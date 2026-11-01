# Sumber data

Semua angka di folder ini **dikumpulkan sekali secara manual** dari laporan, SK, dan artikel yang
dipublikasikan (diakses 1 November 2026), lalu disimpan sebagai CSV. Tidak ada scraping, tidak ada
panggilan API saat dashboard berjalan. Kalau ingin memperbarui, ubah CSV-nya dan catat sumbernya di sini.

Tiap angka harga membawa **kode mutu** supaya pembaca tahu seberapa jauh ia boleh dipercaya:

| Kode | Arti |
|---|---|
| **A** | Angka langsung dari laporan lembaga atau SK resmi, untuk kota dan segmen yang sama |
| **B** | Rentang dari artikel atau simulasi biaya hidup; dipakai titik tengahnya |
| **C** | Dihitung dari listing/iklan atau artikel properti tanpa metode yang jelas |
| **E** | Perkiraan: diturunkan dari segmen lain lewat rasio, atau disamakan dengan kota tetangga |

## 1. `kota.csv` — satu baris per kota (13 kota)

| Kolom | Satuan | Arti |
|---|---|---|
| `kota`, `provinsi` | | Nama kota (semua *kota*, bukan kabupaten) |
| `zona_flpp` | | Zona harga rumah subsidi: Jabodetabek, Jawa, Sumatera, Sulawesi, Bali |
| `umk_2026` | Rp/bulan | Upah minimum 2026 kota itu (UMP untuk Jakarta) |
| `umk_dasar`, `umk_sumber` | | Dasar penetapan dan sumber yang dibaca |
| `rumah_subsidi_juta` | juta Rp | Batas harga jual rumah subsidi FLPP di zona itu |
| `rumah_seken_juta` | juta Rp | Median harga iklan rumah seken dengan luas bangunan ≤60 m² |
| `rumah_seken_mutu`, `rumah_seken_periode`, `rumah_seken_catatan` | | Kode mutu, bulan data, cara mendapatkannya |
| `apartemen_per_m2_juta` | juta Rp/m² | Harga jual rata-rata apartemen per m² (kosong = tidak ada data) |
| `apartemen_mutu`, `apartemen_catatan` | | |
| `kos_min`, `kos_max` | Rp/bulan | Rentang kos standar (kamar, kamar mandi dalam, tanpa AC) |
| `kos_mutu`, `kos_sumber` | | |
| `kontrakan` | Rp/bulan | Rumah petak / kontrakan 1-2 kamar sederhana, kisaran bawah pasar |
| `kontrakan_mutu`, `kontrakan_catatan` | | |

### Upah minimum 2026

Semua UMK 2026 berlaku 1 Januari 2026, ditetapkan Desember 2025 dengan rumus PP 49/2025
(kenaikan rata-rata nasional 6,5%).

| Kota | UMK 2026 | Sumber |
|---|---|---|
| Jakarta | Rp5.729.876 (UMP, DKI tidak punya UMK) | [Kompas TV, 26 Des 2025](https://www.kompas.tv/info-publik/639870/daftar-lengkap-ump-2026-di-seluruh-provinsi-dki-jakarta-tertinggi-dengan-rp5-729-876?page=all) |
| Bekasi, Depok, Bogor, Tangerang, Tangerang Selatan*, Surabaya | Rp5.999.443 / 5.522.662 / 5.437.203 / 5.399.406 / 5.247.870 / 5.288.796 | [Industry.co.id, daftar 10 UMK tertinggi](https://www.industry.co.id/read/152368/daftar-gaji-umrumk-2026-di-seluruh-indonesia-lengkap-38-provinsi) |
| Bandung | Rp4.737.678 | [Kompas Money, 29 Des 2025](https://money.kompas.com/read/2025/12/29/092810326/ump-2026-jawa-barat-naik-jadi-rp-23-juta-ini-daftar-lengkap-umk-jawa-barat) |
| Semarang, Surakarta | Rp3.701.709 / Rp2.570.000 | [Bisnis.com, 28 Des 2025](https://ekonomi.bisnis.com/read/20251228/12/1939935/lengkap-daftar-umk-jateng-2026-di-35-kabupaten-kota) (Kepgub Jateng 100.3.3.1/505/2025) |
| Yogyakarta | Rp2.827.593 | [Doyan Duit, daftar UMK Pulau Jawa](https://doyanduit.com/news/lengkap-daftar-ump-dan-umk-2026-seluruh-kabupaten-kota-di-pulau-jawa/) — satu sumber sekunder, perlu dicek ke SK Gubernur DIY |
| Medan | Rp4.335.198 | [GoodStats, SK Gubsu 24 Des 2025](https://data.goodstats.id/statistic/daftar-umk-sumatra-utara-2026-kota-medan-naik-8-RCShe) |
| Makassar | Rp4.148.719 | [Metro TV / Pemkot Makassar](https://www.metrotvnews.com/read/NOlC9xp9-berapa-umk-makassar-di-2026-cek-besaran-terbarunya-di-sini), [Antara](https://makassar.antaranews.com/berita/616783/sah-umk-makassar-2026-disepakati-rp414-juta) |
| Denpasar | Rp3.499.878,78 (dibulatkan) | [Pengumuman Disnaker ESDM Bali, 24 Des 2025 (PDF)](https://disnakeresdm.baliprov.go.id/wp-content/uploads/2025/12/PENGUMUMAN-DAN-SK-UMK-UMSK-TAHUN-2026.pdf) |

\* Tangerang Selatan tidak dimasukkan karena tidak ada angka rumah per kota yang terpisah dari Tangerang.

### Rumah subsidi (FLPP)

Batas harga jual rumah subsidi per zona menurut Kepmen PUPR 689/KPTS/M/2023, yang oleh Kementerian
PKP dinyatakan tetap berlaku untuk 2025: Jawa (non-Jabodetabek) dan Sumatera Rp166 juta, Kalimantan
Rp182 juta, Sulawesi Rp173 juta, Jabodetabek dan Bali Rp185 juta.
Sumber: [Databoks](https://databoks.katadata.co.id/properti/statistik/6a3cf21c04022/kisaran-harga-rumah-subsidi-bp-tapera),
[Investortrust](https://investortrust.id/business/52428/pemerintah-ungkap-tak-ada-kenaikan-harga-rumah-subsidi-di-2025).
Ini harga rumah tapak baru tipe 30-36 di pinggir kota, dengan syarat penghasilan maksimum
(Rp12-14 juta sejak 2025). Dipakai sebagai "harga atap paling murah yang resmi ada".

### Rumah seken kecil (≤60 m²)

Sumber utama: **Rumah123 Flash Report**, median harga iklan rumah seken per kota per segmen luas
bangunan, sebagaimana dikutip media.

| Kota | Angka | Mutu | Dari mana |
|---|---|---|---|
| Bogor, Depok, Tangerang, Bekasi | 485 / 600 / 850 / 565 juta | A | [Detik, Flash Report Jun 2025](https://www.detik.com/properti/berita/d-8050272/daftar-harga-rumah-bodetabek-penyangga-jakarta-mana-paling-murah) |
| Bandung, Surabaya | 600 / 750 juta | A | [Detik, ~Jan 2025](https://www.detik.com/properti/berita/d-7745385/harga-rumah-seken-di-denpasar-surakarta-makin-mahal-segini-kisarannya) |
| Makassar | 675 juta | A | [Iconomics, Flash Report Jan 2026](https://www.theiconomics.com/art-of-execution/laporan-rumah123-2025-jadi-tahun-penyeimbang-pasar-properti-siap-masuk-fase-baru-di-2026/) |
| Surakarta | 500 juta (Des 2024) | A | [Medcom, Flash Report Feb 2025](https://www.medcom.id/properti/news-properti/lKYD5lVk-rumah-seken-ukuran-kecil-sedang-paling-diminati-harga-naik-melesat) |
| Jakarta | 900 juta | E | Di antara Jakarta Pusat Rp741 juta ([Rumah123, Mar 2026](https://www.rumah123.com/panduan-properti/harga-rumah-sekunder-turun/)) dan Jakarta Selatan Rp1,1 miliar ([Medcom, Agu 2026](https://www.medcom.id/properti/news-properti/Gbm0le4N-harga-rumah-seken-tertahan-makassar-dan-denpasar-justru-melonjak)) |
| Semarang | 525 juta | E | 0,6 × median 61-90 m² Rp875 juta (Medcom, Feb 2025) |
| Yogyakarta | 660 juta | E | 0,6 × median 61-90 m² Rp1,1 miliar (Medcom, Agu 2026) |
| Denpasar | 800 juta | E | 0,4 × median 91-150 m² Rp2 miliar (Medcom, Feb 2025) |
| Medan | 430 juta | E | 0,24 × median 151-250 m² Rp1,8 miliar ([Kompas, Mar 2026](https://www.kompas.com/properti/read/2026/01/14/130000821/harga-rumah-seken-di-yogyakarta-dan-denpasar-anjlok)) |

Rasio untuk kode E diambil dari empat kota Bodetabek yang punya semua segmen pada Juni 2025:
median ≤60 m² dibagi median 61-90 m² berkisar 0,53-0,64 (dipakai 0,6); dibagi 91-150 m²
0,32-0,43 (dipakai 0,4); dibagi 151-250 m² 0,19-0,27 (dipakai 0,24). Ini perkiraan kasar;
Latihan 2 di `docs/LATIHAN.md` meminta pembaca menggantinya dengan angka asli dari Flash Report.

### Apartemen (harga per m²)

| Kota | Rp juta/m² | Mutu | Sumber |
|---|---|---|---|
| Jakarta | 35,9 | A | Colliers, rata-rata harga penawaran Q2 2025 ([HousingEstate](https://housingestate.id/read/2025/10/01/coliiers-pasar-apartemen-jakarta-tetap-stabil/)) |
| Bekasi | 21 | C | Dihitung dari listing studio dan 2BR di 99.co (Rp17-24 juta/m²) |
| Depok, Tangerang | 20 | E | Perkiraan Bodetabek; Savills 2019 menyebut Rp13-23 juta/m², sejak itu naik tipis |
| Bandung | 25 | C | Artikel properti, apartemen pusat kota Rp20-30 juta/m² |
| Surabaya | 18 | C | Artikel properti, kelas menengah dari Rp12 juta/m², premium Rp25-35 juta/m² |
| Semarang, Yogyakarta (Sleman) | 23 / 23,7 | C | [Majalah Teras](https://majalahteras.com/harga-apartemen-jakarta-kalah-mahal-ketimbang-di-gianyar/) |
| Medan, Makassar | 15 / 14,5 | C | Artikel properti sekitar 2024, Rp10-20 dan Rp9-20 juta/m² |
| Bogor, Surakarta, Denpasar | kosong | | Pasokan apartemen strata hampir tidak ada |

Studio dihitung 25 m² (`luas_studio` di `asumsi.csv`).

### Kos

Rentang per kota dari [Dataloka, "Biaya hidup kuliah di 20 kota kampus 2026/2027"](https://dataloka.id/humaniora/7910/biaya-hidup-mahasiswa-kota-kampus-indonesia-2026-2027/)
(25 Sep 2026). Artikel itu sendiri menyebut angkanya **simulasi** berdasarkan BPS, informasi biaya hidup
perguruan tinggi dan KIP Kuliah, bukan survei harga; karena itu kode B. Pembanding:
[SuperKos, Mar 2025](https://superkos.id/blog/perbandingan-harga-kos-di-berbagai-kota/) memberi
Jakarta Rp800 ribu-1,5 juta, Surabaya Rp500 ribu-1 juta, Yogyakarta Rp350-700 ribu, Bandung Rp800 ribu-2
juta (dekat kampus). Bekasi dari [Bekasi Kinian 2026](https://www.bekasikinian.com/kota-bekasi/33816948125/biaya-hidup-di-kota-bekasi-2026-rincian-lengkap-dari-kos-hingga-makan)
(kos sederhana Rp800 ribu-1,5 juta). Tangerang disamakan dengan Bekasi (E).

### Kontrakan

Paling lemah dari semua kolom. Tidak ada laporan publik tentang harga kontrakan petak per kota; yang ada
hanya "harga termurah" di situs sewa dan listing perorangan: Jakarta tipe 2 kamar mulai Rp2,2 juta dan
Bogor Rp600-700 ribu ([Travelio](https://www.travelio.com/sewa-rumah-kontrakan-jakarta)), Surabaya petakan
2 kamar Rp1,1 juta, Yogyakarta Rp1,35 juta (Travelio), Bandung Rp1-2 juta ([99.co](https://www.99.co/id/sewa/rumah/bandung/bulanan)),
Depok Rp1,5-4 juta (Rumah123), Medan Rp1,5 juta (satu iklan petak). Untuk kota tanpa sumber
(Tangerang, Semarang, Surakarta, Makassar, Denpasar) dipakai **1,5 × titik tengah kos** (kode E).
Angka ini sengaja mudah diganti: kolom `kontrakan` di CSV, atau kotak *Monthly rent* di dashboard.

## 2. `asumsi.csv` — angka awal slider

| Parameter | Nilai | Sumber |
|---|---|---|
| BI-Rate | 5,75% | [Bank Indonesia, RDG 20-21 Okt 2026](https://www.bi.go.id/id/statistik/indikator/bi-rate.aspx) |
| Bunga KPR tetap | 6,5% selama 3 tahun | Promo bank besar 2026 berkisar 3-7% untuk 3-5 tahun pertama (mis. [BRI Okt 2026](https://housingestate.id/read/2026/10/27/sambut-ultah-ke-131-bank-bri-tawarkan-kpr-dengan-bunga-131-persen/)); dipakai nilai tengah |
| Bunga KPR mengambang | 11% | BCA 11%, Mandiri 12-13%, Danamon 12,5%, CIMB Niaga 13,5% ([Kontan](https://keuangan.kontan.co.id/news/likuiditas-bank-ketat-begini-bunga-floating-kpr)) |
| DP | 10% | LTV sampai 100% diizinkan BI, tetapi bank umumnya minta 10-20% |
| Tenor | 20 tahun | Tenor paling umum |
| Kenaikan harga rumah | 1%/tahun | BI Survei Harga Properti Residensial 2025: IHPR +0,83% sampai +1,07% yoy ([BI](https://www.bi.go.id/id/publikasi/ruang-media/news-release/Pages/sp_2726625.aspx)) |
| Kenaikan sewa | 3%/tahun | Asumsi mendekati inflasi |
| Kenaikan gaji | 6,5%/tahun | Rata-rata kenaikan UMP 2026 (PP 49/2025) |
| Porsi nabung | 30% gaji | Asumsi awal |

## Keterbatasan data

- Harga rumah dan apartemen adalah **harga iklan/penawaran**, bukan transaksi. Harga deal biasanya 5-10%
  lebih rendah.
- Median per kota mencampur lokasi pinggir dan pusat. "≤60 m²" di Jakarta Selatan dan di Bogor bukan
  barang yang sama.
- Periode data berbeda-beda (Des 2024 sampai Agu 2026). Dengan kenaikan harga 1%/tahun, selisihnya kecil,
  tetapi ada.
- UMK adalah batas bawah upah, bukan upah tipikal. Dashboard menyediakan *Custom salary*.
- Kos dan kontrakan dari simulasi dan listing; tidak ada survei resmi harga sewa per kota.
