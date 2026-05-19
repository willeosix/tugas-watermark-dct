# LAPORAN AKHIR TUGAS: IMPLEMENTASI DAN EVALUASI INVISIBLE WATERMARKING MENGGUNAKAN DISCRETE COSINE TRANSFORM (DCT)

* **Nama:** Christian Wilfredo Pakpahan
* **NIM:** 18224038


## 1. Pendahuluan & Latar Belakang
Digital Watermarking merupakan salah satu teknik steganografi yang digunakan untuk melindungi hak cipta kekayaan intelektual digital dengan cara menyisipkan informasi rahasia (*watermark*) ke dalam media penampung (*cover image*). Tugas ini mengimplementasikan metode *Invisible Robust Watermarking* menggunakan algoritma **Discrete Cosine Transform (DCT)** pada ruang warna **YCbCr** secara *from scratch* (tanpa menggunakan library watermark eksternal). 

Berbeda dengan teknik *Least Significant Bit* (LSB) pada domain spasial yang sangat rapuh (*fragile*) terhadap manipulasi gambar, teknik berbasis domain frekuensi seperti DCT menawarkan ketangguhan (*robustness*) yang tinggi terhadap serangan pemrosesan sinyal digital standar, khususnya kompresi *lossy* JPEG.


## 2. Metodologi dan Algoritma
Sistem ini memproses citra berwarna RGB melalui tahapan-tahapan matematis terstruktur sebagai berikut:
1.  **Transformasi Ruang Warna:** Citra RGB diubah ke ruang warna YCbCr untuk memisahkan komponen *Luminance* / kecerahan (Y) dari komponen *Chrominance* / warna (Cb, Cr). Langkah ini krusial karena sistem visual manusia jauh lebih sensitif terhadap perubahan luminansi dibandingkan perubahan krominansi. Kuantisasi kompresi JPEG juga mengeksploitasi hal ini, sehingga menyisipkan data pada channel Y menjamin ketahanan yang optimal.
2.  **Segmentasi Blok 8x8:** Sesuai dengan standar JPEG dasar, channel Y dipecah menjadi matriks blok-blok independen berukuran $8 \times 8$ piksel.
3.  **Aplikasi DCT 2D:** Setiap blok spasial diubah menjadi representasi frekuensi melalui persamaan Discrete Cosine Transform. Koefisien kiri-atas merepresentasikan frekuensi rendah (DC komponen), sementara koefisien kanan-bawah merepresentasikan frekuensi tinggi.
4.  **Penyisipan Bit pada Frekuensi Menengah:** Sepasang koordinat frekuensi menengah pilihan—dalam proyek ini ditentukan pada posisi koefisien $(4,3)$ dan $(5,2)$—dimodifikasi secara adaptif berdasarkan nilai bit watermark ($0$ atau $1$) dengan parameter kekuatan $\alpha = 25$.
5.  **Inverse DCT (IDCT) & Rekonstruksi:** Blok frekuensi dikembalikan ke domain spasial via IDCT, digabungkan kembali dengan channel Cb-Cr yang tidak disentuh, lalu dikonversi balik menjadi citra RGB berwarna.


## 3. Hasil Visualisasi Pengujian
Eksperimen menghasilkan empat buah berkas visualisasi utama yang merekam detail arsitektur algoritma dari tingkat makro hingga analisis kuantitatif mikroskopis. Berikut adalah penjelasan mendalam mengenai masing-masing visualisasi:





<img width="4800" height="3000" alt="visualisasi_1_utama" src="https://github.com/user-attachments/assets/f40ed1b8-0d04-406d-b990-45df67b677fb" />

