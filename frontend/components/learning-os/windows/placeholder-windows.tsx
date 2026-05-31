import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  currentTask,
  knowledgePoints,
  mockQuestions,
  persistedPlan,
  publicKnowledgeStatus,
  ragPipelineStatus,
  reportMetrics,
} from "@/lib/mock-data";

export function GeneratorWindow() {
  return (
    <div className="grid grid-cols-[1fr_240px] gap-4">
      <div className="space-y-3">
        <div className="rounded-md border-2 border-ink bg-paper-100 p-4">
          <Badge tone="orange" className="mb-3">学习目标</Badge>
          <h3 className="text-xl font-black">{currentTask.goal}</h3>
          <p className="mt-2 text-sm font-semibold text-ink/70">{currentTask.source}</p>
        </div>
        <div className="grid grid-cols-3 gap-3">
          {["12 题", "中等难度", "含详细解析"].map((item) => (
            <div key={item} className="rounded-md border border-ink bg-paper-50 p-3 text-center text-sm font-black">
              {item}
            </div>
          ))}
        </div>
        <div className="rounded-md border-2 border-ink bg-paper-50 p-4">
          <h4 className="mb-3 font-black">已生成题单</h4>
          <div className="space-y-2">
            {mockQuestions.map((question) => (
              <div key={question.id} className="flex items-center justify-between rounded border border-ink/30 bg-paper-100 px-3 py-2 text-sm font-bold">
                <span>{question.type} · {question.title}</span>
                <Badge>{question.difficulty}</Badge>
              </div>
            ))}
          </div>
        </div>
        <div className="rounded-md border-2 border-ink bg-[#dfe8bd] p-4">
          <div className="mb-3 flex items-center justify-between">
            <Badge tone="green">Phase 5 Plan</Badge>
            <span className="rounded border border-ink bg-paper-50 px-2 py-1 text-xs font-black">
              {persistedPlan.status}
            </span>
          </div>
          <p className="text-xs font-black text-ink/70">{persistedPlan.id}</p>
          <div className="mt-1 flex items-center gap-2 text-xs font-bold text-ink/60">
            <span>当前步骤：</span>
            <span>{persistedPlan.currentStepId}</span>
          </div>
          <div className="mt-3 grid grid-cols-2 gap-2 text-xs font-black">
            {persistedPlan.steps.map((step) => (
              <div key={step.id} className="rounded border border-ink bg-paper-50 p-2">
                <p>{step.title}</p>
                <p className="mt-1 text-ink/60">{step.skillId}</p>
                <p className="mt-1 text-[10px] uppercase text-ink/50">{step.status}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
      <aside className="rounded-md border-2 border-ink bg-[#e8d099] p-4">
        <Badge tone="ink" className="mb-3">师傅建议</Badge>
        <p className="text-sm font-semibold leading-6">当前题单覆盖解析式和图像，但应用题偏少。建议增加 2 道真实情境建模题。</p>
        <Button className="mt-5 w-full">应用建议</Button>
      </aside>
    </div>
  );
}

export function EditorWindow() {
  return (
    <div className="grid grid-cols-[190px_1fr_210px] gap-4">
      <div className="space-y-2">
        {mockQuestions.map((question, index) => (
          <div key={question.id} className="rounded border border-ink bg-paper-100 p-2 text-xs font-black">
            {index + 1}. {question.title}
          </div>
        ))}
      </div>
      <div className="rounded-md border-2 border-ink bg-paper-50 p-4">
        <Badge tone="blue" className="mb-3">{mockQuestions[2].type}</Badge>
        <h3 className="text-lg font-black">{mockQuestions[2].title}</h3>
        <p className="mt-3 text-sm font-semibold leading-6">{mockQuestions[2].stem}</p>
        <div className="mt-4 rounded border border-ink bg-paper-100 p-3 text-sm">
          <strong>解析：</strong>{mockQuestions[2].explanation}
        </div>
      </div>
      <aside className="rounded-md border-2 border-ink bg-[#dfe8bd] p-4 text-sm font-semibold">
        <Badge tone="green" className="mb-3">质量检查</Badge>
        <p>覆盖：函数建模</p>
        <p className="mt-2">清晰度：良好</p>
        <p className="mt-2">建议：补充单位说明</p>
      </aside>
    </div>
  );
}

export function PracticeWindow() {
  const question = mockQuestions[0];

  return (
    <div className="grid grid-cols-[1fr_190px] gap-4">
      <section className="rounded-md border-2 border-ink bg-paper-50 p-5">
        <Badge tone="orange" className="mb-4">第 1 / 12 题</Badge>
        <h3 className="text-xl font-black">{question.title}</h3>
        <p className="mt-3 font-semibold leading-7">{question.stem}</p>
        <div className="mt-5 grid grid-cols-2 gap-3">
          {question.options.map((option) => (
            <button key={option} className="rounded-md border-2 border-ink bg-paper-100 p-3 text-left font-black hover:bg-orange">
              {option}
            </button>
          ))}
        </div>
      </section>
      <aside className="rounded-md border-2 border-ink bg-[#e7d6b8] p-4">
        <div className="text-3xl font-black">18:42</div>
        <p className="mt-1 text-sm font-semibold text-ink/70">剩余时间</p>
        <Button className="mt-5 w-full">提交本题</Button>
        <Button variant="paper" className="mt-3 w-full">查看解析</Button>
      </aside>
    </div>
  );
}

export function ReviewWindow() {
  return (
    <div className="grid grid-cols-[230px_1fr] gap-4">
      <aside className="rounded-md border-2 border-ink bg-[#dfe8bd] p-4">
        <Badge tone="green" className="mb-3">练习结果</Badge>
        <div className="text-4xl font-black">75%</div>
        <p className="mt-2 text-sm font-semibold">12 题中 9 题正确</p>
      </aside>
      <section className="rounded-md border-2 border-ink bg-paper-50 p-4">
        <h3 className="text-lg font-black">错因分析</h3>
        <p className="mt-3 text-sm font-semibold leading-6">应用题中没有把固定服务费作为截距处理，导致函数关系式少了常数项。</p>
        <div className="mt-4 rounded border border-ink bg-paper-100 p-3 text-sm">
          下一步：先练 3 道含固定成本的建模题，再回到综合题。
        </div>
      </section>
    </div>
  );
}

export function KnowledgeWindow() {
  return (
    <div className="grid grid-cols-[220px_1fr] gap-4">
      <aside className="rounded-md border-2 border-ink bg-paper-100 p-4 text-sm font-black">
        <Badge tone="ink" className="mb-3">公共知识库</Badge>
        <p className="text-lg">内容暂为空</p>
        <div className="mt-4 space-y-2 rounded border border-ink bg-paper-50 p-3 text-xs">
          <p>知识点：{publicKnowledgeStatus.knowledgePoints}</p>
          <p>标签：{publicKnowledgeStatus.tags}</p>
          <p>关系边：{publicKnowledgeStatus.edges}</p>
        </div>
        <Button className="mt-4 w-full" size="sm" variant="paper">
          录入公共知识库
        </Button>
        <p className="mt-3 text-xs font-bold leading-5 text-ink/60">
          仅预留 schema / import 入口
        </p>
      </aside>
      <section className="space-y-3">
        <div className="rounded-md border-2 border-ink bg-[#dfe8bd] p-4">
          <Badge tone="green" className="mb-3">个人知识库派生层</Badge>
          <p className="text-sm font-semibold leading-6">
            下方为静态个人学习画像示意。公共知识库内容保持空缺，后续由录入或导入流程填充标准知识点。
          </p>
        </div>
        <div className="rounded-md border-2 border-ink bg-paper-100 p-4">
          <div className="mb-3 flex items-center justify-between">
            <Badge tone="orange">Phase 4 RAG 管线</Badge>
            <span className="rounded border border-ink bg-paper-50 px-2 py-1 text-xs font-black">
              {ragPipelineStatus.provider}
            </span>
          </div>
          <div className="grid grid-cols-3 gap-3 text-sm font-black">
            {[
              ragPipelineStatus.ingestFormat,
              ragPipelineStatus.embeddingJobStatus,
              ragPipelineStatus.searchStatus,
            ].map((item) => (
              <div key={item} className="rounded border border-ink bg-paper-50 p-3">
                {item}
              </div>
            ))}
          </div>
          <div className="mt-3 grid grid-cols-[1fr_150px] gap-3 text-xs font-bold">
            <div className="rounded border border-ink bg-[#e8d099] p-3">
              <p>{ragPipelineStatus.keyPolicy}</p>
              <p className="mt-1 text-ink/70">查询样例：{ragPipelineStatus.sampleQuery}</p>
            </div>
            <div className="rounded border border-ink bg-paper-50 p-3">
              <p>chunks：{ragPipelineStatus.chunks}</p>
              <p>vectors：{ragPipelineStatus.vectors}</p>
              <p>trust：{ragPipelineStatus.trustScore}</p>
            </div>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-3">
          {knowledgePoints.map((point) => (
            <article key={point.name} className="rounded-md border-2 border-ink bg-paper-50 p-4">
              <Badge tone="blue" className="mb-3">{point.coverage}% 掌握</Badge>
              <h3 className="font-black">{point.name}</h3>
              <p className="mt-2 text-sm font-semibold text-ink/70">{point.source}</p>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}

export function ReportWindow() {
  return (
    <div className="grid grid-cols-4 gap-3">
      {reportMetrics.map((metric) => (
        <article key={metric.label} className="rounded-md border-2 border-ink bg-paper-100 p-4">
          <p className="text-sm font-black text-ink/60">{metric.label}</p>
          <div className="mt-2 text-3xl font-black">{metric.value}</div>
          <p className="mt-2 text-xs font-bold text-ink/70">{metric.detail}</p>
        </article>
      ))}
      <div className="col-span-4 rounded-md border-2 border-ink bg-[#dfe8bd] p-4 font-semibold">
        下一轮建议：围绕“实际问题建模”生成 8 题，保留 2 道图像交点复习题。
      </div>
    </div>
  );
}

export function ExportWindow() {
  return (
    <div className="grid grid-cols-[1fr_220px] gap-4">
      <section className="min-h-[300px] rounded-md border-2 border-ink bg-white p-6 shadow-[6px_6px_0_rgba(36,32,21,0.12)]">
        <h3 className="text-center text-xl font-black">一次函数专项训练</h3>
        <p className="mt-4 border-b border-ink pb-2 text-sm font-semibold">一、选择题（每题 4 分）</p>
        <p className="mt-4 text-sm">1. 若一次函数 y = 2x - 3 的图像经过点 A(a, 5)，则 a 的值是 ____。</p>
      </section>
      <aside className="rounded-md border-2 border-ink bg-paper-100 p-4">
        <Badge tone="orange" className="mb-3">导出设置</Badge>
        {["A4 试卷", "包含答案", "包含解析", "练习报告"].map((item) => (
          <div key={item} className="mb-2 rounded border border-ink bg-paper-50 px-3 py-2 text-sm font-black">
            {item}
          </div>
        ))}
      </aside>
    </div>
  );
}

export function SuggestionsWindow() {
  return (
    <div className="space-y-3">
      {[
        "应用题比例偏低，下一轮建议增加真实场景建模。",
        "错题集中在截距理解，先复习固定费用和初始值。",
        "本轮不需要增加难度，优先提高稳定性。",
      ].map((item) => (
        <div key={item} className="rounded-md border-2 border-ink bg-paper-100 p-4 text-sm font-bold">
          {item}
        </div>
      ))}
    </div>
  );
}
