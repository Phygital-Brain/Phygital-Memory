---
type: skill
status: active
tags: [brain-keeper, check-up]
---

Pemeriksaan dari Penjaga Otak: melihat seluruh isi otak, kalau {Name} minta. Tidak ada yang berubah sampai {Name} bilang ya. (Perapian harian ada di `harian.md`.)

Pemicu: "cek otakku", "rapikan otakku", "pemeriksaan otak", "check up my brain", "tidy my brain", "brain check-up", atau kalimat serupa dalam {Language}.

## 1. Lihat (jangan ubah apa pun dulu)

Telusuri seluruh folder dan daftar masalahnya dalam kelompok berikut:

- **Tautan rusak**: `[[tautan]]` yang mengarah ke catatan yang tidak ada. Jangan pernah memperbaikinya dengan membuat catatan kosong: catatan aslinya mungkin masih disinkronkan (aturan utama 28).
- **Catatan yatim**: catatan yang tidak ditautkan dari catatan lain mana pun.
- **Catatan kosong atau hampir kosong**, dan isian sementara yang tertinggal (`[name]`, `TBD`).
- **Salah tempat**: file di akar folder (kecuali `CLAUDE.md`, `.claudeignore`, `.backups/`, dan file aturan satu baris milik agen lain, seperti `AGENTS.md`), catatan yang tidak sesuai dengan tabel rute foldernya.
- **Tabel rute yang usang**: sebuah `CLAUDE.md` mencantumkan file atau folder yang tidak ada, atau tidak mencantumkan yang ada (baris bertanda "dibuat saat pertama kali dipakai" tidak masalah).
- **Blok info**: tidak ada atau tidak lengkap, dibandingkan dengan `CLAUDE.md` foldernya. Tidak ada `status:`, kurang dari 2 `tags:`, catatan proyek tanpa `project:`, tag harian di luar daftar tetap.
- **Proyek terbengkalai**: tidak ada pembaruan selama 60 hari atau lebih. Sarankan pembaruan status, `paused`, atau diarsipkan.
- **Tujuan yang terlupakan**: tujuan di `Tentang/tujuan.md` yang tidak punya proyek aktif.
- **Keputusan yang perlu ditinjau**: `updated` lebih dari 30 hari yang lalu dan statusnya bukan `closed`.
- **Relasi lama**: `status: active` tapi `last-contact` lebih dari 12 bulan yang lalu. Sarankan `dormant`.
- **Tugas lama**: tugas yang belum selesai di `Harian/tugas.md` yang umurnya lebih dari 30 hari.
- **Duplikat**: fakta yang sama di lebih dari satu catatan, atau dua catatan untuk orang atau perusahaan yang sama.
- **Kebenaran yang usang**: halaman Tentang atau Relasi yang keadaan terkininya terkubur di bawah pembaruan lama (aturan utama 17).
- **Aturan yang bertabrakan**: aturan di `CLAUDE.md` utama yang saling bertentangan.
- **Privasi**: kata sandi, kunci, atau nomor pribadi yang ada di catatan biasa (aturan utama 25 dan 26). Laporkan catatannya, jangan pernah nilainya.
- **Tulisan**: em dash dan pola Cek Tulisan di dalam catatan.
- **Versi baru**: bandingkan versi otak ini (baris pertama `CLAUDE.md` utama) dengan versi Phygital Brain terbaru. Kalau kamu bisa membuka web, versi terbaru adalah rilis terakhir di https://github.com/Phygital-Brain/phygital-brain/releases/latest. Kalau tidak bisa, pakai versi Phygital Brain yang terpasang di agenmu, kalau terlihat. Kalau tidak bisa dipastikan, lewati bagian ini.

## 2. Laporan

Daftar singkat dengan kata-kata sederhana, dikelompokkan seperti di atas. Untuk setiap masalah: catatannya, apa yang salah, dan perbaikan yang kamu sarankan. Taruh perbaikan yang sederhana dan aman di paling atas (em dash, tag yang kurang, baris tabel rute).

Kalau ada versi yang lebih baru, mulai laporan dengan satu baris. Kalau agenmu sudah punya versi itu: "Ada versi baru Phygital Brain. Bilang 'perbarui otak keduaku' ('Upgrade my second brain') untuk melihat apa yang baru." Kalau belum: "Ada versi baru Phygital Brain. Perbarui dulu di agenmu, lalu bilang 'perbarui otak keduaku'."

## 3. Perbaiki hanya yang disetujui

Sebelum perbaikan pertama, cadangkan setiap file yang akan diubah (Cadangan dan Pembatalan di `CLAUDE.md` utama).

Tanya (pakai pilihan yang bisa diklik kalau bisa): **Perbaiki semua yang aman**, **Satu per satu**, **Laporannya saja**.

- Jangan pernah menghapus atau memindahkan tanpa cek tautan dan jawaban ya yang jelas (aturan utama 21).
- Kalau ragu, arsipkan saja, jangan dihapus.
- Tulis satu baris di catatan `Harian/` hari ini: apa yang dicek dan diperbaiki.
