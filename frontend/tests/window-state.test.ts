import { describe, expect, it } from "vitest";
import {
  desktopWindows,
  getDefaultWindowForRoute,
  getWindowById,
  routeDefaults,
} from "@/lib/window-state";
import {
  currentTask,
  desktopIcons,
  learningLoop,
  mockQuestions,
  publicKnowledgeStatus,
} from "@/lib/mock-data";

describe("Learning OS static state", () => {
  it("maps focused routes to their default windows", () => {
    expect(getDefaultWindowForRoute("/")).toBe("generator");
    expect(getDefaultWindowForRoute("/generate")).toBe("generator");
    expect(getDefaultWindowForRoute("/practice")).toBe("practice");
    expect(getDefaultWindowForRoute("/errors")).toBe("errors");
    expect(getDefaultWindowForRoute("/knowledge")).toBe("knowledge");
    expect(getDefaultWindowForRoute("/review")).toBe("review");
    expect(Object.keys(routeDefaults)).toHaveLength(6);
  });

  it("defines all primary desktop windows", () => {
    expect(desktopWindows.map((window) => window.id)).toEqual([
      "generator",
      "editor",
      "practice",
      "review",
      "errors",
      "knowledge",
      "report",
      "export",
      "suggestions",
    ]);

    expect(getWindowById("errors")?.title).toBe("错题本");
  });

  it("contains the visible task loop and static question set", () => {
    expect(currentTask.title).toBe("一次函数专项训练");
    expect(currentTask.status).toContain("已生成 12 题");
    expect(learningLoop.map((step) => step.label)).toEqual([
      "目标",
      "生成",
      "编辑",
      "练习",
      "解析",
      "错题",
      "再生成",
    ]);
    expect(mockQuestions).toHaveLength(4);
  });

  it("contains desktop shortcuts for the primary workspace entries", () => {
    expect(desktopIcons.map((icon) => icon.label)).toEqual([
      "新建题单",
      "专项练习",
      "错题本",
      "知识库",
      "学习报告",
      "导出试卷",
      "师傅建议",
      "回收站",
    ]);
  });

  it("keeps the public knowledge base empty in the static phase 3 shell", () => {
    expect(publicKnowledgeStatus).toEqual({
      isEmpty: true,
      knowledgePoints: 0,
      tags: 0,
      edges: 0,
      importMode: "schema-only",
    });
  });
});
