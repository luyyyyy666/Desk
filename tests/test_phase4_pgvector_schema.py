from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_phase4_pgvector_migration_declares_rag_tables_and_extension() -> None:
    migration = (
        ROOT
        / "crates"
        / "persistence"
        / "migrations"
        / "0002_phase4_rag_pgvector.sql"
    ).read_text(encoding="utf-8")

    for statement in [
        "CREATE EXTENSION IF NOT EXISTS vector",
        "CREATE TABLE IF NOT EXISTS rag_knowledge_sources",
        "CREATE TABLE IF NOT EXISTS rag_knowledge_chunks",
        "CREATE TABLE IF NOT EXISTS rag_embedding_jobs",
        "CREATE TABLE IF NOT EXISTS rag_embedding_job_sources",
        "CREATE TABLE IF NOT EXISTS rag_embedding_vectors",
        "CREATE TABLE IF NOT EXISTS rag_retrieval_results",
    ]:
        assert statement in migration


def test_phase4_pgvector_migration_preserves_deduplication_and_source_traceability() -> None:
    migration = (
        ROOT
        / "crates"
        / "persistence"
        / "migrations"
        / "0002_phase4_rag_pgvector.sql"
    ).read_text(encoding="utf-8")

    assert "embedding vector(1536)" in migration
    assert "UNIQUE (source_type, source_id, chunk_id, embedding_model, content_hash)" in migration
    assert "content_hash TEXT NOT NULL" in migration
    assert "source_id TEXT NOT NULL" in migration
    assert "trust_score DOUBLE PRECISION NOT NULL" in migration
    assert "final_score DOUBLE PRECISION NOT NULL" in migration
