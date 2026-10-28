<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the "Where a new lead goes" section if there's no `Müşteriler/` folder. Remove subfolder rows that weren't created.
Each subfolder gets its own `CLAUDE.md` from `relationships-subfolder-CLAUDE.md`.
-->

{Name} ile çalışan herkes: her kişi ya da kurum için bir not.

## Alt klasörler

| Klasör | Kimler girer |
|---|---|
| `Müşteriler/` | {Name} ile müşteri olarak çalışan kişi ve şirketler |
| `Ortaklar/` | Yaratıcı ortaklar, karşılıklı paylaşım, işin içinde para yok |
| `Ekip/` | {Name} ile ya da {Name} için çalışan kişiler (serbest çalışanlar, asistanlar) |
| `Kurumlar/` | {Name} için görünürlük sağlayan kurumlar (basın, mekânlar, platformlar) |

## Yeni bir iş fırsatı nereye gider

- Henüz gerçek bir brif olmayan ilk temas: `Müşteriler/_Fırsatlar.md` içinde `## Yeni` altına bir satır (ilk kullanımda oluşturulur).
- "Belki ileride" diyen bir cevap: `Müşteriler/_Fırsatlar.md` içinde `## Sıcak tut` altına bir satır.
- Gerçek bir brif, görüşme ya da süren bir fiyat teklifi: `status: prospect` ile bir müşteri notu, `Müşteriler/{client-name}.md`.

Bir iş fırsatı bir adım ilerleyince onu bir sonraki yerine taşı ve önceki yerden kaldır.

## Bilgi bloğu (frontmatter)

Buradaki her not (`CLAUDE.md` dosyaları ve `_Fırsatlar.md` hariç) şununla başlar:

```yaml
---
type: client
status: active
last-contact: 2026-10
tags: [relationship, client, fashion, brazil]
description: "Kim oldukları ve {Name} ile ilişkileri hakkında sade tek bir cümle."
---
```

- `type`: `client`, `collaborator`, `team` ya da `partner`.
- `status`: `active` (son 12 ay içinde iş ya da iletişim), `prospect` (konuşuluyor, hiç birlikte çalışılmadı), `dormant` (12 aydan uzun süredir iletişim yok), `closed` (tamamen bitti).
- `last-contact`: gerçek iletişimin ya da işin olduğu en son ay, `YYYY-MM`. Bilinmiyorsa boş bırak.
- `tags`: önce `relationship`, sonra tür, sonra 2 ile 5 arası konu etiketi (sektör, ülke, iş türü), İngilizce, küçük harf, kelimeler arasında tire.
- `description`: çift tırnak içinde tek cümle. Her zaman son satır.
- İsteğe bağlı: `aliases` (onlar için kullanılan diğer adlar), `project` (güncel proje).

## Kurallar

- **Tekrar yok.** Bir not oluşturmadan önce adı ve farklı yazılışlarını ara (aksanlar, kısa adlar, marka adı ya da şirket adı). Not varsa onu kullan ve yeni yazılışı `aliases` alanına ekle. Aynı kişi ya da şirket için asla ikinci bir not açma.
- **"Güncel bilgi üstte, kanıtlar altta" biçimi** (ana kural 17): kim oldukları ve güncel durum üstte, tarihli geçmiş altta.
- **Güncel tut.** {Name} biriyle gerçekten iletişim kurduğunda (bir e-posta, bir görüşme, teslim edilen bir iş), `last-contact` alanını bu aya çek, `status` değiştiyse onu da güncelle.
- Bir şirketteki **irtibat kişileri** (menajer, yönetici, editör) şirket notunun içinde düz metindir, asla `[[bağlantı]]` değildir ve kendilerine ait not açılmaz. Onlardan başka yerde bahsetmek için şirkete bağlantı ver: `[[Şirket Adı|İrtibat Kişisinin Adı]]`.
- **Özel bilgiler** (telefonlar, e-postalar, ev adresleri) sadece o kişinin ya da şirketin notunda durur. Asla günlük notlara ya da başka notlara kopyalama.
- Projelerden ve günlük notlardan kişilere `[[wikilink]]` ile bağlantı ver.
- Yeni bir alt klasörü sadece yeni bir ilişki türü ortaya çıktığında oluştur. Önce sor.
