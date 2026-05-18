import { ArrowRight, RotateCcw } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { currentTask, learningLoop } from "@/lib/mock-data";
import type { WindowId } from "@/lib/window-state";
import { cn } from "@/lib/utils";

type MissionBoardProps = {
  activeWindow?: WindowId | null;
  onOpen: (id: WindowId) => void;
};

export function MissionBoard({ activeWindow, onOpen }: MissionBoardProps) {
  return (
    <section className="absolute left-[300px] top-[116px] w-[545px] rotate-[-1deg] rounded-lg border-2 border-ink bg-paper-50 p-5 shadow-ink-lg">
      <div className="mb-4 flex items-start justify-between gap-4">
        <div>
          <Badge tone="orange" className="mb-3">当前任务</Badge>
          <h1 className="text-3xl font-black leading-tight">{currentTask.title}</h1>
          <p className="mt-2 text-sm font-semibold text-ink/70">{currentTask.goal}</p>
        </div>
        <div className="rounded-md border-2 border-ink bg-[#f1d48a] px-3 py-2 text-right text-xs font-black shadow-[3px_3px_0_rgba(36,32,21,0.2)]">
          {currentTask.subject}
          <br />
          <span className="font-bold text-ink/70">{currentTask.source}</span>
        </div>
      </div>

      <div className="mb-5 grid grid-cols-[1fr_120px] gap-4">
        <div className="rounded-md border border-ink/30 bg-paper-100 p-3">
          <div className="mb-2 flex items-center justify-between text-xs font-black">
            <span>{currentTask.status}</span>
            <span>{currentTask.mastery}%</span>
          </div>
          <Progress value={currentTask.mastery} />
        </div>
        <div className="rounded-md border border-ink/30 bg-paper-100 p-3 text-xs font-black">
          <span className="block text-2xl">{currentTask.questionCount}</span>
          题 · {currentTask.duration}
        </div>
      </div>

      <div className="mb-5 flex flex-wrap items-center gap-2">
        {learningLoop.map((step, index) => (
          <button
            type="button"
            key={step.id}
            onClick={() => onOpen(step.windowId)}
            className={cn(
              "flex items-center gap-2 rounded-md border border-ink bg-paper-100 px-2 py-1 text-xs font-black transition hover:-translate-y-0.5",
              activeWindow === step.windowId && "bg-orange shadow-[2px_2px_0_rgba(36,32,21,0.22)]",
            )}
          >
            {step.label}
            {index < learningLoop.length - 1 ? <ArrowRight size={12} /> : null}
          </button>
        ))}
      </div>

      <div className="flex items-center gap-3">
        <Button onClick={() => onOpen("practice")}>继续练习</Button>
        <Button variant="paper" onClick={() => onOpen("generator")}>
          <RotateCcw size={16} />
          重新生成
        </Button>
        <Button variant="ghost" onClick={() => onOpen("review")}>查看解析</Button>
      </div>
    </section>
  );
}
