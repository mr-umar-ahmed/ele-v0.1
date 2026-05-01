import { useState, useRef } from 'react';
import './App.css'; 

export default function App() {
  const [input, setInput] = useState('');
  const [logs, setLogs] = useState([]);
  const [isListening, setIsListening] = useState(false);
  
  // Set up the browser's native Speech Recognition API
  const recognitionRef = useRef(null);

  const startListening = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Your browser does not support Voice Input. Use Chrome or Edge.");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onstart = () => setIsListening(true);
    
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setInput(transcript); // Put the spoken words into the text box
      handleCommand(transcript); // Automatically send it to the brain
    };

    recognition.onerror = (event) => {
      console.error("Speech recognition error", event.error);
      setIsListening(false);
    };

    recognition.onend = () => setIsListening(false);

    recognition.start();
    recognitionRef.current = recognition;
  };

  const handleCommand = async (textToProcess) => {
    // Determine if the text came from the mic (textToProcess) or the typing box (input)
    const userMessage = typeof textToProcess === 'string' ? textToProcess : input;
    
    if (!userMessage.trim()) return;

    setLogs(prev => [...prev, `User: ${userMessage}`]);
    setInput(''); 

    try {
      const response = await fetch('http://127.0.0.1:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: userMessage, user_id: "dev_c" })
      });
      
      if (!response.ok) throw new Error("Server error");

      const data = await response.json();
      setLogs(prev => [...prev, `ELE: ${data.reply}`]);

      // Execution Layer (Electron Bridge)
      if (data.action_required && window.eleAPI) {
         window.eleAPI.executeTask({ intent: data.intent, rawText: userMessage });
      }

    } catch (error) {
      console.error(error);
      setLogs(prev => [...prev, "Error: The Brain is asleep! Run: uvicorn main:app"]);
    }
  };

  return (
    <div className="app-container">
      <header>
        <h1>ELE System Core</h1>
        <div className={`status-dot ${isListening ? 'listening' : ''}`}></div>
      </header>
      
      <div className="chat-box">
        {logs.map((log, index) => (
          <div key={index} className={`log-entry ${log.startsWith('User') ? 'user' : 'ele'}`}>
            {log}
          </div>
        ))}
      </div>

      <div className="input-area">
        {/* NEW PUSH TO TALK BUTTON */}
        <button 
            type="button" 
            className={`mic-btn ${isListening ? 'active' : ''}`}
            onClick={startListening}
        >
            {isListening ? '🎙️ Listening...' : '🎤 Speak'}
        </button>

        <form onSubmit={(e) => { e.preventDefault(); handleCommand(input); }} style={{ display: 'flex', flexGrow: 1, marginLeft: '10px' }}>
          <input 
            type="text" 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Or type a command..." 
          />
          <button type="submit">Send</button>
        </form>
      </div>
    </div>
  );
}