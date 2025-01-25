import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Box,
  Grid,
  Alert,
  CircularProgress,
} from '@mui/material';
import Quagga from 'quagga';
import { db } from '../firebase';
import { collection, addDoc } from 'firebase/firestore';
import { cloudinary, uploadPreset } from '../cloudinary';

function UrunEkle() {
  const navigate = useNavigate();
  const [urun, setUrun] = useState({
    barkod: '',
    ad: '',
    miktar: '',
    fiyat: '',
    resim: null
  });
  const [yukleniyor, setYukleniyor] = useState(false);
  const [kameraAktif, setKameraAktif] = useState(false);
  const [kameraHata, setKameraHata] = useState('');
  const [islemDurumu, setIslemDurumu] = useState({ tip: '', mesaj: '' });
  const videoRef = useRef(null);
  const dosyaInputRef = useRef(null);
  const cloudinaryRef = useRef();
  const widgetRef = useRef();

  useEffect(() => {
    cloudinaryRef.current = window.cloudinary;
    widgetRef.current = cloudinaryRef.current.createUploadWidget(
      {
        cloudName: cloudinary.config().cloud_name,
        uploadPreset: uploadPreset,
        maxFiles: 1,
        maxFileSize: 5000000, // 5MB
        sources: ['local', 'camera'],
        resourceType: 'image'
      },
      function(error, result) {
        if (!error && result && result.event === "success") {
          setUrun(prev => ({
            ...prev,
            resim: result.info.secure_url
          }));
          setIslemDurumu({
            tip: 'success',
            mesaj: 'Fotoğraf başarıyla yüklendi.'
          });
        }
      }
    );

    return () => {
      if (Quagga.initialized) {
        Quagga.stop();
      }
    };
  }, []);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setUrun(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleResimSecimi = () => {
    widgetRef.current.open();
  };

  const baslatBarkodOkuyucu = async () => {
    setKameraHata('');
    setKameraAktif(true);

    try {
      await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } });

      Quagga.init({
        inputStream: {
          name: "Live",
          type: "LiveStream",
          target: videoRef.current,
          constraints: {
            facingMode: "environment",
            width: 640,
            height: 480,
          },
          area: {
            top: "0%",
            right: "0%",
            left: "0%",
            bottom: "0%"
          },
        },
        decoder: {
          readers: [
            "ean_reader",
            "ean_8_reader",
            "code_128_reader",
            "code_39_reader",
            "upc_reader",
            "upc_e_reader"
          ]
        }
      }, function(err) {
        if (err) {
          console.error(err);
          setKameraHata('Kamera başlatılamadı: ' + err.message);
          setKameraAktif(false);
          return;
        }
        console.log("Quagga başarıyla başlatıldı");
        Quagga.start();
      });

      Quagga.onDetected((result) => {
        const barkod = result.codeResult.code;
        console.log("Barkod tespit edildi:", barkod);
        setUrun(prev => ({
          ...prev,
          barkod
        }));
        Quagga.stop();
        setKameraAktif(false);
      });

    } catch (error) {
      console.error('Kamera erişim hatası:', error);
      setKameraHata('Kamera erişimi reddedildi veya kamera bulunamadı.');
      setKameraAktif(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setYukleniyor(true);
    setIslemDurumu({ tip: '', mesaj: '' });

    try {
      // Ürün bilgilerini Firestore'a kaydet
      const urunData = {
        barkod: urun.barkod,
        ad: urun.ad,
        miktar: Number(urun.miktar),
        fiyat: Number(urun.fiyat),
        resimUrl: urun.resim,
        olusturmaTarihi: new Date().toISOString()
      };

      await addDoc(collection(db, 'urunler'), urunData);

      setIslemDurumu({
        tip: 'success',
        mesaj: 'Ürün başarıyla kaydedildi.'
      });

      // Formu sıfırla
      setUrun({
        barkod: '',
        ad: '',
        miktar: '',
        fiyat: '',
        resim: null
      });

      // 2 saniye sonra ürün listesine yönlendir
      setTimeout(() => {
        navigate('/');
      }, 2000);

    } catch (error) {
      console.error('Ürün kaydetme hatası:', error);
      setIslemDurumu({
        tip: 'error',
        mesaj: 'Ürün kaydedilirken bir hata oluştu: ' + error.message
      });
    } finally {
      setYukleniyor(false);
    }
  };

  return (
    <Container maxWidth="md" sx={{ mt: 4 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Typography variant="h5" gutterBottom>
          Yeni Ürün Ekle
        </Typography>
        
        {islemDurumu.mesaj && (
          <Alert severity={islemDurumu.tip} sx={{ mb: 2 }}>
            {islemDurumu.mesaj}
          </Alert>
        )}
        
        <form onSubmit={handleSubmit}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Box display="flex" gap={2}>
                <TextField
                  name="barkod"
                  label="Barkod"
                  value={urun.barkod}
                  onChange={handleInputChange}
                  fullWidth
                />
                <Button
                  variant="contained"
                  onClick={baslatBarkodOkuyucu}
                  disabled={kameraAktif}
                >
                  Barkod Tara
                </Button>
              </Box>
            </Grid>

            {kameraHata && (
              <Grid item xs={12}>
                <Alert severity="error">{kameraHata}</Alert>
              </Grid>
            )}

            {kameraAktif && (
              <Grid item xs={12}>
                <Box
                  ref={videoRef}
                  sx={{
                    width: '100%',
                    height: 300,
                    backgroundColor: '#000',
                    position: 'relative',
                    overflow: 'hidden'
                  }}
                />
              </Grid>
            )}

            <Grid item xs={12}>
              <TextField
                name="ad"
                label="Ürün Adı"
                value={urun.ad}
                onChange={handleInputChange}
                fullWidth
                required
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                name="miktar"
                label="Miktar"
                type="number"
                value={urun.miktar}
                onChange={handleInputChange}
                fullWidth
                required
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                name="fiyat"
                label="Fiyat"
                type="number"
                value={urun.fiyat}
                onChange={handleInputChange}
                fullWidth
                required
              />
            </Grid>

            <Grid item xs={12}>
              <Button
                variant="outlined"
                onClick={handleResimSecimi}
                fullWidth
              >
                Ürün Fotoğrafı Ekle
              </Button>
              {urun.resim && (
                <Box mt={2}>
                  <img
                    src={urun.resim}
                    alt="Ürün önizleme"
                    style={{ maxWidth: '200px', maxHeight: '200px' }}
                  />
                </Box>
              )}
            </Grid>

            <Grid item xs={12}>
              <Button
                type="submit"
                variant="contained"
                color="primary"
                fullWidth
                size="large"
                disabled={yukleniyor}
              >
                {yukleniyor ? (
                  <CircularProgress size={24} color="inherit" />
                ) : (
                  'Ürünü Kaydet'
                )}
              </Button>
            </Grid>
          </Grid>
        </form>
      </Paper>
    </Container>
  );
}

export default UrunEkle; 