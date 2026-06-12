# Apex — Summer '26

> **Release:** Summer '26
> **Gerado em:** 2026-06-12 21:37 UTC
> **Fonte:** https://help.salesforce.com/s/articleView?id=release-notes.salesforce_release_notes.htm&release=262&type=5&language=pt_BR

---

## Apex — Summer '26



### Atualize o Apex code e os fluxos para alterar o comportamento de...

Para otimizar o desempenho após atualizações em grande escala em grupos ou papéis, o Salesforce agora realiza alguns recálculos de compartilhamento de modo assíncrono. Se o Apex code e os fluxos exigirem que os registros de compartilhamento sejam atualizados imediatamente, o código e os fluxos poderão ser interrompidos quando essa atualização de versão for imposta. Atualize classes, testes e fluxos do Apex que atualizam a associação ao grupo ou papéis se eles dependem de recálculo de compartilhamento síncrono. Essa atualização foi disponibilizada inicialmente na versão Spring '26.


[🔗 Leia mais no conteúdo original](https://help.salesforce.com/s/articleView?id=release-notes.rn_sharing_apex_recalc_ru.htm&language=pt_BR&release=262&type=5)



### Operações de banco de dados são executadas no modo de usuário por...

Aproveite um modelo de segurança do Apex aprimorado que protege seus dados através da imposição de acesso em nível de objeto e campo padrão. Operações de banco de dados do Apex, como consultas SOSL e SOQL, instruções DML e métodos de banco de dados, agora são executadas no modo de usuário por padrão. No modo de usuário, as operações de banco de dados aplicam as regras de compartilhamento, a segurança em nível de campo e as permissões de objeto do usuário atual. Em versões anteriores da API, as operações de banco de dados usam como padrão o modo do sistema, o que significa que o usuário atual pode acessar todos os dados independentemente de suas permissões.


[🔗 Leia mais no conteúdo original](https://help.salesforce.com/s/articleView?id=release-notes.rn_apex_default_user_mode.htm&language=pt_BR&release=262&type=5)



### Classes do Apex aplicam regras de compartilhamento por padrão

Aproveite um modelo de segurança do Apex aprimorado que protege seus dados por meio da imposição de acesso de registro padrão. Classes do Apex sem uma declaração de compartilhamento explícita agora usam como padrão o modo with sharing, que aplica configurações de compartilhamento para toda a organização e regras de compartilhamento personalizadas. Em versões anteriores da API, classes do Apex sem uma declaração de compartilhamento explícita usam como padrão o modo without sharing, com algumas exceções. O modo without sharing ignora as regras de compartilhamento e permite que o usuário atual acesse todos os registros.


[🔗 Leia mais no conteúdo original](https://help.salesforce.com/s/articleView?id=release-notes.rn_apex_default_enforce_sharing.htm&language=pt_BR&release=262&type=5)



### A cláusula SOQL WITH SECURITY_ENFORCED foi removida

Para executar uma consulta SOQL ou SOSL no modo de usuário, use a cláusula WITH USER_MODE em vez da cláusula WITH SECURITY_ENFORCED. Classes do Apex definidas como a API versão 67.0 e posterior que incluem WITH SECURITY_ENFORCED não são compiladas.


[🔗 Leia mais no conteúdo original](https://help.salesforce.com/s/articleView?id=release-notes.rn_apex_removed_withSecurityEnforced.htm&language=pt_BR&release=262&type=5)



### Acionadores do Apex sempre são executados no modo do sistema

Os acionadores do Apex agora sempre são executados no modo do sistema, o que significa que ignoram as regras de compartilhamento, a segurança em nível de campo e as permissões de objeto do usuário atual. Antes, acionadores aninhados impedia regras de compartilhamento em determinados casos de borda. Não é possível declarar acionadores do Apex com modos de compartilhamento ou acesso explícitos. Em vez disso, para aplicar as configurações de acesso a dados, delegue a lógica de negócios para separar manipuladores de acionador, em que você pode definir os modos de compartilhamento e acesso.


[🔗 Leia mais no conteúdo original](https://help.salesforce.com/s/articleView?id=release-notes.rn_apex_triggers_system_mode.htm&language=pt_BR&release=262&type=5)



### Escrever testes de integração para Agentforce e Data 360 no Apex...

Escreva testes do Apex completos que fazem chamadas para o Agentforce e o Data 360. Os testes de integração relaxam as restrições de chamadas e a semântica de reversão de transações, para que você possa validar interações reais de serviço e afirmar efeitos colaterais reais em sua organização teste, sem chamadas simuladas.


[🔗 Leia mais no conteúdo original](https://help.salesforce.com/s/articleView?id=release-notes.rn_apex_integrations_testing.htm&language=pt_BR&release=262&type=5)



### Evite interrupções de fluxo de trabalho habilitando limites...

Evite falhas de execução abruptas e limite as exceções se sua organização exceder seu limite diário de trabalho assíncrono. Agora você pode colocar em fila trabalhos de método enfileiráveis e futuros até um novo limite elástico, que é o dobro do limite diário licenciado da sua organização. Os trabalhos assíncronos que excedem o limite diário licenciado são processados a uma taxa limitada.


[🔗 Leia mais no conteúdo original](https://help.salesforce.com/s/articleView?id=release-notes.rn_apex_elastic_async_limit.htm&language=pt_BR&release=262&type=5)



### Bloquear a execução de código anônimo do Apex de pacotes gerenciados...

Para reforçar a segurança da organização assinante, bloqueie IDs de sessão de pacote gerenciado de autenticar código do Apex anônimo. Se você habilitar essa atualização, os pacotes gerenciados instalados não poderão mais usar o UserInfo.getSessionId() para obter um ID da sessão e, em seguida, usar o ID da sessão para executar o Apex anônimo.


[🔗 Leia mais no conteúdo original](https://help.salesforce.com/s/articleView?id=release-notes.rn_apex_block_exec_anon_ru.htm&language=pt_BR&release=262&type=5)


