import { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [response, setResponse] = useState('ELE Stealth Daemon Online. Awaiting wake word.');
  const [status, setStatus] = useState('IDLE'); // States: IDLE, LISTENING, THINKING, ERROR

  // 1. Define the functions FIRST so React knows they exist
  const startWakeWordListener = async () => {
    try {
      // This fetch will "hang" silently until the Python backend hears the trigger
      const res = await fetch('http://127.0.0.1:8000/api/wakeword');
      const data = await res.json();

      if (data.status === 'detected') {
        // Wake word heard! Trigger the main microphone automatically.
        startListening();
      }
    } catch (error) {
      console.error("Wake Word connection lost. Retrying...", error);
      setTimeout(startWakeWordListener, 5000); // Try again in 5 seconds if server drops
    }
  };

  const startListening = async () => {
    setIsListening(true);
    setStatus('LISTENING...');
    setTranscript('');
    setResponse('');

    try {
      const res = await fetch('http://127.0.0.1:8000/api/listen');
      const data = await res.json();

      if (data.error) {
        setStatus('ERROR');
        setResponse(data.error);
        setIsListening(false);
        startWakeWordListener(); // Restart stealth listener
        return;
      }

      setTranscript(data.text);
      setStatus('THINKING...');
      setIsListening(false); 
      
      await sendToBackend(data.text);

    } catch (error) {
      console.error("Mic error:", error);
      setStatus('ERROR');
      setResponse("Failed to connect to the Python Audio Engine.");
      setIsListening(false);
      startWakeWordListener(); // Restart stealth listener
    }
  };

  const sendToBackend = async (text) => {
    try {
      const res = await fetch('http://127.0.0.1:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: text, user_id: 'umar' }) 
      });

      const data = await res.json();
      setResponse(data.reply || `[Action Executed: ${data.intent}]`);
      setStatus('IDLE');

      if (data.action_required && window.eleAPI) {
         window.eleAPI.executeTask(data);
      }

    } catch (error) {
      console.error("Backend error:", error);
      setResponse("Critical connection failure to ELE Core.");
      setStatus('ERROR');
    } finally {
      // Once the action is totally complete, go back into stealth mode!
      startWakeWordListener();
    }
  };

  // 2. NOW we can safely call useEffect, because the function is loaded!
  useEffect(() => {
    startWakeWordListener();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="app-container">
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
          {isListening ? 'Listening...' : 'Manual Override'}
        </button>
      </div>
    </div>
  );
}

export default App;