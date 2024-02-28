#!/bin/bash

args=$@

## check OS
OSname="Mac-Linux"
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "win32" ]]; then
    OSname="Windows"
fi

## set config
docker_head="sudo"; docker_head_images="sudo"
if [[ $OSname == "Windows" ]]; then
    docker_head="winpty"; docker_head_images=""
fi

name="real"

if [[ $name == "real" ]]; then
    # real container
    image_name='real'; tag_name='v1.0'
fi

## pull image
if ! $docker_head_images docker images --format '{{.Repository}}:{{.Tag}}' | grep -q -x "$image_name:$tag_name"; then
    $docker_head docker pull rintrsuzuki/$image_name:$tag_name
    $docker_head docker tag rintrsuzuki/$image_name:$tag_name $image_name:$tag_name
    $docker_head docker rmi rintrsuzuki/$image_name:$tag_name
fi

## run container
workdir=`pwd`
container_name='real-1'
container_workdir='/data/REAL'
if [[ $name == "real" ]]; then
    $docker_head docker run -itd --rm \
    -v $workdir:$container_workdir \
    --name $container_name \
    $image_name:$tag_name
fi

## exec REALAssociator
$docker_head docker exec -it $container_name python3 src/REAL.py $args

## stop container
$docker_head docker stop $container_name