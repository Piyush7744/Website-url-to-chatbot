import { useState } from 'react';
import './App.css';

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
      <div className="chat-container">
        <div className="chat-box">
          <div className="message-container">
            {messages.map((message, index) => (
              <p key={index} className={`message ${message.sender === 'bot' ? 'bot-message' : 'user-message'}`}>
                {message.text}
              </p>
            ))}
            {loading && <div className="loader my-2"><div className="loader-dot h-8 w-8 border-t-4 border-blue-500"></div></div>}
          </div>
        </div>
        <div className="input-box">
          <input
            type="text"
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
            placeholder="Type your question here..."
          />
          <button onClick={sendMessage}>Send</button>
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
