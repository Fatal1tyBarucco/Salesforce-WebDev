# Integrações & APIs — Summer '25

> **Release:** Summer '25
> **Gerado em:** 2026-06-12 21:02 UTC
> **Fonte:** https://help.salesforce.com/s/articleView?id=release-notes.salesforce_release_notes.htm&release=256&type=5&language=pt_BR

---

## Integrações & APIs — Summer '25



### Corpos de solicitação da API REST do Connect alterados

Resumo não disponível para este artigo.


[🔗 Leia mais no conteúdo original](https://help.salesforce.com/s/articleView?id=release-notes.rn_ls_connect_api_request.htm&language=pt_BR&release=256&type=5)



### A documentação da API do carrinho do Salesforce para Comércio está...

A documentação da API do Cart Connect agora está no Guia do desenvolvedor do B2B Commerce e do D2C Commerce. Foi documentado anteriormente no Guia do desenvolvedor da API REST do Connect. As informações de referência agora seguem os padrões de Especificação OpenAPI (OAS) para APIs REST.


[🔗 Leia mais no conteúdo original](https://help.salesforce.com/s/articleView?id=release-notes.rn_cart_api_doc.htm&language=pt_BR&release=256&type=5)



### Localize a documentação da API de Pagamentos do Salesforce em um...

A API Payments Connect, anteriormente documentada no Guia do desenvolvedor da API REST do Connect, foi movida para o Guia do desenvolvedor do B2B Commerce e do D2C Commerce. Além disso, as informações de referência agora seguem os padrões de Especificação OpenAPI (OAS) para APIs REST.


[🔗 Leia mais no conteúdo original](https://help.salesforce.com/s/articleView?id=release-notes.rn_payments_api_doc.htm&language=pt_BR&release=256&type=5)



### Realizar atualizações de registro parciais usando a API de ingestão...

Agora você pode atualizar um registro ingerido anteriormente usando a API de ingestão de streaming. Para fazer uma atualização parcial, inclua a chave primária do registro na sua solicitação, forneça um valor para o registro modificado arquivado e especifique os campos que precisam de atualização. O Data Cloud atualiza apenas os campos incluídos na carga útil e deixa os outros campos inalterados, desde que o valor do campo Registro modificado seja mais recente que o valor atual.


[🔗 Leia mais no conteúdo original](https://help.salesforce.com/s/articleView?id=release-notes.rn_cdp_2025_summer_ingestion_api_partial_updates.htm&language=pt_BR&release=256&type=5)



### Usar o URL de login do Meu domínio da sua organização em chamadas à...

Essa atualização foi cancelada. Ele é substituído pela atualização de versão Atualizar URLs instanciados no tráfego da API.


[🔗 Leia mais no conteúdo original](https://help.salesforce.com/s/articleView?id=release-notes.rn_api_my_domain_login_url_in_api_calls.htm&language=pt_BR&release=256&type=5)



### Atualizar URLs instanciados no tráfego de API

Para evitar interrupções quando o Salesforce encerrar o suporte para tráfego de API que use um URL instanciado incorreto, certifique-se de que o tráfego de API para sua organização use o URL de login do Meu domínio da organização. Essa atualização está disponível da versão Summer '25 em diante.


[🔗 Leia mais no conteúdo original](https://help.salesforce.com/s/articleView?id=release-notes.rn_update_instanced_urls_in_api_traffic.htm&language=pt_BR&release=256&type=5)



### Descontinuação da API da Salesforce Platform versões 21.0 a 30.0...

A descontinuação das versões 21.0 a 30.0 da API da Salesforce Platform foi agendada inicialmente para a versão Summer '23. A descontinuação agora é adiada para a versão Summer '25. Essas versões da API não têm suporte e não estarão disponíveis a partir da versão Summer '25. Os aplicativos que as consomem são então interrompidos. As solicitações falham com uma mensagem de erro indicando que o ponto de extremidade está desativado. Atualize todos os aplicativos que usam uma versão de API legada para uma versão atual antes que essa mudança ocorra.


[🔗 Leia mais no conteúdo original](https://help.salesforce.com/s/articleView?id=release-notes.rn_api_retirement_delay_256rn.htm&language=pt_BR&release=256&type=5)



### Seja notificado sobre solicitações de API composta com tipos de...

Consulte o objeto EventLogFile para os tipos de evento CompositeApi e CompositeApiSubrequest para obter detalhes sobre solicitações e subsolicitações da API de gráfico composto e API composta.


[🔗 Leia mais no conteúdo original](https://help.salesforce.com/s/articleView?id=release-notes.rn_api_composite_em.htm&language=pt_BR&release=256&type=5)


