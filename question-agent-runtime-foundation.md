# 出题 Agent 底层架构设计

本文档定义一个面向“中学生 / 中学老师”的出题 Agent 底层架构。这里先不展开具体出题业务能力，而是确定 Agent Runtime、知识检索层和运行测试支架的核心组成：

- Memory 记忆
- Planning 规划
- Tool Manager 工具管理
- State 状态管理
- Guardrails 安全约束
- Evaluation 评估
- RAG / Knowledge Retrieval 知识检索层
- Harness 运行与测试支架

其中 Memory、Planning、Tool Manager、State、Guardrails、Evaluation 构成通用 Agent Runtime；RAG / Knowledge Retrieval 作为知识支撑层接入 Runtime；Harness 作为外层运行与测试支架包裹整个 Runtime。后续的“出题 Agent”可以作为业务层运行在这个架构之上。

---

## 1. 总体架构

底层执行链路如下：

```text
Harness
  ↓
User Request
  ↓
Context Builder
  ↓
Memory
  ↓
RAG / Knowledge Retrieval
  ↓
Planning
  ↓
Guardrails
  ↓
Tool Manager
  ↓
State
  ↓
Evaluation
  ↓
Response / Persist
```

模块职责可以概括为：

```text
Memory：记住长期信息
RAG / Knowledge Retrieval：检索教材、大纲、题库和业务知识
Planning：决定接下来怎么做
Tool Manager：决定能用什么工具、如何调用
State：记录当前任务做到哪一步
Guardrails：判断能不能做、有没有风险
Evaluation：判断做得好不好、是否完成
Harness：提供运行、复现、测试、压测、回归和观测能力
```

需要特别区分：

```text
Memory 管长期上下文
RAG 管外部知识和领域知识
State 管当前任务进度
```

如果 Memory、RAG 和 State 混在一起，后续会导致任务恢复、用户偏好管理、知识溯源、错误重试和审计都变得混乱。

Harness 不参与具体业务决策，它负责让整个 Agent 系统可运行、可测试、可复现、可评估。

---

## 2. Memory 记忆模块

### 2.1 模块定位

Memory 负责保存跨会话、可复用的长期信息。

它不是简单的聊天记录，而是经过筛选、压缩、结构化后的上下文资产。

### 2.2 记忆分类

```text
Memory
├─ Conversation Memory：历史对话摘要
├─ User Profile Memory：用户画像
├─ Preference Memory：用户偏好
├─ Domain Memory：业务知识沉淀
├─ Task Memory：历史任务记录
└─ Feedback Memory：用户反馈与修正
```

### 2.3 出题 Agent 中可保存的记忆

对于老师用户：

```text
任教学科
任教年级
教材版本
常用题型
偏好的题目难度
偏好的解析详细程度
常用试卷结构
历史生成过的试卷
老师修改过的题目
老师标记为高质量或低质量的题目
```

对于学生用户：

```text
所在年级
学习阶段
薄弱知识点
历史错题
常错题型
常见错误原因
当前学习目标
讲解偏好
练习完成情况
```

### 2.4 记忆写入原则

不是所有信息都应该写入长期记忆。

写入前需要判断：

```text
这个信息是否长期有效
这个信息是否对未来任务有用
这个信息是否涉及隐私或敏感信息
这个信息是用户明确表达的，还是系统推断的
这个信息是否允许被用户查看、修改、删除
```

### 2.5 推荐数据结构

```json
{
  "memory_id": "mem_001",
  "user_id": "u_001",
  "memory_type": "preference",
  "scope": "user",
  "content": "用户偏好选择题难度中等，解析需要详细",
  "source": "conversation",
  "confidence": 0.86,
  "created_at": "2026-05-11T10:00:00+08:00",
  "updated_at": "2026-05-11T10:00:00+08:00",
  "expires_at": null
}
```

### 2.6 Memory 的关键能力

```text
读取相关记忆
写入新记忆
更新旧记忆
删除错误记忆
压缩历史对话
区分事实、偏好、推断、临时上下文
```

---

## 3. RAG / Knowledge Retrieval 知识检索层

### 3.1 模块定位

RAG / Knowledge Retrieval 负责检索外部知识、教材内容、课程标准、题库资源和业务知识。

它解决的问题是：Agent 不能只依赖 LLM 的参数记忆来出题，而要基于可追溯、可更新、可约束的知识来源工作。

### 3.2 RAG 与 Memory 的区别

```text
Memory：记用户相关的信息
RAG：查领域相关的知识
```

例如：

