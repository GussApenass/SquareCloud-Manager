import aiohttp
import json
from typing import Any, Dict, Optional, Union, Mapping
from base.env.config import env
from base import logger

class SquareBlobRequest:
    BASE_URL = "https://blob.squarecloud.app/v1"

    def __init__(self) -> None:
        self._session: Optional[aiohttp.ClientSession] = None
        self._headers: Dict[str, str] = {
            "Authorization": env.SQUARE_CLOUD_TOKEN,
        }

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            connector = aiohttp.TCPConnector(limit=None, ttl_dns_cache=300)
            self._session = aiohttp.ClientSession(
                connector=connector,
                json_serialize=json.dumps
            )
        return self._session

    async def request(
        self,
        method: str,
        endpoint: str,
        body: Optional[Union[Dict[str, Any], Mapping[str, Any]]] = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        session = await self._get_session()
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"

        headers = self._headers.copy()
        if method.upper() in ["POST", "PATCH", "DELETE", "PUT"]:
            headers["Content-Type"] = "application/json"

        try:
            async with session.request(
                method=method.upper(),
                url=url,
                json=body,
                params=params,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30),
                **kwargs
            ) as response:

                data: Dict[str, Any] = await response.json()

                if not response.ok:
                    logger.error(f"Square Cloud API Error [{response.status}]: {data.get('message', 'Sem mensagem')}")
                    return data

                return data

        except aiohttp.ClientError as e:
            logger.critical(f"Erro de conexão com Square Cloud: {e}")
            return {"status": "error", "message": str(e)}
        except Exception as e:
            logger.error(f"Erro inesperado na request: {e}")
            return {"status": "error", "message": "Internal request failure"}

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()

blob_request = SquareBlobRequest()