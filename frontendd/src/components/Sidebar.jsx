import { Link, useLocation } from "react-router-dom";
import { SIDEBAR_NAV, PORTAL_LABEL } from "../sidebarNav";
import Logo from "./Logo";

export default function Sidebar({ portal, basePath }) {
  const location = useLocation();
  const sections = SIDEBAR_NAV[portal] ?? [];

  return (
    <aside className="sidebar">
      <Link to="/" className="sidebar-brand" onClick={(e) => e.currentTarget.blur()}>
        <Logo size="sm" />
      </Link>

      <div className="sidebar-portal-tag">{PORTAL_LABEL[portal]} portal</div>

      <nav className="sidebar-nav">
        {sections.map((section, idx) => (
          <div className="sidebar-section" key={section.group ?? `top-${idx}`}>
            {section.group && <div className="sidebar-group-label">{section.group}</div>}
            {section.items.map((item) => {
              const target = `${basePath}${item.to}`.replace(/\/+$/, "") || basePath;
              const isActive = location.pathname === target || location.pathname === `${target}/`;
              return (
                <Link
                  key={item.label}
                  to={target}
                  className={`sidebar-link${isActive ? " active" : ""}`}
                  onClick={(e) => e.currentTarget.blur()}
                >
                  {item.label}
                </Link>
              );
            })}
          </div>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="sidebar-user-row">
          <span className="avatar-chip">S</span>
          <span className="sidebar-username">suraj</span>
        </div>

        <Link to="/" className="sidebar-logout" onClick={(e) => e.currentTarget.blur()}>
          <span>&larr;</span>
          <span>Sign out</span>
        </Link>
      </div>
    </aside>
  );
}
