Setiap proyek adalah sebuah folder yang terus bertambah seiring datangnya informasi. `README.md` adalah satu-satunya pintu masuk.

## Rute

| Isi | Simpan di |
|---|---|
| Gambaran umum, status, tenggat waktu, langkah berikutnya | `Proyek/{name}/README.md` |
| Catatan kerja {Name} | `Proyek/{name}/catatan/{topic}.md` |
| Riset | `Proyek/{name}/riset/{topic}.md` |
| Brief, spesifikasi, kebutuhan | `Proyek/{name}/brief/{name}.md` |
| Draf, naskah, konten tulisan | `Proyek/{name}/draf/{name}.md` |
| Ide | `Proyek/{name}/ide/{name}.md` |
| Masukan | `Proyek/{name}/masukan/{name}.md` |
| Gambar dan media | `Proyek/{name}/aset/` |
| Bahan lama dari proyek ini | `Proyek/{name}/arsip/` |

Nama folder memakai huruf kecil dengan tanda hubung, tanpa awalan angka (`riset/`, bukan `01-Riset/`). Sebuah proyek boleh menambah folder sendiri kalau tidak ada yang cocok dari daftar ini.

## Susunan README

1. Blok info (di bawah), dengan `description`.
2. `## Tentang proyek ini`: satu atau dua baris, ditautkan ke [[tujuan]].
3. `## Status dan langkah berikutnya`: posisinya sekarang, dan langkah berikutnya.
4. `## Cara jalannya`: hanya kalau ada yang otomatis menulis di sini (tugas terjadwal, skrip).
5. `## Letak isinya`: hanya setelah ada subfolder. Tabel kecil yang menautkan masing-masing.

## Blok info (frontmatter)

```yaml
---
type: notes
date: 2026-10-13
status: active
project: Website-Redesign
tags: [website-redesign, notes]
---
```

- `type`: `project` (README, yang juga punya `created`, `updated`, dan `description`), `notes`, `research`, `brief`, `draft`, `idea`, `feedback`, `plan`.
- `status`: `active`, `paused`, atau `done`. Status README adalah status proyeknya.
- `project`: nama folder proyek.
- `tags`: proyeknya, lalu jenisnya.

## Aturan

- Proyek baru cukup berupa `README.md`. Buat subfolder hanya kalau ada isi baru yang membutuhkannya, dan tautkan dari README.
- README adalah daftar isinya. Jangan ulangi isi subfolder di sana.
- Tidak ada `CLAUDE.md` di dalam proyek. Aturan untuk satu proyek masuk ke "Aturan per proyek" di bawah.
- Cantumkan `project:` di blok info setiap catatan yang berkaitan.
- Proyek yang sudah selesai dipindahkan ke `Memori/arsip/{name}/` hanya kalau {Name} yang bilang.
- Setiap proyek sebaiknya mendukung salah satu tujuan di [[tujuan]]. Saat pemeriksaan, tandai tujuan yang tidak punya proyek dan proyek yang tidak punya tujuan.

## Aturan per proyek

<!-- Aturan khusus untuk satu proyek saja. Tambahkan satu baris kalau sebuah proyek butuh aturan sendiri: "**Nama-Proyek:** aturannya." -->
