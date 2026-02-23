import aiohttp
import json
from typing import Any, Dict, Optional, Union, Mapping, List
from base.env.config import env
from base import logger
import traceback
from .models import (
    SquareErrorModel,
    SuccessModel,
    AppFileContentModel
)
import discord
import io

class SquareRequest:
    BASE_URL = "https://api.squarecloud.app/v2"

    def __init__(self) -> None:
        self._session: Optional[aiohttp.ClientSession] = None
        self._headers: Dict[str, str] = {
            "Authorization": env.SQUARE_CLOUD_TOKEN,
        }

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            connector = aiohttp.TCPConnector(ttl_dns_cache=300)
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
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:

        session = await self._get_session()
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"

        request_headers = self._headers.copy()
        
        if headers:
            request_headers.update(headers)

        last_response = None

        try:
            async with session.request(
                method=method.upper(),
                url=url,
                json=body,
                params=params,
                headers=request_headers,
                timeout=aiohttp.ClientTimeout(
                    total=180,
                    sock_connect=30,
                    sock_read=180
                ),
                **kwargs
            ) as response:

                last_response = response

                try:
                    data = await response.json()
                except Exception:
                    raw = await response.text()
                    logger.error("Falha ao parsear JSON")
                    logger.error(raw)
                    return {
                        "status": "error",
                        "code": "INVALID_JSON_RESPONSE",
                        "message": "Invalid JSON response",
                        "raw": raw
                    }

                if not response.ok:
                    logger.error(f"Status: {response.status}, error: {data}")

                    return {
                        "status": "error",
                        "code": data.get("code", f"UNKNOWN_ERROR ({response.status})"),
                        "http_status": response.status,
                        "response": data
                    }

                return data

        except aiohttp.ClientResponseError as e:
            logger.error("Erro HTTP")
            logger.error(traceback.format_exc())

            return {
                "status": "error",
                "code": e.status,
                "message": e.message
            }

        except aiohttp.ClientError:
            logger.critical("Erro de transporte aiohttp")
            logger.critical(traceback.format_exc())

            if last_response:
                try:
                    data = await last_response.json()
                except Exception:
                    data = await last_response.text()

                return {
                    "status": "error",
                    "code": last_response.status,
                    "response": data
                }

            return {
                "status": "error",
                "code": None,
                "message": "Connection aborted"
            }

        except Exception:
            logger.critical("Erro inesperado na Square request")
            logger.critical(traceback.format_exc())

            if last_response:
                try:
                    data = await last_response.json()
                except Exception:
                    data = await last_response.text()

                return {
                    "status": "error",
                    "code": last_response.status,
                    "response": data
                }

            return {
                "status": "error",
                "code": None,
                "message": "Internal failure"
            }
            
    # ================
    # FUNCTIONS
    # ================

    async def get_app_info(self, app_id: str) -> Union[Dict[str, Any], SquareErrorModel]:
        endpoint = f"apps/{app_id}"
        result = await self.request(method="GET", endpoint=endpoint)

        if result.get("status") == "error":
            return SquareErrorModel(
                status="error",
                message=result.get("message"),
                code=result.get("code"),
            )

        app_data = result.get("response")

        if not app_data:
            return SquareErrorModel(
                status="error", 
                message="API returned success but no data was found in 'response' key.",
                code="DATA_NOT_FOUND"
            )

        return app_data

    async def get_me(self) -> Union[Dict[str, Any], SquareErrorModel]:
        endpoint = "users/me"
        result = await self.request(method="GET", endpoint=endpoint)

        if result.get("status") == "error":
            return SquareErrorModel(
                status="error",
                message=result.get("message"),
                code=result.get("code"),
            )

        user_data = result.get("response")

        if not user_data:
            return SquareErrorModel(
                status="error",
                message="Dados do usuário não encontrados na resposta.",
                code="EMPTY_USER_DATA"
            )

        return user_data

    async def get_app_status(self, app_id: str) -> Union[Dict[str, Any], SquareErrorModel]:
        endpoint = f"apps/{app_id}/status"
        result = await self.request(method="GET", endpoint=endpoint)

        if result.get("status") == "error":
            return SquareErrorModel(
                status="error",
                message=result.get("message"),
                code=result.get("code"),
            )

        status_data = result.get("response")

        if not status_data:
            return SquareErrorModel(
                status="error",
                message="Status da aplicação não encontrado.",
                code="STATUS_NOT_FOUND"
            )

        return status_data

    async def restart_app(self, app_id: str) -> Union[SuccessModel, SquareErrorModel]:
        endpoint = f"apps/{app_id}/restart"
        result = await self.request(method="POST", endpoint=endpoint)

        if result.get("status") == "error":
            return SquareErrorModel(
                status="error",
                message=result.get("message"),
                code=result.get("code")
            )

        return SuccessModel(**result)

    async def start_app(self, app_id: str) -> Union[SuccessModel, SquareErrorModel]:
        endpoint = f"apps/{app_id}/start"
        result = await self.request(method="POST", endpoint=endpoint)

        if result.get("status") == "error":
            return SquareErrorModel(
                status="error",
                message=result.get("message"),
                code=result.get("code")
            )

        return SuccessModel(**result)

    async def stop_app(self, app_id: str) -> Union[SuccessModel, SquareErrorModel]:
        endpoint = f"apps/{app_id}/stop"
        result = await self.request(method="POST", endpoint=endpoint)

        if result.get("status") == "error":
            return SquareErrorModel(
                status="error",
                message=result.get("message"),
                code=result.get("code")
            )

        return SuccessModel(**result)

    async def create_app_snapshot(self, app_id: str) -> Union[Dict[str, Any], SquareErrorModel]:
        endpoint = f"apps/{app_id}/snapshots"
        result = await self.request(method="POST", endpoint=endpoint)

        if result.get("status") == "error":
            return SquareErrorModel(
                status="error",
                message=result.get("message"),
                code=result.get("code")
            )

        snapshot_data = result.get("response")

        if not snapshot_data:
            return SquareErrorModel(
                status="error",
                message="Dados do snapshot não encontrados.",
                code="SNAPSHOT_NOT_FOUND"
            )

        return snapshot_data

    async def get_app_files(self, app_id: str, path: str = "/") -> Union[List[Dict[str, Any]], SquareErrorModel]:
        endpoint = f"apps/{app_id}/files"
        params = {"path": path}

        result = await self.request(method="GET", endpoint=endpoint, params=params)

        if result.get("status") == "error":
            return SquareErrorModel(
                status="error",
                message=result.get("message"),
                code=result.get("code")
            )

        files_data = result.get("response")

        if files_data is None:
            return SquareErrorModel(
                status="error",
                message="Não foi possível obter a lista de arquivos.",
                code="FILES_NOT_FOUND"
            )

        return files_data

    async def create_or_edit_app_file(self, app_id: str, path: str, content: str) -> Union[SuccessModel, SquareErrorModel]:
        endpoint = f"apps/{app_id}/files"
        payload = {
            "path": path,
            "content": content
        }

        result = await self.request(method="PUT", endpoint=endpoint, body=payload)

        if result.get("status") == "error":
            return SquareErrorModel(
                status="error",
                message=result.get("message"),
                code=result.get("code")
            )

        return SuccessModel(**result)

    async def delete_app(self, app_id: str) -> Union[SuccessModel, SquareErrorModel]:
        endpoint = f"apps/{app_id}"

        result = await self.request(method="DELETE", endpoint=endpoint)

        if result.get("status") == "error":
            return SquareErrorModel(
                status="error",
                message=result.get("message"),
                code=result.get("code")
            )

        return SuccessModel(**result)

    async def commit_app(self, app_id: str, file_bytes: bytes, filename: str) -> Union[SuccessModel, SquareErrorModel]:
        endpoint = f"apps/{app_id}/commit"

        form = aiohttp.FormData()
        form.add_field(
            "file",
            file_bytes,
            filename=filename,
            content_type="application/zip"
        )

        result = await self.request(
            method="POST",
            endpoint=endpoint,
            body=None,
            params=None,
            headers={},
            data=form
        )

        if result.get("status") == "error":
            return SquareErrorModel(
                status="error",
                message=result.get("message"),
                code=result.get("code")
            )

        return SuccessModel(**result)

    async def upload_app(self, file_bytes: bytes, filename: str) -> Union[Dict[str, Any], SquareErrorModel]:
        endpoint = "apps"

        form = aiohttp.FormData()
        form.add_field(
            "file",
            file_bytes,
            filename=filename,
            content_type="application/zip"
        )

        result = await self.request(method="POST", endpoint=endpoint, data=form)

        if result.get("status") == "error":
            return SquareErrorModel(
                status="error",
                message=result.get("message"),
                code=result.get("code")
            )

        upload_data = result.get("response")
        if not upload_data:
            return SquareErrorModel(
                status="error",
                message="Upload realizado, mas dados da aplicação não retornados.",
                code="UPLOAD_DATA_MISSING"
            )

        return upload_data

    async def get_app_logs(self, app_id: str) -> Union[Dict[str, Any], SquareErrorModel]:
        endpoint = f"apps/{app_id}/logs"
        result = await self.request(method="GET", endpoint=endpoint)

        if result.get("status") == "error":
            return SquareErrorModel(
                status="error",
                message=result.get("message"),
                code=result.get("code")
            )

        logs_data = result.get("response")
        if logs_data is None:
            return SquareErrorModel(
                status="error",
                message="Logs não encontrados.",
                code="LOGS_NOT_FOUND"
            )

        return logs_data

    async def move_app_file(
        self, 
        app_id: str, 
        origin_path: str, 
        target_path: str, 
        filename: Optional[str] = None
    ) -> Union[SuccessModel, SquareErrorModel]:
        origin = "/" + origin_path.strip("/")

        if filename:
            base_folder = target_path.strip("/")
            if base_folder == "":
                target = f"/{filename.lstrip('/')}"
            else:
                target = f"/{base_folder}/{filename.lstrip('/')}"
        else:
            target = "/" + target_path.strip("/")

        target = target.replace("//", "/")

        endpoint = f"apps/{app_id}/files?path={origin}"

        payload = {
            "path": origin,
            "to": target
        }
        logger.info(endpoint)
        logger.info(payload)

        result = await self.request(method="PATCH", endpoint=endpoint, body=payload)
        logger.info(result)

        if result.get("status") == "error":
            return SquareErrorModel(
                status="error",
                message=result.get("message"),
                code=result.get("code")
            )

        return SuccessModel(**result)

    async def delete_app_file(self, app_id: str, path: str) -> Union[SuccessModel, SquareErrorModel]:
        clean_path = f"/{path.strip('/')}"

        endpoint = f"apps/{app_id}/files"
        payload = {
            "path": clean_path
        }

        result = await self.request(method="DELETE", endpoint=endpoint, body=payload)

        if result.get("status") == "error":
            return SquareErrorModel(
                status="error",
                message=result.get("message"),
                code=result.get("code")
            )

        return SuccessModel(**result)

    async def get_app_file_content(self, app_id: str, path: str) -> Dict[str, Any]:
        clean_path = f"/{path.strip('/')}"
        endpoint = f"apps/{app_id}/files/content"
        params = {"path": clean_path}

        result = await self.request(method="GET", endpoint=endpoint, params=params)

        if result.get("status") == "error":
            return {
                "type": "error",
                "content": SquareErrorModel(
                    status="error",
                    message=result.get("message"),
                    code=result.get("code")
                )
            }

        try:
            content_model = AppFileContentModel(**result)
            byte_data = bytes(content_model.response.data)

            img_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.webp', '.ico')
            if clean_path.lower().endswith(img_extensions):
                file_name = clean_path.split('/')[-1]
                image_file = discord.File(io.BytesIO(byte_data), filename=file_name)
                return {"type": "image", "content": image_file}

            return {"type": "text", "content": byte_data.decode("utf-8")}

        except UnicodeDecodeError:
            return {"type": "binary", "content": "Arquivo binário não suportado para visualização."}
        except Exception as e:
            return {
                "type": "error", 
                "content": SquareErrorModel(status="error", message=str(e), code="PROCESS_ERROR")
            }

    async def get_app_envs(self, app_id: str) -> Union[Dict[str, Any], SquareErrorModel]:
        endpoint = f"apps/{app_id}/envs"
        result = await self.request(method="GET", endpoint=endpoint)

        if result.get("status") == "error":
            return SquareErrorModel(
                status="error",
                message=result.get("message"),
                code=result.get("code"),
            )

        envs_data = result.get("response")

        if envs_data is None:
            return SquareErrorModel(
                status="error",
                message="Variáveis de ambiente não encontradas.",
                code="ENVS_NOT_FOUND"
            )

        return envs_data

    async def set_app_envs(self, app_id: str, envs: Dict[str, str]) -> Union[Dict[str, Any], SquareErrorModel]:
        """
        Ex de envs: {"PORT": "8080", "NODE_ENV": "production"}
        """
        endpoint = f"apps/{app_id}/envs"

        payload = {
            "envs": envs
        }

        result = await self.request(method="POST", endpoint=endpoint, body=payload)

        if result.get("status") == "error":
            return SquareErrorModel(
                status="error",
                message=result.get("message"),
                code=result.get("code"),
            )

        envs_data = result.get("response")

        if envs_data is None:
            return SquareErrorModel(
                status="error",
                message="Falha ao processar resposta das variáveis.",
                code="ENVS_NOT_FOUND"
            )

        return envs_data

    async def update_app_envs(self, app_id: str, envs: Dict[str, str]) -> Union[Dict[str, Any], SquareErrorModel]:
        """
        sobrescreve os env da app
        """
        endpoint = f"apps/{app_id}/envs"
        payload = {
            "envs": envs
        }

        result = await self.request(method="PUT", endpoint=endpoint, body=payload)

        if result.get("status") == "error":
            return SquareErrorModel(
                status="error",
                message=result.get("message"),
                code=result.get("code"),
            )

        envs_data = result.get("response")

        if envs_data is None:
            return SquareErrorModel(
                status="error",
                message="Falha ao processar resposta da atualização de variáveis.",
                code="ENVS_UPDATE_FAILED"
            )

        return envs_data

    async def delete_app_envs(self, app_id: str, env_keys: List[str]) -> Union[Dict[str, Any], SquareErrorModel]:
        endpoint = f"apps/{app_id}/envs"
        payload = {
            "envs": env_keys
        }

        result = await self.request(method="DELETE", endpoint=endpoint, body=payload)

        if result.get("status") == "error":
            return SquareErrorModel(
                status="error",
                message=result.get("message"),
                code=result.get("code"),
            )

        envs_data = result.get("response")

        if envs_data is None:
            return SquareErrorModel(
                status="error",
                message="Falha ao processar resposta da remoção de variáveis.",
                code="ENVS_DELETE_FAILED"
            )

        return envs_data

    async def get_app_snapshots(self, app_id: str) -> Union[List[Dict[str, Any]], SquareErrorModel]:
        endpoint = f"apps/{app_id}/snapshots"

        result = await self.request(method="GET", endpoint=endpoint)

        if result.get("status") == "error":
            return SquareErrorModel(
                status="error",
                message=result.get("message"),
                code=result.get("code")
            )

        snapshots_data = result.get("response")

        if snapshots_data is None:
            return SquareErrorModel(
                status="error",
                message="Não foi possível obter a lista de snapshots.",
                code="SNAPSHOTS_NOT_FOUND"
            )

        return snapshots_data

    async def restore_app_snapshot(self, app_id: str, snapshot_id: str, version_id: str) -> Union[SuccessModel, SquareErrorModel]:
        endpoint = f"apps/{app_id}/snapshots/restore"

        payload = {
            "snapshotId": snapshot_id,
            "versionId": version_id
        }

        result = await self.request(
            method="POST", 
            endpoint=endpoint, 
            body=payload
        )

        if result.get("status") == "error":
            return SquareErrorModel(
                status="error",
                message=result.get("message"),
                code=result.get("code")
            )

        return SuccessModel(**result)

    # Databases Functions

    async def get_database_status(self, database_id: str) -> Union[Dict[str, Any], SquareErrorModel]:
        endpoint = f"databases/{database_id}/status"
        result = await self.request(method="GET", endpoint=endpoint)
    
        if result.get("status") == "error":
            return SquareErrorModel(
                status="error",
                message=result.get("message"),
                code=result.get("code"),
            )
    
        status_data = result.get("response")
    
        if not status_data:
            return SquareErrorModel(
                status="error",
                message="Status do banco de dados não encontrado.",
                code="STATUS_NOT_FOUND"
            )
    
        return status_data

    async def restart_db(self, db_id: str) -> Union[SuccessModel, SquareErrorModel]:
        endpoint_stop = f"databases/{db_id}/stop"
        result_stop = await self.request(method="POST", endpoint=endpoint_stop)

        if result_stop.get("status") == "error":
            return SquareErrorModel(
                status="error",
                message=result_stop.get("message"),
                code=result_stop.get("code")
            )

        endpoint_start = f"databases/{db_id}/start"
        result_start = await self.request(method="POST", endpoint=endpoint_start)

        if result_start.get("status") == "error":
            return SquareErrorModel(
                status="error",
                message=result_start.get("message"),
                code=result_start.get("code")
            )

        return SuccessModel(**result_start)

    async def start_db(self, db_id: str) -> Union[SuccessModel, SquareErrorModel]:
        endpoint = f"databases/{db_id}/start"
        result = await self.request(method="POST", endpoint=endpoint)

        if result.get("status") == "error":
            return SquareErrorModel(
                status="error",
                message=result.get("message"),
                code=result.get("code")
            )

        return SuccessModel(**result)

    async def stop_db(self, db_id: str) -> Union[SuccessModel, SquareErrorModel]:
        endpoint = f"databases/{db_id}/stop"
        result = await self.request(method="POST", endpoint=endpoint)

        if result.get("status") == "error":
            return SquareErrorModel(
                status="error",
                message=result.get("message"),
                code=result.get("code")
            )

        return SuccessModel(**result)

    async def create_database_snapshot(self, db_id: str) -> Union[Dict[str, Any], SquareErrorModel]:
        endpoint = f"databases/{db_id}/snapshots"
        result = await self.request(method="POST", endpoint=endpoint)

        if result.get("status") == "error":
            return SquareErrorModel(
                status="error",
                message=result.get("message"),
                code=result.get("code")
            )

        snapshot_data = result.get("response")

        if not snapshot_data:
            return SquareErrorModel(
                status="error",
                message="Dados do snapshot não encontrados.",
                code="SNAPSHOT_NOT_FOUND"
            )

        return snapshot_data

    async def delete_db(self, db_id: str) -> Union[SuccessModel, SquareErrorModel]:
        endpoint = f"databases/{db_id}"

        result = await self.request(method="DELETE", endpoint=endpoint)

        if result.get("status") == "error":
            return SquareErrorModel(
                status="error",
                message=result.get("message"),
                code=result.get("code")
            )

        return SuccessModel(**result)

    async def create_database(
        self, 
        db_name: str, 
        db_ram: int, 
        db_type: str
    ) -> Union[Dict[str, Any], SquareErrorModel]:
        db_type_lower = db_type.lower()

        versions = {
            "mongo": "8.0.11",
            "redis": "7.4.5",
            "postgres": "17.6", 
            "mysql": "9.5"
        }

        version = versions.get(db_type_lower)

        endpoint = "databases"

        payload = {
            "name": db_name,
            "memory": db_ram,
            "type": db_type_lower,
            "version": version
        }

        result = await self.request(method="POST", endpoint=endpoint, body=payload)

        if result.get("status") == "error":
            return SquareErrorModel(
                status="error",
                message=result.get("message"),
                code=result.get("code")
            )

        response = result.get("response", [])

        return response

    async def get_database(self, db_id: str) -> Union[Dict[str, Any], SquareErrorModel]:
        endpoint = f"databases/{db_id}"
        
        result = await self.request(method="GET", endpoint=endpoint)

        if result.get("status") == "error":
            return SquareErrorModel(
                status="error",
                message=result.get("message"),
                code=result.get("code")
            )

        db = result.get("response", [])

        return db

    async def reset_db_credenciais(self, db_id: str, type: str) -> Union[Dict[str, Any], SquareErrorModel]:
        endpoint = f"databases/{db_id}/credentials/reset"

        payload = {
            "reset": type
        }

        result = await self.request(method="POST", endpoint=endpoint, body=payload)

        if result.get("status") == "error":
            return SquareErrorModel(
                status="error",
                message=result.get("message"),
                code=result.get("code")
            )

        # Essa rota é meio confusa... Caso o type for certificate ela vai retornar apenas o success, mas se for password ela retorna o response com o password... Vai saber né? ent mais facil retornar o result msm e no modal eu organizo ele.

        return result

    async def get_db_credenciais(self, db_id: str) -> Union[Dict[str, Any], SquareErrorModel]:
        endpoint = f"databases/{db_id}/credentials/certificate"

        result = await self.request(method="GET", endpoint=endpoint)

        if result.get("status") == "error":
            return SquareErrorModel(
                status="error",
                message=result.get("message"),
                code=result.get("code")
            )

        response = result.get("response", [])

        return response

    async def alter_db_info(
        self, 
        db_id: str, 
        name: Optional[str] = None, 
        ram: Optional[int] = None
    ) -> Union[SuccessModel, SquareErrorModel]:
        endpoint = f"databases/{db_id}"

        body = {
            "name": name,
            "ram": ram
        }

        result = await self.request(method="PATCH", endpoint=endpoint, body=body)

        if result.get("status") == "error":
            return SquareErrorModel(
                status="error",
                message=result.get("message"),
                code=result.get("code")
            )

        return SuccessModel(**result)

    async def get_database_snapshots(self, db_id: str) -> Union[List[Dict[str, Any]], SquareErrorModel]:
        endpoint = f"databases/{db_id}/snapshots"

        result = await self.request(method="GET", endpoint=endpoint)

        if result.get("status") == "error":
            return SquareErrorModel(
                status="error",
                message=result.get("message"),
                code=result.get("code")
            )

        snapshots_data = result.get("response")

        if snapshots_data is None:
            return SquareErrorModel(
                status="error",
                message="Não foi possível obter a lista de snapshots.",
                code="SNAPSHOTS_NOT_FOUND"
            )

        return snapshots_data

    async def restore_database_snapshot(self, db_id: str, snapshot_id: str, version_id: str) -> Union[SuccessModel, SquareErrorModel]:
        endpoint = f"databases/{db_id}/snapshots/restore"

        payload = {
            "snapshotId": snapshot_id,
            "versionId": version_id
        }

        result = await self.request(
            method="POST", 
            endpoint=endpoint, 
            body=payload
        )

        if result.get("status") == "error":
            return SquareErrorModel(
                status="error",
                message=result.get("message"),
                code=result.get("code")
            )

        return SuccessModel(**result)
        
    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()

squarecloud_request = SquareRequest()