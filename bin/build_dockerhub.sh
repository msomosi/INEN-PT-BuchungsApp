#!/usr/bin/env bash

SCRIPTPATH="$(dirname "$(realpath "$0")")"
declare -a modules=("anbietermgmt" "booked-management" "buchungsmanagement" "frontend" "kundenmanagement" "login" "zimmerverwaltung")
platform="linux/amd64,linux/arm64"
registry="mseyer91/"

if [[ -n "$DOCKERHUB_PASSWORD" ]]; then
  echo "$DOCKERHUB_PASSWORD" | docker login --username mseyer91 --password-stdin || { echo "❌ Docker Login fehlgeschlagen!"; exit 1; }
else
  echo "⚠️  Kein Docker Passwort gefunden. Überspringe Login..."
fi
# Git Branch ermitteln (Falls fehlerhaft -> Default 'latest')
git_branch_name="$(git symbolic-ref --short HEAD 2>/dev/null || echo 'latest')"

# Build & Push Loop
for module in "${modules[@]}"; do
  imagename="apeni-${module}:${git_branch_name}"
  DOCKERFILE_PATH="${SCRIPTPATH}/../app/build/Dockerfile"
  BUILD_CONTEXT="${SCRIPTPATH}/../app"
  echo "🚀 Building and pushing: $imagename"

  docker buildx build \
    --platform "$platform" \
    --tag "$registry$imagename" \
    --push \
    -f "$DOCKERFILE_PATH" \
    --build-arg module=$module \
    "$BUILD_CONTEXT"
done
