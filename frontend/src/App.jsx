import { useState } from 'react';
import './App.css';

function App() {
  const [messages, setMessages] = useState([
    { sender: 'bot', text: 'Hello! How can I assist you today?' }
  ]);
  const [userInput, setUserInput] = useState('');

  const sendMessage = async () => {
    if (userInput.trim() === '') return;

    const userMessage = { sender: 'user', text: userInput };
    setMessages([...messages, userMessage]);
    setUserInput('');

    try {
      const response = await fetch('http://127.0.0.1:5000/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ query: userInput, website: 'https://www.quicsolv.com' })
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const data = await response.json();
      console.log("API response: ", data); // Log the response

      const botMessage = { sender: 'bot', text: data.result || "I'm sorry, I didn't understand that." };

      setMessages((prevMessages) => [...prevMessages, botMessage]);

      // Add default prompt for next question
      setTimeout(() => {
        setMessages((prevMessages) => [...prevMessages, { sender: 'bot', text: 'What else would you like to know?' }]);
      }, 1000);
    } catch (error) {
      console.error('Error fetching the API:', error);
      const errorMessage = { sender: 'bot', text: 'There was an error processing your request.' };
      setMessages((prevMessages) => [...prevMessages, errorMessage]);
    }
  };

  return (
    <div className="App">
      <div className="chat-container">
        <div className="chat-box">
          {messages.map((message, index) => (
            <p key={index} className={message.sender}>
              {message.text}
            </p>
          ))}
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
      </div>
    </div>
  );
}

export default App;
