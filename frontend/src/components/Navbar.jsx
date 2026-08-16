function Navbar() {
  return (
    <nav className="navbar">
      <div className="logo">
        CampusMind AI
      </div>

      <div className="nav-links">
        <button>Dashboard</button>
        <button>My Materials</button>
        <button>Logout</button>
      </div>
    </nav>
  );
}

export default Navbar;