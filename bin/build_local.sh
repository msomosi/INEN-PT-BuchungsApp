#!/usr/bin/env bash

SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 || exit ; pwd -P )"
declare -a modules=("booked-management" "frontend" "login" "zimmerverwaltung" "anbietermgmt")

for module in "${modules[@]}"; do
  imagename="apeni-${module}:latest"
  echo "$imagename"
  docker buildx build \
    --tag "$imagename" \
    --load \
    -f "${SCRIPTPATH}/../app/build/Dockerfile" \
    "${SCRIPTPATH}/../app/"
done
