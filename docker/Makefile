IMAGE_NAME ?= me/aasig_dev_platform
CONTAINER_NAME ?= aasigdp
CONTAINER_HOSTNAME ?= aasigdev_container
EXTERNAL_STORAGE = /optional/host/volume/here

default:
	@echo "make [build|buildnew|run|clean|logs|shell|stop|kill|rm]"
	@echo "(Note: build means only to build the container, not to start the android build)"

fromscratch: clean buildnew run shell

# Use local working directory as input (to get local changes)
# However, this requires files to be ADDed to exist within the docker
# build context (i.e. the same directory).  Using the root of the
# system is intractable because it will eventually contain the gigantic
# Android source code tree, which seems to be treated as part of the
# context to be considered by the docker daemon (whether used or not)
build:
	@if test -z "$$AASIGDP_TARGET"; then echo "Please define \$$AASIGDP_TARGET first" ; fi;
	if test -n "$$AASIGDP_TARGET" ; then \
	  cp ../bin/*.sh . ; \
	  docker build --build-arg AASIGDP_TARGET=$$AASIGDP_TARGET --tag=${IMAGE_NAME}:latest . \
	; fi

_reset:
	date >rebuild_marker

rebuild: _reset build

buildnew:
	@if test -z "$$AASIGDP_TARGET"; then echo "Please define \$$AASIGDP_TARGET first" ; fi;
	if test -n "$$AASIGDP_TARGET" ; then \
	  cp ../bin/*.sh . ; \
	  docker build --no-cache --build-arg AASIGDP_TARGET=$$AASIGDP_TARGET --tag=${IMAGE_NAME}:latest . \
	; fi

run:
	docker run -ti -h "${CONTAINER_HOSTNAME}" -d -v "${EXTERNAL_STORAGE}:/tmp/FIXME" --name=${CONTAINER_NAME} ${IMAGE_NAME}:latest /bin/bash

clean:
	@echo "docker rm -f -v ${CONTAINER_NAME}"
	@docker rm -f -v ${CONTAINER_NAME} >/dev/null || echo "Container removed already"
	@echo docker rmi ${IMAGE_NAME}:latest 
	@docker rmi ${IMAGE_NAME}:latest 2>/dev/null || echo "Image removed already"

logs:
	docker logs -f ${CONTAINER_NAME}

shell:
	docker exec -it ${CONTAINER_NAME} /bin/bash

stop:
	docker stop ${CONTAINER_NAME}

kill:
	docker kill ${CONTAINER_NAME} || echo "Cannot kill - probably not running"
	docker rm ${CONTAINER_NAME} || echo "Container removed already"

rm:
	docker rm ${CONTAINER_NAME} || echo "Container removed already"
