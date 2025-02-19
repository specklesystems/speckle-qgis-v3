#!/usr/bin/env bash
set -euo pipefail

dotnet run --project ci-build/build.csproj -- "$@"
