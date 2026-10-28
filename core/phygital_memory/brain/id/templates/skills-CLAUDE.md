<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the Morning Brief row if BRIEF = off.
-->

Catatan dan preferensi untuk skill yang dipakai agen, ditambah Penjaga Otak.

## Susunan

```
Skill/{skill-name}/
  {skill-name}.md atau SKILL.md   apa yang dilakukan skill ini
  catatan.md                      gaya dan preferensi {Name} untuk skill ini
  references/                     contoh dan bahan yang lebih panjang
```

## Terpasang

| Skill | Folder | Fungsinya |
|---|---|---|
| Penjaga Otak | `penjaga-otak/` | Merapikan setiap hari dengan sendirinya, dan pemeriksaan kalau {Name} minta |
| Ringkasan Pagi | `ringkasan-pagi/` | Rencana singkat untuk hari ini, kalau diminta atau setiap hari kerja |
| Impor | `impor/` | Memasukkan catatan dari aplikasi lain, dengan rencana yang disetujui {Name} dulu |
| Persiapan Rapat | `persiapan-rapat/` | Ringkasan singkat sebelum telepon, dari catatan di otak |
| Alat Berpikir | `alat-berpikir/` | Menguji ide, menemukan pola, mencari catatan yang saling bertentangan |
| Aplikasi Terhubung | `aplikasi-terhubung/` | Aplikasi yang dibaca otak, dan aturannya |
| No AI Slop | `no-ai-slop/` | Cek Tulisan: menyunting tulisan supaya terdengar manusiawi, atau menandai pola khas AI (oleh Peter Yang, Lisensi MIT, tidak pernah diedit) |

## Aturan

- Satu folder per skill, dinamai dengan huruf kecil dan tanda hubung (kebab-case).
- Kalau ada skill baru, tambahkan satu baris ke tabel di atas.
- Untuk menambahkan skill atau menghubungkan aplikasi, cek dulu saran dari Phygital Brain: `suggested-skills/README.md` dan `suggested-apps/README.md` lewat konektor Phygital Brain, atau online di https://github.com/Phygital-Brain/phygital-brain/tree/main/skills. Kalau ada di sana, ikuti halamannya. Kalau {Name} bertanya "apa saja yang bisa kutambahkan ke otakku?", "what can I add to my brain?", tunjukkan kedua daftar itu, yang cocok dengan pekerjaan {Name} lebih dulu, dan jangan tampilkan aplikasi yang sudah terhubung atau skill yang sudah terpasang.
- `SKILL.md` yang berasal dari orang lain tidak pernah diedit. Untuk menyesuaikan sebuah skill, tambahkan `catatan.md` di foldernya.
- `penjaga-otak/harian.md` dibaca oleh tugas terjadwal. Ubah file ini hanya untuk mengubah apa yang dikerjakan rutinitas harian, dan biarkan tetap polos: tanpa tautan, tanpa callout.
