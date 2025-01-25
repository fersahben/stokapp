from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Urun(db.Model):
    __tablename__ = 'urunler'
    
    id = db.Column(db.Integer, primary_key=True)
    barkod = db.Column(db.String(50), unique=True, nullable=False)
    ad = db.Column(db.String(100), nullable=False)
    miktar = db.Column(db.Integer, nullable=False, default=0)
    fiyat = db.Column(db.Float, nullable=False, default=0.0)
    resim_url = db.Column(db.String(500))
    olusturma_tarihi = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    guncelleme_tarihi = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'barkod': self.barkod,
            'ad': self.ad,
            'miktar': self.miktar,
            'fiyat': self.fiyat,
            'resim_url': self.resim_url,
            'olusturma_tarihi': self.olusturma_tarihi.strftime('%Y-%m-%d %H:%M:%S'),
            'guncelleme_tarihi': self.guncelleme_tarihi.strftime('%Y-%m-%d %H:%M:%S')
        } 