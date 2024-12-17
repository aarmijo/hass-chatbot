"""Home Assistant Action Tool spec."""

import logging
import os
import requests  # type: ignore
import json
from llama_index.core.tools import FunctionTool
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class HassAction:
    @classmethod
    def run_hass_action(entity_id: str, accion: str, params: dict) -> str | None:
        """
        Ejecuta una acción (servicio) en Home Assistant.

        Args:
            entity_id (str): El ID de la entidad a la que aplicar la acción.
            acción (str): El nombre de la acción (ej: "turn_on", "toggle").            
            params (dict, opcional): Un diccionario con parámetros adicionales para la acción.

        Returns:
            str o None: La respuesta de Home Assistant si la solicitud fue exitosa,
                        o None si hubo un error.
        """

        hassio_token = os.getenv('HASS_TOKEN')
        if not hassio_token:
            raise ValueError("HASS_TOKEN is not set in the environment variables")
        hassio_base_url = os.getenv('HASS_BASE_URL')
        if not hassio_base_url:
            raise ValueError("HASS_BASE_URL is not set in the environment variables")        

        headers = {
            "Authorization": f"Bearer {hassio_token}",
            "Content-Type": "application/json",
        }
        data = {
            "entity_id": entity_id,
            **params  # Añadir los parámetros adicionales
        }
        url = f"{hassio_base_url}/api/services/{entity_id.split(".")[0]}/{accion}"

        try:
            response = requests.post(url, headers=headers, data=json.dumps(data), verify=False)
            response.raise_for_status()  # Lanza excepción para códigos de error HTTP (4xx, 5xx)

            if response.status_code == 200:
                return f"Acción {accion} ejecutada correctamente en entidad {entity_id}. Action data: {data}"
            else:
                print(f"Error inesperado: Código de estado {response.status_code}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"Error de solicitud: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error al decodificar JSON: {e}")
            return None

def get_tools(**kwargs):
    return [FunctionTool.from_defaults(HassAction.run_hass_action)]
