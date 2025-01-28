#!/usr/bin/env bash

SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 || exit ; pwd -P )"
declare -a modules=("buchungsmanagement" "frontend" "login" "zimmerverwaltung")

for module in "${modules[@]}"; do
  imagename="apeni-${module}:latest"
  echo "$imagename"
  docker buildx build \
    --tag "$imagename" \
    --load \
    "${SCRIPTPATH}/../app/$module/"
done
