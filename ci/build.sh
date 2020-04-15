#!/bin/bash -e

image_uri=$1
image_name=cdk

branch_name=$(git rev-parse --abbrev-ref HEAD)
revision=$(git rev-parse HEAD)
short_rev=${revision:0:7}
semvar=$(cat version.txt)
image_version=$semvar-$branch_name-$short_rev

export BUILD_TAG=$image_version

docker-compose build --pull $image_name

docker-compose run tests

if [ "${branch_name}" == "master" ]; then
  docker tag $image_name:$image_version $image_name:latest

  if [ -n "${image_uri}" ]; then
    docker tag $image_name:latest $image_uri:latest
    docker push $image_uri:latest
  fi
fi
