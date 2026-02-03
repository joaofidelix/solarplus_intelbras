import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN, CONF_BEARER_TOKEN, CONF_REFRESH_TOKEN

class IntelbrasSolarConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            # Aqui poderíamos validar o token fazendo uma chamada teste
            return self.async_create_entry(title="Intelbras Solar", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_BEARER_TOKEN): str,
                vol.Required(CONF_REFRESH_TOKEN): str,
            }),
            errors=errors,
        )