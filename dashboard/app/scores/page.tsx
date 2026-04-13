import { getScores } from "@/lib/data";

export default function ScoresPage() {
  const scores = getScores();

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold">Score History</h1>
        <p className="text-muted mt-2">
          {scores.length} cycle{scores.length !== 1 ? "s" : ""} completed.
          Each cycle tests active hypotheses and updates the belief state.
        </p>
      </div>

      {scores.length === 0 ? (
        <p className="text-muted">No cycles completed yet.</p>
      ) : (
        <div className="space-y-4">
          {[...scores].reverse().map((s, i) => (
            <div
              key={i}
              className="bg-surface border border-border rounded-lg p-6"
            >
              <div className="flex items-center justify-between mb-4">
                <h2 className="font-bold font-mono">{s.date}</h2>
                <div className="flex gap-4 text-sm font-mono">
                  <span>
                    Surprise:{" "}
                    <span className="text-accent">
                      {s.progress.surprise.toFixed(4)}
                    </span>
                  </span>
                  <span>
                    Beliefs: {s.belief_count_before} → {s.belief_count_after}
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
                <div className="text-center">
                  <div className="text-2xl font-bold font-mono">
                    {s.progress.total_hypotheses}
                  </div>
                  <div className="text-xs text-muted">Total</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold font-mono text-success">
                    {s.progress.active}
                  </div>
                  <div className="text-xs text-muted">Active</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold font-mono text-danger">
                    {s.progress.eliminated}
                  </div>
                  <div className="text-xs text-muted">Eliminated</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold font-mono text-warning">
                    {s.progress.high_confidence}
                  </div>
                  <div className="text-xs text-muted">High confidence</div>
                </div>
              </div>

              {s.scored_hypotheses && s.scored_hypotheses.length > 0 && (
                <div className="space-y-2">
                  {s.scored_hypotheses.map((sh) => (
                    <div
                      key={sh.id}
                      className="flex items-center gap-3 text-sm p-2 rounded bg-surface-2"
                    >
                      <span className="font-mono text-xs text-muted w-10">
                        {sh.id}
                      </span>
                      <span
                        className={`font-mono font-bold w-10 ${
                          sh.confidence > 0.7
                            ? "text-success"
                            : sh.confidence > 0.4
                              ? "text-warning"
                              : "text-danger"
                        }`}
                      >
                        {sh.confidence.toFixed(2)}
                      </span>
                      <span className="flex-1 truncate text-xs">
                        {sh.claim}
                      </span>
                      <span
                        className={`text-xs px-2 py-0.5 rounded ${
                          sh.status === "active"
                            ? "bg-success/20 text-success"
                            : sh.status === "eliminated"
                              ? "bg-danger/20 text-danger"
                              : "bg-warning/20 text-warning"
                        }`}
                      >
                        {sh.status}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
