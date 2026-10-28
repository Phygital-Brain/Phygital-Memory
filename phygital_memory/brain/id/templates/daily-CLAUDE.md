<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the `clients` tag line if BUSINESS = off.
-->

Jurnal harian {Name}. Satu file per hari: `YYYY-MM-DD.md`. Tugas yang belum selesai ada di `tugas.md`.

## Blok info (frontmatter)

Setiap catatan harian diawali dengan blok ini. Tanpa pengecualian.

```yaml
---
type: daily
date: 2026-10-13
day: Tuesday
week: W42
month: October
status: active
tags: [daily, meeting]
---
```

- `type`: selalu `daily`.
- `date`: tanggal catatan, `YYYY-MM-DD`.
- `day`: nama hari, dalam bahasa Inggris (Monday, Tuesday...).
- `week`: nomor minggu ISO, `WNN`.
- `month`: nama bulan, dalam bahasa Inggris (January, February...).
- `status`: `active` selama harinya masih berjalan, `completed` setelah umurnya 2 hari atau lebih.
- `tags`: selalu `daily`, ditambah tag dari daftar tetap ini sesuai yang terjadi hari itu. Jangan pernah mengarang tag lain.
  - `problem`: ada yang rusak atau tidak berjalan lancar
  - `clients`: pekerjaan untuk klien atau kontak dengan klien
  - `meeting`: telepon atau rapat
  - `money`: invoice, pembayaran, pajak, investasi
  - `research`: riset yang dilakukan atau temuannya
  - `decision`: {Name} memutuskan sesuatu
  - `travel`: {Name} sedang bepergian
  - `personal`: kesehatan, kehidupan pribadi, apa pun di luar pekerjaan

## Aturan

- Tanggal mengikuti aturan utama 30 (zona waktu komputer dulu, lalu {Time zone}).
- Siapa pun yang membuat catatan (agenmu atau tugas terjadwal) menulis blok info lebih dulu. Kalau ada catatan yang belum punya blok info, tambahkan di bagian paling atas saat catatan itu diedit lagi.
- Tidak ada judul `# YYYY-MM-DD`. Nama file sudah jadi judulnya.
- Catatan harian menyimpan keadaan hari itu: satu dokumen rapi per hari, bagian-bagiannya diperbarui di tempat, bukan tumpukan catatan yang berulang.
- Log sesi: judul tebal ditambah 1 atau 2 kalimat, orang dan proyek sebagai `[[wikilink]]`, detailnya masuk ke catatan yang ditautkan.
- Catatan hari ini hanya berisi kegiatan hari ini. Tugas yang belum selesai dari hari-hari sebelumnya masuk ke `tugas.md`. Jangan pernah menyalinnya ke hari berikutnya.
- Saat membuat catatan hari ini, lihat catatan dari 2, 3, dan 4 hari yang lalu. Yang masih `status: active` diubah jadi `completed`, dan diberi tag dari daftar tetap sesuai apa yang jelas terjadi hari itu. Jangan melihat lebih jauh ke belakang.

## tasks.md

Tugas yang belum selesai dan tidak termasuk proyek mana pun. Tugas proyek masuk ke README proyek itu ("Status dan langkah berikutnya"). Dibuat saat pertama kali dipakai:

```markdown
---
type: tasks
status: active
tags: [tasks, daily]
---

## Belum selesai

- [ ] 2026-10-13: Kirim invoice ke [[Ana]]

## Selesai

- [x] 2026-10-12: Buat janji ke dokter gigi (selesai 2026-10-13)
```

- Tugas terbaru di paling atas, dengan tanggal saat ditambahkan.
- Kalau tugas sudah selesai, centang, tambahkan tanggal selesainya, lalu pindahkan ke `## Selesai`.
- Tugas selesai yang umurnya lebih dari 30 hari boleh dihapus (tanya dulu, aturan utama 9).
