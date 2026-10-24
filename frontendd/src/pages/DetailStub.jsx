import { useParams } from "react-router-dom";
import PageHeader from "../components/PageHeader";

export default function DetailStub({ section = "01", title = "Detail" }) {
  const params = useParams();
  const entries = Object.entries(params);

  return (
    <>
      <PageHeader step={section} title={title} />

      <div className="card stub-card">
        <h1>{title}</h1>
        <p>
          This page mirrors <code className="mono">{title}</code> from ifind's route structure.
          It's a frontend-only placeholder in this demo — no backend call is made here.
        </p>
        {entries.length > 0 && (
          <div className="route-params">
            {entries.map(([key, value]) => (
              <span className="route-param-chip" key={key}>
                :{key} = {value}
              </span>
            ))}
          </div>
        )}
      </div>
    </>
  );
}
