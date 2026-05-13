# Learning OS Frontend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a high-fidelity static PC web prototype for "我的师傅" as a Next.js 15 Learning OS desktop.

**Architecture:** Create a clean `frontend/` Next.js App Router project with focused React components, static mock data, and local client state for desktop windows. The root route and focus routes render the same desktop shell with different default active windows.

**Tech Stack:** Next.js 15, TypeScript, React 19, Tailwind CSS, shadcn-style primitives, lucide-react, Vitest, Testing Library, Playwright.

---

## File Structure

- Create `frontend/package.json`: scripts and dependencies for Next.js, tests, lint, and Playwright.
- Create `frontend/app/layout.tsx`: root metadata and global stylesheet import.
- Create `frontend/app/page.tsx`: desktop home route.
- Create `frontend/app/generate/page.tsx`, `frontend/app/practice/page.tsx`, `frontend/app/errors/page.tsx`, `frontend/app/knowledge/page.tsx`, `frontend/app/review/page.tsx`: focus routes.
- Create `frontend/app/globals.css`: Tailwind imports, design tokens, desktop texture, component utility classes.
- Create `frontend/components/learning-os/learning-desktop.tsx`: client shell and window state.
- Create `frontend/components/learning-os/top-bar.tsx`: OS top navigation.
- Create `frontend/components/learning-os/desktop-icon.tsx`: file-like desktop icon.
- Create `frontend/components/learning-os/mission-board.tsx`: central loop board.
- Create `frontend/components/learning-os/learning-island.tsx`: CSS-built education object cluster.
- Create `frontend/components/learning-os/floating-window.tsx`: reusable window frame.
- Create `frontend/components/learning-os/windows/*.tsx`: static feature windows.
- Create `frontend/components/ui/button.tsx`, `frontend/components/ui/badge.tsx`, `frontend/components/ui/progress.tsx`: shadcn-style primitives.
- Create `frontend/lib/mock-data.ts`: static task, question, knowledge, error, report, and window data.
- Create `frontend/lib/window-state.ts`: route-to-window mapping and window metadata helpers.
- Create `frontend/lib/utils.ts`: class name helper.
- Create `frontend/tests/learning-os.test.tsx`: component behavior tests.
- Create `frontend/tests/window-state.test.ts`: data and route mapping tests.
- Create `frontend/e2e/desktop.spec.ts`: Playwright smoke test for desktop rendering.

## Visual Thesis

Create a tactile paper-and-desktop learning OS: warm paper grain, dark ink outlines, orange primary actions, muted green learning progress, restrained blue knowledge accents, file-like shortcuts, floating windows, and a central mission board. The first viewport should feel like a product workspace, not a marketing landing page or generic card dashboard.

## Content Plan

The first screen shows the working desktop, not an explainer page. It exposes the current task, desktop shortcuts, the learning loop, and a large education object cluster. Feature details live inside floating windows.

## Interaction Thesis

Use three restrained interactions: desktop icons lift and rotate slightly on hover or drag, windows open as layered static panels with close/minimize controls, and mission loop steps highlight based on the active window.

---

