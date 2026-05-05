import { useState, useEffect, useRef } from "react";
import "./App.css";

function App() {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [response, setResponse] = useState("");
  const [status, setStatus] = useState("IDLE");
  const isPollingRef = useRef(false);

  // 1. STEALTH DAEMON
  const startWakeWordListener = async () => {
    if (isPollingRef.current) return;

    isPollingRef.current = true;
    console.log("[ELE] Daemon: Entering stealth mode...");

    try {
      const res = await fetch("http://127.0.0.1:8000/api/wakeword");
      const data = await res.json();

      if (data.status === "detected") {
        console.log("[ELE] Daemon: Trigger detected!");
        setStatus("LISTENING");

        setTimeout(() => {
          isPollingRef.current = false;
          startListening();
        }, 800);
      }
    } catch (error) {
      console.error("[ELE] Daemon: Connection lost. Retrying...", error);
      isPollingRef.current = false;
      setTimeout(startWakeWordListener, 5000);
    }
  };

  // 2. ACTIVE COMMAND LISTENER
  const startListening = async () => {
    setIsListening(true);
    setStatus("LISTENING");
    setTranscript("");
    setResponse("");

    try {
      const res = await fetch("http://127.0.0.1:8000/api/listen");
      const data = await res.json();

      if (data.error) {
        setStatus("IDLE");
        setIsListening(false);
        startWakeWordListener();
        return;
      }

      setTranscript(data.text);
      setStatus("THINKING");
      setIsListening(false);

      await sendToBackend(data.text);
    } catch (error) {
      console.error("[ELE] Core: Mic synchronization failed.", error);
      setStatus("ERROR");
      setResponse("Mic synchronization failed.");
      setIsListening(false);
      startWakeWordListener();
    }
  };

  // 3. BRAIN ENGINE
  const sendToBackend = async (text) => {
    try {
      const res = await fetch("http://127.0.0.1:8000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: text, user_id: "umar" }),
      });

      const data = await res.json();

      setResponse(data.reply || `Executed command.`);
      setStatus("IDLE");

      if (data.action_required && window.eleAPI) {
        window.eleAPI.executeTask(data);
      }
    } catch (error) {
      console.error("[ELE] Core: Backend connection failure.", error);
      setResponse("Critical core connection failure.");
      setStatus("ERROR");
    } finally {
      startWakeWordListener();
    }
  };

  useEffect(() => {
    startWakeWordListener();
    return () => {
      isPollingRef.current = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // --- Date/Time helper for the HUD display ---
  const [dateTime, setDateTime] = useState(new Date());
  useEffect(() => {
    const timer = setInterval(() => setDateTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className={`app-root ${status.toLowerCase()}`}>
      {/* Background Grid Pattern */}
      <div className="hud-grid-overlay" />

      {/* Main HUD Framework */}
      <div className="hud-container">
        
        {/* ---- Top Status Bar ---- */}
        <header className="hud-header">
          <div className="header-left">
            <span className="status-indicator">SYSTEM STATUS: <span className={`status-text ${status.toLowerCase()}`}>{status}</span></span>
          </div>
          <div className="header-center">
            <div className="version-pill-hud">
              ELE // 3.0 CORE <span className="beta-tag-hud">STABLE</span>
            </div>
          </div>
          <div className="header-right">
            <span className="datetime-display">
              {dateTime.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' }).toUpperCase()} // 
              {dateTime.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false })}
            </span>
          </div>
        </header>

        {/* ---- Main Content Area (3 Columns) ---- */}
        <main className="hud-main">
          
          {/* Left Panel: Mock System Data */}
          <aside className="hud-panel panel-left">
            <div className="panel-header">NETWORK_STATUS</div>
            <div className="panel-content monospace">
              <div>UPLINK: ACTIVE</div>
              <div>LATENCY: 24ms</div>
              <div>IP: 192.168.1.103</div>
              <div className="separator"></div>
              <div>CORE_TEMP: 42°C</div>
              <div>FAN_SPEED: 1200 RPM</div>
            </div>
          </aside>

          {/* Central Section: The Core Visual */}
          <section className="hud-center">
            <div className="core-visual-wrapper">
              <div className={`core-visual ${status.toLowerCase()}`}>
                <div className="ring ring-outer"></div>
                <div className="ring ring-middle"></div>
                <div className="ring ring-inner">
                  <span className="core-text monospace">ELE</span>
                </div>
              </div>
            </div>
            
            {/* Dialogue Display */}
            <div className="dialogue-display-hud">
              {status === "IDLE" && !transcript && !response && (
                <div className="greeting-hud">Awaiting Command...</div>
              )}
              {/* === FIX IS HERE ON THIS LINE === */}
              {transcript && <div className="transcript-hud monospace">{">>>"} {transcript}</div>}
              {response && <div className="response-hud monospace">ELE: {response}</div>}
            </div>
          </section>

          {/* Right Panel: Mock Diagnostics */}
          <aside className="hud-panel panel-right">
            <div className="panel-header">DIAGNOSTICS</div>
            <div className="panel-content monospace">
              <div>MEMORY: 48% USED</div>
              <div>THREADS: 12 ACTIVE</div>
              <div className="separator"></div>
              <div>LAST_CMD: NONE</div>
              <div>DAEMON_POLLING: TRUE</div>
            </div>
          </aside>
        </main>

        {/* ---- Bottom Control Bar ---- */}
        <footer className="hud-footer">
          <div className="footer-left">
            <button className="hud-icon-btn">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M3 12h18M3 6h18M3 18h18"/></svg>
            </button>
          </div>

          <div className="footer-center">
            {/* Microphone Control */}
            <div className="mic-wrapper-hud">
              {isListening && (
                <div className="mic-waves">
                  <div className="wave-hud wave1"></div>
                  <div className="wave-hud wave2"></div>
                </div>
              )}
              <button
                className={`mic-btn-hud ${status.toLowerCase()}`}
                onClick={!isListening ? startListening : undefined}
                disabled={status === "THINKING"}
              >
                <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5">
                  <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
                  <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                  <line x1="12" y1="19" x2="12" y2="23"></line>
                  <line x1="8" y1="23" x2="16" y2="23"></line>
                </svg>
              </button>
            </div>
          </div>

          <div className="footer-right">
            <button className="hud-icon-btn red-hover">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M18.36 6.64a9 9 0 1 1-12.73 0"/><line x1="12" y1="2" x2="12" y2="12"/></svg>
            </button>
          </div>
        </footer>

      </div>
    </div>
  );
}

export default App;