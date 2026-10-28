<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the `clients` tag line if BUSINESS = off.
-->

Jurnal harian {Name}. Satu fail setiap hari: `YYYY-MM-DD.md`. Tugasan yang belum selesai disimpan dalam `tugasan.md`.

## Blok info (frontmatter)

Setiap nota harian bermula dengan blok ini. Tiada pengecualian.

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

- `type`: sentiasa `daily`.
- `date`: tarikh nota, `YYYY-MM-DD`.
- `day`: hari dalam minggu, dalam bahasa Inggeris (Monday, Tuesday...).
- `week`: nombor minggu ISO, `WNN`.
- `month`: bulan, dalam bahasa Inggeris (January, February...).
- `status`: `active` selagi hari itu masih berjalan, `completed` apabila nota itu sudah berusia 2 hari atau lebih.
- `tags`: sentiasa `daily`, ditambah mana-mana tag daripada senarai tetap ini yang berlaku pada hari itu. Jangan sekali-kali reka tag lain.
  - `problem`: ada yang rosak atau tidak menjadi
  - `clients`: kerja klien atau berhubung dengan klien
  - `meeting`: panggilan atau mesyuarat
  - `money`: invois, bayaran, cukai, pelaburan
  - `research`: kajian yang dibuat atau hasil kajian
  - `decision`: {Name} membuat keputusan
  - `travel`: {Name} sedang dalam perjalanan
  - `personal`: kesihatan, kehidupan, apa-apa di luar kerja

## Peraturan

- Tarikh ikut peraturan utama 30 (zon waktu komputer dulu, kemudian {Time zone}).
- Sesiapa yang membuat nota (anda sebagai ejen atau tugasan berjadual) tulis blok info dulu. Jika sesuatu nota tiada blok info, tambah blok itu di bahagian atas kali seterusnya nota itu disunting.
- Tiada tajuk `# YYYY-MM-DD`. Nama fail sudah menjadi tajuknya.
- Nota harian menyimpan keadaan terkini hari itu: satu dokumen kemas setiap hari, bahagiannya dikemas kini di tempat yang sama, bukan timbunan catatan yang berulang.
- Log sesi: tajuk utama bercetak tebal ditambah 1 atau 2 ayat, orang dan projek sebagai `[[wikilink]]`, butiran masuk ke nota yang dipautkan.
- Nota hari ini hanya untuk aktiviti hari ini. Tugasan yang belum selesai dari hari sebelumnya masuk ke `tugasan.md`. Jangan sekali-kali salin tugasan itu ke nota hari baharu.
- Apabila anda membuat nota hari ini, lihat nota dari 2, 3 dan 4 hari lepas. Mana-mana yang masih `status: active` ditukar menjadi `completed`, dan diberi tag daripada senarai tetap untuk perkara yang jelas berlaku pada hari itu. Jangan lihat lebih jauh ke belakang.

## tasks.md

Tugasan yang belum selesai dan bukan milik mana-mana projek. Tugasan projek masuk ke README projek itu ("Status dan langkah seterusnya"). Dibuat apabila mula-mula diperlukan:

```markdown
---
type: tasks
status: active
tags: [tasks, daily]
---

## Belum selesai

- [ ] 2026-10-13: Hantar invois kepada [[Ana]]

## Selesai

- [x] 2026-10-12: Buat temu janji dengan doktor gigi (selesai 2026-10-13)
```

- Tugasan baharu yang belum selesai di bahagian atas, dengan tarikh ia ditambah.
- Apabila tugasan selesai, tandakan, tambah tarikh ia selesai, dan pindahkan ke `## Selesai`.
- Tugasan selesai yang lebih lama daripada 30 hari boleh dibuang (tanya dulu, peraturan utama 9).
