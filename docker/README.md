# Local Docker Runtime

Phase 2.5 uses Docker Compose for local dependencies only. Keep application code running on the
host during this phase.

Services:

- `postgres`: PostgreSQL for durable AgentRun and future product data.
- `new-api`: local OpenAI-compatible model gateway. Configure upstream provider keys in the New API
  admin UI or local environment; never commit real keys.
- `redis`: placeholder for future queue, cache, rate-limit, and job lifecycle work. New API uses
  its default local SQLite mode in this phase, so Redis is not wired into New API yet.
- `minio`: placeholder object storage for future uploads, exports, and evaluation artifacts.

Optional local env file:

```powershell
Copy-Item .env.docker.example .env.docker
```

The `just docker-*` commands use `.env.docker.example`. Edit the example only for shared safe
defaults. Put machine-local secrets or upstream model keys in an untracked `.env.docker` file and
pass it to Docker Compose manually when needed.
