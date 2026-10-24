import { useState } from "react";
import { Link } from "react-router-dom";
import PageHeader from "../../components/PageHeader";
import { CheckIcon, BriefcaseIcon } from "../../components/Icon";
import { accentColor } from "../../accentColors";
import { DEMO } from "../../routes";

const COMPANIES = [
  { id: "demo-co", name: "Veridex Labs", verified: true, openRoles: 4, location: "Bengaluru, India" },
  { id: "co-2", name: "Northwind Analytics", verified: true, openRoles: 2, location: "Hyderabad, India" },
  { id: "co-3", name: "Acme Robotics", verified: false, openRoles: 1, location: "Remote" },
];

export default function Companies({ section = "01", title = "Companies" }) {
  const [companies] = useState(COMPANIES);

  return (
    <>
      <PageHeader step={section} title={title} />

      <div className="label" style={{ marginBottom: 14 }}>
        {companies.length} companies
      </div>

      <div className="company-grid">
        {companies.map((c) => (
          <div className="company-card" key={c.id}>
            <div className="company-card-top">
              <div className="company-logo" style={{ background: accentColor(c.name) }}>
                {c.name[0]}
              </div>
              {c.verified ? (
                <span className="badge badge-success">
                  <CheckIcon width={11} height={11} /> Verified
                </span>
              ) : (
                <span className="badge badge-warning">Pending verification</span>
              )}
            </div>
            <div className="company-name">{c.name}</div>
            <div className="company-meta">{c.location}</div>
            <div className="company-roles">
              <BriefcaseIcon width={13} height={13} /> {c.openRoles} open role{c.openRoles === 1 ? "" : "s"}
            </div>
            <Link to={`/employer/company/${c.id}/overview`} className="btn-secondary company-manage">
              Manage
            </Link>
          </div>
        ))}

        <Link to={`/employer/company/${DEMO.companyId}/overview`} className="company-card company-card-add">
          <span className="company-add-icon">+</span>
          <span>Add a company</span>
        </Link>
      </div>
    </>
  );
}
