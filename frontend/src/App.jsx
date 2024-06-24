import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [url, setUrl] = useState('');
  const [keywords, setKeywords] = useState('');
  const [depth, setDepth] = useState(2);
  const [result, setResult] = useState(null);

  const handleSubmit = async (event) => {
    event.preventDefault();
    try {
      const response = await axios.post('http://127.0.0.1:5000/scrape', {
        url,
        keywords: keywords.split(','),
        depth,
      });
      setResult(response.data);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  return (
    <div className="App">
      <h1>Web Scraper</h1>
      <form onSubmit={handleSubmit}>
        <div>
          <label>
            URL:
            <input type="text" value={url} onChange={(e) => setUrl(e.target.value)} required />
          </label>
        </div>
        <div>
          <label>
            Keywords (comma separated):
            <input type="text" value={keywords} onChange={(e) => setKeywords(e.target.value)} />
          </label>
        </div>
        <div>
          <label>
            Depth:
            <input type="number" value={depth} onChange={(e) => setDepth(e.target.value)} />
          </label>
        </div>
        <button type="submit">Scrape</button>
      </form>
      {result && (
        <div>
          <h2>Scraping Result</h2>
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}

export default App;
