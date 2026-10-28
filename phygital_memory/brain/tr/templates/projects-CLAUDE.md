Her proje, bilgi geldikçe büyüyen bir klasördür. Tek giriş noktası `README.md` dosyasıdır.

## Ne nereye gider

| İçerik | Gideceği yer |
|---|---|
| Genel bakış, durum, son tarih, sıradaki adımlar | `Projeler/{name}/README.md` |
| {Name} tarafından tutulan çalışma notları | `Projeler/{name}/notlar/{topic}.md` |
| Araştırma | `Projeler/{name}/araştırmalar/{topic}.md` |
| Brif, şartname, gereksinimler | `Projeler/{name}/brifler/{name}.md` |
| Taslaklar, senaryolar, yazılı içerik | `Projeler/{name}/taslaklar/{name}.md` |
| Fikirler | `Projeler/{name}/fikirler/{name}.md` |
| Geri bildirim | `Projeler/{name}/geri-bildirim/{name}.md` |
| Resimler ve medya | `Projeler/{name}/medya/` |
| Bu projeden kalan eski malzemeler | `Projeler/{name}/arşiv/` |

Klasör adları küçük harfle, kelimeler arasında tireyle yazılır, başlarında numara olmaz (`araştırmalar/`, `01-Research/` değil). Bunların hiçbiri uymazsa bir proje kendi klasörünü ekleyebilir.

## README düzeni

1. Bilgi bloğu (aşağıda), bir `description` ile.
2. `## Nedir`: bir ya da iki satır, [[hedefler]] notuna bağlantıyla.
3. `## Durum ve sıradaki adım`: nerede olduğu, sıradaki adım.
4. `## Nasıl işliyor`: sadece buraya otomatik yazan bir şey varsa (zamanlanmış bir görev, bir betik).
5. `## Ne nerede`: sadece alt klasörler oluştuktan sonra. Her birine bağlantı veren küçük bir tablo.

## Bilgi bloğu (frontmatter)

```yaml
---
type: notes
date: 2026-10-13
status: active
project: Website-Redesign
tags: [website-redesign, notes]
---
```

- `type`: `project` (README; onda ayrıca `created`, `updated` ve `description` olur), `notes`, `research`, `brief`, `draft`, `idea`, `feedback`, `plan`.
- `status`: `active`, `paused` ya da `done`. README'nin durumu projenin durumudur.
- `project`: proje klasörünün adı.
- `tags`: önce proje, sonra tür.

## Kurallar

- Yeni bir proje sadece bir `README.md` dosyasıdır. Alt klasörleri ancak onlara ihtiyaç duyan içerik geldiğinde oluştur ve README'den bağlantı ver.
- README bir dizindir. Alt klasörlerdeki içeriği orada tekrarlama.
- Bir projenin içinde `CLAUDE.md` olmaz. Tek bir projeye özel kurallar aşağıdaki "Projeye özel kurallar" bölümüne gider.
- İlgili her notun bilgi bloğuna `project:` ekle.
- Biten bir proje `Hafıza/arşiv/{name}/` içine ancak {Name} söylerse taşınır.
- Her proje [[hedefler]] içindeki bir hedefe hizmet etmeli. Genel kontrolde projesi olmayan hedefleri ve hedefi olmayan projeleri işaretle.

## Projeye özel kurallar

<!-- Sadece tek bir projeye özel kurallar. Bir projenin kendi kuralı gerektiğinde bir satır ekle: "**Proje-Adı:** kural." -->
