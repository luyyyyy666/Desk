# Learning OS Frontend Design

Date: 2026-05-13

## Summary

Build a high-fidelity static PC web prototype for "我的师傅" using Next.js 15, TypeScript, shadcn/ui, Tailwind CSS, and React. The interface should reference PostHog's desktop-like product surface: a textured desktop canvas, draggable-feeling icons, floating windows, and playful object placement. The design should translate that language into an education-focused "Learning OS" for generating questions, practicing, reviewing explanations, collecting mistakes, and using that learning state to guide the next generation cycle.

This phase is UI design only. It does not include real Agent APIs, authentication, persistence, database work, or mobile-specific design.

## Product Direction

The product is not split into teacher and student modes. It is a unified learning and question-generation workspace. The same user can generate questions, edit them, practice them, review explanations, collect mistakes, inspect knowledge sources, export materials, and start the next generation round.

The core loop is:

```text
Generate questions / paper
  -> Edit generated questions
  -> Practice directly
  -> Review answers and explanations
  -> Save mistakes and weak points
  -> Use that feedback to guide the next generation
```

The first prototype should make this loop visible in the first screen and in the major windows.

## Chosen Approach

Use the "Desktop OS + central mission board" approach.

The first screen is a full desktop workspace rather than a conventional SaaS dashboard. It keeps PostHog's memorable desktop metaphor while giving the center of the page a practical working surface.

Rejected alternatives:

- Full workbench with desktop decoration: easier to implement but too close to generic education SaaS.
- Flow-map desktop: explains the loop clearly but risks becoming a diagram instead of a usable tool.

## Target Platform

The first version targets PC web only.

Primary viewport range:

```text
1280px to 1920px wide desktop browsers
```

Mobile and tablet-specific layouts are out of scope for this design phase. The implementation should avoid obvious desktop breakage at common laptop widths, but it does not need a mobile-first layout.

## Information Architecture

Primary desktop entries:

- New question set
- Focused practice
- Mistake book
- Knowledge base
- Learning report
- Export paper
- Master suggestions
- Trash

Primary windows:

- Generator window
- Question editor window
- Practice window
- Review and evaluation window
- Mistake book window
- Knowledge base window
- Learning report window
- Export window

Primary static route set:

```text
/           Desktop home
/generate   Generator-focused state
/practice   Practice-focused state
/errors     Mistake book-focused state
/knowledge  Knowledge base-focused state
/review     Review and evaluation-focused state
```

Routes can render the same desktop shell with different default windows opened. This keeps the UI feeling like one OS while still allowing direct links.

## First Screen

The first screen is a `LearningDesktop`.

Main regions:

- `TopBar`: shallow OS-style menu bar with brand, menu groups, global actions, and a primary action.
- `DesktopCanvas`: full remaining viewport with paper texture and placed desktop items.
- `DesktopIconGrid`: left and right groups of file-like shortcuts.
- `MissionBoard`: central task board showing the current learning loop state.
- `LearningIsland`: large education-themed visual object in the lower-right area.
- `FloatingWindowLayer`: stack for opened static windows.

Default desktop content:

- Current task: `一次函数专项训练`
- Status: `已生成 12 题 / 待练习 / 2 个知识点需强化`
- Actions: `继续练习`, `重新生成`, `查看解析`
- Loop progress: `目标 -> 生成 -> 编辑 -> 练习 -> 解析 -> 错题 -> 再生成`

The central task board should feel like a clipboard, paper sheet, or desktop note rather than a generic dashboard card. It can use borders, paper shadows, tabs, and small status stamps.

## Window Content

### Generator Window

Purpose: show the static question-generation setup and generated result preview.

Content:

- Learning goal prompt
- Subject / chapter / knowledge point controls
- Difficulty selector
- Question count
- Question type distribution
- Source scope such as textbook chapter or knowledge base
- Generated question list preview
- Static "Master suggestion" panel

No real generation is required. Use mock data and polished loading/completed states if useful for the prototype.

### Question Editor Window

Purpose: show how generated questions can be refined before practice or export.

Content:

- Left question list
- Central question stem, options, answer, and explanation
- Right quality checks: difficulty, coverage, clarity, source alignment
- Suggested edits from the Agent
- Actions: replace, simplify, deepen explanation, send to practice

### Practice Window

Purpose: show direct practice against the generated set.

Content:

- Current question
- Answer controls
- Question navigation
- Timer or progress indicator
- Submit and reveal explanation actions
- Static answered / unanswered / incorrect states

This is a static prototype; answer checking can be simulated through mock state.

### Review And Evaluation Window

Purpose: show answer feedback and learning evaluation after practice.

Content:

