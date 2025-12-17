"use client";

import { Badge } from "@/components/ui/Badge";
import { JobDetail } from "@/types";
import { ExternalLink } from "lucide-react";
import Link from "next/link";

interface JobTableProps {
  jobs: JobDetail[];
}

export function JobTable({ jobs }: JobTableProps) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b border-border text-sm text-muted-foreground">
            <th className="pb-3 text-left font-medium">제목</th>
            <th className="pb-3 text-left font-medium">회사</th>
            <th className="pb-3 text-left font-medium">위치</th>
            <th className="pb-3 text-left font-medium">위험도</th>
            <th className="pb-3 text-left font-medium">점수</th>
            <th className="pb-3 text-left font-medium">사이트</th>
            <th className="pb-3 text-left font-medium">날짜</th>
            <th className="pb-3 text-left font-medium"></th>
          </tr>
        </thead>
        <tbody>
          {jobs.length === 0 ? (
            <tr>
              <td colSpan={8} className="py-8 text-center text-sm text-muted-foreground">
                검색 결과가 없습니다.
              </td>
            </tr>
          ) : (
            jobs.map((job) => (
              <tr key={job.id} className="border-b border-border hover:bg-accent/50 transition-colors">
                <td className="py-4 max-w-xs">
                  <p className="font-medium truncate">{job.title}</p>
                </td>
                <td className="py-4">
                  <p className="text-sm text-muted-foreground">{job.company}</p>
                </td>
                <td className="py-4">
                  <p className="text-sm text-muted-foreground">{job.location || "-"}</p>
                </td>
                <td className="py-4">
                  <Badge riskLevel={job.risk_analysis.risk_level} />
                </td>
                <td className="py-4">
                  <p className="text-sm font-medium">{job.risk_analysis.final_score.toFixed(1)}</p>
                </td>
                <td className="py-4">
                  <p className="text-sm text-muted-foreground">{job.source_site}</p>
                </td>
                <td className="py-4">
                  <p className="text-sm text-muted-foreground">
                    {new Date(job.crawled_at).toLocaleDateString()}
                  </p>
                </td>
                <td className="py-4">
                  {job.url && (
                    <Link
                      href={job.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-muted-foreground hover:text-foreground transition-colors"
                    >
                      <ExternalLink className="h-4 w-4" />
                    </Link>
                  )}
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
