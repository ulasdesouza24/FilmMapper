# FilmMapper - Film Veri Analizi ve Görselleştirme Projesi

FilmMapper, herhangi bir filmin yapısını, karakterlerini, lokasyonlarını, sahnelerini ve olaylarını analiz etmek ve görselleştirmek için tasarlanmış bir Python uygulamasıdır.

## Proje Hakkında

FilmMapper, filmlerin yapısal analizini kolaylaştırmak için geliştirilmiş bir araçtır. Bu araç sayesinde:

- Film verilerini (karakterler, lokasyonlar, sahneler, ilişkiler, olaylar) sistematik bir şekilde toplayabilir
- Toplanan verileri görselleştirebilir
- Filmin yapısını, karakter ilişkilerini ve hikaye akışını analiz edebilirsiniz

## Sistem Bileşenleri

Proje üç ana bileşenden oluşmaktadır:

1. **Veri Yapısı Tanımı (`film_veri_yapisi.py`)**: Film, karakter, lokasyon, sahne, ilişki ve olay sınıflarını içerir.
2. **Veri Toplama Aracı (`veri_toplama_araci.py`)**: Kullanıcı dostu bir arayüz ile film verilerini toplamak için kullanılır.
3. **Veri Analizi ve Görselleştirme (`film_analiz.py`)**: Toplanan verileri analiz eder ve çeşitli görselleştirmeler oluşturur.

## Kurulum

### Gereksinimler

Projeyi çalıştırmak için aşağıdaki Python kütüphanelerine ihtiyacınız vardır:

```bash
pip install numpy matplotlib seaborn networkx pandas bokeh plotly

### Kurulum Adımları

1. Bu depoyu klonlayın:

```shellscript
git clone https://github.com/kullaniciadi/film-veri-analizi.git
cd film-veri-analizi
```


2. Gerekli kütüphaneleri yükleyin:

```shellscript
pip install -r requirements.txt
```




## Kullanım

### 1. Veri Toplama

Veri toplama aracını başlatmak için:

```shellscript
python veri_toplama_araci.py
```

Bu araç ile:

- Film bilgilerini (başlık, süre) girebilirsiniz
- Karakterleri ekleyebilir ve özelliklerini tanımlayabilirsiniz
- Lokasyonları ekleyebilirsiniz
- Sahneleri, başlangıç ve bitiş zamanları, lokasyonları ve karakterleri ile tanımlayabilirsiniz
- Karakterler arasındaki ilişkileri tanımlayabilirsiniz
- Önemli olayları kaydedebilirsiniz


### 2. Veri Analizi ve Görselleştirme

Toplanan verileri analiz etmek ve görselleştirmek için:

```shellscript
python film_analiz.py dosya_adi.json
```

Bu komut, belirtilen JSON dosyasındaki film verilerini yükleyecek ve aşağıdaki görselleştirmeleri oluşturacaktır:

#### Temel Görselleştirmeler

1. **Karakter Ağı**: Karakterler arasındaki ilişkileri gösteren bir ağ grafiği
2. **Sahne Zaman Çizelgesi**: Sahnelerin zaman içindeki dağılımını gösteren bir çizelge
3. **Lokasyon Kullanım Grafiği**: Lokasyonların film boyunca ne kadar kullanıldığını gösteren bir grafik
4. **Karakter Ekran Süresi**: Her karakterin ekranda ne kadar süre göründüğünü gösteren bir grafik
5. **Olay Zaman Çizelgesi**: Önemli olayların zaman içindeki dağılımını gösteren bir çizelge


#### İleri Düzey Görselleştirmeler

1. **Duygusal Yoğunluk Grafiği**: Film boyunca duygusal yoğunluğun nasıl değiştiğini gösteren bir grafik
2. **Karakter Etkileşim Isı Haritası**: Karakterlerin birbirleriyle ne kadar etkileşimde bulunduğunu gösteren bir ısı haritası
3. **Karakter Yörüngeleri**: Karakterlerin film boyunca hangi lokasyonlarda bulunduğunu gösteren bir yörünge grafiği
4. **Üç Perde Yapısı Analizi**: Filmin klasik üç perde yapısına göre analizini gösteren bir görselleştirme
5. **Karakter Gelişim Grafiği**: Karakterlerin film boyunca gelişimini gösteren bir grafik
6. **Tema Analizi Grafiği**: Filmdeki temaların zaman içindeki dağılımını gösteren bir grafik
7. **Paralel Hikaye Çizgileri Analizi**: Filmdeki paralel hikaye çizgilerini gösteren bir grafik
8. **Görsel Stil Analizi**: Filmin görsel stilini analiz eden bir grafik
9. **İnteraktif Zaman Çizelgesi**: Fare ile üzerine gelindiğinde detayları görebileceğiniz interaktif bir zaman çizelgesi
10. **3D Karakter-Lokasyon-Zaman Grafiği**: Karakterlerin zaman içinde lokasyonlar arasındaki hareketini üç boyutlu olarak görselleştiren bir grafik


## Örnek Kullanım

1. Veri toplama aracını başlatın:

```shellscript
python veri_toplama_araci.py
```


2. "Film Oluştur" butonuna tıklayarak yeni bir film oluşturun
3. Karakterler, lokasyonlar, sahneler, ilişkiler ve olaylar ekleyin
4. "Kaydet" butonuna tıklayarak verileri bir JSON dosyasına kaydedin
5. Analiz ve görselleştirme aracını çalıştırın:

```shellscript
python film_analiz.py film_adi_data.json
```


6. Oluşturulan görselleştirmeleri `output` klasöründe bulabilirsiniz


## Proje Yapısı

```plaintext
film-veri-analizi/
├── film_veri_yapisi.py     # Veri yapısı tanımları
├── veri_toplama_araci.py   # Veri toplama arayüzü
├── film_analiz.py          # Analiz ve görselleştirme aracı
├── kullanim_kilavuzu.py    # Kullanım kılavuzu
├── requirements.txt        # Gerekli kütüphaneler
├── output/                 # Oluşturulan görselleştirmeler
└── README.md               # Bu dosya
```

## Özellikler

- **Kullanıcı Dostu Arayüz**: Veri toplama aracı, film verilerini kolayca girmenizi sağlayan sezgisel bir arayüz sunar
- **Kapsamlı Veri Modeli**: Film, karakter, lokasyon, sahne, ilişki ve olay sınıfları ile kapsamlı bir veri modeli
- **Çeşitli Görselleştirmeler**: Filmin yapısını, karakter ilişkilerini ve hikaye akışını analiz etmek için çeşitli görselleştirmeler
- **Veri Kaydetme ve Yükleme**: Verileri JSON formatında kaydedebilir ve daha sonra yükleyebilirsiniz
- **İnteraktif Görselleştirmeler**: Bazı görselleştirmeler interaktif olup daha detaylı inceleme yapmanıza olanak tanır
