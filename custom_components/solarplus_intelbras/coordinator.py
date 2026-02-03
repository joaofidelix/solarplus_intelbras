from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .api import IntelbrasSolarAPI

class IntelbrasSolarCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, api):
        super().__init__(
            hass,
            _LOGGER,
            name="Intelbras Solar Data",
            update_interval=timedelta(minutes=5),
        )
        self.api = api

    async def _async_update_data(self):
        try:
            return await self.api.get_data()
        except Exception as err:
            raise UpdateFailed(f"Erro ao comunicar com a API: {err}")