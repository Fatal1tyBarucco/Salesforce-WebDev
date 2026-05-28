"""
scraper.py — Extrator HTTP resiliente para as Release Notes do Salesforce.

Estratégia de resiliência:
  - Backoff exponencial com jitter entre tentativas.
  - Validação de payload antes de retornar conteúdo.
  - Logs detalhados em cada etapa do ciclo de requisição.
"""

import logging
import random
import time
from typing import Optional

import requests
from bs4 import BeautifulSoup

from config import (
    BASE_URL,
    MAX_RETRY_ATTEMPTS,
    REQUEST_TIMEOUT_SECONDS,
    RETRY_BASE_DELAY_SECONDS,
    USER_AGENT,
    ReleaseInfo,
)

logger: logging.Logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Tipos auxiliares
# ---------------------------------------------------------------------------

RawHtmlContent = str  # alias semântico para HTML bruto retornado


# ---------------------------------------------------------------------------
# Scraper
# ---------------------------------------------------------------------------

class SalesforceReleaseScraper:
    """
    Responsável por buscar o HTML bruto das Release Notes do Salesforce.

    Cada instância mantém uma sessão HTTP persistente com headers padronizados,
    reutilizando conexões TCP e controlando timeouts de forma centralizada.
    """

    def __init__(self) -> None:
        self._session: requests.Session = self._build_session()

    # ------------------------------------------------------------------
    # Interface Pública
    # ------------------------------------------------------------------

    def fetch(self, release: ReleaseInfo) -> Optional[BeautifulSoup]:
        """
        Busca e parseia o HTML de uma release específica.

        Args:
            release: Metadados da release a ser buscada.

        Returns:
            Objeto BeautifulSoup com o DOM parseado, ou None em caso de falha
            após todos os retries.
        """
        url: str = BASE_URL.format(release_id=release.release_id)
        logger.info(
            "[SCRAPER] Iniciando extração | release=%s | url=%s",
            release.name,
            url,
        )

        raw_html: Optional[RawHtmlContent] = self._fetch_with_retry(url, release.name)

        if raw_html is None:
            logger.error(
                "[SCRAPER] Falha definitiva na extração | release=%s",
                release.name,
            )
            return None

        if not self._is_valid_payload(raw_html, release.name):
            return None

        soup: BeautifulSoup = BeautifulSoup(raw_html, "html.parser")
        logger.info(
            "[SCRAPER] HTML parseado com sucesso | release=%s | tamanho=%d bytes",
            release.name,
            len(raw_html),
        )
        return soup

    def close(self) -> None:
        """Encerra a sessão HTTP de forma explícita."""
        self._session.close()
        logger.debug("[SCRAPER] Sessão HTTP encerrada.")

    # ------------------------------------------------------------------
    # Métodos Privados
    # ------------------------------------------------------------------

    def _build_session(self) -> requests.Session:
        """Cria sessão HTTP com headers padrão e configuração de retry no nível do adapter."""
        session = requests.Session()
        session.headers.update(
            {
                "User-Agent": USER_AGENT,
                "Accept": "text/html,application/xhtml+xml",
                "Accept-Language": "en-US,en;q=0.9",
            }
        )
        return session

    def _fetch_with_retry(
        self,
        url: str,
        release_name: str,
    ) -> Optional[RawHtmlContent]:
        """
        Executa a requisição HTTP com backoff exponencial e jitter.

        Delay entre tentativas: (2^attempt + jitter_aleatório) segundos.
        Isso evita thundering herd em caso de múltiplas execuções paralelas.
        """
        last_exception: Optional[Exception] = None

        for attempt in range(1, MAX_RETRY_ATTEMPTS + 1):
            logger.info(
                "[SCRAPER] Tentativa %d/%d | release=%s",
                attempt,
                MAX_RETRY_ATTEMPTS,
                release_name,
            )
            try:
                response: requests.Response = self._session.get(
                    url,
                    timeout=REQUEST_TIMEOUT_SECONDS,
                    allow_redirects=True,
                )
                response.raise_for_status()
                logger.info(
                    "[SCRAPER] Resposta HTTP %d recebida | release=%s",
                    response.status_code,
                    release_name,
                )
                return response.text

            except requests.exceptions.Timeout as exc:
                logger.warning(
                    "[SCRAPER] Timeout na tentativa %d | release=%s | erro=%s",
                    attempt,
                    release_name,
                    exc,
                )
                last_exception = exc

            except requests.exceptions.HTTPError as exc:
                status_code: int = exc.response.status_code if exc.response else 0
                logger.warning(
                    "[SCRAPER] Erro HTTP %d na tentativa %d | release=%s",
                    status_code,
                    attempt,
                    release_name,
                )
                # Não faz retry para erros 4xx (client errors)
                if exc.response is not None and 400 <= exc.response.status_code < 500:
                    logger.error(
                        "[SCRAPER] Erro do cliente (%d). Abortando retries | release=%s",
                        exc.response.status_code,
                        release_name,
                    )
                    return None
                last_exception = exc

            except requests.exceptions.RequestException as exc:
                logger.warning(
                    "[SCRAPER] Erro de rede na tentativa %d | release=%s | erro=%s",
                    attempt,
                    release_name,
                    exc,
                )
                last_exception = exc

            if attempt < MAX_RETRY_ATTEMPTS:
                delay: float = (RETRY_BASE_DELAY_SECONDS ** attempt) + random.uniform(0, 1)
                logger.info(
                    "[SCRAPER] Aguardando %.2fs antes do próximo retry | release=%s",
                    delay,
                    release_name,
                )
                time.sleep(delay)

        logger.error(
            "[SCRAPER] Esgotadas %d tentativas | release=%s | último_erro=%s",
            MAX_RETRY_ATTEMPTS,
            release_name,
            last_exception,
        )
        return None

    def _is_valid_payload(self, html: RawHtmlContent, release_name: str) -> bool:
        """
        Valida se o HTML retornado contém conteúdo mínimo esperado.
        Evita processar páginas de erro ou redirecionamentos silenciosos.
        """
        minimum_length: int = 500  # bytes mínimos para um payload válido

        if len(html) < minimum_length:
            logger.error(
                "[SCRAPER] Payload muito pequeno (%d bytes) | release=%s",
                len(html),
                release_name,
            )
            return False

        # Verifica marcadores conhecidos de páginas de erro do Salesforce
        error_indicators: list[str] = [
            "Page Not Found",
            "This page doesn't exist",
            "Something went wrong",
        ]
        for indicator in error_indicators:
            if indicator.lower() in html.lower():
                logger.error(
                    "[SCRAPER] Página de erro detectada ('%s') | release=%s",
                    indicator,
                    release_name,
                )
                return False

        return True
