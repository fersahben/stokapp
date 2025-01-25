# Stok Yönetim Sistemi

Modern ve kullanıcı dostu bir stok yönetim uygulaması. Barkod okuma, Excel entegrasyonu ve resim yönetimi özellikleri ile stok takibini kolaylaştırır.

## Özellikler

### Temel Özellikler
- Ürün ekleme, düzenleme ve silme
- Barkod tarama ile hızlı ürün arama ve miktar artırma
- Excel ile toplu ürün içe/dışa aktarma
- Ürün resmi yükleme ve görüntüleme
- Anlık arama filtreleme
- Mobil uyumlu responsive tasarım

### Barkod Özellikleri
- Kamera ile barkod tarama (mobil cihaz desteği)
- Otomatik barkod oluşturma
- Libre Barcode 128 fontu ile görsel barkod gösterimi
- EAN-13 formatı desteği

### Excel İşlemleri
- Ürünleri Excel'e aktarma
- Excel'den ürün yükleme
- Resim verilerini base64 formatında saklama
- Otomatik resim dönüştürme ve geri yükleme

### Stok Takibi
- Toplam ürün sayısı istatistikleri
- Toplam ürün miktarı takibi
- Toplam stok değeri hesaplama

## Kurulum

1. Gerekli Python paketlerini yükleyin:
```bash
pip install -r requirements.txt
```

2. Veritabanını oluşturun:
```python
from app import db
db.create_all()
```

3. Uygulamayı başlatın:
```bash
python app.py
```

## Kullanım

### Ürün Ekleme
1. "Yeni Ürün" butonuna tıklayın
2. Barkodu manuel girin veya "Barkod Tara" ile otomatik okutun
3. Ürün bilgilerini doldurun
4. İsterseniz ürün fotoğrafı ekleyin
5. Kaydet butonuna basın

### Barkod Tarama
1. Ana sayfada "Barkod Tara" butonuna tıklayın
2. Kamera izni verin
3. Barkodu kameraya gösterin
4. Barkod otomatik okunacak ve işlem yapılacaktır

### Excel İşlemleri
1. **Dışa Aktarma**
   - "Excel İndir" butonuna tıklayın
   - Tüm ürünler ve resimleri Excel dosyasına kaydedilecektir

2. **İçe Aktarma**
   - "Excel Yükle" butonuna tıklayın
   - Excel dosyanızı seçin
   - Ürünler ve resimler otomatik içe aktarılacaktır

## Güvenlik Notları
- Debug modunu production ortamında kapatın
- SECRET_KEY değerini değiştirin
- Yüklenen dosya boyutlarını kontrol edin
- Hassas verileri SSL/TLS ile koruyun

## Mobil Kullanım
- Uygulama mobil tarayıcılarda tam uyumlu çalışır
- Kamera erişimi için HTTPS gerekebilir
- Arka kamera otomatik tercih edilir
- Responsive tasarım ile tüm ekranlarda uyumlu görüntüleme

## Lisans
MIT License

## İletişim
Sorun ve önerileriniz için Issues bölümünü kullanabilirsiniz. 