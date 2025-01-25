import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
  Button,
  Box,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  CircularProgress,
  Alert,
  Avatar,
} from '@mui/material';
import { Edit as EditIcon, Delete as DeleteIcon, Download as DownloadIcon, Upload as UploadIcon } from '@mui/icons-material';
import * as XLSX from 'xlsx';
import { db } from '../firebase';
import { collection, query, onSnapshot, updateDoc, deleteDoc, doc } from 'firebase/firestore';

function UrunListesi() {
  const [urunler, setUrunler] = useState([]);
  const [yukleniyor, setYukleniyor] = useState(true);
  const [hata, setHata] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [secilenUrun, setSecilenUrun] = useState(null);
  const [toplamUrun, setToplamUrun] = useState(0);
  const [toplamMiktar, setToplamMiktar] = useState(0);

  useEffect(() => {
    const q = query(collection(db, 'urunler'));
    const unsubscribe = onSnapshot(q, (querySnapshot) => {
      try {
        const urunlerData = querySnapshot.docs.map(doc => ({
          id: doc.id,
          ...doc.data()
        }));
        setUrunler(urunlerData);
        
        // Toplam hesaplamaları
        setToplamUrun(urunlerData.length);
        setToplamMiktar(urunlerData.reduce((acc, curr) => acc + (curr.miktar || 0), 0));
        
        setYukleniyor(false);
      } catch (error) {
        console.error('Veri çekme hatası:', error);
        setHata('Ürünler yüklenirken bir hata oluştu.');
        setYukleniyor(false);
      }
    }, (error) => {
      console.error('Firestore dinleme hatası:', error);
      setHata('Veritabanı bağlantısında bir hata oluştu.');
      setYukleniyor(false);
    });

    return () => unsubscribe();
  }, []);

  const handleDuzenle = (urun) => {
    setSecilenUrun({ ...urun });
    setDialogOpen(true);
  };

  const handleDialogKapat = () => {
    setSecilenUrun(null);
    setDialogOpen(false);
  };

  const handleUrunGuncelle = async () => {
    if (!secilenUrun) return;

    try {
      const urunRef = doc(db, 'urunler', secilenUrun.id);
      await updateDoc(urunRef, {
        ad: secilenUrun.ad,
        miktar: Number(secilenUrun.miktar),
        fiyat: Number(secilenUrun.fiyat)
      });
      setDialogOpen(false);
    } catch (error) {
      console.error('Güncelleme hatası:', error);
      alert('Ürün güncellenirken bir hata oluştu.');
    }
  };

  const handleUrunSil = async (urunId) => {
    if (window.confirm('Bu ürünü silmek istediğinizden emin misiniz?')) {
      try {
        await deleteDoc(doc(db, 'urunler', urunId));
      } catch (error) {
        console.error('Silme hatası:', error);
        alert('Ürün silinirken bir hata oluştu.');
      }
    }
  };

  const handleExcelIndir = () => {
    const ws = XLSX.utils.json_to_sheet(urunler.map(urun => ({
      Barkod: urun.barkod,
      'Ürün Adı': urun.ad,
      Miktar: urun.miktar,
      Fiyat: urun.fiyat,
      'Oluşturma Tarihi': urun.olusturmaTarihi
    })));
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Ürünler");
    XLSX.writeFile(wb, "urun-listesi.xlsx");
  };

  const handleExcelYukle = (e) => {
    const file = e.target.files[0];
    const reader = new FileReader();
    reader.onload = (evt) => {
      try {
        const bstr = evt.target.result;
        const wb = XLSX.read(bstr, { type: 'binary' });
        const wsname = wb.SheetNames[0];
        const ws = wb.Sheets[wsname];
        const data = XLSX.utils.sheet_to_json(ws);
        // Excel'den yüklenen verileri işleme
        console.log('Excel verileri:', data);
        // Burada verileri Firebase'e yükleyebilirsiniz
      } catch (error) {
        console.error('Excel okuma hatası:', error);
        alert('Excel dosyası okunurken bir hata oluştu.');
      }
    };
    reader.readAsBinaryString(file);
  };

  if (yukleniyor) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress />
      </Box>
    );
  }

  if (hata) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Alert severity="error">{hata}</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h5" gutterBottom>
            Ürün Listesi
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Toplam {toplamUrun} ürün | Toplam {toplamMiktar} adet
          </Typography>
        </Box>
        <Box>
          <input
            accept=".xlsx,.xls"
            style={{ display: 'none' }}
            id="excel-yukle"
            type="file"
            onChange={handleExcelYukle}
          />
          <label htmlFor="excel-yukle">
            <Button
              variant="contained"
              component="span"
              startIcon={<UploadIcon />}
              sx={{ mr: 1 }}
            >
              Excel Yükle
            </Button>
          </label>
          <Button
            variant="contained"
            onClick={handleExcelIndir}
            startIcon={<DownloadIcon />}
          >
            Excel İndir
          </Button>
        </Box>
      </Box>

      <Paper elevation={3}>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Fotoğraf</TableCell>
                <TableCell>Barkod</TableCell>
                <TableCell>Ürün Adı</TableCell>
                <TableCell>Miktar</TableCell>
                <TableCell>Fiyat</TableCell>
                <TableCell>İşlemler</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {urunler.map((urun) => (
                <TableRow key={urun.id}>
                  <TableCell>
                    {urun.resimUrl ? (
                      <Avatar
                        src={urun.resimUrl}
                        alt={urun.ad}
                        variant="rounded"
                        sx={{ width: 40, height: 40 }}
                      />
                    ) : (
                      <Avatar variant="rounded" sx={{ width: 40, height: 40 }}>
                        {urun.ad[0]}
                      </Avatar>
                    )}
                  </TableCell>
                  <TableCell>{urun.barkod}</TableCell>
                  <TableCell>{urun.ad}</TableCell>
                  <TableCell>{urun.miktar}</TableCell>
                  <TableCell>{urun.fiyat} TL</TableCell>
                  <TableCell>
                    <Button
                      size="small"
                      startIcon={<EditIcon />}
                      onClick={() => handleDuzenle(urun)}
                    >
                      Düzenle
                    </Button>
                    <Button
                      size="small"
                      color="error"
                      startIcon={<DeleteIcon />}
                      onClick={() => handleUrunSil(urun.id)}
                    >
                      Sil
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      <Dialog open={dialogOpen} onClose={handleDialogKapat}>
        <DialogTitle>Ürün Düzenle</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <TextField
              fullWidth
              label="Ürün Adı"
              value={secilenUrun?.ad || ''}
              onChange={(e) => setSecilenUrun(prev => ({ ...prev, ad: e.target.value }))}
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              label="Miktar"
              type="number"
              value={secilenUrun?.miktar || ''}
              onChange={(e) => setSecilenUrun(prev => ({ ...prev, miktar: e.target.value }))}
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              label="Fiyat"
              type="number"
              value={secilenUrun?.fiyat || ''}
              onChange={(e) => setSecilenUrun(prev => ({ ...prev, fiyat: e.target.value }))}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDialogKapat}>İptal</Button>
          <Button onClick={handleUrunGuncelle} variant="contained">
            Güncelle
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
}

export default UrunListesi; 