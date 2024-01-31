#!/bin/bash

## params
name=$1

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

if [[ $name == "" ]]; then
    name="real"
fi

if [[ $name == "real" ]]; then
    # real container
    image_name='real'; tag_name='v1.0'
fi

## pull image
if ! $docker_head_images docker images --format '{{.Repository}}:{{.Tag}}' | grep -q "$image_name:$tag_name"; then
    $docker_head docker pull rintrsuzuki/$image_name:$tag_name
    $docker_head docker tag rintrsuzuki/$image_name:$tag_name $image_name:$tag_name
    $docker_head docker rmi rintrsuzuki/$image_name:$tag_name
fi

## run container
workdir=`pwd`
if [[ $name == "real" ]]; then
    $docker_head docker run -it --rm \
    -v $workdir:/data/REAL \
    $image_name:$tag_name
    /bin/bash
fi