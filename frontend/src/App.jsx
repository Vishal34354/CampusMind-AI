import { useCallback, useEffect, useState } from "react";
import "./App.css";
import MaterialChat from "./components/MaterialChat";
import AdminUsers from "./pages/AdminUsers";
import Login from "./pages/Login";

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(
    Boolean(localStorage.getItem("access_token"))
  );

  const [currentUser, setCurrentUser] = useState(null);
  const [currentView, setCurrentView] = useState(
    window.location.pathname === "/admin/users" ? "admin" : "dashboard"
  );

  const [selectedMaterial, setSelectedMaterial] = useState(null);
  const [materials, setMaterials] = useState([]);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Upload states
  const [showUpload, setShowUpload] = useState(false);
  const [title, setTitle] = useState("");
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState("");
  const [uploadSuccess, setUploadSuccess] = useState("");

  // ==========================================
  // Fetch Current User
  // ==========================================

  const fetchCurrentUser = useCallback(async () => {
    try {
      const token = localStorage.getItem("access_token");
      if (!token) return;

      const response = await fetch("http://127.0.0.1:8000/api/v1/auth/me", {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const userData = await response.json();
        setCurrentUser(userData);
      }
    } catch (err) {
      console.error("Failed to fetch current user profile:", err);
    }
  }, []);

  // ==========================================
  // Fetch Materials
  // ==========================================

  const fetchMaterials = async () => {
    setLoading(true);
    setError("");

    try {
      const token = localStorage.getItem("access_token");

      const response = await fetch(
        "http://127.0.0.1:8000/api/v1/materials",
        {
          method: "GET",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const data = await response.json();

      console.log("Materials response:", data);

      if (!response.ok) {
        throw new Error(
          typeof data.detail === "string"
            ? data.detail
            : "Failed to fetch materials"
        );
      }

      setMaterials(data);
    } catch (err) {
      console.error("Materials error:", err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // ==========================================
  // Load Data After Login
  // ==========================================

  useEffect(() => {
    if (isLoggedIn) {
      fetchMaterials();
      fetchCurrentUser();
    }
  }, [isLoggedIn, fetchCurrentUser]);

  // Handle URL change / back button
  useEffect(() => {
    const handlePopState = () => {
      if (window.location.pathname === "/admin/users") {
        setCurrentView("admin");
      } else {
        setCurrentView("dashboard");
      }
    };

    window.addEventListener("popstate", handlePopState);
    return () => window.removeEventListener("popstate", handlePopState);
  }, []);

  // Navigation helpers
  const navigateTo = (view, path = "/") => {
    setCurrentView(view);
    setSelectedMaterial(null);
    if (window.location.pathname !== path) {
      window.history.pushState({}, "", path);
    }
  };

  // ==========================================
  // Logout
  // ==========================================

  const handleLogout = () => {
    localStorage.removeItem("access_token");

    setIsLoggedIn(false);
    setCurrentUser(null);
    setSelectedMaterial(null);
    setMaterials([]);
    setCurrentView("dashboard");
    if (window.location.pathname !== "/") {
      window.history.pushState({}, "", "/");
    }
  };

  // ==========================================
  // Select PDF
  // ==========================================

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];

    setUploadError("");
    setUploadSuccess("");

    if (!selectedFile) {
      setFile(null);
      return;
    }

    if (selectedFile.type !== "application/pdf") {
      setFile(null);
      setUploadError("Only PDF files are allowed.");
      return;
    }

    setFile(selectedFile);
  };

  // ==========================================
  // Upload Material
  // ==========================================

  const handleUpload = async (event) => {
    event.preventDefault();

    setUploadError("");
    setUploadSuccess("");

    if (!title.trim()) {
      setUploadError("Please enter a title.");
      return;
    }

    if (!file) {
      setUploadError("Please select a PDF file.");
      return;
    }

    setUploading(true);

    try {
      const token = localStorage.getItem("access_token");

      const formData = new FormData();

      formData.append("title", title.trim());
      formData.append("file", file);

      const response = await fetch(
        "http://127.0.0.1:8000/api/v1/materials/upload",
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
          body: formData,
        }
      );

      const data = await response.json();

      console.log("Upload response:", data);

      if (!response.ok) {
        throw new Error(
          typeof data.detail === "string"
            ? data.detail
            : "Failed to upload material"
        );
      }

      setUploadSuccess("Study material uploaded successfully!");

      setTitle("");
      setFile(null);

      const fileInput = document.getElementById("material-file");
      if (fileInput) fileInput.value = "";

      setTimeout(() => {
        setShowUpload(false);
        setUploadSuccess("");
      }, 1200);

      await fetchMaterials();
    } catch (err) {
      console.error("Upload error:", err);
      setUploadError(err.message);
    } finally {
      setUploading(false);
    }
  };

  // ==========================================
  // Login Page
  // ==========================================

  if (!isLoggedIn) {
    return (
      <Login
        onLogin={() => setIsLoggedIn(true)}
      />
    );
  }

  // ==========================================
  // Material Chat Page
  // ==========================================

  if (selectedMaterial) {
    return (
      <MaterialChat
        material={selectedMaterial}
        onBack={() => setSelectedMaterial(null)}
      />
    );
  }

  const isAdminUser =
    currentUser?.is_admin || currentUser?.role === "admin";

  // Navbar component reused across views
  const renderNavbar = () => (
    <nav className="navbar">
      <div className="logo" onClick={() => navigateTo("dashboard", "/")} style={{ cursor: "pointer" }}>
        CampusMind AI
      </div>

      <div className="nav-links">
        <button
          className={currentView === "dashboard" ? "active-nav" : ""}
          onClick={() => navigateTo("dashboard", "/")}
        >
          Dashboard
        </button>

        <button
          onClick={() => {
            navigateTo("dashboard", "/");
            setShowUpload(true);
            setUploadError("");
            setUploadSuccess("");
          }}
        >
          My Materials
        </button>

        {isAdminUser && (
          <button
            className={`admin-nav-btn ${currentView === "admin" ? "active-nav" : ""}`}
            onClick={() => navigateTo("admin", "/admin/users")}
          >
            👑 Admin Users
          </button>
        )}

        <button onClick={handleLogout}>Logout</button>
      </div>
    </nav>
  );

  // ==========================================
  // Admin Page View
  // ==========================================

  if (currentView === "admin") {
    return (
      <div className="app">
        {renderNavbar()}
        <AdminUsers
          currentUser={currentUser}
          onNavigateBack={() => navigateTo("dashboard", "/")}
        />
      </div>
    );
  }

  // ==========================================
  // Dashboard
  // ==========================================

  return (
    <div className="app">
      {renderNavbar()}


      {/* ================= MAIN ================= */}

      <main className="container">

        {/* ================= HERO ================= */}

        <section className="hero">

          <h1>
            Welcome to CampusMind AI
          </h1>

          <p>
            Your AI-powered study assistant
          </p>

        </section>


        {/* ================= MATERIAL HEADER ================= */}

        <section className="materials-header">

          <div>
            <h2 className="section-title">
              My Study Materials
            </h2>

            <p>
              Upload your notes and ask AI questions about them.
            </p>
          </div>

          <button
            className="upload-button"
            onClick={() => {
              setShowUpload(!showUpload);
              setUploadError("");
              setUploadSuccess("");
            }}
          >
            {showUpload
              ? "Cancel Upload"
              : "+ Upload Material"}
          </button>

        </section>


        {/* ================= UPLOAD FORM ================= */}

        {showUpload && (

          <section className="upload-card">

            <h2>
              Upload Study Material
            </h2>

            <p>
              Add a PDF to your personal study library.
            </p>

            <form onSubmit={handleUpload}>

              {/* Title */}

              <div className="form-group">

                <label htmlFor="material-title">
                  Material Title
                </label>

                <input
                  id="material-title"
                  type="text"
                  placeholder="e.g. Computer Networks"
                  value={title}
                  onChange={(e) =>
                    setTitle(e.target.value)
                  }
                  disabled={uploading}
                />

              </div>


              {/* File */}

              <div className="form-group">

                <label htmlFor="material-file">
                  PDF File
                </label>

                <input
                  id="material-file"
                  type="file"
                  accept=".pdf,application/pdf"
                  onChange={handleFileChange}
                  disabled={uploading}
                />

                {file && (
                  <p className="selected-file">
                    Selected: {file.name}
                  </p>
                )}

              </div>


              {/* Error */}

              {uploadError && (
                <div className="error-message">
                  {uploadError}
                </div>
              )}


              {/* Success */}

              {uploadSuccess && (
                <div className="success-message">
                  {uploadSuccess}
                </div>
              )}


              {/* Submit */}

              <button
                type="submit"
                className="upload-submit-button"
                disabled={uploading}
              >
                {uploading
                  ? "Uploading..."
                  : "Upload Material"}
              </button>

            </form>

          </section>

        )}


        {/* ================= MATERIALS ================= */}

        <section>

          {loading && (
            <p className="loading-message">
              Loading your materials...
            </p>
          )}


          {error && (
            <div className="error-message">
              {error}
            </div>
          )}


          {!loading &&
            !error &&
            materials.length === 0 && (

              <div className="empty-state">

                <h3>
                  No study materials yet
                </h3>

                <p>
                  Upload your first PDF to start
                  studying with CampusMind AI.
                </p>

                <button
                  className="upload-button"
                  onClick={() => setShowUpload(true)}
                >
                  + Upload Your First Material
                </button>

              </div>

            )}


          <div className="material-grid">

            {materials.map((material) => (

              <div
                className="material-card"
                key={material.id}
                onClick={() =>
                  setSelectedMaterial(material)
                }
              >

                <h3>
                  {material.title}
                </h3>

                <p className="filename">
                  {material.original_filename}
                </p>

                <span className="file-type">
                  {material.file_type.toUpperCase()}
                </span>

              </div>

            ))}

          </div>

        </section>

      </main>

    </div>
  );
}

export default App;