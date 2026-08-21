# 📋 Plano de Ação: Corrigir Modificação Não Esperada nas Releases

## **🎯 Objetivo**
Corrigir o comportamento do workflow `release.yml` que apagou as **releases antigas** e manteve apenas a última, restaurando o comportamento esperado de **manter todas as releases** e marcar apenas a mais recente como `--latest`.

---

## **🔍 Análise do Problema**

### **1. Causa Raiz**
- O workflow `release.yml` usava a flag `--latest` **incorretamente**, substituindo a release marcada como "latest" no GitHub.
- O comando `gh release create --latest` **apaga automaticamente a marcação `--latest` das outras releases**, mas **não apaga as releases antigas**. No entanto, a lógica de comparação de `release_id` estava **falhando** e sempre marcava a nova release como `--latest`.
- O script de extração de `release_id` do corpo das releases não estava funcionando corretamente, resultando em `MAX_EXISTING=0` e, consequentemente, **todas as novas releases eram marcadas como `--latest`**, substituindo a anterior.

### **2. Impacto**
- **Releases antigas (Summer '26, Spring '26, etc.)** foram **perdidas** como "latest", mas **ainda existem no GitHub** (não foram apagadas).
- O comportamento esperado era **manter todas as releases** e **marcar apenas a mais recente como `--latest`**.

---

## **✅ Soluções Implementadas**

### **1. Correção do Workflow `release.yml`**
- **Adicionado um passo** para capturar **todas as releases existentes** e seus `release_id`s:
  ```yaml
  - name: Get all existing releases and their IDs
    id: get_existing_releases
    env:
      GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    run: |
      EXISTING_RELEASES=$(gh release list --json tagName,body 2>/dev/null)
      EXISTING_IDS=$(echo "$EXISTING_RELEASES" | python3 -c "
      import json, sys, re
      releases = json.load(sys.stdin)
      ids = []
      for release in releases:
          body = release.get('body', '')
          match = re.search(r'release_id.*?(\d+)', body)
          if match:
              ids.append(int(match.group(1)))
      print(' '.join(map(str, ids)) if ids else '0')
      ")
      echo "existing_ids=$EXISTING_IDS" >> $GITHUB_OUTPUT
  ```

- **Corrigida a lógica de `--latest`**:
  ```yaml
  MAX_EXISTING=$(echo "$EXISTING_IDS" | tr ' ' '\n' | sort -n | tail -1 || echo "0")
  if [ -z "$MAX_EXISTING" ] || [ "$RELEASE_ID" -gt "$MAX_EXISTING" ]; then
    IS_LATEST="--latest"
  else
    IS_LATEST=""  # Não usa --latest se não for a maior
  fi
  ```

### **2. Scripts para Restaurar Releases**
- **`scripts/restore_releases.py`**: Script em Python para **restaurar releases apagadas** no GitHub.
- **`scripts/restore_releases.sh`**: Script em Bash para **restaurar releases apagadas** no GitHub.

---

## **🚀 Passos para Executar o Plano de Ação**

### **1. Mesclar o Branch `fix-release-workflow` no `main`**
- **Ações**:
  - Revisar o [PR #76](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/pull/76) (ou criar um novo PR com o branch `fix-release-workflow`).
  - Mesclar as mudanças no `main`.

### **2. Restaurar as Releases Apagadas**
- **Opção 1: Usar o Script Python**
  ```bash
  # Instalar dependências (se necessário)
  pip install pygithub
  
  # Executar o script
  python scripts/restore_releases.py
  ```

- **Opção 2: Usar o Script Bash**
  ```bash
  # Dar permissão de execução
  chmod +x scripts/restore_releases.sh
  
  # Executar o script
  ./scripts/restore_releases.sh
  ```

### **3. Verificar as Releases no GitHub**
- **Ações**:
  - Acessar o repositório no GitHub: [Releases](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/releases).
  - Verificar se **todas as releases** (Summer '26, Spring '26, etc.) estão presentes.
  - Verificar se a **release mais recente está marcada como `--latest`**.

### **4. Testar o Workflow `release.yml`**
- **Ações**:
  - Executar manualmente o workflow **`🚀 Salesforce Release Notes Pipeline`** no GitHub Actions.
  - Verificar se o **`release.yml`** é disparado automaticamente.
  - Verificar se **não apaga releases antigas** e **marca corretamente a mais recente como `--latest`**.

---

## **📌 Verificação Final**

| **Item** | **Status** | **Ação** |
|----------|------------|----------|
| Workflow `release.yml` corrigido | ✅ | Mesclar no `main` |
| Scripts de restauração criados | ✅ | Executar `restore_releases.py` ou `restore_releases.sh` |
| Releases antigas restauradas | ⏳ | Verificar no GitHub |
| Workflow testado | ⏳ | Executar manualmente |

---

## **🔧 Comandos Úteis**

### **1. Listar Releases no GitHub**
```bash
gh release list
```

### **2. Verificar Detalhes de uma Release**
```bash
gh release view v2026-summer
```

### **3. Marcar uma Release como `--latest`**
```bash
gh release edit v2026-summer --latest
```

### **4. Remover a Marcação `--latest` de uma Release**
```bash
gh release edit v2026-summer --latest=false
```

---

## **📝 Notas Adicionais**
- Os scripts **não apagam releases existentes**, apenas recriam as que estão faltando.
- O workflow corrigido **não usa `--latest`** se já houver uma release com `release_id` maior.
- Se o `release_id` não estiver presente no corpo da release, o script assume `0`.

---

## **✨ Resultado Esperado**
- **Todas as releases** (Summer '26, Spring '26, etc.) **restauradas** no GitHub.
- **Apenas a release mais recente marcada como `--latest`**.
- **Workflow `release.yml` funcionando corretamente** sem apagar releases antigas.