### Gambar 1: Alur Utama Proses Transformation (`visualisasi_1_utama.jpg`)
Gambar ini menyajikan 6 panel linier yang mendokumentasikan siklus hidup penyisipan watermark dari awal hingga akhir:
1.  **Panel 1. Gambar Asli (RGB):** Citra masukan bersumber dari berkas `wajahsendiri.jpg` dengan representasi warna penuh (*Full Color*).
2.  **Panel 2. Ekstraksi Channel Y (Luminance):** Representasi visual channel kecerahan setelah konversi YCbCr dilakukan. Karakteristik visualnya tampak seperti gambar grayscale standar, yang memuat seluruh detail struktural dan kontras utama dari foto wajah.
3.  **Panel 3. Pola Watermark Biner:** Visualisasi matriks data rahasia biner acak berukuran $(Tinggi/8) \times (Lebar/8)$ bit yang dihasilkan melalui generator berbasis *seed* acak tetap (`seed=42`). Pola kotak-kotak hitam (bit 0) dan putih (bit 1) merepresentasikan muatan (*payload*) rahasia yang akan disembunyikan.
4.  **Panel 4. Channel Y Setelah Disisipi (DCT):** Channel Luminance setelah seluruh blok $8 \times 8$ mengalami modifikasi koefisien frekuensi menengah dan direkonstruksi kembali lewat IDCT. Secara visual, panel ini tampak **identik** dengan Panel 2. Hal ini membuktikan keterpenuhan aspek *Imperceptibility* (tidak terdeteksi oleh mata manusia).
5.  **Panel 5. Hasil Akhir Watermarked (RGB):** Hasil penggabungan kembali channel Y yang termodifikasi dengan channel Cb dan Cr asli. Foto wajah tetap mempertahankan ketajaman warna, gradasi bayangan, dan kualitas perseptual asli tanpa adanya artefak visual yang mengganggu.
6.  **Panel 6. Jejak Noise Watermark (Selisih Diperkuat):** Panel pembuktian objek. Diperoleh dari operasi matematika: $|Citra\,Asli - Citra\,Watermarked| \times 15$. Perkalian dengan faktor magnitudo 15 dilakukan agar selisih nilai piksel yang sangat kecil (halus) dapat diangkat ke rentang visual manusia. Hasilnya memperlihatkan pola grid berstruktur kotak-kotak kecil ukuran $8 \times 8$ piksel secara homogen di seluruh area citra, yang menegaskan keberadaan muatan data DCT tersembunyi.


<img width="5400" height="1500" alt="visualisasi_2_blok_dct" src="https://github.com/user-attachments/assets/ca15819e-709b-4e23-a005-123ae272c2dc" />

### Gambar 2: Analisis Mikroskopis Blok 8x8 DCT (`visualisasi_2_blok_dct.jpg`)
Visualisasi ini membedah fenomena matematika yang terjadi di dalam satu blok tunggal berukuran $8 \times 8$ piksel tepat di area tengah citra:
1.  **Sub-panel 1. Spatial Asli:** Menampilkan nilai intensitas spasial asli dari blok $8 \times 8$ piksel sebelum proses transformasi. Distribusi warna/gradasi grayscale diwakili oleh bar pemetaan warna di sebelah kanan.
2.  **Sub-panel 2. Koefisien DCT Asli:** Hasil transformasi DCT terhadap blok spasial asli. Terlihat lonjakan nilai yang sangat masif terpusat pada sudut kiri atas (frekuensi rendah/DC koefisien), sementara nilai koefisien melandai menuju angka mendekati nol pada area kanan bawah (frekuensi tinggi). Ini membuktikan bahwa sebagian besar energi visual citra wajah terpusat pada frekuensi rendah.
3.  **Sub-panel 3. DCT + Watermark Disisipkan:** Menunjukkan nilai koefisien setelah bit watermark disisipkan melalui modifikasi selisih nilai koefisien pada koordinat frekuensi menengah $(4,3)$ dan $(5,2)$. Perubahan nilai diatur sedemikian rupa agar selisih absolut antar kedua koordinat tersebut memenuhi ambang batas $\alpha = 25$, menciptakan relasi keteraturan biner yang kokoh tanpa mengganggu kestabilan nilai energi DC utama di pojok kiri atas.
4.  **Sub-panel 4. Spatial Rekonstruksi (IDCT):** Blok setelah dikembangkan dari domain frekuensi modifikasi menjadi domain spasial. Blok piksel ini tampak sama persis dengan blok spasial asli di Sub-panel 1, membuktikan bahwa pergeseran nilai pada frekuensi menengah DCT tidak mengakibatkan distorsi lokal atau cacat piksel (*noise* pecah) yang kentara pada domain spasial citra.

<img width="6000" height="1200" alt="visualisasi_3_ekstraksi_qf" src="https://github.com/user-attachments/assets/394e8fb6-4786-4b81-abf8-4e25cafcf4ca" />

### Gambar 3: Evaluasi Visual Kerusakan Watermark akibat Kompresi JPEG (`visualisasi_3_ekstraksi_qf.jpg`)
Gambar ini menunjukkan perbandingan hasil ekstraksi fisik matriks watermark biner pada berbagai tingkat keganasan serangan kompresi JPEG:
1.  **Watermark Asli:** Pola matriks biner referensi sebelum citra diserang.
2.  **Diekstrak pada QF 100:** Hasil rekonstruksi data biner menunjukkan kemiripan mutlak tanpa cacat bit (*Bit Error Rate* = 0.0000). Pola kotak hitam-putih terekstrak secara sempurna.
3.  **Diekstrak pada QF 80:** Citra biner berhasil terekstrak dengan tingkat keutuhan yang sangat tinggi. Kerusakan bit sangat minim (BER hanya 3.8%), di mana bentuk umum dari sebaran data biner masih sangat jelas dikenali oleh sistem ekstraktor.
4.  **Diekstrak pada QF 50 & QF 10:** Pola biner mengalami kerusakan total struktural. Matriks berubah menjadi sebaran titik acak (*noise* statis menyerupai layar televisi rusak) dengan nilai BER melonjak ke angka kritis ~50%. Ini secara visual membuktikan kegagalan total proses ekstraksi akibat hilangnya relasi selisih koefisien DCT karena terpotong oleh matriks kuantisasi agresif milik JPEG.

