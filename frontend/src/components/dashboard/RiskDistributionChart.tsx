"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from "recharts";

interface RiskDistributionChartProps {
  data: Array<{
    name: string;
    value: number;
  }>;
}

const COLORS = {
  "고위험": "#ef4444",
  "중위험": "#eab308",
  "저위험": "#22c55e",
};

export function RiskDistributionChart({ data }: RiskDistributionChartProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>위험도 분포</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[entry.name as keyof typeof COLORS]} />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                backgroundColor: "hsl(var(--card))",
                border: "1px solid hsl(var(--border))",
                borderRadius: "0.5rem",
              }}
            />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
