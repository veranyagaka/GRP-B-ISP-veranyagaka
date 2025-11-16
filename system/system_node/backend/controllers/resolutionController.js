const path = require('path');
const { spawn } = require('child_process');
const pool = require('../db'); // optional if you'll save results later

exports.runResolution = async (req, res) => {
  try {
    const imagePath = req.file.path;

    // Run the resolution model script
    const python = spawn('python3', [
      path.join(__dirname, '../python/resolution.py'),
      imagePath
    ]);

    let data = '';
    python.stdout.on('data', chunk => (data += chunk.toString()));

    python.stderr.on('data', err => console.error('Python Error:', err.toString()));

    python.on('close', async (code) => {
      try {
        const result = JSON.parse(data);

        // (Optional) save result to DB
        // await pool.query(
        //   'INSERT INTO resolutions (user_id, image_path, metrics, output_path) VALUES ($1, $2, $3, $4)',
        //   [1, imagePath, result.metrics, result.output_path]
        // );

        // Render EJS page
        res.render('resolution', { result });
      } catch (err) {
        console.error('Parse/Render Error:', err);
        res.status(500).send('Resolution failed');
      }
    });
  } catch (err) {
    console.error('Controller Error:', err);
    res.status(500).send('Error uploading file');
  }
};
