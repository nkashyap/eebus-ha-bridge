package eebus_test

import (
	"testing"

	spineapi "github.com/enbility/spine-go/api"
	"github.com/volschin/eebus-bridge/internal/eebus"
)

type stubEntity struct {
	spineapi.EntityRemoteInterface
}

func TestRegistryAddAndLookup(t *testing.T) {
	reg := eebus.NewDeviceRegistry()

	reg.AddDevice("ski-123", eebus.DeviceInfo{
		Brand:  "Vaillant",
		Model:  "VR940f",
		Serial: "12345",
	})

	info, ok := reg.GetDevice("ski-123")
	if !ok {
		t.Fatal("device not found")
	}
	if info.Brand != "Vaillant" {
		t.Errorf("Brand = %q, want Vaillant", info.Brand)
	}
}

func TestRegistryRemove(t *testing.T) {
	reg := eebus.NewDeviceRegistry()
	reg.AddDevice("ski-123", eebus.DeviceInfo{Brand: "Vaillant"})
	reg.RemoveDevice("ski-123")

	_, ok := reg.GetDevice("ski-123")
	if ok {
		t.Error("device should have been removed")
	}
}

func TestRegistryListDevices(t *testing.T) {
	reg := eebus.NewDeviceRegistry()
	reg.AddDevice("ski-1", eebus.DeviceInfo{Brand: "A"})
	reg.AddDevice("ski-2", eebus.DeviceInfo{Brand: "B"})

	devices := reg.ListDevices()
	if len(devices) != 2 {
		t.Errorf("len(devices) = %d, want 2", len(devices))
	}
}

func TestRegistryFirstAvailableEntity(t *testing.T) {
	reg := eebus.NewDeviceRegistry()
	entity := &stubEntity{}

	reg.UpsertObservation("ski-1", nil, entity, "monitoring")

	got := reg.FirstAvailableEntity()
	if got == nil {
		t.Fatal("FirstAvailableEntity() = nil, want non-nil")
	}
}
