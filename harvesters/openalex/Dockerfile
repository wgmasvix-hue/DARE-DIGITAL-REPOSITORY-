FROM golang:1.21-alpine AS builder

WORKDIR /build

RUN apk add --no-cache git make

COPY go.* ./
RUN go mod download

COPY . .

RUN make build-static

FROM alpine:3.18

RUN apk add --no-cache ca-certificates tzdata

WORKDIR /app

COPY --from=builder /build/openalex-harvester-static ./openalex-harvester

# Create default directories
RUN mkdir -p /config /data /logs

# Default environment variables
ENV CONFIG_PATH=/config/config.json \
    TOPICS_PATH=/config/topics.json \
    STATE_PATH=/data/state.json \
    LOG_FILE=/logs/harvest.log

VOLUME ["/config", "/data", "/logs"]

ENTRYPOINT ["/app/openalex-harvester"]
CMD ["-config", "$CONFIG_PATH", "-topics", "$TOPICS_PATH", "-state", "$STATE_PATH"]