<img width="3000" height="1800" alt="visualisasi_4_grafik_ber" src="https://github.com/user-attachments/assets/938dc8fc-d118-4c29-a26e-1f58e2148e30" />

### Gambar 4: Grafik Kuantitatif BER vs JPEG Quality Factor (`visualisasi_4_grafik_ber.jpg`)
Grafik garis (Line Chart) ini memetakan metrik performa objektif dari algoritma watermarking yang dikembangkan:
* **Sumbu X (Horizontal):** Menunjukkan tingkat *JPEG Quality Factor* (QF) dari skala 100 (kualitas tertinggi/kompresi terendah) hingga 10 (kualitas terendah/kompresi terekstrem).
* **Sumbu Y (Vertikal):** Menunjukkan nilai rasio kesalahan bit atau *Bit Error Rate* (BER) dari rentang 0.0 (tanpa error) hingga 0.5 (error maksimal/acak).
* **Garis Analisis Biru (Kurva BER):** Memperlihatkan performa algoritma yang sangat stabil pada nilai BER = 0.0000 dari QF 100 hingga QF 90. Pada QF 80, kurva mengalami kenaikan landai yang sangat aman ke angka BER 0.0387. Namun, terjadi penurunan performa kritis (*cliff effect*) yang tajam di antara QF 80 dan QF 50, di mana garis biru melonjak menembus garis ambang batas merah.
* **Garis Batas Merah Putus-putus (Batas Toleransi Kerusakan):** Diletakkan pada koordinat nilai BER 0.45 sebagai indikator kegagalan sistem. Secara akademis, apabila nilai BER menyentuh rentang 0.45 - 0.50, maka informasi biner di dalamnya dianggap telah terhapus/rusak total karena nilainya identik dengan probabilitas tebakan acak (*koin seimbang*).
* **Anotasi Sektoral:** Grafik secara tegas membagi zona menjadi dua area: Zona Hijau di sisi kanan (QF 80-100) sebagai wilayah keberhasilan ekstraksi watermark, dan Zona Merah di sisi kiri (QF < 50) sebagai wilayah kehancuran data akibat kuantisasi ekstrem JPEG.

Berikut adalah hasil evaluasi ekstraksi watermark menggunakan metode DCT:

| Quality Factor (QF) JPEG | Bit Error Rate (BER) | Status Ekstraksi |
| --- | --- | --- |
| **100** | 0.0000 | Sempurna (100% terekstrak) |
| **95** | 0.0000 | Sempurna (100% terekstrak) |
| **90** | 0.0000 | Sempurna (100% terekstrak) |
| **80** | 0.0387 | Sangat Baik (Hanya 3,8% *error*) |
| **50** | 0.4976 | **Rusak Total (Hancur)** |
| **10** | 0.4980 | **Rusak Total (Hancur)** |


---

## 4. Kesimpulan 
Praktikum evaluasi kinerja *Digital Watermarking* ini berhasil membuktikan keunggulan analisis domain frekuensi melalui Discrete Cosine Transform (DCT). 
Berdasarkan data kuantitatif dan pembuktian visual yang diperoleh, metode DCT terbukti memiliki karakteristik **Robust (Tangguh)** terhadap kompresi lossy JPEG hingga tingkat kualitas menengah-tinggi (**QF 80**). Sifat ketahanan ini berbanding terbalik dengan metode domain spasial (LSB) yang sangat rapuh (*fragile*), di mana manipulasi QF ringan pada angka 95 saja sudah mampu melenyapkan watermark secara total. 

Watermark berbasis DCT baru benar-benar hancur dan tidak dapat diekstrak ketika citra mengalami serangan kompresi destruktif di bawah **QF 50**. Pada titik tersebut, pembulatan nilai koefisien pada matriks kuantisasi JPEG mulai memangkas dan meratakan nilai-nilai pada pita frekuensi menengah, sehingga menghapus selisih matematis koefisien $(4,3)$ dan $(5,2)$ yang menjadi wadah penyimpanan bit rahasia kita.
