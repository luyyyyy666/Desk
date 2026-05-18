from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_phase25_compose_declares_required_local_services() -> None:
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")

    for service in ["postgres:", "new-api:", "redis:", "minio:"]:
        assert service in compose

    for image in [
        "postgres:17-alpine",
        "calciumion/new-api:latest",
        "redis:7-alpine",
        "minio/minio:latest",
    ]:
        assert image in compose

    for port in ['"5432:5432"', '"3000:3000"', '"6379:6379"', '"9000:9000"', '"9001:9001"']:
        assert port in compose

    for volume in [
        "my_sifu_postgres_data:",
        "my_sifu_new_api_data:",
        "my_sifu_redis_data:",
        "my_sifu_minio_data:",
    ]:
        assert volume in compose

    assert "pg_isready" in compose
    assert "redis-cli" in compose
    assert "mc" in compose
    assert "REDIS_CONN_STRING" not in compose
    assert "SQL_DSN" not in compose


def test_phase25_docker_environment_example_has_safe_local_defaults() -> None:
    env = (ROOT / ".env.docker.example").read_text(encoding="utf-8")

    required_lines = [
        "MY_SIFU_DATABASE_URL=postgres://my_sifu:my_sifu@127.0.0.1:5432/my_sifu",
        "MY_SIFU_LLM_GATEWAY_PROVIDER=new-api",
        "MY_SIFU_LLM_GATEWAY_BASE_URL=http://127.0.0.1:3000",
        "MY_SIFU_LLM_GATEWAY_API_KEY=",
        "MY_SIFU_DEFAULT_MODEL=gpt-4o-mini",
        "MY_SIFU_REDIS_URL=redis://127.0.0.1:6379/0",
        "MY_SIFU_OBJECT_STORE_ENDPOINT=http://127.0.0.1:9000",
        "POSTGRES_DB=my_sifu",
        "POSTGRES_USER=my_sifu",
        "POSTGRES_PASSWORD=my_sifu",
    ]

    for line in required_lines:
        assert line in env

    forbidden_fragments = ["sk-", "OPENAI_API_KEY=", "ANTHROPIC_API_KEY=", "DASHSCOPE_API_KEY="]
    for fragment in forbidden_fragments:
        assert fragment not in env

    assert "NEW_API_SQL_DSN" not in env


def test_phase25_justfile_exposes_docker_commands() -> None:
    justfile = (ROOT / "justfile").read_text(encoding="utf-8")

    for recipe in [
        "docker-config:",
        "docker-up:",
        "docker-down:",
        "docker-logs:",
        "docker-ps:",
        "docker-clean:",
        "postgres-check-docker:",
        "new-api-status:",
    ]:
        assert recipe in justfile

    assert "docker compose --env-file .env.docker.example config" in justfile
    assert "MY_SIFU_DATABASE_URL='postgres://my_sifu:my_sifu@127.0.0.1:5432/my_sifu'" in justfile
