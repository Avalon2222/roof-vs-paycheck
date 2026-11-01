# 🎓 Panduan Belajar: Menghitung Jarak antara Gaji dan Atap

Panduan ini untuk pembaca yang sudah bisa Python dasar (variabel, fungsi, list, dict) dan ingin tahu
*mengapa* kode di repo ini ditulis seperti itu. Bacalah sambil membuka file yang dibahas. Semua bisa
dicoba di terminal Python tanpa internet, karena datanya sudah ada di `data/`.

Yang akan kamu kuasai setelah selesai:

- membangun **dataset kecil dengan tangan** dan tetap jujur soal kualitas tiap angkanya,
- tiga cara mengukur keterjangkauan: rasio, tahun menabung, dan porsi cicilan,
- rumus **anuitas** KPR dan kenapa cicilan melonjak di tahun ke-4,
- membandingkan dua jalan hidup (sewa vs cicil) secara **adil**, bukan hanya menjumlahkan uang keluar,
- dan kebiasaan memisahkan rumus dari tampilan supaya rumusnya bisa diuji.

---

## Peta besar

```
┌──────────────────────────────────────────────────────────────────┐
│  LAPISAN 3: TAMPILAN     app.py                                   │
│  sidebar → ambil baris kota → panggil hitung → Plotly             │
├──────────────────────────────────────────────────────────────────┤
│  LAPISAN 2: LOGIKA       src/hitung.py                            │
│  tahun_menabung · rasio · jadwal_kpr · banding_beli_sewa          │
├──────────────────────────────────────────────────────────────────┤
│  LAPISAN 1: DATA         src/muat_data.py + data/*.csv            │
│  13 kota, satuan dikonversi, kode mutu divalidasi                 │
└──────────────────────────────────────────────────────────────────┘
```

Lapisan 2 tidak tahu apa-apa soal file, Streamlit, atau kota. Ia hanya menerima angka dan
mengembalikan angka. Itu sebabnya `tests/test_hitung.py` bisa memakai contoh seperti "rumah 120 juta,
gaji 1 juta" yang hasilnya bisa dihitung di kepala.

---

## Langkah 1 — Data yang dibuat dengan tangan (`data/kota.csv`)

Kebanyakan dashboard di repo-repo sebelah mengunduh data dari API. Di sini tidak ada API: tidak ada
lembaga yang menerbitkan "harga rumah kecil per kota" dalam format JSON. Yang ada adalah laporan
PDF, artikel berita yang mengutip laporan itu, dan SK gubernur. Maka datanya **dibaca manual** dan
diketik ke CSV.

Dua keputusan penting di sini:

1. **Satu baris per kota, satu kolom per angka, satu kolom tambahan untuk mutu dan catatan.** Buka
   CSV-nya: `rumah_seken_juta` ditemani `rumah_seken_mutu`, `rumah_seken_periode`, dan
   `rumah_seken_catatan`. Angka tanpa asal-usul tidak berguna untuk siapa pun yang ingin mengecek.
2. **Kode mutu A/B/C/E.** A = angka persis dari laporan untuk kota dan segmen yang sama. E = perkiraan,
   misalnya "0,6 × median segmen 61-90 m²". Dashboard menampilkan kode ini di tab City table. Pembaca
   boleh tidak percaya, tetapi ia tahu persis *apa* yang tidak dipercayainya.

Coba:

```python
import pandas as pd
df = pd.read_csv("data/kota.csv")
print(df[["kota", "rumah_seken_juta", "rumah_seken_mutu", "rumah_seken_catatan"]])
```

Perhatikan satuan yang sengaja berbeda: harga rumah dalam juta (supaya mudah diketik dan dibaca),
kos dalam rupiah penuh. `src/muat_data.py` yang menyamakan semuanya ke rupiah penuh, sekali, di satu
tempat. Kalau konversinya tersebar di app.py, cepat atau lambat ada yang lupa dikali sejuta.

---

## Langkah 2 — Validasi sebelum dipakai (`src/muat_data.py`)

`muat_kota` tidak hanya `read_csv`. Ia memeriksa kolom wajib, nama kota ganda, kode mutu yang tidak
dikenal, dan angka negatif, lalu melempar `ValueError` dengan pesan yang jelas. Kenapa repot?

