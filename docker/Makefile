IMAGE_NAME ?= localhost/aasig_dev_platform
CONTAINER_NAME ?= aasigdp
CONTAINER_HOSTNAME ?= aasigdev_container

.PHONY: _reset build kill rm rmi

ifndef AASIGDP_TARGET
   $(error "Please define $$AASIGDP_TARGET first (h3ulcb,m3ulcb,imx8,hikey960,hikey970,...)")
endif

default:
	@echo "make [build|buildnew|run|clean|logs|shell|stop|kill|rm|rmi]"
	@echo "(Note: build means only to build the container, not to start the android build)"

# Use local working directory as input (to get local changes)
# However, this requires files to be ADDed to exist within the docker
# build context (i.e. the same directory).  Using the root of the
# system is intractable because it will eventually contain the gigantic
# Android source code tree, which seems to be treated as part of the
# context to be considered by the docker daemon (whether used or not)

build: 
	cp -r ../bin .
	cp -r ../vendor/* vendor/
	docker build --build-arg AASIGDP_TARGET=$$AASIGDP_TARGET --tag=${IMAGE_NAME}:latest .

# Modify build marker, this will invalidate any cached steps after its use
_reset:
	date >rebuild_marker

# Build container from the point of rebuild_marker (if used)
rebuild: _reset build

# Build container fully from scratch, without reusing cached steps
buildnew:
	cp -r ../bin .
	cp -r ../vendor/* vendor/
	docker build --no-cache --build-arg AASIGDP_TARGET=$$AASIGDP_TARGET --tag=${IMAGE_NAME}:latest .

# Run container (detached)
run:
	docker run -ti -h "${CONTAINER_HOSTNAME}" -d -v ${PWD}/..:/workdir --name=${CONTAINER_NAME} ${IMAGE_NAME}:latest /bin/bash

# Force remove container and image
clean:  kill rm rmi

logs:
	docker logs -f ${CONTAINER_NAME}

shell:
	docker exec -it ${CONTAINER_NAME} /bin/bash

stop:
	docker stop ${CONTAINER_NAME} || true

# Force stop and remove container
kill:
	docker kill ${CONTAINER_NAME} || echo "Cannot kill - probably not running"
	docker rm ${CONTAINER_NAME} || echo "Container removed already"

rm:
	docker kill ${CONTAINER_NAME} 2>/dev/null && echo killed || echo "Container seems stopped already"
	docker rm ${CONTAINER_NAME} || echo "Container seems removed already"

rmi:
	@docker rmi ${IMAGE_NAME}:latest 2>/dev/null && echo removed image || echo "Image seems removed already"
