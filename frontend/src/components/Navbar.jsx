import { useNavigate } from "react-router-dom";

export default function Navbar() {
  const navigate = useNavigate();

  return (
    <nav className="navbar">
      <div className="navbar-logo">datamind.</div>
      <div className="navbar-actions">
        <button className="btn-ghost" onClick={() => navigate("/")}>Sign up</button>
        <button className="btn-primary-nav" onClick={() => navigate("/")}>Log in</button>
      </div>
    </nav>
  );
}
