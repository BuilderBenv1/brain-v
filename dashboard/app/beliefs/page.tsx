import { getBeliefs } from "@/lib/data";

export default function BeliefsPage() {
  const beliefs = getBeliefs();

  const sorted = [...beliefs].sort((a, b) => {
    const ca = typeof a.confidence === "number" ? a.confidence : 0;
    const cb = typeof b.confidence === "number" ? b.confidence : 0;
    return cb - ca;
  });

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold">Belief State</h1>
        <p className="text-muted mt-2">
          Brain-V&apos;s current world model. {beliefs.length} beliefs, updated
          each cycle based on hypothesis test results.
        </p>
      </div>

      <div className="space-y-3">
        {sorted.map((b, i) => {
          const conf =
            typeof b.confidence === "number"
              ? b.confidence
              : parseFloat(String(b.confidence)) || 0;
          const confColor =
            conf > 0.7
              ? "text-success"
              : conf > 0.4
                ? "text-warning"
                : "text-danger";
          const barWidth = Math.max(2, conf * 100);

          return (
            <div
              key={i}
              className="bg-surface border border-border rounded-lg p-4"
            >
              <div className="flex items-start gap-4">
                <span
                  className={`font-mono text-xl font-bold w-14 text-right flex-shrink-0 ${confColor}`}
                >
                  {conf.toFixed(2)}
                </span>
                <div className="flex-1">
                  <p className="text-sm">{b.belief}</p>
                  <div className="flex gap-4 mt-2 text-xs text-muted">
                    <span>Source: {b.source}</span>
                    <span>{b.date}</span>
                    {b.last_scored && (
                      <span>Last scored: {b.last_scored}</span>
                    )}
                  </div>
                  {b.evidence && (
                    <p className="text-xs text-muted mt-1 italic">
                      {b.evidence}
                    </p>
                  )}
                  {/* Confidence bar */}
                  <div className="mt-2 h-1.5 bg-surface-2 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full ${
                        conf > 0.7
                          ? "bg-success"
                          : conf > 0.4
                            ? "bg-warning"
                            : "bg-danger"
                      }`}
                      style={{ width: `${barWidth}%` }}
                    />
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
