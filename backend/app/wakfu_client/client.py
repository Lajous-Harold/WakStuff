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
