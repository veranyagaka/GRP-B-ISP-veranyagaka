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

// const upload = multer({
//   dest: path.join(__dirname, '../public/uploads')
// });

router.get("/resolve", (req, res) => {
  res.render("resolution_upload"); 
});

router.post("/resolve", upload.single("image"), runResolution);

module.exports = router;
