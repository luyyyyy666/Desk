#[derive(Debug, Clone, PartialEq, Eq)]
pub struct PersistenceInfo {
    pub database_backend: &'static str,
}

impl PersistenceInfo {
    pub fn phase0() -> Self {
        Self {
            database_backend: "not_configured_yet",
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn phase0_persistence_is_not_configured_yet() {
        let info = PersistenceInfo::phase0();

        assert_eq!(info.database_backend, "not_configured_yet");
    }
}
