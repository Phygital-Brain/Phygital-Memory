Pengetahuan yang bertambah dari masa ke masa: keputusan, kajian, permohonan dan arkib.

## Laluan

| Isi | Simpan di |
|---|---|
| Keputusan beserta sebabnya, atau kajian tentang sesuatu dari luar (aplikasi, laman web, kursus, pesaing) | `keputusan/YYYY-MM-DD-{title}.md` |
| Kajian (pasaran, trend, pilihan) | `kajian/{topic}.md` |
| Permohonan: kerja, geran, anugerah, panggilan terbuka (dibuat apabila mula-mula diperlukan) | `permohonan/{name}/` |
| Profil pesaing (dibuat apabila mula-mula diperlukan) | `pesaing/{name}.md` |
| Wang: invois, cukai, bayaran. Peribadi | `kewangan/` |
| Keputusan yang diarkibkan | `arkib/keputusan/` |
| Kajian yang sudah selesai atau lapuk | `arkib/kajian/` |
| Projek yang sudah selesai | `arkib/{name}/` |
| Nota mesyuarat | `keputusan/` jika ada keputusan dibuat, jika tidak, nota `Harian/` hari itu. Cadangkan folder mesyuarat hanya apabila sudah banyak. |

## Blok info (frontmatter)

```yaml
---
type: research
date: 2026-10-13
status: active
tags: [research, pricing]
---
```

- `type`: `decision`, `research`, `application`, `competitor`.
- `date`: tarikh nota ditulis.
- `status`: lihat di bawah untuk keputusan dan permohonan. Selain itu: `active` atau `closed`.
- `tags`: jenisnya, kemudian topiknya.
- Pilihan: `project`, `deadline`, `description` (satu ayat, dalam tanda petik berganda, baris terakhir).

## Nota keputusan

Sentiasa sertakan sebabnya: siapa yang terlibat, apa yang mencetuskannya, apa yang terpaksa dikorbankan. Guna `> [!important]` untuk keputusan itu sendiri dan `> [!warning]` untuk risiko yang diketahui.

Keputusan juga ada `updated:` terus selepas `date:`. `date` ialah bila ia dibuat, `updated` ialah kali terakhir ia disemak atau diubah.

```yaml
---
type: decision
date: 2026-09-02
updated: 2026-10-13
status: open
tags: [decision, website]
---
```

- `status`: `open` (masih difikirkan atau sedang dikerjakan), `waiting` (menunggu orang lain), `paused`, `closed`.
- Keputusan yang `updated` lebih daripada 30 hari lepas perlu disemak. Penjaga Otak akan menandakannya sehingga {Name} mengekalkan, menutup atau mengarkibkannya (setiap satu menetapkan `updated` kepada hari itu).
- Keputusan dipindahkan ke `arkib/keputusan/` hanya apabila {Name} kata begitu.

## Permohonan

Satu folder untuk setiap permohonan: `permohonan/{name}/`, dengan `README.md` yang mengandungi tarikh akhir, pautan, status dan apa yang dihantar. Fail lain (jawapan, kenyataan) diletakkan bersebelahan.

- `status`: `draft`, `submitted`, `accepted`, `rejected` atau `withdrawn`.
- Simpan jawapan dalam markdown. PDF dan slaid yang besar kekal di luar folder otak: ringkaskan dalam nota.

## Peraturan

- Kajian bersifat neutral secara lalai (peraturan utama 23).
- Pindahkan kajian yang sudah digantikan ke `arkib/kajian/`, jangan padam.
- `kewangan/` bersifat peribadi dan disenaraikan dalam `.claudeignore`. Buka hanya apabila {Name} minta fail tertentu (peraturan utama 8).
