import {
  BookOpen,
  ClipboardEdit,
  FileDown,
  Lightbulb,
  NotebookTabs,
  PenTool,
  Recycle,
  Target,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import type { WindowId } from "@/lib/window-state";

export type DesktopIconData = {
  id: string;
  label: string;
  detail: string;
  windowId: WindowId;
  side: "left" | "right";
  icon: LucideIcon;
  x: number;
  y: number;
  fileColor: "orange" | "green" | "blue" | "paper" | "pink";
};

export type LearningLoopStep = {
  id: string;
  label: string;
  windowId: WindowId;
};

export type MockQuestion = {
  id: string;
  type: string;
  title: string;
  stem: string;
  options: string[];
  answer: string;
  explanation: string;
  knowledge: string[];
  difficulty: "基础" | "中等" | "提高";
  status: "待练习" | "正确" | "错题";
};

export const currentTask = {
  title: "一次函数专项训练",
  status: "已生成 12 题 / 待练习 / 2 个知识点需强化",
  subject: "八年级数学",
  source: "人教版 · 第十九章",
  goal: "巩固一次函数图像、解析式与实际应用题",
  questionCount: 12,
  duration: "25 分钟",
  mastery: 68,
};

export const learningLoop: LearningLoopStep[] = [
  { id: "goal", label: "目标", windowId: "generator" },
  { id: "generate", label: "生成", windowId: "generator" },
  { id: "edit", label: "编辑", windowId: "editor" },
  { id: "practice", label: "练习", windowId: "practice" },
  { id: "review", label: "解析", windowId: "review" },
  { id: "errors", label: "错题", windowId: "errors" },
  { id: "regenerate", label: "再生成", windowId: "generator" },
];

export const desktopIcons: DesktopIconData[] = [
  {
    id: "new-set",
    label: "新建题单",
    detail: "按目标生成",
    windowId: "generator",
    side: "left",
    icon: ClipboardEdit,
    x: 42,
    y: 72,
    fileColor: "orange",
  },
  {
    id: "practice",
    label: "专项练习",
    detail: "直接作答",
    windowId: "practice",
    side: "left",
    icon: PenTool,
    x: 54,
    y: 176,
    fileColor: "green",
  },
  {
    id: "errors",
    label: "错题本",
    detail: "弱点沉淀",
    windowId: "errors",
    side: "left",
    icon: NotebookTabs,
    x: 46,
    y: 282,
    fileColor: "pink",
  },
  {
    id: "knowledge",
    label: "知识库",
    detail: "教材来源",
    windowId: "knowledge",
    side: "left",
    icon: BookOpen,
    x: 76,
    y: 410,
    fileColor: "blue",
  },
  {
    id: "report",
    label: "学习报告",
    detail: "掌握度",
    windowId: "report",
    side: "right",
    icon: Target,
    x: 1260,
    y: 88,
    fileColor: "green",
  },
  {
    id: "export",
    label: "导出试卷",
    detail: "A4 / 解析",
    windowId: "export",
    side: "right",
    icon: FileDown,
    x: 1248,
    y: 206,
    fileColor: "paper",
  },
  {
    id: "suggestions",
    label: "师傅建议",
    detail: "下一步",
    windowId: "suggestions",
    side: "right",
    icon: Lightbulb,
    x: 1220,
    y: 340,
    fileColor: "orange",
  },
  {
    id: "trash",
    label: "回收站",
    detail: "草稿",
    windowId: "export",
    side: "right",
    icon: Recycle,
    x: 1286,
    y: 474,
    fileColor: "paper",
  },
];

export const mockQuestions: MockQuestion[] = [
  {
    id: "q1",
    type: "选择题",
    title: "图像与斜率",
    stem: "若一次函数 y = 2x - 3 的图像经过点 A(a, 5)，则 a 的值是？",
    options: ["2", "3", "4", "5"],
    answer: "4",
    explanation: "将 y = 5 代入 y = 2x - 3，得到 5 = 2a - 3，所以 a = 4。",
    knowledge: ["一次函数解析式", "代入求值"],
    difficulty: "基础",
    status: "正确",
  },
  {
    id: "q2",
    type: "填空题",
    title: "函数图像交点",
    stem: "直线 y = -x + 6 与 x 轴的交点坐标是 ______。",
    options: [],
    answer: "(6, 0)",
    explanation: "与 x 轴相交时 y = 0，代入得 0 = -x + 6，因此 x = 6。",
    knowledge: ["坐标轴交点", "一次函数图像"],
    difficulty: "中等",
    status: "待练习",
  },
  {
    id: "q3",
    type: "解答题",
    title: "实际应用建模",
    stem: "某打印店基础服务费 5 元，每打印一页加收 0.4 元。写出费用 y 与页数 x 的函数关系式，并求打印 30 页的费用。",
    options: [],
    answer: "y = 0.4x + 5，打印 30 页需 17 元。",
    explanation: "固定费用是截距 5，每页费用是斜率 0.4，因此 y = 0.4x + 5。x = 30 时，y = 12 + 5 = 17。",
    knowledge: ["一次函数应用", "函数建模"],
    difficulty: "中等",
    status: "错题",
  },
  {
    id: "q4",
    type: "选择题",
    title: "增减性判断",
    stem: "下列函数中，y 随 x 的增大而减小的是？",
    options: ["y = 3x + 1", "y = -2x + 4", "y = x - 5", "y = 0.5x"],
    answer: "y = -2x + 4",
    explanation: "一次函数 y = kx + b 中，当 k < 0 时，y 随 x 增大而减小。",
    knowledge: ["一次函数增减性"],
    difficulty: "基础",
    status: "待练习",
  },
];

export const knowledgePoints = [
  { name: "一次函数解析式", coverage: 92, source: "19.2.1 正比例函数与一次函数" },
  { name: "函数图像与交点", coverage: 76, source: "19.2.2 一次函数的图像" },
  { name: "实际问题建模", coverage: 54, source: "19.3 课题学习" },
  { name: "增减性", coverage: 81, source: "19.2.2 一次函数的图像" },
];

export const publicKnowledgeStatus = {
  isEmpty: true,
  knowledgePoints: 0,
  tags: 0,
  edges: 0,
  importMode: "schema-only",
} as const;

export const ragPipelineStatus = {
  provider: "New API / OpenAI-compatible",
  keyPolicy: "后端网关持有 provider key",
  ingestFormat: "plain_text ingest",
  embeddingJobStatus: "Embedding Job",
  searchStatus: "向量检索",
  sampleQuery: "一次函数",
  chunks: 2,
  vectors: 2,
  trustScore: 0.9,
} as const;

export const persistedPlan = {
  id: "plan_run_fixture_linear_function_001",
  agentRunId: "run_fixture_linear_function_001",
  status: "ready",
  currentStepId: "step_01_search_knowledge",
  steps: [
    {
      id: "step_01_search_knowledge",
      skillId: "search_knowledge",
      title: "检索知识",
      status: "pending",
    },
    {
      id: "step_02_generate_question_set",
      skillId: "generate_question_set",
      title: "生成题单",
      status: "pending",
    },
    {
      id: "step_03_check_curriculum_alignment",
      skillId: "check_curriculum_alignment",
      title: "课标对齐检查",
      status: "pending",
    },
    {
      id: "step_04_evaluate_question_quality",
      skillId: "evaluate_question_quality",
      title: "题目质量评估",
      status: "pending",
    },
  ],
} as const;

export const mistakeGroups = [
  {
    knowledge: "实际问题建模",
    count: 3,
    reason: "容易漏掉固定费用或把斜率、截距写反。",
    recommendation: "下一轮增加 4 道分段语境应用题。",
  },
  {
    knowledge: "函数图像与交点",
    count: 2,
    reason: "代入 x 轴或 y 轴条件时，坐标含义不稳定。",
    recommendation: "先做坐标轴交点专项，再做综合题。",
  },
];

export const reportMetrics = [
  { label: "掌握度", value: "68%", detail: "较上次 +9%" },
  { label: "正确率", value: "75%", detail: "12 题中 9 题正确" },
  { label: "薄弱点", value: "2", detail: "建模、交点" },
  { label: "建议题量", value: "8", detail: "下一轮小测" },
];
