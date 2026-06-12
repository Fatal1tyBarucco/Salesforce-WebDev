# Apex — Summer '26

> **Release:** Summer '26
> **Gerado em:** 2026-06-08 02:24 UTC
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


