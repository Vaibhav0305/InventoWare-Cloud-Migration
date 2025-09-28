#!/bin/bash
set -e
APP_URL=$1
echo "Running smoke test on: $APP_URL"
if curl -s --fail --max-time 10 "$APP_URL/login" | grep -q "Login"; then
  echo "✅ Smoke test passed."
  exit 0
else
  echo "❌ Smoke test failed!"
  exit 1
fi

