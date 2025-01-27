#!/usr/bin/env bash

SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 || exit ; pwd -P )"
declare -a modules=("booked-management" "frontend" "login" "zimmerverwaltung" "anbietermgmt")
platform="linux/amd64,linux/arm64"
registry="mseyer91/"

docker login --username mseyer91 --password "$DOCKERHUB_PASSWORD"

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
    -f "${SCRIPTPATH}/../app/build/Dockerfile" \
    "${SCRIPTPATH}/../app/"
done
