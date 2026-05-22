import { useState, useEffect, useRef } from "react";
import "./App.css";

function App() {

  const [message, setMessage] = useState("");
  const [chatHistory, setChatHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadMessage, setUploadMessage] = useState("");

  const chatContainerRef = useRef(null);

  // Load chat history
  useEffect(() => {

    const savedChats =
      localStorage.getItem("chatHistory");

    if (savedChats) {
      setChatHistory(JSON.parse(savedChats));
    }

  }, []);

  // Save chat history
  useEffect(() => {

    localStorage.setItem(
      "chatHistory",
      JSON.stringify(chatHistory)
    );

  }, [chatHistory]);

  // Auto scroll
  useEffect(() => {

    if (chatContainerRef.current) {

      chatContainerRef.current.scrollTop =
        chatContainerRef.current.scrollHeight;

    }

  }, [chatHistory, loading]);

  const getCurrentTime = () => {

    return new Date().toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit"
    });

  };

  const clearChat = () => {

    setChatHistory([]);
    localStorage.removeItem("chatHistory");

  };

  // Upload document
  const uploadDocument = async () => {

    if (!selectedFile) {

      setUploadMessage(
        "Please select a file."
      );

      return;
    }

    const formData = new FormData();

    formData.append(
      "file",
      selectedFile
    );

    try {

      const response = await fetch(
        "http://127.0.0.1:8000/upload",
        {
          method: "POST",
          body: formData
        }
      );

      const data = await response.json();

      setUploadMessage(
        `Uploaded successfully: ${data.filename}`
      );

    } catch (error) {

      console.log(error);

      setUploadMessage(
        "Upload failed."
      );

    }

  };

  // Ask question
  const askQuestion = async () => {

    if (!message.trim()) return;

    const userMessage = message;

    setChatHistory((prev) => [
      ...prev,
      {
        type: "user",
        text: userMessage,
        time: getCurrentTime()
      }
    ]);

    setMessage("");
    setLoading(true);

    try {

      const response = await fetch(
        "http://127.0.0.1:8000/chat",
        {
          method: "POST",
          headers: {
            "Content-Type":
              "application/json"
          },
          body: JSON.stringify({
            message: userMessage
          })
        }
      );

      const data = await response.json();

      setChatHistory((prev) => [
        ...prev,
        {
          type: "bot",
          text:
            data.response ||
            "No response generated",
          time: getCurrentTime()
        }
      ]);

    } catch (error) {

      console.log(error);

      setChatHistory((prev) => [
        ...prev,
        {
          type: "bot",
          text:
            "Error connecting to backend.",
          time: getCurrentTime()
        }
      ]);

    }

    setLoading(false);

  };

  return (

    <div className="app">

      {/* Hero Section */}
      <div className="hero-section">

        <div className="logo-circle">
          🤖
        </div>

        <h1>
          GenAI Banking Chatbot
        </h1>

       <p className="subtitle">
  Intelligent RAG-powered AI Assistant for Document Question Answering
</p>

<p className="backend-note">
  Backend currently runs locally using Ollama + Mistral.
</p>

      </div>

      {/* Upload Section */}
      <div className="upload-section">

        <div className="upload-card">

          <div className="upload-icon">
            📄
          </div>

          <input
            type="file"
            accept=".pdf,.txt"
            className="file-input"
            onChange={(e) =>
              setSelectedFile(
                e.target.files[0]
              )
            }
          />

          {selectedFile && (

            <p className="selected-file">
              {selectedFile.name}
            </p>

          )}

          <button
            className="upload-btn"
            onClick={uploadDocument}
          >
            Upload Document
          </button>

          {uploadMessage && (

            <p className="upload-message">
              {uploadMessage}
            </p>

          )}

        </div>

      </div>

      {/* Clear Chat */}
      <div className="top-actions">

        <button
          className="clear-btn"
          onClick={clearChat}
        >
          Clear Chat
        </button>

      </div>

      {/* Chat Area */}
      <div
        className="chat-container"
        ref={chatContainerRef}
      >

        {chatHistory.map((chat, index) => (

          <div
            key={index}
            className={
              chat.type === "user"
                ? "chat-wrapper user-wrapper"
                : "chat-wrapper bot-wrapper"
            }
          >

            <div
              className={
                chat.type === "user"
                  ? "chat-bubble user"
                  : "chat-bubble bot"
              }
            >
              {chat.text}
            </div>

            <span className="timestamp">
              {chat.time}
            </span>

          </div>

        ))}

        {loading && (

          <div className="chat-wrapper bot-wrapper">

            <div className="chat-bubble bot">
              Thinking...
            </div>

          </div>

        )}

      </div>

      {/* Input */}
      <div className="input-section">

        <textarea
          placeholder="Ask your question..."
          value={message}
          onChange={(e) =>
            setMessage(e.target.value)
          }
          onKeyDown={(e) => {

            if (
              e.key === "Enter" &&
              !e.shiftKey
            ) {

              e.preventDefault();
              askQuestion();

            }

          }}
        />

        <button
          onClick={askQuestion}
          disabled={loading}
        >
          {loading
            ? "Thinking..."
            : "Ask"}
        </button>

      </div>

    </div>

  );

}

export default App;