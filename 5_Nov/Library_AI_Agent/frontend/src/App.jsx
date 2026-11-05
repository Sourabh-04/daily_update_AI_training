import { useState } from 'react'
import './App.css'

const API_URL = 'http://localhost:8000'

export default function App() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [pending, setPending] = useState(null)
  const [loading, setLoading] = useState(false)


  async function callApi(path, body) {
    setLoading(true)
    try {
      const response = await fetch(API_URL + path, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })
      const data = await response.json()
      setMessages((prev) => [...prev, { role: 'bot', text: data.reply, tool: data.tool_used }])
      setPending(data.pending) // null unless a reservation needs confirming
    } catch {
      setMessages((prev) => [...prev, { role: 'bot', text: 'Cannot reach the server on port 8000.' }])
    }
    setLoading(false)
  }

    function sendMessage(event) {
    event.preventDefault() // stop the page from reloading
    if (!input.trim()) return
    setMessages((prev) => [...prev, { role: 'user', text: input }])
    callApi('/api/chat', { message: input })
    setInput('')
  }

  function answer(confirmed) {
    callApi('/api/confirm', { ...pending, confirmed })
    setPending(null) // hide the buttons
  }
  return (
    <div className="chat">
      <h2>📖 AI Library Assistant</h2>

      <div className="messages">
        {messages.map((msg, i) => (
          <div key={i} className={msg.role}>
            <p>{msg.text}</p>
            {msg.tool && <small>Tool used: {msg.tool}</small>}
          </div>
        ))}
        {loading && <p className="bot">Thinking…</p>}
      </div>
      {pending && (
        <div>
          <button onClick={() => answer(true)} disabled={loading}>Confirm</button>
          <button onClick={() => answer(false)} disabled={loading}>Cancel</button>
        </div>
      )}

      <form onSubmit={sendMessage}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
        />
        <button disabled={loading}>Send</button>
      </form>
    </div>
  )
}