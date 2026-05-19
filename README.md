# Robust Invisible Watermarking using DCT (Discrete Cosine Transform)

Repositori ini berisi implementasi *Digital Watermarking* (Steganografi) tingkat lanjut dari awal (*from scratch*) menggunakan Python. Proyek ini menyisipkan *watermark* berupa citra biner acak ke dalam foto digital (Cover Image) tanpa mengubah persepsi visual aslinya (*imperceptible*), serta tetap mempertahankan warna asli gambar.

## Metodologi
proyek ini menggunakan pendekatan **Domain Frekuensi**.
1. **Color Space Transformation:** Gambar RGB diubah menjadi **YCbCr**. Penyisipan hanya dilakukan pada *channel* Luminance (Y) karena mata manusia lebih peka terhadap perubahan cahaya dibandingkan warna.
2. **DCT 8x8 Blocks:** *Channel* Y dipecah menjadi blok 8x8 piksel dan diubah ke domain frekuensi menggunakan DCT.
3. **Mid-Frequency Embedding:** *Watermark* disisipkan dengan memodifikasi koefisien pada frekuensi menengah untuk mencapai keseimbangan antara *invisibility* (tidak kasat mata) dan *robustness* (ketahanan).

## 📂 Struktur Repositori
- `src/` : Berisi *source code* utama (`main_dct.py`) yang melakukan penyisipan, evaluasi kompresi JPEG, dan pembuatan visualisasi.
- `test_vectors/` : Berisi gambar asli untuk pengujian dan *output* visualisasinya.

## 🛠️ Instalasi & Penggunaan

Pastikan Anda memiliki Python 3.8+ terinstal. 

```bash
# 1. Clone repositori ini
git clone [https://github.com/username-anda/tugas-watermark-dct.git](https://github.com/username-anda/tugas-watermark-dct.git)
cd tugas-watermark-dct

# 2. Instal dependencies
pip install -r requirements.txt

# 3. Jalankan script utama
python src/main_watermarking.py