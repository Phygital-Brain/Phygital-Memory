<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the "Where a new lead goes" section if there's no `Klien/` folder. Remove subfolder rows that weren't created.
Each subfolder gets its own `CLAUDE.md` from `relationships-subfolder-CLAUDE.md`.
-->

Semua orang yang bekerja dengan {Name}: satu catatan per orang atau organisasi.

## Subfolder

| Folder | Siapa yang masuk ke sini |
|---|---|
| `Klien/` | Orang dan perusahaan yang memakai jasa {Name} |
| `Kolaborator/` | Rekan kreatif, saling bertukar, tanpa melibatkan uang |
| `Tim/` | Orang yang bekerja bersama atau untuk {Name} (freelancer, asisten) |
| `Mitra/` | Organisasi tempat {Name} membangun nama (media, tempat acara, platform) |

## Ke mana calon klien baru dicatat

- Kontak pertama yang belum punya brief jelas: satu baris di bawah `## Baru` di `Klien/_Prospek.md` (dibuat saat pertama kali dipakai).
- Balasan yang bilang "mungkin nanti": satu baris di bawah `## Tetap dihubungi` di `Klien/_Prospek.md`.
- Brief, telepon, atau penawaran harga yang sedang berjalan: catatan klien `Klien/{client-name}.md` dengan `status: prospect`.

Kalau calon klien naik satu tahap, pindahkan ke tempat berikutnya dan hapus dari tempat sebelumnya.

## Blok info (frontmatter)

Setiap catatan di sini (kecuali file `CLAUDE.md` dan `_Prospek.md`) diawali dengan:

```yaml
---
type: client
status: active
last-contact: 2026-10
tags: [relationship, client, fashion, brazil]
description: "Satu kalimat sederhana tentang siapa mereka dan hubungannya dengan {Name}."
---
```

- `type`: `client`, `collaborator`, `team`, atau `partner`.
- `status`: `active` (ada pekerjaan atau kontak dalam 12 bulan terakhir), `prospect` (masih berdiskusi, belum pernah bekerja sama), `dormant` (tidak ada kontak selama 12 bulan atau lebih), `closed` (sudah berakhir untuk selamanya).
- `last-contact`: bulan terakhir ada kontak atau pekerjaan sungguhan, `YYYY-MM`. Kosongkan kalau tidak diketahui.
- `tags`: `relationship`, lalu jenisnya, lalu 2 sampai 5 tag topik (industri, negara, jenis pekerjaan), bahasa Inggris, huruf kecil, pakai tanda hubung.
- `description`: satu kalimat dalam tanda kutip ganda. Selalu di baris terakhir.
- Opsional: `aliases` (nama lain yang dipakai untuk mereka), `project` (proyek saat ini).

## Aturan

- **Tidak ada duplikat.** Sebelum membuat catatan, cari namanya beserta variasinya (aksen, nama panggilan, nama brand atau nama perusahaannya). Kalau catatannya sudah ada, pakai itu dan tambahkan ejaan barunya ke `aliases`. Jangan pernah membuat catatan kedua untuk orang atau perusahaan yang sama.
- **Format kebenaran terkini** (aturan utama 17): siapa mereka dan keadaan saat ini di atas, riwayat bertanggal di bawah.
- **Jaga tetap terkini.** Kalau {Name} benar-benar berhubungan dengan seseorang (email, telepon, pekerjaan yang dikirim), ubah `last-contact` ke bulan ini, dan `status` kalau berubah.
- **Narahubung** di sebuah perusahaan (agen, manajer, editor) ditulis sebagai teks biasa di dalam catatan perusahaannya, tidak pernah sebagai `[[tautan]]`, dan tidak punya catatan sendiri. Untuk menyebut mereka di tempat lain, tautkan perusahaannya: `[[Nama Perusahaan|Nama Narahubung]]`.
- **Data pribadi** (nomor telepon, email, alamat rumah) hanya ada di catatan orang atau perusahaan itu. Jangan pernah menyalinnya ke catatan harian atau catatan lain.
- Tautkan orang dari proyek dan catatan harian dengan `[[wikilink]]`.
- Buat subfolder baru hanya kalau muncul jenis hubungan baru. Tanya dulu.
