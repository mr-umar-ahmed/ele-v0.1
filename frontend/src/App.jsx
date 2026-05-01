import { useState } from 'react';
import './App.css';

function App() {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [response, setResponse] = useState('ELE System Core Online. Awaiting command.');
  const [status, setStatus] = useState('IDLE'); // States: IDLE, LISTENING, THINKING, ERROR

  const startListening = async () => {
    // 1. Instantly update UI to show it's activating
    setIsListening(true);
    setStatus('LISTENING...');
    setTranscript('');
    setResponse('');

    try {
      // 2. Tell Python to open the hardware microphone
      const res = await fetch('http://127.0.0.1:8000/api/listen');
      const data = await res.json();

      // 3. Handle errors (like silence or mumbled words)
      if (data.error) {
        setStatus('ERROR');
        setResponse(data.error);
        setIsListening(false);
        return;
      }

      // 4. Success! Python heard you. Show the text and send it to the brain.
      setTranscript(data.text);
      setStatus('THINKING...');
      setIsListening(false); 
      
      await sendToBackend(data.text);

    } catch (error) {
      console.error("Mic error:", error);
      setStatus('ERROR');
      setResponse("Failed to connect to the Python Audio Engine.");
      setIsListening(false);
    }
  };

  const sendToBackend = async (text) => {
    try {
      const res = await fetch('http://127.0.0.1:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: text, user_id: 'umar' }) // Passed directly to FastAPI
      });

      const data = await res.json();
      setResponse(data.reply || `[Action Executed: ${data.intent}]`);
      setStatus('IDLE');

      // If the backend says Electron needs to handle an OS action, trigger the bridge
      if (data.action_required && window.eleAPI) {
         window.eleAPI.executeTask(data);
      }

    } catch (error) {
      console.error("Backend error:", error);
      setResponse("Critical connection failure to ELE Core.");
      setStatus('ERROR');
    }
  };

  return (
    <div className="app-container">
      {/* The Reactive Visualizer Orb */}
      <div className={`glow-orb ${status.toLowerCase().replace('...', '')}`}></div>
      
      <div className="glass-panel">
        <div className="header">
          <h1 className="system-title">ELE <span>CORE</span></h1>
          <div className={`status-badge ${status.toLowerCase().replace('...', '')}`}>
            {status}
          </div>
        </div>
        
        <div className="chat-log">
          {transcript && (
            <div className="message user-message">
              <span className="label">USER</span>
              <p>{transcript}</p>
            </div>
          )}
          {response && (
            <div className="message ele-message">
              <span className="label">ELE</span>
              <p>{response}</p>
            </div>
          )}
        </div>

        <button 
          className={`mic-button ${isListening ? 'active' : ''}`}
          onClick={startListening}
        >
          {isListening ? 'Listening...' : 'Initialize Microphone'}
        </button>
      </div>
    </div>
  );
}

export default App;