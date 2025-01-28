from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import Integer, String, Float, DateTime
from datetime import datetime
import os
import pandas as pd
from PIL import Image
from pyzbar.pyzbar import decode

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stok.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'gizli-anahtar-buraya'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max-limit

db = SQLAlchemy(app)

# Ürün modeli
class Urun(db.Model):
    id = Column(Integer, primary_key=True)
    barkod = Column(String(50), unique=True, nullable=False)
    ad = Column(String(100), nullable=False)
    miktar = Column(Integer, nullable=False)
    fiyat = Column(Float, nullable=False)
    eklenme_tarihi = Column(DateTime, default=datetime.utcnow)

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

# Otomatik barkod oluştur
def yeni_barkod_olustur():
    son_urun = Urun.query.order_by(Urun.id.desc()).first()
    if son_urun:
        # Son ürünün ID'sini al ve 1 artır
        yeni_id = son_urun.id + 1
    else:
        # İlk ürün için başlangıç değeri
        yeni_id = 1
    
    # 13 haneli barkod oluştur (örnek: 2000000000001)
    return f"2{str(yeni_id).zfill(12)}"

# Yeni ürün ekleme
@app.route('/urun/ekle', methods=['GET', 'POST'])
def urun_ekle():
    if request.method == 'POST':
        try:
            barkod = request.form['barkod'].strip()
            ad = request.form['ad']
            miktar = int(request.form['miktar'])
            fiyat = float(request.form['fiyat'])
            
            # Barkod boş ise otomatik oluştur
            if not barkod:
                barkod = yeni_barkod_olustur()
            
            # Barkod kontrolü
            if Urun.query.filter_by(barkod=barkod).first():
                flash('Bu barkod numarası zaten kullanılıyor.', 'danger')
                return render_template('urun_ekle.html')
            
            yeni_urun = Urun(
                barkod=barkod,
                ad=ad,
                miktar=miktar,
                fiyat=fiyat
            )
            
            db.session.add(yeni_urun)
            db.session.commit()
            
            flash('Ürün başarıyla eklendi.', 'success')
            return redirect(url_for('urun_listesi'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Ürün eklenirken bir hata oluştu: {str(e)}', 'danger')
    
    return render_template('urun_ekle.html')

# Ürün düzenleme
@app.route('/urun/duzenle/<int:id>', methods=['GET', 'POST'])
def urun_duzenle(id):
    urun = Urun.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            yeni_barkod = request.form['barkod']
            
            # Barkod değişmişse ve yeni barkod başka bir üründe kullanılıyorsa
            if yeni_barkod != urun.barkod and Urun.query.filter_by(barkod=yeni_barkod).first():
                flash('Bu barkod numarası zaten kullanılıyor.', 'danger')
                return render_template('urun_duzenle.html', urun=urun)
            
            urun.barkod = yeni_barkod
            urun.ad = request.form['ad']
            urun.miktar = int(request.form['miktar'])
            urun.fiyat = float(request.form['fiyat'])
            
            db.session.commit()
            flash('Ürün başarıyla güncellendi.', 'success')
            return redirect(url_for('urun_listesi'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Ürün güncellenirken bir hata oluştu: {str(e)}', 'danger')
    
    return render_template('urun_duzenle.html', urun=urun)

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
            'Toplam Değer': urun.miktar * urun.fiyat
        } for urun in urunler])
        
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
        df = pd.read_excel(file)
        
        basarili = 0
        hatali = 0
        
        for _, row in df.iterrows():
            try:
                # Ürün bilgilerini al
                barkod = str(row['Barkod'])
                ad = row['Ürün Adı']
                miktar = int(row['Miktar'])
                fiyat = float(row['Fiyat'])
                
                # Mevcut ürünü kontrol et
                urun = Urun.query.filter_by(barkod=barkod).first()
                
                if urun:
                    # Ürün varsa güncelle
                    urun.ad = ad
                    urun.miktar = miktar
                    urun.fiyat = fiyat
                else:
                    # Yeni ürün ekle
                    urun = Urun(
                        barkod=barkod,
                        ad=ad,
                        miktar=miktar,
                        fiyat=fiyat
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

# Barkod tarama
@app.route('/barkod/tara', methods=['POST'])
def barkod_tara():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'Görüntü bulunamadı'}), 400
            
        image_file = request.files['image']
        # Dosyayı geçici olarak kaydet
        temp_path = os.path.join('static/temp', 'temp_barcode.jpg')
        os.makedirs('static/temp', exist_ok=True)
        image_file.save(temp_path)
        
        # Kaydedilen dosyayı aç ve işle
        image = Image.open(temp_path)
        
        # Görüntüyü gri tonlamaya çevir
        gray_image = image.convert('L')
        
        # Barkodu tara
        barcodes = decode(gray_image)
        
        # Geçici dosyayı sil
        os.remove(temp_path)
        
        if barcodes:
            barkod = barcodes[0].data.decode('utf-8')
            return jsonify({'barkod': barkod})
        else:
            return jsonify({'error': 'Barkod bulunamadı'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Barkod kontrolü
@app.route('/urun/barkod/<barkod>/kontrol')
def urun_barkod_kontrol(barkod):
    urun = Urun.query.filter_by(barkod=barkod).first()
    if urun:
        return jsonify({
            'exists': True,
            'id': urun.id,
            'ad': urun.ad,
            'miktar': urun.miktar,
            'fiyat': urun.fiyat
        })
    return jsonify({'exists': False})

# Ürün miktarını artır
@app.route('/urun/<int:id>/miktar-artir', methods=['POST'])
def urun_miktar_artir(id):
    try:
        urun = Urun.query.get_or_404(id)
        urun.miktar += 1
        db.session.commit()
        return jsonify({'success': True, 'yeni_miktar': urun.miktar})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Ürün silme
@app.route('/urun/sil/<int:id>', methods=['POST'])
def urun_sil(id):
    try:
        urun = Urun.query.get_or_404(id)
        db.session.delete(urun)
        db.session.commit()
        flash('Ürün başarıyla silindi.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Ürün silinirken bir hata oluştu: {str(e)}', 'danger')
    return redirect(url_for('urun_listesi'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True) 