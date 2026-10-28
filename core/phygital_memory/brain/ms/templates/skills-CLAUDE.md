<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the Morning Brief row if BRIEF = off.
-->

Nota dan pilihan untuk kemahiran yang digunakan oleh ejen, serta Penjaga Otak.

## Struktur

```
Kemahiran/{skill-name}/
  {skill-name}.md atau SKILL.md   apa yang kemahiran itu buat
  notes.md                        suara dan pilihan {Name} untuk kemahiran ini
  references/                     contoh dan bahan yang lebih panjang
```

## Dipasang

| Kemahiran | Folder | Apa yang ia buat |
|---|---|---|
| Penjaga Otak | `penjaga-otak/` | Kemas harian dengan sendirinya, dan semakan apabila {Name} minta |
| Taklimat Pagi | `taklimat-pagi/` | Rancangan pendek untuk hari ini, bila diminta atau setiap hari bekerja |
| Import | `import/` | Membawa masuk nota dari aplikasi lain, dengan rancangan yang {Name} luluskan dulu |
| Persediaan Mesyuarat | `persediaan-mesyuarat/` | Ringkasan pendek sebelum panggilan, daripada nota dalam otak ini |
| Alat Berfikir | `alat-berfikir/` | Mencabar idea, mencari corak, mencari nota yang bercanggah |
| Aplikasi Bersambung | `aplikasi-bersambung/` | Aplikasi mana yang dibaca oleh otak ini, dan peraturannya |
| No AI Slop | `no-ai-slop/` | Semakan Tulisan: menyunting tulisan supaya berbunyi seperti manusia, atau menandakan corak AI (oleh Peter Yang, Lesen MIT, tidak pernah disunting) |

## Peraturan

- Satu folder untuk setiap kemahiran, dinamakan dalam kebab-case.
- Apabila kemahiran baharu ditambah, tambah satu baris dalam jadual di atas.
- Untuk menambah kemahiran atau menyambungkan aplikasi, semak dahulu cadangan Phygital Brain: `suggested-skills/README.md` dan `suggested-apps/README.md` melalui penyambung Phygital Brain, atau dalam talian di https://github.com/Phygital-Brain/phygital-brain/tree/main/skills. Jika ada di situ, ikut halamannya. Apabila {Name} bertanya "apa yang boleh saya tambah pada otak saya?", "what can I add to my brain?", tunjukkan kedua-dua senarai, yang sesuai dengan kerja {Name} dahulu, dan tinggalkan aplikasi yang sudah disambungkan serta kemahiran yang sudah dipasang.
- `SKILL.md` yang datang daripada orang lain tidak pernah disunting. Untuk menyesuaikan sesuatu kemahiran, tambah `nota.md` dalam foldernya.
- `penjaga-otak/harian.md` dibaca oleh tugasan berjadual. Ubah hanya untuk mengubah apa yang dibuat oleh larian harian, dan pastikan ia ringkas: tiada pautan, tiada kotak nota.
