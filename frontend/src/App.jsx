import DiagnosticsPanel from "./components/DiagnosticsPanel";
import CircularRadar from "./components/CircularRadar";
import "./styles/hud.css";
import HUDButton from "./components/HUDButton";
import "./styles/panels.css";
import VoiceConsole from "./components/VoiceConsole";
import "./styles/reactor.css";
import ReactorCore from "./components/ReactorCore";
import { useState, useEffect, useRef } from "react";
import "./App.css";

function App() {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [response, setResponse] = useState("");
  const [textInput, setTextInput] = useState("");
  const [status, setStatus] = useState("IDLE");
  const isPollingRef = useRef(false);

  // ==========================================
  // ACTIVE COMMAND LISTENER (Voice)
  // ==========================================
  const startListening = async () => {
    setIsListening(true);
    setStatus("LISTENING");
    setTranscript("");
    setResponse("");
    try {
      const res = await fetch("http://127.0.0.1:8000/api/listen");
      const data = await res.json();
      if (data.error) {
        setStatus("ERROR");
        setResponse(data.error);
        setIsListening(false);
        return;
      }
      setTranscript(data.text);
      setStatus("THINKING");
      await sendToBackend(data.text);
      setIsListening(false);
      setStatus("IDLE");
    } catch (error) {
      console.error("[ELE] Core: Mic synchronization failed.", error);
      setStatus("ERROR");
      setResponse("Mic synchronization failed.");
      setIsListening(false);
    }
  };

  // ==========================================
  // TEXT COMMAND HANDLER
  // ==========================================
  const handleTextCommand = async () => {
    if (!textInput.trim()) return;

    setTranscript(textInput);
    setStatus("THINKING");
    await sendToBackend(textInput);
    setTextInput("");
    setStatus("IDLE");
  };

  // ==========================================
  // BRAIN ENGINE (Backend + Speech)
  // ==========================================
  const sendToBackend = async (text) => {
    try {
      const res = await fetch("http://127.0.0.1:8000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: text, user_id: "umar" }),
      });

      const data = await res.json();
      console.log(data);

      const aiReply = data.reply || "Executed command.";
      setResponse(aiReply);

      // Text-to-Speech
      const speech = new SpeechSynthesisUtterance(aiReply);
      speech.rate = 1;
      speech.pitch = 1;
      speech.volume = 1;
      speech.lang = "en-US";
      window.speechSynthesis.cancel();
      window.speechSynthesis.speak(speech);

      // Execute Electron task if any
      if (data.intent && window.eleAPI) {
        window.eleAPI.executeTask({
          intent: data.intent,
          target: data.target,
          rawText: text,
        });
      }
    } catch (error) {
      console.error("[ELE] Core: Backend connection failure.", error);
      setResponse("Critical core connection failure.");
      setStatus("ERROR");
    }
  };

  // ==========================================
  // CLEANUP
  // ==========================================
  useEffect(() => {
    return () => {
      isPollingRef.current = false;
    };
  }, []);

  // ==========================================
  // DATE + TIME
  // ==========================================
  const [dateTime, setDateTime] = useState(new Date());
  useEffect(() => {
    const timer = setInterval(() => setDateTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  // ==========================================
  // UI
  // ==========================================
  return (
    <div className={`app-root ${status.toLowerCase()}`}>
      {/* FLOATING HUD BUTTONS */}
      <HUDButton icon="◉" top="170px" />
      <HUDButton icon="⬡" top="250px" />
      <HUDButton icon="⌘" top="330px" />
      <HUDButton icon="✦" top="410px" />
      <HUDButton icon="◎" top="490px" />

      <div className="hud-grid-overlay"></div>

      <div className="hud-container">
        {/* HEADER */}
        <header className="hud-header">
          <div className="header-left">
            <span className="status-indicator">
              SYSTEM STATUS:
              <span className={`status-text ${status.toLowerCase()}`}>
                {status}
              </span>
            </span>
          </div>
          <div className="header-center">
            <div className="version-pill-hud">
              ELE // 3.0 CORE
              <span className="beta-tag-hud">STABLE</span>
            </div>
          </div>
          <div className="header-right">
            <span className="datetime-display">
              {dateTime
                .toLocaleDateString("en-US", {
                  weekday: "short",
                  month: "short",
                  day: "numeric",
                })
                .toUpperCase()}{" // "}
              {dateTime.toLocaleTimeString("en-US", {
                hour: "2-digit",
                minute: "2-digit",
                hour12: false,
              })}
            </span>
          </div>
        </header>

        {/* MAIN SECTION */}
        <main className="hud-main">
          {/* LEFT PANEL */}
          <aside className="hud-panel panel-left">
            <div className="panel-header">NETWORK_STATUS</div>
            <div className="panel-content monospace">
              <DiagnosticsPanel />
              <div>UPLINK: ACTIVE</div>
              <div>LATENCY: 24ms</div>
              <div>IP: 192.168.1.103</div>
              <div className="separator"></div>
              <div>CORE_TEMP: 42°C</div>
              <div>FAN_SPEED: 1200 RPM</div>
            </div>
          </aside>

          {/* CENTER - REACTOR */}
          <section className="hud-center">
            <ReactorCore status={status} />
            <CircularRadar />
          </section>

          {/* RIGHT PANEL */}
          <aside className="hud-panel panel-right">
            <div className="panel-header">COMMAND_INTERFACE</div>
            <VoiceConsole
              transcript={transcript}
              response={response}
              status={status}
            />
          </aside>
        </main>

        {/* FOOTER */}
        <footer className="hud-footer">
          <div className="footer-left">
            <button className="hud-icon-btn">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M3 12h18M3 6h18M3 18h18" />
              </svg>
            </button>
          </div>

          <div className="footer-center">
            <div className="mic-wrapper-hud">
              {/* Text Command Bar */}
              <div className="text-command-bar">
                <input
                  type="text"
                  placeholder="TYPE COMMAND..."
                  value={textInput}
                  onChange={(e) => setTextInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") handleTextCommand();
                  }}
                />
                <button onClick={handleTextCommand}>EXECUTE</button>
              </div>

              {/* Voice Waves */}
              {isListening && (
                <div className="mic-waves">
                  <div className="wave-hud wave1"></div>
                  <div className="wave-hud wave2"></div>
                </div>
              )}

              {/* Mic Button */}
              <button
                className={`mic-btn-hud ${status.toLowerCase()}`}
                onClick={startListening}
                disabled={status === "THINKING"}
              >
                <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5">
                  <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" />
                  <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
                  <line x1="12" y1="19" x2="12" y2="23" />
                  <line x1="8" y1="23" x2="16" y2="23" />
                </svg>
              </button>
            </div>
          </div>

          <div className="footer-right">
            <button className="hud-icon-btn red-hover">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M18.36 6.64a9 9 0 1 1-12.73 0" />
                <line x1="12" y1="2" x2="12" y2="12" />
              </svg>
            </button>
          </div>
        </footer>
      </div>
    </div>
  );
}

export default App;