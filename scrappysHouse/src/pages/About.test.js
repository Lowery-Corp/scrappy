import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const aboutSource = readFileSync(new URL("./About.jsx", import.meta.url), "utf8");

test("About page ends with the Hermes testing message", () => {
  assert.match(
    aboutSource,
    />\s*testing: Hermes was here!\s*</,
    "Expected the About page to include the exact Hermes testing message",
  );
});
