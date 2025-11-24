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
    const [predictions] = await pool.query(
      'SELECT * FROM predictions ORDER BY created_at DESC'
    );

    const [resolutions] = await pool.query(
      'SELECT * FROM resolutions ORDER BY created_at DESC'
    );

    res.render('history', {
      predictions: predictions || [],
      resolutions: resolutions || []
    });

  } catch (err) {
    console.error(err);
    res.status(500).send('Failed to load history');
  }
});


module.exports = router;