```text
Memory 记住：这位老师偏好中等难度、解析详细、使用人教版教材
RAG 检索：人教版八年级一次函数对应的知识点、例题、考查方式
```

二者不能混在一起：

```text
用户偏好不应该放进教材知识库
教材知识不应该作为用户长期记忆保存
学生错题可以进入 Memory，也可以沉淀为班级统计，但不等同于通用题库
```

### 3.3 出题 Agent 需要检索的知识

```text
课程标准
教材章节
知识点体系
能力要求
题型模板
历史题库
高质量例题
常见易错点
评分标准
考试说明
地区或学校的出题规范
```

### 3.4 推荐知识库分层

```text
Knowledge Base
├─ Curriculum KB：课程标准与知识点体系
├─ Textbook KB：教材版本、章节、例题、习题
├─ Question KB：题库、题型、答案、解析
├─ Pedagogy KB：教学策略、易错点、讲解方式
├─ Rubric KB：评分标准、阅卷规则
└─ Institution KB：学校、地区、老师自定义规范
```

### 3.5 RAG 检索流程

```text
1. 根据用户请求识别检索意图
2. 从 Memory 读取用户偏好和教材版本
3. 构造检索查询
4. 检索相关知识片段
5. 对结果重排和过滤
6. 做可信度与来源检查
7. 将检索结果交给 Planning 或题目生成步骤
8. 在输出中保留必要的知识来源引用
```

### 3.6 RAG 输出结构

```json
{
  "retrieval_id": "ret_001",
  "query": "人教版八年级数学一次函数知识点与常见题型",
  "results": [
    {
      "source_id": "kb_textbook_math_rj_8_001",
      "source_type": "textbook",
      "title": "八年级数学下册 - 一次函数",
      "content": "一次函数通常考查函数表达式、图像性质、实际应用等内容。",
      "relevance_score": 0.92,
      "trust_score": 0.95
    }
  ]
}
```

### 3.7 RAG 的质量要求

```text
知识来源要可追溯
教材版本要匹配
年级和章节要匹配
检索结果不能直接等同于事实，仍需评估
低可信来源不能用于生成高风险题目
题库内容需要去重和版权风险检查
```

### 3.8 RAG 与其他模块的关系

```text
与 Memory：Memory 提供用户偏好，RAG 提供领域知识
与 Planning：Planning 根据检索结果制定出题蓝图
与 Tool Manager：RAG 检索器本身可以作为工具注册
与 State：检索请求和结果 ID 写入当前任务状态
与 Guardrails：检查知识来源、版权、隐私和权限
与 Evaluation：评估题目是否符合检索到的课程标准和知识点
```

### 3.9 是否必须有 RAG

对于出题 Agent，RAG 基本是必要的。

没有 RAG 的风险：

```text
容易超纲
容易教材版本不匹配
容易生成看似合理但不符合教学进度的题
难以解释题目对应哪个知识点
难以保证不同地区、不同学校要求
难以沉淀高质量题库
```

MVP 阶段可以先做轻量 RAG：

```text
先维护结构化知识点表
再接入教材章节索引
最后接入题库和评分标准
```

---

## 4. Planning 规划模块

### 4.1 模块定位

Planning 负责把用户的复杂请求拆成可执行步骤。

它不直接执行任务，而是生成结构化计划。

### 4.2 示例

用户输入：

```text
帮我给初二学生出一套一次函数测验，20 分钟完成。
```

Planning 应该拆成：

```text
1. 识别任务类型：出卷
2. 补全关键约束：年级、学科、章节、时长
3. 读取用户偏好：教材版本、题型、难度、解析风格
4. 生成试卷蓝图
5. 生成题目
6. 校验题目
7. 生成答案和解析
8. 输出给用户确认
9. 保存任务状态和必要记忆
```

### 4.3 结构化计划

```json
{
  "plan_id": "plan_001",
  "task_type": "generate_exam",
  "goal": "生成一套初二一次函数 20 分钟测验",
  "status": "pending",
  "steps": [
    {
      "id": "s1",
      "name": "build_exam_blueprint",
      "description": "生成试卷蓝图",
      "status": "pending",
      "required_tools": ["curriculum_mapper"]
    },
    {
      "id": "s2",
      "name": "generate_questions",
      "description": "按照蓝图生成题目",
      "status": "pending",
      "required_tools": ["llm"]
    },
    {
      "id": "s3",
      "name": "validate_questions",
      "description": "校验题目、答案和解析",
      "status": "pending",
      "required_tools": ["question_validator"]
    }
  ]
}
```

### 4.4 Planning 的职责边界

Planning 负责：

