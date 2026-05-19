import numpy as np
from PIL import Image
import os
import matplotlib.pyplot as plt
from scipy.fftpack import dct, idct

def dct2(blok):
    return dct(dct(blok.T, norm='ortho').T, norm='ortho')

def idct2(blok):
    return idct(idct(blok.T, norm='ortho').T, norm='ortho')

def proses_watermarking_lengkap(path_foto_wajah):
    if not os.path.exists(path_foto_wajah):
        print(f"Error: File tidak ditemukan di {path_foto_wajah}")
        return

    img_asli = Image.open(path_foto_wajah).convert('RGB')
    lebar, tinggi = img_asli.size
    lebar_baru, tinggi_baru = (lebar // 8) * 8, (tinggi // 8) * 8
    img_asli = img_asli.crop((0, 0, lebar_baru, tinggi_baru))
    
    img_ycbcr = img_asli.convert('YCbCr')
    channel_y, channel_cb, channel_cr = img_ycbcr.split()
    img_array_y = np.array(channel_y, dtype=np.float32)

    np.random.seed(42)
    kapasitas_bit = (tinggi_baru // 8) * (lebar_baru // 8)
    watermark_acak = np.random.randint(0, 2, size=(tinggi_baru // 8, lebar_baru // 8), dtype=np.uint8)
    
    alpha = 25 
    kordinat_1, kordinat_2 = (4, 3), (5, 2)
    img_watermarked_y = np.zeros_like(img_array_y)

    print("[INFO] Memulai penyisipan watermark pada Channel Y (Metode DCT)...")
    for i in range(0, tinggi_baru, 8):
        for j in range(0, lebar_baru, 8):
            blok_dct = dct2(img_array_y[i:i+8, j:j+8])
            bit = watermark_acak[i//8, j//8]
            val1, val2 = blok_dct[kordinat_1], blok_dct[kordinat_2]
            
            if bit == 0 and (val1 - val2 < alpha):
                diff = alpha - (val1 - val2)
                blok_dct[kordinat_1] += diff / 2
                blok_dct[kordinat_2] -= diff / 2
            elif bit == 1 and (val2 - val1 < alpha):
                diff = alpha - (val2 - val1)
                blok_dct[kordinat_2] += diff / 2
                blok_dct[kordinat_1] -= diff / 2
            
            img_watermarked_y[i:i+8, j:j+8] = idct2(blok_dct)

    img_watermarked_y = np.clip(img_watermarked_y, 0, 255).astype(np.uint8)
    y_baru = Image.fromarray(img_watermarked_y, mode='L')
    img_final_rgb = Image.merge('YCbCr', (y_baru, channel_cb, channel_cr)).convert('RGB')

    print("\n[EVALUASI] Menguji ketahanan terhadap kompresi lossy JPEG:")
    qf_test_list = [100, 95, 90, 80, 50, 10]
    folder_simpan = os.path.dirname(path_foto_wajah)
    
    for qf in qf_test_list:
        nama_file_kompres = os.path.join(folder_simpan, f"wajah_warna_QF{qf}.jpg")
        img_final_rgb.save(nama_file_kompres, "JPEG", quality=qf)

        y_kompres = np.array(Image.open(nama_file_kompres).convert('YCbCr').split()[0], dtype=np.float32)
        watermark_diekstrak = np.zeros_like(watermark_acak)
        
        for i in range(0, tinggi_baru, 8):
            for j in range(0, lebar_baru, 8):
                blok_dct = dct2(y_kompres[i:i+8, j:j+8])
                watermark_diekstrak[i//8, j//8] = 0 if blok_dct[kordinat_1] > blok_dct[kordinat_2] else 1
                    
        ber = np.sum(watermark_acak != watermark_diekstrak) / kapasitas_bit
        status = "Rusak Total" if ber > 0.45 else "Terekstrak"
        print(f" -> QF: {qf:3d} | BER: {ber:.4f} | Status: {status}")


    print("\n[INFO] Menyiapkan gambar visualisasi step-by-step...")
    selisih_array = np.abs(np.array(img_asli, dtype=int) - np.array(img_final_rgb, dtype=int))
    jejak_watermark = np.clip(selisih_array * 15, 0, 255).astype(np.uint8)

    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    ax = axes.ravel()
    
    ax[0].imshow(img_asli); ax[0].set_title("1. Gambar Asli (RGB)")
    ax[1].imshow(channel_y, cmap='gray'); ax[1].set_title("2. Ekstraksi Channel Y (Luminance)")
    ax[2].imshow(watermark_acak, cmap='gray', interpolation='nearest'); ax[2].set_title("3. Pola Watermark Biner")
    ax[3].imshow(y_baru, cmap='gray'); ax[3].set_title("4. Channel Y Setelah Disisipi (DCT)")
    ax[4].imshow(img_final_rgb); ax[4].set_title("5. Hasil Akhir Watermarked (RGB)")
    ax[5].imshow(jejak_watermark); ax[5].set_title("6. Jejak Noise Watermark (Selisih Diperkuat)")

    for a in ax: a.axis('off')
    plt.tight_layout()
    
    file_visualisasi = os.path.join(folder_simpan, "visualisasi_watermark.jpg")
    plt.savefig(file_visualisasi, dpi=300, bbox_inches='tight')
    print(f"[SUKSES] Visualisasi disimpan di: {file_visualisasi}")
    plt.show()

if __name__ == "__main__":
    folder_script = os.path.dirname(os.path.abspath(__file__))
    folder_utama = os.path.dirname(folder_script)
    foto_saya = os.path.join(folder_utama, "test_vectors", "wajahsendiri.jpg")
    
    proses_watermarking_lengkap(foto_saya)