<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove table rows for files that weren't created.
-->

Folder ini berisi fakta-fakta inti tentang {Name}. Catatan di sini jadi sumber kebenaran untuk semua pekerjaan lain.

## File

| File | Isinya | Tag kategori |
|---|---|---|
| `profil.md` | Siapa {Name}, cara kerjanya, dan cara ia ingin agennya bekerja | `identity` |
| `biografi.md` | Kisah hidup {Name} | `identity` |
| `tujuan.md` | Tujuan dan prioritas | `goals` |
| `bisnis.md` | Bisnisnya | `business` |
| `layanan.md` | Jasa, produk, penawaran | `business` |
| `pelanggan.md` | Siapa yang membeli dan bagaimana mereka menemukan {Name} | `customers` |
| `kendala.md` | Masalah yang perlu dipecahkan | `customers` (atau `goals` kalau {Name} tidak berjualan) |
| `brand.md` | Gaya bicara, nada, kata yang dipakai dan dihindari | `brand` |
| `alat.md` | Alat yang dipakai dan tempat menyimpan tiap jenis hal | `tools` |
| `cv.md` | Riwayat kerja, pendidikan, liputan media, penghargaan | `career` |

## Blok info (frontmatter)

Setiap file di sini (kecuali file ini) diawali dengan:

```yaml
---
type: about
status: active
updated: 2026-10-13
tags: [about, identity, working-style]
description: "Siapa {Name} dan bagaimana ia ingin agennya bekerja."
---
```

- `type`: selalu `about`.
- `status`: `active`, atau `outdated` kalau ada fakta yang diketahui sudah usang.
- `updated`: tanggal terakhir faktanya berubah. Tidak diubah untuk perbaikan salah ketik atau gaya tulisan.
- `tags`: `about`, lalu tag kategori file dari tabel di atas, lalu tag topik yang menyebut isi file (bahasa Inggris, huruf kecil, pakai tanda hubung). Perbarui tag topik setiap ada bagian yang ditambah atau dihapus.
- `description`: satu kalimat dalam tanda kutip ganda yang menjelaskan isi file ini. Selalu di baris terakhir.

## Aturan

- File-file ini adalah sumber kebenaran. Jangan salin isinya ke tempat lain: tautkan saja.
- Format kebenaran terkini (aturan utama 17): kebenaran saat ini di atas, bukti bertanggal di bawahnya.
- Tanggal lahir lengkap {Name} hanya ada di `profil.md`. Jangan pernah menyalinnya atau menyebutnya dalam balasan. Tahun lahir saja boleh.
- Buat file baru hanya kalau ada topik baru yang butuh file sendiri. Tanya dulu (aturan utama 9).
- Saat pemeriksaan, tandai tujuan di `tujuan.md` yang belum punya proyek aktif.
