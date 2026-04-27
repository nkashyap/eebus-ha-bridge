package grpc

import (
	"context"

	spineapi "github.com/enbility/spine-go/api"
	"google.golang.org/protobuf/types/known/timestamppb"

	pb "github.com/volschin/eebus-bridge/gen/proto/eebus/v1"
	"github.com/volschin/eebus-bridge/internal/eebus"
	"github.com/volschin/eebus-bridge/internal/usecases"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
)

type MonitoringService struct {
	pb.UnimplementedMonitoringServiceServer
	monitoring *usecases.MonitoringWrapper
	bus        *eebus.EventBus
	registry   *eebus.DeviceRegistry
}

func NewMonitoringService(monitoring *usecases.MonitoringWrapper, bus *eebus.EventBus, registry *eebus.DeviceRegistry) *MonitoringService {
	return &MonitoringService{monitoring: monitoring, bus: bus, registry: registry}
}

func (s *MonitoringService) GetPowerConsumption(_ context.Context, req *pb.DeviceRequest) (*pb.PowerMeasurement, error) {
	if s.monitoring == nil {
		return nil, status.Error(codes.Unavailable, "monitoring use case not initialized")
	}
	entity, err := s.resolveEntity(req.Ski)
	if err != nil {
		return nil, err
	}
	value, err := s.monitoring.Power(entity)
	if err != nil {
		return nil, status.Errorf(codes.Internal, "reading power: %v", err)
	}
	return &pb.PowerMeasurement{
		Watts:     value,
		Timestamp: timestamppb.Now(),
	}, nil
}

func (s *MonitoringService) GetEnergyConsumed(_ context.Context, req *pb.DeviceRequest) (*pb.EnergyMeasurement, error) {
	if s.monitoring == nil {
		return nil, status.Error(codes.Unavailable, "monitoring use case not initialized")
	}
	entity, err := s.resolveEntity(req.Ski)
	if err != nil {
		return nil, err
	}
	value, err := s.monitoring.EnergyConsumed(entity)
	if err != nil {
		return nil, status.Errorf(codes.Internal, "reading energy: %v", err)
	}
	return &pb.EnergyMeasurement{
		KilowattHours: value,
		Timestamp:     timestamppb.Now(),
	}, nil
}

func (s *MonitoringService) GetMeasurements(_ context.Context, req *pb.DeviceRequest) (*pb.MeasurementList, error) {
	if s.monitoring == nil {
		return nil, status.Error(codes.Unavailable, "monitoring use case not initialized")
	}
	entity, err := s.resolveEntity(req.Ski)
	if err != nil {
		return nil, err
	}

	now := timestamppb.Now()
	measurements := make([]*pb.MeasurementEntry, 0, 2)

	if value, err := s.monitoring.Power(entity); err == nil {
		measurements = append(measurements, &pb.MeasurementEntry{
			Type:      "power_consumption",
			Value:     value,
			Unit:      "W",
			Timestamp: now,
		})
	}

	if value, err := s.monitoring.EnergyConsumed(entity); err == nil {
		measurements = append(measurements, &pb.MeasurementEntry{
			Type:      "energy_consumed",
			Value:     value,
			Unit:      "kWh",
			Timestamp: now,
		})
	}

	if len(measurements) == 0 {
		return nil, status.Error(codes.NotFound, "no monitoring measurements available for device")
	}

	return &pb.MeasurementList{Measurements: measurements}, nil
}

func (s *MonitoringService) SubscribeMeasurements(req *pb.DeviceRequest, stream pb.MonitoringService_SubscribeMeasurementsServer) error {
	ch := s.bus.Subscribe()
	defer s.bus.Unsubscribe(ch)

	for {
		select {
		case evt, ok := <-ch:
			if !ok {
				return nil
			}
			if req.Ski != "" && evt.SKI != req.Ski {
				continue
			}
			var eventType pb.MeasurementEventType
			switch evt.Type {
			case "monitoring.power_updated":
				eventType = pb.MeasurementEventType_MEASUREMENT_EVENT_POWER_UPDATED
			case "monitoring.energy_consumed_updated":
				eventType = pb.MeasurementEventType_MEASUREMENT_EVENT_ENERGY_UPDATED
			default:
				continue
			}
			if err := stream.Send(&pb.MeasurementEvent{
				Ski:       evt.SKI,
				EventType: eventType,
			}); err != nil {
				return err
			}
		case <-stream.Context().Done():
			return stream.Context().Err()
		}
	}
}

func (s *MonitoringService) resolveEntity(ski string) (spineapi.EntityRemoteInterface, error) {
	if s.registry == nil {
		return nil, status.Error(codes.Unavailable, "device registry not initialized")
	}
	entity := s.registry.FirstEntity(ski)
	if entity == nil {
		return nil, status.Errorf(codes.NotFound, "no remote entity found for ski %s", ski)
	}
	return entity, nil
}