```text
拆解任务
安排步骤顺序
识别缺失信息
选择候选工具
判断是否需要用户确认
生成可恢复的执行计划
```

Planning 不负责：

```text
直接调用工具
直接生成最终答案
绕过安全检查
保存长期记忆
判断最终质量是否合格
```

---

## 5. Tool Manager 工具管理模块

### 5.1 模块定位

Tool Manager 负责管理 Agent 可用工具、参数、权限、调用和结果解析。

LLM 可以建议使用某个工具，但最终是否允许调用、如何调用，应该由 Tool Manager 决定。

### 5.2 核心组成

```text
Tool Registry：工具注册表
Tool Schema：工具参数定义
Permission Policy：工具权限策略
Tool Router：工具选择与路由
Tool Executor：工具执行器
Tool Result Parser：工具结果解析
Tool Error Handler：错误处理与降级
Tool Audit Log：调用审计日志
```

### 5.3 出题 Agent 可能使用的工具

```text
课程知识点检索工具
教材版本映射工具
题库检索工具
数学求解工具
公式校验工具
文本查重工具
题目质量评估工具
Word / PDF 导出工具
OCR 工具
MCP 外部资源工具
```

### 5.4 工具注册结构

```json
{
  "tool_name": "question_validator",
  "description": "校验题目、答案、解析是否正确",
  "category": "validation",
  "input_schema": {
    "subject": "string",
    "grade": "string",
    "question": "string",
    "answer": "string",
    "explanation": "string"
  },
  "permission_level": "internal",
  "timeout_ms": 30000,
  "retry": 1
}
```

### 5.5 工具调用结构

```json
{
  "call_id": "tool_call_001",
  "tool_name": "question_validator",
  "task_id": "task_001",
  "step_id": "s3",
  "input": {
    "subject": "math",
    "grade": "8",
    "question": "已知一次函数 y = 2x + 1，求 x = 3 时 y 的值。",
    "answer": "7",
    "explanation": "将 x = 3 代入 y = 2x + 1，得 y = 7。"
  }
}
```

### 5.6 Tool Manager 的关键原则

```text
工具必须注册后才能调用
工具参数必须校验
工具权限必须检查
工具调用必须可追踪
工具失败必须有处理策略
工具输出必须结构化
```

---

## 6. State 状态管理模块

### 6.1 模块定位

State 负责记录当前任务执行到了哪一步。

它是运行时状态，不是长期记忆。

### 6.2 State 应该记录什么

```text
当前任务 ID
当前用户 ID
任务状态
当前执行步骤
计划 ID
每一步输入
每一步输出
中间产物
错误信息
是否需要用户确认
是否暂停
是否完成
```

### 6.3 推荐数据结构

```json
{
  "task_id": "task_20260511_001",
  "user_id": "u_001",
  "status": "running",
  "current_step": "validate_questions",
  "plan_id": "plan_001",
  "variables": {
    "grade": "8",
    "subject": "math",
    "chapter": "一次函数",
    "duration_minutes": 20
  },
  "artifacts": {
    "blueprint_id": "bp_001",
    "draft_exam_id": "exam_draft_001"
  },
  "errors": [],
  "requires_user_input": false,
  "created_at": "2026-05-11T10:00:00+08:00",
  "updated_at": "2026-05-11T10:05:00+08:00"
}
```

### 6.4 任务状态枚举

```text
pending：等待执行
running：执行中
waiting_user：等待用户输入
waiting_tool：等待工具返回
retrying：重试中
failed：失败
completed：完成
cancelled：取消
```

### 6.5 State 的作用

```text
支持任务中断恢复
支持多轮对话继续执行
支持失败重试
支持人工接管
支持执行审计
支持问题排查
```

---

## 7. Guardrails 安全约束模块

### 7.1 模块定位

Guardrails 负责限制 Agent 的行为边界，防止越权、错误调用、危险操作和不合规输出。

Guardrails 不应该只放在最终输出前，而应该贯穿全流程。

### 7.2 检查位置

```text
输入前检查：用户请求是否合规
规划后检查：任务计划是否越权
工具前检查：工具调用是否允许
执行中检查：中间结果是否异常
输出前检查：最终内容是否安全、准确、适龄
记忆前检查：哪些内容可以被保存
```

### 7.3 Guardrails 分类

```text
Policy Guardrails：安全与权限约束
Quality Guardrails：质量与正确性约束
Privacy Guardrails：隐私与数据保存约束
```

### 7.4 出题 Agent 的安全约束

```text
不生成不适龄内容
不引导作弊
不伪造真实考试来源
不泄露老师私有题库
不保存不必要的学生敏感信息
不输出危险实验操作
不调用未授权工具
不把一个用户的数据泄露给另一个用户
```

