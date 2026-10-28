<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the `clients` tag line if BUSINESS = off.
-->

Günlük notlar ({Name}). Her gün için bir dosya: `YYYY-MM-DD.md`. Açık görevler `görevler.md` içinde durur.

## Bilgi bloğu (frontmatter)

Her günlük not bu blokla başlar. İstisna yok.

```yaml
---
type: daily
date: 2026-10-13
day: Tuesday
week: W42
month: October
status: active
tags: [daily, meeting]
---
```

- `type`: her zaman `daily`.
- `date`: notun tarihi, `YYYY-MM-DD`.
- `day`: haftanın günü, İngilizce (Monday, Tuesday...).
- `week`: ISO hafta numarası, `WNN`.
- `month`: ay, İngilizce (January, February...).
- `status`: gün açıkken `active`, not 2 gün ya da daha eski olunca `completed`.
- `tags`: her zaman `daily`, artı bu sabit listeden o gün olanlar. Asla başka etiket uydurma.
  - `problem`: bir şey bozuldu ya da ters gitti
  - `clients`: müşteri işi ya da müşteriyle iletişim
  - `meeting`: bir görüşme ya da toplantı
  - `money`: faturalar, ödemeler, vergiler, yatırımlar
  - `research`: yapılan araştırma ya da bulgular
  - `decision`: {Name} bir karar verdi
  - `travel`: {Name} seyahatteydi
  - `personal`: sağlık, özel hayat, işin dışındaki her şey

## Kurallar

- Tarihler ana kural 30'a uyar (önce bilgisayarın saat dilimi, sonra {Time zone}).
- Notu kim oluşturursa (asistanın ya da zamanlanmış bir görev) önce bilgi bloğunu yazar. Bilgi bloğu olmayan bir notta blok, bir sonraki düzenlemede en üste eklenir.
- `# YYYY-MM-DD` diye başlık yok. Dosya adı zaten başlık.
- Günlük not günün güncel halini tutar: her gün için tek ve derli toplu bir belge, bölümler yerinde güncellenir, asla üst üste tekrarlanan kayıtlar yığını olmaz.
- Oturum kayıtları: kalın bir başlık ve 1 ya da 2 cümle, kişiler ve projeler `[[wikilink]]` olarak, ayrıntılar bağlantı verilen notta.
- Bugünün notu sadece bugün olanları tutar. Önceki günlerden kalan açık görevler `görevler.md` dosyasına gider. Onları asla ileriye kopyalama.
- Bugünün notunu oluştururken 2, 3 ve 4 gün önceki notlara bak. Hâlâ `status: active` olanlar `completed` olur ve o gün açıkça ne olduysa sabit listeden etiketlerini alır. Daha geriye bakma.

## tasks.md

Bir projeye ait olmayan açık görevler. Proje görevleri o projenin README dosyasına ("Durum ve sıradaki adım") gider. İlk kullanımda oluşturulur:

```markdown
---
type: tasks
status: active
tags: [tasks, daily]
---

## Açık

- [ ] 2026-10-13: Faturayı [[Ana]]'ya gönder

## Bitti

- [x] 2026-10-12: Diş hekiminden randevu al (bitti 2026-10-13)
```

- En yeni açık görevler en üstte, eklendikleri tarihle.
- Bir görev bitince işaretle, bittiği tarihi ekle ve `## Bitti` altına taşı.
- 30 günden eski bitmiş görevler kaldırılabilir (önce sor, ana kural 9).
