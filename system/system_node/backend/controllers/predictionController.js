const path = require('path');
const { spawn } = require('child_process');
const pool = require('../db');

exports.runPrediction = async (req, res) => {
  try {
    if (!req.files || req.files.length === 0) {
      return res.status(400).send("No files uploaded");
    }

    const results = [];

    for (const file of req.files) {
      const imagePath = file.path;
      console.log("Processing:", imagePath);

      // Run Python script for each file
      const data = await new Promise((resolve, reject) => {
        const python = spawn('python3', [
          path.join(__dirname, '../python/predictor.py'),
          imagePath
        ]);

        let output = '';

        python.stdout.on('data', chunk => output += chunk.toString());
        python.on('close', () => resolve(output));
        python.on('error', reject);
      });

      const result = JSON.parse(data);
      results.push({
        image: file.filename,
        path: imagePath,
        label: result.label,
        confidence: result.confidence
      });

      // Save to DB
await pool.query(
  'INSERT INTO predictions (image, path, label, confidence) VALUES (?, ?, ?, ?)',
  [file.filename, imagePath, result.label, result.confidence]
);


    }

    res.render('prediction_multiple', { results });

  } catch (err) {
    console.error(err);
    res.status(500).send('Prediction failed');
  }
};

