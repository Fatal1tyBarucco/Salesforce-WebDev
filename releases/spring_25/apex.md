# Apex — Spring '25

> **Release:** Spring '25
> **Gerado em:** 2026-06-12 20:52 UTC
> **Fonte:** https://help.salesforce.com/s/articleView?id=release-notes.salesforce_release_notes.htm&release=254&type=5&language=pt_BR

---

## Apex — Spring '25



### Batch Test with Agentforce Testing Center

O teste é essencial para iniciar um agente confiável, mas o teste de turno de enunciados é demorado. Com o Centro de teste, agora você pode testar em escala usando testes em lote em seu sandbox, reduzindo a quantidade de tempo de teste de dias para minutos. Fornecemos um modelo CSV para ajudá-lo a colocar seus dados em ordem e pronto para uso.


[🔗 Leia mais no conteúdo original](https://help.salesforce.com/s/articleView?id=release-notes.rn_einstein_copilot_testing_center.htm&language=pt_BR&release=254&type=5)



### Call an Agent from a Flow or Apex Class

Coloque os tópicos, ações e recursos de raciocínio dos agentes para funcionarem para seus usuários fora de uma janela de chat com ações invocáveis do agente personalizadas. Chame um agente de serviço Agentforce (ASA) ou agente Agentforce (padrão) para concluir tarefas em segundo plano ou acionadas por evento de qualquer lugar que você possa chamar um fluxo ou classe do Apex. Adicione uma ação invocável a um fluxo ou classe do Apex e especifique a tarefa que o agente conclui e as condições que acionam o agente. Para ações invocáveis associadas a um agente de ASA, você também pode especificar as variáveis de contexto que você definiu para seu agente para passar ao agente as informações de que ele precisa. Você pode fazer várias chamadas ao mesmo agente para lidar com tarefas relacionadas ou chamar vários agentes do mesmo fluxo para lidar com tarefas mais especializadas.


[🔗 Leia mais no conteúdo original](https://help.salesforce.com/s/articleView?id=release-notes.rn_einstein_agent_flow_apex.htm&language=pt_BR&release=254&type=5)



### Batch Test Agents with Testing API

Reduce testing time and test your agent at scale with Testing API, which enables you to programmatically create and run multiple tests in one batch. Testing API gives you access to functionality in Agentforce Testing Center.


[🔗 Leia mais no conteúdo original](https://help.salesforce.com/s/articleView?id=release-notes.rn_einstein_testing_api.htm&language=pt_BR&release=254&type=5)



### Optimize Resources Using Merge Write Mode for Batch Transforms

Merge write mode only processes new and updated records when writing to a batch transform output object. This optimizes resource usage and prevents unnecessary reprocessing.


[🔗 Leia mais no conteúdo original](https://help.salesforce.com/s/articleView?id=release-notes.rn_cdp_2025_spring_merge_write_mode.htm&language=pt_BR&release=254&type=5)



### Delivered Idea: Compress and Extract Zip Files in Apex (Generally...

Use o namespace Compression e aproveite uma biblioteca zip do Apex nativa para compactar e extrair arquivos. Compacte facilmente arquivos em um arquivo zip de blobs e descompacte diretamente os arquivos armazenados em um arquivo zip para blobs. Otimize a compactação especificando o método e o nível de compactação. Você pode compactar vários anexos ou documentos como um blob do Apex em um arquivo zip. Também pode especificar os dados a serem extraídos do arquivo zip sem descompactar todo o arquivo zip. Entregamos esse recurso graças às suas ideias compartilhadas no IdeaExchange.


[🔗 Leia mais no conteúdo original](https://help.salesforce.com/s/articleView?id=release-notes.rn_apex_compression.htm&language=pt_BR&release=254&type=5)



### Delivered Idea: Evaluate Dynamic Formulas in Apex (Generally...

Fórmulas dinâmicas no Apex oferecem suporte a sObjects e objetos do Apex como objetos de contexto. Use os métodos de classe no namespace FormulaEval para criar e avaliar fórmulas dinâmicas. Esse recurso, agora disponível ao público em geral, dá suporte ao acesso a campos de relacionamento polimórficos. Você também pode fazer referência a pesquisas padrão e pesquisas personalizadas em campos de fórmula. Entregamos esse recurso graças às suas ideias compartilhadas no IdeaExchange.


[🔗 Leia mais no conteúdo original](https://help.salesforce.com/s/articleView?id=release-notes.rn_apex_formulaeval.htm&language=pt_BR&release=254&type=5)



### Scale Your Concurrent Long-Running Apex Requests Limit Based on...

The default limit for the number of synchronous concurrent transactions for long-running Apex requests now depends on the type and number of licenses in your org. Scaled license-based limits can avoid service disruptions caused by the limit, increase system stability with minimal risk to performance, and improve resource allocation. To ensure fair usage, the limit is capped at a maximum of 50 Apex requests. The minimum number of long-running concurrent Apex requests remains at 10.


[🔗 Leia mais no conteúdo original](https://help.salesforce.com/s/articleView?id=release-notes.rn_apex_limit.htm&language=pt_BR&release=254&type=5)



### Pause and Resume Scheduled Jobs by Using Apex

Com os novos métodos na classe System, você pode programaticamente pausar e retomar trabalhos agendados do Apex. Esse recurso complementa a capacidade de monitorar trabalhos agendados na IU de Configuração, que foi lançada na versão Summer '24. Para pausar ou retomar um trabalho agendado, especifique o nome do trabalho ou cronTriggerId. Chamar os métodos de pausa e retomada conta para o limite da instrução DML.


[🔗 Leia mais no conteúdo original](https://help.salesforce.com/s/articleView?id=release-notes.rn_apex_scheduledjobs.htm&language=pt_BR&release=254&type=5)


