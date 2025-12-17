import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { JobDetail } from "@/types";
import Link from "next/link";
import { ExternalLink } from "lucide-react";

interface HighRiskJobsListProps {
  jobs: JobDetail[];
}

export function HighRiskJobsList({ jobs }: HighRiskJobsListProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>최근 고위험 공고</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {jobs.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-4">고위험 공고가 없습니다.</p>
          ) : (
            jobs.map((job) => (
              <div
                key={job.id}
                className="flex items-start justify-between border-b border-border pb-4 last:border-0 last:pb-0"
              >
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <h4 className="font-medium truncate">{job.title}</h4>
                    <Badge riskLevel={job.risk_analysis.risk_level} />
                  </div>
                  <p className="text-sm text-muted-foreground">{job.company}</p>
                  <div className="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
                    <span>{job.source_site}</span>
                    <span>점수: {job.risk_analysis.final_score.toFixed(1)}</span>
                    <span>{new Date(job.crawled_at).toLocaleDateString()}</span>
                  </div>
                </div>
                {job.url && (
                  <Link
                    href={job.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="ml-4 flex-shrink-0 text-muted-foreground hover:text-foreground transition-colors"
                  >
                    <ExternalLink className="h-4 w-4" />
                  </Link>
                )}
              </div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  );
}
