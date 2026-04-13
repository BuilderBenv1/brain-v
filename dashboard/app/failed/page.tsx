import fs from "fs";
import path from "path";

interface FailedApproach {
  id: string;
  researcher: string;
  year: number;
  claim: string;
  type: string;
  cipher_type: string;
  proposed_language: string;
  status: string;
  failure_reason: string;
  source: string;
}

function getFailedApproaches(): FailedApproach[] {
  const filePath = path.resolve(
    process.cwd(),
    "..",
    "raw/corpus/failed-approaches.json"
  );
  if (!fs.existsSync(filePath)) return [];
  return JSON.parse(fs.readFileSync(filePath, "utf-8"));
}

export default function FailedPage() {
  const approaches = getFailedApproaches();

  const debunked = approaches.filter((a) => a.status === "debunked");
  const debated = approaches.filter((a) => a.status === "debated");
  const unproven = approaches.filter(
    (a) => a.status === "unproven" || a.status === "unverified"
  );

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold">Failed Approaches Catalogue</h1>
        <p className="text-muted mt-2 max-w-2xl">
          {approaches.length} documented decipherment attempts spanning{" "}
          {approaches.length > 0
            ? `${Math.min(...approaches.map((a) => a.year))}-${Math.max(
                ...approaches.map((a) => a.year)
              )}`
            : "—"}
          . Brain-V ingests these as eliminated hypotheses to avoid wasting
          cycles rediscovering known failures.
        </p>
      </div>

      {/* Summary stats */}
      <div className="grid grid-cols-3 gap-3">
        <div className="bg-surface border border-border rounded-lg p-4 text-center">
          <div className="text-2xl font-bold font-mono text-danger">
            {debunked.length}
          </div>
          <div className="text-xs text-muted">Debunked</div>
        </div>
        <div className="bg-surface border border-border rounded-lg p-4 text-center">
          <div className="text-2xl font-bold font-mono text-warning">
            {debated.length}
          </div>
          <div className="text-xs text-muted">Debated</div>
        </div>
        <div className="bg-surface border border-border rounded-lg p-4 text-center">
          <div className="text-2xl font-bold font-mono text-muted">
            {unproven.length}
          </div>
          <div className="text-xs text-muted">Unproven</div>
        </div>
      </div>

      {/* Timeline */}
      <div className="space-y-3">
        {[...approaches]
          .sort((a, b) => a.year - b.year)
          .map((a) => (
            <div
              key={a.id}
              className="bg-surface border border-border rounded-lg p-4"
            >
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0 text-center w-16">
                  <div className="font-mono text-lg font-bold text-accent">
                    {a.year}
                  </div>
                  <span
                    className={`text-xs px-1.5 py-0.5 rounded ${
                      a.status === "debunked"
                        ? "bg-danger/20 text-danger"
                        : a.status === "debated"
                          ? "bg-warning/20 text-warning"
                          : "bg-surface-2 text-muted"
                    }`}
                  >
                    {a.status}
                  </span>
                </div>
                <div className="flex-1">
                  <div className="font-bold text-sm">{a.researcher}</div>
                  <p className="text-sm mt-1">{a.claim}</p>
                  <div className="flex flex-wrap gap-2 mt-2">
                    <span className="text-xs px-2 py-0.5 rounded bg-accent-dim/30 text-accent">
                      {a.cipher_type}
                    </span>
                    <span className="text-xs px-2 py-0.5 rounded bg-surface-2 text-muted">
                      {a.proposed_language}
                    </span>
                  </div>
                  <div className="mt-2 text-xs text-danger">
                    {a.failure_reason}
                  </div>
                  <div className="mt-1 text-xs text-muted italic">
                    {a.source}
                  </div>
                </div>
              </div>
            </div>
          ))}
      </div>
    </div>
  );
}
