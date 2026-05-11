import { Link, NavLink, Outlet } from "react-router-dom";

import "../styles/app.css";
import "../styles/list.css";
import "../styles/nav.css";

const navLinkClass = ({ isActive }: { isActive: boolean }) =>
  "navLink" + (isActive ? " navLinkActive" : "");

export default function AppLayout() {
  return (
    <div className="app">
      <header className="nav">
        <div className="navInner">
          <Link to="/" className="brand brandLink">
            LeadsForge
          </Link>
          <nav className="navActions" aria-label="Primary">
            <NavLink to="/" className={navLinkClass} end>
              Home
            </NavLink>
            <NavLink to="/leads" className={navLinkClass}>
              Leads
            </NavLink>
            <NavLink to="/metrics" className={navLinkClass}>
              Metrics
            </NavLink>
            <NavLink to="/subscriptions" className={navLinkClass}>
              Subscriptions
            </NavLink>
            <NavLink to="/settings" className={navLinkClass}>
              Settings
            </NavLink>
          </nav>
        </div>
      </header>

      <main className="container">
        <Outlet />
      </main>
    </div>
  );
}
