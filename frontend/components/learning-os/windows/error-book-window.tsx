import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { mistakeGroups, mockQuestions } from "@/lib/mock-data";

export function ErrorBookWindow() {
  const wrongQuestion = mockQuestions.find((question) => question.status === "错题");

  return (
    <div className="grid grid-cols-[1fr_240px] gap-4">
      <div className="space-y-3">
        {mistakeGroups.map((group) => (
          <article key={group.knowledge} className="rounded-md border-2 border-ink bg-paper-100 p-4">
            <div className="mb-2 flex items-center justify-between">
              <h3 className="text-lg font-black">{group.knowledge}</h3>
              <Badge tone="orange">{group.count} 题</Badge>
            </div>
            <p className="text-sm font-semibold text-ink/70">{group.reason}</p>
            <div className="mt-3 rounded border border-ink/30 bg-paper-50 p-3 text-sm font-bold">
              {group.recommendation}
            </div>
          </article>
        ))}
      </div>
      <aside className="rounded-md border-2 border-ink bg-[#f2ddba] p-4">
        <Badge tone="ink" className="mb-3">最近错题</Badge>
        <h3 className="text-base font-black">{wrongQuestion?.title}</h3>
        <p className="mt-2 text-sm font-semibold text-ink/70">{wrongQuestion?.stem}</p>
        <div className="mt-3 rounded border border-ink bg-paper-50 p-3 text-sm">
          <strong>正确答案：</strong>
          {wrongQuestion?.answer}
        </div>
        <Button className="mt-4 w-full">生成同类题</Button>
      </aside>
    </div>
  );
}
