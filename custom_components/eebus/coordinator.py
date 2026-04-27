"""DataUpdateCoordinator for EEBUS integration."""

from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import Any

import grpc
import grpc.aio

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER = logging.getLogger(__name__)

POLL_INTERVAL = timedelta(seconds=30)


class EebusCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator that manages gRPC connection and data updates."""

    def __init__(
        self,
        hass: HomeAssistant,
        host: str,
        port: int,
        ski: str,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="EEBUS",
            update_interval=POLL_INTERVAL,
        )
        self.host = host
        self.port = port
        self.ski = ski
        self._channel: grpc.aio.Channel | None = None
        self._stream_tasks: list[asyncio.Task] = []
        self._was_unavailable: bool = False

    async def _ensure_channel(self) -> grpc.aio.Channel:
        """Create or return existing gRPC channel."""
        if self._channel is None:
            self._channel = grpc.aio.insecure_channel(f"{self.host}:{self.port}")
        return self._channel

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data via gRPC polling."""
        try:
            channel = await self._ensure_channel()
            from . import proto_stubs

            device_stub = proto_stubs.DeviceServiceStub(channel)
            status = await device_stub.GetStatus(proto_stubs.Empty())

            data: dict[str, Any] = {
                "connected": status.running,
                "local_ski": status.local_ski,
            }

            try:
                monitoring_stub = proto_stubs.MonitoringServiceStub(channel)
                power = await monitoring_stub.GetPowerConsumption(
                    proto_stubs.DeviceRequest(ski=self.ski)
                )
                data["power_watts"] = power.watts
            except grpc.aio.AioRpcError:
                data["power_watts"] = None

            try:
                monitoring_stub = proto_stubs.MonitoringServiceStub(channel)
                energy = await monitoring_stub.GetEnergyConsumed(
                    proto_stubs.DeviceRequest(ski=self.ski)
                )
                data["energy_consumed_kwh"] = energy.kilowatt_hours
            except grpc.aio.AioRpcError:
                data["energy_consumed_kwh"] = None

            try:
                lpc_stub = proto_stubs.LPCServiceStub(channel)
                limit = await lpc_stub.GetConsumptionLimit(
                    proto_stubs.DeviceRequest(ski=self.ski)
                )
                data["consumption_limit"] = {
                    "value_watts": limit.value_watts,
                    "is_active": limit.is_active,
                    "is_changeable": limit.is_changeable,
                }
            except grpc.aio.AioRpcError:
                data["consumption_limit"] = None

            try:
                lpc_stub = proto_stubs.LPCServiceStub(channel)
                hb = await lpc_stub.GetHeartbeatStatus(
                    proto_stubs.DeviceRequest(ski=self.ski)
                )
                data["heartbeat_status"] = {
                    "running": hb.running,
                    "within_duration": hb.within_duration,
                }
            except grpc.aio.AioRpcError:
                data["heartbeat_status"] = None

            if self._was_unavailable:
                _LOGGER.info("EEBUS bridge connection restored at %s:%s", self.host, self.port)
                self._was_unavailable = False

            return data
        except grpc.aio.AioRpcError as err:
            if self._channel is not None:
                await self._channel.close()
                self._channel = None

            if not self._was_unavailable:
                _LOGGER.warning(
                    "EEBUS bridge unavailable at %s:%s: %s", self.host, self.port, err
                )
                self._was_unavailable = True

            raise UpdateFailed(f"gRPC error: {err}") from err

    async def async_write_lpc_limit(self, value_watts: float) -> None:
        """Write LPC consumption limit via gRPC."""
        channel = await self._ensure_channel()
        from . import proto_stubs
        stub = proto_stubs.LPCServiceStub(channel)
        await stub.WriteConsumptionLimit(
            proto_stubs.WriteLoadLimitRequest(
                ski=self.ski, value_watts=value_watts, is_active=True
            )
        )

    async def async_write_failsafe_limit(self, value_watts: float) -> None:
        """Write failsafe limit via gRPC."""
        channel = await self._ensure_channel()
        from . import proto_stubs
        stub = proto_stubs.LPCServiceStub(channel)
        await stub.WriteFailsafeLimit(
            proto_stubs.WriteFailsafeLimitRequest(
                ski=self.ski, value_watts=value_watts
            )
        )

    async def async_set_lpc_active(self, active: bool) -> None:
        """Activate or deactivate LPC limit via gRPC."""
        channel = await self._ensure_channel()
        from . import proto_stubs
        stub = proto_stubs.LPCServiceStub(channel)
        current = await stub.GetConsumptionLimit(
            proto_stubs.DeviceRequest(ski=self.ski)
        )
        await stub.WriteConsumptionLimit(
            proto_stubs.WriteLoadLimitRequest(
                ski=self.ski,
                value_watts=current.value_watts,
                is_active=active,
            )
        )

    async def async_start_heartbeat(self) -> None:
        """Start EEBUS heartbeat via gRPC."""
        channel = await self._ensure_channel()
        from . import proto_stubs
        stub = proto_stubs.LPCServiceStub(channel)
        await stub.StartHeartbeat(proto_stubs.DeviceRequest(ski=self.ski))

    async def async_stop_heartbeat(self) -> None:
        """Stop EEBUS heartbeat via gRPC."""
        channel = await self._ensure_channel()
        from . import proto_stubs
        stub = proto_stubs.LPCServiceStub(channel)
        await stub.StopHeartbeat(proto_stubs.DeviceRequest(ski=self.ski))

    async def async_shutdown(self) -> None:
        """Close gRPC channel and cancel stream tasks."""
        for task in self._stream_tasks:
            task.cancel()
        self._stream_tasks.clear()
        if self._channel is not None:
            await self._channel.close()
            self._channel = None
