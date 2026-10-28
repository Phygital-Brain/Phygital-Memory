<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove table rows for files that weren't created.
-->

Folder ini menyimpan fakta utama tentang {Name}. Nota di sini ialah sumber kebenaran untuk semua kerja lain.

## Fail

| Fail | Isi | Tag kategori |
|---|---|---|
| `saya.md` | Siapa {Name}, cara {Name} bekerja, dan cara {Name} mahu ejennya bekerja | `identity` |
| `biografi.md` | Kisah hidup {Name} | `identity` |
| `matlamat.md` | Matlamat dan keutamaan | `goals` |
| `perniagaan.md` | Perniagaannya | `business` |
| `perkhidmatan.md` | Perkhidmatan, produk, tawaran | `business` |
| `pelanggan.md` | Siapa yang membeli dan bagaimana mereka jumpa {Name} | `customers` |
| `masalah.md` | Masalah yang perlu diselesaikan | `customers` (atau `goals` jika {Name} tidak menjual apa-apa) |
| `jenama.md` | Gaya bahasa, nada, perkataan yang digunakan dan yang dielakkan | `brand` |
| `alatan.md` | Alatan, dan di mana setiap jenis perkara disimpan | `tools` |
| `resume.md` | Pengalaman kerja, pendidikan, liputan media, anugerah | `career` |

## Blok info (frontmatter)

Setiap fail di sini (kecuali fail ini) bermula dengan:

```yaml
---
type: about
status: active
updated: 2026-10-13
tags: [about, identity, working-style]
description: "Siapa {Name} dan bagaimana {Name} mahu ejennya bekerja."
---
```

- `type`: sentiasa `about`.
- `status`: `active`, atau `outdated` apabila ada fakta yang diketahui sudah lapuk.
- `updated`: tarikh fakta terakhir berubah. Jangan ubah tarikh ini untuk pembetulan ejaan atau gaya.
- `tags`: `about`, kemudian tag kategori fail daripada jadual di atas, kemudian tag topik yang menamakan isi fail (bahasa Inggeris, huruf kecil, guna tanda sempang). Kemas kini tag topik apabila satu bahagian ditambah atau dibuang.
- `description`: satu ayat, dalam tanda petik berganda, yang menyatakan isi fail ini. Sentiasa di baris terakhir.

## Peraturan

- Fail-fail ini ialah sumber kebenaran. Jangan salin isinya ke tempat lain: pautkan sahaja.
- Format kebenaran terkini (peraturan utama 17): kebenaran semasa di atas, bukti bertarikh di bawah.
- Tarikh lahir penuh {Name} hanya disimpan dalam `saya.md`. Jangan sekali-kali salin atau sebut tarikh itu dalam balasan. Tahun lahir sahaja tidak mengapa.
- Buat fail baharu hanya apabila ada topik baharu yang memerlukannya. Tanya dulu (peraturan utama 9).
- Semasa semakan, tandakan matlamat dalam `matlamat.md` yang tiada projek aktif.
