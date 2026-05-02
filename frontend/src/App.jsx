import { useState } from 'react';
import './App.css';

export default function App() {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [aiResponse, setAiResponse] = useState('');
  const [textInput, setTextInput] = useState(''); // New state for typing

  // The function to send text to the backend
  const sendToBackend = async (textToSend) => {
    try {
      setAiResponse("Thinking...");
      const response = await fetch('http://127.0.0.1:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: textToSend, user_id: "testing_user" })
      });

      if (!response.ok) throw new Error("Backend connection failed");
      
      const data = await response.json();
      setAiResponse(data.reply); 

    } catch (error) {
      console.error("Connection Error:", error);
      setAiResponse("Error: Could not reach ELE Core. Is the backend running?");
    }
  };

  // The Voice Engine
  const handleVoiceInput = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Browser unsupported. Use Chrome or Edge.");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
      setIsListening(true);
      setTranscript('Listening... Speak now!');
      setAiResponse('');
    };

    recognition.onresult = (event) => {
      const text = event.results[0][0].transcript;
      setTranscript(text);
      setIsListening(false);
      sendToBackend(text); // Send the spoken text
    };

    recognition.onerror = (event) => {
      // Better error logging!
      console.error("Microphone error code:", event.error);
      setTranscript(`Hardware Error: ${event.error}. Check browser permissions.`);
      setIsListening(false);
    };

    recognition.onend = () => setIsListening(false);
    recognition.start();
  };

  // The Text Engine (Fallback)
  const handleTextSubmit = (e) => {
    e.preventDefault();
    if (!textInput.trim()) return;
    setTranscript(`(Typed): ${textInput}`);
    sendToBackend(textInput);
    setTextInput('');
  };

  return (
    <div style={{ padding: '2rem', fontFamily: 'sans-serif', color: 'white', backgroundColor: '#111', minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
      <h2>ELE CORE: Interaction Layer</h2>
      
      {/* Voice Button */}
      <button 
        onClick={handleVoiceInput}
        style={{ padding: '1rem 2rem', fontSize: '1.2rem', backgroundColor: isListening ? '#ff4444' : '#4CAF50', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', marginBottom: '1rem' }}
      >
        {isListening ? '🎙️ Listening (Speak clearly)...' : '🎙️ Tap to Speak'}
      </button>

      {/* Text Fallback */}
      <form onSubmit={handleTextSubmit} style={{ marginBottom: '2rem', display: 'flex', gap: '10px' }}>
        <input 
          type="text" 
          value={textInput}
          onChange={(e) => setTextInput(e.target.value)}
          placeholder="Or type here to test backend..."
          style={{ padding: '0.5rem', width: '300px', borderRadius: '4px', border: 'none' }}
        />
        <button type="submit" style={{ padding: '0.5rem 1rem', backgroundColor: '#333', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>Send</button>
      </form>

      {/* Display Screens */}
      <div style={{ width: '100%', maxWidth: '500px', backgroundColor: '#222', padding: '1.5rem', borderRadius: '8px', marginBottom: '1rem' }}>
        <strong>Input:</strong>
        <p style={{ color: '#aaa' }}>{transcript || "Waiting for input..." }</p>
      </div>

      <div style={{ width: '100%', maxWidth: '500px', backgroundColor: '#222', padding: '1.5rem', borderRadius: '8px' }}>
        <strong>ELE says:</strong>
        <p style={{ color: '#00e5ff' }}>{aiResponse || "..." }</p>
      </div>
    </div>
  );
}