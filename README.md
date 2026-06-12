![Salesforce Release Intelligence](./assets/banner.png)

# 🚀 Salesforce Release Notes Intelligence

Pipeline automatizado para extração, classificação e versionamento das **Salesforce Release Notes** como artefatos Markdown estruturados (*Knowledge-as-Code*).

### ⚙️ CI/CD Status & Conformidade

[![Python Quality & Validation](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/actions/workflows/python-quality.yml/badge.svg)](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/actions/workflows/python-quality.yml)
![Python](https://img.shields.io/badge/Python-3.14-blue.svg?logo=python&logoColor=white) 
![Playwright](https://img.shields.io/badge/Playwright-Headless_SPA-green.svg?logo=playwright&logoColor=white) 
![Mypy](https://img.shields.io/badge/Mypy-Strict_Mode-blue.svg) 
![Ruff](https://img.shields.io/badge/Ruff-Linter-black.svg) 
![Black](https://img.shields.io/badge/Formatter-Black-000000.svg)

| Tecnologia / Ferramenta | Descrição | Status no Pipeline |
| :--- | :--- | :---: |
| 🐍 **Python 3.14** | Ambiente de execução principal | `Conforme` |
| 🎭 **Playwright** | Scraper Headless para aplicações SPA do Salesforce Help | `Ativo` |
| 🧪 **Pytest** | Suíte de testes unitários automatizados | `100% Cobertura` |
| 🔍 **Mypy** | Verificação estática de tipos com modo estrito | `Strict` |
| ⚡ **Ruff & Black** | Linter e formatação estrita de código (line-length = 100) | `Conforme` |

---

## 📋 Notas de Release e Resumos por Tópico

### ❄️ Winter 26

#### 💻 Apex

* **Faça o escape do atributo de rótulo de elementos <apex:inputField>...**
  Para evitar a execução de código mal-intencionado em ataques de script entre sites (XSS) em suas páginas do Visualforce, esta atualização de versão escapa ao atributo label das suas tags de <apex:inputField>. Essa atualização foi disponibilizada inicialmente na versão Winter '23.

* **Simplificar a recuperação e a execução de testes do Apex e do Fluxo**
  Obtenha uma visão unificada de seus testes de fluxo automatizados e do Apex existentes com a nova API Test Discovery. Use a API do Test Runner atualizada para executar testes do Apex e do fluxo na mesma execução de teste. Ambas as APIs são recursos REST da API do conjunto de ferramentas. Você também pode executar e inspecionar testes de fluxo automatizados e do Apex declarativamente em Configuração.

* **Padronizar a documentação do Apex usando o formato de comentário do...**
  O ApexDoc, um novo formato de comentário padronizado, torna mais fácil para humanos, geradores de documentação e agentes de IA entenderem sua base de códigos. Use os comentários do ApexDoc para facilitar a colaboração de código e aumentar a capacidade de manutenção de código de longo prazo. Com base no padrão JavaDoc, o Apex Doc fornece especificações, como marcas e diretrizes especializadas, que são adaptadas ao Apex e ao ecossistema do Salesforce. O padrão ApexDoc fornece uma base para a integração com ferramentas de desenvolvimento populares, permitindo que elas criem referências contextuais para melhorar a experiência de desenvolvimento.

* **Usar modificadores de acesso em métodos abstratos e de substituição**
  Na API versão 65.0 e posteriores, os métodos abstract e override exigem um modificador de acesso protected, public ou global. O modificador de acesso private não é permitido porque impede que a classe de implementação acesse o método. Se você tentar declarar um método de abstract ou override sem um dos modificadores de acesso permitidos, ocorrerá um erro de compilação.

* **Lide com grandes chamadas de serviço externo e cargas úteis sem...**
  Carregue e baixe grandes quantidades de dados de seu serviço externo como arquivos binários. Anteriormente, a transferência de blobs grandes por meio do Apex estava limitada pelo limite de heap. Agora, os Serviços externos usam ponteiros para ContentDocument IDs de objeto em vez de carregar os dados diretamente no heap do Apex. Com esse processo mais eficiente, você pode carregar e baixar arquivos binários de até 16 MB. Esse recurso fornece um método ideal para transferir dados que não requer manipulação adicional do Apex.

* **Expor métodos do controlador AuraEnabled como ações do agente (beta)**
  Disponibilize os métodos do controlador Apex AuraEnabled como ações usando a integração beta com o Catálogo da API do MuleSoft para Salesforce. Certifique-se de que a extensão Agentforce para desenvolvedores esteja instalada a partir do Pacote de extensão do Salesforce no Visual Studio Code (VS Code). Em seguida, gere documentos OpenAPI para classes do Apex (beta) que tenham métodos de controlador AuraEnabled. Quando você implementa essas classes do Apex, os documentos OpenAPI e seus metadados são adicionados ao seu catálogo de API. Os métodos então ficam disponíveis como ações do agente.

* **Integrar o teste de unidade do Apex com o teste DevOps**
  Aumente a confiabilidade e a qualidade do seu Apex code adicionando o Apex Unit Testing como provedor de teste no DevOps Testing. Sincronize testes de unidade do Apex e pacotes de testes, defina portões de qualidade, atribua e execute testes de unidade do Apex e analise os resultados, tudo no DevOps Testing.

* **Otimize o código com o ApexGuru**
  Gere percepções sob demanda. A nova guia Casos de teste verifica as classes de teste quanto a práticas ruins e lógica de preenchimento. O ApexGuru detecta consultas repetidas na Linguagem de consulta de objeto do Salesforce (SOQL) para armazenamento em cache com o Cache da plataforma. Além disso, o Apex Guru agora inclui mais detecção antipadrão para destacar mapas ineficientes, classificação no Apex e uso de loops do Apex para agregação de dados em vez de SOQL.

> 📄 **Notas Completas:** consulte os detalhes completos na página do tópico [Apex](./releases/winter_26/apex.md).

#### ⚙️ Flow & Automação

* **Configurar páginas de registro padrão do Salesforce Flow no Criador...**
  Use as páginas de registro padrão do Salesforce Flow novas e atualizadas em qualquer aplicativo.

* **Integrar o teste de fluxo com o teste de DevOps**
  Adicione o Teste de fluxo como provedor de teste no Teste de DevOps e você receberá uma camada extra de teste para garantir que seus fluxos funcionem conforme o esperado e estejam alinhados aos requisitos de negócios. Agora você pode gerenciar diretamente ativos de teste de fluxo, definir portões de qualidade, atribuir e executar testes de fluxo e analisar resultados, tudo em Teste de DevOps.

* **Aproveite os recursos mais recentes do Salesforce Flow para...**
  Imagens de recurso estáticas agora estão disponíveis em componentes de Texto de exibição em fluxos de tela para disponibilidade de imagem consistente em sites do Experience Cloud. Use o novo recurso Estilo de visualização para ver como as telas aparecem em sites do Aura e do LWR.

* **Flow Builder**
  Agora, os clientes do Marketing Cloud Engagement podem acessar o Flow Builder. Use um fluxo para automatizar processos internos e pontos de contato externos. Crie experiências de cliente coesas que combinam dados do Sales Cloud, do Service Cloud, do Marketing Cloud, do Commerce Cloud, do Data Cloud, do Agentforce e de seus sistemas externos.

* **Obtenha percepções avançadas e estabilidade no Automation Studio**
  Obtenha mais dados e otimize suas automações com a nova funcionalidade para o Automation Studio.

* **Flow Builder**
  Use a IA generativa para conduzir suas decisões. Acesse novos registros sem precisar usar um elemento Obter registros. Visualize fluxos de tela no Lightning ou na identidade visual do seu site do Experience Cloud. Exibir coleções definidas pelo Apex no componente Tabela de dados. Simplifique a experimentação do caminho e escolha automaticamente um caminho vencedor com a seleção de caminho automatizada. Use as respostas de ações personalizadas do agente em um fluxo. Compare duas versões de um fluxo e veja detalhes sobre as diferenças no Flow Builder.

* **Atualizações do Flow Builder**
  Use a IA generativa para conduzir suas decisões. Encontre recursos mais rapidamente com um menu de recurso atualizado. Acesse novos registros sem precisar usar um elemento Obter registros. Use loops aninhados para acessar dados em diferentes níveis. Gere fluxos de rascunho com o Einstein Next Generation (beta).

* **Localize recursos mais rapidamente com atualizações no menu de...**
  Localize recursos sem esforço com rolagem mínima. Agora você vê apenas as opções relevantes para sua posição atual no fluxo e que correspondem ao tipo de dados. Além disso, com a pesquisa expandida no menu de recurso, você pode incluir resultados de recursos aninhados, como campos de registros e ações relacionadas, componentes e saídas. A pesquisa expandida, agora disponível ao público em geral, foi aprimorada desde a última versão para ser mais eficiente e fácil de usar.

> 📄 **Notas Completas:** consulte os detalhes completos na página do tópico [Flow & Automação](./releases/winter_26/flow.md).

#### 🔌 Integrações & APIs

* **Localizar colunas do conjunto de dados usando nomes de API**
  Agora você pode pesquisar campos de conjunto de dados usando seu nome de API exclusivo ao conectar conjuntos de dados, adicionar filtros ou explorar um conjunto de dados. Essa atualização simplifica o processo de encontrar o campo desejado. Antes, era difícil localizar campos específicos em conjuntos de dados complexos, especialmente aqueles com nomes de exibição semelhantes.

* **Ativar segmentos do Data Cloud para qualquer destino baseado em API...**
  Execute um fluxo acionado por ativação com uma ativação do Data Cloud quando a ativação estiver concluída. Use os dados de ativação para realizar ações usando serviços externos ou conectores do Mulesoft disponíveis no Fluxo. Por exemplo, use dados de ativação para criar ou atualizar contatos, leads ou oportunidades em um serviço externo. Isso permite um engajamento eficaz de marketing, publicidade, personalização, aprimoramento, análise, omni-channel e outros usando os atributos adicionais nos dados de ativação.

* **A chamada de login da API SOAP() nas versões da API SOAP 31.0 a 64.0...**
  Na versão Summer '27, a chamada de login() da API SOAP nas versões da API SOAP 31.0 a 64.0 não terá mais suporte e não estará mais disponível.

* **Atualizar URLs instanciados no tráfego de API (atualização de versão)**
  Para evitar interrupções quando o Salesforce encerrar o suporte para tráfego de API que use um URL instanciado incorreto, certifique-se de que o tráfego de API para sua organização use o URL de login do Meu domínio da organização. Primeiro disponível na versão Summer '25, essa atualização de versão é imposta nos sandboxes Winter '26 e imposta em todas as outras organizações na versão Spring '26.

* **Acompanhe seu uso de serviços externos com adições à API de limites**
  Obtenha mais visibilidade e controle sobre o consumo de serviços externos em sua organização com estas adições à API de limites: ExternalServicesActiveObjects, ExternalServicesActiveOperations, ExternalServicesObjectProperties, ExternalServicesObjects, ExternalServicesOperations e ExternalServicesRegistrations.

* **Unificar o teste com as APIs de Descoberta de teste e Test Runner**
  Recupere e execute testes de fluxo e Apex em um só lugar. Obtenha uma experiência de teste unificada que permite criar aplicativos mais confiáveis. Anteriormente, os testes do Apex e do fluxo exigiam diferentes pontos de invocação e não tinham um sistema de relatórios centralizado. Agora, você pode obter uma visão completa de seus testes usando a API Test Discovery para chamar um novo recurso REST da API do conjunto de ferramentas. Execute testes do Apex e do fluxo na mesma execução de teste com a API do Test Runner, que aprimora os recursos REST da API do conjunto de ferramentas existentes.

* **Consultas SOQL do Data Cloud agora dão suporte a funções agregadas...**
  Consultas SOQL agora dão suporte a funções agregadas MIN e MAX, e todas as funções agregadas com suporte (AVG, SUM, COUNT, MIN e MAX) agora estão disponíveis em objetos de data lake (DLOs) além de objetos de modelo de dados (DMOs) no Data Cloud.

* **Consultar objetos padrão do Salesforce para dados do Data 360 usando...**
  Filtre dados de objeto do Salesforce por atributos de objeto de modelo de dados (DMO) filho usando uma consulta de semijunção. A consulta externa faz referência ao objeto pai do Salesforce e a consulta interna faz referência a um DMO filho em que há um relacionamento direto. A consulta interna não pode fazer referência a um DMO usando um relacionamento baseado em resolução de identidade.

> 📄 **Notas Completas:** consulte os detalhes completos na página do tópico [Integrações & APIs](./releases/winter_26/integrations.md).

#### ⚡ Lightning Web Components (LWC)

* **API versão 65.0 do LWC**
  Atualize a versão da API de seus componentes para usar novos recursos e melhorias. A versão dos componentes da Web Lightning garante que os componentes existentes não sejam afetados quando o Salesforce envia novos recursos, correções de bugs e melhorias de desempenho que alteram o comportamento existente. O controle de versões também ajuda o Salesforce a descontinuar os recursos legados.

* **Visualizar um único componente da Web Lightning usando o...**
  Agora, ao visualizar um único componente da Web Lightning com o desenvolvedor local, você pode acessar módulos de plataforma, como adaptadores de conexão públicos do Lightning Data Service, módulos com escopo de @salesforce e controladores do Apex. Antes, esses recursos não estavam disponíveis em visualizações de componente único.

* **Mais definições de tipo disponíveis para componentes de base**
  Melhorar sua experiência de desenvolvimento do LWC com mais definições de tipo para componentes de base do Lightning. O TypeScript for LWC está na visualização para desenvolvedores e tem várias limitações.

* **Usar componentes do LWC para ações locais em fluxos de tela**
  Torne seus fluxos de tela mais eficientes e eficientes com ações locais do Componente da Web Lightning (LWC). Por exemplo, adicione um toast de confirmação ou navegue para uma página de registro. As ações locais são executadas diretamente no navegador, o que significa que elas têm acesso às funcionalidades do navegador.

* **Simplificar interações de dados com o Gerenciamento de estado para...**
  Agrupe e gerencie dados e sua lógica relacionada com mais eficiência em seus aplicativos.

* **Desempenho aprimorado do aplicativo Aura com otimização dinâmica do...**
  Os componentes do Aura usam um processo chamado boxcar’ing para agrupar várias ações no lado do servidor em uma solicitação de rede (XMLHttpRequest, ou XHR). A partir da versão Winter '26, a estrutura usa uma nova maneira de agrupar ações do Aura em boxcars, chamada de otimização dinâmica de boxcar.

* **Acelere o desenvolvimento com ferramentas de MCP do LWC (beta)**
  Crie aplicativos mais rapidamente sem sair do seu Ambiente de desenvolvimento integrado (IDE). Use avisos de linguagem natural para auxiliar no desenvolvimento, no teste, na otimização e na migração do Aura para o LWC do LWC.

* **Componentes da Web do Lightning novos e alterados**
  Crie a interface do usuário facilmente com componentes novos e alterados.

> 📄 **Notas Completas:** consulte os detalhes completos na página do tópico [Lightning Web Components (LWC)](./releases/winter_26/lwc.md).

#### 🔒 Segurança & Permissões

* **Usar a segurança do OAuth com sua conexão do Databricks**
  Aproveite o OAuth de máquina para máquina (M2M) para conectores do Databricks para fornecer segurança adicional. Agora você pode especificar quais objetos podem ser acessados e os privilégios de acesso concedidos a esses objetos. Com o M2M OAuth, você não precisa configurar um provedor de autenticação externo. Basta fornecer seus valores de ID do cliente e segredo do cliente do Databricks.

* **Usar a segurança do OAuth com sua conexão do Databricks**
  Aproveite o OAuth de máquina para máquina (M2M) para conectores do Databricks para fornecer segurança adicional. Agora você pode especificar quais objetos podem ser acessados e os privilégios de acesso concedidos a esses objetos. Com o M2M OAuth, você não precisa configurar um provedor de autenticação externo. Basta fornecer seus valores de ID do cliente e segredo do cliente do Databricks.

* **Permissões e compartilhamento**
  Depois de remover um conjunto de permissões ou grupo de conjuntos de permissões de um usuário, as licenças de conjunto de permissões relacionadas serão canceladas automaticamente. O comportamento de papéis seguros é imposto em organizações de produção. Para melhorar o desempenho, o Salesforce está mudando o modo como o recálculo de compartilhamento funciona.

* **Licenças de conjunto de permissões são removidas após cancelar a...**
  As atribuições de licença de conjunto de permissões relacionadas agora são removidas automaticamente depois que você cancela a atribuição de um conjunto de permissões ou grupo de conjuntos de permissões de um usuário. Essa alteração torna o gerenciamento de licenças mais eficiente, pois a remoção manual era obrigatória anteriormente. O cancelamento automático da atribuição não ocorre quando as atualizações são feitas por meio de políticas de acesso do usuário, quando o usuário exige a licença por meio de outro conjunto de permissões, ao remover um conjunto de permissões licenciado de um grupo de conjuntos de permissões ou ao cancelar a atribuição de 50 ou mais conjuntos de permissões ou grupos de conjuntos de permissões de uma só vez.

* **Alterações de distorção da API no Lightning Web Security**
  O Lightning Web Security inclui novas proteções de segurança com distorções adicionais para APIs da Web. Regras do ESLint que correspondem às distorções também estão disponíveis.

* **O suporte para autenticação de fluxo de dispositivo do OAuth 2.0...**
  A Salesforce está removendo o suporte para autenticação de fluxo de dispositivo do OAuth 2.0 nos aplicativos conectados do Data Loader instalados automaticamente em 2 de setembro de 2025. Não há exceções ou extensões disponíveis para essa remoção.

* **Segurança, identidade e privacidade**
  A Detecção de dados oferece recursos de digitalização expandidos e tipos de dados. Monitore as atividades de acesso a dados do agente com Eventos em tempo real. Use dados de evento em objetos padrão com objetos de log de eventos adicionais e maior disponibilidade regional. Defina políticas de retenção com a Trilha de auditoria de campo. A Criptografia de plataforma para Data Cloud agora oferece suporte ao Tableau Next. A Criptografia de banco de dados agora é GA. Prepare e faça a rotação das credenciais do aplicativo cliente externo. Configure recursos móveis e notificações para aplicativos cliente externos. Redefina sua senha esquecida usando seu endereço de email. Use tempos limite mais longos para tokens de acesso baseados em JWT. Escolha quais métodos de verificação de identidade registrar em novas organizações. Obtenha visibilidade das atividades do agente com Rastreamento de plataforma e dados no Data Cloud.

* **Domínios**
  Para evitar interrupções, atualize as referências a nomes de host legados, incluindo nomes de host instanciados em chamadas à API. E a vantagem regional está disponível no Japão.

> 📄 **Notas Completas:** consulte os detalhes completos na página do tópico [Segurança & Permissões](./releases/winter_26/security.md).


---

### ☀️ Summer 26

#### 💻 Apex

* **Atualize o Apex code e os fluxos para alterar o comportamento de...**
  Para otimizar o desempenho após atualizações em grande escala em grupos ou papéis, o Salesforce agora realiza alguns recálculos de compartilhamento de modo assíncrono. Se o Apex code e os fluxos exigirem que os registros de compartilhamento sejam atualizados imediatamente, o código e os fluxos poderão ser interrompidos quando essa atualização de versão for imposta. Atualize classes, testes e fluxos do Apex que atualizam a associação ao grupo ou papéis se eles dependem de recálculo de compartilhamento síncrono. Essa atualização foi disponibilizada inicialmente na versão Spring '26.

* **Operações de banco de dados são executadas no modo de usuário por...**
  Aproveite um modelo de segurança do Apex aprimorado que protege seus dados através da imposição de acesso em nível de objeto e campo padrão. Operações de banco de dados do Apex, como consultas SOSL e SOQL, instruções DML e métodos de banco de dados, agora são executadas no modo de usuário por padrão. No modo de usuário, as operações de banco de dados aplicam as regras de compartilhamento, a segurança em nível de campo e as permissões de objeto do usuário atual. Em versões anteriores da API, as operações de banco de dados usam como padrão o modo do sistema, o que significa que o usuário atual pode acessar todos os dados independentemente de suas permissões.

* **Classes do Apex aplicam regras de compartilhamento por padrão**
  Aproveite um modelo de segurança do Apex aprimorado que protege seus dados por meio da imposição de acesso de registro padrão. Classes do Apex sem uma declaração de compartilhamento explícita agora usam como padrão o modo with sharing, que aplica configurações de compartilhamento para toda a organização e regras de compartilhamento personalizadas. Em versões anteriores da API, classes do Apex sem uma declaração de compartilhamento explícita usam como padrão o modo without sharing, com algumas exceções. O modo without sharing ignora as regras de compartilhamento e permite que o usuário atual acesse todos os registros.

* **A cláusula SOQL WITH SECURITY_ENFORCED foi removida**
  Para executar uma consulta SOQL ou SOSL no modo de usuário, use a cláusula WITH USER_MODE em vez da cláusula WITH SECURITY_ENFORCED. Classes do Apex definidas como a API versão 67.0 e posterior que incluem WITH SECURITY_ENFORCED não são compiladas.

* **Acionadores do Apex sempre são executados no modo do sistema**
  Os acionadores do Apex agora sempre são executados no modo do sistema, o que significa que ignoram as regras de compartilhamento, a segurança em nível de campo e as permissões de objeto do usuário atual. Antes, acionadores aninhados impedia regras de compartilhamento em determinados casos de borda. Não é possível declarar acionadores do Apex com modos de compartilhamento ou acesso explícitos. Em vez disso, para aplicar as configurações de acesso a dados, delegue a lógica de negócios para separar manipuladores de acionador, em que você pode definir os modos de compartilhamento e acesso.

* **Escrever testes de integração para Agentforce e Data 360 no Apex...**
  Escreva testes do Apex completos que fazem chamadas para o Agentforce e o Data 360. Os testes de integração relaxam as restrições de chamadas e a semântica de reversão de transações, para que você possa validar interações reais de serviço e afirmar efeitos colaterais reais em sua organização teste, sem chamadas simuladas.

* **Evite interrupções de fluxo de trabalho habilitando limites...**
  Evite falhas de execução abruptas e limite as exceções se sua organização exceder seu limite diário de trabalho assíncrono. Agora você pode colocar em fila trabalhos de método enfileiráveis e futuros até um novo limite elástico, que é o dobro do limite diário licenciado da sua organização. Os trabalhos assíncronos que excedem o limite diário licenciado são processados a uma taxa limitada.

* **Bloquear a execução de código anônimo do Apex de pacotes gerenciados...**
  Para reforçar a segurança da organização assinante, bloqueie IDs de sessão de pacote gerenciado de autenticar código do Apex anônimo. Se você habilitar essa atualização, os pacotes gerenciados instalados não poderão mais usar o UserInfo.getSessionId() para obter um ID da sessão e, em seguida, usar o ID da sessão para executar o Apex anônimo.

> 📄 **Notas Completas:** consulte os detalhes completos na página do tópico [Apex](./releases/summer_26/apex.md).

#### ⚙️ Flow & Automação

* **Flow Builder**
  Crie e configure agentes do Agentforce no Flow Builder. Otimize, aumente o desempenho e evite limites do controlador em fluxos agendados com tamanhos de lote personalizados. Desenvolva fluxos de tela usando idioma nativo. Personalize mensagens de email usando variáveis de conteúdo do Email Content Builder. Notifique os usuários com mensagens de toast. Adicione editores de propriedade personalizados a parâmetros de entrada individuais.

* **Atualizações do Flow Builder**
  Otimize, aumente o desempenho e evite limites do controlador em fluxos agendados com tamanhos de lote personalizados. Use referências de modelo de email entre ambientes. Recolha caminhos de falha na tela do Flow Builder. Encontre recursos mais facilmente no elemento Adicionar instruções de prompt.

* **Melhorar o desempenho com lote para fluxos agendados**
  Otimize a execução de seus fluxos agendados e evite atingir os limites do controlador especificando um tamanho de lote personalizado. Particione entrevistas de fluxo em lotes menores variando de 1 a 200 diretamente do elemento de início do fluxo. Antes, os fluxos agendados processavam entrevistas em tamanhos de lote padrão de 200, o que pode esgotar recursos em automações complexas.

* **Evite corrigir manualmente referências de modelo de email depois de...**
  Implemente fluxos com ações Enviar email entre ambientes sem referências de modelo de email corrompidas. Selecione um nome de modelo de email em uma lista suspensa na ação Enviar email. A ação armazena o modelo selecionado como uma referência que persiste em ambientes de implementação. Antes, a ação Enviar email salvava o modelo de email selecionado como um ID de modelo. Como o ID muda durante a implementação do fluxo de uma organização para outra, a ação falhou e exigia atualizações manuais.

* **Recolha caminhos de falha para focar seu fluxo principal**
  Simplifique seu fluxo e concentre-se no caminho de trabalho ocultando caminhos de falha. Expanda os caminhos de falha apenas quando estiver pronto para editá-los ou revisá-los. Seu navegador mostra seu estado de layout pessoal, assim, sua visualização de tela é exclusiva para você.

* **Usar ativações de DMO de streaming, mais elementos de fluxo e...**
  Use ativações de objeto de modelo de dados (DMO) de streaming para acionar um fluxo para que você possa agir em eventos quase em tempo real. Agora você pode usar coleções em um elemento Decisão e usar o elemento Aguardar até o evento. A depuração também está disponível para solucionar problemas e testar seu fluxo.

* **Localizar e selecionar recursos mais facilmente no elemento...**
  Encontre o recurso certo mais rapidamente ao usar o elemento Adicionar instruções de instrução em um fluxo de instrução acionado por modelo. O seletor de recursos aprimorado agrupa recursos e os exibe com seus rótulos e ícones intuitivos.

* **Seleção de recurso aprimorada em elementos de fluxo de estratégia de...**
  Selecione recursos nos elementos Atribuição de recomendação e Limitar repetições usando listas de opções de recursos atualizadas. As listas de opções de recursos agora filtram os recursos disponíveis com base no tipo de dados necessário para cada campo. Antes, esses elementos usavam seletores de recurso legados.

> 📄 **Notas Completas:** consulte os detalhes completos na página do tópico [Flow & Automação](./releases/summer_26/flow.md).

#### 🔌 Integrações & APIs

* **Gerenciar bibliotecas de dados do Agentforce com a API ADL Connect...**
  As Bibliotecas de dados do Agentforce (ADL) aumentam a precisão dos recursos de IA, como agentes do Agentforce, conectando-os às suas fontes de dados confiáveis. Com o lançamento da API do ADL Connect (beta), os clientes podem programaticamente criar e gerenciar bibliotecas de dados, permitindo que os desenvolvedores automatizem e integram o provisionamento de ADL diretamente em seus fluxos de trabalho e aplicativos.

* **Notas da versão 26.6 da B2C Commerce API**
  Confira os recursos e atualizações mais recentes da B2C Commerce API.

* **Enviar eventos com a categoria Outro por meio da API de servidor...**
  A API Server-to-Server (S2S) agora oferece suporte à categoria de evento Other. Classifique corretamente eventos de fontes como Agentforce, dispositivos IoT, sistemas de POS de varejo e fluxos de trabalho de processos de negócios.

* **Ingerir dados de outras origens com a API de servidor para servidor**
  A nova opção Dados de outras fontes usa três campos (eventId, eventType e dateTime) para tornar a ingestão de dados mais flexível. Ingira dados de fontes não web e não móveis, como conversas do Agentforce, transações de POS, telemetria de dispositivos de IoT e quiosques de autoatendimento, usando a API Server-to-Server (S2S). Antes, a API S2S impedia a ingestão de dados de origens que não tinham contexto de navegador ou aplicativo.

* **Adote o streaming para atualizações de gráfico de dados mais rápidas**
  Mantenha seus dados atualizados com Gráficos de dados de streaming que são atualizados assim que os dados subjacentes mudam. Antes, você precisava determinar manualmente a frequência de atualização para seus Gráficos de dados, o que às vezes levava a dados obsoletos. Agora, as alterações de dados do objeto de modelo de dados (DMO) subjacente acionam automaticamente atualizações e fornecem atualizações mais rápidas quase em tempo real. Esse comportamento de atualização previsível torna seus SLAs mais confiáveis e dá aos agentes Agentforce ou mecanismos de personalização acesso aos perfis Customer 360 mais atualizados.

* **Filtrar ativações de DMO de streaming com atributos de gráfico de...**
  Use DMOs em seu gráfico de dados para definir critérios de associação para ativações de DMO de streaming, indo até dois saltos do DMO ativado. Crie públicos mais direcionados com base nos relacionamentos que você já modelou, sem ser limitado apenas aos atributos do DMO ativado.

* **Conecte agentes de IA ao Salesforce com segurança com servidores MCP...**
  Conecte qualquer cliente de IA compatível com MCP, incluindo Claude, ChatGPT, Cursor ou agentes personalizados, à sua organização do Salesforce usando o padrão de Protocolo de contexto de modelo (MCP) aberto. Seus agentes de IA agora podem interagir com dados e automação do Salesforce de maneira segura e controlada com a autenticação OAuth padrão. Os servidores MCP hospedados não exigem nenhuma infraestrutura para gerenciar. Acesse operações do sObject, consultas do Data 360, análises do Tableau e APIs de produto e crie ferramentas personalizadas usando suas próprias ações do Apex, fluxos e consultas nomeadas sem escrever código de integração.

* **Permitir que os assistentes de IA localizem e criem metadados do...**
  O servidor de MCP de Contexto da API do Salesforce agora tem cinco ferramentas de MCP de Contexto da API de metadados em vez de uma. Essas ferramentas mais granulares significam que as consultas do agente de IA podem ser direcionadas, os tempos de resposta são mais rápidos e seu uso de token pode ser mais eficiente. As ferramentas de MCP Contexto da API de metadados fornecem informações contextuais sobre tipos de metadados do Salesforce para ajudar a gerar arquivos de metadados do Salesforce precisos. Essas ferramentas fornecem definições de campo completas, valores válidos, restrições e exemplos para tipos de metadados.

> 📄 **Notas Completas:** consulte os detalhes completos na página do tópico [Integrações & APIs](./releases/summer_26/integrations.md).

#### ⚡ Lightning Web Components (LWC)

* **Integre componentes da Web Lightning personalizados em painéis para...**
  Adicione componentes da Web Lightning (LWC) personalizados diretamente aos painéis do Lightning para criar visualizações de dados interativas em tempo real que vão além das funcionalidades padrão do painel. Filtre, explore e aja com base em dados imediatamente sem sair do painel. Por exemplo, um analista de negócios pode usar um LWC personalizado para exibir um gráfico de cascata ou outras visualizações que não estejam disponíveis em painéis padrão.

* **Obtenha as alterações mais recentes do LWC com a API versão 67.0 do...**
  Atualize a versão da API para seus componentes para aproveitar os novos recursos e melhorias. O controle de versão garante que os componentes existentes não sejam afetados quando o Salesforce envia novos recursos, correções de bugs e melhorias de desempenho que alteram o comportamento existente. O controle de versões também ajuda o Salesforce a descontinuar os recursos legados.

* **Elementos de detalhes do grupo com o nome Atributo**
  Atualize a versão da API para seus componentes para aproveitar os novos recursos e melhorias. O controle de versão garante que os componentes existentes não sejam afetados quando o Salesforce envia novos recursos, correções de bugs e melhorias de desempenho que alteram o comportamento existente. O controle de versões também ajuda o Salesforce a descontinuar os recursos legados.

* **Melhorar o desempenho de recarregamento de módulo hot**
  Atualize a versão da API para seus componentes para aproveitar os novos recursos e melhorias. O controle de versão garante que os componentes existentes não sejam afetados quando o Salesforce envia novos recursos, correções de bugs e melhorias de desempenho que alteram o comportamento existente. O controle de versões também ajuda o Salesforce a descontinuar os recursos legados.

* **O desenvolvedor local agora é a visualização ativa**
  Para refletir melhor a natureza em tempo real do componente, do site do Experience e das visualizações do aplicativo Lightning, o desenvolvedor local agora se chama Visualização em tempo real.

* **Visualizar um único componente da Web Lightning no seu navegador...**
  Use a Visualização ativa de componente único para executar uma visualização em tempo real de um componente da Web Lightning em seu navegador. Esse recurso, que agora está disponível ao público em geral, inclui algumas alterações desde a versão beta.

* **Visualizar um único componente da Web Lightning no Visual Studio...**
  Para executar uma visualização em tempo real de um componente da Web Lightning diretamente no Visual Studio Code (VS Code) ou no Criador de código, use a extensão Visualização em tempo real VS Code. Essa extensão agora está disponível ao público em geral para componentes da Web Lightning.

* **Simplificar interações de dados com gerentes de estado para LWC...**
  Agrupe e gerencie dados e sua lógica relacionada com mais eficiência em seus aplicativos com gerentes de estado. Esse recurso, que agora está disponível ao público em geral, inclui algumas alterações desde a versão beta.

> 📄 **Notas Completas:** consulte os detalhes completos na página do tópico [Lightning Web Components (LWC)](./releases/summer_26/lwc.md).

#### 🔒 Segurança & Permissões

* **Permissões**
  Veja onde as permissões de campo estão habilitadas usando o Resumo de acesso ao campo. Na interface de usuário de perfil avançada, o Salesforce mostra as alterações necessárias para manter as permissões dependentes alinhadas. Crie políticas de segurança da transação para monitorar ou bloquear atualizações de permissão críticas em perfis. Revise a atualização de versão que habilita a filtragem de perfil por padrão.

* **Revise o acesso ao campo entre perfis, conjuntos de permissões e...**
  Poupe tempo revisando a segurança em nível de campo para um campo específico em todos os perfis, conjuntos de permissões e grupos de conjuntos de permissões. Em vez de ir para páginas de Configuração individuais, você pode visualizar essas informações em um só lugar no Resumo de acesso ao campo no Gerenciador de objetos.

* **Rastrear dependências de permissão mais facilmente**
  Ao atualizar permissões ou aplicativos na interface de usuário de perfil avançada, você verá quaisquer alterações adicionais necessárias para manter as permissões dependentes alinhadas após atualizações anteriores. Antes, essas alterações ocorriam em segundo plano, mas estavam visíveis apenas na Trilha de auditoria de configuração.

* **Habilitar filtragem de perfil (atualização de versão)**
  Para melhorar a segurança da sua organização do Salesforce, a configuração Filtragem de perfil está habilitada por padrão. A filtragem de perfil impede que os usuários visualizem nomes de perfil que não sejam os próprios, a menos que tenham a permissão Visualizar todos os perfis. Se o papel de um usuário exigir que ele veja todos os nomes de perfil, atribua a ele a permissão Visualizar todos os perfis antes da imposição dessa atualização de versão. Essa atualização está disponível da versão Summer '26 em diante.

* **Monitore alterações administrativas em perfis com políticas de...**
  Gere eventos de rastreamento quando os administradores do Salesforce modificam ou criam perfis de usuário que incluem permissões críticas. Bloqueie alterações não autorizadas em permissões de perfil críticas. Use Políticas de segurança da transação para monitorar, alertar e bloquear atualizações de permissão em tempo real. Essas políticas ajudam você a monitorar privilégios de segurança aprimorados e manter uma estrutura de auditoria robusta. Você também pode rastrear a remoção específica da permissão de isenção de TransactionSecurity de perfis.

* **Alterações de distorção da API no Lightning Web Security**
  O Lightning Web Security (LWS) inclui novas proteções de segurança com mais distorções para APIs da Web. Regras do ESLint que correspondem às distorções também estão disponíveis.

* **Segurança, identidade e privacidade**
  Prepare-se para aprimoramentos de segurança novos e futuros. Restaure dados com mais eficiência e obtenha controle sobre operações de backup. Garanta que suas integrações permaneçam conectadas alternando para endereços da Web exclusivos com marca. Cumpra normas padrão com percepções conduzidas por IA.

* **Aprimoramentos de segurança**
  Prepare-se para aprimoramentos de segurança novos e futuros.

> 📄 **Notas Completas:** consulte os detalhes completos na página do tópico [Segurança & Permissões](./releases/summer_26/security.md).


---

### ☀️ Summer 25

#### 💻 Apex

* **Atribuir compradores a grupos de compradores usando a lógica do Apex**
  Atribua automaticamente convidados e compradores autenticados a grupos de compradores usando uma lógica do Apex personalizada definida nas configurações da sua loja. Controle quais produtos eles veem, os preços exibidos e as promoções oferecidas, o que pode levar a interações mais relevantes na sua loja.

* **Avaliar fórmulas dinâmicas no modo de modelo**
  Escreva código mais conciso usando o novo método parseAsTemplate() na classe FormulaBuilder. O método parseAsTemplate() avalia uma fórmula dinâmica no modo de modelo. No modo de modelo, você pode criar expressões de fórmula em que os valores são interpolados em uma string usando a sintaxe de campo de mesclagem {!Object_Name.Field_Name}. Comparado à concatenação de string tradicional, essa sintaxe torna seu código mais limpo e legível.

* **Especificar uma habilitação para toda a organização de logs de...**
  Gerar registros de depuração durante uma implantação de metadados pode causar execução de teste mais longa e está desabilitado por padrão. No entanto, os administradores podem optar por habilitar registros de depuração durante a implementação de metadados por meio dessa configuração, junto com um sinalizador de rastreamento de registro de depuração ativo. A ativação do registro de depuração no DebuggingHeader substitui essa configuração.

* **Aprimore os designs de configuração do Apex invocável com os novos...**
  Use o tipo de metadados InvocableActionExtension (Visualização do desenvolvedor) para especificar como apresentar as entradas da ação. Você pode definir a ordem das entradas e fornecer descrições e rótulos, bem como adicionar atributos estendidos para ações e tipos do Apex, melhorando a experiência do usuário em ferramentas com pouco código, como o Flow Builder. A experiência de desenvolvimento geral foi aprimorada dando a você mais controle sobre a experiência de configuração sem precisar codificar um editor de propriedade personalizado (CPE).

* **Gere investigações do Apex aprimoradas, forneça feedback no...**
  Melhore o desempenho do Apex com orientações prescritivas e percepções úteis. Forneça feedback sobre o recurso usando o botão Feedback. Obtenha percepções de pesquisa para recomendações para melhorar o desempenho da pesquisa.

* **Otimize o código com o ApexGuru**
  Recursos de detecção antipadrão otimizam o Apex code e melhoram o desempenho. Visualize consultas SOQL em loops, identifique filtros e operações de consulta ineficientes e receba recomendações para reduzir operações de string caras e instruções de depuração.

* **Descubra o tamanho e o usuário do lote do acionador do Apex**
  Agora você pode visualizar a configuração do acionador de evento da plataforma Apex em Configuração verificando as novas colunas Tamanho do lote e Usuário. Ter essas informações disponíveis na IU facilita o monitoramento e o ajuste fino da configuração do acionador. Antes, o tamanho do lote e as informações do usuário estavam disponíveis apenas por meio da API do conjunto de ferramentas ou da API de metadados em PlatformEventSubscriberConfig.

* **Apex: Itens novos e alterados**
  Essas classes, enums e interfaces são novas ou foram alteradas.

> 📄 **Notas Completas:** consulte os detalhes completos na página do tópico [Apex](./releases/summer_25/apex.md).

#### ⚙️ Flow & Automação

* **Simplificar o registro de Single Sign On com o Flow Builder**
  Para simplificar o processo de criar um manipulador de registro para login único (SSO) em seu site do Experience Cloud, use o Flow Builder em vez do Apex. Personalize o novo modelo de fluxo Registro de usuário do provedor de autenticação para criar e atualizar usuários que fazem login em seu site por meio de um provedor de identidade de terceiros.

* **Flow Builder**
  Obtenha registros relacionados no elemento Obter registros (beta). Pesquise recursos aninhados no Flow Builder (beta). Simplifique os fluxos de tela com ações de tela acionadas automaticamente. Encaminhe os usuários por um fluxo com base em engajamentos com o elemento de Decisão do Einstein. Crie processos de aprovação de fluxo com uma ação. Depure mais fluxos e faça isso com mais eficiência com melhorias na experiência de depuração. Acelere o teste de fluxo com testes integrados.

* **Atualizações do Flow Builder**
  Obtenha registros relacionados no elemento Obter registros (beta). Pesquise recursos aninhados (beta). Crie fluxos que realizem operações baseadas em tempo com o novo tipo de dados de hora. Configure declarações negativas em testes de fluxo. Trabalhe com mais eficiência com melhorias na interface do usuário para o painel do Einstein, listas de opções, a capacidade de apontar e ampliar e uma maneira mais fácil de selecionar recursos.

* **Obtenha registros relacionados mais rapidamente (beta)**
  Agora você pode obter registros relacionados em uma só consulta no Flow Builder, facilitando o gerenciamento de registros relacionados. Antes, você gerenciava registros relacionados adicionando elementos Obter registros separados. Com o elemento Obter registros, você pode selecionar relacionamentos de objeto relacionados, o que pode ajudá-lo a refletir a lógica de negócios complexa. Registros relacionados no elemento Obter registros estão disponíveis em fluxos iniciados automaticamente.

* **Encontre mais recursos com a pesquisa expandida (beta)**
  Ao pesquisar e selecionar recursos no Flow Builder, você pode escolher expandir sua pesquisa para incluir resultados de um conjunto expandido de recursos, como campos de registros e ações, componentes e saídas relacionadas. Esse recurso foi lançado anteriormente na versão Winter '25, mas foi removido posteriormente. Estamos reintroduzindo esse recurso depois de lidar com o feedback do cliente.

* **Gerenciar dados específicos de horário facilmente**
  Use recursos e campos do tipo de dados Hora para processar dados em que somente a hora do dia importa, não a data associada. Você pode especificar a hora do dia até o milissegundo exato. O tipo de dados Hora está disponível entre elementos de fluxo, criador de fórmula, criador de expressões, subfluxos e recursos como variáveis e constantes. Também está disponível em entradas e saídas de e para ações invocáveis. Não há suporte para o tipo de dados de hora nos fluxos offline disponíveis no aplicativo Salesforce móvel.

* **Visualizar seleções da lista de opções como pílulas**
  Depois de selecionar um valor da lista de opções, para tornar sua seleção mais clara e fácil de entender, a seleção é renderizada como uma pílula com um rótulo fácil de ler. Antes, as seleções da lista de opções eram mostradas com nomes de API, o que podia variar significativamente dos rótulos fornecidos. Por exemplo, uma opção de lista de opções rotulada como "Verdadeiro" pode aparecer como o valor "1" depois de selecioná-la.

* **Selecionar um recurso inteiro com mais eficiência ao navegar por um...**
  O novo item de menu Recurso inteiro no menu de seleção de recurso simplifica como selecionar todo o recurso que você está navegando no momento. Antes, para selecionar todo o recurso, era necessário selecionar o recurso no menu do recurso e, em seguida, clicar fora do menu sem selecionar um campo específico.

> 📄 **Notas Completas:** consulte os detalhes completos na página do tópico [Flow & Automação](./releases/summer_25/flow.md).

#### 🔌 Integrações & APIs

* **Corpos de solicitação da API REST do Connect alterados**
  Resumo não disponível para este artigo.

* **A documentação da API do carrinho do Salesforce para Comércio está...**
  A documentação da API do Cart Connect agora está no Guia do desenvolvedor do B2B Commerce e do D2C Commerce. Foi documentado anteriormente no Guia do desenvolvedor da API REST do Connect. As informações de referência agora seguem os padrões de Especificação OpenAPI (OAS) para APIs REST.

* **Localize a documentação da API de Pagamentos do Salesforce em um...**
  A API Payments Connect, anteriormente documentada no Guia do desenvolvedor da API REST do Connect, foi movida para o Guia do desenvolvedor do B2B Commerce e do D2C Commerce. Além disso, as informações de referência agora seguem os padrões de Especificação OpenAPI (OAS) para APIs REST.

* **Realizar atualizações de registro parciais usando a API de ingestão...**
  Agora você pode atualizar um registro ingerido anteriormente usando a API de ingestão de streaming. Para fazer uma atualização parcial, inclua a chave primária do registro na sua solicitação, forneça um valor para o registro modificado arquivado e especifique os campos que precisam de atualização. O Data Cloud atualiza apenas os campos incluídos na carga útil e deixa os outros campos inalterados, desde que o valor do campo Registro modificado seja mais recente que o valor atual.

* **Usar o URL de login do Meu domínio da sua organização em chamadas à...**
  Essa atualização foi cancelada. Ele é substituído pela atualização de versão Atualizar URLs instanciados no tráfego da API.

* **Atualizar URLs instanciados no tráfego de API**
  Para evitar interrupções quando o Salesforce encerrar o suporte para tráfego de API que use um URL instanciado incorreto, certifique-se de que o tráfego de API para sua organização use o URL de login do Meu domínio da organização. Essa atualização está disponível da versão Summer '25 em diante.

* **Descontinuação da API da Salesforce Platform versões 21.0 a 30.0...**
  A descontinuação das versões 21.0 a 30.0 da API da Salesforce Platform foi agendada inicialmente para a versão Summer '23. A descontinuação agora é adiada para a versão Summer '25. Essas versões da API não têm suporte e não estarão disponíveis a partir da versão Summer '25. Os aplicativos que as consomem são então interrompidos. As solicitações falham com uma mensagem de erro indicando que o ponto de extremidade está desativado. Atualize todos os aplicativos que usam uma versão de API legada para uma versão atual antes que essa mudança ocorra.

* **Seja notificado sobre solicitações de API composta com tipos de...**
  Consulte o objeto EventLogFile para os tipos de evento CompositeApi e CompositeApiSubrequest para obter detalhes sobre solicitações e subsolicitações da API de gráfico composto e API composta.

> 📄 **Notas Completas:** consulte os detalhes completos na página do tópico [Integrações & APIs](./releases/summer_25/integrations.md).

#### ⚡ Lightning Web Components (LWC)

* **API versão 64.0 do LWC**
  Atualize a versão da API de seus componentes para usar novos recursos e melhorias. A versão dos componentes da Web Lightning garante que os componentes existentes não sejam afetados quando o Salesforce envia novos recursos, correções de bugs e melhorias de desempenho que alteram o comportamento existente. O controle de versões também ajuda o Salesforce a descontinuar os recursos legados.

* **Visualizar um único componente da Web Lightning usando um...**
  Agora você pode configurar o Desenvolvedor local para executar uma visualização em tempo real de um único componente da Web Lightning. Antes, era preciso publicar um componente em uma organização para visualizá-lo usando o desenvolvedor local.

* **O servidor de desenvolvimento local está sendo descontinuado**
  A descontinuação do servidor de desenvolvimento local está agendada para 5 de setembro de 2025. Para continuar testando seus componentes da Web Lightning em uma visualização em tempo real do navegador, migre para a nova experiência de desenvolvedor local. Com o Desenvolvedor local, você pode visualizar seus componentes da Web Lightning isoladamente ou em um aplicativo Lightning ou site do Lightning Web Runtime do Experience Cloud.

* **Migrar projetos de componentes da Web Lightning para o ESLint v9...**
  Para ajudá-lo a escrever JavaScript mais consistente e moderno para seus componentes, o Lightning Web Components agora oferece suporte ao ESLint v9. Esta versão introduz desempenho aprimorado, gerenciamento de regras aprimorado e gerenciamento de plug-ins aprimorado. Recomendamos que você atualize para a v9 antes da versão Spring '26 porque planejamos encerrar o suporte para o ESLint v8 na versão Winter '26.

* **Usar TypeScript com componentes de base do Lightning**
  Melhorar a experiência de desenvolvimento do LWC usando as definições de tipo para componentes de base do Lightning. O TypeScript for LWC está na visualização para desenvolvedores e tem várias limitações.

* **Componentes da Web do Lightning novos e alterados**
  Crie a interface do usuário facilmente com componentes novos e alterados.

* **Módulos alterados para Componentes da Web Lightning**
  Resumo não disponível para este artigo.

* **Novas metas para componentes da Web Lightning**
  Resumo não disponível para este artigo.

> 📄 **Notas Completas:** consulte os detalhes completos na página do tópico [Lightning Web Components (LWC)](./releases/summer_25/lwc.md).

#### 🔒 Segurança & Permissões

* **Usar a segurança OAuth com sua conexão do Snowflake VPC**
  Aproveite o OAuth em todos os conectores do Snowflake para proporcionar uma experiência de conexão consistente e segura. O conector de entrada de Conexão privada virtual (VPC) para Snowflake agora tem funcionalidade completa do OAuth para combinar os conectores de entrada, saída e sincronização do Snowflake.

* **Usar a segurança OAuth com sua conexão do Snowflake VPC**
  Aproveite o OAuth em todos os conectores do Snowflake para proporcionar uma experiência de conexão consistente e segura. O conector de entrada de Conexão privada virtual (VPC) para Snowflake agora tem funcionalidade completa do OAuth para combinar os conectores de entrada, saída e sincronização do Snowflake.

* **Permissões**
  Os aprimoramentos no usuário, no conjunto de permissões, no grupo do conjunto de permissões e nos resumos de acesso ao objeto facilitam o gerenciamento do acesso do usuário.

* **Ideia entregue: Atualizar permissões de objeto para todos os...**
  Economize tempo e cliques editando o acesso ao objeto simultaneamente em todos os conjuntos de permissões e perfis personalizados. Não é necessário acessar páginas de perfil ou conjuntos de permissões individuais. No Gerenciador de objetos, acesse o resumo de acesso de um objeto específico para revisar, adicionar ou remover permissões de objeto. Entregamos esse recurso graças às suas ideias compartilhadas no IdeaExchange.

* **Ideia entregue: Editar permissões mais rapidamente no resumo do...**
  Em vez de acessar muitas páginas de Configuração, agora você pode atualizar as permissões de usuário, objeto, campo e personalizado em um conjunto de permissões diretamente no modo de exibição de resumo. Antes, era possível fazer apenas edições de permissões mínimas no resumo. Entregamos esse recurso graças às suas ideias compartilhadas no IdeaExchange.

* **Ideia entregue: Gerenciar conjuntos de permissões inclusos no resumo...**
  Edite quais conjuntos de permissões estão incluídos em um grupo de conjuntos de permissões sem sair da visualização de resumo. Antes, essas informações eram somente leitura, assim, essa atualização facilita a realização de ações ao revisar o grupo de conjuntos de permissões. Entregamos esse recurso graças às suas ideias compartilhadas no IdeaExchange.

* **Ideia entregue: Revisar as configurações de guia em Resumos de acesso**
  Veja facilmente as guias que um usuário pode acessar ou as guias incluídas em um conjunto de permissões ou grupo de conjuntos de permissões. Usar as visualizações de resumo é mais rápido do que pesquisar em várias páginas de Configuração, que antes eram necessárias para obter essas informações. Entregamos esse recurso graças às suas ideias compartilhadas no IdeaExchange.

* **Ideia entregue: Visualizar e gerenciar conjuntos de permissões,...**
  Se você quiser saber a quais conjuntos de permissões, grupos e filas um usuário está atribuído, terá sorte. Com os aprimoramentos no resumo de acesso do usuário, você pode adicionar ou remover um usuário de um ou mais conjuntos de permissões, grupos ou filas. Você também pode pesquisar, classificar e atualizar as listas em cada seção de resumo.

> 📄 **Notas Completas:** consulte os detalhes completos na página do tópico [Segurança & Permissões](./releases/summer_25/security.md).


---

### ☀️ Summer-26

* 💻 **Apex**: Acesse o arquivo de notas de versão em [./releases/summer-26/apex.md](./releases/summer-26/apex.md).
* ⚙️ **Flow & Automação**: Acesse o arquivo de notas de versão em [./releases/summer-26/flow.md](./releases/summer-26/flow.md).
* 🔌 **Integrações & APIs**: Acesse o arquivo de notas de versão em [./releases/summer-26/integrations.md](./releases/summer-26/integrations.md).
* ⚡ **Lightning Web Components (LWC)**: Acesse o arquivo de notas de versão em [./releases/summer-26/lwc.md](./releases/summer-26/lwc.md).
* 🔒 **Segurança & Permissões**: Acesse o arquivo de notas de versão em [./releases/summer-26/security.md](./releases/summer-26/security.md).

---

### 🌸 Spring 26

#### 💻 Apex

* **Atualize o Apex code e os fluxos para alterar o comportamento de...**
  Para otimizar o desempenho após atualizações em grande escala em grupos ou papéis, o Salesforce agora realiza alguns recálculos de compartilhamento de modo assíncrono. Se o Apex code e os fluxos exigirem que os registros de compartilhamento sejam atualizados imediatamente, o código e os fluxos poderão ser interrompidos quando essa atualização de versão for imposta. Atualize classes, testes e fluxos do Apex que atualizam a associação ao grupo ou papéis se eles dependem de recálculo de compartilhamento síncrono. Essa atualização estará disponível da versão Spring '26 em diante.

* **Estenda o Data 360 usando código personalizado com extensão de...**
  Com a extensão de código, você pode levar seu código do Python personalizado para o Data 360 para estender os recursos nativos do Data 360. Se os recursos nativos do Data 360 não atenderem aos seus requisitos de negócios, implemente sua lógica personalizada em recursos compatíveis do Data 360, como transformações de dados em lote. Por exemplo, se você precisar de transformações de dados avançadas para seu caso de uso de negócios, poderá implementar a lógica de negócios personalizada no Data 360 para implementar seus requisitos. O SDK de Código personalizado de dados é o kit de ferramentas para criar e validar código personalizado para extensão de código.

* **Acelere a implantação de dados do Inspetor DX com SOQL**
  Acelere seu processo de implementação no Inspetor DX usando consultas SELECT para definir os registros que você deseja implementar. Insira as consultas Salesforce Object Query Language (SOQL) para buscar registros e campos específicos da sua organização de origem. Esse recurso é uma alternativa mais rápida aos filtros, permitindo que você busque dados com base em critérios complexos instantaneamente.

* **Faça o escape do atributo de rótulo de elementos <apex:inputField>...**
  Para evitar a execução de código mal-intencionado em ataques de script entre sites (XSS) em suas páginas do Visualforce, esta atualização de versão escapa ao atributo label das suas tags de <apex:inputField>. Essa atualização foi disponibilizada inicialmente na versão Winter '23.

* **Implemente componentes do Apex mais rapidamente executando apenas...**
  Para reduzir o tempo de implantação do componente Apex, use o novo nível de teste de RunRelevantTests para executar apenas os testes relevantes para suas alterações de código. Esse recurso determina automaticamente quais testes executar com base em uma análise da carga útil da implementação e das dependências da carga útil. Para um controle detalhado, você pode anotar classes de teste para que elas sejam executadas independentemente da carga útil da implementação ou quando os componentes especificados forem novos ou modificados. Essa abordagem direcionada aumenta a velocidade e a confiabilidade da sua implementação enquanto mantém a qualidade do código e os requisitos de cobertura.

* **Usar cursores do Apex para suporte expandido aos resultados da...**
  Use cursores do Apex e cursores de paginação para trabalhar com grandes conjuntos de resultados de consulta SOQL em partes gerenciáveis. Esse recurso, agora disponível ao público em geral, inclui aprimoramentos desde a versão beta. Os cursores padrão, quando combinados com o Apex enfileirável, abordam as limitações do Apex em lote. Os cursores de paginação são projetados para elementos da IU, como listas de registros de várias páginas. Ambos os tipos de cursor do Apex podem passar para frente e para trás por conjuntos de resultados e podem lidar com processamento de alto volume e alto recurso.

* **Extrair valores da lista de opções com base no tipo de registro**
  Obtenha os valores de todos os campos da lista de opções para um determinado tipo de registro usando o novo método ConnectApi.RecordUi.getPicklistValuesByRecordType(objectApiName, recordTypeId). Entregamos esse recurso devido à sua ideia no IdeaExchange.

* **Expor métodos de controlador REST e AuraEnabled do Apex como ações...**
  Crie ações do agente com base em classes do Apex anotando métodos nessas classes, gerando um documento de especificação OpenAPI e implementando esse documento em sua organização. Gerencie os métodos expostos como APIs no Catálogo de API. Esse recurso agora está disponível ao público em geral.

> 📄 **Notas Completas:** consulte os detalhes completos na página do tópico [Apex](./releases/spring_26/apex.md).

#### ⚙️ Flow & Automação

* **Flow Builder**
  Modifique fluxos acionados por registro e acionados por agendamento com Agentforce. Navegue pelo Flow Builder com caminhos recolhíveis e novos controles do mouse. Classifique e edite registros no componente de tela Tabela de dados. Personalize fluxos de tela com substituições de estilo no nível do componente. Envie mensagens para públicos grandes e use elementos Aguardar em fluxos de transmissão assíncronos. Use decisões, regras de saída, condições de reentrada e muito mais em fluxos acionados por ativação. Envie emails do Marketing Cloud Engagement em fluxos acionados por segmento, acionados por evento, acionados por ativação e de transmissão. Acione fluxos acionados por evento de automação quando os registros relacionados a um indivíduo forem alterados.

* **Atualizações do Flow Builder**
  Faça alterações em fluxos acionados por registro e agendados usando linguagem natural. Facilite a navegação na tela do Flow Builder com caminhos de ramificação recolhíveis e controles de rolagem de mouse mais intuitivos. Acesse o painel Agentforce sem a configuração do administrador.

* **Obtenha fluxos de rascunho mais precisos com IA (disponível ao...**
  O Agentforce divide seus requisitos de negócios em tarefas específicas e dá instruções específicas de IA generativa sobre como concluir essas tarefas, tornando seus fluxos acionados por registro ou acionados por agenda mais precisos. Insira suas instruções e deixe a IA trabalhar. Você também pode usar e modificar as instruções de exemplo e gerar o fluxo de rascunho.

* **Evolva fluxos iterativamente com Agentforce**
  Melhore e modifique fluxos acionados por registro e acionados por agenda usando linguagem natural sem começar do zero. Use avisos conversacionais no painel Agentforce para adicionar, modificar e excluir elementos em um fluxo. Esse recurso não consome créditos de IA generativa.

* **Simplifique seu layout do Flow Builder recolhendo elementos de...**
  Gerencie fluxos complexos com mais eficiência ocultando detalhes desnecessários na tela. Agora você pode recolher e expandir elementos de ramificação com o Flow Builder, incluindo Aguardar, Decisão, Loop, Experimento de caminho e Ações assíncronas, ajudando você a se concentrar nas principais partes do fluxo. Para garantir um fluxo de trabalho consistente, o Flow Builder lembra suas preferências específicas de expandir e recolher. Esse layout é salvo automaticamente e localmente no navegador, facilitando o retorno ao trabalho sem alterar a visualização para outros usuários.

* **Navegue em fluxos grandes mais rapidamente recolhendo ou expandindo...**
  Recolha ou expanda todos os elementos de vários caminhos, como Aguardar, Decisão, Loop, Experimento de caminho e Ações assíncronas, na tela do Flow Builder com um clique. Esse recurso simplifica sua visualização para que você possa reduzir a bagunça visual e se concentrar nas partes importantes do fluxo. Você ainda pode expandir ou recolher elementos individuais conforme necessário. O Flow Builder se lembra do seu layout atual automaticamente, mesmo que você saia do fluxo. Esse layout é salvo localmente no navegador para que você possa retomar do ponto em que parou sem alterar a visualização para outros usuários.

* **Configurar o painel Agentforce sem configuração do administrador**
  Os usuários agora podem migrar rapidamente para o painel Agentforce e acessar novos recursos, como criar, resumir ou evoluir um fluxo. Esse recurso não consome créditos de IA generativa.

* **Visualize mais facilmente as descrições de variável de saída e...**
  Os balões de informações para variáveis de saída de subfluxo agora mostram a descrição personalizada definida pelo administrador ou desenvolvedor. Se nenhuma descrição personalizada for definida, o texto padrão aprimorado conduzirá você a atribuir um recurso. Além disso, visualize descrições para os recursos de entrada de um subfluxo em uma bolha de informações mesmo que o recurso não esteja incluído. Antes, era preciso habilitar o recurso de entrada para saber se era necessário.

> 📄 **Notas Completas:** consulte os detalhes completos na página do tópico [Flow & Automação](./releases/spring_26/flow.md).

#### 🔌 Integrações & APIs

* **Notas da versão 26.4 da B2C Commerce API**
  Acompanhe os novos recursos e funcionalidades da B2C Commerce API.

* **Notas de versão do B2C Commerce API 26.3**
  Acompanhe os novos recursos e funcionalidades da B2C Commerce API.

* **Usar clientes de Public API com o Account Manager**
  O Account Manager agora oferece suporte a fluxos de concessão de código de autorização com PKCE (Proof Key for Code Exchange) para clientes de Public API. Troque tokens OAuth com segurança por aplicativos cliente que não podem armazenar com segurança um segredo do cliente. O PKCE fornece um fluxo de autenticação mais seguro para aplicativos móveis e de desktop nativos de página única.

* **Atribuir mais funções administrativas a clientes de API**
  Agora você pode atribuir a função de administrador de conta ou administrador de API a um cliente de API diretamente da página de detalhes do cliente de API do Account Manager. Esta atualização simplifica o gerenciamento de clientes de API, economizando tempo para os administradores ao gerenciar usuários técnicos e integrações. Os administradores de conta podem gerenciar ambas as funções. Os administradores de API só podem gerenciar a função de Administrador de API.

* **Identificar clientes de API compartilhada com indicadores e avisos**
  Entenda como as alterações no cliente de API afetam outras organizações que usam o mesmo cliente de API. Ao editar uma configuração de cliente compartilhada, indicadores e avisos agora aparecem na lista de clientes de API, na página de detalhes do cliente de API e nas caixas de diálogo de confirmação. Esses aprimoramentos de visibilidade ajudam a determinar quando criar um novo cliente de API dedicado para uma organização.

* **Explorar a referência de API REST atualizada do Data 360 Connect**
  A Referência da API REST do Data 360 Connect tem um novo layout de três painéis. Procure pontos de extremidade agrupados à esquerda, revise os detalhes do ponto de extremidade no centro e acesse exemplos de carga útil à direita.

* **Expor SOQL personalizado em chamadas à API REST usando a API de...**
  Use a API de consulta nomeada para definir e expor consultas SOQL personalizadas, ou APIs de consulta nomeada, como ações escalonáveis para clientes da API REST. As APIs de consulta nomeada podem recuperar dados de forma rápida e mais eficiente do que os processos existentes de Fluxo ou Apex.

* **Atualizar URLs instanciados no tráfego de API (atualização de versão)**
  Para evitar interrupções quando o Salesforce encerrar o suporte para tráfego de API que use um URL instanciado incorreto, certifique-se de que o tráfego de API para sua organização use o URL de login do Meu domínio da organização. Inicialmente disponível na versão Summer '25, essa atualização de versão estava agendada para imposição na versão Spring '26, mas adiamos a imposição para a Summer '26.

> 📄 **Notas Completas:** consulte os detalhes completos na página do tópico [Integrações & APIs](./releases/spring_26/integrations.md).

#### ⚡ Lightning Web Components (LWC)

* **Componentes do Aura em fluxos do Salesforce Scheduler estão...**
  Os componentes do Aura em fluxos do Salesforce Scheduler estão agendados para descontinuação em 14 de fevereiro de 2027. Você pode continuar usando os componentes do Aura até essa data, mas recomendamos a transição para sites do LWR para fluxos de agendamento modernizados.

* **Integre componentes da Web Lightning personalizados em painéis para...**
  Adicione componentes da Web Lightning (LWC) personalizados diretamente aos painéis do Lightning para criar visualizações de dados interativas em tempo real que vão além das funcionalidades padrão do painel. Filtre, explore e aja com base em dados imediatamente sem sair do painel. Por exemplo, um analista de negócios pode usar um LWC personalizado para exibir um gráfico de cascata ou outras visualizações que não estejam disponíveis em painéis padrão.

* **API versão 66.0 do LWC**
  Atualize a versão da API de seus componentes para usar novos recursos e melhorias. A versão dos componentes da Web Lightning garante que os componentes existentes não sejam afetados quando o Salesforce envia novos recursos, correções de bugs e melhorias de desempenho que alteram o comportamento existente. O controle de versões também ajuda o Salesforce a descontinuar os recursos legados.

* **Usar expressões de modelo complexas em seus componentes da Web...**
  Adicione lógica de apresentação sofisticada aos arquivos de modelo de componente da Web Lightning e remova código extra da implementação do componente. Um componente que renderiza uma interface do usuário agora pode usar expressões JavaScript complexas diretamente em seu arquivo de modelo HTML. Use expressões de modelo complexas sempre que usar propriedades básicas.

* **Obtenha definições de tipo completas para componentes de base do...**
  Construa seus aplicativos com confiança com a conclusão da distribuição de TypeScript para todos os componentes básicos do Lightning.

* **Atualize seus componentes personalizados para uso em configuração...**
  Torne seus componentes da Web do Aura e do Lightning personalizados acessíveis ao Agentforce em Configuração adicionando descrições de propriedade e componente relacionados à IA aos arquivos js-meta.xml e .design. As descrições de propriedade e componente de IA são usadas apenas em organizações que têm Configuração com Agentforce (beta) habilitado.

* **Verificar se há erros na correção de reidratação de nó do DOM...**
  Para melhorar a consistência da estrutura, os componentes da Web Lightning agora se rehidratam apenas quando estão ativamente conectados ao DOM. Por exemplo, a rehidratação ignora nós separados para evitar que métodos de ciclo de vida como o renderedCallback sejam disparados várias vezes. Anteriormente, certos casos de borda permitiam que nós DOM desconectados fossem rehidratados, o que podia acionar atualizações de estado reativas ou invocações de função em componentes desconectados.

* **Trabalhar com mais ferramentas de MCP para desenvolvimento do LWC...**
  Criar aplicativos mais rapidamente com as ferramentas MCP para desenvolvimento do LWC.

> 📄 **Notas Completas:** consulte os detalhes completos na página do tópico [Lightning Web Components (LWC)](./releases/spring_26/lwc.md).

#### 🔒 Segurança & Permissões

* **Usar a segurança OAuth com sua conexão de banco de dados SQL do...**
  Aumente a segurança dos dados conectando-se ao Banco de Dados SQL do Microsoft Azure usando a autenticação OAuth 2.0. Agora você pode fornecer valores de autenticação do Azure diretamente, eliminando a necessidade de uma configuração separada do provedor de autenticação externo.

* **Atualize para a Segurança do OAuth para suas conexões externas do...**
  Aumente a segurança de dados usando a autenticação do OAuth 2.0 com seus conectores de entrada e saída externos do Salesforce. Não há suporte para a API SOAP login() após a versão 64. Para manter a sincronização de dados, você deve atualizar todas as conexões externas existentes do Salesforce para usar o OAuth antes da versão Summer '27.

* **Usar a segurança OAuth com sua conexão de banco de dados SQL do...**
  Aumente a segurança dos dados conectando-se ao Banco de Dados SQL do Microsoft Azure usando a autenticação OAuth 2.0. Agora você pode fornecer valores de autenticação do Azure diretamente, eliminando a necessidade de uma configuração separada do provedor de autenticação externo.

* **Atualize para a Segurança do OAuth para suas conexões externas do...**
  Aumente a segurança de dados usando a autenticação do OAuth 2.0 com seus conectores de entrada e saída externos do Salesforce. Não há suporte para a API SOAP login() após a versão 64. Para manter a sincronização de dados, você deve atualizar todas as conexões externas existentes do Salesforce para usar o OAuth antes da versão Summer '27.

* **Alterações de distorção da API no Lightning Web Security**
  O Lightning Web Security (LWS) inclui novas proteções de segurança com mais distorções para APIs da Web. Regras do ESLint que correspondem às distorções também estão disponíveis.

* **Segurança, identidade e privacidade**
  Os redirecionamentos terminam para nomes de host legados, incluindo nomes de host instanciados em chamadas à API. A criação de aplicativo conectado é desabilitada por padrão para todas as organizações do Salesforce. O Backup e recuperação do Salesforce agora é um aplicativo nativo. Além disso, as Solicitações de privacidade cumprem as solicitações de Direito de ser esquecido de seus clientes.

* **Fazer backup e recuperar em seguida**
  Salesforce Backup & Recover Next agora é um aplicativo nativo. Gerencie backups e recupere dados diretamente em sua organização com uma interface de usuário atualizada e detecção automática de região.

* **Proteja e recupere seus dados com o Backup e recuperação Avançar**
  O Salesforce Backup & Recover Next agora é um recurso nativo do Salesforce que ajuda você a proteger seus dados do Salesforce gerando automaticamente backups diários de seus dados. Use esses backups para identificar e recuperar rapidamente da perda ou corrupção de dados. Em vez de gerenciar seus backups externamente, você pode ativá-los e gerenciá-los diretamente em sua organização.

> 📄 **Notas Completas:** consulte os detalhes completos na página do tópico [Segurança & Permissões](./releases/spring_26/security.md).


---

### 🌸 Spring 25

#### 💻 Apex

* **Batch Test with Agentforce Testing Center**
  O teste é essencial para iniciar um agente confiável, mas o teste de turno de enunciados é demorado. Com o Centro de teste, agora você pode testar em escala usando testes em lote em seu sandbox, reduzindo a quantidade de tempo de teste de dias para minutos. Fornecemos um modelo CSV para ajudá-lo a colocar seus dados em ordem e pronto para uso.

* **Call an Agent from a Flow or Apex Class**
  Coloque os tópicos, ações e recursos de raciocínio dos agentes para funcionarem para seus usuários fora de uma janela de chat com ações invocáveis do agente personalizadas. Chame um agente de serviço Agentforce (ASA) ou agente Agentforce (padrão) para concluir tarefas em segundo plano ou acionadas por evento de qualquer lugar que você possa chamar um fluxo ou classe do Apex. Adicione uma ação invocável a um fluxo ou classe do Apex e especifique a tarefa que o agente conclui e as condições que acionam o agente. Para ações invocáveis associadas a um agente de ASA, você também pode especificar as variáveis de contexto que você definiu para seu agente para passar ao agente as informações de que ele precisa. Você pode fazer várias chamadas ao mesmo agente para lidar com tarefas relacionadas ou chamar vários agentes do mesmo fluxo para lidar com tarefas mais especializadas.

* **Batch Test Agents with Testing API**
  Reduce testing time and test your agent at scale with Testing API, which enables you to programmatically create and run multiple tests in one batch. Testing API gives you access to functionality in Agentforce Testing Center.

* **Optimize Resources Using Merge Write Mode for Batch Transforms**
  Merge write mode only processes new and updated records when writing to a batch transform output object. This optimizes resource usage and prevents unnecessary reprocessing.

* **Delivered Idea: Compress and Extract Zip Files in Apex (Generally...**
  Use o namespace Compression e aproveite uma biblioteca zip do Apex nativa para compactar e extrair arquivos. Compacte facilmente arquivos em um arquivo zip de blobs e descompacte diretamente os arquivos armazenados em um arquivo zip para blobs. Otimize a compactação especificando o método e o nível de compactação. Você pode compactar vários anexos ou documentos como um blob do Apex em um arquivo zip. Também pode especificar os dados a serem extraídos do arquivo zip sem descompactar todo o arquivo zip. Entregamos esse recurso graças às suas ideias compartilhadas no IdeaExchange.

* **Delivered Idea: Evaluate Dynamic Formulas in Apex (Generally...**
  Fórmulas dinâmicas no Apex oferecem suporte a sObjects e objetos do Apex como objetos de contexto. Use os métodos de classe no namespace FormulaEval para criar e avaliar fórmulas dinâmicas. Esse recurso, agora disponível ao público em geral, dá suporte ao acesso a campos de relacionamento polimórficos. Você também pode fazer referência a pesquisas padrão e pesquisas personalizadas em campos de fórmula. Entregamos esse recurso graças às suas ideias compartilhadas no IdeaExchange.

* **Scale Your Concurrent Long-Running Apex Requests Limit Based on...**
  The default limit for the number of synchronous concurrent transactions for long-running Apex requests now depends on the type and number of licenses in your org. Scaled license-based limits can avoid service disruptions caused by the limit, increase system stability with minimal risk to performance, and improve resource allocation. To ensure fair usage, the limit is capped at a maximum of 50 Apex requests. The minimum number of long-running concurrent Apex requests remains at 10.

* **Pause and Resume Scheduled Jobs by Using Apex**
  Com os novos métodos na classe System, você pode programaticamente pausar e retomar trabalhos agendados do Apex. Esse recurso complementa a capacidade de monitorar trabalhos agendados na IU de Configuração, que foi lançada na versão Summer '24. Para pausar ou retomar um trabalho agendado, especifique o nome do trabalho ou cronTriggerId. Chamar os métodos de pausa e retomada conta para o limite da instrução DML.

> 📄 **Notas Completas:** consulte os detalhes completos na página do tópico [Apex](./releases/spring_25/apex.md).

#### ⚙️ Flow & Automação

* **Track Generated Content Quality and Feedback in Flow Builder**
  Mantenha-se proativo com alertas em tempo real quando a toxicidade ou o feedback negativo de qualquer recurso de IA generativa exceder o limite definido e fique de olho nas pontuações de fidelidade da geração aumentada de recuperação que ficam abaixo do valor aceitável. Use esse feedback para aprimorar continuamente a qualidade do seu conteúdo e refinar respostas de IA generativa em seus recursos.

* **Create Coupons Using a Guided Workflow**
  Use o fluxo de trabalho guiado para configurar códigos de cupom personalizados para qualquer promoção que você queira oferecer. Agora você não precisa acessar a página de Registro da promoção para configurar cupons na sua loja. No fluxo de trabalho guiado, você pode definir horários de início e término para seus cupons, especificar limites de resgate por comprador e definir um limite geral sobre o número total de usos, tudo em um processo fácil.

* **Customize and Extend Commerce Messages Using Flow**
  O recurso Mensagens de comércio agora está integrado ao Fluxo. Use o Flow Builder para adicionar mais elementos e ações aos fluxos de mensagens padrão, como enviar ao cliente uma mensagem SMS ou criar um caso de suporte.

* **Create a Real-Time Data Action Using Automation Event-Triggered Flow...**
  Execute an action in seconds by creating a custom real-time Data Graph event in automation event-triggered flow. Define the event that triggers the flow by using real-time data from Data Cloud without persisting the event to the Event Library. To define the event, you select a real-time data graph and a data model object that include the fields that trigger the flow, and then specify the conditions that trigger the flow.

* **Simplify Mobile Forms with Data Capture Flow (Generally Available)**
  Crie formulários dinâmicos responsivos no Flow Builder com o tipo de fluxo Captura de dados. A Captura de dados é a solução do Salesforce Field Service para formulários que abrangem tudo, desde tarefas pré-trabalho, como protocolos de segurança, até avaliações ambientais. Com a Captura de dados, crie formulários que usam lógica condicional para simplificar a experiência móvel, responder a entradas de usuários móveis e reduzir o tempo de conclusão da tarefa. Antes, era preciso integrar aplicativos externos para criar formulários que eram iniciados no aplicativo móvel. Com o fluxo da Captura de dados, os formulários são integrados perfeitamente à Salesforce Platform e são adaptados à tarefa.

* **Build Dynamic Forms with Discovery Framework Data Capture Flow...**
  Crie formulários dinâmicos responsivos no Flow Builder com o tipo Fluxo de captura de dados do Discovery Framework. Use as perguntas de avaliação do Discovery Framework para criar formulários compatíveis com dispositivos móveis que funcionam mesmo em áreas com baixa conectividade. Adicione lógica condicional e perguntas superior e secundária para garantir que seus trabalhadores móveis vejam apenas as perguntas necessárias. Mantenha uma trilha de auditoria clara reutilizando e fazendo o controle de versões de perguntas em vários formulários.

* **Increase the Efficiency of Your Loan Approval Workflow**
  Ajude seus usuários a realizar verificações relacionadas a empréstimo com finalidade conectando-se aos serviços externos preferidos por meio dos novos modelos de integração. Com os serviços de origem de empréstimo automatizados, melhore a eficiência e a precisão e reduza o esforço manual para verificar se os solicitantes atendem aos critérios de aprovação de empréstimo.

* **Service Process Automation**
  Os modelos de processo de serviço predefinidos ajudam você a começar mais rapidamente.

> 📄 **Notas Completas:** consulte os detalhes completos na página do tópico [Flow & Automação](./releases/spring_25/flow.md).

#### 🔌 Integrações & APIs

* **Book and Pay Easily with Payment Integration**
  Simplifique as reservas de compromisso com a capacidade de pagar por compromissos de serviço. Defina preços para compromissos configurando cartões de taxa para combinações de tipos de trabalho e territórios de serviço. Para compromissos de saída, seus representantes de suporte ao cliente podem gerar e enviar links de pagamento aos clientes. Para compromissos de entrada, seus clientes podem pagar por seus compromissos enquanto os reservam. Além disso, envie emails automaticamente aos clientes para pagar suas reservas usando novos modelos de email para pagamentos.

* **Get Faster Agent Responses with Text Streaming**
  Agentforce (Default) progressively streams plain text responses from the large language model (LLM) in the agent conversation.

* **Improve Agent Quality with New Test Metrics in the Testing API**
  Write more types of tests in the Testing API with new response-quality metrics for coherence, completeness, conciseness, and response latency. These metrics help you identify areas where you can improve your agent.

* **Connect Agentforce Agents to Any Application with the Agent API**
  Improve user engagement and automate key processes by using Agent API to connect your applications and platforms to Agentforce agents. With standardized API endpoints, you can integrate agents from your website, create and deploy headless agents, and connect agents to your favorite platforms and workflows.

* **New Connect REST API Resources for Einstein Bots (Beta)**
  Teste a precisão de um modelo de intenção e otimize seus enunciados com os recursos da API de Previsão de enunciados disponíveis com Bots do Einstein.

* **Add Assets to Collections in Bulk**
  Chega de adicionar ativos a coleções um por vez. Agora você pode adicionar itens a coleções em lotes. Também é possível adicionar vários itens a várias coleções com uma única ação.

* **Data Integration**
  Obtenha uma visão melhor do resultado de uma receita com novos recursos para criar dados de amostra e examinar o conteúdo em visualizações de receita. Monitore o fluxo de dados e as exclusões de receita na Trilha de auditoria. Controle o acesso aos dados com base nos territórios atribuídos ao usuário (agora disponível ao público em geral).

* **Import Inventory in Bulk**
  Adicione o inventário e atualize registros existentes em massa usando o aplicativo Omnichannel Inventory em vez de APIs ou de adicionar registros individualmente. Use o arquivo CSV de amostra fornecido para preparar seu inventário. Você então poderá importar as informações usando um arquivo CSV ou JSON.

> 📄 **Notas Completas:** consulte os detalhes completos na página do tópico [Integrações & APIs](./releases/spring_25/integrations.md).

#### ⚡ Lightning Web Components (LWC)

* **Enable LWC Stacked Modals (Release Update)**
  Como parte da migração interna do Salesforce do Aura para LWC, mais modais no Lightning Experience agora são renderizados usando o LWC. Essa atualização fornece desempenho aprimorado, especialmente ao trabalhar com inúmeros campos em um modal de criação ou edição de registro. Agora você também pode usar Formulários dinâmicos em um modal aberto de um campo Criar da pesquisa na maioria das páginas de registro habilitadas para LWC. Quando você habilita essa atualização, espere pequenas mudanças no comportamento do modal. Essa atualização foi disponibilizada inicialmente na versão Summer '24.

* **LWC API Version 63.0**
  Atualize a versão da API de seus componentes para usar novos recursos e melhorias. A versão dos componentes da Web Lightning garante que os componentes existentes não sejam afetados quando o Salesforce envia novos recursos, correções de bugs e melhorias de desempenho que alteram o comportamento existente. O controle de versões também ajuda o Salesforce a descontinuar os recursos legados.

* **Custom Components Must Specify an API Version**
  A chave apiVersion é um elemento obrigatório para todos os componentes personalizados. Componentes personalizados que foram salvos antes sem uma chave apiVersion no arquivo de ajustes do componente .js-meta.xml têm uma chave apiVersion adicionada ao arquivo de ajustes automaticamente quando o componente é recuperado do Salesforce.

* **Wire Adapters Have Improved Type Checking**
  A partir da versão Spring '25, os usuários do TypeScript terão uma melhor verificação de tipo de configuração de @wire e valores de propriedade. A verificação de tipo também resolve propriedades reativas para o tipo usado pelo componente. Por exemplo, uma string que começa com $ como $reactiveProp.

* **Update JavaScript Selectors to Remove Extra Whitespace**
  Revise seus seletores JavaScript para ignorar espaços em branco (espaços, guias etc.). Essa alteração elimina inconsistências na renderização de espaço em branco extra.

* **Develop Lightning Web Components Faster in a Real-Time Preview of...**
  O Desenvolvedor local agora está disponível ao público em geral para aplicativos Lightning. Fizemos algumas alterações desde a versão beta. Ao usar o Local Dev, você pode desenvolver seus componentes da Web Lightning em uma visualização em tempo real do aplicativo Lightning sem implementar código nem atualizar manualmente o navegador. O desenvolvedor local está em beta para sites do Lightning Web Runtime.

* **New and Changed Lightning Web Components**
  Crie a interface do usuário facilmente com componentes novos e alterados.

* **New and Changed Modules for Lightning Web Components**
  Do more with Lightning web components by using modules.

> 📄 **Notas Completas:** consulte os detalhes completos na página do tópico [Lightning Web Components (LWC)](./releases/spring_25/lwc.md).

#### 🔒 Segurança & Permissões

* **Secure Salesforce External Connections with OAuth 2.0**
  Use o OAuth 2.0 para criar uma conexão segura com uma organização externa do Salesforce que está adicionando seus dados ao CRM Analytics.

* **Enhance Security by Controlling Access to Agentforce**
  Controle o acesso ao Agentforce (padrão) com permissões específicas do tipo. Para usar o Agentforce (padrão), os usuários devem ter o grupo de conjuntos de permissões Acessar agente padrão do Agentforce ou ser um administrador com a permissão Personalizar aplicativo. Usuários que antes acessaram o Agentforce (padrão) apenas com a permissão Modificar metadados não terão mais acesso.

* **Enhance Security with the Customer Verification Topic**
  Add the new Customer Verification topic to your Agentforce Service agent to ensure secure access to topics and actions to be taken only on behalf of a specific user. You decide which topics and actions require user verification based on your company’s security standards and requirements. For example, control access to actions that update reservations, process refunds, or access customer account details.

* **Improve Content Security Through Prompt Injection Detection (Beta)**
  You can now enable prompt injection detection in Einstein Trust Layer Setup to enhance your content security. Prompt injection detection together with the existing system policies provide an in-depth approach to prompt defense. Prompt defense is now consistently applied to all user prompts, bolstering security in Agentforce and embedded AI applications.

* **Secure Salesforce External Connections with OAuth 2.0**
  Use o OAuth 2.0 para criar uma conexão segura com uma organização externa do Salesforce que está adicionando seus dados ao CRM Analytics.

* **Get Improved Performance with the Enhanced Role List View**
  With a new user experience, you can view, sort, and filter user roles in a list format and edit roles inline. This enhancement makes it easier to manage role-based access control so that users see the data that they need.

* **Manage Permissions Sets with the Enhanced List View**
  Essa experiência de usuário aprimorada oferece uma navegação simplificada, opções de filtragem aprimoradas, recursos de pesquisa e um layout mais intuitivo. Esse aprimoramento facilita o gerenciamento e a navegação por conjuntos de permissões. As principais melhorias incluem opções de filtragem avançadas, um layout mais organizado e acesso mais rápido a ações críticas.

* **Enforce View Roles and Role Hierarchy Permission When Editing Public...**
  Com essa atualização, apenas usuários com a permissão Exibir papéis e hierarquia de papéis podem ver ou selecionar na lista de papéis da sua organização quando editam a visibilidade do modo de exibição de lista público. Essa atualização foi disponibilizada inicialmente na versão Spring '24. Se você não usar papéis, essa atualização não terá efeito.

> 📄 **Notas Completas:** consulte os detalhes completos na página do tópico [Segurança & Permissões](./releases/spring_25/security.md).


---

