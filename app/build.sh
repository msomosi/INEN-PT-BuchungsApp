#!/usr/bin/env bash

registry="mrangger/"

#declare -a modules=("buchungsmanagement" "kundenverwaltung" "login-service" "zimmerverwaltung")
declare -a modules=("buchungsmanagement" "login-service" "zimmerverwaltung")

if [[ $1 == "-local" ]]; then
  if [[ ! $(docker buildx ls | grep host-builder) ]]; then
    docker buildx create --name host-builder --driver-opt network=host
  fi

  docker buildx use host-builder
  registry="localhost:32000/"
else
  docker login --username mrangger --password "$DOCKERHUB_PASSWORD"
fi

for module in "${modules[@]}"; do
  imagename="apeni-${module}:latest"
  echo $imagename
  docker buildx build \
    --platform linux/amd64 \
    --tag "$registry$imagename" \
    --push \
    $module
done
