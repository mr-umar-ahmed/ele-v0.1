import { useState } from 'react';
import './App.css'; 

export default function App() {
  const [input, setInput] = useState('');
  const [logs, setLogs] = useState([]);

  const handleCommand = async (e) => {
    e.preventDefault(); 
    if (!input.trim()) return;

    const userMessage = input;
    setLogs(prev => [...prev, `User: ${userMessage}`]);
    setInput(''); // Clear box immediately for better UX

    try {
      // FIXED URL: Removed markdown formatting from the string
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
        <div className="status-dot"></div>
      </header>
      
      <div className="chat-box">
        {logs.map((log, index) => (
          <div key={index} className={`log-entry ${log.startsWith('User') ? 'user' : 'ele'}`}>
            {log}
          </div>
        ))}
      </div>

      <form onSubmit={handleCommand} className="input-area">
        <input 
          type="text" 
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Command ELE..." 
        />
        <button type="submit">Send</button>
      </form>
    </div>
  );
}