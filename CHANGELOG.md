# Changelog

## v3.1.0 — Refatoração de Testes e Correções

### ✅ Melhorias

- **Cobertura de testes:** 70% → 96% (4129 statements, 177 remaining)
- **Testes:** 371 → 704 funções de teste (479 passando no CI)
- **Módulos em 100%:** 9 → 21 arquivos com cobertura total
- **Correções de sintaxe:** Erros Python 2→3 em 15 arquivos fonte
- **Bug fix:** Regex GraphQL em `src/api.py` não considerava seleção de campos `{ ... }`
- **CI:** Threshold de cobertura ajustado para 95%

### 📁 Novos arquivos de teste

- `tests/test_analytics.py` — Cobertura para `src/analytics.py`
- `tests/test_api_coverage.py` — Cobertura para `src/api.py`
- `tests/test_dashboard.py` — Cobertura para `src/dashboard.py`
- `tests/test_health.py` — Cobertura para `src/health.py`
- `tests/test_main_extra.py` — Cobertura adicional para `src/main.py`
- `tests/test_notifications.py` — Cobertura para `src/notifications.py`
- `tests/test_salesforce_coverage.py` — Cobertura para `src/salesforce.py`
- `tests/test_scraper_coverage.py` — Cobertura para `src/scraper.py`
- `tests/test_workflow.py` — Cobertura para `src/workflow.py`

### 🔧 Arquivos expandidos

- `tests/test_impact_analyzer.py` — Testes adicionais para `except` branch
- `tests/test_src_logger.py` — Refatorado para cobertura completa
- `tests/test_config.py` — Testes para `build_release_info`, `_id_to_season`
- `tests/test_llm_service.py` — Teste para resposta não-padrão do OpenAI
- `tests/test_src_parser.py` — Testes para `FeatureImpactParser`
- `tests/test_ai_automation.py` — Testes para funções wrapper de nível de módulo

## Summer '26

**1373 recursos** em 22 categorias

- **Documentação legal**: 6 recursos
- **Salesforce geral**: 36 recursos
- **Agentforce**: 37 recursos
- **Análise de dados**: 58 recursos
- **Automação**: 118 recursos
- **OmniStudio**: 9 recursos
- **Personalização**: 33 recursos
- **Data 360**: 72 recursos
- **Desenvolvimento**: 127 recursos
- **Experience Cloud**: 14 recursos
- **Field Service**: 48 recursos
- **Hyperforce**: 3 recursos
- **Setores**: 309 recursos
- **Marketing**: 64 recursos
- **MuleSoft**: 8 recursos
- **Aplicativo móvel**: 17 recursos
- **Partner Cloud**: 1 recursos
- **Gerenciamento de receita**: 97 recursos
- **Vendas**: 58 recursos
- **Integrações do Salesforce para Slack**: 2 recursos
- **Segurança, identidade e privacidade**: 58 recursos
- **Serviço**: 198 recursos

## Spring '26

**1438 recursos** em 21 categorias

- **Documentação legal**: 6 recursos
- **Salesforce geral**: 38 recursos
- **Agentforce**: 35 recursos
- **Análise de dados**: 54 recursos
- **Automação**: 151 recursos
- **Personalização**: 18 recursos
- **Data 360**: 53 recursos
- **Desenvolvimento**: 97 recursos
- **Experience Cloud**: 21 recursos
- **Field Service**: 41 recursos
- **Hyperforce**: 5 recursos
- **Setores**: 194 recursos
- **Aplicativo móvel**: 187 recursos
- **Marketing**: 72 recursos
- **MuleSoft**: 8 recursos
- **OmniStudio**: 10 recursos
- **Partner Cloud**: 4 recursos
- **Gerenciamento de receita**: 131 recursos
- **Vendas**: 85 recursos
- **Segurança, identidade e privacidade**: 61 recursos
- **Serviço**: 167 recursos

## Winter '26

**1348 recursos** em 19 categorias

- **Documentação legal**: 11 recursos
- **Salesforce geral**: 32 recursos
- **Análise de dados**: 91 recursos
- **Personalização**: 65 recursos
- **Desenvolvimento**: 101 recursos
- **Agentforce**: 39 recursos
- **Experience Cloud**: 8 recursos
- **Field Service**: 24 recursos
- **Hyperforce**: 5 recursos
- **Setores**: 459 recursos
- **Marketing**: 87 recursos
- **MuleSoft**: 4 recursos
- **Aplicativo móvel**: 7 recursos
- **OmniStudio**: 8 recursos
- **Partner Cloud**: 156 recursos
- **Vendas**: 154 recursos
- **Integrações do Salesforce para Slack**: 1 recursos
- **Segurança, identidade e privacidade**: 55 recursos
- **Serviço**: 41 recursos
