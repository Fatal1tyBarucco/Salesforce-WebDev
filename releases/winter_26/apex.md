# Apex — Winter '26

> **Release:** Winter '26
> **Gerado em:** 2026-06-12 21:14 UTC
> **Fonte:** https://help.salesforce.com/s/articleView?id=release-notes.salesforce_release_notes.htm&release=258&type=5&language=pt_BR

---

## Apex — Winter '26



### Faça o escape do atributo de rótulo de elementos <apex:inputField>...

Para evitar a execução de código mal-intencionado em ataques de script entre sites (XSS) em suas páginas do Visualforce, esta atualização de versão escapa ao atributo label das suas tags de <apex:inputField>. Essa atualização foi disponibilizada inicialmente na versão Winter '23.


[🔗 Leia mais no conteúdo original](https://help.salesforce.com/s/articleView?id=release-notes.rn_vf_escape_apex_inputfield_label_ru.htm&language=pt_BR&release=258&type=5)



### Simplificar a recuperação e a execução de testes do Apex e do Fluxo

Obtenha uma visão unificada de seus testes de fluxo automatizados e do Apex existentes com a nova API Test Discovery. Use a API do Test Runner atualizada para executar testes do Apex e do fluxo na mesma execução de teste. Ambas as APIs são recursos REST da API do conjunto de ferramentas. Você também pode executar e inspecionar testes de fluxo automatizados e do Apex declarativamente em Configuração.


[🔗 Leia mais no conteúdo original](https://help.salesforce.com/s/articleView?id=release-notes.rn_apex_unified_testing.htm&language=pt_BR&release=258&type=5)



### Padronizar a documentação do Apex usando o formato de comentário do...

O ApexDoc, um novo formato de comentário padronizado, torna mais fácil para humanos, geradores de documentação e agentes de IA entenderem sua base de códigos. Use os comentários do ApexDoc para facilitar a colaboração de código e aumentar a capacidade de manutenção de código de longo prazo. Com base no padrão JavaDoc, o Apex Doc fornece especificações, como marcas e diretrizes especializadas, que são adaptadas ao Apex e ao ecossistema do Salesforce. O padrão ApexDoc fornece uma base para a integração com ferramentas de desenvolvimento populares, permitindo que elas criem referências contextuais para melhorar a experiência de desenvolvimento.


[🔗 Leia mais no conteúdo original](https://help.salesforce.com/s/articleView?id=release-notes.rn_apex_apexdoc.htm&language=pt_BR&release=258&type=5)



### Usar modificadores de acesso em métodos abstratos e de substituição

Na API versão 65.0 e posteriores, os métodos abstract e override exigem um modificador de acesso protected, public ou global. O modificador de acesso private não é permitido porque impede que a classe de implementação acesse o método. Se você tentar declarar um método de abstract ou override sem um dos modificadores de acesso permitidos, ocorrerá um erro de compilação.


[🔗 Leia mais no conteúdo original](https://help.salesforce.com/s/articleView?id=release-notes.rn_apex_access_modifier.htm&language=pt_BR&release=258&type=5)



### Lide com grandes chamadas de serviço externo e cargas úteis sem...

Carregue e baixe grandes quantidades de dados de seu serviço externo como arquivos binários. Anteriormente, a transferência de blobs grandes por meio do Apex estava limitada pelo limite de heap. Agora, os Serviços externos usam ponteiros para ContentDocument IDs de objeto em vez de carregar os dados diretamente no heap do Apex. Com esse processo mais eficiente, você pode carregar e baixar arquivos binários de até 16 MB. Esse recurso fornece um método ideal para transferir dados que não requer manipulação adicional do Apex.


[🔗 Leia mais no conteúdo original](https://help.salesforce.com/s/articleView?id=release-notes.rn_apex_ext_services_binary.htm&language=pt_BR&release=258&type=5)



### Expor métodos do controlador AuraEnabled como ações do agente (beta)

Disponibilize os métodos do controlador Apex AuraEnabled como ações usando a integração beta com o Catálogo da API do MuleSoft para Salesforce. Certifique-se de que a extensão Agentforce para desenvolvedores esteja instalada a partir do Pacote de extensão do Salesforce no Visual Studio Code (VS Code). Em seguida, gere documentos OpenAPI para classes do Apex (beta) que tenham métodos de controlador AuraEnabled. Quando você implementa essas classes do Apex, os documentos OpenAPI e seus metadados são adicionados ao seu catálogo de API. Os métodos então ficam disponíveis como ações do agente.


[🔗 Leia mais no conteúdo original](https://help.salesforce.com/s/articleView?id=release-notes.rn_apex_auraenabled_actions.htm&language=pt_BR&release=258&type=5)



### Integrar o teste de unidade do Apex com o teste DevOps

Aumente a confiabilidade e a qualidade do seu Apex code adicionando o Apex Unit Testing como provedor de teste no DevOps Testing. Sincronize testes de unidade do Apex e pacotes de testes, defina portões de qualidade, atribua e execute testes de unidade do Apex e analise os resultados, tudo no DevOps Testing.


[🔗 Leia mais no conteúdo original](https://help.salesforce.com/s/articleView?id=release-notes.rn_apex_testing_integration_devops_testing.htm&language=pt_BR&release=258&type=5)



### Otimize o código com o ApexGuru

Gere percepções sob demanda. A nova guia Casos de teste verifica as classes de teste quanto a práticas ruins e lógica de preenchimento. O ApexGuru detecta consultas repetidas na Linguagem de consulta de objeto do Salesforce (SOQL) para armazenamento em cache com o Cache da plataforma. Além disso, o Apex Guru agora inclui mais detecção antipadrão para destacar mapas ineficientes, classificação no Apex e uso de loops do Apex para agregação de dados em vez de SOQL.


[🔗 Leia mais no conteúdo original](https://help.salesforce.com/s/articleView?id=release-notes.rn_apexguru.htm&language=pt_BR&release=258&type=5)