### Task 1: Scaffold Next.js Frontend

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/next.config.ts`
- Create: `frontend/tsconfig.json`
- Create: `frontend/postcss.config.mjs`
- Create: `frontend/tailwind.config.ts`
- Create: `frontend/vitest.config.ts`
- Create: `frontend/playwright.config.ts`
- Create: `frontend/.gitignore`
- Create: `frontend/app/layout.tsx`
- Create: `frontend/app/page.tsx`
- Create: `frontend/app/globals.css`

- [ ] **Step 1: Write scaffold files**

Create a clean Next.js 15 project under `frontend/` with scripts:

```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "lint": "next lint",
    "test": "vitest run",
    "test:watch": "vitest",
    "e2e": "playwright test"
  }
}
```

- [ ] **Step 2: Install dependencies**

Run: `npm install`

Expected: lockfile is created and dependencies install under `frontend/node_modules`.

- [ ] **Step 3: Run baseline build**

Run: `npm run build`

Expected: Next.js builds the minimal home route.

### Task 2: Add Route Mapping And Mock Data Tests First

**Files:**
- Create: `frontend/tests/window-state.test.ts`
- Create: `frontend/lib/window-state.ts`
- Create: `frontend/lib/mock-data.ts`

- [ ] **Step 1: Write failing route and data tests**

Test route defaults, required window ids, and the visible learning loop.

- [ ] **Step 2: Run tests to verify failure**

Run: `npm test -- tests/window-state.test.ts`

Expected: FAIL because `lib/window-state.ts` and `lib/mock-data.ts` do not exist.

- [ ] **Step 3: Implement mock data and route mapping**

Create static data for the current task, desktop icons, learning loop, questions, knowledge points, mistakes, report, and export options.

- [ ] **Step 4: Run tests to verify pass**

Run: `npm test -- tests/window-state.test.ts`

Expected: PASS.

### Task 3: Add Component Behavior Tests First

**Files:**
- Create: `frontend/tests/learning-os.test.tsx`
- Create: `frontend/components/learning-os/learning-desktop.tsx`
- Create: `frontend/components/learning-os/top-bar.tsx`
- Create: `frontend/components/learning-os/desktop-icon.tsx`
- Create: `frontend/components/learning-os/mission-board.tsx`
- Create: `frontend/components/learning-os/floating-window.tsx`
- Create: `frontend/components/learning-os/learning-island.tsx`
- Create: `frontend/components/ui/button.tsx`
- Create: `frontend/components/ui/badge.tsx`
- Create: `frontend/components/ui/progress.tsx`
- Create: `frontend/lib/utils.ts`

- [ ] **Step 1: Write failing component tests**

Tests should verify the desktop renders brand text, current task, loop steps, desktop icons, and opens the mistake book window after clicking the shortcut.

- [ ] **Step 2: Run tests to verify failure**

Run: `npm test -- tests/learning-os.test.tsx`

Expected: FAIL because components are missing.

- [ ] **Step 3: Implement shared components**

Build the desktop shell, top bar, icon, mission board, floating window, and learning island.

- [ ] **Step 4: Run tests to verify pass**

Run: `npm test -- tests/learning-os.test.tsx`

Expected: PASS.

### Task 4: Implement Feature Windows And Routes

**Files:**
- Create: `frontend/components/learning-os/windows/generator-window.tsx`
- Create: `frontend/components/learning-os/windows/editor-window.tsx`
- Create: `frontend/components/learning-os/windows/practice-window.tsx`
- Create: `frontend/components/learning-os/windows/review-window.tsx`
- Create: `frontend/components/learning-os/windows/error-book-window.tsx`
- Create: `frontend/components/learning-os/windows/knowledge-window.tsx`
- Create: `frontend/components/learning-os/windows/report-window.tsx`
- Create: `frontend/components/learning-os/windows/export-window.tsx`
- Create: `frontend/app/generate/page.tsx`
- Create: `frontend/app/practice/page.tsx`
- Create: `frontend/app/errors/page.tsx`
- Create: `frontend/app/knowledge/page.tsx`
- Create: `frontend/app/review/page.tsx`
- Modify: `frontend/app/page.tsx`

- [ ] **Step 1: Extend tests for focused routes and windows**

Add assertions that focused route components render with their expected default window title.

- [ ] **Step 2: Run tests to verify failure**

Run: `npm test`

Expected: FAIL until the route pages and window components exist.

- [ ] **Step 3: Implement windows and focus routes**

Each window uses mock data and utility copy. No API calls, auth, or persistence.

- [ ] **Step 4: Run tests to verify pass**

Run: `npm test`

Expected: PASS.

### Task 5: Apply Visual System And PC Web Polish

**Files:**
- Modify: `frontend/app/globals.css`
- Modify: `frontend/components/learning-os/*.tsx`
- Modify: `frontend/components/learning-os/windows/*.tsx`

- [ ] **Step 1: Implement desktop visual system**

Add paper texture, warm surfaces, dark outlines, object-like icons, mission board styling, window layering, hover states, and CSS-only learning island.

- [ ] **Step 2: Check color and layout constraints**

Run: `Select-String -Path frontend/app/globals.css -Pattern '#|rgb|hsl'`

Expected: Palette contains warm paper, ink, orange, green, and blue; no purple-blue gradient or generic blob styling.

- [ ] **Step 3: Run build and tests**

Run: `npm test` and `npm run build`

Expected: both pass.

### Task 6: Add Playwright Smoke Test And Verify

**Files:**
- Create: `frontend/e2e/desktop.spec.ts`

- [ ] **Step 1: Write desktop smoke test**

Test should visit `/`, assert desktop shell content, click a shortcut, and assert the corresponding window title appears.

- [ ] **Step 2: Run Playwright install if needed**

Run: `npx playwright install chromium`

Expected: Chromium browser is available for the smoke test.

- [ ] **Step 3: Run smoke test**

Run: `npm run e2e`

Expected: PASS.

- [ ] **Step 4: Run final verification**

Run: `npm test`, `npm run build`, and `npm run e2e`.

Expected: all pass.

## Self-Review

- Spec coverage: Tasks cover Next.js 15, static mock data, PC desktop shell, all primary windows, focus routes, desktop visual system, and verification.
- Scope: No API integration, auth, database, real export generation, real grading, or mobile design.
- Risk: Playwright browser installation may require network; if it fails, report the exact failure and complete unit/build verification.
