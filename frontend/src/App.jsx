// App.jsx

import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [url, setUrl] = useState('');
  const [depth, setDepth] = useState(2);
  const [links, setLinks] = useState([]);
  const [query, setQuery] = useState('');
  const [token, setToken] = useState('');
  const [response, setResponse] = useState('');
  const [cost, setCost] = useState(0);

  const handleFetchLinks = async () => {
    try {
      console.log('Fetching links...');
      const res = await axios.post('http://localhost:3000/fetch-links', { url, depth });
      console.log('Response received:', res.data);
      setLinks(res.data.split('\n'));
    } catch (err) {
      console.error('Error fetching links:', err);
    }
  };

  const handleDownloadWebpages = async () => {
    try {
      const res = await axios.post('http://localhost:3000/download-webpages', { links });
      console.log(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleExtractText = async () => {
    try {
      const res = await axios.post('http://localhost:3000/extract-text', { inputDirectory: 'downloaded_webpages', outputFilePath: 'cleaned_text.txt' });
      console.log(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleRunQuery = async () => {
    try {
      const res = await axios.post('http://localhost:3000/run-query', { filePath: 'cleaned_text.txt', query });
      setResponse(res.data.response);
      setCost(res.data.cost);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Web Crawler and Query Interface</h1>

        <div>
          <h2>Fetch Links</h2>
          <input type="text" placeholder="Enter Website URL" value={url} onChange={(e) => setUrl(e.target.value)} />
          <input type="number" placeholder="Enter Depth" value={depth} onChange={(e) => setDepth(parseInt(e.target.value))} />
          <button onClick={handleFetchLinks}>Fetch Links</button>
        </div>

        <div>
          <h2>Download Webpages</h2>
          <button onClick={handleDownloadWebpages}>Download Webpages</button>
        </div>

        <div>
          <h2>Extract Text</h2>
          <button onClick={handleExtractText}>Extract Text</button>
        </div>

        <div>
          <h2>Run Query</h2>
          <input type="text" placeholder="Enter Query" value={query} onChange={(e) => setQuery(e.target.value)} />
          <input type="password" placeholder="Enter your access token" value={token} onChange={(e) => setToken(e.target.value)} />
          <button onClick={handleRunQuery}>Run Query</button>
        </div>

        {response && (
          <div>
            <h2>Response</h2>
            <p>{response}</p>
            <p>Cost: ${cost.toFixed(4)}</p>
          </div>
        )}

        {links.length > 0 && (
          <div>
            <h2>Fetched Links</h2>
            <ul>
              {links.map((link, index) => (
                <li key={index}>{link}</li>
              ))}
            </ul>
          </div>
        )}
      </header>
    </div>
  );
}

export default App;
