import type { DesktopIconData } from "@/lib/mock-data";
import { cn } from "@/lib/utils";

const fileColorClasses = {
  orange: "bg-[#f7b94a]",
  green: "bg-[#b7c66d]",
  blue: "bg-[#92c2d1]",
  paper: "bg-paper-50",
  pink: "bg-[#eda6a6]",
};

type DesktopIconProps = {
  icon: DesktopIconData;
  onOpen: (id: DesktopIconData["windowId"]) => void;
};

export function DesktopIcon({ icon, onOpen }: DesktopIconProps) {
  const Icon = icon.icon;

  return (
    <button
      type="button"
      className="desktop-icon group absolute flex w-24 flex-col items-center gap-1 text-center text-xs font-black text-ink transition hover:-translate-y-1 hover:rotate-[-2deg]"
      style={{ left: icon.x, top: icon.y }}
      aria-label={`${icon.label} ${icon.detail}`}
      onClick={() => onOpen(icon.windowId)}
    >
      <span
        className={cn(
          "relative grid h-[54px] w-[46px] place-items-center rounded-[5px] border-2 border-ink shadow-[4px_4px_0_rgba(36,32,21,0.22)]",
          fileColorClasses[icon.fileColor],
        )}
      >
        <span className="absolute right-0 top-0 h-3 w-3 border-b-2 border-l-2 border-ink bg-paper-200" />
        <Icon size={25} strokeWidth={2.4} />
      </span>
      <span className="rounded bg-paper-50/80 px-1 leading-tight">{icon.label}</span>
    </button>
  );
}
