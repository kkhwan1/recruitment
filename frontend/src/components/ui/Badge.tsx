import { cn } from "@/lib/utils";
import { RiskLevel } from "@/types";

interface BadgeProps {
  riskLevel: RiskLevel;
  className?: string;
}

export function Badge({ riskLevel, className }: BadgeProps) {
  const variants = {
    "고위험": "bg-red-500/10 text-red-500 border-red-500/20",
    "중위험": "bg-yellow-500/10 text-yellow-500 border-yellow-500/20",
    "저위험": "bg-green-500/10 text-green-500 border-green-500/20",
  };

  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors",
        variants[riskLevel],
        className
      )}
    >
      {riskLevel}
    </span>
  );
}
