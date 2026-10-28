Setiap projek ialah folder yang berkembang apabila maklumat masuk. `README.md` ialah satu-satunya pintu masuk.

## Laluan

| Isi | Simpan di |
|---|---|
| Gambaran keseluruhan, status, tarikh akhir, langkah seterusnya | `Projek/{name}/README.md` |
| Nota kerja {Name} | `Projek/{name}/nota/{topic}.md` |
| Kajian | `Projek/{name}/kajian/{topic}.md` |
| Taklimat, spesifikasi, keperluan | `Projek/{name}/taklimat/{name}.md` |
| Draf, skrip, kandungan bertulis | `Projek/{name}/draf/{name}.md` |
| Idea | `Projek/{name}/idea/{name}.md` |
| Maklum balas | `Projek/{name}/maklum-balas/{name}.md` |
| Gambar dan media | `Projek/{name}/media/` |
| Bahan lama daripada projek ini | `Projek/{name}/arkib/` |

Nama folder dalam huruf kecil dengan tanda sempang, tanpa nombor di depan (`kajian/`, bukan `01-Research/`). Projek boleh tambah folder sendiri apabila tiada yang sesuai di atas.

## Susunan README

1. Blok info (di bawah), dengan `description`.
2. `## Apa projek ini`: satu atau dua baris, dipautkan ke [[matlamat]].
3. `## Status dan langkah seterusnya`: kedudukan sekarang, langkah seterusnya.
4. `## Cara ia berjalan`: hanya jika ada sesuatu yang automatik menulis di sini (tugasan berjadual, skrip).
5. `## Di mana semuanya`: hanya apabila subfolder sudah ada. Jadual kecil yang memautkan setiap satu.

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

- `type`: `project` (README, yang juga ada `created`, `updated` dan `description`), `notes`, `research`, `brief`, `draft`, `idea`, `feedback`, `plan`.
- `status`: `active`, `paused` atau `done`. Status README ialah status projek.
- `project`: nama folder projek.
- `tags`: projeknya, kemudian jenisnya.

## Peraturan

- Projek baharu hanyalah satu `README.md`. Buat subfolder hanya apabila ada isi yang memerlukannya, dan pautkan dari README.
- README ialah indeks. Jangan ulang isi subfolder di dalamnya.
- Tiada `CLAUDE.md` di dalam projek. Peraturan untuk satu projek masuk ke "Peraturan setiap projek" di bawah.
- Masukkan `project:` dalam blok info setiap nota yang berkaitan.
- Projek yang sudah selesai dipindahkan ke `Ingatan/arkib/{name}/` hanya apabila {Name} kata begitu.
- Setiap projek patut membantu satu matlamat dalam [[matlamat]]. Semasa semakan, tandakan matlamat yang tiada projek dan projek yang tiada matlamat.

## Peraturan setiap projek

<!-- Peraturan untuk satu projek sahaja. Tambah satu baris apabila sesebuah projek perlukan peraturannya sendiri: "**Nama-Projek:** peraturannya." -->
