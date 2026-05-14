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
