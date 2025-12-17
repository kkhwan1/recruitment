"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card";
import { FileText, Calendar, TrendingUp } from "lucide-react";
import api from "@/lib/api";

interface Report {
  id: number;
  date: string;
  total_jobs: number;
  high_risk: number;
  medium_risk: number;
  low_risk: number;
  summary: string;
  top_keywords: string[];
  recommendations: string[];
}

export default function ReportsPage() {
  const [reports, setReports] = useState<Report[]>([]);
  const [selectedReport, setSelectedReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get("/reports")
      .then((response) => {
        setReports(response.data);
        if (response.data.length > 0) {
          setSelectedReport(response.data[0]);
        }
      })
      .catch((error) => {
        console.error("Failed to fetch reports:", error);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-muted-foreground">로딩 중...</p>
      </div>
    );
  }

  return (
    <div className="p-8 space-y-6">
      <div>
        <h1 className="text-3xl font-bold mb-2">분석 리포트</h1>
        <p className="text-muted-foreground">일일 크롤링 결과 및 위험도 분석 리포트</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Report List */}
        <div className="lg:col-span-1 space-y-3">
          <h2 className="text-lg font-semibold mb-4">리포트 목록</h2>
          {reports.length === 0 ? (
            <Card>
              <CardContent className="p-6">
                <p className="text-sm text-muted-foreground text-center">리포트가 없습니다.</p>
              </CardContent>
            </Card>
          ) : (
            reports.map((report) => (
              <Card
                key={report.id}
                className={`cursor-pointer transition-colors ${
                  selectedReport?.id === report.id ? "border-primary" : "hover:bg-accent/50"
                }`}
                onClick={() => setSelectedReport(report)}
              >
                <CardContent className="p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <FileText className="h-4 w-4 text-muted-foreground" />
                        <p className="font-medium text-sm">일일 리포트</p>
                      </div>
                      <div className="flex items-center gap-2 text-xs text-muted-foreground">
                        <Calendar className="h-3 w-3" />
                        {new Date(report.date).toLocaleDateString()}
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-semibold">{report.total_jobs}</p>
                      <p className="text-xs text-muted-foreground">건</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>

        {/* Report Detail */}
        <div className="lg:col-span-2">
          {selectedReport ? (
            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle>일일 분석 리포트</CardTitle>
                      <CardDescription className="mt-2">
                        {new Date(selectedReport.date).toLocaleDateString()}
                      </CardDescription>
                    </div>
                    <TrendingUp className="h-8 w-8 text-muted-foreground" />
                  </div>
                </CardHeader>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>수집 통계</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-4 gap-4">
                    <div className="text-center">
                      <p className="text-2xl font-bold">{selectedReport.total_jobs}</p>
                      <p className="text-sm text-muted-foreground mt-1">총 공고</p>
                    </div>
                    <div className="text-center">
                      <p className="text-2xl font-bold text-red-500">{selectedReport.high_risk}</p>
                      <p className="text-sm text-muted-foreground mt-1">고위험</p>
                    </div>
                    <div className="text-center">
                      <p className="text-2xl font-bold text-yellow-500">{selectedReport.medium_risk}</p>
                      <p className="text-sm text-muted-foreground mt-1">중위험</p>
                    </div>
                    <div className="text-center">
                      <p className="text-2xl font-bold text-green-500">{selectedReport.low_risk}</p>
                      <p className="text-sm text-muted-foreground mt-1">저위험</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>요약</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground leading-relaxed">{selectedReport.summary}</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>주요 키워드</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-2">
                    {selectedReport.top_keywords.map((keyword, index) => (
                      <span
                        key={index}
                        className="px-3 py-1 rounded-full bg-secondary text-secondary-foreground text-sm"
                      >
                        {keyword}
                      </span>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>권장사항</CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {selectedReport.recommendations.map((rec, index) => (
                      <li key={index} className="flex items-start gap-2 text-sm text-muted-foreground">
                        <span className="flex-shrink-0 mt-1 w-1.5 h-1.5 rounded-full bg-primary"></span>
                        <span>{rec}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            </div>
          ) : (
            <Card>
              <CardContent className="p-12">
                <p className="text-center text-muted-foreground">리포트를 선택해주세요.</p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
