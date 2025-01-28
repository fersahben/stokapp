# Stok Takip Uygulaması

Bu uygulama, küçük işletmeler için geliştirilmiş basit ve kullanışlı bir stok takip sistemidir. Mobil cihazlarla uyumlu olup, barkod okuma özelliği ile hızlı ürün girişi ve takibi sağlar.

## Özellikler

- 📱 Mobil uyumlu tasarım
- 📷 Kamera ile barkod okuma
- 🔄 Otomatik barkod oluşturma
- 📊 Stok istatistikleri
- 📥 Excel ile toplu ürün içe aktarma
- 📤 Excel ile ürün dışa aktarma
- 🔍 Anlık ürün arama
- ✏️ Ürün düzenleme ve silme
- 📊 Toplam stok değeri takibi

## Kurulum

### Gereksinimler

- Python 3.8 veya üzeri
- pip (Python paket yöneticisi)
- Kamera erişimi (barkod okuma için)

### Adımlar

1. Projeyi klonlayın:
```bash
git clone https://github.com/kullanici_adi/stok-takip.git
cd stok-takip
```

2. Sanal ortam oluşturun ve aktif edin:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

3. Gerekli paketleri yükleyin:
```bash
pip install -r requirements.txt
```

4. Veritabanını oluşturun:
```bash
python app.py
```

5. Uygulamayı başlatın:
```bash
python app.py
```

Uygulama http://localhost:5000 adresinde çalışmaya başlayacaktır.

## Kullanım

### Yeni Ürün Ekleme
- "Yeni Ürün" butonuna tıklayın
- Barkodu okutun veya manuel girin (boş bırakırsanız otomatik oluşturulur)
- Ürün bilgilerini doldurun
- "Ekle" butonuna tıklayın

### Barkod Okutma
- "Barkod Oku" butonuna tıklayın
- Kamera açıldığında barkodu gösterin
- Barkod okunduğunda otomatik olarak işlem yapılacaktır

### Excel İşlemleri
- Toplu ürün eklemek için Excel şablonunu indirin
- Şablonu doldurup "Excel Yükle" ile içe aktarın
- Mevcut ürünleri dışa aktarmak için "Excel İndir" butonunu kullanın

## Güvenlik

- Uygulama yerel ağda çalışır
- Veritabanı SQLite kullanır
- Hassas veriler şifrelenmez

## Teknik Detaylar

- Flask web framework
- SQLite veritabanı
- Bootstrap 5 arayüz
- JavaScript barkod okuma
- Responsive tasarım

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın. 