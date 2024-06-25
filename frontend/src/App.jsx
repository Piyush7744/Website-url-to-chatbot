import React, { useState } from 'react';
import axios from 'axios';

function App() {
    const [url, setUrl] = useState('');
    const [keywords, setKeywords] = useState('');
    const [depth, setDepth] = useState('');
    const [output, setOutput] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.post('http://localhost:3001/run-python-script', { url, keywords, depth });
            setOutput(response.data.message);
        } catch (error) {
            console.error('Error:', error);
            setOutput('An error occurred. Please check the console.');
        }
    };

    return (
        <div>
            <form onSubmit={handleSubmit}>
                <label>
                    URL:
                    <input type="text" value={url} onChange={(e) => setUrl(e.target.value)} />
                </label>
                <label>
                    Keywords (comma-separated):
                    <input type="text" value={keywords} onChange={(e) => setKeywords(e.target.value.split(','))} />
                </label>
                <label>
                    Depth:
                    <input type="number" value={depth} onChange={(e) => setDepth(e.target.value)} />
                </label>
                <button type="submit">Run Python Script</button>
            </form>
            <p>{output}</p>
        </div>
    );
}

export default App;