### 7.5 Guardrails 检查结果结构

```json
{
  "passed": true,
  "risk_level": "low",
  "blocked": false,
  "issues": [],
  "action": "continue"
}
```

如果存在风险：

```json
{
  "passed": false,
  "risk_level": "high",
  "blocked": true,
  "issues": [
    {
      "type": "privacy_risk",
      "message": "请求包含不必要的学生个人敏感信息"
    }
  ],
  "action": "ask_user_to_remove_sensitive_info"
}
```

---

## 8. Evaluation 评估模块

### 8.1 模块定位

Evaluation 负责判断任务是否完成、结果是否合格。

它既可以在任务结束时运行，也可以在每个关键步骤后运行。

### 8.2 通用评估维度

```text
目标是否达成
步骤是否完成
输出是否符合用户约束
工具结果是否可信
是否需要重试
是否需要人工确认
是否应该写入记忆
```

### 8.3 出题 Agent 的评估维度

```text
题量是否正确
题型是否正确
知识点是否覆盖
难度是否符合
答案是否正确
解析是否完整
题目是否有歧义
是否存在重复题
是否超纲
是否符合老师偏好
是否适合目标学生
```

### 8.4 评估结果结构

```json
{
  "evaluation_id": "eval_001",
  "task_id": "task_001",
  "passed": false,
  "score": 0.78,
  "issues": [
    {
      "type": "difficulty_mismatch",
      "message": "第 8 题难度高于设定范围",
      "severity": "medium"
    },
    {
      "type": "weak_explanation",
      "message": "第 3 题解析缺少关键推导步骤",
      "severity": "low"
    }
  ],
  "next_action": "revise_questions"
}
```

### 8.5 评估后的动作

```text
passed = true：进入最终输出
passed = false 且问题可修复：回到对应步骤重新执行
passed = false 且缺少信息：向用户追问
passed = false 且风险较高：交给人工审核或拒绝执行
```

---

## 9. Harness 运行与测试支架

### 9.1 模块定位

Harness 是包在 Agent Runtime 外层的运行、测试、复现和观测支架。

它不直接决定题目怎么出，也不直接参与用户画像、规划、工具调用或安全判断。它的价值是让整个 Agent 系统可以被稳定运行、重复测试、批量评估和回归验证。

### 9.2 Harness 解决的问题

```text
如何稳定启动一次 Agent 任务
如何注入用户输入、Memory、RAG 结果和工具模拟结果
如何复现一次失败的出题过程
如何批量跑测试用例
如何比较不同模型、提示词、工具策略的效果
如何记录每一步的输入、输出、耗时和错误
如何在上线前做质量回归
```

### 9.3 Harness 与 Runtime 的关系

```text
Harness
  ├─ 准备测试输入
  ├─ 初始化 Runtime 环境
  ├─ 注入 Memory / RAG / Tool Mock
  ├─ 驱动 Agent 执行
  ├─ 收集 State / Tool Call / Evaluation 结果
  ├─ 生成运行报告
  └─ 判断本次运行是否通过
```

Runtime 负责完成任务，Harness 负责让任务可运行、可观测、可复现。

### 9.4 Harness 的典型使用场景

```text
本地调试：开发者手动跑一个出题任务
单元测试：测试某个模块是否按预期工作
集成测试：测试 Memory、RAG、Planning、Tool Manager 等模块串联是否正常
回归测试：更新提示词、模型或工具后，检查旧任务是否变差
批量评测：用一批老师需求测试出题质量
故障复现：根据任务日志重新运行一次失败任务
A/B 测试：比较不同规划策略、检索策略或评估策略
压测：检查并发任务下的延迟、失败率和资源消耗
```

### 9.5 Harness 输入结构

```json
{
  "case_id": "case_math_exam_001",
  "user_id": "teacher_001",
  "user_input": "帮我给初二学生出一套一次函数 20 分钟小测。",
  "memory_seed": {
    "profile": "初二数学老师",
    "preferences": ["人教版", "解析详细", "难度中等"]
  },
  "knowledge_seed": {
    "textbook_version": "人教版",
    "grade": "8",
    "chapter": "一次函数"
  },
  "tool_mode": "mock",
  "expected": {
    "task_type": "generate_exam",
    "min_question_count": 8,
    "must_include": ["答案", "解析", "知识点标签"],
    "must_not_include": ["超纲知识点"]
  }
}
```

### 9.6 Harness 输出结构

