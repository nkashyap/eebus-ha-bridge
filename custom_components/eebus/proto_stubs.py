"""Convenience re-exports for generated protobuf stubs.

Run `generate_proto.sh` to regenerate after proto changes.
"""

from __future__ import annotations

import sys
from pathlib import Path

# The generated protobuf files use absolute imports like `from eebus.v1 import ...`.
# In Home Assistant they are vendored under `custom_components/eebus/generated`, so
# we need that directory on sys.path for the generated modules to import each other.
GENERATED_ROOT = Path(__file__).resolve().parent / "generated"
if str(GENERATED_ROOT) not in sys.path:
    sys.path.insert(0, str(GENERATED_ROOT))

try:
    from .generated.eebus.v1.common_pb2 import (  # noqa: F401
        DeviceRequest,
        Empty,
        LoadLimit,
        MeasurementEntry,
        PowerMeasurement,
    )
    from .generated.eebus.v1.device_service_pb2_grpc import DeviceServiceStub  # noqa: F401
    from .generated.eebus.v1.lpc_service_pb2 import (  # noqa: F401
        WriteFailsafeLimitRequest,
        WriteLoadLimitRequest,
    )
    from .generated.eebus.v1.lpc_service_pb2_grpc import LPCServiceStub  # noqa: F401
    from .generated.eebus.v1.monitoring_service_pb2_grpc import MonitoringServiceStub  # noqa: F401
except ImportError:
    # Stubs not yet generated — will fail at runtime if used
    pass
