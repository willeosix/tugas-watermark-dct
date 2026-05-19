import numpy as np
from PIL import Image
import os
import matplotlib.pyplot as plt
from scipy.fftpack import dct, idct

# --- Fungsi Bantuan ---
def dct2(blok):
    return dct(dct(blok.T, norm='ortho').T, norm='ortho')

def idct2(blok):
    return idct(idct(blok.T, norm='ortho').T, norm='ortho')

def proses_watermarking_lengkap(path_foto_wajah):
    if not os.path.exists(path_foto_wajah):
        print(f"Error: File tidak ditemukan di {path_foto_wajah}")
        return

    # ==========================================
    # 1. PERSIAPAN
    # ==========================================
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

    sampel_blok_asli = None
    sampel_blok_dct = None
    sampel_blok_dct_mod = None
    sampel_blok_idct = None

    target_i = (tinggi_baru // 2) // 8 * 8
    target_j = (lebar_baru // 2) // 8 * 8

    print("[INFO] Memulai penyisipan watermark pada Channel Y (Metode DCT)...")
    for i in range(0, tinggi_baru, 8):
        for j in range(0, lebar_baru, 8):
            blok_asli = img_array_y[i:i+8, j:j+8]
            blok_dct = dct2(blok_asli)
            
            if i == target_i and j == target_j:
                sampel_blok_asli = blok_asli.copy()
                sampel_blok_dct = blok_dct.copy()

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
            
            blok_rekonstruksi = idct2(blok_dct)
            img_watermarked_y[i:i+8, j:j+8] = blok_rekonstruksi
            
            if i == target_i and j == target_j:
                sampel_blok_dct_mod = blok_dct.copy()
                sampel_blok_idct = blok_rekonstruksi.copy()

    img_watermarked_y = np.clip(img_watermarked_y, 0, 255).astype(np.uint8)
    y_baru = Image.fromarray(img_watermarked_y, mode='L')
    img_final_rgb = Image.merge('YCbCr', (y_baru, channel_cb, channel_cr)).convert('RGB')

    # ==========================================
    # 2. EVALUASI KETAHANAN JPEG & PENGUMPULAN DATA
    # ==========================================
    print("\n[EVALUASI] Menguji ketahanan terhadap kompresi lossy JPEG:")
    qf_test_list = [100, 95, 90, 80, 50, 30, 10] # Ditambah QF 30 agar grafik lebih mulus
    folder_simpan = os.path.dirname(path_foto_wajah)
    
    koleksi_ekstraksi = {}
    ber_list = [] # List untuk menyimpan data untuk grafik

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
        ber_list.append(ber) # Simpan BER ke list
        
        status = "Rusak Total" if ber > 0.45 else "Terekstrak"
        print(f" -> QF: {qf:3d} | BER: {ber:.4f} | Status: {status}")
        
        if qf in [100, 80, 50, 10]:
            koleksi_ekstraksi[qf] = watermark_diekstrak.copy()

    # ==========================================
    # 3. PEMBUATAN VISUALISASI GAMBAR & GRAFIK
    # ==========================================
    print("\n[INFO] Menyiapkan gambar-gambar visualisasi dan grafik...")

    # --- GAMBAR 1: PROSES UTAMA (6 PANEL) ---
    selisih_array = np.abs(np.array(img_asli, dtype=int) - np.array(img_final_rgb, dtype=int))
    jejak_watermark = np.clip(selisih_array * 15, 0, 255).astype(np.uint8)

    fig1, ax1 = plt.subplots(2, 3, figsize=(16, 10))
    ax1 = ax1.ravel()
    ax1[0].imshow(img_asli); ax1[0].set_title("1. Gambar Asli (RGB)")
    ax1[1].imshow(channel_y, cmap='gray'); ax1[1].set_title("2. Ekstraksi Channel Y (Luminance)")
    ax1[2].imshow(watermark_acak, cmap='gray', interpolation='nearest'); ax1[2].set_title("3. Pola Watermark Biner")
    ax1[3].imshow(y_baru, cmap='gray'); ax1[3].set_title("4. Channel Y Setelah Disisipi (DCT)")
    ax1[4].imshow(img_final_rgb); ax1[4].set_title("5. Hasil Akhir Watermarked (RGB)")
    ax1[5].imshow(jejak_watermark); ax1[5].set_title("6. Jejak Noise Watermark (Selisih Diperkuat)")
    for a in ax1: a.axis('off')
    fig1.tight_layout()
    fig1.savefig(os.path.join(folder_simpan, "visualisasi_1_utama.jpg"), dpi=300)

    # --- GAMBAR 2: DIBALIK LAYAR BLOK 8x8 DCT ---
    fig2, ax2 = plt.subplots(1, 4, figsize=(18, 5))
    fig2.suptitle("Analisis Mikroskopis: Transformasi pada Satu Blok 8x8 Piksel", fontsize=16)
    c1 = ax2[0].imshow(sampel_blok_asli, cmap='gray')
    ax2[0].set_title("1. Spatial Asli")
    fig2.colorbar(c1, ax=ax2[0], fraction=0.046, pad=0.04)
    c2 = ax2[1].imshow(np.abs(sampel_blok_dct), cmap='viridis', vmax=100)
    ax2[1].set_title("2. Koefisien DCT Asli")
    fig2.colorbar(c2, ax=ax2[1], fraction=0.046, pad=0.04)
    c3 = ax2[2].imshow(np.abs(sampel_blok_dct_mod), cmap='viridis', vmax=100)
    ax2[2].set_title("3. DCT + Watermark Disisipkan")
    fig2.colorbar(c3, ax=ax2[2], fraction=0.046, pad=0.04)
    c4 = ax2[3].imshow(sampel_blok_idct, cmap='gray')
    ax2[3].set_title("4. Spatial Rekonstruksi (IDCT)")
    fig2.colorbar(c4, ax=ax2[3], fraction=0.046, pad=0.04)
    fig2.tight_layout()
    fig2.savefig(os.path.join(folder_simpan, "visualisasi_2_blok_dct.jpg"), dpi=300)

    # --- GAMBAR 3: DAMPAK KOMPRESI TERHADAP WATERMARK ---
    fig3, ax3 = plt.subplots(1, 5, figsize=(20, 4))
    fig3.suptitle("Evaluasi Visual: Kerusakan Watermark akibat Kompresi JPEG", fontsize=16)
    ax3[0].imshow(watermark_acak, cmap='gray', interpolation='nearest')
    ax3[0].set_title("Watermark Asli")
    ax3[0].axis('off')
    for idx, qf in enumerate([100, 80, 50, 10]):
        ax3[idx+1].imshow(koleksi_ekstraksi[qf], cmap='gray', interpolation='nearest')
        ax3[idx+1].set_title(f"Diekstrak pada QF {qf}")
        ax3[idx+1].axis('off')
    fig3.tight_layout()
    fig3.savefig(os.path.join(folder_simpan, "visualisasi_3_ekstraksi_qf.jpg"), dpi=300)

    # --- GAMBAR 4: GRAFIK GARIS (BER vs QF) ---
    fig4, ax4 = plt.subplots(figsize=(10, 6))
    # Membalik urutan data agar sumbu X (QF) berjalan dari 0 ke 100 secara logis
    ax4.plot(qf_test_list[::-1], ber_list[::-1], marker='o', linestyle='-', color='#1f77b4', linewidth=2.5, markersize=8)
    
    ax4.set_title('Ketahanan Watermark: Bit Error Rate (BER) vs JPEG Quality Factor', fontsize=15, fontweight='bold', pad=15)
    ax4.set_xlabel('JPEG Quality Factor (QF)', fontsize=12)
    ax4.set_ylabel('Bit Error Rate (BER)', fontsize=12)
    
    # Batas sumbu
    ax4.set_xlim(-5, 105)
    ax4.set_ylim(-0.02, 0.55)
    
    # Garis panduan batas rusak total (BER 0.45 - 0.50)
    ax4.axhline(y=0.45, color='red', linestyle='--', linewidth=1.5, label='Batas Toleransi Kerusakan (BER 0.45)')
    ax4.axhline(y=0.0, color='green', linestyle='-', linewidth=1, alpha=0.5)
    
    ax4.grid(True, linestyle=':', alpha=0.7)
    ax4.legend(loc='lower right', fontsize=11)
    
    # Menambahkan anomali teks
    ax4.text(80, 0.1, "Watermark\nMasih Bertahan", color='green', fontsize=10, ha='center')
    ax4.text(30, 0.40, "Watermark\nHancur Total", color='red', fontsize=10, ha='center')
    
    fig4.tight_layout()
    fig4.savefig(os.path.join(folder_simpan, "visualisasi_4_grafik_ber.jpg"), dpi=300)

    print("[SUKSES] Seluruh gambar visualisasi & grafik berhasil dibuat!")
    print("Silakan cek folder Anda untuk 4 file .jpg baru.")
    
    plt.show()

if __name__ == "__main__":
    folder_script = os.path.dirname(os.path.abspath(__file__))
    folder_utama = os.path.dirname(folder_script)
    foto_saya = os.path.join(folder_utama, "test_vectors", "wajahsendiri.jpg")
    
    proses_watermarking_lengkap(foto_saya)