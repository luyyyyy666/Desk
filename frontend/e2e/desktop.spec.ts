import { expect, test } from "@playwright/test";

test("renders the Learning OS desktop and opens a shortcut window", async ({ page }) => {
  await page.goto("/");

  await expect(page.getByRole("banner")).toContainText("我的师傅");
  await expect(page.getByRole("main")).toContainText("一次函数专项训练");
  await expect(page.getByRole("dialog", { name: "出题生成器" })).toBeVisible();

  await page.getByRole("button", { name: "错题本 弱点沉淀" }).click();

  await expect(page.getByRole("dialog", { name: "错题本" })).toBeVisible();
  await expect(page.getByText("实际问题建模")).toBeVisible();
});
