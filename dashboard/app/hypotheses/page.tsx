import { getHypotheses } from "@/lib/data";

export default function HypothesesPage() {
  const hypotheses = getHypotheses();
  const active = hypotheses
    .filter((h) => h.status === "active")
    .sort((a, b) => b.confidence - a.confidence);
  const eliminated = hypotheses
    .filter((h) => h.status === "eliminated")
    .sort((a, b) => b.id.localeCompare(a.id));
  const parked = hypotheses.filter((h) => h.status === "parked");

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold">Hypothesis Board</h1>
        <p className="text-muted mt-2">
          {hypotheses.length} total hypotheses. {active.length} active,{" "}
          {eliminated.length} eliminated, {parked.length} parked.
        </p>
      </div>

      {/* Active */}
      <section>
        <h2 className="text-xl font-bold mb-4 text-success">
          Active ({active.length})
        </h2>
        <div className="space-y-3">
          {active.map((h) => (
            <HypothesisCard key={h.id} h={h} />
          ))}
        </div>
      </section>

      {/* Parked */}
      {parked.length > 0 && (
        <section>
          <h2 className="text-xl font-bold mb-4 text-warning">
            Parked ({parked.length})
          </h2>
          <p className="text-muted text-sm mb-3">
            Unproven but not debunked. May be revisited with new evidence or
            methods.
          </p>
          <div className="space-y-3">
            {parked.map((h) => (
              <HypothesisCard key={h.id} h={h} />
            ))}
          </div>
        </section>
      )}

      {/* Eliminated */}
      <section>
        <h2 className="text-xl font-bold mb-4 text-danger">
          Eliminated ({eliminated.length})
        </h2>
        <p className="text-muted text-sm mb-3">
          These approaches have been tested and failed. Brain-V will not
          re-test them.
        </p>
        <div className="space-y-3">
          {eliminated.map((h) => (
            <HypothesisCard key={h.id} h={h} />
          ))}
        </div>
      </section>
    </div>
  );
}

function HypothesisCard({ h }: { h: ReturnType<typeof getHypotheses>[0] }) {
  const confColor =
    h.confidence > 0.7
      ? "text-success"
      : h.confidence > 0.4
        ? "text-warning"
        : h.confidence > 0.1
          ? "text-danger"
          : "text-muted";

  return (
    <div className="bg-surface border border-border rounded-lg p-4">
      <div className="flex items-start gap-4">
        <div className="flex-shrink-0 text-center">
          <span className="font-mono text-xs text-muted block">{h.id}</span>
          <span className={`text-xl font-bold font-mono ${confColor}`}>
            {h.confidence.toFixed(2)}
          </span>
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium">{h.claim}</p>
          <div className="flex flex-wrap gap-2 mt-2">
            <span className="text-xs px-2 py-0.5 rounded bg-accent-dim/30 text-accent">
              {h.type}
            </span>
            <span
              className={`text-xs px-2 py-0.5 rounded ${
                h.status === "active"
                  ? "bg-success/20 text-success"
                  : h.status === "eliminated"
                    ? "bg-danger/20 text-danger"
                    : "bg-warning/20 text-warning"
              }`}
            >
              {h.status}
            </span>
            {h.created && (
              <span className="text-xs text-muted">
                {h.created}
              </span>
            )}
          </div>
          {h.evidence_against.length > 0 && (
            <div className="mt-2 text-xs text-muted">
              <span className="text-danger">Against:</span>{" "}
              {h.evidence_against[0]}
            </div>
          )}
          {h.tests_run.length > 0 && (
            <div className="mt-2 text-xs text-muted">
              <span className="text-accent">Last test:</span>{" "}
              {h.tests_run[h.tests_run.length - 1].details?.slice(0, 150)}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
