import PageHeader from "../components/PageHeader";
import { InboxIcon } from "../components/Icon";
import { MOCK_ITEMS } from "../mockData";

export default function ListPage({ section = "01", title = "List", items = "internships" }) {
  const rows = MOCK_ITEMS[items] ?? [];

  return (
    <>
      <PageHeader step={section} title={title} />

      {rows.length === 0 ? (
        <div className="card empty-state">
          <div className="empty-state-icon">
            <InboxIcon width={22} height={22} />
          </div>
          <h2>Nothing here yet</h2>
          <p>Once there's {items} to show, they'll show up here.</p>
        </div>
      ) : (
        <div className="card">
          <div className="label" style={{ marginBottom: 14 }}>
            {rows.length} {items}
          </div>
          <ul className="simple-list">
            {rows.map((row) => (
              <li key={row.name}>
                <div>
                  <div className="name">{row.name}</div>
                  <div className="meta">{row.meta}</div>
                </div>
                <span className="pill">View</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </>
  );
}
