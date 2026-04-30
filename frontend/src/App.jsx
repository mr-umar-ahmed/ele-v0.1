import { useState } from 'react';
import './App.css'; 

export default function App() {
  const [input, setInput] = useState('');
  const [logs, setLogs] = useState([]);

  // This runs when you click "Send"
  const handleCommand = async (e) => {
    e.preventDefault(); 
    if (input === '') return;

    // 1. Show what you typed on the screen
    setLogs(previousLogs => [...previousLogs, "User: " + input]);

    try {
      // 2. Send your text to the Python Brain
      const response = await fetch('[http://127.0.0.1:8000/api/chat](http://127.0.0.1:8000/api/chat)', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: input, user_id: "dev_c" })
      });
      
      const data = await response.json();
      
      // 3. Show what the Brain replied
      setLogs(previousLogs => [...previousLogs, "ELE: " + data.reply]);

      // 4. Tell the Hands (Electron) to open the app!
      if (data.action_required === true) {
         window.eleAPI.executeTask({ intent: data.intent, rawText: input });
      }

    } catch (error) {
      setLogs(previousLogs => [...previousLogs, "Error: The Brain is asleep! Turn on Python."]);
    }
    
    setInput(''); // Clear the text box
  };

  return (
    <div className="app-container">
      <h1>ELE System Core</h1>
      
      <div className="chat-box">
        {logs.map((log, index) => (
          <p key={index}>{log}</p>
        ))}
      </div>

      <form onSubmit={handleCommand}>
        <input 
          type="text" 
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type 'open app'..." 
        />
        <button type="submit">Send</button>
      </form>
    </div>
  );
}