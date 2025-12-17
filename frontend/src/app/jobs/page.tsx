"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { JobTable } from "@/components/jobs/JobTable";
import { Search } from "lucide-react";
import api from "@/lib/api";
import { JobDetail, RiskLevel } from "@/types";

export default function JobsPage() {
  const [jobs, setJobs] = useState<JobDetail[]>([]);
  const [filteredJobs, setFilteredJobs] = useState<JobDetail[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [riskFilter, setRiskFilter] = useState<RiskLevel | "all">("all");
  const [siteFilter, setSiteFilter] = useState("all");
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 20;

  useEffect(() => {
    api
      .get("/jobs")
      .then((response) => {
        setJobs(response.data);
        setFilteredJobs(response.data);
      })
      .catch((error) => {
        console.error("Failed to fetch jobs:", error);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  useEffect(() => {
    let filtered = jobs;

    if (searchTerm) {
      filtered = filtered.filter(
        (job) =>
          job.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
          job.company.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    if (riskFilter !== "all") {
      filtered = filtered.filter((job) => job.risk_analysis.risk_level === riskFilter);
    }

    if (siteFilter !== "all") {
      filtered = filtered.filter((job) => job.source_site === siteFilter);
    }

    setFilteredJobs(filtered);
    setCurrentPage(1);
  }, [searchTerm, riskFilter, siteFilter, jobs]);

  const sites = ["all", ...Array.from(new Set(jobs.map((job) => job.source_site)))];
  const totalPages = Math.ceil(filteredJobs.length / itemsPerPage);
  const paginatedJobs = filteredJobs.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);

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
        <h1 className="text-3xl font-bold mb-2">채용 공고 목록</h1>
        <p className="text-muted-foreground">총 {filteredJobs.length}개의 공고</p>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle>필터</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <input
                type="text"
                placeholder="제목 또는 회사 검색..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 rounded-md border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
              />
            </div>

            {/* Risk Level Filter */}
            <select
              value={riskFilter}
              onChange={(e) => setRiskFilter(e.target.value as RiskLevel | "all")}
              className="px-4 py-2 rounded-md border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            >
              <option value="all">모든 위험도</option>
              <option value="고위험">고위험</option>
              <option value="중위험">중위험</option>
              <option value="저위험">저위험</option>
            </select>

            {/* Site Filter */}
            <select
              value={siteFilter}
              onChange={(e) => setSiteFilter(e.target.value)}
              className="px-4 py-2 rounded-md border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            >
              {sites.map((site) => (
                <option key={site} value={site}>
                  {site === "all" ? "모든 사이트" : site}
                </option>
              ))}
            </select>
          </div>
        </CardContent>
      </Card>

      {/* Table */}
      <Card>
        <CardContent className="p-6">
          <JobTable jobs={paginatedJobs} />
        </CardContent>
      </Card>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex justify-center gap-2">
          <button
            onClick={() => setCurrentPage((prev) => Math.max(1, prev - 1))}
            disabled={currentPage === 1}
            className="px-4 py-2 rounded-md border border-input bg-background text-sm hover:bg-accent disabled:opacity-50 disabled:cursor-not-allowed"
          >
            이전
          </button>
          <span className="px-4 py-2 text-sm text-muted-foreground">
            {currentPage} / {totalPages}
          </span>
          <button
            onClick={() => setCurrentPage((prev) => Math.min(totalPages, prev + 1))}
            disabled={currentPage === totalPages}
            className="px-4 py-2 rounded-md border border-input bg-background text-sm hover:bg-accent disabled:opacity-50 disabled:cursor-not-allowed"
          >
            다음
          </button>
        </div>
      )}
    </div>
  );
}
