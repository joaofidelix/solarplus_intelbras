from .const import DOMAIN, CONF_BEARER_TOKEN, CONF_REFRESH_TOKEN
from .api import IntelbrasSolarAPI
from .coordinator import IntelbrasSolarCoordinator

async def async_setup_entry(hass, entry):
    api = IntelbrasSolarAPI(entry.data[CONF_BEARER_TOKEN], entry.data[CONF_REFRESH_TOKEN])
    coordinator = IntelbrasSolarCoordinator(hass, api)
    
    await coordinator.async_config_entry_first_refresh()
    
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True