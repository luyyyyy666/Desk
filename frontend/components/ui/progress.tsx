import { cn } from "@/lib/utils";

type ProgressProps = {
  value: number;
  className?: string;
};

export function Progress({ value, className }: ProgressProps) {
  const bounded = Math.max(0, Math.min(100, value));

  return (
    <div className={cn("h-3 overflow-hidden rounded-full border border-ink bg-paper-200", className)}>
      <div className="h-full rounded-full bg-moss" style={{ width: `${bounded}%` }} />
    </div>
  );
}