```json
{
  "case_id": "case_math_exam_001",
  "run_id": "run_20260511_001",
  "passed": true,
  "duration_ms": 18500,
  "steps": [
    {
      "step_id": "s1",
      "name": "build_exam_blueprint",
      "status": "completed",
      "duration_ms": 3200
    }
  ],
  "tool_calls": [
    {
      "tool_name": "curriculum_mapper",
      "status": "completed",
      "duration_ms": 900
    }
  ],
  "evaluation": {
    "score": 0.91,
    "passed": true,
    "issues": []
  }
}
```

### 9.7 Harness 与其他模块的关系

```text
与 Memory：可以注入测试记忆，也可以检查任务结束后写入了哪些记忆
与 RAG：可以使用真实检索，也可以注入固定知识片段做可复现测试
与 Planning：检查计划是否符合预期任务类型和步骤顺序
与 Tool Manager：可以切换真实工具、模拟工具和失败工具
与 State：读取完整任务状态，支持失败复现和中断恢复测试
与 Guardrails：验证违规输入是否被拦截
与 Evaluation：收集评估结果，并判断测试用例是否通过
```

### 9.8 出题 Agent 中的 Harness 指标

```text
任务成功率
平均生成耗时
工具调用失败率
题目正确率
超纲率
解析完整率
难度匹配率
重复题比例
用户偏好命中率
Guardrails 拦截准确率
```

### 9.9 MVP 阶段的 Harness

第一版 Harness 不需要复杂平台，先做命令行或脚本化测试即可。

MVP 能力：

```text
读取测试用例
初始化 Memory 和 Knowledge Seed
运行一次完整 Agent 任务
记录每一步 State
记录工具调用
执行基础 Evaluation
输出 JSON 测试报告
支持失败用例复跑
```

---

## 10. 完整执行工作流

```text
1. Harness 接收真实请求或测试用例
2. 初始化运行环境、用户上下文和观测日志
3. Runtime 接收用户请求
4. 识别用户身份和任务类型
5. 从 Memory 读取相关上下文
6. 通过 RAG / Knowledge Retrieval 检索领域知识
7. 构建当前 Context
8. Planning 生成结构化任务计划
9. Guardrails 检查计划是否合规
10. State 初始化任务状态
11. Tool Manager 按步骤执行工具调用
12. 每一步执行结果写入 State
13. Evaluation 检查阶段结果
14. 如果不合格，回到 Planning 或对应执行步骤
15. 如果合格，生成最终回复
16. Guardrails 检查最终输出
17. 写入必要 Memory
18. 更新 State 为 completed
19. Harness 收集运行日志、状态、工具调用和评估结果
20. 任务结束
```

---

## 11. MVP 版本建议

第一版不建议把所有模块都做成复杂系统。

推荐 MVP 范围：

```text
Memory：用户偏好 + 历史任务摘要
RAG / Knowledge Retrieval：结构化知识点表 + 教材章节索引
Planning：模板式计划，不做完全自主规划
Tool Manager：工具注册 + 参数校验 + 调用日志
State：任务状态表 + Step 状态
Guardrails：权限、隐私、内容安全、输出前检查
Evaluation：规则校验 + LLM 自评 + 必要工具复核
Harness：测试用例驱动运行 + 日志记录 + 失败复跑
```

MVP 底层组件：

```text
Memory Store
Knowledge Store / Retriever
Plan Engine
Tool Registry
Task State Store
Guardrail Checker
Evaluator
Runtime Harness
```

---

## 12. 后续业务层扩展

在底层 Runtime 和知识检索层稳定后，出题 Agent 可以继续扩展业务层：

```text
课程知识图谱
出题蓝图生成器
题目生成器
题目校验器
试卷排版器
Word / PDF 导出器
学情反馈器
错题分析器
个性化练习推荐器
```

建议优先级：

```text
第一阶段：老师出题助手
第二阶段：题目质量校验与导出
第三阶段：学生练习与错题记录
第四阶段：老师端学情分析
第五阶段：个性化学习路径
```

---

## 13. 核心设计结论

这个出题 Agent 的底层不是一个单次问答系统，而是一个可恢复、可评估、可约束、可持续学习的任务执行系统。

最关键的边界是：

```text
Memory 负责长期上下文
RAG / Knowledge Retrieval 负责领域知识检索
Planning 负责任务拆解
Tool Manager 负责工具调用治理
State 负责当前任务进度
Guardrails 负责安全和权限边界
Evaluation 负责结果质量判断
Harness 负责运行、测试、复现、回归和观测
```

后续所有出题业务能力都应该围绕 Runtime、知识检索层和 Harness 展开，而不是直接让 LLM 自由生成题目。
