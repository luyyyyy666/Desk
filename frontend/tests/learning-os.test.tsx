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

  it("can close the active floating window", async () => {
    const user = userEvent.setup();
    render(<LearningDesktop defaultWindow="errors" />);

    expect(screen.getByRole("dialog", { name: "错题本" })).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "关闭错题本" }));

    expect(screen.queryByRole("dialog", { name: "错题本" })).not.toBeInTheDocument();
  });
});
