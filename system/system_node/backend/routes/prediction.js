const express = require('express');
const router = express.Router();
const multer = require('multer');
const path = require('path');
const { runPrediction } = require('../controllers/predictionController');
const pool = require('../db');
// File upload config
const upload = multer({
  dest: path.join(__dirname, '../public/uploads')
});

router.get('/predict', (req, res) => {
  res.render('upload');
});

router.post('/predict', upload.array('xrayImage', 5), runPrediction); // allowing maximumm 5

router.get('/history', async (req, res) => {
  try {
    const [rows] = await pool.query('SELECT * FROM predictions ORDER BY created_at DESC');
    // Pass an empty array if no rows are returned
    res.render('history', { predictions: rows || [] });
  } catch (err) {
    console.error(err);
    res.status(500).send('Failed to fetch prediction history');
  }
});

module.exports = router;
