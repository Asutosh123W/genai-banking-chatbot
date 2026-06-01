import { useState, useEffect, useRef } from "react";
import "../App.css";
import { useAuth } from "../context/AuthContext";
import ReactMarkdown from "react-markdown";
import {apiFetch} from "../services/api";

function Dashboard() {

  const {
  logout,
  user
} = useAuth();
  const { token } = useAuth();

  const [showProfileMenu,
  setShowProfileMenu] =
  useState(false);

  const [message, setMessage] = useState("");
  const [chatHistory, setChatHistory] = useState([]);
  const [sessions, setSessions] =
  useState([]);

const [currentSessionId,
  setCurrentSessionId] =
  useState(null);
  
  const [sessionSearch,
  setSessionSearch] =
  useState("");

  const [loading, setLoading] = useState(false);

  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadMessage, setUploadMessage] = useState("");
  const [knowledgeBase, setKnowledgeBase] =
  useState("general");
  const [documents, setDocuments] =
  useState([]);
  const [stats, setStats] =
  useState({
    total_documents: 0,
    total_chunks: 0
  });

  const chatContainerRef = useRef(null);

  const createSession = async () => {

  try {

    const response = await apiFetch(
      "http://127.0.0.1:8000/sessions",
      {
        method: "POST",
        headers: {
          Authorization:
            `Bearer ${token}`
        }
      },
      logout
    );

    const data =
      await response.json();

    await fetchSessions();

    setCurrentSessionId(
      data.id
    );

    setChatHistory([]);

  } catch (error) {

    console.log(error);

  }

};

const fetchSessions = async () => {

  console.log("TOKEN:", token);

  try {

    const response = await apiFetch(
      "http://127.0.0.1:8000/sessions",
      {
        headers: {
          Authorization:
            `Bearer ${token}`
        }
      },
      logout
    );

    const data =
      await response.json();

      console.log(
  "Sessions API:",
  data
);

    if (
  Array.isArray(data)
) {

  if (
  Array.isArray(data)
) {

  setSessions(data);

} else {

  setSessions([]);

}

} else {

  console.error(
    "Sessions API Error:",
    data
  );

  setSessions([]);

}

  } catch (error) {

    console.log(error);

  }

};

const loadSession = async (
  sessionId
) => {

  try {

    const response = await fetch(
      `http://127.0.0.1:8000/sessions/${sessionId}/messages`,
      {
        headers: {
          Authorization:
            `Bearer ${token}`
        }
      }
    );

    const data =
      await response.json();

    const formattedMessages =
      data.map((msg) => ({

        type:
          msg.sender === "user"
            ? "user"
            : "bot",

        text: msg.content,

        sources:
          msg.sources
            ? msg.sources
                .split(",")
                .filter(Boolean)
            : [],

        time: ""

      }));

    setChatHistory(
      formattedMessages
    );

    setCurrentSessionId(
      sessionId
    );

  } catch (error) {

    console.log(error);

  }

};

const deleteSession = async (
  sessionId
) => {

  const confirmDelete =
    window.confirm(
      "Delete this chat?"
    );

  if (!confirmDelete)
    return;

  try {

    await fetch(
      `http://127.0.0.1:8000/sessions/${sessionId}`,
      {
        method: "DELETE",
        headers: {
          Authorization:
            `Bearer ${token}`
        }
      },
      logout
    );

    fetchSessions();

    if (
      currentSessionId ===
      sessionId
    ) {

      setCurrentSessionId(
        null
      );

      setChatHistory([]);

    }

  } catch (error) {

    console.log(error);

  }

};

const renameSession = async (
  sessionId,
  currentTitle
) => {

  const newTitle =
    prompt(
      "Rename chat",
      currentTitle
    );

  if (
    !newTitle ||
    !newTitle.trim()
  ) {
    return;
  }

  try {

    await fetch(
      `http://127.0.0.1:8000/sessions/${sessionId}`,
      {
        method: "PUT",

        headers: {
          "Content-Type":
            "application/json",

          Authorization:
            `Bearer ${token}`
        },

        body: JSON.stringify({
          title: newTitle
        })
      },
      logout
    );

    fetchSessions();

  } catch (error) {

    console.log(error);

  }

};


  const fetchDocuments = async () => {

  try {

    const response = await apiFetch(
  `http://127.0.0.1:8000/documents/${knowledgeBase}`,
  {
    headers: {
      Authorization:
        `Bearer ${token}`
    }
  },
  logout
);

    const data = await response.json();

    setDocuments(
      data.documents || []
    );

  } catch (error) {

    console.log(error);

  }

};

