const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const { spawn } = require('child_process');

const app = express();
const port = 3000;

app.use(cors()); // Enable CORS for all routes
app.use(bodyParser.json());

app.post('/fetch-links', async (req, res) => {
  const { url, depth } = req.body;
  console.log('Received request to fetch links:', { url, depth });
  const pythonProcess = spawn('python', ['fetch_links.py', url, depth]);

  pythonProcess.stdout.on('data', (data) => {
    console.log('Links fetched:', data.toString());
    res.status(200).send(data.toString());
  });

  pythonProcess.stderr.on('data', (data) => {
    console.error('Error fetching links:', data.toString());
    res.status(500).send(data.toString());
  });
});

app.post('/download-webpages', (req, res) => {
    const { links } = req.body;
    console.log('Received request to download webpages:', { links });
    const pythonProcess = spawn('python', ['download_webpages.py', ...links]);
  
    let downloadedWebpages = [];
  
    pythonProcess.stdout.on('data', (data) => {
      console.log('Webpages downloaded:', data.toString());
      downloadedWebpages.push(data.toString());
    });
  
    pythonProcess.stderr.on('data', (data) => {
      console.error('Error downloading webpages:', data.toString());
    });
  
    pythonProcess.on('close', (code) => {
      if (code === 0) {
        res.status(200).send(downloadedWebpages.join('\n'));
      } else {
        res.status(500).send('Error downloading webpages');
      }
    });
  });

app.post('/extract-text', (req, res) => {
  const { inputDirectory, outputFilePath } = req.body;
  console.log('Received request to extract text:', { inputDirectory, outputFilePath });
  const pythonProcess = spawn('python', ['extract_text.py', inputDirectory, outputFilePath]);

  pythonProcess.stdout.on('data', (data) => {
    console.log('Text extracted:', data.toString());
    res.status(200).send(data.toString());
  });

  pythonProcess.stderr.on('data', (data) => {
    console.error('Error extracting text:', data.toString());
    res.status(500).send(data.toString());
  });
});

app.post('/run-query', async (req, res) => {
  const { filePath, query } = req.body;
  console.log('Received request to run query:', { filePath, query });
  const pythonProcess = spawn('python', ['run_query.py', filePath, query]);

  pythonProcess.stdout.on('data', (data) => {
    console.log('Query response:', data.toString());
    res.status(200).json(JSON.parse(data.toString()));
  });

  pythonProcess.stderr.on('data', (data) => {
    console.error('Error running query:', data.toString());
    res.status(500).send(data.toString());
  });
});

app.post('/save-token', (req, res) => {
  const { token } = req.body;
  console.log('Received request to save token:', { token });
  const pythonProcess = spawn('python', ['save_token.py', token]);

  pythonProcess.stdout.on('data', (data) => {
    console.log('Token saved:', data.toString());
    res.status(200).send(data.toString());
  });

  pythonProcess.stderr.on('data', (data) => {
    console.error('Error saving token:', data.toString());
    res.status(500).send(data.toString());
  });
});

app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});