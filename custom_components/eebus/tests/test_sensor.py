"""Tests for EEBUS sensor entities."""

from unittest.mock import MagicMock

from custom_components.eebus.sensor import (
    EebusEnergyConsumedDhwSensor,
    EebusEnergyConsumedHeatingSensor,
    EebusPowerSensor,
)


def test_power_sensor_value():
    """Test power sensor returns correct value from coordinator data."""
    coordinator = MagicMock()
    coordinator.data = {"power_watts": 1500.0, "connected": True}
    coordinator.ski = "test-ski-123"

    sensor = EebusPowerSensor(coordinator)
    assert sensor.native_value == 1500.0
    assert sensor.native_unit_of_measurement == "W"


def test_power_sensor_unavailable():
    """Test power sensor returns None when data missing."""
    coordinator = MagicMock()
    coordinator.data = {"power_watts": None, "connected": True}
    coordinator.ski = "test-ski-123"

    sensor = EebusPowerSensor(coordinator)
    assert sensor.native_value is None


def test_heating_energy_sensor_value():
    """Test heating energy sensor returns correct value from coordinator data."""
    coordinator = MagicMock()
    coordinator.data = {"energy_consumed_heating_kwh": 8.4, "connected": True}
    coordinator.ski = "test-ski-123"

    sensor = EebusEnergyConsumedHeatingSensor(coordinator)
    assert sensor.native_value == 8.4
    assert sensor.native_unit_of_measurement == "kWh"


def test_dhw_energy_sensor_value():
    """Test DHW energy sensor returns correct value from coordinator data."""
    coordinator = MagicMock()
    coordinator.data = {"energy_consumed_dhw_kwh": 3.1, "connected": True}
    coordinator.ski = "test-ski-123"

    sensor = EebusEnergyConsumedDhwSensor(coordinator)
    assert sensor.native_value == 3.1
    assert sensor.native_unit_of_measurement == "kWh"
