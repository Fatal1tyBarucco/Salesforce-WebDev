import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, patch

from src.translator import TranslatorService


def test_translate_feature_success(tmp_path: Path) -> None:
    with patch("src.translator.LLMService") as MockLLM:
        mock_llm = MockLLM.return_value
        mock_llm.generate_text = AsyncMock(return_value="Improved voice clarity")

        service = TranslatorService(cache_dir=str(tmp_path))
        result = asyncio.run(service.translate_feature("Transcrição mais nítida", "pt_BR", "en_US"))
        assert result == "Improved voice clarity"


def test_translate_feature_fallback(tmp_path: Path) -> None:
    with patch("src.translator.LLMService") as MockLLM:
        mock_llm = MockLLM.return_value
        mock_llm.generate_text = AsyncMock(return_value=None)

        service = TranslatorService(cache_dir=str(tmp_path))
        result = asyncio.run(service.translate_feature("Texto original", "pt_BR", "en_US"))
        assert result == "Texto original"


def test_translate_batch_success(tmp_path: Path) -> None:
    with patch("src.translator.LLMService") as MockLLM:
        mock_llm = MockLLM.return_value
        mock_llm.generate_text = AsyncMock(side_effect=["Feature A", "Feature B"])

        service = TranslatorService(cache_dir=str(tmp_path))
        results = asyncio.run(
            service.translate_batch(["Funcionalidade A", "Funcionalidade B"], "pt_BR", "en_US")
        )
        assert len(results) == 2
        assert results[0] == "Feature A"
        assert results[1] == "Feature B"


def test_translate_category(tmp_path: Path) -> None:
    with patch("src.translator.LLMService") as MockLLM:
        mock_llm = MockLLM.return_value
        mock_llm.generate_text = AsyncMock(return_value="Security")

        service = TranslatorService(cache_dir=str(tmp_path))
        result = asyncio.run(service.translate_category("Segurança", "pt_BR", "en_US"))
        assert result == "Security"


def test_cache_hit(tmp_path: Path) -> None:
    with patch("src.translator.LLMService") as MockLLM:
        mock_llm = MockLLM.return_value
        mock_llm.generate_text = AsyncMock(return_value="Cached result")

        service = TranslatorService(cache_dir=str(tmp_path))
        asyncio.run(service.translate_feature("Test text", "pt_BR", "en_US"))
        result = asyncio.run(service.translate_feature("Test text", "pt_BR", "en_US"))
        assert result == "Cached result"
        assert mock_llm.generate_text.call_count == 1


def test_same_locale_no_translation(tmp_path: Path) -> None:
    service = TranslatorService(cache_dir=str(tmp_path))
    result = asyncio.run(service.translate_feature("Already English", "en_US", "en_US"))
    assert result == "Already English"


def test_load_cache_invalid_json(tmp_path: Path) -> None:
    cache_file = tmp_path / ".translation_cache.json"
    cache_file.write_text("not valid json {{{")
    service = TranslatorService(cache_dir=str(tmp_path))
    assert service._cache == {}


def test_load_cache_os_error(tmp_path: Path) -> None:
    cache_file = tmp_path / ".translation_cache.json"
    cache_file.write_text('{"key": "value"}')
    cache_file.chmod(0o000)
    try:
        service = TranslatorService(cache_dir=str(tmp_path))
        assert service._cache == {}
    finally:
        cache_file.chmod(0o644)


def test_cache_expiration(tmp_path: Path) -> None:
    import time

    with patch("src.translator.LLMService") as MockLLM:
        mock_llm = MockLLM.return_value
        mock_llm.generate_text = AsyncMock(return_value="Translated")

        service = TranslatorService(cache_dir=str(tmp_path))
        asyncio.run(service.translate_feature("Test", "pt_BR", "en_US"))

        key = service._cache_key("Test", "pt_BR", "en_US")
        service._cache[key]["timestamp"] = time.time() - (8 * 24 * 60 * 60)
        result = asyncio.run(service.translate_feature("Test", "pt_BR", "en_US"))
        assert result == "Translated"
        assert mock_llm.generate_text.call_count == 2
