.PHONY: help
help:
	echo "Ask for help"

.PHONY: run
run: .artifacts/app.txt .artifacts/webpack.txt
	docker-compose up -d

BUILD_TAG ?= latest

.artifacts:
	mkdir -p .artifacts

.artifacts/app.txt: pyproject.toml poetry.lock Dockerfile | .artifacts
	DOCKER_BUILDKIT=1 docker build -t registry.gitlab.com/hunter2.app/hunter2/app:$(BUILD_TAG) --progress plain .
	docker image inspect -f '{{.Id}}' registry.gitlab.com/hunter2.app/hunter2/app:$(BUILD_TAG) > .artifacts/app.txt

.artifacts/metrics.txt: prometheus/* | .artifacts
	DOCKER_BUILDKIT=1 docker build -t registry.gitlab.com/hunter2.app/hunter2/metrics:$(BUILD_TAG) --progress plain prometheus
	docker image inspect -f '{{.Id}}' registry.gitlab.com/hunter2.app/hunter2/metrics:$(BUILD_TAG) > .artifacts/metrics.txt

.artifacts/web.txt: .artifacts/app.txt nginx/* | .artifacts
	DOCKER_BUILDKIT=1 docker build -t registry.gitlab.com/hunter2.app/hunter2/web:$(BUILD_TAG) --progress plain nginx
	docker image inspect -f '{{.Id}}' registry.gitlab.com/hunter2.app/hunter2/web:$(BUILD_TAG) > .artifacts/web.txt

.artifacts/webpack.txt: webpack/* | .artifacts
	DOCKER_BUILDKIT=1 docker build -t registry.gitlab.com/hunter2.app/hunter2/webpack:$(BUILD_TAG) --progress plain webpack
	docker image inspect -f '{{.Id}}' registry.gitlab.com/hunter2.app/hunter2/webpack:$(BUILD_TAG) > .artifacts/webpack.txt