Karena CSV ini akan diedit tangan (oleh kamu, di Latihan 2). Salah ketik `rumah_seken_juta` menjadi
`600000000` (sudah rupiah) akan membuat Jakarta terlihat 1.000× lebih mahal, dan dashboard akan tetap
jalan tanpa protes. Lebih baik gagal keras di awal daripada menghasilkan grafik yang salah dengan
percaya diri. `tests/test_muat_data.py` memastikan batas-batas itu (gaji 2-8 juta, rumah 300 juta-2
miliar) tetap berlaku untuk semua baris.

---

## Langkah 3 — Rasio harga terhadap gaji

```python
def rasio_harga_gaji(harga, gaji_bulanan):
    return harga / (gaji_bulanan * 12)
```

Satu baris, tetapi ini ukuran keterjangkauan yang dipakai Demographia, UN-Habitat, dan hampir semua
studi perumahan internasional. Kelebihannya: tidak butuh asumsi apa pun soal bunga, tabungan, atau
masa depan. Kekurangannya: mengabaikan semua itu juga. Angka 3 dianggap terjangkau, 5 ke atas "sangat
tidak terjangkau". Rumah seken kecil di 13 kota kita semuanya di atas 7.

---

## Langkah 4 — Tahun menabung: kenapa harus disimulasikan

Kalau gaji dan harga diam, `tahun = harga / (gaji × porsi × 12)`. Tetapi gaji naik (UMK naik 6,5% per
tahun belakangan) dan harga juga naik (1% per tahun menurut BI). Dua laju berbeda membuat rumus
tertutupnya tidak enak dilihat, dan lebih penting lagi, tidak enak *dijelaskan*. Jadi `tahun_menabung`
menyimulasikannya bulan per bulan:

```python
for tahun in range(BATAS_TAHUN):
    setoran = gaji * porsi_nabung / 100
    for bulan in range(1, 13):
        tabungan += setoran
        if tabungan >= target:
            return tahun + bulan / 12
    gaji *= 1 + kenaikan_gaji / 100
    target *= 1 + kenaikan_target / 100
return math.inf
```

Tiga hal yang layak diperhatikan:

- **Resolusi bulan.** Mengembalikan `2.25` lebih informatif daripada `3`.
- **`math.inf` kalau tidak tercapai.** Kalau harga naik 20% per tahun dan gaji diam, tabungan tidak akan
  pernah mengejar. Tanpa batas 100 tahun, loop-nya berputar selamanya. `inf` juga mudah diperiksa
  (`math.isinf`) dan Plotly menggambarnya sebagai "tidak ada data" setelah diganti `NaN`.
- **Tidak ada bunga tabungan.** Sengaja. Menambahkan 4% bunga deposito mengubah angkanya sedikit dan
  menambah satu slider lagi. Itu Latihan 4.

Coba di terminal: ubah `kenaikan_gaji` dari 0 ke 6,5 dan lihat tahun menabung untuk rumah Rp600 juta
dengan gaji Rp5 juta turun dari 40 tahun ke sekitar 20 tahun. Kenaikan gaji adalah variabel yang
paling sering dilupakan orang ketika bilang "tidak akan pernah".

---

## Langkah 5 — Anuitas: cicilan yang sama tiap bulan

Bank menghitung cicilan KPR dengan rumus anuitas:

```python
def cicilan_anuitas(pokok, bunga_tahunan, sisa_bulan):
    r = bunga_tahunan / 100 / 12          # bunga per bulan
    return pokok * r / (1 - (1 + r) ** (-sisa_bulan))
```

Dari mana rumus ini? Cicilan tetap C selama n bulan dengan bunga r per bulan harus "senilai" dengan
pokok hari ini. Nilai sekarang dari n pembayaran C adalah deret geometri
`C × (1 − (1+r)^−n) / r`. Samakan dengan pokok, selesaikan untuk C. Tes di `test_hitung.py` memakai
100 juta, 12% per tahun, 12 bulan dan membandingkan dengan 8.884.879, angka yang bisa kamu cek di
kalkulator KPR mana pun.

Kasus khusus `r == 0` ditangani terpisah, karena rumus di atas membagi dengan nol. Tes
`test_banding_beli_sewa_bunga_nol_tanpa_kenaikan` memanfaatkan kasus ini: dengan bunga nol semua angka
jadi bulat dan mudah diverifikasi.

---

## Langkah 6 — KPR dua tahap dan lonjakan tahun ke-4

Hampir semua promo KPR di Indonesia berbunyi "6,5% fixed 3 tahun, selanjutnya floating". Yang jarang
dibaca orang: setelah masa tetap berakhir, bank **menghitung ulang** cicilan dari sisa pokok dan sisa
tenor dengan bunga mengambang (11-13%). `jadwal_kpr` meniru persis itu:

```python
cicilan = cicilan_anuitas(sisa, bunga_tetap, total_bulan)
for b in range(1, total_bulan + 1):
    if b == bulan_tetap + 1:
        cicilan = cicilan_anuitas(sisa, bunga_mengambang, total_bulan - bulan_tetap)
    bunga = sisa * laju / 100 / 12
    angsuran_pokok = cicilan - bunga
    sisa -= angsuran_pokok
```

Buka tab Buy vs rent, pilih Jakarta, rumah seken: cicilan pertama Rp6 juta, cicilan setelah tahun
ke-3 Rp8,1 juta. Kenaikan sepertiga. Grafik "Where each instalment goes" menunjukkan kenapa: di tahun
pertama, lebih dari separuh cicilan adalah bunga, karena pokoknya masih hampir utuh.

Fungsi ini mengembalikan **DataFrame per bulan**, bukan hanya total. Dengan jadwal lengkap, semua
turunannya (total bunga, sisa pokok di tahun ke-t, komposisi per tahun) tinggal `groupby` dan `sum`.
Menghitung tiap turunan dengan rumus tertutup terpisah berarti tiga rumus yang bisa saling tidak
konsisten.

---

## Langkah 7 — Beli vs sewa yang adil

Perbandingan naif: total sewa 10 tahun vs total cicilan 10 tahun. Cicilan hampir selalu menang
"lebih mahal", dan kesimpulannya "sewa lebih untung". Tetapi di tahun ke-10 penyewa tidak punya apa-apa,
sedangkan pencicil punya rumah dikurangi sisa utang. Maka:

```python
ekuitas = nilai_rumah - sisa_pokok                 # yang benar-benar dimiliki
biaya_bersih_beli = kpr_kumulatif - ekuitas        # uang keluar dikurangi aset
```

Garis `biaya_bersih_beli` inilah yang dibandingkan dengan `sewa_kumulatif`, dan `titik_impas` mencari
tahun pertama ketika garis itu turun di bawah sewa. Dengan kenaikan harga 1% per tahun, titik impas
sering tidak tercapai dalam 10 tahun; dengan 5% per tahun hampir selalu tercapai. Itu sebabnya slider
*House price growth* adalah slider paling berbahaya di dashboard ini: satu angka kecil mengubah
kesimpulan besar. Dashboard yang jujur menaruh angka itu di tangan pembaca, bukan menyembunyikannya di
konstanta.

Yang masih belum adil, dan sengaja ditinggalkan untuk Latihan 6: biaya beli (BPHTB 5%, notaris, provisi),
perawatan tahunan, dan *opportunity cost* kalau DP diinvestasikan.

---

## Langkah 8 — Tampilan yang tidak menghitung (`app.py`)

Perhatikan pola di tiap halaman: baca pilihan dari sidebar → ambil satu baris kota → panggil satu
fungsi di `hitung` → gambar. `app.py` tidak pernah mengalikan atau membagi harga, kecuali untuk format
teks. Beberapa kebiasaan kecil yang membantu:

- `@st.cache_data` di `muat_semua` supaya CSV dibaca sekali, bukan tiap klik slider.
- `rp()` mengubah 900000000 jadi "Rp900,0 jt" dengan pemisah ribuan gaya Indonesia (titik dan koma
  ditukar lewat trik `replace` tiga langkah).
- `st.segmented_control` untuk halaman, bukan `st.tabs`, supaya hanya satu halaman yang dirender.
- `delta_color="inverse"` pada `st.metric` ketika cicilan melewati 35% gaji, dan `st.error` yang
  menjelaskan kenapa bank akan menolak. Dashboard boleh punya pendapat, asal pendapatnya ditulis
  sebagai aturan yang bisa dicek.

---

## Langkah 9 — Tes yang bisa dihitung di kepala (`tests/`)

Setiap tes di `test_hitung.py` memakai angka bulat: rumah 120 juta, DP 0, bunga 0, tenor 10 tahun,
cicilan tepat 1 juta per bulan. Dengan angka seperti itu, kalau tes gagal kamu langsung tahu *apa*
yang salah, bukan hanya *bahwa* ada yang salah. Tes di `test_muat_data.py` berbeda sifatnya: ia menjaga
**data**, bukan rumus, dengan rentang kewajaran. Kalau nanti kamu menambah kota dan salah satuan,
tes inilah yang berteriak lebih dulu.

Jalankan `python -m pytest tests/ -v` setelah tiap perubahan. Lalu lanjut ke `LATIHAN.md`.