const fetchStats = async () => {

  try {

    const response = await apiFetch(
  `http://127.0.0.1:8000/documents/${knowledgeBase}`,
  {
    headers: {
      Authorization:
        `Bearer ${token}`
    }
  },
  logout
);

    const data = await response.json();

    setStats(data);

  } catch (error) {

    console.log(error);

  }

};

const deleteDocument = async (filename) => {

  const confirmDelete = window.confirm(
    `Delete ${filename}?`
  );

  if (!confirmDelete) {
    return;
  }

  try {

    await fetch(
  `http://127.0.0.1:8000/documents/${knowledgeBase}/${filename}`,
  {
    method: "DELETE",

    headers: {
      Authorization:
        `Bearer ${token}`
    }
  }
);

    fetchDocuments();
    fetchStats();

  } catch (error) {

    console.log(error);

  }

};

 useEffect(() => {

  fetchDocuments();
  fetchStats();
  fetchSessions();

}, [knowledgeBase]);

useEffect(() => {

  if (
    sessions.length > 0 &&
    !currentSessionId
  ) {

    loadSession(
      sessions[0].id
    );

  }

}, [
  sessions,
  currentSessionId
]);

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

  const exportChat = () => {

  if (chatHistory.length === 0) {

    alert(
      "No chat available to export."
    );

    return;
  }

  let content = "";

  chatHistory.forEach((message) => {

    content +=
      `${message.type.toUpperCase()}\n`;

    content +=
      `${message.text}\n\n`;

    if (
      message.sources &&
      message.sources.length > 0
    ) {

      content +=
        `Sources: ${message.sources.join(", ")}\n\n`;
    }

    content +=
      "-----------------------------------\n\n";

  });

  const blob = new Blob(
    [content],
    {
      type: "text/plain"
    }
  );

  const url =
    URL.createObjectURL(
      blob
    );

  const link =
    document.createElement(
      "a"
    );

  link.href = url;

  link.download =
    "chat-history.txt";

  link.click();

  URL.revokeObjectURL(
    url
  );
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

formData.append(
  "knowledge_base",
  knowledgeBase
);

    try {

      const response = await fetch(
  "http://127.0.0.1:8000/upload",
  {
    method: "POST",

    headers: {
      Authorization:
        `Bearer ${token}`
    },

    body: formData
  }
);

      const data = await response.json();

      setUploadMessage(
        `Uploaded successfully: ${data.filename}`
      );

      fetchDocuments();
      fetchStats();

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
    "application/json",

  Authorization:
    `Bearer ${token}`
},
          body: JSON.stringify({
  message: userMessage,
  knowledge_base:
    knowledgeBase,
  session_id:
    currentSessionId
})
        },
        logout
      );

      const data = await response.json();

setChatHistory((prev) => [
  ...prev,
  {
    type: "bot",
    text:
      data.response ||
      "No response generated",

    sources:
      data.sources || [],

    time: getCurrentTime()
  }
]);

