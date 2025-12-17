"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";

interface TrendChartProps {
  data: Array<{
    date: string;
    total: number;
    high: number;
    medium: number;
    low: number;
  }>;
}

export function TrendChart({ data }: TrendChartProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>7일 트렌드</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
            <XAxis dataKey="date" stroke="hsl(var(--muted-foreground))" fontSize={12} />
            <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} />
            <Tooltip
              contentStyle={{
                backgroundColor: "hsl(var(--card))",
                border: "1px solid hsl(var(--border))",
                borderRadius: "0.5rem",
              }}
              labelStyle={{ color: "hsl(var(--foreground))" }}
            />
            <Legend />
            <Line type="monotone" dataKey="total" stroke="#3b82f6" name="전체" strokeWidth={2} />
            <Line type="monotone" dataKey="high" stroke="#ef4444" name="고위험" strokeWidth={2} />
            <Line type="monotone" dataKey="medium" stroke="#eab308" name="중위험" strokeWidth={2} />
            <Line type="monotone" dataKey="low" stroke="#22c55e" name="저위험" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
