"""
Support for HomeSeer binary-type devices.
"""
import logging

from homeassistant.components.binary_sensor import BinarySensorDevice
from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

DEPENDENCIES = ['homeseer']


async def async_setup_platform(hass, config, async_add_entities,
                               discovery_info=None):
    """Set up HomeSeer binary-type devices."""
    from pyhs3 import HASS_BINARY_SENSORS

    binary_sensor_devices = []
    homeseer = hass.data[DOMAIN]

    for device in homeseer.devices:
        if device.device_type_string in HASS_BINARY_SENSORS:
            dev = HSBinarySensor(device, homeseer)
            binary_sensor_devices.append(dev)
            _LOGGER.info('Added HomeSeer binary-sensor-type device: {}'.format(dev.name))

    async_add_entities(binary_sensor_devices)


class HSBinarySensor(BinarySensorDevice):
    """Representation of a HomeSeer binary-type device."""
    def __init__(self, device, connection):
        self._device = device
        self._connection = connection

    @property
    def available(self):
        """Return True if the HomeSeer connection is available."""
        from pyhs3 import STATE_LISTENING
        return self._connection.api.state == STATE_LISTENING

    @property
    def device_state_attributes(self):
        attr = {
            'Device Ref': self._device.ref,
            'Location': self._device.location,
            'Location 2': self._device.location2
        }
        return attr

    @property
    def name(self):
        """Return the name of the device."""
        if self._connection.location_names:
            return '{} {} {}'.format(self._device.location2, self._device.location, self._device.name)
        else:
            return self._device.name

    @property
    def should_poll(self):
        """No polling needed."""
        return False

    @property
    def is_on(self):
        """Return true if device is on."""
        return self._device.value > 0

    async def async_added_to_hass(self):
        """Register value update callback."""
        self._device.register_update_callback(self.async_schedule_update_ha_state)
