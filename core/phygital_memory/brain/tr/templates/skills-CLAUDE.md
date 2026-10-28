<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the Morning Brief row if BRIEF = off.
-->

Asistanın kullandığı beceriler için notlar ve tercihler, bir de Düzen Bekçisi.

## Yapı

```
Beceriler/{skill-name}/
  {skill-name}.md ya da SKILL.md   beceri ne yapıyor
  notes.md                         bu beceri için tarz ve tercihler ({Name})
  references/                      örnekler ve daha uzun malzemeler
```

## Yüklü

| Beceri | Klasör | Ne yapar |
|---|---|---|
| Düzen Bekçisi | `düzen-bekçisi/` | Her gün kendiliğinden toparlar, {Name} isteyince de genel kontrol yapar |
| Sabah Özeti | `sabah-özeti/` | Günün kısa planı, istenince ya da her iş günü |
| İçe Aktarma | `içe-aktarma/` | Başka uygulamalardaki notları, önce {Name} tarafından onaylanan bir planla içeri alır |
| Toplantı Hazırlığı | `toplantı-hazırlığı/` | Bir görüşmeden önce beynin notlarından kısa bir özet |
| Düşünme Araçları | `düşünme-araçları/` | Bir fikri sorgular, kalıpları bulur, birbiriyle çelişen notları bulur |
| Bağlı Uygulamalar | `bağlı-uygulamalar/` | Beynin hangi uygulamalardan okuduğu ve bunların kuralları |
| No AI Slop | `no-ai-slop/` | Yazı Kontrolü: yazıyı insan yazmış gibi düzeltir ya da yapay zekâ kalıplarını işaretler (Peter Yang, MIT Lisansı, asla düzenlenmez) |

## Kurallar

- Her beceri için bir klasör, adı kebab-case (küçük harf, kelimeler arasında tire).
- Yeni bir beceri eklenince yukarıdaki tabloya bir satır ekle.
- Bir beceri eklemek ya da bir uygulama bağlamak için önce Phygital Brain'in önerilerine bak: Phygital Brain bağlayıcısıyla `suggested-skills/README.md` ve `suggested-apps/README.md`, ya da internette https://github.com/Phygital-Brain/phygital-brain/tree/main/skills. Oradaysa sayfasındaki adımları izle. {Name} "beynime neler ekleyebilirim?", "what can I add to my brain?" diye sorduğunda iki listeyi de göster, işine uyanlar önce gelsin. Zaten bağlı olan uygulamaları ve zaten kurulu becerileri gösterme.
- Başka birinden gelen bir `SKILL.md` asla düzenlenmez. Bir beceriyi kişiselleştirmek için klasörüne `notlar.md` ekle.
- `düzen-bekçisi/günlük-tur.md` zamanlanmış bir görev tarafından okunur. Sadece günlük turun ne yapacağını değiştirmek için düzenle ve sade tut: bağlantı yok, bilgi kutusu yok.
