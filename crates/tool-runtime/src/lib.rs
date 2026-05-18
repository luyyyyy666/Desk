use domain::SkillId;

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ToolRegistryInfo {
    pub status: &'static str,
    pub registered_skill_ids: Vec<SkillId>,
}

impl ToolRegistryInfo {
    pub fn phase0() -> Self {
        Self {
            status: "not_registered_yet",
            registered_skill_ids: Vec::new(),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn phase0_tool_registry_has_no_registered_skills() {
        let registry = ToolRegistryInfo::phase0();

        assert!(registry.registered_skill_ids.is_empty());
    }
}
