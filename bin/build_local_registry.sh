#!/usr/bin/env bash

SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 || exit ; pwd -P )"
declare -a modules=("booked-management" "frontend" "login" "zimmerverwaltung" "anbietermgmt")
platform="linux/amd64"
registry="localhost:32000/"

if ! docker buildx ls | grep -q host-builder; then
  docker buildx create --name host-builder --driver-opt network=host
fi

docker buildx use host-builder

for module in "${modules[@]}"; do
  imagename="apeni-${module}:latest"
  echo "$imagename"
  docker buildx build \
    --platform "$platform" \
    --tag "$registry$imagename" \
    --push \
    -f "${SCRIPTPATH}/../app/build/Dockerfile" \
    "${SCRIPTPATH}/../app/"
done