- Correctness summary
- Explanation for selected question
- Reason for mistake
- Related knowledge points
- Recommended next action

### Mistake Book Window

Purpose: show accumulated weak points and mistakes from practice.

Content:

- Mistakes grouped by knowledge point
- Incorrect answer and correct answer
- Error reason
- Related practice recommendation
- Action to regenerate similar questions

### Knowledge Base Window

Purpose: show the domain knowledge layer supporting generation.

Content:

- Textbook / curriculum chapter tree
- Knowledge point cards
- Question templates
- Source snippets and references
- Coverage indicators

### Learning Report Window

Purpose: summarize current progress and feed the next generation loop.

Content:

- Mastery overview
- Weak knowledge points
- Question type performance
- Recommended next generation settings
- Recent practice history

### Export Window

Purpose: preview static export formats.

Content:

- Paper preview
- Answer sheet preview
- Explanation document preview
- Practice report preview
- Format toggles such as A4, answer included, explanations included

## Visual System

Visual thesis: a playful paper-and-desktop learning OS, with the tactility of files, books, stamps, notes, and study tools rather than a generic analytics dashboard.

Palette:

- Paper background: warm beige
- Surface: off-white / paper white
- Text and outlines: dark ink
- Primary action: PostHog-like orange
- Learning progress: muted green
- Knowledge/source accents: restrained blue

Texture:

- Use a subtle paper grain or dot texture on the desktop canvas.
- Keep texture quiet enough that Chinese text remains readable.

Shape and borders:

- Prefer 6px to 8px radii for buttons, windows, and controls.
- Use black or dark brown outlines where they strengthen the desktop-object feel.
- Avoid large soft SaaS cards and nested card stacks.

Typography:

- Use system fonts for Chinese-first UI.
- Use strong weight contrast for labels, board titles, and window headers.
- Keep letter spacing at 0.
- Avoid oversized marketing hero typography inside the app surface.

Icons and illustration:

- Desktop shortcuts should look like documents, books, papers, notes, stamps, or folders.
- Use lucide-react for functional button icons where a standard icon exists.
- The large `LearningIsland` should be an education-themed desk or object cluster, not a decorative gradient.
- Do not use generic gradient blobs or abstract SaaS decoration.

Motion:

- Desktop icons lift on hover.
- Windows open with a restrained scale/fade motion.
- Dragging a desktop item shows shadow and slight rotation.
- Mission progress steps can highlight as the user moves between static states.

Motion should make the interface feel tactile and interactive, not noisy.

## Component Architecture

Core components:

```text
LearningDesktop
TopBar
DesktopCanvas
DesktopIcon
MissionBoard
LearningIsland
FloatingWindowLayer
FloatingWindow
WindowHeader
GeneratorWindow
EditorWindow
PracticeWindow
ReviewWindow
ErrorBookWindow
KnowledgeWindow
ReportWindow
ExportWindow
```

Static data modules:

```text
mock-task.ts
mock-questions.ts
mock-knowledge.ts
mock-errors.ts
mock-report.ts
```

State model:

- Local React state controls open windows.
- Local React state controls selected desktop item.
- Local React state controls active question / active mock state.
- Routes can choose the default opened window.

No server state is required.

## Technology Requirements

Use:

- Next.js 15
- TypeScript
- App Router
- React
- Tailwind CSS
- shadcn/ui
- lucide-react

The existing `frontend` folder currently appears to be a Vite + React project. Implementation planning should decide whether to replace it with a Next.js app or create a clean Next.js app in place after preserving any useful static assets. The target architecture is Next.js 15, not Vite.

## Out Of Scope

- Real Agent API integration
- User authentication
- Database or persistence
- Real document export generation
- Real answer grading
- Mobile-specific design
- Role separation between teacher and student
- Production deployment

## Acceptance Criteria

- The first screen clearly reads as a desktop-style Learning OS.
- The UI visibly borrows PostHog's desktop metaphor without copying its brand assets or exact scene.
- The core loop from generation to practice to mistakes to regeneration is visible.
- The prototype includes all primary windows listed in this spec.
- The implementation uses mock data only.
- The prototype feels designed for PC web, especially 1280px to 1920px widths.
- The UI avoids generic dashboard-card mosaics.
- The visual system uses education-specific desktop objects and functional windows.
- The app builds and runs locally with standard Next.js scripts.

## Implementation Constraints

- shadcn/ui should provide base primitives, but components must be styled to match the desktop OS visual language.
- If drag behavior is implemented in the static prototype, it can be visual-only and does not need persistence.
- The first implementation pass should use CSS-built or inline SVG education object clusters for `LearningIsland`. Commissioned or AI-generated illustration assets are outside this prototype scope.
