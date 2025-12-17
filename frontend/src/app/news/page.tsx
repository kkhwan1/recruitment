"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { ExternalLink, Calendar } from "lucide-react";
import api from "@/lib/api";
import Link from "next/link";

interface NewsItem {
  id: number;
  title: string;
  description: string;
  url: string;
  published_at: string;
  source: string;
  category: string;
}

export default function NewsPage() {
  const [news, setNews] = useState<NewsItem[]>([]);
  const [filteredNews, setFilteredNews] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeCategory, setActiveCategory] = useState("all");

  useEffect(() => {
    api
      .get("/news")
      .then((response) => {
        setNews(response.data);
        setFilteredNews(response.data);
      })
      .catch((error) => {
        console.error("Failed to fetch news:", error);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  useEffect(() => {
    if (activeCategory === "all") {
      setFilteredNews(news);
    } else {
      setFilteredNews(news.filter((item) => item.category === activeCategory));
    }
  }, [activeCategory, news]);

  const categories = ["all", ...Array.from(new Set(news.map((item) => item.category)))];

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
        <h1 className="text-3xl font-bold mb-2">관련 뉴스</h1>
        <p className="text-muted-foreground">기술 유출 및 채용 관련 최신 뉴스</p>
      </div>

      {/* Category Tabs */}
      <div className="flex gap-2 overflow-x-auto pb-2">
        {categories.map((category) => (
          <button
            key={category}
            onClick={() => setActiveCategory(category)}
            className={`px-4 py-2 rounded-md text-sm font-medium whitespace-nowrap transition-colors ${
              activeCategory === category
                ? "bg-primary text-primary-foreground"
                : "bg-secondary text-secondary-foreground hover:bg-secondary/80"
            }`}
          >
            {category === "all" ? "전체" : category}
          </button>
        ))}
      </div>

      {/* News Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {filteredNews.length === 0 ? (
          <div className="col-span-full text-center py-12">
            <p className="text-muted-foreground">뉴스가 없습니다.</p>
          </div>
        ) : (
          filteredNews.map((item) => (
            <Card key={item.id} className="hover:shadow-md transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between gap-2">
                  <CardTitle className="text-lg line-clamp-2">{item.title}</CardTitle>
                  <Link
                    href={item.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex-shrink-0 text-muted-foreground hover:text-foreground transition-colors"
                  >
                    <ExternalLink className="h-4 w-4" />
                  </Link>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground line-clamp-3 mb-4">{item.description}</p>
                <div className="flex items-center justify-between text-xs text-muted-foreground">
                  <span className="inline-flex items-center gap-1">
                    <Calendar className="h-3 w-3" />
                    {new Date(item.published_at).toLocaleDateString()}
                  </span>
                  <span>{item.source}</span>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
