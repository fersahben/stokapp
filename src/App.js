import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Navbar from './components/Navbar';
import UrunEkle from './pages/UrunEkle';
import UrunListesi from './pages/UrunListesi';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <div className="App">
        <Navbar />
        <Routes>
          <Route path="/" element={<UrunListesi />} />
          <Route path="/urun-ekle" element={<UrunEkle />} />
        </Routes>
      </div>
    </ThemeProvider>
  );
}

export default App; 