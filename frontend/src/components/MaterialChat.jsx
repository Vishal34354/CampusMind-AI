import { useState } from "react";
import "./MaterialChat.css";

function MaterialChat({ material, onBack }) {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const askQuestion = async () => {
    if (!question.trim()) {
      return;
    }

    setLoading(true);
    setError("");
    setAnswer("");
    setSources([]);

    try {
      const token = localStorage.getItem("access_token");

      const response = await fetch(
        `http://127.0.0.1:8000/api/v1/materials/${material.id}/ask`,
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },

          body: JSON.stringify({
            question: question,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Failed to get answer"
        );
      }

      setAnswer(data.answer);
      setSources(data.sources || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-page">

      {/* Navbar */}
      <nav className="navbar">
        <div className="logo">
          CampusMind AI
        </div>

        <div className="nav-links">
          <button>My Materials</button>
          <button>Logout</button>
        </div>
      </nav>


      {/* Main */}
      <main className="chat-container">

        <button
          className="back-button"
          onClick={onBack}
        >
          ← Back to Materials
        </button>


        {/* Material information */}
        <section className="material-header">

          <h1>{material.title}</h1>

          <p className="material-filename">
            {material.filename}
          </p>

        </section>


        {/* Chat */}
        <section className="chat-card">

          <label className="question-label">
            Ask a question about this material
          </label>

          <textarea
            className="question-input"
            placeholder="Example: What is the difference between TCP and UDP?"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
          />

          <button
            className="ask-button"
            onClick={askQuestion}
            disabled={loading}
          >
            {loading
              ? "Thinking..."
              : "Ask CampusMind"}
          </button>


          {/* Error */}
          {error && (
            <div className="error-message">
              {error}
            </div>
          )}


          {/* Answer */}
          {answer && (
            <div className="answer-section">

              <h2>AI Answer</h2>

              <div className="answer">
                {answer}
              </div>


              {/* Sources */}
              {sources.length > 0 && (
                <div className="sources">

                  <h3>Sources</h3>

                  {sources.map((source, index) => (
                    <span
                      className="source-item"
                      key={index}
                    >
                      Chunk {source.chunk_index}
                      {" • "}
                      Score {source.score.toFixed(3)}
                    </span>
                  ))}

                </div>
              )}

            </div>
          )}

        </section>

      </main>

    </div>
  );
}

export default MaterialChat;