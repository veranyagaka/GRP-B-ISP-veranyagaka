const path = require('path');
const { spawn } = require('child_process');
const pool = require('../db');

exports.runPrediction = async (req, res) => {
  try {
    const imagePath = req.file.path;

    // Run the Python script
    const python = spawn('python3', [
      path.join(__dirname, '../python/predictor.py'),
      imagePath
    ]);

    let data = '';
    python.stdout.on('data', chunk => data += chunk.toString());

    python.on('close', async () => {
      try {
        const result = JSON.parse(data);
        // Save to DB
        // await pool.query(
        //   'INSERT INTO predictions (user_id, image_path, result_label, confidence) VALUES ($1, $2, $3, $4)',
        //   [1, imagePath, result.label, result.confidence] // temporary user_id=1
        // );
        res.render('prediction', { result });
      } catch (err) {
        console.error(err);
        res.status(500).send('Prediction failed');
      }
    });
  } catch (err) {
    console.error(err);
    res.status(500).send('Error uploading file');
  }
};
