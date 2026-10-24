import Sidebar from "./Sidebar";
import { DEMO } from "../routes";

const BASE_PATH = {
  user: `/user/${DEMO.username}/`,
  employer: `/employer/company/${DEMO.companyId}/`,
  moderator: `/moderator/${DEMO.username}/`,
};

export default function PortalShell({ portal, children }) {
  return (
    <div className="portal-shell">
      <Sidebar portal={portal} basePath={BASE_PATH[portal]} />
      <main className="portal-content">{children}</main>
    </div>
  );
}
