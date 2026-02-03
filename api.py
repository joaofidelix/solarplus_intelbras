import aiohttp
import logging
from .const import CONF_BEARER_TOKEN

_LOGGER = logging.getLogger(__name__)

class IntelbrasSolarAPI:
    def __init__(self, bearer, refresh):
        self.bearer = bearer
        self.refresh = refresh  # Este é o refreshJWT do seu retorno
        self.base_url = "https://ens-server.intelbras.com.br/api"
        self.headers_base = {
            "plus": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eQFAmRC5Tb2xhcm9uZ3JpZDIwMjI=yJjbGllbnRfaWQiOiJpbnRiX2NsaWVudCIsImNsaWVudF9zZWNyZXQiOiJlZTI0ZWEwMy0wNDg1LTFudDNsNnJhNS05ZTBiLTZjMGVlYzcyNmZhNyJ9.G7qlZLztXQDcSaGCPwZVhQtDNWiy5Q7rKfYx96OXzGE",
            "origin": "https://solarplus.intelbras.com.br",
            "referer": "https://solarplus.intelbras.com.br/",
            "accept": "*/*",
            "content-type": "application/json",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"
        }

    async def _do_refresh_token(self):
        """Usa o refresh_token (JWT) para obter um novo access_token."""
        url = f"{self.base_url}/refresh-token"
        # Para o refresh, a Intelbras pede o Refresh JWT no header de Authorization
        headers = {**self.headers_base, "authorization": f"Bearer {self.refresh}"}
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        self.bearer = data["accessToken"]["accessJWT"]
                        _LOGGER.info("Token Intelbras Solar renovado com sucesso.")
                        return True
                    else:
                        _LOGGER.error("Erro ao renovar token. Status: %s", resp.status)
                        return False
            except Exception as e:
                _LOGGER.error("Falha na chamada de refresh: %s", e)
                return False

    async def request(self, method, endpoint):
        """Executa chamadas à API e gerencia expiração de token (401)."""
        url = f"{self.base_url}/{endpoint}"
        headers = {**self.headers_base, "authorization": f"Bearer {self.bearer}"}

        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, headers=headers) as resp:
                if resp.status == 401:
                    _LOGGER.warning("Acesso expirado. Tentando renovação...")
                    if await self._do_refresh_token():
                        # Recursão: tenta a chamada original com o novo bearer
                        return await self.request(method, endpoint)
                
                resp.raise_for_status()
                return await resp.json()

    async def get_data(self):
        """Busca as plantas e, para cada planta, busca os dispositivos."""
        try:
            # 1. Obter Plantas
            plants_data = await self.request("GET", "plants")
            if not plants_data.get("rows"):
                return None

            primary_plant = plants_data["rows"][0]
            plant_id = primary_plant["id"]

            # 2. Obter Microinversores
            devices_path = f"plants/{plant_id}/allDevices?limit=20"
            devices_data = await self.request("GET", devices_path)

            return {
                "plant": primary_plant,
                "devices": devices_data.get("rows", [])
            }
        except Exception as e:
            _LOGGER.error("Erro ao coletar dados da Intelbras Solar: %s", e)
            raise