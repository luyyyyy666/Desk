import { Minus, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { DesktopWindowDefinition } from "@/lib/window-state";

type FloatingWindowProps = {
  definition: DesktopWindowDefinition;
  children: React.ReactNode;
  onClose: () => void;
};

export function FloatingWindow({ definition, children, onClose }: FloatingWindowProps) {
  return (
    <section
      role="dialog"
      aria-label={definition.title}
      className="absolute overflow-hidden rounded-lg border-2 border-ink bg-paper-50 shadow-ink-lg"
      style={{
        left: definition.x,
        top: definition.y,
        width: definition.width,
        minHeight: definition.height,
        zIndex: 20,
      }}
    >
      <div className="flex h-10 items-center border-b-2 border-ink bg-[#ddd8c7] px-3">
        <div className="mr-3 flex gap-1.5">
          <button
            type="button"
            className="grid h-5 w-5 place-items-center rounded-full border border-ink bg-[#f29b88]"
            onClick={onClose}
            aria-label={`关闭${definition.title}`}
          >
            <X size={12} />
          </button>
          <button
            type="button"
            className="grid h-5 w-5 place-items-center rounded-full border border-ink bg-[#f4c86a]"
            aria-label={`最小化${definition.title}`}
          >
            <Minus size={12} />
          </button>
        </div>
        <div>
          <p className="text-[10px] font-black uppercase text-ink/50">{definition.eyebrow}</p>
          <h2 className="text-sm font-black leading-none">{definition.title}</h2>
        </div>
        <Button className="ml-auto" size="sm" variant="paper">置顶</Button>
      </div>
      <div className="p-5">{children}</div>
    </section>
  );
}
