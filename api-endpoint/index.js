const express = require('express');
const mysql = require('mysql');

// Membuat koneksi ke database MySQL
const db = mysql.createConnection({
  host: '34.128.86.191',
  user: 'root',
  password: 'skinnie-db-project',
  database: 'skinnie_database'
});

// Membuat server Express
const app = express();

// Menyajikan file statis dari direktori 'public'
app.use(express.static('public'));

// Menangani permintaan untuk halaman utama
app.get('/', (req, res) => {
  res.sendFile(__dirname + '/public/documentation.html');
});

// Mengambil data dari MySQL
app.get('/data', (req, res) => {
  const query = 'SELECT * FROM list_skincare LIMIT 10';

  db.query(query, (error, results) => {
    if (error) {
      console.error(error);
      res.status(500).json({ error: 'Error retrieving data from MySQL' });
    } else {
      res.json(results);
    }
  });
});

app.get('/data/random', (req, res) => {
  const query = 'SELECT * FROM list_skincare ORDER BY RAND() LIMIT 1';

  db.query(query, (error, results) => {
    if (error) {
      console.error(error);
      res.status(500).json({ error: 'Error retrieving data from MySQL' });
    } else {
      res.json(results);
    }
  });
});

// Mengambil data berdasarkan ID dari MySQL
app.get('/data/:id', (req, res) => {
  const id = req.params.id;
  const query = `SELECT * FROM list_skincare WHERE id = ${id}`;

  db.query(query, (error, results) => {
    if (error) {
      console.error(error);
      res.status(500).json({ error: 'Error retrieving data from MySQL' });
    } else {
      res.json(results);
    }
  });
});

// Menjalankan server
app.listen(3000, () => {
  console.log('Server running on port 3000');
});
