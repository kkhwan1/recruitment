"use client";

import { useEffect, useState } from "react";
import { MetricCard } from "@/components/dashboard/MetricCard";
import { TrendChart } from "@/components/dashboard/TrendChart";
import { RiskDistributionChart } from "@/components/dashboard/RiskDistributionChart";
import { HighRiskJobsList } from "@/components/dashboard/HighRiskJobsList";
import { Briefcase, AlertTriangle, AlertCircle, CheckCircle } from "lucide-react";
import api from "@/lib/api";
import { JobDetail } from "@/types";

export default function Dashboard() {
  const [stats, setStats] = useState({
    total: 0,
    high: 0,
    medium: 0,
    low: 0,
  });
  const [trendData, setTrendData] = useState<any[]>([]);
  const [distributionData, setDistributionData] = useState<any[]>([]);
  const [highRiskJobs, setHighRiskJobs] = useState<JobDetail[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.get("/stats/dashboard"),
      api.get("/stats/trend?days=7"),
      api.get("/jobs/high-risk?limit=5"),
    ])
      .then(([statsRes, trendRes, jobsRes]) => {
        setStats(statsRes.data);
        setTrendData(trendRes.data);
        setDistributionData([
          { name: "고위험", value: statsRes.data.high },
          { name: "중위험", value: statsRes.data.medium },
          { name: "저위험", value: statsRes.data.low },
        ]);
        setHighRiskJobs(jobsRes.data);
      })
      .catch((error) => {
        console.error("Failed to fetch dashboard data:", error);
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
    <div className="p-8 space-y-8">
      <div>
        <h1 className="text-3xl font-bold mb-2">대시보드</h1>
        <p className="text-muted-foreground">채용 공고 분석 현황을 한눈에 확인하세요</p>
      </div>

      {/* Metrics */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <MetricCard title="총 공고" value={stats.total} icon={Briefcase} color="blue" />
        <MetricCard title="고위험" value={stats.high} icon={AlertTriangle} color="red" />
        <MetricCard title="중위험" value={stats.medium} icon={AlertCircle} color="yellow" />
        <MetricCard title="저위험" value={stats.low} icon={CheckCircle} color="green" />
      </div>

      {/* Charts */}
      <div className="grid gap-4 md:grid-cols-2">
        <TrendChart data={trendData} />
        <RiskDistributionChart data={distributionData} />
      </div>

      {/* High Risk Jobs */}
      <HighRiskJobsList jobs={highRiskJobs} />
    </div>
  );
}
