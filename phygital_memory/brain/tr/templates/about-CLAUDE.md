<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove table rows for files that weren't created.
-->

Bu klasör {Name} hakkındaki temel bilgileri tutar. Buradaki notlar, diğer bütün işler için doğru bilginin kaynağıdır.

## Dosyalar

| Dosya | Ne için | Kategori etiketi |
|---|---|---|
| `ben.md` | {Name} kim, nasıl çalışıyor, asistanın nasıl çalışmasını istiyor | `identity` |
| `biyografi.md` | Hayat hikâyesi ({Name}) | `identity` |
| `hedefler.md` | Hedefler ve öncelikler | `goals` |
| `işletme.md` | İşletme | `business` |
| `hizmetler.md` | Hizmetler, ürünler, teklifler | `business` |
| `hedef-kitle.md` | Kimler satın alıyor ve {Name} ile nasıl tanışıyorlar | `customers` |
| `sorunlar.md` | Çözülecek sorunlar | `customers` ({Name} bir şey satmıyorsa `goals`) |
| `marka.md` | Ses, ton, kullanılacak ve kaçınılacak kelimeler | `brand` |
| `araçlar.md` | Araçlar ve her şeyin nerede durduğu | `tools` |
| `özgeçmiş.md` | İş geçmişi, eğitim, basın, ödüller | `career` |

## Bilgi bloğu (frontmatter)

Buradaki her dosya (bu dosya hariç) şununla başlar:

```yaml
---
type: about
status: active
updated: 2026-10-13
tags: [about, identity, working-style]
description: "{Name} kim ve asistanın nasıl çalışmasını istiyor."
---
```

- `type`: her zaman `about`.
- `status`: `active` ya da bir bilginin eskidiği biliniyorsa `outdated`.
- `updated`: bilgilerin en son değiştiği tarih. Yazım hatası ya da üslup düzeltmelerinde değişmez.
- `tags`: önce `about`, sonra yukarıdaki tablodan dosyanın kategori etiketi, sonra dosyanın neyi anlattığını gösteren konu etiketleri (İngilizce, küçük harf, kelimeler arasında tire). Bir bölüm eklenince ya da çıkarılınca konu etiketlerini güncelle.
- `description`: bu dosyada ne olduğunu söyleyen, çift tırnak içinde tek bir cümle. Her zaman son satır.

## Kurallar

- Bu dosyalar doğru bilginin kaynağıdır. İçeriklerini başka yere kopyalama: bağlantı ver.
- "Güncel bilgi üstte, kanıtlar altta" biçimi (ana kural 17): bugünkü doğru bilgi en üstte, tarihli kanıtlar altta.
- Tam doğum tarihi sadece `ben.md` içinde durur. Asla kopyalama ya da bir cevapta yazma. Doğum yılı sorun değil.
- Yeni bir dosyayı sadece yeni bir konu gerektirdiğinde oluştur. Önce sor (ana kural 9).
- Genel kontrolde `hedefler.md` içinde aktif projesi olmayan hedefleri işaretle.
