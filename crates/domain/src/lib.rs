use serde::{Deserialize, Serialize};
use uuid::Uuid;

pub type AgentRunId = Uuid;
pub type QuestionSetId = Uuid;
pub type SkillId = String;

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct HealthResponse {
    pub service: &'static str,
    pub status: &'static str,
    pub runtime: &'static str,
    pub tool_registry: &'static str,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub enum AgentRunStatus {
    Pending,
    Running,
    WaitingUser,
    WaitingTool,
    Retrying,
    Failed,
    Completed,
    Cancelled,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct User {
    pub id: String,
    pub display_name: String,
    pub created_at: String,
}

impl User {
    pub fn fixture() -> Self {
        Self {
            id: "user_fixture_001".to_string(),
            display_name: "默认学习者".to_string(),
            created_at: "2026-05-14T16:00:00+08:00".to_string(),
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct LearningProfile {
    pub id: String,
    pub user_id: String,
    pub subject: String,
    pub stage: LearningStage,
    pub textbook: String,
    pub preference_summary: String,
}

impl LearningProfile {
    pub fn fixture_for_user(user_id: String) -> Self {
        Self {
            id: "profile_fixture_001".to_string(),
            user_id,
            subject: "数学".to_string(),
            stage: LearningStage::Grade8,
            textbook: "人教版 · 八年级下册".to_string(),
            preference_summary: "解析详细，难度中等".to_string(),
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub enum LearningStage {
    Grade7,
    Grade8,
    Grade9,
    HighSchool,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Task {
    pub id: String,
    pub user_id: String,
    pub title: String,
    pub learning_goal: String,
    pub subject: String,
    pub source: String,
    pub question_count: u16,
    pub status: TaskStatus,
    pub created_at: String,
    pub updated_at: String,
}

impl Task {
    pub fn new_fixture() -> Self {
        Self {
            id: "task_fixture_linear_function_001".to_string(),
            user_id: "user_fixture_001".to_string(),
            title: "一次函数专项训练".to_string(),
            learning_goal: "巩固一次函数图像、解析式与实际应用题".to_string(),
            subject: "八年级数学".to_string(),
            source: "人教版 · 第十九章".to_string(),
            question_count: 12,
            status: TaskStatus::Active,
            created_at: "2026-05-14T16:00:00+08:00".to_string(),
            updated_at: "2026-05-14T16:00:00+08:00".to_string(),
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum TaskStatus {
    Draft,
    Active,
    Completed,
    Archived,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct AnswerAttempt {
    pub id: String,
    pub question_id: String,
    pub user_answer: String,
    pub is_correct: bool,
    pub submitted_at: String,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Mistake {
    pub id: String,
    pub question_id: String,
    pub knowledge: String,
    pub reason: String,
    pub created_at: String,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct KnowledgeSource {
    pub id: String,
    pub source_type: String,
    pub title: String,
    pub version: String,
    pub trust_score: f64,
}

impl KnowledgeSource {
    pub fn fixture() -> Self {
        Self {
            id: "kb_textbook_math_rj_8_001".to_string(),
            source_type: "textbook".to_string(),
            title: "八年级数学下册 - 一次函数".to_string(),
            version: "人教版".to_string(),
            trust_score: 0.95,
        }
    }
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct RetrievalResult {
    pub id: String,
    pub source_id: String,
    pub query: String,
    pub snippet: String,
    pub relevance_score: f64,
    pub trust_score: f64,
}

impl RetrievalResult {
    pub fn fixture(source_id: String) -> Self {
        Self {
            id: "retrieval_fixture_001".to_string(),
            source_id,
            query: "一次函数".to_string(),
            snippet: "一次函数通常考查函数表达式、图像性质、实际应用等内容。".to_string(),
            relevance_score: 0.92,
            trust_score: 0.95,
        }
    }
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct EvaluationResult {
    pub id: String,
    pub agent_run_id: String,
    pub score: f64,
    pub passed: bool,
    pub summary: String,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct MemoryItem {
    pub id: String,
    pub user_id: String,
    pub memory_type: String,
    pub content: String,
    pub source: String,
    pub confidence_basis: String,
}

impl MemoryItem {
    pub fn fixture_for_user(user_id: String) -> Self {
        Self {
            id: "memory_fixture_001".to_string(),
            user_id,
            memory_type: "preference".to_string(),
            content: "用户偏好中等难度，解析需要详细。".to_string(),
            source: "fixture".to_string(),
            confidence_basis: "explicit".to_string(),
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct AgentRun {
    pub id: String,
    pub task_id: String,
    pub status: AgentRunStatus,
    pub current_step: String,
    pub created_at: String,
    pub updated_at: String,
}

impl AgentRun {
    pub fn new_fixture() -> Self {
        Self {
            id: "run_fixture_linear_function_001".to_string(),
            task_id: "task_fixture_linear_function_001".to_string(),
            status: AgentRunStatus::Completed,
            current_step: "completed".to_string(),
            created_at: "2026-05-14T16:00:00+08:00".to_string(),
            updated_at: "2026-05-14T16:00:08+08:00".to_string(),
        }
    }

    pub fn new_pending(id: String, task_id: String) -> Self {
        Self {
            id,
            task_id,
            status: AgentRunStatus::Pending,
            current_step: "created".to_string(),
            created_at: "2026-05-14T16:00:00+08:00".to_string(),
            updated_at: "2026-05-14T16:00:00+08:00".to_string(),
        }
    }
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct AgentRunEvent {
    pub id: String,
    pub agent_run_id: String,
    pub sequence: u64,
    pub kind: AgentRunEventKind,
    pub payload: serde_json::Value,
    pub created_at: String,
}

impl AgentRunEvent {
    pub fn new(
        agent_run_id: String,
        sequence: u64,
        kind: AgentRunEventKind,
        payload: serde_json::Value,
    ) -> Self {
        Self {
            id: format!("event_{agent_run_id}_{sequence}"),
            agent_run_id,
            sequence,
            kind,
            payload,
            created_at: "2026-05-14T16:00:00+08:00".to_string(),
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum AgentRunEventKind {
    PlanCreated,
    GenerationJobCreated,
    RetrievalContextReady,
    QuestionSetReady,
    ToolCallStarted,
    ToolCallCompleted,
    EvaluationCompleted,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ToolCall {
    pub id: String,
    pub agent_run_id: String,
    pub tool_name: String,
    pub status: String,
    pub input: serde_json::Value,
    pub output: Option<serde_json::Value>,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct ApiErrorEnvelope {
    pub error: ApiErrorBody,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct ApiErrorBody {
    pub code: &'static str,
    pub message: &'static str,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct CurrentTaskResponse {
    pub task: CurrentTask,
    pub learning_loop: Vec<LearningLoopStep>,
    pub desktop_shortcuts: Vec<DesktopShortcut>,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct CurrentTask {
    pub title: &'static str,
    pub status: &'static str,
    pub subject: &'static str,
    pub source: &'static str,
    pub goal: &'static str,
    pub question_count: u16,
    pub duration: &'static str,
    pub mastery: u8,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct LearningLoopStep {
    pub id: &'static str,
    pub label: &'static str,
    pub window_id: &'static str,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct DesktopShortcut {
    pub id: &'static str,
    pub label: &'static str,
    pub detail: &'static str,
    pub window_id: &'static str,
    pub side: &'static str,
    pub x: u16,
    pub y: u16,
    pub file_color: &'static str,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct CreateGenerationJobRequest {
    pub learning_goal: String,
    pub subject: String,
    pub question_count: u16,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct GenerationJobResponse {
    pub job: GenerationJob,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct GenerationJob {
    pub id: &'static str,
    pub status: &'static str,
    pub question_set_id: &'static str,
    pub progress: u8,
    pub message: &'static str,
    pub created_at: &'static str,
    pub updated_at: &'static str,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct QuestionSetResponse {
    pub question_set_id: &'static str,
    pub title: &'static str,
    pub source: &'static str,
    pub questions: Vec<Question>,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct Question {
    pub id: &'static str,
    #[serde(rename = "type")]
    pub question_type: &'static str,
    pub title: &'static str,
    pub stem: &'static str,
    pub options: Vec<&'static str>,
    pub answer: &'static str,
    pub explanation: &'static str,
    pub knowledge: Vec<&'static str>,
    pub difficulty: &'static str,
    pub status: &'static str,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct MistakesResponse {
    pub groups: Vec<MistakeGroup>,
    pub recent_wrong_question: Option<Question>,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct MistakeGroup {
    pub knowledge: &'static str,
    pub count: u16,
    pub reason: &'static str,
    pub recommendation: &'static str,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct KnowledgeSearchResponse {
    pub query: String,
    pub results: Vec<KnowledgePoint>,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct KnowledgePoint {
    pub name: &'static str,
    pub coverage: u8,
    pub source: &'static str,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct ReportResponse {
    pub metrics: Vec<ReportMetric>,
    pub recommendation: &'static str,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct ReportMetric {
    pub label: &'static str,
    pub value: &'static str,
    pub detail: &'static str,
}

pub mod fixtures {
    use super::{
        CurrentTask, CurrentTaskResponse, DesktopShortcut, GenerationJob, GenerationJobResponse,
        KnowledgePoint, KnowledgeSearchResponse, LearningLoopStep, MistakeGroup, MistakesResponse,
        Question, QuestionSetResponse, ReportMetric, ReportResponse,
    };

    pub const FIXTURE_JOB_ID: &str = "job_fixture_linear_function_001";
    pub const FIXTURE_QUESTION_SET_ID: &str = "qs_fixture_linear_function_001";

    pub fn current_task() -> CurrentTaskResponse {
        CurrentTaskResponse {
            task: CurrentTask {
                title: "一次函数专项训练",
                status: "已生成 12 题 / 待练习 / 2 个知识点需强化",
                subject: "八年级数学",
                source: "人教版 · 第十九章",
                goal: "巩固一次函数图像、解析式与实际应用题",
                question_count: 12,
                duration: "25 分钟",
                mastery: 68,
            },
            learning_loop: learning_loop(),
            desktop_shortcuts: desktop_shortcuts(),
        }
    }

    pub fn generation_job() -> GenerationJobResponse {
        GenerationJobResponse {
            job: GenerationJob {
                id: FIXTURE_JOB_ID,
                status: "completed",
                question_set_id: FIXTURE_QUESTION_SET_ID,
                progress: 100,
                message: "fixture question set is ready",
                created_at: "2026-05-14T15:00:00+08:00",
                updated_at: "2026-05-14T15:00:08+08:00",
            },
        }
    }

    pub fn question_set() -> QuestionSetResponse {
        QuestionSetResponse {
            question_set_id: FIXTURE_QUESTION_SET_ID,
            title: "一次函数专项训练",
            source: "人教版 · 第十九章",
            questions: questions(),
        }
    }

    pub fn mistakes() -> MistakesResponse {
        MistakesResponse {
            groups: vec![
                MistakeGroup {
                    knowledge: "实际问题建模",
                    count: 3,
                    reason: "容易漏掉固定费用或把斜率、截距写反。",
                    recommendation: "下一轮增加 4 道分段语境应用题。",
                },
                MistakeGroup {
                    knowledge: "函数图像与交点",
                    count: 2,
                    reason: "代入 x 轴或 y 轴条件时，坐标含义不稳定。",
                    recommendation: "先做坐标轴交点专项，再做综合题。",
                },
            ],
            recent_wrong_question: questions()
                .into_iter()
                .find(|question| question.status == "错题"),
        }
    }

    pub fn knowledge_search(query: String) -> KnowledgeSearchResponse {
        KnowledgeSearchResponse {
            query,
            results: vec![
                KnowledgePoint {
                    name: "一次函数解析式",
                    coverage: 92,
                    source: "19.2.1 正比例函数与一次函数",
                },
                KnowledgePoint {
                    name: "函数图像与交点",
                    coverage: 76,
                    source: "19.2.2 一次函数的图像",
                },
                KnowledgePoint {
                    name: "实际问题建模",
                    coverage: 54,
                    source: "19.3 课题学习",
                },
                KnowledgePoint {
                    name: "增减性",
                    coverage: 81,
                    source: "19.2.2 一次函数的图像",
                },
            ],
        }
    }

    pub fn report() -> ReportResponse {
        ReportResponse {
            metrics: vec![
                ReportMetric {
                    label: "掌握度",
                    value: "68%",
                    detail: "较上次 +9%",
                },
                ReportMetric {
                    label: "正确率",
                    value: "75%",
                    detail: "12 题中 9 题正确",
                },
                ReportMetric {
                    label: "薄弱点",
                    value: "2",
                    detail: "建模、交点",
                },
                ReportMetric {
                    label: "建议题量",
                    value: "8",
                    detail: "下一轮小测",
                },
            ],
            recommendation: "围绕“实际问题建模”生成 8 题，保留 2 道图像交点复习题。",
        }
    }

    fn learning_loop() -> Vec<LearningLoopStep> {
        vec![
            LearningLoopStep {
                id: "goal",
                label: "目标",
                window_id: "generator",
            },
            LearningLoopStep {
                id: "generate",
                label: "生成",
                window_id: "generator",
            },
            LearningLoopStep {
                id: "edit",
                label: "编辑",
                window_id: "editor",
            },
            LearningLoopStep {
                id: "practice",
                label: "练习",
                window_id: "practice",
            },
            LearningLoopStep {
                id: "review",
                label: "解析",
                window_id: "review",
            },
            LearningLoopStep {
                id: "errors",
                label: "错题",
                window_id: "errors",
            },
            LearningLoopStep {
                id: "regenerate",
                label: "再生成",
                window_id: "generator",
            },
        ]
    }

    fn desktop_shortcuts() -> Vec<DesktopShortcut> {
        vec![
            DesktopShortcut {
                id: "new-set",
                label: "新建题单",
                detail: "按目标生成",
                window_id: "generator",
                side: "left",
                x: 42,
                y: 72,
                file_color: "orange",
            },
            DesktopShortcut {
                id: "practice",
                label: "专项练习",
                detail: "直接作答",
                window_id: "practice",
                side: "left",
                x: 54,
                y: 176,
                file_color: "green",
            },
            DesktopShortcut {
                id: "errors",
                label: "错题本",
                detail: "弱点沉淀",
                window_id: "errors",
                side: "left",
                x: 46,
                y: 282,
                file_color: "pink",
            },
            DesktopShortcut {
                id: "knowledge",
                label: "知识库",
                detail: "教材来源",
                window_id: "knowledge",
                side: "left",
                x: 76,
                y: 410,
                file_color: "blue",
            },
            DesktopShortcut {
                id: "report",
                label: "学习报告",
                detail: "掌握度",
                window_id: "report",
                side: "right",
                x: 1260,
                y: 88,
                file_color: "green",
            },
            DesktopShortcut {
                id: "export",
                label: "导出试卷",
                detail: "A4 / 解析",
                window_id: "export",
                side: "right",
                x: 1248,
                y: 206,
                file_color: "paper",
            },
            DesktopShortcut {
                id: "suggestions",
                label: "师傅建议",
                detail: "下一步",
                window_id: "suggestions",
                side: "right",
                x: 1220,
                y: 340,
                file_color: "orange",
            },
            DesktopShortcut {
                id: "trash",
                label: "回收站",
                detail: "草稿",
                window_id: "export",
                side: "right",
                x: 1286,
                y: 474,
                file_color: "paper",
            },
        ]
    }

    fn questions() -> Vec<Question> {
        vec![
            Question {
                id: "q1",
                question_type: "选择题",
                title: "图像与斜率",
                stem: "若一次函数 y = 2x - 3 的图像经过点 A(a, 5)，则 a 的值是？",
                options: vec!["2", "3", "4", "5"],
                answer: "4",
                explanation: "将 y = 5 代入 y = 2x - 3，得到 5 = 2a - 3，所以 a = 4。",
                knowledge: vec!["一次函数解析式", "代入求值"],
                difficulty: "基础",
                status: "正确",
            },
            Question {
                id: "q2",
                question_type: "填空题",
                title: "函数图像交点",
                stem: "直线 y = -x + 6 与 x 轴的交点坐标是 ______。",
                options: Vec::new(),
                answer: "(6, 0)",
                explanation: "与 x 轴相交时 y = 0，代入得 0 = -x + 6，因此 x = 6。",
                knowledge: vec!["坐标轴交点", "一次函数图像"],
                difficulty: "中等",
                status: "待练习",
            },
            Question {
                id: "q3",
                question_type: "解答题",
                title: "实际应用建模",
                stem: "某打印店基础服务费 5 元，每打印一页加收 0.4 元。写出费用 y 与页数 x 的函数关系式，并求打印 30 页的费用。",
                options: Vec::new(),
                answer: "y = 0.4x + 5，打印 30 页需 17 元。",
                explanation: "固定费用是截距 5，每页费用是斜率 0.4，因此 y = 0.4x + 5。x = 30 时，y = 12 + 5 = 17。",
                knowledge: vec!["一次函数应用", "函数建模"],
                difficulty: "中等",
                status: "错题",
            },
            Question {
                id: "q4",
                question_type: "选择题",
                title: "增减性判断",
                stem: "下列函数中，y 随 x 的增大而减小的是？",
                options: vec!["y = 3x + 1", "y = -2x + 4", "y = x - 5", "y = 0.5x"],
                answer: "y = -2x + 4",
                explanation: "一次函数 y = kx + b 中，当 k < 0 时，y 随 x 增大而减小。",
                knowledge: vec!["一次函数增减性"],
                difficulty: "基础",
                status: "待练习",
            },
        ]
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn status_serializes_to_pascal_case_by_default() {
        let value = serde_json::to_value(AgentRunStatus::WaitingTool).unwrap();

        assert_eq!(value, "WaitingTool");
    }
}
