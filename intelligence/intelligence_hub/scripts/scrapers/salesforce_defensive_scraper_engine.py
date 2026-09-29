# Arquitetura de Extração (SoC) — Salesforce Intelligence Hub
# Este módulo NÃO injeta README. Apenas extrai, valida e converte.
# Nomes completos. Nenhuma abreviação.

from typing import Optional, Dict, List, Any
from urllib.parse import urlparse, parse_qs

# Defensivo: importações opcionais tratadas com None
try:
    import requests
except Exception:
    requests = None  # type: ignore[assignment]

try:
    from bs4 import BeautifulSoup
except Exception:
    BeautifulSoup = None  # type: ignore[assignment, misc]


class SalesforceStatusScraperEngineDefensive:
    """Motor defensivo para extração do Salesforce Status."""

    def __init__(self, target_status_url: str) -> None:
        if not target_status_url or not isinstance(target_status_url, str):
            raise ValueError("target_status_url deve ser string não nula.")
        self.target_status_url: str = target_status_url
        self.parsed_release_number: Optional[str] = None

    def extract_release_identifier_from_url(self) -> Optional[str]:
        """Identifica dinamicamente o número da release a partir de query params."""
        try:
            parsed_url = urlparse(self.target_status_url)
            # Para status.salesforce.com não temos release, mas mantemos a validação defensiva
            query_dictionary: Dict[str, List[str]] = parse_qs(parsed_url.query)
            # Se houver parâmetro release, retornamos; senão None defensivo
            release_list = query_dictionary.get("release", [])
            if release_list and len(release_list) > 0 and release_list[0] is not None:
                self.parsed_release_number = release_list[0]
                return self.parsed_release_number
        except Exception:
            # Captura Timeout, ValueError, KeyError de forma defensiva
            pass
        return None

    def retrieve_html_content_defensive(self, connection_timeout: int = 30) -> Optional[str]:
        """Recupera HTML com tratamento defensivo de Timeout e HTTPError."""
        if requests is None:
            print("[DEFENSIVO] requests não disponível.")
            return None
        try:
            response_object = requests.get(
                self.target_status_url,
                timeout=connection_timeout,
                headers={
                    "User-Agent": (
                        "Salesforce-Intelligence-Hub-Defensive-Scraper/1.0 "
                        "(Enterprise-DevOps-Automation; +https://github.com/Fatal1tyBarucco/Salesforce-WebDev)"
                    )
                },
            )
            response_object.raise_for_status()
            return response_object.text
        except Exception as exception_instance:
            print(f"[DEFENSIVO] Falha de conexão/Timeout ao consultar status: {exception_instance}")
            return None


class ChangeLogDefensiveParserEngine:
    """Parser defensivo para o Change Log da Release (ex: release=264)."""

    def __init__(self, change_log_source_url: str) -> None:
        self.change_log_source_url: str = change_log_source_url
        self.release_identifier: Optional[str] = None
        self._perform_defensive_extraction()

    def _perform_defensive_extraction(self) -> None:
        try:
            parsed_change_url = urlparse(self.change_log_source_url)
            parsed_query_dictionary = parse_qs(parsed_change_url.query)
            release_identifier_list = parsed_query_dictionary.get("release", [])
            if release_identifier_list and len(release_identifier_list) > 0:
                self.release_identifier = release_identifier_list[0]
        except Exception:
            self.release_identifier = None

    def parse_change_log_document_nodes(self, html_content_string: Optional[str]) -> List[Dict[str, Any]]:
        """Parseia nós HTML sem gerar exceções obstrutivas."""
        results_list: List[Dict[str, Any]] = []
        if html_content_string is None:
            return results_list
        if BeautifulSoup is None:
            return results_list
        try:
            soup_document = BeautifulSoup(html_content_string, "html.parser")
            # Exemplo defensivo: captura de nós <article>, <section>, <table>
            for document_node in soup_document.find_all(["article", "section", "table"]):
                node_text_content = document_node.get_text(separator=" ", strip=True)
                if node_text_content and len(node_text_content) > 50:
                    results_list.append({
                        "element_tag_name": document_node.name,
                        "element_text_preview": node_text_content[:500],
                    })
        except Exception:
            pass
        return results_list


class ReleaseNotesHomeDefensiveParserEngine:
    """Parser defensivo para Home das Release Notes."""

    def __init__(self, release_notes_home_url_string: str) -> None:
        self.release_notes_home_url_string: str = release_notes_home_url_string
        self.release_identifier: Optional[str] = None
        self.language_parameter: Optional[str] = None
        self._perform_defensive_extraction()

    def _perform_defensive_extraction(self) -> None:
        try:
            parsed_home_url = urlparse(self.release_notes_home_url_string)
            query_dictionary = parse_qs(parsed_home_url.query)
            release_identifier_list = query_dictionary.get("release", [])
            if release_identifier_list and len(release_identifier_list) > 0:
                self.release_identifier = release_identifier_list[0]
            language_parameter_list = query_dictionary.get("language", [])
            if language_parameter_list and len(language_parameter_list) > 0:
                self.language_parameter = language_parameter_list[0]
        except Exception:
            self.release_identifier = None
            self.language_parameter = None
