ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:latest

FROM golang:1.26-alpine AS builder

ARG EEBUS_HA_BRIDGE_REF=main
ARG EEBUS_HA_BRIDGE_REPO=https://github.com/nkashyap/eebus-ha-bridge.git

RUN apk add --no-cache git

WORKDIR /src
RUN git clone --depth 1 --branch "${EEBUS_HA_BRIDGE_REF}" "${EEBUS_HA_BRIDGE_REPO}" repo

WORKDIR /src/repo/eebus-bridge
RUN go mod download
RUN CGO_ENABLED=0 go build -o /out/eebus-bridge ./cmd/eebus-bridge

FROM ${BUILD_FROM}

COPY --from=builder /out/eebus-bridge /usr/local/bin/eebus-bridge
COPY rootfs /

RUN chmod a+x /usr/local/bin/eebus-bridge /usr/local/bin/run.sh

CMD ["/usr/local/bin/run.sh"]
