import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file, make_response
from flask_bootstrap import Bootstrap
from werkzeug.utils import secure_filename
import cv2
from pyzbar.pyzbar import decode
import numpy as np
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
import random
import base64
import time

app = Flask(__name__, static_folder='static', static_url_path='/static')
bootstrap = Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stok.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'gizli-anahtar-buraya'  # Güvenlik için değiştirin
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max-limit

# Veritabanı başlatma
db = SQLAlchemy(app)

# Yükleme klasörünü oluştur
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Ürün modeli
class Urun(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    barkod = db.Column(db.String(50), unique=True, nullable=False)
    ad = db.Column(db.String(100), nullable=False)
    miktar = db.Column(db.Integer, nullable=False)
    fiyat = db.Column(db.Float, nullable=False)
    resim_url = db.Column(db.String(200))
    eklenme_tarihi = db.Column(db.DateTime, default=datetime.utcnow)

def barkod_formatla(barkod):
    # Barkodu sadece sayılara indir
    barkod = ''.join(filter(str.isdigit, str(barkod)))
    
    # 12 haneye tamamla (soldan sıfırlarla)
    barkod = barkod.zfill(12)
    
    # İlk 12 haneyi al
    barkod = barkod[:12]
    
    return barkod

# Barkod oluşturma
@app.route('/barkod/<barkod>')
def barkod_olustur(barkod):
    try:
        # Barkodu formatla
        barkod = barkod_formatla(barkod)
        
        # EAN13 barkod oluştur
        EAN = barcode.get_barcode_class('ean13')
        ean = EAN(barkod, writer=ImageWriter())
        
        # Barkod yazıcı ayarları
        options = {
            'module_width': 0.4,    # Çubuk genişliği
            'module_height': 15.0,  # Çubuk yüksekliği
            'quiet_zone': 6.0,      # Kenar boşluğu
            'font_size': 10,        # Yazı boyutu
            'text_distance': 5.0,   # Metin mesafesi
            'background': 'white',  # Arka plan rengi
            'foreground': 'black',  # Çubuk rengi
            'write_text': True,     # Barkod numarasını göster
            'dpi': 300             # Çözünürlük
        }
        
        # Barkodu bir BytesIO nesnesine kaydet
        buffer = BytesIO()
        ean.write(buffer, options=options)
        
        # Response oluştur
        buffer.seek(0)
        response = make_response(buffer.getvalue())
        response.mimetype = 'image/png'
        
        # Cache kontrolü ve CORS başlıkları
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET'
        
        return response
        
    except Exception as e:
        print(f"Barkod oluşturma hatası: {str(e)}")
        return '', 404

# Ana sayfa ve ürün listesi
@app.route('/')
def urun_listesi():
    urunler = Urun.query.order_by(Urun.eklenme_tarihi.desc()).all()
    
    # Toplam değerleri hesapla
    toplam_urun_sayisi = len(urunler)
    toplam_urun_miktari = sum(urun.miktar for urun in urunler)
    toplam_stok_degeri = sum(urun.miktar * urun.fiyat for urun in urunler)
    
    return render_template('urun_listesi.html', 
                         urunler=urunler,
                         toplam_urun_sayisi=toplam_urun_sayisi,
                         toplam_urun_miktari=toplam_urun_miktari,
                         toplam_stok_degeri=toplam_stok_degeri)

def generate_unique_barcode():
    while True:
        # 12 haneli rastgele bir sayı oluştur
        random_barcode = ''.join([str(random.randint(0, 9)) for _ in range(12)])
        
        # Bu barkod zaten kullanılmış mı kontrol et
        if not Urun.query.filter_by(barkod=random_barcode).first():
            return random_barcode

# Yeni ürün ekleme
@app.route('/urun/ekle', methods=['GET', 'POST'])
def urun_ekle():
    if request.method == 'POST':
        try:
            # Form verilerini al
            barkod = request.form['barkod'].strip()
            ad = request.form['ad']
            miktar = int(request.form['miktar'])
            fiyat = float(request.form['fiyat'])
            
            # Eğer barkod boşsa, otomatik oluştur
            if not barkod:
                barkod = generate_unique_barcode()
            
            # Resim yükleme
            resim_url = None
            if 'resim' in request.files:
                resim = request.files['resim']
                if resim.filename:
                    filename = secure_filename(f"{datetime.now().timestamp()}_{resim.filename}")
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    resim.save(filepath)
                    resim_url = f"uploads/{filename}"
            
            # Yeni ürün oluştur
            yeni_urun = Urun(
                barkod=barkod,
                ad=ad,
                miktar=miktar,
                fiyat=fiyat,
                resim_url=resim_url
            )
            
            db.session.add(yeni_urun)
            db.session.commit()
            
            flash(f'Ürün başarıyla eklendi. Barkod: {barkod}', 'success')
            return redirect(url_for('urun_listesi'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Ürün eklenirken bir hata oluştu: {str(e)}', 'danger')
    
    # GET isteği için barkod parametresini al
    barkod = request.args.get('barkod', '')
    return render_template('urun_ekle.html', barkod=barkod)

# Ürün düzenleme
@app.route('/urun/duzenle/<int:id>', methods=['GET', 'POST'])
def urun_duzenle(id):
    urun = Urun.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            # Form verilerini al
            urun.barkod = request.form['barkod']
            urun.ad = request.form['ad']
            urun.miktar = int(request.form['miktar'])
            urun.fiyat = float(request.form['fiyat'])
            
            # Resim yükleme
            if 'resim' in request.files:
                resim = request.files['resim']
                if resim.filename:
                    # Eski resmi sil
                    if urun.resim_url:
                        eski_resim_yolu = os.path.join('static', urun.resim_url)
                        if os.path.exists(eski_resim_yolu):
                            os.remove(eski_resim_yolu)
                    
                    # Yeni resmi kaydet
                    filename = secure_filename(f"{datetime.now().timestamp()}_{resim.filename}")
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    resim.save(filepath)
                    urun.resim_url = f"uploads/{filename}"
            
            db.session.commit()
            flash('Ürün başarıyla güncellendi.', 'success')
            return redirect(url_for('urun_listesi'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Ürün güncellenirken bir hata oluştu: {str(e)}', 'danger')
    
    return render_template('urun_duzenle.html', urun=urun)

# Ürün silme
@app.route('/urun/<int:id>/sil', methods=['POST'])
def urun_sil(id):
    try:
        urun = Urun.query.get_or_404(id)
        
        # Ürün resmini sil
        if urun.resim_url:
            resim_yolu = os.path.join('static', urun.resim_url)
            if os.path.exists(resim_yolu):
                os.remove(resim_yolu)
        
        db.session.delete(urun)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Barkod tarama
@app.route('/barkod/tara', methods=['POST'])
def barkod_tara():
    if 'image' not in request.files:
        return jsonify({'error': 'Resim bulunamadı'}), 400
    
    try:
        # Resmi oku
        image_file = request.files['image']
        nparr = np.frombuffer(image_file.read(), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Görüntü iyileştirme
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Farklı eşik değerleri dene
        thresholds = [
            cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1],
            cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2),
            gray  # Orijinal gri görüntü
        ]
        
        # Her eşik değeri için barkod tarama
        for thresh in thresholds:
            barcodes = decode(thresh)
            if barcodes:
                # İlk bulunan barkodu döndür
                barcode = barcodes[0]
                barkod = barcode.data.decode('utf-8')
                
                # Barkodu formatla
                barkod = barkod_formatla(barkod)
                
                return jsonify({'barkod': barkod})
        
        return jsonify({'error': 'Barkod bulunamadı'}), 404
        
    except Exception as e:
        print(f"Barkod tarama hatası: {str(e)}")  # Hata ayıklama için
        return jsonify({'error': str(e)}), 500

# Excel indirme
@app.route('/excel/indir')
def excel_indir():
    try:
        # Tüm ürünleri al
        urunler = Urun.query.all()
        
        # DataFrame oluştur
        df = pd.DataFrame([{
            'Barkod': urun.barkod,
            'Ürün Adı': urun.ad,
            'Miktar': urun.miktar,
            'Fiyat': urun.fiyat,
            'Resim': ''
        } for urun in urunler])
        
        # Resimleri base64'e çevir ve DataFrame'e ekle
        for i, urun in enumerate(urunler):
            if urun.resim_url and os.path.exists(os.path.join('static', urun.resim_url)):
                with open(os.path.join('static', urun.resim_url), 'rb') as img_file:
                    img_data = img_file.read()
                    base64_img = base64.b64encode(img_data).decode('utf-8')
                    df.at[i, 'Resim'] = f"data:image/jpeg;base64,{base64_img}"
            else:
                df.at[i, 'Resim'] = 'NO_IMAGE'
        
        # Excel dosyasını oluştur
        excel_path = os.path.join('static/temp', 'urunler.xlsx')
        os.makedirs('static/temp', exist_ok=True)
        df.to_excel(excel_path, index=False)
        
        return send_file(
            excel_path,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='urunler.xlsx'
        )
        
    except Exception as e:
        flash(f'Excel dosyası oluşturulurken bir hata oluştu: {str(e)}', 'danger')
        return redirect(url_for('urun_listesi'))

# Excel yükleme
@app.route('/excel/yukle', methods=['POST'])
def excel_yukle():
    try:
        if 'excel_file' not in request.files:
            flash('Excel dosyası seçilmedi', 'danger')
            return redirect(url_for('urun_listesi'))
        
        file = request.files['excel_file']
        if file.filename == '':
            flash('Dosya seçilmedi', 'danger')
            return redirect(url_for('urun_listesi'))
        
        # Excel dosyasını oku
        df = pd.read_excel(file, dtype={'Resim': str})
        
        basarili = 0
        hatali = 0
        
        for _, row in df.iterrows():
            try:
                # Ürün bilgilerini al
                barkod = str(row['Barkod'])
                ad = row['Ürün Adı']
                miktar = int(row['Miktar'])
                fiyat = float(row['Fiyat'])
                
                # Resim verisini al ve kontrol et
                resim_data = str(row.get('Resim', 'NO_IMAGE'))
                if pd.isna(resim_data) or resim_data == 'nan' or resim_data == '' or resim_data == 'None':
                    resim_data = 'NO_IMAGE'
                
                # Mevcut ürünü kontrol et
                urun = Urun.query.filter_by(barkod=barkod).first()
                
                # Resim işleme
                resim_url = None
                if resim_data and resim_data != 'NO_IMAGE':
                    try:
                        # Base64'ten resmi çöz
                        if 'data:image/' in resim_data:
                            # MIME türünü ve base64 verisini ayır
                            mime_type = resim_data.split(';')[0].split(':')[1]
                            base64_data = resim_data.split(',')[1]
                        else:
                            # Sadece base64 verisi var
                            mime_type = 'image/jpeg'  # Varsayılan
                            base64_data = resim_data
                        
                        # Base64 verisini temizle
                        base64_data = base64_data.strip()
                        
                        # Padding kontrolü
                        padding = 4 - (len(base64_data) % 4) if len(base64_data) % 4 != 0 else 0
                        base64_data += '=' * padding
                        
                        try:
                            # Base64'ten resmi çöz
                            img_data = base64.b64decode(base64_data)
                            
                            # Resmi kaydet
                            resim_adi = f"urun_{barkod}_{int(time.time())}.jpg"
                            resim_yolu = os.path.join('static/uploads', resim_adi)
                            os.makedirs('static/uploads', exist_ok=True)
                            
                            with open(resim_yolu, 'wb') as f:
                                f.write(img_data)
                            
                            resim_url = f"uploads/{resim_adi}"
                            print(f"Resim kaydedildi: {resim_url}")
                            
                        except Exception as e:
                            print(f"Base64 çözme hatası: {str(e)}")
                            resim_url = None
                            
                    except Exception as e:
                        print(f"Resim işleme hatası: {str(e)}")
                        resim_url = None
                
                if urun:
                    # Ürün varsa güncelle
                    urun.ad = ad
                    urun.miktar = miktar
                    urun.fiyat = fiyat
                    if resim_url:
                        # Eski resmi sil
                        if urun.resim_url and os.path.exists(os.path.join('static', urun.resim_url)):
                            os.remove(os.path.join('static', urun.resim_url))
                        urun.resim_url = resim_url
                else:
                    # Yeni ürün ekle
                    urun = Urun(
                        barkod=barkod,
                        ad=ad,
                        miktar=miktar,
                        fiyat=fiyat,
                        resim_url=resim_url
                    )
                    db.session.add(urun)
                
                basarili += 1
                
            except Exception as e:
                print(f"Ürün işleme hatası: {str(e)}")
                hatali += 1
                continue
        
        db.session.commit()
        flash(f'{basarili} ürün başarıyla işlendi, {hatali} ürün işlenemedi', 'success' if hatali == 0 else 'warning')
        
    except Exception as e:
        flash(f'Excel dosyası işlenirken bir hata oluştu: {str(e)}', 'danger')
    
    return redirect(url_for('urun_listesi'))

@app.route('/urun/barkod/<barkod>/kontrol')
def urun_barkod_kontrol(barkod):
    urun = Urun.query.filter_by(barkod=barkod).first()
    return jsonify({
        'exists': urun is not None,
        'id': urun.id if urun else None
    })

@app.route('/urun/<int:id>/miktar-artir', methods=['POST'])
def urun_miktar_artir(id):
    urun = Urun.query.get_or_404(id)
    urun.miktar += 1
    db.session.commit()
    return jsonify({'success': True})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True) 