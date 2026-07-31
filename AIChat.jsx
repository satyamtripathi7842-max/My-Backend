import React, { useState, useRef, useEffect } from "react";
import api from "./api.js";

export default function AIChat() {
  const [messages, setMessages] = useState([
    { role: "assistant", text: "SentinelX-AI online. Ask me about supplier risk, alerts, or critical exposure." },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function send(e) {
    e.preventDefault();
    if (!input.trim()) return;
    const question = input;
    setMessages((m) => [...m, { role: "user", text: question }]);
    setInput("");
    setLoading(true);
    try {
      const res = await api.post("/chat", { question });
      setMessages((m) => [...m, { role: "assistant", text: res.data.answer }]);
    } catch {
      setMessages((m) => [...m, { role: "assistant", text: "Error reaching decision agent." }]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="sx-chat">
      <h1 className="sx-page__title">AI CHAT — DECISION AGENT</h1>
      <div className="sx-chat__window">
        {messages.map((m, i) => (
          <div key={i} className={`sx-chat__bubble sx-chat__bubble--${m.role}`}>
            {m.text}
          </div>
        ))}
        {loading && <div className="sx-chat__bubble sx-chat__bubble--assistant">Analyzing...</div>}
        <div ref={bottomRef} />
      </div>
      <form className="sx-chat__input" onSubmit={send}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask: which supplier is highest risk?"
        />
        <button type="submit" disabled={loading}>
          SEND
        </button>
      </form>
    </div>
  );
}
