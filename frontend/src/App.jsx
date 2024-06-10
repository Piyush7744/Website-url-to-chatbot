import React, { useState } from 'react';
import axios from 'axios';
import { Widget, addResponseMessage } from 'react-chat-widget';
import 'react-chat-widget/lib/styles.css';
import './App.css';

function App() {
  const [website, setWebsite] = useState('');
  const [queryText, setQueryText] = useState('');
  const [queryURL, setQueryURL] = useState('');
  const [response, setResponse] = useState('');
  const [error, setError] = useState('');

  const handleGenerateURL = async () => {
    try {
      const response = await axios.post('http://localhost:5000/generate_url', {
        website,
      });

      if (response.data.error) {
        setError(response.data.error);
      } else {
        setQueryURL(response.data.url);
        setError('');
      }
    } catch (err) {
      setError('Failed to generate URL. Please try again.');
      console.error(err);
    }
  };

  const handleNewUserMessage = (newMessage) => {
    // Handle the new message here
    console.log(`New message incoming! ${newMessage}`);
  };

  const handleQuery = async () => {
    try {
      const response = await axios.get(queryURL, {
        params: { query: queryText },
      });

      if (response.data.error) {
        setError(response.data.error);
      } else {
        setResponse(response.data.result);
        setError('');
      }
    } catch (err) {
      setError('Failed to get response. Please try again.');
      console.error(err);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Chatbot Demo</h1>
        <input
          type="text"
          value={website}
          onChange={(e) => setWebsite(e.target.value)}
          placeholder="Enter website URL"
        />
        <button onClick={handleGenerateURL}>Generate Query URL</button>
        {queryURL && (
          <div>
            <h2>Query URL:</h2>
            <code>{queryURL}</code>
          </div>
        )}
        <input
          type="text"
          value={queryText}
          onChange={(e) => setQueryText(e.target.value)}
          placeholder="Enter your query"
        />
        <button onClick={handleQuery}>Query</button>
        {response && (
          <div>
            <h2>Response:</h2>
            <p>{response}</p>
          </div>
        )}
        {error && <p className="error">{error}</p>}
        <Widget
          handleNewUserMessage={handleNewUserMessage}
          title="Chatbot"
          subtitle="Ask me anything"
        />
      </header>
    </div>
  );
}

export default App;
