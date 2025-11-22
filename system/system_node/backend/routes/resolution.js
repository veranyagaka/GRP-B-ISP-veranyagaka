const express = require('express');
const multer = require('multer');
const path = require('path');
const { runResolution } = require('../controllers/resolutionController');

const router = express.Router();
const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    cb(null, path.join(__dirname, '../public/uploads'));
  },
  filename: function (req, file, cb) {
    cb(null, file.originalname); // keep original name
  }
});

const upload = multer({ storage });


router.get("/resolve", (req, res) => {
  res.render("resolution_upload"); 
});

router.post("/resolve", upload.single("image"), runResolution);
const pool = require('../db'); // MySQL pool

router.get('/res-history', async (req, res) => {
  try {
    const [rows] = await pool.query('SELECT * FROM resolutions ORDER BY created_at DESC');
    res.render('resolutionHistory', { resolutions: rows || [] });
  } catch (err) {
    console.error(err);
    res.status(500).send('Failed to fetch resolution history');
  }
});
module.exports = router;
