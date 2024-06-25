const express = require('express');
const cors = require('cors');
const { spawn } = require('child_process');
const app = express();
const port = 3001;

app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.post('/run-python-script', (req, res) => {
    // Get the Python script content from the request body
    const { script } = req.body;

    // Run the Python script
    const pythonProcess = spawn('python', ['-c', script]);

    let output = '';

    // Handle script output
    pythonProcess.stdout.on('data', (data) => {
        console.log(`stdout: ${data}`);
        output += data;
    });

    pythonProcess.stderr.on('data', (data) => {
        console.error(`stderr: ${data}`);
        res.status(500).send(`Error: ${data}`);
    });

    pythonProcess.on('close', (code) => {
        console.log(`child process exited with code ${code}`);
        if (code === 0) {
            res.send(output);
        } else {
            res.status(500).send(`Script execution failed with code ${code}`);
        }
    });
});

app.listen(port, () => {
    console.log(`Express server running at http://localhost:${port}`);
});
