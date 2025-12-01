import logging
import os
from typing import Any, Dict, Iterable, List, Optional, Union

import requests

logger = logging.getLogger(__name__)


class WakfuClient:
    """
    Client WakStuff : récupère la version courante via config.json,
    puis télécharge items.json pour cette version.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: int = 20,
        session: Optional[requests.Session] = None,
    ) -> None:
        # URL de base stable
        self.base_url = (
            base_url
            or os.getenv(
                "WAKFU_GAMEDATA_BASE_URL", "https://wakfu.cdn.ankama.com/gamedata"
            )
        ).rstrip("/")

        self.timeout = timeout
        self.session = session or requests.Session()
        
        # Headers pour éviter les 403 Forbidden du CDN Ankama
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': 'https://www.wakfu.com/',
            'Origin': 'https://www.wakfu.com'
        })

    @property
    def config_url(self) -> str:
        return f"{self.base_url}/config.json"

    def _get_json(self, url: str) -> Union[List[Any], Dict[str, Any]]:
        logger.info("GET %s", url)
        resp = self.session.get(url, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def get_current_version(self) -> str:
        """
        Lit config.json et en déduit la version de gamedata.
        On ne suppose pas le nom exact de la clé : on teste quelques variantes.
        """
        config = self._get_json(self.config_url)

        if not isinstance(config, dict):
            raise ValueError("Format inattendu pour config.json (dict attendu).")

        candidates = [
            config.get("version"),
            config.get("gameDataVersion"),
            config.get("gamedataVersion"),
            config.get("dataVersion"),
        ]

        for candidate in candidates:
            if isinstance(candidate, str) and candidate.strip():
                version = candidate.strip()
                logger.info("Version Wakfu détectée depuis config.json : %s", version)
                return version

        raise ValueError("Impossible de déterminer la version dans config.json")

    def fetch_all_items(self, version: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Récupère items.json pour la version donnée.
        Si version=None, lit d'abord la version courante via config.json.
        """
        game_version = version or self.get_current_version()
        items_url = f"{self.base_url}/{game_version}/items.json"

        data = self._get_json(items_url)

        if isinstance(data, list):
            return data

        if isinstance(data, dict):
            maybe_items = data.get("items") or data.get("data")
            if isinstance(maybe_items, list):
                return maybe_items

        raise ValueError(
            "Format inattendu pour items.json (ni liste ni dict['items'])."
        )

    def iter_all_items(self, version: Optional[str] = None) -> Iterable[Dict[str, Any]]:
        """
        Itérateur sur tous les items JSON pour une version donnée (ou la version courante).
        """
        for item in self.fetch_all_items(version=version):
            if isinstance(item, dict):
                yield item
            else:
                logger.warning("Item non dict ignoré: %r", item)

    def _fetch_resource(
        self, resource_name: str, version: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Méthode générique pour récupérer n'importe quelle ressource JSON de l'API Wakfu.
        Ex: actions.json, states.json, jobs.json, itemTypes.json, recipeCategories.json, etc.
        """
        game_version = version or self.get_current_version()
        resource_url = f"{self.base_url}/{game_version}/{resource_name}"

        data = self._get_json(resource_url)

        if isinstance(data, list):
            return data

        if isinstance(data, dict):
            # Certains fichiers ont un wrapper
            for key in ["items", "data", "definitions", resource_name.replace(".json", "")]:
                maybe_data = data.get(key)
                if isinstance(maybe_data, list):
                    return maybe_data

        raise ValueError(
            f"Format inattendu pour {resource_name} (ni liste ni dict exploitable)."
        )

    def fetch_all_actions(self, version: Optional[str] = None) -> List[Dict[str, Any]]:
        """Récupère actions.json pour décoder les effets."""
        return self._fetch_resource("actions.json", version)

    def fetch_all_states(self, version: Optional[str] = None) -> List[Dict[str, Any]]:
        """Récupère states.json pour les états/buffs/debuffs."""
        return self._fetch_resource("states.json", version)

    def fetch_all_jobs(self, version: Optional[str] = None) -> List[Dict[str, Any]]:
        """Récupère jobs.json pour les métiers."""
        return self._fetch_resource("jobs.json", version)

    def fetch_all_item_types(self, version: Optional[str] = None) -> List[Dict[str, Any]]:
        """Récupère itemTypes.json pour la classification des items."""
        return self._fetch_resource("itemTypes.json", version)

    def fetch_all_recipe_categories(
        self, version: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Récupère recipeCategories.json pour les recettes de craft."""
        return self._fetch_resource("recipeCategories.json", version)

    def fetch_all_recipes(self, version: Optional[str] = None) -> List[Dict[str, Any]]:
        """Récupère recipes.json pour les recettes de craft."""
        return self._fetch_resource("recipes.json", version)

    def fetch_all_equipments(self, version: Optional[str] = None) -> List[Dict[str, Any]]:
        """Récupère equipments.json si disponible."""
        return self._fetch_resource("equipments.json", version)

    def fetch_all_resources(self, version: Optional[str] = None) -> List[Dict[str, Any]]:
        """Récupère resources.json si disponible."""
        return self._fetch_resource("resources.json", version)
