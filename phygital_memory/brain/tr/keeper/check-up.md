---
type: skill
status: active
tags: [brain-keeper, check-up]
---

Düzen Bekçisi'nin genel kontrolü: {Name} isteyince bütün beyne baştan sona bakmak. {Name} evet demeden hiçbir şey değişmez. (Günlük toparlama `günlük-tur.md` içinde.)

Ne zaman: "beynimi kontrol et", "check up my brain", "beynimi toparla", "tidy my brain", "beyin kontrolü", "brain check-up" ya da {Language} olarak aynısı.

## 1. Bak (henüz hiçbir şeyi değiştirme)

Bütün klasörde ara ve sorunları şu gruplarda listele:

- **Kırık bağlantılar**: var olmayan notlara giden `[[bağlantılar]]`. Bunları asla boş bir not oluşturarak düzeltme: asıl not hâlâ senkronize oluyor olabilir (ana kural 28).
- **Sahipsiz notlar**: başka hiçbir notun bağlantı vermediği notlar.
- **Boş ya da neredeyse boş notlar** ve unutulmuş yer tutucular (`[name]`, `TBD`).
- **Yanlış yer**: klasörün en üst seviyesindeki dosyalar (`CLAUDE.md`, `.claudeignore`, `.backups/` ve başka bir asistanın tek satırlık kural dosyası, örneğin `AGENTS.md` hariç), klasörünün Ne Nereye Gider tablosuna uymayan notlar.
- **Eskimiş Ne Nereye Gider tabloları**: bir `CLAUDE.md` var olmayan dosya ya da klasörleri listeliyor ya da var olanları atlıyor ("ilk kullanımda oluşturulur" diye işaretli satırlar sorun değil).
- **Bilgi blokları**: klasörün `CLAUDE.md` dosyasına göre eksik ya da yarım. `status:` yok, 2'den az `tags:` var, `project:` olmayan bir proje notu, sabit listenin dışında günlük etiketleri.
- **Hareketsiz projeler**: 60 günden uzun süredir güncelleme yok. Bir durum güncellemesi, `paused` ya da arşiv öner.
- **Projesiz hedefler**: `Profil/hedefler.md` içinde aktif projesi olmayan hedefler.
- **Gözden geçirilmesi gereken kararlar**: `updated` 30 günden eski ve durumu `closed` değil.
- **Eski ilişkiler**: `status: active` ama `last-contact` 12 aydan eski. `dormant` öner.
- **Eski görevler**: `Günlük/görevler.md` içinde 30 günden eski açık görevler.
- **Tekrarlar**: aynı bilgiler birden fazla notta ya da aynı kişi veya şirket için iki not.
- **Eskimiş güncel bilgi**: eski güncellemelerin güncel durumu gömdüğü Profil ya da Kişiler sayfaları (ana kural 17).
- **Kural çatışmaları**: kök `CLAUDE.md` içinde birbiriyle çelişen kurallar.
- **Gizlilik**: sıradan notlarda duran şifreler, anahtarlar ya da özel numaralar (ana kurallar 25 ve 26). Notu bildir, değeri asla yazma.
- **Yazı**: notlardaki uzun tireler ve Yazı Kontrolü kalıpları.
- **Yeni sürüm**: bu beynin sürümünü (kök `CLAUDE.md` dosyasının ilk satırı) en yeni Phygital Brain ile karşılaştır. Web'e bakabiliyorsan en yenisi https://github.com/Phygital-Brain/phygital-brain/releases/latest adresindeki son sürümdür. Bakamıyorsan ve asistanında yüklü Phygital Brain sürümünü görebiliyorsan onu kullan. Anlayamıyorsan bu adımı atla.

## 2. Rapor

Yukarıdaki gruplara göre, sade bir dille kısa bir liste. Her sorun için: not, neyin yanlış olduğu, önerdiğin düzeltme. Basit ve güvenli düzeltmeleri başa koy (uzun tireler, eksik etiketler, Ne Nereye Gider tablosu satırları).

Daha yeni bir sürüm çıktıysa raporu tek satırla başlat. Asistanında zaten varsa: "Phygital Brain'in yeni bir sürümü çıktı. Nelerin yeni olduğunu görmek için 'ikinci beynimi güncelle' ('Upgrade my second brain') de." Yoksa: "Phygital Brain'in yeni bir sürümü çıktı. Önce asistanında güncelle, sonra 'ikinci beynimi güncelle' de."

## 3. Sadece onaylananı düzelt

İlk düzeltmeden önce değiştireceğin her dosyanın yedeğini al (kök `CLAUDE.md` içinde Yedekler ve Geri Alma).

Sor (mümkünse tıklanabilir seçeneklerle): **Güvenli olanların hepsini düzelt**, **Tek tek git**, **Sadece rapor**.

- Bağlantı kontrolü ve net bir evet olmadan asla silme ya da taşıma (ana kural 21).
- Emin değilsen silmek yerine arşivle.
- Bugünün `Günlük/` notuna tek satır yaz: neler kontrol edildi ve düzeltildi.
