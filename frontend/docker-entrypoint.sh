#!/bin/sh
set -eu

node <<'NODE'
const fs = require("node:fs");

const apiUrl = process.env.VITE_SCRAPPYS_SCRAPYARD_URL || "";
const config = `window.__SCRAPPY_CONFIG__ = ${JSON.stringify({ apiUrl })};\n`;
fs.writeFileSync("/app/dist/env-config.js", config);
NODE

exec "$@"
