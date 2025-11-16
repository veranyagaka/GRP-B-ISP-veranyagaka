const express = require('express');
const router = express.Router();
const multer = require('multer');
const path = require('path');
const { runPrediction } = require('../controllers/predictionController');

// File upload config
const upload = multer({
  dest: path.join(__dirname, '../public/uploads')
});

router.get('/predict', (req, res) => {
  res.render('upload');
});

router.post('/predict', upload.array('xrayImage', 5), runPrediction); // allowing maximumm 5

module.exports = router;
