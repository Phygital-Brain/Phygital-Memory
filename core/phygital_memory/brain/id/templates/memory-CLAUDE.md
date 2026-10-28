Pengetahuan yang terkumpul seiring waktu: keputusan, riset, pengajuan, dan arsip.

## Rute

| Isi | Simpan di |
|---|---|
| Keputusan beserta alasannya, atau kajian tentang hal dari luar (aplikasi, situs web, kursus, pesaing) | `keputusan/YYYY-MM-DD-{title}.md` |
| Riset (pasar, tren, pilihan) | `riset/{topic}.md` |
| Pengajuan: lamaran kerja, hibah, penghargaan, open call (dibuat saat pertama kali dipakai) | `pengajuan/{name}/` |
| Profil pesaing (dibuat saat pertama kali dipakai) | `pesaing/{name}.md` |
| Uang: invoice, pajak, pembayaran. Pribadi | `keuangan/` |
| Keputusan yang diarsipkan | `arsip/keputusan/` |
| Riset yang sudah selesai atau usang | `arsip/riset/` |
| Proyek yang sudah selesai | `arsip/{name}/` |
| Catatan rapat | `keputusan/` kalau rapatnya menghasilkan keputusan, kalau tidak masuk ke catatan `Harian/` hari itu. Sarankan folder khusus rapat hanya kalau jumlahnya sudah banyak. |

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
- `date`: tanggal catatan ditulis.
- `status`: untuk keputusan dan pengajuan, lihat di bawah. Selain itu: `active` atau `closed`.
- `tags`: jenisnya, lalu topiknya.
- Opsional: `project`, `deadline`, `description` (satu kalimat dalam tanda kutip ganda, di baris terakhir).

## Catatan keputusan

Selalu tulis alasannya: siapa yang terlibat, apa pemicunya, dan apa yang dikorbankan demi pilihan itu. Pakai `> [!important]` untuk keputusannya dan `> [!warning]` untuk risiko yang sudah diketahui.

Keputusan juga punya `updated:` tepat setelah `date:`. `date` adalah tanggal dibuat, `updated` adalah terakhir kali ditinjau atau diubah.

```yaml
---
type: decision
date: 2026-09-02
updated: 2026-10-13
status: open
tags: [decision, website]
---
```

- `status`: `open` (masih dipertimbangkan atau dikerjakan), `waiting` (menunggu orang lain), `paused`, `closed`.
- Keputusan yang `updated`-nya lebih dari 30 hari perlu ditinjau. Penjaga Otak terus menandainya sampai {Name} mempertahankannya, menutupnya, atau mengarsipkannya (masing-masing mengubah `updated` ke tanggal hari itu).
- Keputusan dipindahkan ke `arsip/keputusan/` hanya kalau {Name} yang bilang.

## Pengajuan

Satu folder per pengajuan: `pengajuan/{name}/`, dengan `README.md` berisi tenggat waktu, link, status, dan apa yang sudah dikirim. File lain (jawaban, pernyataan) disimpan di sebelahnya.

- `status`: `draft`, `submitted`, `accepted`, `rejected`, atau `withdrawn`.
- Simpan jawaban dalam markdown. PDF dan slide yang besar tetap di luar vault: buat ringkasannya di sebuah catatan.

## Aturan

- Riset bersifat netral secara default (aturan utama 23).
- Pindahkan riset yang sudah tergantikan ke `arsip/riset/`, jangan dihapus.
- `keuangan/` bersifat pribadi dan tercantum di `.claudeignore`. Buka hanya kalau {Name} meminta file tertentu (aturan utama 8).
