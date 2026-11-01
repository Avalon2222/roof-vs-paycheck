# 🏋️ Latihan

Urut dari yang paling mudah. Bintang = tingkat kesulitan. Tiap latihan punya petunjuk dan cara
mengecek jawabanmu. Kerjakan di branch baru (`git checkout -b latihan-1`) supaya kalau ada yang rusak
kamu bisa kembali dengan mudah. Jalankan `python -m pytest tests/ -v` setelah tiap latihan.

---

### Latihan 1 — Gaji kamu sendiri ⭐

Buka dashboard, pilih *Custom salary*, masukkan gaji (atau gaji yang kamu harapkan). Di tab Years to
own, catat tiga kota dengan tahun menabung terpendek untuk rumah seken. Lalu ke Buy vs rent: di kota
mana cicilan pertama rumah seken masuk di bawah 35% gaji?

**Cek:** kamu bisa menjelaskan kenapa urutan kota di Years to own berubah saat gaji diganti dari UMK ke
angka tunggal (petunjuk: dengan gaji tunggal, yang tersisa hanya urutan harga).

---

### Latihan 2 — Ganti perkiraan dengan angka asli ⭐

Lima kota memakai kode mutu **E** untuk rumah seken (Jakarta, Semarang, Yogyakarta, Medan, Denpasar).
Cari edisi terbaru Rumah123 Flash Report (atau berita yang mengutipnya) yang memuat median segmen
≤60 m² untuk salah satu kota itu. Ganti angkanya di `data/kota.csv`, ubah mutunya jadi **A**, isi
`rumah_seken_periode` dan `rumah_seken_catatan`, dan tambahkan tautannya di `data/SUMBER_DATA.md`.

**Cek:** `pytest tests/test_muat_data.py` tetap hijau, dan tab City table menampilkan A untuk kota itu.
Kalau angkanya di luar rentang 300 juta-2 miliar, tes akan gagal; itu pertanda baik, cek ulang
satuannya.

---

### Latihan 3 — Tambah kota ⭐⭐

Tambahkan Tangerang Selatan, Malang, Palembang, atau Balikpapan. UMK 2026-nya mudah dicari; harga
rumahnya yang sulit. Terima saja kode mutu C atau E untuk awal, asal catatannya jujur. Untuk zona
FLPP: Kalimantan Rp182 juta, Sumatera Rp166 juta, Jawa Rp166 juta, Jabodetabek Rp185 juta.

**Cek:** kota baru muncul di semua halaman tanpa mengubah `app.py` sama sekali. Kalau kamu harus
mengubah app.py, berarti ada yang di-*hardcode* dan itu bug yang layak diperbaiki.

---

### Latihan 4 — Bunga tabungan ⭐⭐

`tahun_menabung` menganggap tabungan tidak berbunga. Tambahkan parameter `bunga_tabungan` (persen per
tahun, default 0) yang diterapkan tiap akhir tahun: `tabungan *= 1 + bunga_tabungan / 100`. Tambahkan
slider di sidebar dan teruskan ke `tabel_tahun_menabung`.

**Cek:** tulis tes: 1 juta/bulan, target 24 juta, bunga 0 → 2 tahun; bunga 10% → kurang dari 2 tahun
(tabungan 12 juta di akhir tahun pertama jadi 13,2 juta). Semua tes lama harus tetap lulus karena
default-nya 0.

---

### Latihan 5 — KPR berjenjang ⭐⭐

Beberapa bank memakai bunga berjenjang: 3% tahun 1-3, 7% tahun 4-6, 10% tahun 7-20. Ubah `jadwal_kpr`
agar menerima daftar `[(tahun_sampai, bunga), ...]` alih-alih dua bunga. Cicilan dihitung ulang tiap
kali masuk jenjang baru, dari sisa pokok dan sisa tenor.

**Cek:** dengan daftar satu elemen `[(20, 11.0)]`, hasilnya identik dengan `jadwal_kpr(..., tahun_tetap=0,
bunga_mengambang=11)` yang lama. Pertahankan fungsi lama sebagai pembungkus supaya `app.py` dan tes
tidak perlu diubah.

---

### Latihan 6 — Biaya beli yang sebenarnya ⭐⭐⭐

`banding_beli_sewa` belum menghitung: BPHTB 5% dari (harga − NPOPTKP), biaya notaris dan provisi
(sekitar 1-2% harga), perawatan sekitar 1% nilai rumah per tahun, dan biaya jual 2-3% kalau rumah
dijual di akhir horizon. Tambahkan semuanya sebagai parameter dengan default masuk akal, dan masukkan
ke `kpr_kumulatif` (biaya awal dan perawatan) serta `ekuitas` (biaya jual).

Lalu tambahkan yang paling sering dilupakan: **opportunity cost DP**. Kalau DP tidak dipakai beli rumah
dan diinvestasikan di 5% per tahun, berapa nilainya di tahun ke-10? Kurangkan dari keunggulan membeli.

**Cek:** titik impas di Jakarta dengan asumsi awal bergeser lebih jauh, atau hilang. Tulis di komentar
atas fungsi: menurutmu, parameter mana yang paling mengubah hasil?

---

### Latihan 7 — Peta bukan tabel ⭐⭐⭐

Tambahkan kolom `lat`, `lon` di `kota.csv`, lalu buat halaman kelima "Map" dengan
`plotly.graph_objects.Scattergeo` (atau `Scattermap`) di mana ukuran titik = rasio harga ÷ gaji dan
warna = kode mutu. Gunakan `st.segmented_control` yang sudah ada; jangan `st.tabs`.

**Cek:** hover di tiap titik menampilkan kota, UMK, harga rumah, dan rasio dengan format `rp()`.

---

### Latihan 8 — Versi 2027 ⭐⭐⭐

UMK 2027 akan diumumkan Desember 2026. Tambahkan kolom `umk_2027` tanpa menghapus `umk_2026`, lalu
buat pemilih tahun di sidebar. Ubah `muat_kota` agar kolom `gaji` diisi dari tahun yang dipilih.
Sekalian: tambahkan kolom `rumah_seken_2027` kalau Flash Report-nya sudah ada, dan grafik kecil
"berapa persen gaji naik vs berapa persen harga naik" per kota.

**Cek:** semua tes lama lulus dengan tahun 2026 sebagai default; tes baru memastikan memilih 2027
mengubah `gaji` di semua baris. Pertanyaan penutup: dalam setahun, apakah jarak antara gaji dan atap
melebar atau menyempit? Itu pertanyaan yang seharusnya dijawab dashboard ini tiap tahun.
