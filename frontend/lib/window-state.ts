import type { ComponentType } from "react";

export type WindowId =
  | "generator"
  | "editor"
  | "practice"
  | "review"
  | "errors"
  | "knowledge"
  | "report"
  | "export"
  | "suggestions";

export type DesktopWindowDefinition = {
  id: WindowId;
  title: string;
  eyebrow: string;
  width: number;
  height: number;
  x: number;
  y: number;
};

export const desktopWindows: DesktopWindowDefinition[] = [
  { id: "generator", title: "出题生成器", eyebrow: "Generate", width: 760, height: 500, x: 310, y: 92 },
  { id: "editor", title: "题目编辑器", eyebrow: "Edit", width: 820, height: 520, x: 276, y: 104 },
  { id: "practice", title: "练习窗口", eyebrow: "Practice", width: 780, height: 520, x: 332, y: 112 },
  { id: "review", title: "解析与评估", eyebrow: "Review", width: 780, height: 510, x: 348, y: 116 },
  { id: "errors", title: "错题本", eyebrow: "Mistakes", width: 760, height: 500, x: 348, y: 104 },
  { id: "knowledge", title: "知识库", eyebrow: "Knowledge", width: 800, height: 520, x: 316, y: 96 },
  { id: "report", title: "学习报告", eyebrow: "Report", width: 760, height: 480, x: 360, y: 120 },
  { id: "export", title: "导出窗口", eyebrow: "Export", width: 760, height: 480, x: 372, y: 116 },
  { id: "suggestions", title: "师傅建议", eyebrow: "Coach", width: 620, height: 420, x: 424, y: 148 },
];

export const routeDefaults: Record<string, WindowId> = {
  "/": "generator",
  "/generate": "generator",
  "/practice": "practice",
  "/errors": "errors",
  "/knowledge": "knowledge",
  "/review": "review",
};

export function getDefaultWindowForRoute(route: string): WindowId {
  return routeDefaults[route] ?? "generator";
}

export function getWindowById(id: WindowId): DesktopWindowDefinition | undefined {
  return desktopWindows.find((window) => window.id === id);
}

export type WindowComponentMap = Partial<Record<WindowId, ComponentType>>;
