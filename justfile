set shell := ["powershell.exe", "-NoLogo", "-NoProfile", "-Command"]

default:
    just --list

check: rust-check python-check frontend-check phase0-test

rust-check:
    $env:CARGO_HOME='E:\DevData\cargo'; cargo fmt --all --check
    $env:CARGO_HOME='E:\DevData\cargo'; cargo test --workspace
    $env:CARGO_HOME='E:\DevData\cargo'; cargo clippy --workspace --all-targets -- -D warnings

python-check:
    $env:UV_CACHE_DIR='E:\DevData\uv\cache'; uv run ruff check .
    $env:UV_CACHE_DIR='E:\DevData\uv\cache'; uv run pytest

frontend-check:
    cd frontend; npm run lint
    cd frontend; npm test
    cd frontend; npm run build

phase0-test:
    python -m unittest tests.test_phase0_structure

dev-api:
    cargo run -p my-sifu-api

dev-web:
    cd frontend; npm run dev -- --hostname 127.0.0.1 --port 3001

postgres-check:
    $env:CARGO_HOME='E:\DevData\cargo'; cargo test -p persistence --test postgres_persistence_contract

docker-config:
    docker compose --env-file .env.docker.example config

docker-up:
    docker compose --env-file .env.docker.example up -d

docker-down:
    docker compose --env-file .env.docker.example down

docker-logs:
    docker compose --env-file .env.docker.example logs -f --tail=120

docker-ps:
    docker compose --env-file .env.docker.example ps

docker-clean:
    docker compose --env-file .env.docker.example down --volumes --remove-orphans

postgres-check-docker:
    $env:MY_SIFU_DATABASE_URL='postgres://my_sifu:my_sifu@127.0.0.1:5432/my_sifu'; $env:CARGO_HOME='E:\DevData\cargo'; cargo test -p persistence --test postgres_persistence_contract

new-api-status:
    Invoke-WebRequest -UseBasicParsing http://127.0.0.1:3000 | Select-Object -ExpandProperty StatusCode
