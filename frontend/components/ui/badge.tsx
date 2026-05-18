import * as React from "react";
import { cn } from "@/lib/utils";

type BadgeProps = React.HTMLAttributes<HTMLSpanElement> & {
  tone?: "paper" | "orange" | "green" | "blue" | "ink";
};

const tones = {
  paper: "border-ink/25 bg-paper-50 text-ink",
  orange: "border-ink bg-orange text-ink",
  green: "border-ink/40 bg-moss/20 text-ink",
  blue: "border-ink/40 bg-pond/15 text-ink",
  ink: "border-ink bg-ink text-paper-50",
};

export function Badge({ className, tone = "paper", ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-md border px-2 py-1 text-xs font-bold leading-none",
        tones[tone],
        className,
      )}
      {...props}
    />
  );
}
