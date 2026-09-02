# Operações de Workflow

Este documento descreve as operações dos workflows do pipeline no repositório Salesforce-WebDev.

## Pipeline de Notas de Release

O workflow `release_notes_pipeline.yml` é responsável por extrair, processar e publicar as notas de release do Salesforce. Ele é acionado semanalmente ou manualmente e inclui jobs de extração e criação de releases.

### Mudanças Recentes (Reconciliação)

Devido a atualizações no código-fonte, a documentação foi revisada para incluir as seguintes alterações no pipeline:

1. **Processo de Commit**:
   - Antes: Usava `git add releases/ README.md README.en.md` para adicionar apenas caminhos específicos.
   - Agora: Usa `git add -A` para adicionar todas as alterações no diretório de trabalho, e verifica se há commits vazios antes de confirmar (evitando commits desnecessários).
   - Isso garante que todas as mudanças, incluindo logs ou caches intermediários, sejam commitadas de forma consistente.

2. **Token para Criação de Releases**:
   - Antes: Usava exclusivamente `GITHUB_TOKEN`.
   - Agora: Preferencialmente usa `RELEASE_TOKEN` (um PAT com escopo repo) se disponível, senão usa `GITHUB_TOKEN`. Se estiver usando `GITHUB_TOKEN`, um aviso é impresso no log para alertar sobre possíveis restrições de criação de refs (HTTP 422 "Cannot create ref"), conforme issue #112.
   - Recomenda-se configurar `RELEASE_TOKEN` como secret no GitHub para evitar falhas em organizações com restrições.

3. **Formato de Tag para Releases**:
   - Antes: `v{release_id}-{year_short}-{season}` (ex: `v1-26-summer`).
   - Agora: `v{release_id}-{season}-{year_short}` (ex: `v1-summer-26`).
   - Esta mudança unifica o formato e pode afetar scripts ou referências externas que dependem das tags.

4. **Tratamento de Releases Imutáveis**:
   - Agora, antes de tentar atualizar uma release existente, o pipeline verifica se ela é imutável (usando `gh release view` com o campo `isImmutable`).
   - Se imutável, a atualização é pulada com um log, evitando erros HTTP 422.
   - Se não imutável, a release é deletada e recriada normalmente.

5. **Migração Legada Removida**:
   - A lógica para deletar tags legadas no formato `v20{year_short}-{season}` foi removida, simplificando o fluxo.

### Considerações Operacionais

- **Logs**: Os logs do pipeline são armazenados em `/tmp/pipeline_logs/` e podem ser revisados para diagnóstico.
- **Secrets Necessários**: `GITHUB_TOKEN` (padrão) e opcionalmente `RELEASE_TOKEN` para releases. Outros secrets como `GOOGLE_API_KEY` e `OPENROUTER_API_KEY` são usados na extração.
- **Workdir**: O diretório de trabalho padrão é a raiz do repositório (`.`).
- **Timeout**: O job de extração tem timeout de 240 minutos devido à complexidade da extração e processamento.

Para detalhes completos, consulte o arquivo `.github/workflows/release_notes_pipeline.yml` no repositório.
