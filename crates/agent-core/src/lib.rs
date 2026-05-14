use domain::AgentRunStatus;

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct RuntimeInfo {
    pub name: &'static str,
    pub initial_status: AgentRunStatus,
}

impl RuntimeInfo {
    pub fn phase0() -> Self {
        Self {
            name: "phase0-runtime-foundation",
            initial_status: AgentRunStatus::Pending,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn phase0_runtime_starts_pending() {
        let runtime = RuntimeInfo::phase0();

        assert_eq!(runtime.initial_status, AgentRunStatus::Pending);
    }
}
