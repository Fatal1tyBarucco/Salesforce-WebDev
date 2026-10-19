# Artefatos de Auditoria do Pipeline AI Docs

Quando o pipeline chama o LLM, grava um JSON por execução em `docs/.ai-logs/`. O registro contém timestamp, identificador do modelo, uso de tokens/custo informado pelo provedor, prompts, respostas brutas quando disponíveis, classificação e documentos validados, diff documental e, em caso de falha, tipo e mensagem do erro acompanhados da cadeia de exceções sanitizada (tipo, status HTTP e erro do provedor), sem chaves de API, prompts nem conteúdo sensível.

As execuções no GitHub Actions publicam `docs/.ai-logs/` como artefato privado do run, com retenção configurada para 30 dias. Os arquivos de auditoria não são adicionados ao commit de documentação. Eles podem conter trechos de commits, PRs e diffs; trate-os como dados internos e nunca inclua credenciais nesses conteúdos.

Execuções sem mudanças relevantes não chamam o LLM nem criam registros. Uma falha depois de iniciar uma chamada grava um registro de falha sempre que possível; o workflow continua falhando e não publica documentação parcial.
