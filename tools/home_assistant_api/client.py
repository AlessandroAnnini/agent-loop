from typing import Dict, List, Optional, Any
import requests
from .entity_state import EntityState


class HassClient:
    """Handles direct interactions with Home Assistant REST API."""

    def __init__(self, base_url: str, access_token: str):
        """Initialize Home Assistant API client.

        Args:
            base_url: Home Assistant instance URL (e.g., 'http://localhost:8123')
            access_token: Long-lived access token from Home Assistant
        """
        self.base_url = base_url.rstrip("/")
        self.headers = {"authorization": f"Bearer {access_token}"}

    def get_all_states(self) -> List[EntityState]:
        """Retrieve states of all entities from Home Assistant.

        Returns:
            List of EntityState objects representing current states

        Raises:
            requests.exceptions.RequestException: If API request fails
        """

        url = f"{self.base_url}/api/states"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()

        all_states = response.json()

        whitelist_entities_types = ["weather", "switch", "light", "climate", "todo"]

        whitelisted_states = []
        for state in all_states:
            state_type = state["entity_id"].split(".")[0]
            if state_type in whitelist_entities_types:
                new_state = EntityState(
                    entity_id=state["entity_id"],
                    state=state["state"],
                    attributes=state.get("attributes", {}),
                )
                whitelisted_states.append(new_state)

        return whitelisted_states

    def get_services(self) -> List[Dict[str, Any]]:
        """Retrieve available services from Home Assistant.

        Returns:
            List of dictionaries containing domain and available services.
            Each dictionary has format: {
                "domain": str,
                "services": List[str]
            }

        Raises:
            requests.exceptions.RequestException: If API request fails
        """
        url = f"{self.base_url}/api/services"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        all_services = response.json()

        services_whitelist = ["light", "shopping_list", "switch", "netatmo"]

        whitelisted_services = []
        for service in all_services:
            if service["domain"] in services_whitelist:
                whitelisted_services.append(service)

        return whitelisted_services

    def call_service(
        self, domain: str, service: str, service_data: Optional[Dict[str, Any]] = None
    ) -> List[EntityState]:
        """Call a Home Assistant service.

        Args:
            domain: The domain of the service (e.g., 'light', 'switch')
            service: The service to call (e.g., 'turn_on', 'turn_off')
            service_data: Optional dictionary containing service call parameters

        Returns:
            List of EntityState objects representing states that changed during service execution

        Raises:
            requests.exceptions.RequestException: If API request fails
        """
        url = f"{self.base_url}/api/services/{domain}/{service}"
        response = requests.post(url, headers=self.headers, json=service_data or {})
        response.raise_for_status()

        return [
            EntityState(
                entity_id=state["entity_id"],
                state=state["state"],
                attributes=state.get("attributes", {}),
            )
            for state in response.json()
        ]

    def update_entity_state(
        self, entity_id: str, state: str, attributes: Optional[Dict[str, Any]] = None
    ) -> EntityState:
        """Update state and attributes of a specific entity.

        Args:
            entity_id: Entity ID to update (e.g., 'light.living_room')
            state: New state value
            attributes: Optional dict of attributes to update

        Returns:
            Updated entity state

        Raises:
            requests.exceptions.RequestException: If API request fails
        """
        payload = {"state": state}

        if attributes:
            payload["attributes"] = attributes

        response = requests.post(
            f"{self.base_url}/api/states/{entity_id}",
            json=payload,
            headers=self.headers,
        )
        response.raise_for_status()
        result = response.json()

        return EntityState(
            entity_id=result["entity_id"],
            state=result["state"],
            attributes=result.get("attributes", {}),
        )
