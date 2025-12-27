const path = require('path');
const { spawn } = require('child_process');
const pool = require('../db'); // optional

exports.runResolution = async (req, res) => {
  try {
    const imagePath = req.file.path;
    console.log(imagePath)
    // Spawn Python process
    const python = spawn('python3.11', [
      path.join(__dirname, '../python/resolution.py'),
      imagePath
    ]);

    let data = '';

    python.stdout.on('data', chunk => {
      data += chunk.toString();
    });

    python.stderr.on('data', err => {
      console.error('Python Error:', err.toString());
    });

    python.on('close', async () => {
      if (!data) {
        console.error("Python returned no output");
        return res.status(500).send("Resolution failed");
      }

      try {
        const result = JSON.parse(data);
        await pool.query(
  'INSERT INTO resolutions (user_id, image_path, metrics, output_path) VALUES (?, ?, ?, ?)',
  [
    1, 
    imagePath,
    JSON.stringify(result.metrics),
    result.output_path
  ]
);


        res.render('resolution', { result });
      } catch (err) {
        console.error('JSON Parse Error:', err, 'Data:', data);
        res.status(500).send('Resolution failed (invalid JSON)');
      }
    });

  } catch (err) {
    console.error('Controller Error:', err);
    res.status(500).send('Error uploading file');
  }
};
