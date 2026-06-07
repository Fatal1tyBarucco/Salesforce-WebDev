import logging
from pathlib import Path
from unittest.mock import MagicMock, patch
import requests
from automation.core.scraper import ReleaseNotesScraper
from automation.shared.config import ApplicationConfig
from automation.shared.file_utils import ensure_directory_exists
from automation.shared.http_client import HttpClient
from automation.shared.logger import build_logger, JsonLikeFormatter


def test_application_config_defaults() -> None:
    config = ApplicationConfig()
    assert config.request_timeout_seconds == 30
    assert config.releases_directory == "releases"


def test_ensure_directory_exists(tmp_path: Path) -> None:
    target_dir = tmp_path / "new_dir" / "nested_dir"
    ensure_directory_exists(str(target_dir))
    assert target_dir.exists()


def test_json_like_formatter() -> None:
    formatter = JsonLikeFormatter()
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="path",
        lineno=10,
        msg="Test message",
        args=(),
        exc_info=None,
    )
    formatted = formatter.format(record)
    assert "[LEVEL=INFO]" in formatted
    assert "[LOGGER=test_logger]" in formatted
    assert "Test message" in formatted


def test_build_logger() -> None:
    logger = build_logger("custom_test_logger")
    assert logger.name == "custom_test_logger"
    assert logger.level == logging.INFO
    assert len(logger.handlers) > 0


@patch("automation.shared.http_client.requests.get")
def test_http_client_get_success(mock_get: MagicMock) -> None:
    mock_response = MagicMock()
    mock_response.text = "HTML Content"
    mock_get.return_value = mock_response

    client = HttpClient()
    result = client.get("https://fake-url.com")

    assert result == "HTML Content"
    mock_get.assert_called_once_with(
        "https://fake-url.com",
        timeout=30,
        headers={"User-Agent": "Salesforce-WebDev-Release-Intelligence"},
    )


@patch("automation.shared.http_client.requests.get")
def test_http_client_get_retries_on_failure(mock_get: MagicMock) -> None:
    # Vamos simular falhas consecutivas e depois um sucesso
    mock_get.side_effect = [
        requests.exceptions.RequestException("Fail 1"),
        requests.exceptions.RequestException("Fail 2"),
        MagicMock(text="Success After Retries"),
    ]

    client = HttpClient()
    # Reduzimos o tempo de espera do retry alterando a configuração do retry se necessário,
    # mas o tenacity usa wait_exponential. 2^1 = 2 segundos de espera.
    # Vamos mockar o sleep interno para o teste rodar rápido
    with patch("time.sleep", return_value=None):
        result = client.get("https://fake-url.com")
        assert result == "Success After Retries"
        assert mock_get.call_count == 3


@patch("automation.core.scraper.HttpClient")
def test_scraper_fetches_release_notes(mock_client_class: MagicMock) -> None:
    mock_client_instance = MagicMock()
    mock_client_instance.get.return_value = "Page Content"
    mock_client_class.return_value = mock_client_instance

    scraper = ReleaseNotesScraper()
    result = scraper.fetch_release_notes()

    assert result == "Page Content"
    mock_client_instance.get.assert_called_once()


def test_build_logger_already_has_handlers() -> None:
    # Chama uma vez para configurar
    build_logger("already_configured_logger")
    # Chama a segunda vez para acionar o retorno rápido de handlers existentes
    logger = build_logger("already_configured_logger")
    assert logger.name == "already_configured_logger"
