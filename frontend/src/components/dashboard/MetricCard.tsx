import { Card, CardContent } from "@/components/ui/Card";
import { LucideIcon } from "lucide-react";

interface MetricCardProps {
  title: string;
  value: number;
  icon: LucideIcon;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  color: "blue" | "red" | "yellow" | "green";
}

const colorClasses = {
  blue: "bg-blue-500/10 text-blue-500",
  red: "bg-red-500/10 text-red-500",
  yellow: "bg-yellow-500/10 text-yellow-500",
  green: "bg-green-500/10 text-green-500",
};

export function MetricCard({ title, value, icon: Icon, trend, color }: MetricCardProps) {
  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-muted-foreground">{title}</p>
            <h3 className="mt-2 text-3xl font-bold">{value.toLocaleString()}</h3>
            {trend && (
              <p className={`mt-2 text-sm ${trend.isPositive ? "text-green-500" : "text-red-500"}`}>
                {trend.isPositive ? "+" : ""}{trend.value}% vs 지난주
              </p>
            )}
          </div>
          <div className={`rounded-full p-3 ${colorClasses[color]}`}>
            <Icon className="h-6 w-6" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
