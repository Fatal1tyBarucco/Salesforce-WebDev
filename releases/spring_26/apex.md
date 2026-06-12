# Apex — Spring '26

> **Release:** Spring '26
> **Gerado em:** 2026-06-08 02:18 UTC
> **Fonte:** https://help.salesforce.com/s/articleView?id=release-notes.salesforce_release_notes.htm&release=260&type=5&language=pt_BR

---

## Apex — Spring '26



### Atualize o Apex code e os fluxos para alterar o comportamento de...

Para otimizar o desempenho após atualizações em grande escala em grupos ou papéis, o Salesforce agora realiza alguns recálculos de compartilhamento de modo assíncrono. Se o Apex code e os fluxos exigirem que os registros de compartilhamento sejam atualizados imediatamente, o código e os fluxos poderão ser interrompidos quando essa atualização de versão for imposta. Atualize classes, testes e fluxos do Apex que atualizam a associação ao grupo ou papéis se eles dependem de recálculo de compartilhamento síncrono. Essa atualização estará disponível da versão Spring '26 em diante.


[🔗 Leia mais no conteúdo original](https://help.salesforce.com/s/articleView?id=release-notes.rn_customization_apex_sharing_ru.htm&language=pt_BR&release=260&type=5)



### Estenda o Data 360 usando código personalizado com extensão de...

Com a extensão de código, você pode levar seu código do Python personalizado para o Data 360 para estender os recursos nativos do Data 360. Se os recursos nativos do Data 360 não atenderem aos seus requisitos de negócios, implemente sua lógica personalizada em recursos compatíveis do Data 360, como transformações de dados em lote. Por exemplo, se você precisar de transformações de dados avançadas para seu caso de uso de negócios, poderá implementar a lógica de negócios personalizada no Data 360 para implementar seus requisitos. O SDK de Código personalizado de dados é o kit de ferramentas para criar e validar código personalizado para extensão de código.


[🔗 Leia mais no conteúdo original](https://help.salesforce.com/s/articleView?id=release-notes.rn_code_extension.htm&language=pt_BR&release=260&type=5)



### Acelere a implantação de dados do Inspetor DX com SOQL

Acelere seu processo de implementação no Inspetor DX usando consultas SELECT para definir os registros que você deseja implementar. Insira as consultas Salesforce Object Query Language (SOQL) para buscar registros e campos específicos da sua organização de origem. Esse recurso é uma alternativa mais rápida aos filtros, permitindo que você busque dados com base em critérios complexos instantaneamente.


[🔗 Leia mais no conteúdo original](https://help.salesforce.com/s/articleView?id=release-notes.rn_data_deployment_with_soql.htm&language=pt_BR&release=260&type=5)


