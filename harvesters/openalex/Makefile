.PHONY: build test clean deps lint run run-test help

BINARY_NAME=openalex-harvester
VERSION=1.0.0
BUILD_TIME=$(shell date -u '+%Y-%m-%d_%H:%M:%S')
GIT_COMMIT=$(shell git rev-parse --short HEAD)
LDFLAGS=-ldflags "-X main.Version=$(VERSION) -X main.BuildTime=$(BUILD_TIME) -X main.GitCommit=$(GIT_COMMIT)"

help:
	@echo "OpenAlex Harvester - Makefile targets"
	@echo ""
	@echo "Usage:"
	@echo "  make build          Build the harvester binary"
	@echo "  make build-static   Build static binary"
	@echo "  make test-api       Test OpenAlex API connectivity"
	@echo "  make run            Run incremental harvest"
	@echo "  make run-full       Run full harvest"
	@echo "  make init           Initialize default configuration"
	@echo "  make deps           Download dependencies"
	@echo "  make clean          Remove build artifacts"
	@echo "  make lint           Run linter"
	@echo "  make fmt            Format code"
	@echo "  make docker-build   Build Docker image"
	@echo "  make docker-run     Run harvester in Docker"
	@echo ""

build:
	@echo "Building $(BINARY_NAME)..."
	go build $(LDFLAGS) -o $(BINARY_NAME) .
	@echo "✓ Build complete: $(BINARY_NAME)"

build-static:
	@echo "Building static binary..."
	CGO_ENABLED=0 GOOS=linux go build $(LDFLAGS) -a -installsuffix cgo -o $(BINARY_NAME)-static .
	@echo "✓ Static build complete: $(BINARY_NAME)-static"

deps:
	@echo "Downloading dependencies..."
	go mod download
	go mod tidy
	@echo "✓ Dependencies updated"

clean:
	@echo "Cleaning build artifacts..."
	rm -f $(BINARY_NAME) $(BINARY_NAME)-static
	rm -f *.prof
	go clean
	@echo "✓ Clean complete"

lint:
	@echo "Running linter..."
	golangci-lint run ./...

fmt:
	@echo "Formatting code..."
	go fmt ./...
	@echo "✓ Code formatted"

test-api:
	@echo "Testing OpenAlex API connectivity..."
	@./$(BINARY_NAME) -test-api

run: build
	@echo "Running incremental harvest..."
	@./$(BINARY_NAME)

run-full: build
	@echo "Running full harvest..."
	@./$(BINARY_NAME) -full

run-topic: build
	@echo "Running harvest for specific topic..."
	@./$(BINARY_NAME) -topic "$(TOPIC)"

init: build
	@echo "Initializing configuration..."
	@./$(BINARY_NAME) -init-config

docker-build:
	@echo "Building Docker image..."
	docker build -t dare/openalex-harvester:$(VERSION) .
	docker tag dare/openalex-harvester:$(VERSION) dare/openalex-harvester:latest
	@echo "✓ Docker image built"

docker-run:
	@echo "Running harvester in Docker..."
	docker run --rm \
		-v $(PWD)/config:/config \
		-v $(PWD)/data:/data \
		dare/openalex-harvester:$(VERSION)

docker-push:
	@echo "Pushing Docker image..."
	docker push dare/openalex-harvester:$(VERSION)
	docker push dare/openalex-harvester:latest
	@echo "✓ Docker image pushed"

install: build
	@echo "Installing harvester..."
	mkdir -p ~/.dare/harvester
	cp $(BINARY_NAME) ~/.dare/harvester/
	cp config.json ~/.dare/harvester/
	cp topics.json ~/.dare/harvester/
	@echo "✓ Installed to ~/.dare/harvester/"

install-systemd:
	@echo "Installing systemd service..."
	sudo cp systemd/openalex-harvester.service /etc/systemd/system/
	sudo cp systemd/openalex-harvester.timer /etc/systemd/system/
	sudo systemctl daemon-reload
	sudo systemctl enable openalex-harvester.timer
	@echo "✓ Systemd service installed"
	@echo "Start with: sudo systemctl start openalex-harvester.timer"

bench:
	@echo "Running benchmarks..."
	go test -bench=. -benchmem ./...

profile-cpu: build
	@echo "Running CPU profile..."
	./$(BINARY_NAME) -cpuprofile=cpu.prof
	go tool pprof $(BINARY_NAME) cpu.prof

profile-mem: build
	@echo "Running memory profile..."
	./$(BINARY_NAME) -memprofile=mem.prof
	go tool pprof $(BINARY_NAME) mem.prof

all: clean deps build
	@echo "✓ Full build complete"

.DEFAULT_GOAL := help
