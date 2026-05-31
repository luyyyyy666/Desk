import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { LearningDesktop } from "@/components/learning-os/learning-desktop";

describe("LearningDesktop", () => {
  it("renders the Learning OS desktop shell", () => {
    render(<LearningDesktop defaultWindow="generator" />);

    expect(screen.getByRole("banner")).toHaveTextContent("我的师傅");
    expect(screen.getByRole("main")).toHaveTextContent("一次函数专项训练");
    expect(screen.getByText("目标")).toBeInTheDocument();
    expect(screen.getAllByText("生成").length).toBeGreaterThan(0);
    expect(screen.getByText("编辑")).toBeInTheDocument();
    expect(screen.getAllByText("练习").length).toBeGreaterThan(0);
    expect(screen.getByText("解析")).toBeInTheDocument();
    expect(screen.getAllByText("错题").length).toBeGreaterThan(0);
    expect(screen.getByText("再生成")).toBeInTheDocument();
  });

  it("renders all desktop shortcuts", () => {
    render(<LearningDesktop defaultWindow="generator" />);

    for (const label of [
      "新建题单 按目标生成",
      "专项练习 直接作答",
      "错题本 弱点沉淀",
      "知识库 教材来源",
      "学习报告 掌握度",
      "导出试卷 A4 / 解析",
      "师傅建议 下一步",
      "回收站 草稿",
    ]) {
      expect(screen.getByRole("button", { name: label })).toBeInTheDocument();
    }
  });

  it("opens a floating window when a desktop shortcut is clicked", async () => {
    const user = userEvent.setup();
    render(<LearningDesktop defaultWindow="generator" />);

    await user.click(screen.getByRole("button", { name: "错题本 弱点沉淀" }));

    expect(screen.getByRole("dialog", { name: "错题本" })).toBeInTheDocument();
    expect(screen.getByText("实际问题建模")).toBeInTheDocument();
  });

  it("shows an empty public knowledge base entry point in the knowledge window", () => {
    render(<LearningDesktop defaultWindow="knowledge" />);

    expect(screen.getByRole("dialog", { name: "知识库" })).toBeInTheDocument();
    expect(screen.getByText("公共知识库")).toBeInTheDocument();
    expect(screen.getByText("内容暂为空")).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "录入公共知识库" }),
    ).toBeInTheDocument();
    expect(screen.getByText("仅预留 schema / import 入口")).toBeInTheDocument();
  });

  it("shows phase 4 rag ingestion embedding and search status in the knowledge window", () => {
    render(<LearningDesktop defaultWindow="knowledge" />);

    expect(screen.getByText("Phase 4 RAG 管线")).toBeInTheDocument();
    expect(screen.getByText("plain_text ingest")).toBeInTheDocument();
    expect(screen.getByText("Embedding Job")).toBeInTheDocument();
    expect(screen.getByText("向量检索")).toBeInTheDocument();
    expect(screen.getByText("New API / OpenAI-compatible")).toBeInTheDocument();
    expect(screen.getByText("后端网关持有 provider key")).toBeInTheDocument();
    expect(screen.getByText("查询样例：一次函数")).toBeInTheDocument();
  });

  it("shows persisted phase 5 plan progress in the generator window", () => {
    render(<LearningDesktop defaultWindow="generator" />);

    expect(screen.getByText("Phase 5 Plan")).toBeInTheDocument();
    expect(screen.getByText("plan_run_fixture_linear_function_001")).toBeInTheDocument();
    expect(screen.getByText("step_01_search_knowledge")).toBeInTheDocument();
    expect(screen.getAllByText("search_knowledge").length).toBeGreaterThan(0);
    expect(screen.getByText("generate_question_set")).toBeInTheDocument();
    expect(screen.getByText("check_curriculum_alignment")).toBeInTheDocument();
    expect(screen.getByText("evaluate_question_quality")).toBeInTheDocument();
  });

  it("shows phase 6 tool manager progress events in the generator window", () => {
    render(<LearningDesktop defaultWindow="generator" />);

    expect(screen.getByText("Phase 6 Tool Manager")).toBeInTheDocument();
    expect(screen.getByText("tool_call_run_fixture_linear_function_001_001")).toBeInTheDocument();
    expect(screen.getByText("mock executor")).toBeInTheDocument();
    expect(screen.getByText("tool_call_started")).toBeInTheDocument();
    expect(screen.getByText("tool_call_completed")).toBeInTheDocument();
  });

  it("shows phase 7 agent run state and resume status in the generator window", () => {
    render(<LearningDesktop defaultWindow="generator" />);

    expect(screen.getByText("Phase 7 State")).toBeInTheDocument();
    expect(screen.getByText("run_fixture_linear_function_001")).toBeInTheDocument();
    expect(screen.getByText("tool_execution")).toBeInTheDocument();
    expect(screen.getByText("waiting_for_user")).toBeInTheDocument();
    expect(screen.getByText("resume_plan_step")).toBeInTheDocument();
    expect(screen.getByText("transitions: 7")).toBeInTheDocument();
  });

  it("can close the active floating window", async () => {
    const user = userEvent.setup();
    render(<LearningDesktop defaultWindow="errors" />);

    expect(screen.getByRole("dialog", { name: "错题本" })).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "关闭错题本" }));

    expect(screen.queryByRole("dialog", { name: "错题本" })).not.toBeInTheDocument();
  });
});
