import React from 'react';
import { Link } from 'react-router-dom';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import InventoryIcon from '@mui/icons-material/Inventory';

function Navbar() {
  return (
    <AppBar position="static">
      <Toolbar>
        <InventoryIcon sx={{ mr: 2 }} />
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          Stok Yönetim Sistemi
        </Typography>
        <Button color="inherit" component={Link} to="/">
          Ürün Listesi
        </Button>
        <Button color="inherit" component={Link} to="/urun-ekle">
          Ürün Ekle
        </Button>
      </Toolbar>
    </AppBar>
  );
}

export default Navbar; 