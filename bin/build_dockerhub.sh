#!/usr/bin/env bash

SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 || exit ; pwd -P )"
declare -a modules=("buchungsmanagement" "frontend" "login" "zimmerverwaltung")
platform="linux/amd64,linux/arm64"
registry="mrangger/"

docker login --username mrangger --password "$DOCKERHUB_PASSWORD"

git_branch_name="$(git symbolic-ref HEAD 2>/dev/null)" ||
git_branch_name="(unnamed branch)"     # detached HEAD
git_branch_name=${git_branch_name##refs/heads/}

for module in "${modules[@]}"; do
  imagename="apeni-${module}:${git_branch_name}"
  echo "$imagename"
  docker buildx build \
    --platform "$platform" \
    --tag "$registry$imagename" \
    --push \
    "${SCRIPTPATH}/../app/$module/"
done
