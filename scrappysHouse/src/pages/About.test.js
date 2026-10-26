import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const aboutSource = readFileSync(new URL("./About.jsx", import.meta.url), "utf8");

test("About page does not include the temporary Hermes testing message", () => {
  assert.doesNotMatch(
    aboutSource,
    />\s*testing: Hermes was here!\s*</,
    "Expected the temporary Hermes testing message to be removed",
  );
});
