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
});
