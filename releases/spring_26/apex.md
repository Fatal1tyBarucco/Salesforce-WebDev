# Apex — Spring '26

> **Release:** Spring '26
> **Gerado em:** 2026-06-12 21:26 UTC
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



### Faça o escape do atributo de rótulo de elementos <apex:inputField>...

Para evitar a execução de código mal-intencionado em ataques de script entre sites (XSS) em suas páginas do Visualforce, esta atualização de versão escapa ao atributo label das suas tags de <apex:inputField>. Essa atualização foi disponibilizada inicialmente na versão Winter '23.


[🔗 Leia mais no conteúdo original](https://help.salesforce.com/s/articleView?id=release-notes.rn_vf_escape_apex_inputfield_label_ru.htm&language=pt_BR&release=260&type=5)



### Implemente componentes do Apex mais rapidamente executando apenas...

Para reduzir o tempo de implantação do componente Apex, use o novo nível de teste de RunRelevantTests para executar apenas os testes relevantes para suas alterações de código. Esse recurso determina automaticamente quais testes executar com base em uma análise da carga útil da implementação e das dependências da carga útil. Para um controle detalhado, você pode anotar classes de teste para que elas sejam executadas independentemente da carga útil da implementação ou quando os componentes especificados forem novos ou modificados. Essa abordagem direcionada aumenta a velocidade e a confiabilidade da sua implementação enquanto mantém a qualidade do código e os requisitos de cobertura.


[🔗 Leia mais no conteúdo original](https://help.salesforce.com/s/articleView?id=release-notes.rn_apex_run_relevant_tests.htm&language=pt_BR&release=260&type=5)



### Usar cursores do Apex para suporte expandido aos resultados da...

Use cursores do Apex e cursores de paginação para trabalhar com grandes conjuntos de resultados de consulta SOQL em partes gerenciáveis. Esse recurso, agora disponível ao público em geral, inclui aprimoramentos desde a versão beta. Os cursores padrão, quando combinados com o Apex enfileirável, abordam as limitações do Apex em lote. Os cursores de paginação são projetados para elementos da IU, como listas de registros de várias páginas. Ambos os tipos de cursor do Apex podem passar para frente e para trás por conjuntos de resultados e podem lidar com processamento de alto volume e alto recurso.


[🔗 Leia mais no conteúdo original](https://help.salesforce.com/s/articleView?id=release-notes.rn_apex_cursors.htm&language=pt_BR&release=260&type=5)



### Extrair valores da lista de opções com base no tipo de registro

Obtenha os valores de todos os campos da lista de opções para um determinado tipo de registro usando o novo método ConnectApi.RecordUi.getPicklistValuesByRecordType(objectApiName, recordTypeId). Entregamos esse recurso devido à sua ideia no IdeaExchange.


[🔗 Leia mais no conteúdo original](https://help.salesforce.com/s/articleView?id=release-notes.rn_apex_extract_picklist_values.htm&language=pt_BR&release=260&type=5)



### Expor métodos de controlador REST e AuraEnabled do Apex como ações...

Crie ações do agente com base em classes do Apex anotando métodos nessas classes, gerando um documento de especificação OpenAPI e implementando esse documento em sua organização. Gerencie os métodos expostos como APIs no Catálogo de API. Esse recurso agora está disponível ao público em geral.


[🔗 Leia mais no conteúdo original](https://help.salesforce.com/s/articleView?id=release-notes.rn_apex_auraenabled_rest_actions.htm&language=pt_BR&release=260&type=5)


