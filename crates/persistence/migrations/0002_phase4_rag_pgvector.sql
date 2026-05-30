CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS rag_knowledge_sources (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    knowledge_layer TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    chunk_count INTEGER NOT NULL,
    created_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS rag_knowledge_chunks (
    id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL REFERENCES rag_knowledge_sources(id) ON DELETE CASCADE,
    ordinal INTEGER NOT NULL,
    text TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL,
    UNIQUE (source_id, ordinal),
    UNIQUE (source_id, content_hash)
);

CREATE TABLE IF NOT EXISTS rag_embedding_jobs (
    id TEXT PRIMARY KEY,
    provider_id TEXT NOT NULL,
    embedding_model TEXT NOT NULL,
    status TEXT NOT NULL,
    total_texts INTEGER NOT NULL,
    embedded_texts INTEGER NOT NULL DEFAULT 0,
    skipped_texts INTEGER NOT NULL DEFAULT 0,
    failed_texts INTEGER NOT NULL DEFAULT 0,
    failure_summary TEXT,
    created_at TIMESTAMPTZ NOT NULL,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS rag_embedding_job_sources (
    id BIGSERIAL PRIMARY KEY,
    job_id TEXT NOT NULL REFERENCES rag_embedding_jobs(id) ON DELETE CASCADE,
    source_type TEXT NOT NULL,
    source_id TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    text TEXT NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    UNIQUE (job_id, source_type, source_id, content_hash)
);

CREATE TABLE IF NOT EXISTS rag_embedding_vectors (
    id TEXT PRIMARY KEY,
    source_type TEXT NOT NULL,
    source_id TEXT NOT NULL,
    chunk_id TEXT NOT NULL,
    embedding_model TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    embedding vector(1536) NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (source_type, source_id, chunk_id, embedding_model, content_hash)
);

CREATE INDEX IF NOT EXISTS rag_embedding_vectors_embedding_idx
    ON rag_embedding_vectors USING ivfflat (embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS rag_embedding_vectors_metadata_idx
    ON rag_embedding_vectors USING gin (metadata);

CREATE TABLE IF NOT EXISTS rag_retrieval_results (
    id BIGSERIAL PRIMARY KEY,
    query TEXT NOT NULL,
    source_type TEXT NOT NULL,
    source_id TEXT NOT NULL,
    chunk_id TEXT NOT NULL,
    knowledge_layer TEXT NOT NULL,
    similarity_score DOUBLE PRECISION NOT NULL,
    trust_score DOUBLE PRECISION NOT NULL,
    final_score DOUBLE PRECISION NOT NULL,
    trust_tier TEXT NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
