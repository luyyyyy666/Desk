"use client";

import { useMemo, useState } from "react";
import { DesktopIcon } from "@/components/learning-os/desktop-icon";
import { FloatingWindow } from "@/components/learning-os/floating-window";
import { LearningIsland } from "@/components/learning-os/learning-island";
import { MissionBoard } from "@/components/learning-os/mission-board";
import { TopBar } from "@/components/learning-os/top-bar";
import { ErrorBookWindow } from "@/components/learning-os/windows/error-book-window";
import {
  EditorWindow,
  ExportWindow,
  GeneratorWindow,
  KnowledgeWindow,
  PracticeWindow,
  ReportWindow,
  ReviewWindow,
  SuggestionsWindow,
} from "@/components/learning-os/windows/placeholder-windows";
import { desktopIcons } from "@/lib/mock-data";
import { desktopWindows, getWindowById, type WindowId } from "@/lib/window-state";

type LearningDesktopProps = {
  defaultWindow?: WindowId | null;
};

const windowContent: Record<WindowId, React.ReactNode> = {
  generator: <GeneratorWindow />,
  editor: <EditorWindow />,
  practice: <PracticeWindow />,
  review: <ReviewWindow />,
  errors: <ErrorBookWindow />,
  knowledge: <KnowledgeWindow />,
  report: <ReportWindow />,
  export: <ExportWindow />,
  suggestions: <SuggestionsWindow />,
};

export function LearningDesktop({ defaultWindow = "generator" }: LearningDesktopProps) {
  const [activeWindow, setActiveWindow] = useState<WindowId | null>(defaultWindow);
  const activeDefinition = useMemo(
    () => (activeWindow ? getWindowById(activeWindow) : undefined),
    [activeWindow],
  );

  return (
    <div className="h-screen min-w-[1280px] overflow-hidden bg-paper text-ink">
      <TopBar />
      <main className="paper-desktop relative h-[calc(100vh-44px)] overflow-hidden" role="main">
        {desktopIcons.map((icon) => (
          <DesktopIcon key={icon.id} icon={icon} onOpen={setActiveWindow} />
        ))}

        <MissionBoard activeWindow={activeWindow} onOpen={setActiveWindow} />
        <LearningIsland />

        <div className="absolute left-[445px] top-[42px] text-center text-sm font-black text-ink/70">
          ✉️
          <br />
          交给师傅
        </div>
        <div className="absolute left-[690px] top-[340px] rotate-[-4deg] text-center text-sm font-black text-ink/70">
          🎬
          <br />
          生成流程
        </div>

        {activeDefinition ? (
          <FloatingWindow definition={activeDefinition} onClose={() => setActiveWindow(null)}>
            {windowContent[activeDefinition.id]}
          </FloatingWindow>
        ) : null}

        <div className="absolute bottom-0 left-0 right-0 flex h-10 items-center border-t-2 border-ink bg-[#ddd8c7] px-4 text-xs font-black">
          {desktopWindows.map((window) => (
            <button
              key={window.id}
              type="button"
              className="mr-2 rounded border border-ink bg-paper-50 px-3 py-1 hover:bg-orange"
              onClick={() => setActiveWindow(window.id)}
            >
              {window.title}
            </button>
          ))}
        </div>
      </main>
    </div>
  );
}
