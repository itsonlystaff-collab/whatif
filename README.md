# WHAT IF — Jakarta Semua Naik Transportasi Umum

Blender procedural 3D project dengan arah visual **stylized 3D realistic**: geometri kota yang bersih dan sedikit stylized, material PBR, kaca reflektif, detail kendaraan, gedung bertingkat dengan jendela individual, lampu jalan, pepohonan, manusia, MRT, TransJakarta, suasana senja/malam, kamera sinematik, dan subtitle.

## Spesifikasi
- Video vertikal 1080 × 1920 (9:16)
- 30 FPS, durasi sekitar 75,9 detik
- Blender 4.x / EEVEE Next (script fallback ke EEVEE bila tersedia)
- Voice-over MP3 asli sudah disertakan
- Output: `output/jakarta_whatif.mp4`

## Render melalui GitHub Actions
1. Ekstrak ZIP ini.
2. Upload seluruh isi folder ke repository GitHub.
3. Buka tab **Actions**.
4. Pilih workflow **Render Jakarta What If** lalu klik **Run workflow**.
5. Setelah workflow selesai, buka bagian **Artifacts** dan unduh `jakarta-whatif-video`.

## Render lokal
Dari folder project, jalankan:

```bash
blender -b -t 4 -P main.py
```

File `.blend` disimpan sebagai `jakarta_whatif.blend` dan MP4 di folder `output/`.

## Catatan visual
Style sengaja diarahkan ke kota 3D stylized realistis, bukan low-poly sederhana: ada detail fasad, jendela, roda dan kaca kendaraan, struktur rel layang, gantry kamera lalu lintas, street lighting, bayangan lembut, dan glow tipis. Hasil akhir tetap bergantung pada versi Blender dan performa mesin GitHub runner; lakukan test render frame pendek terlebih dahulu bila ingin mengubah kualitas atau durasi.