fetchSessions();

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

  const filteredSessions =
  sessions.filter((session) =>

    session.title
      .toLowerCase()
      .includes(
        sessionSearch
          .toLowerCase()
      )

  );

  return (

  <div className="app-layout">

    <div className="sidebar">

      <div className="sidebar-header">

        <button
          className="new-chat-btn"
          onClick={createSession}
        >
          + New Chat
        </button>

      </div>

      <div className="session-search-container">

  <input
    type="text"
    placeholder="🔍 Search chats..."
    value={sessionSearch}
    onChange={(e) =>
      setSessionSearch(
        e.target.value
      )
    }
    className="session-search-input"
  />

</div>

      <div className="sessions-list">

        {filteredSessions.map((session) => (

          <div
  key={session.id}
  className={
    currentSessionId === session.id
      ? "session-item active"
      : "session-item"
  }
>

  <div
    className="session-title"
    onClick={() =>
      loadSession(
        session.id
      )
    }
  >

    {session.title}

  </div>

  <div className="session-actions">

    <button
      className="rename-session-btn"
      onClick={(e) => {

        e.stopPropagation();

        renameSession(
          session.id,
          session.title
        );

      }}
    >

      ✏️

    </button>

    <button
      className="delete-session-btn"
      onClick={(e) => {

        e.stopPropagation();

        deleteSession(
          session.id
        );

      }}
    >

      ✕

    </button>

  </div>

</div>

        ))}

      </div>

    </div>

    <div className="main-content">

      <div className="app">

  {/* Hero Section */}
  <div className="hero-section">

    <div className="profile-section">

  <button
    className="profile-btn"
    onClick={() =>
      setShowProfileMenu(
        !showProfileMenu
      )
    }
  >

    👤 {user?.username} ▼

  </button>

  {showProfileMenu && (

    <div
      className="profile-dropdown"
    >

      <div
        className="profile-header"
      >

        <strong>
          {user?.username}
        </strong>

        <p>
          {user?.email}
        </p>

      </div>

      <button
        className="dropdown-item"
      >
        Profile
      </button>

      <button
        className="dropdown-item logout-item"
        onClick={logout}
      >
        Logout
      </button>

    </div>

  )}

</div>

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

          {/* Knowledge Base Dropdown */}
  <div className="kb-section">

    <label className="kb-label">
      Knowledge Base
    </label>

    <select
      className="kb-select"
      value={knowledgeBase}
      onChange={(e) =>
        setKnowledgeBase(e.target.value)
      }
    >
      <option value="general">
        General
      </option>

      <option value="hr">
        HR
      </option>

      <option value="finance">
        Finance
      </option>

      <option value="legal">
        Legal
      </option>

      <option value="research">
        Research
      </option>

    </select>

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

      {/* Documents Dashboard */}

<div className="documents-section">

  <h2>
    📚 {knowledgeBase.toUpperCase()} Knowledge Base
  </h2>

  <div className="documents-card">

  {/* Statistics */}

  <div className="stats-section">

    <div className="stat-box">

      <span className="stat-label">
        Documents
      </span>

      <span className="stat-value">
        {stats.total_documents}
      </span>

    </div>

    <div className="stat-box">

      <span className="stat-label">
        Chunks
      </span>

      <span className="stat-value">
        {stats.total_chunks}
      </span>

    </div>

  </div>

  {documents.length === 0 ? (

  <p className="empty-docs">
    No documents uploaded.
  </p>

) : (

  documents.map(
    (doc, index) => (

      <div
        key={index}
        className="document-item"
      >

        <span>
          📄 {doc}
        </span>

        <button
          className="delete-doc-btn"
          onClick={() =>
            deleteDocument(doc)
          }
        >
          Delete
        </button>

      </div>

    ))
)}

  <div className="document-count">

    Total Documents:
    {" "}
    {documents.length}

  </div>

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

        <button
  onClick={exportChat}
>
  📤 Export Chat
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

  <div className="message-content">

  <ReactMarkdown>
    {chat.text}
  </ReactMarkdown>

</div>

{chat.type === "bot" && (

  <div className="message-actions">

    <button
      className="action-btn"
      onClick={() =>
        navigator.clipboard.writeText(
          chat.text
        )
      }
    >

      📋 Copy

    </button>

     <button
      className="action-btn"
      onClick={() => {

        const blob = new Blob(
          [chat.text],
          {
            type: "text/plain"
          }
        );

        const url =
          URL.createObjectURL(
            blob
          );

        const link =
          document.createElement(
            "a"
          );

        link.href = url;

        link.download =
          "answer.txt";

        link.click();

        URL.revokeObjectURL(
          url
        );

      }}
    >
      ⬇ Download
    </button>

  </div>

)}

  {chat.sources &&
    chat.sources.length > 0 && (

      <div className="sources-section">

        <div className="sources-title">
          📄 Sources
        </div>

        {chat.sources.map(
          (source, sourceIndex) => (
            <div
              key={sourceIndex}
              className="source-chip"
            >
              📄 {source}
            </div>
          )
        )}

      </div>

    )}

</div>

            <span className="timestamp">
              {chat.time}
            </span>

          </div>

        ))}

        {loading && (

          <div className="chat-wrapper bot-wrapper">

            <div className="chat-bubble bot thinking-bubble">
              🤖 AI is thinking...
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

  </div>

</div>

);

}

export default Dashboard;