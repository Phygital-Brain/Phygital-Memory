<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the "Where a new lead goes" section if there's no `Klien/` folder. Remove subfolder rows that weren't created.
Each subfolder gets its own `CLAUDE.md` from `relationships-subfolder-CLAUDE.md`.
-->

Semua orang yang bekerja dengan {Name}: satu nota untuk setiap orang atau organisasi.

## Subfolder

| Folder | Siapa yang masuk ke sini |
|---|---|
| `Klien/` | Orang dan syarikat yang {Name} buat kerja untuk mereka |
| `Kolaborator/` | Rakan kreatif, saling bertukar bantuan, tiada wang terlibat |
| `Pasukan/` | Orang yang bekerja bersama atau untuk {Name} (pekerja bebas, pembantu) |
| `Rakan-Kongsi/` | Organisasi yang membantu {Name} membina nama (media, tempat acara, platform) |

## Ke mana prospek baharu pergi

- Hubungan pertama yang belum ada taklimat sebenar: satu baris di bawah `## Baharu` dalam `Klien/_Prospek.md` (dibuat apabila mula-mula diperlukan).
- Balasan yang kata "mungkin nanti": satu baris di bawah `## Jaga hubungan` dalam `Klien/_Prospek.md`.
- Taklimat, panggilan atau sebut harga yang sebenar sedang berjalan: nota klien `Klien/{client-name}.md` dengan `status: prospect`.

Apabila prospek naik satu langkah, pindahkannya ke tempat seterusnya dan buang dari tempat sebelumnya.

## Blok info (frontmatter)

Setiap nota di sini (kecuali fail `CLAUDE.md` dan `_Prospek.md`) bermula dengan:

```yaml
---
type: client
status: active
last-contact: 2026-10
tags: [relationship, client, fashion, brazil]
description: "Satu ayat mudah tentang siapa mereka dan hubungan mereka dengan {Name}."
---
```

- `type`: `client`, `collaborator`, `team` atau `partner`.
- `status`: `active` (ada kerja atau hubungan dalam 12 bulan lepas), `prospect` (sedang berbincang, belum pernah bekerja bersama), `dormant` (tiada hubungan selama 12 bulan atau lebih), `closed` (sudah tamat terus).
- `last-contact`: bulan terkini yang ada hubungan atau kerja sebenar, `YYYY-MM`. Biarkan kosong jika tidak tahu.
- `tags`: `relationship`, kemudian jenisnya, kemudian 2 hingga 5 tag topik (industri, negara, jenis kerja), bahasa Inggeris, huruf kecil, guna tanda sempang.
- `description`: satu ayat, dalam tanda petik berganda. Sentiasa di baris terakhir.
- Pilihan: `aliases` (nama lain yang digunakan untuk mereka), `project` (projek semasa).

## Peraturan

- **Jangan ada pendua.** Sebelum membuat nota, cari nama itu dan variasinya (huruf beraksen, nama pendek, nama jenama berbanding nama syarikat). Jika nota sudah ada, gunakannya dan tambah ejaan baharu itu ke `aliases`. Jangan sekali-kali buat nota kedua untuk orang atau syarikat yang sama.
- **Format kebenaran terkini** (peraturan utama 17): siapa mereka dan keadaan semasa di atas, sejarah bertarikh di bawah.
- **Sentiasa terkini.** Apabila {Name} ada hubungan sebenar dengan seseorang (e-mel, panggilan, kerja yang dihantar), kemas kini `last-contact` kepada bulan ini, dan `status` jika ia berubah.
- **Orang hubungan** di sesebuah syarikat (ejen, pengurus, editor) ditulis sebagai teks biasa di dalam nota syarikat, bukan `[[pautan]]`, dan tidak diberi nota sendiri. Untuk menyebut mereka di tempat lain, pautkan syarikatnya: `[[Nama Syarikat|Nama Orang]]`.
- **Butiran peribadi** (nombor telefon, e-mel, alamat rumah) hanya disimpan dalam nota orang atau syarikat itu. Jangan sekali-kali salin ke nota harian atau nota lain.
- Pautkan orang dari projek dan nota harian dengan `[[wikilink]]`.
- Buat subfolder baharu hanya apabila muncul jenis hubungan yang baharu. Tanya dulu.
