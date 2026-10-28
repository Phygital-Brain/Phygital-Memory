---
type: skill
status: active
tags: [morning-brief, planning]
---

Rencana singkat untuk hari ini. Ada dua mode: **Ringkasan** (kalau diminta) dan **Jadwal** (setiap hari kerja).

## Ringkasan

Pemicu: "ringkasan pagi", "morning brief", atau kalimat serupa dalam {Language}.

1. Baca `Harian/tugas.md`, catatan harian terbaru, bagian "Status dan langkah berikutnya" dari setiap proyek dengan `status: active`, dan keputusan dengan status `open` atau `waiting`.
2. Kalau kalender terhubung, baca acara hari ini.
3. Balas paling banyak 6 baris pendek:
   - 3 hal terpenting hari ini, masing-masing dengan `[[tautan]]` ke catatannya.
   - Apa yang sedang {Name} tunggu dari orang lain.
   - Satu keputusan yang perlu diambil, kalau ada.
   - Acara hari ini, kalau kalender terhubung.
4. Jangan menulis file apa pun. Kalau {Name} menanggapi dengan info baru, simpan sesuai aturan utama 9.

## Jadwal

Pemicu: "atur ringkasan pagiku", "set up my morning brief", atau kalimat serupa dalam {Language}.

1. Tanya jamnya (pilihan yang bisa diklik: 7.00, 8.00, 9.00, 10.00), di hari kerja {Name}. Lewati pertanyaan ini kalau jamnya sudah diatur saat pengaturan.
2. Buat tugas terjadwal di aplikasi agen, yang berjalan di folder ini, dengan prompt ini:

   > Buka folder otak keduaku. Baca `Skill/ringkasan-pagi/ringkasan-pagi.md` dan berikan ringkasan pagiku.

3. Kalau tugas terjadwal tidak tersedia, minta {Name} bilang "ringkasan pagi" setiap kali mulai hari.
