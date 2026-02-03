from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import UnitOfPower, UnitOfEnergy, PERCENTAGE
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    """Configura os sensores baseados na entrada de configuração."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = []

    # 1. Sensores Globais da Planta (Dados mestres)
    entities.append(PlantPowerSensor(coordinator))
    entities.append(PlantEnergyTodaySensor(coordinator))

    # 2. Sensores Dinâmicos por Microinversor
    # O loop abaixo percorre todos os dispositivos retornados no seu CURL
    for device in coordinator.data["devices"]:
        entities.append(MicroinverterStatusSensor(coordinator, device))
        entities.append(MicroinverterRSSISensor(coordinator, device))

    async_add_entities(entities)

class IntelbrasBaseSensor(SensorEntity):
    """Classe base para sensores Intelbras."""
    def __init__(self, coordinator):
        self.coordinator = coordinator

    @property
    def should_poll(self):
        return False

    @property
    def available(self):
        return self.coordinator.last_update_success

    async def async_added_to_hass(self):
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))

# --- Sensores da Planta ---

class PlantPowerSensor(IntelbrasBaseSensor):
    _attr_name = "Intelbras Solar Potência Atual"
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def unique_id(self):
        return f"{self.coordinator.data['plant']['id']}_current_power"

    @property
    def native_value(self):
        return self.coordinator.data["plant"]["metrics"]["currentPower"]

class PlantEnergyTodaySensor(IntelbrasBaseSensor):
    _attr_name = "Intelbras Solar Energia Hoje"
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING

    @property
    def unique_id(self):
        return f"{self.coordinator.data['plant']['id']}_energy_today"

    @property
    def native_value(self):
        return self.coordinator.data["plant"]["metrics"]["energyToday"]

# --- Sensores Dinâmicos dos Microinversores ---

class MicroinverterStatusSensor(IntelbrasBaseSensor):
    """Sensor de Status Online/Offline para cada microinversor."""
    def __init__(self, coordinator, device):
        super().__init__(coordinator)
        self._serial = device["serialNumber"]
        self._attr_name = f"Microinversor {self._serial} Status"
        self._attr_unique_id = f"{self._serial}_status"

    @property
    def native_value(self):
        # Localiza os dados deste microinversor específico na lista atualizada
        for d in self.coordinator.data["devices"]:
            if d["serialNumber"] == self._serial:
                return d["status"]
        return "Desconhecido"

class MicroinverterRSSISensor(IntelbrasBaseSensor):
    """Sensor de Sinal WiFi para cada microinversor."""
    _attr_native_unit_of_measurement = "dBm"
    _attr_device_class = SensorDeviceClass.SIGNAL_STRENGTH

    def __init__(self, coordinator, device):
        super().__init__(coordinator)
        self._serial = device["serialNumber"]
        self._attr_name = f"Microinversor {self._serial} Sinal"
        self._attr_unique_id = f"{self._serial}_rssi"

    @property
    def native_value(self):
        for d in self.coordinator.data["devices"]:
            if d["serialNumber"] == self._serial:
                return d["rssi"]
        return None