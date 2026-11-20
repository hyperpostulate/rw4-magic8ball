<!-- Dil: [English](README.md) | Türkçe -->

<p align="center">
  <img src="src/common/logo.png" alt="Magic 8 Ball" width="96" height="96">
</p>

<h1 align="center">rw4-magic8ball — Redmi Watch 4 için Magic 8 Ball</h1>

<p align="center">
  <img src="https://img.shields.io/badge/platform-Xiaomi%20Vela-blue" alt="Platform: Xiaomi Vela">
  <img src="https://img.shields.io/badge/device-Redmi%20Watch%204-orange" alt="Cihaz: Redmi Watch 4">
  <img src="https://img.shields.io/badge/version-1.0.0-green" alt="Sürüm 1.0.0">
  <img src="https://img.shields.io/badge/license-GPLv3-blue" alt="Lisans: GPLv3">
</p>

<p align="center">Sorunu sesli sor, ekrana dokun, cevabı al. Redmi Watch 4 için bir Xiaomi Vela hızlı uygulaması.</p>

<p align="center">English version: <a href="README.md">README.md</a></p>

[1950'den beri bilinen](https://en.wikipedia.org/wiki/Magic_8_Ball) Magic 8 Ball oyuncağı, Redmi Watch 4 üzerinde tek ekranlık bir `.rpk` olarak yeniden yapıldı. Klasik 20 cevabın tamamı uygulamanın içinde ve eşit olasılıkla seçiliyor. [rw4-poc](https://github.com/hyperpostulate/rw4-poc) şablonu üzerine kurulu olduğu için cihazın gerçekten izin verdiği sınırların içinde kalıyor: metin çizimi yok, canvas yok, ağ yok.

* * *

## İçindekiler

- [Ne yapıyor](#ne-yapıyor)
- [Saate kurulum](#saate-kurulum)
- [Derleme ve çalıştırma](#derleme-ve-çalıştırma)
- [Proje yapısı](#proje-yapısı)
- [Tasarım](#tasarım)
- [Cihaz üstü bulgular](#cihaz-üstü-bulgular)
- [Sınırlar](#sınırlar)
- [Lisans](#lisans)
- [Geliştirici](#geliştirici)
- [Katkı](#katkı)

* * *

## Ne yapıyor

Tek ekran, üç durum, tek girdi: **ekranın herhangi bir yerine dokun**.

| Durum | Ekran | Titreşim |
| :-- | :-- | :-- |
| **Boşta** | Çelik halkalı lacivert kart ve "8", ipucu `Tap to seek answer…` | — |
| **Dönüyor** (600 ms) | Halka dönen bir yaya dönüşür, 100 ms'de bir 6 kare | dokunuşta kısa titreşim |
| **Cevap** | Kartta 20 cevaptan biri, ipucu `Tap to ask again` | cevap oturunca uzun titreşim |

Cevaplar klasik kümedir: 10 olumlu, 5 kararsız, 5 olumsuz; her biri 1/20 olasılıkla gelir — klasik topun hafızası da yanlılığı da yoktur. Cevabın rengi kategorisini taşır: olumluda beyaza yakın, kararsızda gümüş mavisi, olumsuzda soluk gül.

```
┌───────────────────────────────┐    ┌───────────────────────────────┐
│          MAGIC 8 BALL         │    │          MAGIC 8 BALL         │
│    ╭───────────────────╮      │    │    ╭───────────────────╮      │
│    │                   │      │    │    │                   │      │
│    │       ( 8 )       │      │    │    │  Concentrate      │      │
│    │                   │      │    │    │  and ask again.   │      │
│    ╰───────────────────╯      │    │    ╰───────────────────╯      │
│      Tap to seek answer…      │    │        Tap to ask again       │
└───────────────────────────────┘    └───────────────────────────────┘
```

* * *

## Saate kurulum

`.rpk` dosyası, Android telefondan Bluetooth üzerinden **[Notify for Xiaomi](https://play.google.com/store/apps/details?id=com.mc.xiaomi1)** uygulamasıyla kurulur (paket adı `com.mc.xiaomi1`, geliştirici OneZeroBit). Redmi Watch 4 uygulamanın resmî uyumluluk listesindedir ve uygulamanın resmî sitesi özel VelaJS (`.rpk`) uygulamalarının bu yolla kurulduğunu belgeler.

> **Doğrulama durumu:** gerçek bir Redmi Watch 4 üzerinde tamamen doğrulandı — uygulama kuruluyor, dokunuş boşta→dönüş→cevap akışını sürüyor ve her iki titreşim darbesi de çalışıyor.

> **Her derlemede sürümü artırın.** Notify for Xiaomi ve saat, hızlı uygulama paketlerini `versionName` ve `versionCode` ile önbelleğe alır. İkisi de değişmezse taze `.rpk` yerine önbellekteki derleme kurulabilir. Her derlemeden önce `src/manifest.json` içindeki iki alanı da artırın; `versionName` aynı zamanda çıktı dosya adının parçasıdır, böylece her sürüm ayrı bir dosya olur (`dist/com.hyperpostulate.rw4magic8ball.debug.<versionName>.rpk`).

### Önkoşullar

- Bir **Android telefon** (iOS `.rpk` kuramaz).
- Google Play'den kurulmuş **Notify for Xiaomi**.
- Saatin Notify ile eşleştirilmiş olması: uygulama içindeki kurulum sihirbazı eşleşme (auth) anahtarını Xiaomi hesabınız üzerinden alır, yani Mi Fitness'ın kurulu kalması gerekmez.
- Saatin Bluetooth bağlantısını aynı anda yalnızca bir uygulama tutabilir. Mi Fitness kuruluysa zorla durdurun, "Yakındaki cihazlar" iznini kaldırın veya kaldırın — ancak **Mi Fitness'tan eşleştirmeyi, uygulamayı silmeden önce kesmeyin**.

### Adımlar

1. Paketi derleyin: `npm run build` → `dist/com.hyperpostulate.rw4magic8ball.debug.1.0.0.rpk`.
2. **Notify for Xiaomi** uygulamasını açın.
3. **Device** bölümüne gidin.
4. **Third party app** seçeneğini seçin.
5. `.rpk` dosyasını seçin.
6. Saati telefonun yanında tutun ve yönlendirilen adımları izleyin.
7. Kurulum bitince saatteki uygulama listesinde **Magic 8 Ball** görünür.

### Notlar

- `npm run build` ile üretilen debug imzalı `.rpk` bu uygulama için yeterlidir: Vela sertifikayı yalnızca saat↔telefon Interconnect iletişiminde denetler; bu uygulama onu kullanmıyor.
- Redmi Watch 4 sınırları: en fazla ~20 hızlı uygulama kurulabilir, kurulum için ~87 MB boş alan gerekir.
- Güncelleme için yeni bir `.rpk` derleyip aynı paket adının (`com.hyperpostulate.rw4magic8ball`) üzerine kurun. `package` değerini değiştirmek güncelleme yerine **ayrı** bir uygulama kurar.
- Doğrulanmamış ayrıntılar: `.rpk` kurulumlarını hangi uygulama sürümünün başlattığı ve bu özelliğin (yaklaşık 3 €, tek seferlik) PRO satın alımı gerektirip gerektirmediği resmî olarak belgelenmemiş. Yukarıdaki menü adları İngilizce olanlardır; uygulama yerelleştirilmiştir ancak Türkçe etiketler doğrulanmamıştır.

Kaynaklar: [Notify for Xiaomi VelaJS kurulum kılavuzu](https://mibandnotify.com/xiaomi-mi-band/notify-xms-app-instructions.php) · [Google Play sayfası](https://play.google.com/store/apps/details?id=com.mc.xiaomi1)

* * *

## Derleme ve çalıştırma

| Gereksinim | Sürüm / Not |
| :-- | :-- |
| Node.js | 18+ (v24.12.0 ile denendi) |
| npm | 9+ (11.6.2 ile denendi) |
| Python 3 + Pillow | Yalnızca PNG varlıklarını yeniden üretmek için (`scripts/gen_assets.py`) |
| Android telefon | Yalnızca `.rpk` dosyasını **Notify for Xiaomi** ile saate kurmak için (bkz. [Saate kurulum](#saate-kurulum)) |
| `aiot-toolkit` | `npm install` ile dev bağımlılığı olarak gelir |

```
git clone https://github.com/hyperpostulate/rw4-magic8ball.git
cd rw4-magic8ball
npm install                          # aiot-toolkit zincirini kur
npm run build                        # dist/ içine debug .rpk üret
npm run release                      # release .rpk (imza anahtarları gerekir)
npm run start                        # aiot start --watch (canlı geliştirme)
python3 scripts/gen_assets.py        # PNG varlıklarını koddan yeniden üret
```

Derleme `dist/com.hyperpostulate.rw4magic8ball.debug.1.0.0.rpk` dosyasını üretir. Debug `.rpk` imza gerektirmez; release paketi için `sign/private.pem` ve `sign/certificate.pem` gerekir (OpenSSL ile üretin).

### Cihaz üstü kontrol listesi

Aşağıdaki yedi kontrolün tamamı **gerçek bir Redmi Watch 4 üzerinde geçiyor** (2026-11-20'de doğrulandı). Bir değişiklikten sonra regresyon için listeyi koruyun.

1. Uygulama boşta kartla açılıyor mu (başlık, "8" halkası, `Tap to seek answer…`)? ✅
2. **Dokunuş dönüşü başlatıyor mu?** ✅ Hem `@click` hem `@touchstart` bağlı; çalışma zamanının hangisini yaydığı ayrıştırılmadı, bu yüzden ikisi 350 ms korumanın arkasında bağlı kalıyor.
3. 6 yay karesi canlanıyor ve ~0,7 sn içinde bir cevap geliyor mu? ✅
4. Cevap en fazla 3 satıra sarıyor ve karttan taşmıyor mu? ✅
5. Dokunuşta ve cevap oturunca titreşim geliyor mu? ✅ İki darbe de teyit edildi.
6. İkinci dokunuş yeniden döndürüyor mu, ipucu dönüş sırasında `ask` olarak kalıyor mu? ✅
7. Ekranın yuvarlak köşeleri hiçbir şeyi kırpmıyor mu (başlık, ipucu, kart kenarı)? ✅

* * *

## Proje yapısı

```
rw4-magic8ball/
├── src/
│   ├── manifest.json          # paket com.hyperpostulate.rw4magic8ball, designWidth 390
│   ├── app.ux                 # uygulama girişi (onCreate/onDestroy)
│   ├── common/
│   │   ├── logo.png           # başlatıcı simgesi: lacivert kare + halka + "8", 96x96
│   │   ├── txt/               # başlık + iki ipucu (üretilmiş)
│   │   └── face/              # boşta + 6 dönüş + 20 cevap yüzü (üretilmiş)
│   └── pages/
│       └── index/
│           └── index.ux       # uygulamanın tamamı: 3 görsel, durum makinesi, stiller
├── scripts/
│   ├── gen_assets.py          # 31 PNG'nin yeniden üretilebilir Pillow üreteci
│   └── assets/
│       ├── ui-subset.ttf          # DejaVu Sans Book (yalnızca üretim anında)
│       └── DejaVuSans-Bold.ttf    # yalnızca üretim anında
├── docs/
│   ├── design.md              # arayüz spesifikasyonu: palet, geometri, tipografi, hareket, metinler
│   ├── findings.md            # iki dilli cihaz üstü bulgular (şablondan)
│   ├── development.md         # iki dilli rehber: bu şablondan yeni uygulama geliştirme
│   └── native-development.md  # araştırma: hızlı uygulama ötesinde neler mümkün
├── dist/                      # derleme çıktısı (.rpk) - gitignore
├── build/                     # ara derleme çıktısı - gitignore
├── package.json
├── LICENSE                    # GPLv3 tam metni
├── README.md                  # İngilizce
└── README-TR.md               # Türkçe
```

### Temel dosyalar

| Dosya | Amaç |
| :-- | :-- |
| `src/manifest.json` | Vela manifesti: `package` = `com.hyperpostulate.rw4magic8ball`, `name` = `Magic 8 Ball`, `deviceTypeList: ["watch"]`, `designWidth: 390`, `features: ["system.router", "system.vibrator"]` |
| `src/pages/index/index.ux` | Uygulamanın tamamı: şablon (başlık, yüz, ipucu), boşta→dönüş→cevap durum makinesi, dokunma koruması, zamanlayıcılar, stiller, üretilmiş varlık adları |
| `scripts/gen_assets.py` | Kart yüzlerini, başlığı, ipuçlarını ve simgeyi belirlenimci biçimde üretir; dosya adlarına içerik damgası koyar ve `index.ux` içindeki varlık bloğunu kendisi günceller |
| `docs/design.md` | Yetkili arayüz spesifikasyonu (palet, geometri, tipografi, hareket, metin listesi) |

* * *

## Tasarım

"Gece mavisi minimal": tam siyah zemin, 2 px çelik kenarlı (`#4A6B8A`) tek bir koyu lacivert yuvarlatılmış kart (`#0A192F`), beyaza yakın metin. Taklit küre yok, üçgen yok — topun kendisi karttır.

Her sayı **[docs/design.md](docs/design.md)** içinde. Kısacası:

- Tuval 390×450; içerik y = 398'de biter çünkü kavisli cam köşeleri kırpıyor.
- Başlık (35,34) konumunda 320×34; kart (40,86) konumunda 310×280; ipucu (35,374) konumunda 320×24.
- Kartın içindeki cevap kutusu 242×184, 30 px DejaVu Sans Book, 38 px satır yüksekliği, sözcük bazlı sarma, en fazla 3 satır — herhangi bir cevap taşarsa üreteç 28/26 px'e iner ve bloğun sığdığını doğrular.
- 31 PNG, ekranda 3 `<image>` düğümü.

### Neden her şey PNG

Redmi Watch 4'ün Vela çalışma zamanı **okunabilir metin çizmiyor**: `<text>`, `<span>` ve `<input>` hiçbir şey ya da tofu kutuları basıyor; paketlenen `@font-face` etkisiz. `<image>` ise sorunsuz çiziliyor. Bu yüzden her görünür yazı `scripts/gen_assets.py` tarafından önceden üretilir ve kart yüzü (dolgu + kenar + cevap metni) tek bir görselde birleştirilir; bu da ekrandaki düğüm sayısını üçte tutar.

Saat görselleri **yol bazında** önbelleğe aldığı için varlık adları içerik damgası taşır (`ans00_81d7cf41.png`). Metni düzenlemek damgayı değiştirir, böylece yeni derleme eski pikselleri çizemez.

* * *

## Cihaz üstü bulgular

**Gerçek bir Redmi Watch 4** üzerinde doğrulandı. Tamamı — sistem API tablosu dahil — **[docs/findings.md](docs/findings.md)** içinde.

- **Metin çizilmiyor.** Her görünür yazı önceden üretilmiş bir PNG olmak zorunda.
- **Hangi sistem API'leri çalışıyor.** `@system.device`, `@system.storage`, `@system.brightness`, `@system.app`, `@system.vibrator` ve JS saati çalışıyor; geolocation (GPS, hata `203`), sensor, battery, network, bluetooth, record, fetch ve crypto çalışmıyor.
- **Canvas saati çökertiyor** — siyah ekran, ardından çalışma zamanı yeniden başlaması. Tek seçenek `<image>` çizici.
- **Simge boyutu uygulama adını kaydırıyor**: **96×96** `logo.png` bilinçli (`192×192` etiketi satırın ortasına itiyordu).
- **Dokunma girdisi ve titreşim doğrulandı.** `@click` ve `@touchstart` 350 ms korumanın arkasında tek işleyiciye bağlı — çalışma zamanı dokunuşları güvenilir teslim ediyor, ancak iki olay adından *hangisini* yaydığı ayrıştırılmadı, bu yüzden ikisi bağlı kalıyor. `vibrator.vibrate()` kısa (dokunuş) ve uzun (cevap) darbenin ikisini de üretiyor.

* * *

## Sınırlar

- **Ağ, GPS, sensör yok.** Cevaplar sabit yerel bir listedir; hiçbir şey indirilmez veya ortamdan hesaplanmaz.
- **Metin görsel olmak zorunda.** Cevap eklemek ya da düzenlemek `scripts/gen_assets.py` içindeki `ANSWERS` listesini değiştirmek, üreteci çalıştırmak ve yeniden derlemek demektir — metin dizgi olarak değil, PNG olarak derlenir.
- **Tek girdi mekanizması.** Yalnızca dokunma; ayar ekranı, geçmiş, ses yok.
- **Arka plan yürütme yok.** Uygulama kapalıyken hiçbir şey çalışmaz.
- **`npm audit`**, `aiot-toolkit`'in dolaylı dev bağımlılıklarında güvenlik açıkları raporlar. Yalnızca derleme zamanı; `.rpk` içinde hiçbir şey taşınmaz.

* * *

## Lisans

Bu proje **GNU Genel Kamu Lisansı v3.0 (GPL-3.0)** ile lisanslanmıştır — tam metin için [LICENSE](LICENSE) dosyasına bakın. [hyperpostulate/rw4-poc](https://github.com/hyperpostulate/rw4-poc) türevi olduğu için GPLv3 olarak kalır.

* * *

## Geliştirici

**Mesut ORMANLI**

- E-posta: [mesutormanli@gmail.com](mailto:mesutormanli@gmail.com)
- GitHub: [@hyperpostulate](https://github.com/hyperpostulate)

* * *

## Katkı

1. Depoyu forklayın
2. Bir özellik dalı açın (`git checkout -b feature/yeni-ozellik`)
3. Değişikliklerinizi işleyin (`git commit -m 'Yeni özellik ekle'`)
4. Dalı gönderin (`git push origin feature/yeni-ozellik`)
5. Bir Pull Request açın
