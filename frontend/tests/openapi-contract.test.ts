import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import yaml from "js-yaml";
import { describe, expect, it } from "vitest";

describe("OpenAPI contract", () => {
  it("parses as valid YAML", () => {
    const contractPath = resolve(__dirname, "../../contracts/openapi/learning-os.yaml");
    const contract = yaml.load(readFileSync(contractPath, "utf8"));

    expect(contract).toBeTruthy();
  });

  it("declares phase 7 agent run state polling and resume contracts", () => {
    const contractPath = resolve(__dirname, "../../contracts/openapi/learning-os.yaml");
    const contract = yaml.load(readFileSync(contractPath, "utf8")) as {
      paths: Record<string, unknown>;
      components: { schemas: Record<string, unknown> };
    };

    expect(contract.paths["/api/agent-runs/{agent_run_id}/state"]).toBeTruthy();
    expect(contract.paths["/api/agent-runs/{agent_run_id}/state/transitions"]).toBeTruthy();
    expect(contract.paths["/api/agent-runs/{agent_run_id}/resume"]).toBeTruthy();
    expect(contract.components.schemas.AgentRunStateSnapshot).toBeTruthy();
    expect(contract.components.schemas.StateTransition).toBeTruthy();
    expect(contract.components.schemas.ResumeActionResponse).toBeTruthy();
  });
});
