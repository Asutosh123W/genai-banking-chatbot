import { useState, useEffect, useRef } from "react";
import "../App.css";
import { useAuth } from "../context/AuthContext";
import ReactMarkdown from "react-markdown";
import {apiFetch} from "../services/api";


function Dashboard() {

  const getCurrentTime = () => {

    return new Date().toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit"
    });

  };

  const {
  logout,
  user
} = useAuth();
  const { token } = useAuth();

  const [showProfileMenu,
  setShowProfileMenu] =
  useState(false);

  const [sidebarOpen, setSidebarOpen] =
  useState(true);

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

  const [analytics, setAnalytics] =
  useState({
    avg_relevancy: 0,
    avg_faithfulness: 0,
    avg_precision: 0,
    total_evaluations: 0
  });

  const qualityScore = (
  (
    analytics.avg_relevancy +
    analytics.avg_faithfulness +
    analytics.avg_precision
  ) / 3 * 100
).toFixed(1);

const getMetricStatus = (value) => {

  if (value >= 0.75) {

    return {
      label: "Good",
      className: "metric-good"
    };

  }

  if (value >= 0.50) {

    return {
      label: "Moderate",
      className: "metric-moderate"
    };

  }

  return {
    label: "Needs Improvement",
    className: "metric-poor"
  };

};

  const chatContainerRef = useRef(null);

  const createSession = async () => {

  try {

    const response = await apiFetch(
      "https://genai-rag-backend-asu-a8cjhsevdhbgftg9.centralindia-01.azurewebsites.net/sessions",
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
      "https://genai-rag-backend-asu-a8cjhsevdhbgftg9.centralindia-01.azurewebsites.net/sessions",
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

    const response = await apiFetch(
      `https://genai-rag-backend-asu-a8cjhsevdhbgftg9.centralindia-01.azurewebsites.net/sessions/${sessionId}/messages`,
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
       "SESSION DATA:",
        data
);

console.log(
  "SESSION DATA:",
  data
);

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

        time: msg.created_at
  ? new Date(
      msg.created_at + "Z"
    ).toLocaleTimeString(
      "en-IN",
      {
        timeZone: "Asia/Kolkata",
        hour: "2-digit",
        minute: "2-digit"
      }
    )
  : getCurrentTime()

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

    await apiFetch(
      `https://genai-rag-backend-asu-a8cjhsevdhbgftg9.centralindia-01.azurewebsites.net/sessions/${sessionId}`,
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

    await apiFetch(
      `https://genai-rag-backend-asu-a8cjhsevdhbgftg9.centralindia-01.azurewebsites.net/sessions/${sessionId}`,
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
  `https://genai-rag-backend-asu-a8cjhsevdhbgftg9.centralindia-01.azurewebsites.net/documents/${knowledgeBase}`,
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
  `https://genai-rag-backend-asu-a8cjhsevdhbgftg9.centralindia-01.azurewebsites.net/stats/${knowledgeBase}`,
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

const fetchAnalytics = async () => {

  try {

    const response =
      await apiFetch(
        "https://genai-rag-backend-asu-a8cjhsevdhbgftg9.centralindia-01.azurewebsites.net/analytics",
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

    setAnalytics(data);

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

    await apiFetch(
  `https://genai-rag-backend-asu-a8cjhsevdhbgftg9.centralindia-01.azurewebsites.net/documents/${knowledgeBase}/${filename}`,
  {
    method: "DELETE",

    headers: {
      Authorization:
        `Bearer ${token}`
    }
  },
  logout
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
  fetchAnalytics();
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

      const response = await apiFetch(
  "https://genai-rag-backend-asu-a8cjhsevdhbgftg9.centralindia-01.azurewebsites.net/upload",
  {
    method: "POST",

    headers: {
      Authorization:
        `Bearer ${token}`
    },

    body: formData
  },
  logout
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

    if (loading) return;


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

      const response = await apiFetch(
        "https://genai-rag-backend-asu-a8cjhsevdhbgftg9.centralindia-01.azurewebsites.net/chat-stream",
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

      const reader =
  response.body.getReader();

const decoder =
  new TextDecoder();

let streamedText = "";

const botMessageIndex =
  chatHistory.length + 1;

setChatHistory((prev) => [
  ...prev,
  {
    type: "bot",
    text: "",
    sources: [],
    time: getCurrentTime()
  }
]);

while (true) {

  const {
    done,
    value
  } = await reader.read();

  if (done) {
    await fetchAnalytics();
    break;
  }

  const chunk =
    decoder.decode(value);

  streamedText += chunk;

  setChatHistory((prev) => {

    const updated = [...prev];

    updated[
      updated.length - 1
    ] = {
      ...updated[
        updated.length - 1
      ],
      text: streamedText
    };

    return updated;

  });

}

await loadSession(
  currentSessionId
);

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

    <div
  className={
    sidebarOpen
      ? "sidebar"
      : "sidebar collapsed"
  }
>
  <div className="sidebar-topbar">

  <button
    className="sidebar-toggle"
    onClick={() =>
      setSidebarOpen(!sidebarOpen)
    }
  >
    ☰
  </button>

</div>

      {sidebarOpen && (

  <div className="sidebar-header">

    <button
      className="new-chat-btn"
      onClick={createSession}
    >
      + New Chat
    </button>

  </div>

)}

      {sidebarOpen && (
  <>
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
  </>
)}

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

  <div className="avatar-circle">
    {user?.username
      ?.charAt(0)
      ?.toUpperCase()}
  </div>

  <span>
    {user?.username}
  </span>

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
      FinIntel AI
    </h1>

    <p className="subtitle">
      Document Intelligence & Conversational Analytics
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

{/* =========================
    RAG EVALUATION DASHBOARD
========================= */}

<div className="analytics-section">

  <h3>
    📊 RAG Evaluation
  </h3>

  <div className="quality-score-card">

    <div className="quality-title">
      Overall RAG Score
    </div>

    <div className="quality-value">
      {qualityScore}%
    </div>

  </div>

  <div className="stats-section">

    <div className="stat-box">

  <span className="stat-label">
    Relevancy
  </span>

  <span className="stat-value">
    {(analytics.avg_relevancy * 100).toFixed(1)}%
  </span>

  <span
    className={
      getMetricStatus(
        analytics.avg_relevancy
      ).className
    }
  >

    {
      getMetricStatus(
        analytics.avg_relevancy
      ).label
    }

  </span>

</div>

    <div className="stat-box">

      <span className="stat-label">
        Faithfulness
      </span>

      <span className="stat-value">
  {(analytics.avg_faithfulness * 100).toFixed(1)}%
</span>

<span
  className={
    getMetricStatus(
      analytics.avg_faithfulness
    ).className
  }
>

  {
    getMetricStatus(
      analytics.avg_faithfulness
    ).label
  }

</span>

    </div>

    <div className="stat-box">

      <span className="stat-label">
        Precision
      </span>

      <span className="stat-value">
  {(analytics.avg_precision * 100).toFixed(1)}%
</span>

<span
  className={
    getMetricStatus(
      analytics.avg_precision
    ).className
  }
>

  {
    getMetricStatus(
      analytics.avg_precision
    ).label
  }

</span>

    </div>

    <div className="stat-box">

      <span className="stat-label">
        Evaluations
      </span>

      <span className="stat-value">
        {analytics.total_evaluations}
      </span>

    </div>

  </div>

</div>

{/* Documents List Starts Here */}

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
          🗑 Clear Chat
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

  {chatHistory.length === 0 && !loading && (

    <div className="welcome-screen">

      <div className="welcome-icon">
        🤖
      </div>

      <h2>
        Welcome to FinIntel AI
      </h2>

      <p>
        Ask questions from your uploaded documents and knowledge bases.
      </p>

      <div className="welcome-features">

        <div>
          📄 Upload & Analyze Documents
        </div>

        <div>
          🧠 AI-Powered Retrieval Augmented Generation
        </div>

        <div>
          📊 Built-in RAG Evaluation Metrics
        </div>

        <div>
          💬 Multi-Session Conversational Memory
        </div>

      </div>

    </div>

  )}

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