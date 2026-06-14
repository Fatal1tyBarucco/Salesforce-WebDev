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

### ☀️ Summer 26

<details>
<summary><b>📄 ANALYTICS (Clique para expandir 27 alterações)</b></summary>

* **Tableau**
  Use o Tableau para analisar, explorar e tomar decisões quanto a seus dados com apenas alguns cliques. Crie visualizações interessantes e integre-as às páginas do Lightning para usá-las em fluxos de trabalho. O Tableau tem soluções de plataforma de análise empresarial para exploração profunda de dados.

* **Aprimoramentos de acessibilidade no Analytics**
  Saiba mais sobre pequenas alterações, mas importantes, que tornam as análises mais acessíveis.

* **Próximos recursos do Tableau lançados por mês**
  Recursos e alterações do Tableau Next são lançados com frequência mensal, portanto, volte em breve para as soluções mais recentes.

* **Próximos destaques do Tableau**
  Não perca os recursos do Tableau Next da última versão. Recapitule ou aprofunde-se nos recursos e oportunidades de aprendizado da versão Spring '26.

* **Analisar objetos do Data Lake no Tableau Next**
  Explore objetos de data lake (DLOs) grandes e objetos de modelo de dados (DMOs) diretamente de seus espaços de trabalho do Tableau Next. Resuma dados, identifique as principais métricas, filtre, classifique, agrupe e detalhe os dados em seu fluxo de trabalho. Simplifique sua visualização para descobrir relacionamentos de dados e analisar distribuições.

* **Garanta a consistência da identidade visual em seus relatórios e painéis com paletas de cores da marca**
  Reduza o esforço manual e mantenha visualizações de dados padronizadas e acessíveis em toda a sua organização usando uma paleta de cores da marca. Em vez de atualizar manualmente as cores em relatórios e painéis individuais, você pode configurar uma paleta de marca uma vez nas configurações de tema da sua organização e aplicá-la a gráficos de relatório e painel.

* **Integre componentes da Web Lightning personalizados em painéis para visualizações de dados interativas (disponível ao público em geral)**
  Adicione componentes da Web Lightning (LWC) personalizados diretamente aos painéis do Lightning para criar visualizações de dados interativas em tempo real que vão além das funcionalidades padrão do painel. Filtre, explore e aja com base em dados imediatamente sem sair do painel. Por exemplo, um analista de negócios pode usar um LWC personalizado para exibir um gráfico de cascata ou outras visualizações que não estejam disponíveis em painéis padrão.

* **Expanda os recursos de geração de relatórios com mais fórmulas no nível da linha**
  Poupe tempo em relatórios e gere percepções mais profundas incluindo até duas fórmulas em nível de linha em seus relatórios do Salesforce. Calcule valores diretamente no relatório sem adicionar campos de fórmula em um objeto. Por exemplo, calcule a taxa de comissão e a métrica de tempo para fechamento em um único relatório. Antes, os relatórios tinham suporte apenas para uma fórmula no nível da linha.

* **Proteger exportações do Excel desabilitando fórmulas**
  Proteja seus dados e reduza os riscos de segurança ao exportar relatórios como arquivos do Excel. Adicione um apóstrofo reta (') antes dos valores de campo que começam com caracteres como igual (=), mais (+), menos (-), etc., para evitar que programas de planilha interpretem incorretamente esses valores de célula como fórmulas. Isso protege contra possíveis manipulações de dados ou execução de código inadvertida. Antes, esse recurso tinha suporte apenas para exportações CSV.

* **Analisar tendências de dados com histórico de objeto de Insight calculado (beta)**
  Compare métricas e visualize como as percepções calculadas evoluem em períodos selecionados com dados de instantâneo do objeto Histórico do objeto de insight calculado (CIO). Selecione datas de instantâneo para gerar gráficos de tendências e relatórios agregados que impulsionam decisões estratégicas. Por exemplo, seus usuários podem rastrear o crescimento do Valor da vida útil do cliente (CLV) mês a mês nos últimos seis meses para informar sua estratégia de marketing.

* **Realizar drill downs mais rápidos com hierarquias de dimensões (beta)**
  Navegue por vários níveis de granularidade de dados diretamente em relatórios do Data 360 criados com base em modelos semânticos. Realize ações de detalhamento e totalização perfeitas em campos relacionados, como categorias de produto ou datas, usando hierarquias de dimensões. Em vez de selecionar campos individuais manualmente, mova-se perfeitamente entre os níveis para comparar rapidamente o desempenho entre os grupos de dimensões.

* **Obtenha percepções financeiras precisas com relatórios de moeda em relatórios do Data 360 (beta)**
  Analise dados de moeda no Salesforce e outras fontes de dados externas diretamente em seus relatórios do Data 360. Filtre, classifique e avalie esses valores para obter percepções mais claras sobre suas métricas financeiras. Esse recurso está disponível apenas para organizações de moeda única.

* **Integrar widgets de dados ativos do Data 360 em sites do Experience Cloud**
  Integre painéis com widgets que usam conectores ativos, incluindo o Data 360, diretamente em seus sites do Experience Cloud. Dê aos usuários acesso a informações atualizadas para que possam revisar, definir o perfil e traçar tendências em dados em tempo real diretamente nos fluxos de trabalho diários.

* **Melhore a responsividade do painel com reutilização de resultados para consultas ao vivo do Data 360**
  Reduza os custos de processamento e equilibre a atualidade dos dados configurando por quanto tempo reter os resultados da consulta. Quando você executa uma consulta com acesso a dados idêntico, o CRM Analytics recupera os resultados anteriores. Essa reutilização acelera os tempos de carregamento, especialmente para consultas grandes ou complexas.

* **Aumente o desempenho da consulta e a eficiência de dados com semijunções e antijunções (disponível ao público em geral)**
  Agora você pode adicionar semijunções e antijunções às suas consultas para identificar linhas duplicadas e sem correspondência sem codificação. Essa atualização não apenas acelera o desempenho da consulta recuperando apenas dados essenciais, mas também permite que você realize a análise de dados avançada com mais eficiência, tornando percepções de dados complexos acessíveis a todos. Esse recurso agora está disponível ao público em geral.

* **Filtrar painéis com diversos valores de texto simultaneamente**
  Limite seus dados exatamente ao que você precisa inserindo diversos valores de texto em filtros de painel, incluindo filtros globais. Antes, os filtros tinham suporte apenas para entradas de texto simples ou correspondência ampla. Agora, você pode inserir valores separados por vírgula para visualizar grupos específicos de registros, como vários números de SKU ou nomes de clientes, tudo de uma só vez.

* **Publicar layouts de painel grandes com impressão em largura total**
  Garanta que seus gráficos e tabelas largos sejam impressos claramente sem dados cortados usando a nova opção de largura total. Alterne da largura A4 padrão para um layout de full viewport para usar o espaço horizontal extra em tamanhos de papel A3 ou maiores. Todos os widgets de painel são atualizados para ocupar o espaço disponível para um relatório físico polido.

* **Gerenciar a visibilidade total da coluna em sua tabela comparativa**
  Personalize as tabelas do painel para mostrar apenas os resumos que são importantes para você. Agora você pode ocultar totais para colunas em que um resumo não adiciona valor, como proporções ou identificadores exclusivos. Essa atualização simplifica tabelas de comparação complexas focando a atenção nas métricas mais afetadas.

* **Exportar painéis do CRM Analytics como documentos com tamanhos de página personalizados (beta)**
  Baixe e compartilhe o CRM Analytics como PDFs com opções de dados e tamanhos de página personalizados. Por exemplo, seus usuários podem exportar uma página de painel em formato A4 e compartilhá-la no Slack para análises semanais.

* **Assinar widgets de painel em sites do Experience Cloud (beta)**
  Mantenha seus usuários da comunidade informados com assinaturas de widget de painel em seus sites do Experience Cloud. Envie atualizações automatizadas a seus usuários externos por email ou notificações de portal com base em suas agendas e filtros selecionados. O CRM Analytics aplica perfis de portal e regras de compartilhamento para que os usuários da comunidade vejam apenas dados autorizados.

* **Aumente o desempenho e a confiabilidade com o Inspetor de receita do CRM Analytics**
  Use o inspetor de receita para solucionar problemas e melhorar o desempenho. Aprofunde-se nos trabalhos de receita para visualizar as informações detalhadas em cada estágio do fluxo. Monitore o desempenho e o status de nós individuais. Você pode identificar rapidamente uma junção lenta ou um nó de transformação que falhou em fazer correções imediatamente.

* **Exportar agendas de receita para seu calendário externo para fácil rastreamento**
  Exporte suas agendas de receita do CRM Analytics como formato de calendário (ICS) para referência rápida e visibilidade em seu calendário. Por exemplo, compartilhe a agenda de execução de uma receita com as partes interessadas em outras equipes para coordenar a prontidão dos dados e os prazos de relatório.

* **Simplifique o backup de receita com upload e download diretos no Gerenciador de dados**
  Economize tempo e cliques acessando seu JSON de receita do CRM Analytics para backups ou edição. Agora você pode carregar e baixar suas receitas diretamente do Gerenciador de dados sem abrir o editor de receita.

* **Simplifique sua preparação de dados escrevendo em várias saídas do Data 360 em uma única receita**
  Consolide seus processos do Preparador de dados escrevendo em vários objetos do Data 360 Data Lake (DLO) em uma única receita do CRM Analytics. Minimize problemas com limites de execução de receita consolidando seu preparador de dados em uma receita. Por exemplo, insira seus dados e use nós de filtro para escrever dois subconjuntos separados e filtrados, um para o DLO de marketing e outro para o DLO de vendas, em uma única execução de receita. Isso reduz a complexidade e mantém suas transformações organizadas.

* **Melhore o desempenho da receita de dados de instantâneo com ações de inserção e inserção e exclusão otimizadas (disponível ao público em geral)**
  Reduza o tempo de processamento com execuções de receita de dados mais rápidas. Em vez de processar todas as linhas nos dados de instantâneo, as ações de inserção e atualização e exclusão otimizadas são executadas incrementalmente em subconjuntos dos dados, resultando em execuções mais rápidas. Esse recurso agora está disponível ao público em geral.

* **Melhore o desempenho de saída de gravação no Data 360 com ações otimizadas de adicionar, inserir e inserir e excluir (disponível ao público em geral)**
  Reduza o tempo de processamento ao escrever no Data 360 substituindo Objetos do Data Lake (DLO) existentes usando operações de saída otimizadas. Em vez de processar todas as linhas dos dados de saída, as operações otimizadas de adicionar, inserir e atualizar e excluir são executadas incrementalmente em subconjuntos dos dados de saída, resultando em execuções mais rápidas. Esse recurso agora está disponível ao público em geral.

* **Exportar seus dados do CRM Analytics para o Azure Data Lake (disponível ao público em geral)**
  Grave seus dados do CRM Analytics no Azure Data Lake da Microsoft com o conector de saída do Azure Data Lake. Escreva conjuntos de dados de saída de receita como um ou mais arquivos .csv em seu data lake, melhorando seus processos de negócios gerais com dados melhores. Por exemplo, você pode gerar dados de atendimento ao cliente processados e transformados para ajudar sua equipe a melhorar a satisfação do cliente. Esse recurso agora está disponível ao público em geral.

> 📄 **Notas Completas:** consulte os detalhes completos na página do tópico [ANALYTICS](./releases/summer_26/analytics.md).
</details>

<details>
<summary><b>📄 AUTOMATE (Clique para expandir 67 alterações)</b></summary>

* **Recursos de automação lançados por mês**
  Recursos e alterações de automação são lançados mensalmente. Consulte esta página para ver as versões mais recentes.

* **Melhorar o desempenho com lote para fluxos agendados**
  Otimize a execução de seus fluxos agendados e evite atingir os limites do controlador especificando um tamanho de lote personalizado. Particione entrevistas de fluxo em lotes menores variando de 1 a 200 diretamente do elemento de início do fluxo. Antes, os fluxos agendados processavam entrevistas em tamanhos de lote padrão de 200, o que pode esgotar recursos em automações complexas.

* **Evite corrigir manualmente referências de modelo de email depois de implementar fluxos em ambientes**
  Implemente fluxos com ações Enviar email entre ambientes sem referências de modelo de email corrompidas. Selecione um nome de modelo de email em uma lista suspensa na ação Enviar email. A ação armazena o modelo selecionado como uma referência que persiste em ambientes de implementação. Antes, a ação Enviar email salvava o modelo de email selecionado como um ID de modelo. Como o ID muda durante a implementação do fluxo de uma organização para outra, a ação falhou e exigia atualizações manuais.

* **Recolha caminhos de falha para focar seu fluxo principal**
  Simplifique seu fluxo e concentre-se no caminho de trabalho ocultando caminhos de falha. Expanda os caminhos de falha apenas quando estiver pronto para editá-los ou revisá-los. Seu navegador mostra seu estado de layout pessoal, assim, sua visualização de tela é exclusiva para você.

* **Usar ativações de DMO de streaming, mais elementos de fluxo e depurar com fluxos acionados por ativação aprimorada**
  Use ativações de objeto de modelo de dados (DMO) de streaming para acionar um fluxo para que você possa agir em eventos quase em tempo real. Agora você pode usar coleções em um elemento Decisão e usar o elemento Aguardar até o evento. A depuração também está disponível para solucionar problemas e testar seu fluxo.

* **Localizar e selecionar recursos mais facilmente no elemento Adicionar instruções de prompt**
  Encontre o recurso certo mais rapidamente ao usar o elemento Adicionar instruções de instrução em um fluxo de instrução acionado por modelo. O seletor de recursos aprimorado agrupa recursos e os exibe com seus rótulos e ícones intuitivos.

* **Seleção de recurso aprimorada em elementos de fluxo de estratégia de recomendação**
  Selecione recursos nos elementos Atribuição de recomendação e Limitar repetições usando listas de opções de recursos atualizadas. As listas de opções de recursos agora filtram os recursos disponíveis com base no tipo de dados necessário para cada campo. Antes, esses elementos usavam seletores de recurso legados.

* **Usar operadores de data na lógica de decisão**
  Crie ramificação baseada em data com operadores de data nos elementos de Decisão. Selecione operadores como É hoje, É aniversário de hoje e Último número de dias quando uma condição usar um tipo de dados de data. Essa atualização ajuda a modelar a lógica de recentidade e marco sem soluções alternativas de fórmula.

* **Agentforce para Fluxo agora é beta**
  As funcionalidades para criar, resumir e evoluir um fluxo com Agentforce mudaram de disponível ao público em geral para beta. Após o lançamento disponível ao público em geral, esses recursos não forneceram de modo consistente a precisão necessária para fluxos de trabalho complexos. Esses recursos permanecem acessíveis no Flow Builder enquanto melhorias no desempenho e na confiabilidade estão em andamento.

* **Atualizar fluxos de tela com avisos de linguagem natural (beta)**
  Itere rapidamente em fluxos de tela voltados para o usuário e reduza o risco de erros de configuração manual. Antes, você podia usar IA para modificar fluxos acionados por registro, acionados por agenda, acionados por alteração do sistema externo e fluxos que usam conectores como ações. Agora, use a IA generativa para modificar seus fluxos de tela existentes descrevendo as alterações com avisos de linguagem natural no painel Agentforce. Adicione, remova ou altere elementos de tela e ação sem ajustar manualmente a lógica no Flow Builder.

* **Visualizar nomes de registro relacionados e abrir o registro relacionado em colunas de pesquisa de tabela de dados**
  Exiba um nome de registro legível por humanos em vez de um ID do Salesforce no tempo de execução quando a coluna Tabela de dados for um campo de pesquisa. Além disso, escolha tornar o nome do registro relacionado um hiperlink que abre o registro relacionado em uma nova guia do navegador no tempo de execução. Você pode visualizar e navegar para a página do registro relacionado sem soluções alternativas complexas.

* **Personalizar fluxos de tela com substituições de estilo em mais componentes**
  Personalize fluxos de tela para seu público com opções de estilo expandidas. Agora você pode personalizar a aparência de mais componentes de fluxo de tela. Os novos componentes com suporte são Botão de ação, Endereço, Pesquisa de opção, Listas de opções dependentes, Email, Pesquisa, Nome, Telefone, Seletor, Alternância e URL.

* **Adicionar imagens de recurso estático para exibir texto sem sair do Flow Builder (disponível ao público em geral)**
  Procure e carregue facilmente imagens de recursos estáticos diretamente de dentro do componente Texto de exibição. A opção Imagem, que agora está disponível ao público em geral, inclui algumas alterações desde a versão beta. Antes, para adicionar uma imagem de recurso estática, você acessava a página Recursos estáticos em Configuração para obter os nomes das imagens existentes e usá-las no componente. Agora, em um processo de duas etapas simplificado, você pode pesquisar imagens existentes, carregar novas imagens e adicionar texto alternativo, tudo dentro do fluxo de tela.

* **Economizar espaço na tela com grupos de botões seletores em fluxos de tela**
  Use o novo componente de tela Grupo de botões de opção para apresentar horizontalmente (desktop) ou verticalmente (dispositivos móveis) opções empilhadas que são compactas e fáceis de ler. O componente Grupo de botões de opção funciona como o componente Botões de opção tradicional em que os usuários selecionam uma única opção no tempo de execução, mas suas opções aparecem empilhadas horizontalmente ou verticalmente. A orientação horizontal ou vertical reduz a rolagem e oferece uma alternativa moderna a botões de opção tradicionais, caixas de seleção ou listas de opções.

* **Expor a versão do tempo de execução do fluxo a componentes de tela personalizados**
  Controle como seu componente personalizado para fluxos de tela age com base na versão do tempo de execução do fluxo com o novo atributo flowRole. No componente da Web Lightning, crie uma propriedade que tenha o atributo flowRole="flowRuntimeApiVersion". Em seguida, use o valor dessa propriedade no tempo de execução para executar a lógica condicional. Retenha a funcionalidade em fluxos mais antigos enquanto incorpora recursos mais recentes ao mesmo componente.

* **Personalizar mensagens com dados integrados usando cliques, não código**
  Expanda suas opções de personalização de mensagens de email mapeando variáveis de conteúdo do Email Content Builder para campos de mesclagem no Flow Builder sem escrever Apex code. Quando você cria conteúdo de email com recursos personalizados, como variáveis manuais ou provedores de dados de registro, o Flow Builder renderiza entradas dinâmicas para esses campos na ação de mensagem. Essa abordagem de baixa codificação dá à sua equipe de marketing mais controle sobre como você usa dados para personalizar a comunicação com seus clientes.

* **Visualizar e restaurar o histórico de edição da versão do fluxo**
  Visualize um histórico de alterações salvas em uma versão do fluxo e restaure salvas anteriores. Sempre que você salva uma versão do fluxo, o sistema adiciona uma nova instância de salvamento ao seu histórico. Veja os salvos anteriores com a data, o usuário e um resumo dos elementos adicionados, editados ou excluídos.

* **Usar elementos e recursos de fluxo em todos os tipos de fluxo de marketing**
  Os recursos de fluxo e a disponibilidade de elementos agora são consistentes em todos os tipos de fluxo de marketing. Isso significa que recursos e elementos como Aguardar e Decidir estão disponíveis em todos os diferentes tipos de fluxo de marketing. A consistência entre os tipos de fluxo de marketing facilita a alternância perfeita entre os diferentes fluxos de marketing sem se preocupar com a compatibilidade do elemento ou a disponibilidade de recursos.

* **Coordenar jornadas complexas entre fluxos**
  Direcione indivíduos para um novo fluxo enquanto mantém seu progresso no fluxo original. Use o novo elemento Enviar para um fluxo para criar estratégias de engajamento do cliente mais sofisticadas e interrelacionadas. O elemento passa os identificadores do cliente para o fluxo de destino. O fluxo original e o fluxo de destino são executados de modo assíncrono, portanto, o fluxo original continua sendo executado enquanto o fluxo de destino funciona simultaneamente. Antes, orquestrar usuários por meio de vários fluxos exigia lógica personalizada complexa ou integrações de API.

* **Remover contatos automaticamente de um fluxo de engajamento ativo**
  Adicione o novo elemento Saída de um fluxo para deixar de enviar comunicações irrelevantes aos contatos quando eles atendem a uma meta ou condição específica. Antes, a remoção de contatos exigia intervenção manual ou lógica personalizada complexa. Agora, você pode optar por remover contatos de todas as versões do fluxo selecionado ou apenas da versão mais recente.

* **Personalize fluxos com acesso mais profundo aos dados de origem**
  Classifique e filtre dados de uma origem para criar um recurso de registro selecionado. O recurso de registro selecionado fornece acesso a dados aninhados de Gráficos de dados e outras fontes de dados, expandindo sua capacidade de personalizar fluxos.

* **Alcance públicos de uma categoria de fluxo simplificada**
  Crie fluxos com base em dados de público de uma única categoria de fluxo simplificada: fluxo de público. Selecione uma fonte de dados (Lista, Segmento, Registro ou Campanha) com base em seu caso de uso. O público do segmento substitui o fluxo acionado por segmento, proporcionando consistência entre fluxos baseados em público. As opções de lista, registro e campanha são baseadas nos novos tipos de fluxo.

* **Crie lógica mais precisa em elementos de decisão e regras de saída**
  Aplique uma lógica de elemento de Decisão mais eficiente com grupos de condições aninhados. Combine condições, adicione funções de agregação (Média, Soma, Máximo, Mínimo) para tipos de dados numéricos e use operadores de data expandidos, como É aniversário de hoje, É hoje e Último número de dias. Em regras de saída, adicione funções de agregação para tipos de dados numéricos.

* **Adicionar regras de saída que usam eventos**
  Para fluxos que oferecem suporte a regras de saída, como fluxos acionados por segmento, acionados por evento e sob demanda, agora você pode usar eventos para sair de um fluxo de um indivíduo. Por exemplo, se um cliente estiver em um fluxo acionado por evento para abandono do carrinho, use um evento de compra como uma regra de saída para que o cliente não receba mensagens irrelevantes.

* **Definir condições e critérios de nova entrada para fluxos acionados por evento**
  Para fluxos acionados por evento, agora você pode especificar condições de acionador adicionais com campos do objeto de modelo de dados primário especificado. Agora você também pode definir critérios de nova entrada para especificar se um indivíduo pode participar do fluxo novamente.

* **Adicionar mais pontos de contato e DMOs relacionados a fluxos acionados por evento com sinais de engajamento aprimorados**
  Agora você pode especificar pontos de contato de SMS e WhatsApp em seus fluxos. Ao criar sinais de engajamento, você também pode especificar um objeto de modelo de dados (DMO) de perfil em vez de apenas DMOs de engajamento. Os DMOs de perfil dão acesso direto aos dados de um indivíduo em um fluxo. Opcionalmente, adicione um objeto relacionado e faça referência a seus campos para definir o sinal de engajamento ou usar filtros. Por exemplo, crie um fluxo que é acionado depois que um cliente faz um pedido e, em seguida, inclua informações de item do pedido relacionado com um filtro que é acionado apenas se o gasto exceder um determinado valor

* **Filtrar o Analytics do elemento por intervalo de datas**
  Filtre a análise em elementos de fluxo por um intervalo de datas. As métricas em elementos refletem o período selecionado para que você possa analisar o desempenho recente, comparar períodos e alinhar a análise às janelas da campanha.

* **Visualizar métricas de resultado do caminho para experimento de caminho**
  Veja as métricas de resultado do caminho para elementos de experiência de caminho no painel de análise. Visualize o desempenho de cada caminho em um experimento. Compare caminhos e escolha um vencedor com melhor contexto.

* **Manter dados de registro de envio em fluxos de marketing**
  Os elementos de envio de marketing agora dão suporte ao registro de envio. Use a nova opção Reter dados de registro de envio para manter os dados de registro de envio e passá-los para o Marketing Cloud Engagement para relatórios e solução de problemas.

* **Os usuários agora podem visualizar dependências de fluxo**
  Usuários que não são administradores agora podem visualizar dependências de fluxo para seus fluxos de marketing no aplicativo Automação. Antes, apenas usuários com a permissão Gerenciar fluxo tinham acesso a essas informações.

* **Usar ativações de DMO de streaming, mais elementos de fluxo e depurar com fluxos acionados por ativação aprimorada**
  Use ativações de objeto de modelo de dados (DMO) de streaming para acionar um fluxo para que você possa agir em eventos quase em tempo real. Agora você pode usar coleções em um elemento Decisão e usar o elemento Aguardar até o evento. A depuração também está disponível para solucionar problemas e testar seu fluxo.

* **Usar elementos Aguardar e fluxos de teste com aprimoramentos de fluxo de transmissão**
  Fluxos de transmissão assíncronos agora dão suporte a elementos Aguardar. Agora você também pode testar fluxos de transmissão na depuração.

* **Usar conectores ilimitados do MuleSoft em fluxos acionados por segmento, acionados por ativação e de transmissão**
  Para casos de uso de segmentação e ativação, o MuleSoft para Fluxo: Os conectores de integração não consomem mais créditos de automação para fluxos acionados por segmento, acionados por ativação e de transmissão. Você pode usar conectores do MuleSoft nestes tipos de fluxo sem um MuleSoft para Fluxo: Licença do complemento de integração. Outros tipos de fluxo ainda exigem o MuleSoft para Fluxo: Licença do complemento de integração.

* **Notificar usuários com a ação Mostrar mensagem de toast**
  Forneça feedback imediato mostrando atualizações de status não invasivas ou mensagens de erro durante as transições da tela de fluxo. Essa nova ação declarativa mostra uma mensagem instantânea temporária na parte superior do viewport para manter seus usuários informados sem interromper a tarefa atual. Você também pode incluir a vinculação dinâmica ao Salesforce ou a uma página externa. Você não precisa mais criar soluções alternativas complexas para comunicar o sucesso ou a falha entre as telas.

* **Simplifique o fluxo de trabalho do usuário com a ação Abrir uma página**
  Inicie registros do Salesforce ou qualquer URL externo diretamente de seu fluxo, inclusive entre transições de tela, adicionando a ação Abrir uma página. Abra informações relacionadas, como uma oportunidade recém-criada, em uma guia separada sem exigir que os usuários saibam o fluxo.

* **Usar o modo de fórmula para entradas de ação sem criar recursos**
  Ignore a criação de recursos de fórmula para parâmetros de entrada de elemento de ação. Ao configurar parâmetros de entrada de ação no painel de propriedades do elemento Ação, você agora pode selecionar o modo Fórmula para criar fórmulas. Essa alteração reduz a bagunça em seus fluxos. Visualize visualizações de fórmula no painel de propriedades do elemento de ação e edite-as a qualquer momento, facilitando a leitura e a manutenção de suas configurações.

* **Controlar a visibilidade do caminho de tempo limite para ações assíncronas**
  Ações assíncronas agora mostram apenas o caminho Concluído por padrão quando adicionadas a fluxos no modo Layout automático, reduzindo a bagunça da tela. Ainda é possível incluir o caminho Tempo limite para ações assíncronas.

* **Usar o modo de transformação para entradas de ação sem adicionar elementos de transformação**
  Defina e edite suas transformações de dados diretamente no painel de propriedades Ação, simplificando tarefas complexas de mapeamento de dados. Ao configurar os parâmetros de entrada de um elemento de ação, selecione Modo de transformação para definir transformações de dados sem adicionar elementos de transformação ao seu fluxo. O modo de transformação ajuda a manter seus fluxos mais limpos reduzindo o número de elementos necessários para manipulação de dados.

* **Definir valores de campo diretamente para entradas definidas pelo Apex**
  Defina diretamente os valores de parâmetros de entrada definidos pelo Apex no painel de propriedades de ação, reduzindo recursos e elementos em seus fluxos. Cada campo aparece com sua própria entrada, eliminando a criação de variável separada e a atribuição de valor.

* **Simplificar a seleção de tipo de objeto para entradas de ação de sObject genéricas**
  O painel de propriedades da ação agora fornece um contexto melhor durante a configuração para ações com parâmetros sObject genéricos. Quando o painel de ação é aberto, ele mostra todos os parâmetros, incluindo parâmetros que não sejam de objeto, como Texto ou Booleano. Parâmetros de entrada relacionados a objeto, como campos de registro, aparecem quando você seleciona o tipo de objeto para cada parâmetro sObject.

* **Configurar entradas de ação do Apex opcionais sem incluir alternância**
  O Flow Builder agora oculta a opção Incluir para parâmetros de entrada de ação do Apex opcionais, simplificando a experiência de configuração. Um asterisco vermelho ainda denota os parâmetros de entrada necessários. Parâmetros de entrada com valores padrão ainda têm uma opção Substituir.

* **Usar tipos de coleção personalizados e personalizados em parâmetros de saída de ação invocável**
  Simplifique estruturas de dados complexas em fluxos usando os tipos Coleção personalizada e Coleção personalizada para parâmetros de saída em ações invocáveis. Os tipos Coleção personalizada e Coleção personalizada oferecem suporte a tipos sObject, tipos definidos pelo Apex e outros campos de tipo Personalizado. Usar tipos personalizados em vez de ações personalizadas do Apex reduz o número de ações baseadas no Apex que o Flow Builder carrega, o que melhora o desempenho de carregamento do Flow Builder.

* **Visualizar o caminho de execução ao testar um fluxo de tela**
  Acompanhe o caminho do fluxo de tela diretamente na tela para entender como ele está sendo executado. Agora, quando você termina de testar manualmente um fluxo de tela, a tela destaca o caminho que o fluxo seguiu. Antes, o teste de fluxo não mostrava o caminho após a conclusão. O caminho de execução mostra quando o teste de fluxo atinge um destes estados: Concluído, Pausado, Aguardando ou Erro. O caminho leva a todos os elementos tocados durante a execução do fluxo, mesmo que não fizessem parte do caminho concluído.

* **Solucionar e corrigir erros de fluxo com Agentforce (beta)**
  Use a IA generativa para diagnosticar problemas de tempo de design em fluxos salvos e falhas de tempo de execução em fluxos ativos. Identifique a causa-raiz dos erros e entenda as opções de solução em linguagem natural usando o Ask Agentforce (beta). Use a opção Corrigir problema para IA para corrigir automaticamente o fluxo e evitar solução de problemas manual.

* **Revise erros e avisos de fluxo com o painel de validação remodelado**
  Concentre-se na criação de fluxos sem interrupções de validação constantes. O painel de validação agora permanece fechado quando você abre um fluxo de rascunho para que você possa revisar erros e avisos apenas quando estiver pronto. O painel reprojetado mostra problemas em cartões organizados agrupados por elemento. Clique no título de um cartão para abrir o painel de propriedades desse elemento e corrigir o problema. Os padrões de validação consistentes em todos os elementos tornam os erros de manipulação mais previsíveis no Flow Builder.

* **Identificar alterações de versão do fluxo em uma visão geral**
  Entenda as diferenças entre duas versões de fluxo com uma comparação visual detalhada no Flow Builder. Identifique visualmente elementos adicionados, modificados ou ausentes na tela sem comparar manualmente arquivos XML complexos ou tabelas abstratas. Acompanhe modificações em um nível granular, de alterações de elemento a ajustes de configuração, para melhorar a legibilidade e reduzir o risco de erros de implementação.

* **Comparar alterações de elemento de transformação em um fluxo**
  Obtenha mais visibilidade das alterações de automação comparando diferentes versões dos elementos Transformação no Flow Builder. A ferramenta Comparação de versões do fluxo agora mostra um detalhamento de mapeamentos de transformação, junções e fórmulas. Identifique facilmente mapeamentos de campo adicionados, atualizados ou removidos e revise alterações de configuração detalhadas para transformações complexas.

* **Triagem de problemas diretamente no modo de exibição de lista Fluxos**
  Monitore a integridade do fluxo com a nova coluna Taxa de erro do elemento. Essa coluna mostra a porcentagem de elementos de fluxo que resultaram em erros durante a última ocorrência do fluxo. Um ícone de sucesso verde indica uma taxa de erro de 0%, enquanto um ícone de aviso amarelo representa uma taxa de erro de 1% a 100%. Identifique e teste problemas acionáveis sem abrir fluxos individuais.

* **Os nomes de colunas do modo de exibição de lista de fluxo foram alterados**
  Renomeamos dois cabeçalhos de coluna no modo de exibição de lista Fluxos para maior clareza. Status de progresso agora é rotulado como Status, indicando o status do fluxo em execução. A coluna Status anterior agora se chama Status da ativação, indicando se o fluxo está ativo ou não.

* **Adicionar editores de propriedade personalizados a entradas de ação do Apex individuais**
  Os desenvolvedores agora podem criar e atribuir editores de propriedade personalizados (CPE) a parâmetros de entrada individuais em vez de ações inteiras do Apex. Um componente da Web Lightning (LWC) pode controlar um único parâmetro de entrada ou gerenciar vários parâmetros relacionados. Parâmetros de entrada sem CPEs continuam usando o editor de propriedade padrão no Flow Builder. Essa abordagem dá aos desenvolvedores um controle detalhado sobre a configuração de parâmetros com menos complexidade.

* **Definir valores da lista de opções para entradas de ação do Apex**
  Os desenvolvedores podem fornecer opções de lista de opções para parâmetros de entrada de ação do Apex para simplificar a configuração de ação. Os desenvolvedores usam o atributo padrão ProvidedValuesList para especificar valores separados por vírgula ou fazer referência a uma classe do Apex que estende o DynamicPicklist. Cada parâmetro de entrada oferece suporte a até 500 valores totais da lista de opções. No Flow Builder, os usuários selecionam valores válidos na lista de opções do parâmetro de entrada, o que reduz os erros de configuração.

* **Personalizar o cabeçalho do editor de propriedades padrão de uma ação do Apex**
  Os desenvolvedores agora podem adicionar um cabeçalho personalizado à ação do Apex. O cabeçalho orienta os usuários com contexto e instruções quando eles configuram a ação no Flow Builder. O cabeçalho aparece na parte superior do painel de propriedades e fornece contexto, instruções ou informações adicionais para melhorar a experiência de configuração.

* **Simplifique a seleção de metadados para entradas de ação do Apex**
  Os desenvolvedores podem simplificar a seleção de registro de metadados para usuários que configuram ações do Apex no Flow Builder. Ao definir suas ações do Apex, os desenvolvedores atribuem tipos de entidade de configuração a parâmetros de entrada. Em seguida, os usuários podem selecionar entre registros válidos no Flow Builder, evitando erros ao configurar a ação.

* **Expor configurações de estilo para seus componentes de tela de fluxo personalizados**
  Permita que os autores de fluxo personalizem componentes da Web Lightning (LWC) adicionando ganchos de estilo ao seu código. Os ganchos definem quais propriedades um autor pode ajustar no Flow Builder, como cores e dimensões para atender às necessidades de identidade visual.

* **Impor o Construtor sem argumento em classes do Apex usadas para parâmetros de ação invocável (atualização de versão)**
  Quando essa atualização está habilitada, você obtém acesso a determinadas classes do Apex integradas que estão disponíveis para serem usadas como parâmetros de ação invocáveis. Além disso, essa atualização impõe a visibilidade do construtor sem argumento em qualquer classe. Essa atualização estava agendada para imposição na versão Summer '26. A partir da versão Spring '26, o Salesforce não impõe mais essa atualização, mas recomendamos que você a habilite. Essa atualização de versão antes se chamava Impor requisitos de permissão definidos em classes do Apex integradas usadas como entradas.

* **Classificar os resultados de ação em massa do Apex usando a ordem da solicitação (atualização de versão)**
  Com essa atualização habilitada, os resultados da ação em lote do Apex são exibidos na ordem em que as solicitações são recebidas. No momento, as solicitações sujeitas a erros são priorizadas no topo da lista de resultados e as solicitações bem-sucedidas estão na parte inferior.

* **Exigir aprovação unânime para etapas de aprovação atribuídas a grupos**
  Exija que todos os membros do grupo aprovem seus itens de trabalho para que uma etapa de aprovação possa prosseguir. Quando você configura uma etapa de aprovação com aprovação unânime, todos os membros recebem um item de trabalho de aprovação. Se algum membro rejeitar, a etapa de aprovação será rejeitada. Se todos os membros aprovarem, a etapa de aprovação será aprovada.

* **Os designers de aprovação agora podem visualizar dependências de fluxo**
  Usuários com a permissão Designer de aprovação agora podem visualizar dependências de fluxo para seus processos de aprovação de fluxo no aplicativo Approvals. Antes, apenas usuários com a permissão Gerenciar fluxo tinham acesso a essas informações.

* **A orquestração de fluxo agora é um recurso padrão**
  As execuções de orquestração agora estão incluídas nas edições disponíveis sem limitações baseadas em uso. Antes, os direitos de execução de orquestração eram limitados.

* **Aprimore a troca de dados com conectores de terceiros recém-adicionados**
  Use esses conectores de terceiros recém-adicionados em fluxos para conectividade sem código a sistemas externos e para facilitar a troca de dados e informações entre diferentes sistemas.

* **Centralize o gerenciamento de mapeamento de valor para o MuleSoft para Fluxo: Integração**
  Defina, gerencie e rastreie todas as pesquisas de tradução de valor em um local central. O recurso de mapeamento de valor impõe restrições de mapeamento, lida com valores ausentes e garante a estabilidade de seus fluxos.

* **Concluir várias tarefas por vez**
  Conclua várias tarefas ao mesmo tempo quando você tiver cinco ou mais que compartilham o mesmo nome, tipo e projeto. Quando você tem um conjunto de 5 tarefas ou mais, o Agentforce Operations cria uma visualização dedicada. Você pode inserir informações da tarefa nessa visualização e concluir várias tarefas em um só lugar, em vez de abrir e concluir cada tarefa uma por vez.

* **Iniciar até 2.500 fluxos de trabalho de um arquivo CSV**
  Use um assistente de página inteira para carregar dados CSV e iniciar até 2.500 fluxos de trabalho por vez. O assistente oferece suporte a projetos com campos de documento e inclui validação que reduz falhas de dados inválidos ou ausentes. O limite anterior de criação de fluxo de trabalho era de 500 e o produto não suportava esquemas com campos de documento.

* **Configurar vários escalonamentos de tarefa**
  Mantenha as tarefas no caminho certo com até cinco escalonamentos por tarefa padrão ou de aprovação. Um escalonamento adiciona um usuário adicional à tarefa como um designado ou cópia de carbono (CC) para garantir que a tarefa permaneça na agenda. Escalonamentos que ocorrem antes do prazo são exibidos como lembretes no feed de atividades, notificações e emails para que você possa diferenciá-los. As escalações respeitam o horário do calendário comercial e os cessionários e os CCs recebem notificações no aplicativo.

* **Gerar modelos descrevendo seu processo**
  Descreva seu processo em linguagem simples e a IA gerará um projeto. Antes, só era possível gerar um esquema a partir de documentos carregados. Agora, você também pode fazer isso. Quando você gera um projeto com IA, a IA pode adicionar tarefas atribuídas a agentes de IA, liberando seus trabalhadores humanos para trabalho de maior valor. Além disso, qualquer pessoa com a permissão de Criador pode gerar esquemas, o que dá mais pessoas o poder de automatizar seus processos.

* **Criar automações baseadas em Excel (beta)**
  Crie uma automação a partir de uma planilha existente ou gerada com o Excel Agent (beta). Forneça os campos compartilhados como valores a serem adicionados, os campos solicitados como valores a serem recuperados e explique como usar esses dados. Em seguida, o agente insere automaticamente os valores de campo compartilhados, executa todas as fórmulas e extrai os valores de campo solicitados. Também é fácil ver o que o agente faz quando a tarefa é executada. Em vez de analisar históricos de auditoria complexos do agente, os usuários podem baixar o arquivo Excel para analisar todas as fórmulas e dados processados em um só lugar.

* **Extraia dados mais precisos do novo agente do Leitor de documentos (beta)**
  Você agora pode fornecer alternativas de rótulo de campo e instruções extras para garantir que o agente encontre os dados corretos. O novo e aprimorado Agente do Leitor de documentos (beta) pode extrair valores de campo de documentos não estruturados, como PDFs e imagens. Além disso, o agente pode lidar com campos de múltiplos valores e extrair dados tabulares, como itens de linha em um PDF.

> 📄 **Notas Completas:** consulte os detalhes completos na página do tópico [AUTOMATE](./releases/summer_26/automate.md).
</details>

<details>
<summary><b>📄 C360 TRUTH (Clique para expandir 29 alterações)</b></summary>

* **Migrar metadados de governança do Data 360 do sandbox para produção**
  Mantenha uma postura de segurança consistente em ambientes e reduza erros de configuração usando kits de dados DevOps para mover metadados de governança do sandbox para a produção. Mova políticas como mascaramento estruturado, segurança em nível de registro, segurança em nível de campo e segurança em nível de objeto entre ambientes.

* **Habilitar automaticamente as permissões corretas para aprimoramentos de campo de cópia**
  Agora, usuários administradores ou usuários com as permissões Gerenciar perfis e conjuntos de permissões ou Gerenciar usuários podem automaticamente conceder ao usuário C2C as permissões corretas necessárias para ativar aprimoramentos de campo de cópia na maioria das entidades. Antes, você atribuía manualmente permissões de aprimoramentos de campo de cópia. Se o usuário não tiver as permissões corretas para habilitar automaticamente ou se as entidades precisarem de permissões organizacionais, o Salesforce exibirá a interface do usuário para atribuir permissões manualmente.

* **Usar objetos de Insights calculados agregáveis multidimensionais em aprimoramentos de campo de cópia**
  O Salesforce agora oferece suporte a objetos de percepções calculadas multidimensionais agregáveis como a origem para aprimoramentos de campo de cópia. Antes, você podia usar apenas objetos de percepções calculadas unidimensionais. Essa alteração permite que você use mais de seus objetos de percepções calculadas existentes.

* **Solucionar erros de ingestão com DLOs de registros problemáticos**
  Capture e isole automaticamente dados que falham durante o processo de ingestão com o Objeto de data lake (DLO) Registros problemáticos. Em vez de perder dados devido a erros de formatação ou incompatibilidades do sistema, o Data 360 isola esses registros específicos nesse DLO para solução de problemas mais fácil.

* **Ingerir dados estruturados do Databricks (disponível ao público em geral)**
  Leve dados de seu DataBricks Lakehouse para o Data 360 usando processamento em lote para uso em segmentação, ativação e resolução de identidade. Esse conector agora está disponível ao público em geral.

* **Enviar eventos com a categoria Outro por meio da API de servidor para servidor**
  A API Server-to-Server (S2S) agora oferece suporte à categoria de evento Other. Classifique corretamente eventos de fontes como Agentforce, dispositivos IoT, sistemas de POS de varejo e fluxos de trabalho de processos de negócios.

* **Ingerir dados de outras origens com a API de servidor para servidor**
  A nova opção Dados de outras fontes usa três campos (eventId, eventType e dateTime) para tornar a ingestão de dados mais flexível. Ingira dados de fontes não web e não móveis, como conversas do Agentforce, transações de POS, telemetria de dispositivos de IoT e quiosques de autoatendimento, usando a API Server-to-Server (S2S). Antes, a API S2S impedia a ingestão de dados de origens que não tinham contexto de navegador ou aplicativo.

* **Acompanhe o engajamento do usuário com o rastreamento de tempo no SDK da Web do Data 360**
  Rastreie automaticamente as métricas de engajamento do usuário, incluindo tempo na página e duração da sessão, com o recurso Rastreamento de tempo. Monitore a atividade do usuário e envie eventos quando limites de engajamento específicos forem alcançados. Use estas métricas para entender como os usuários interagem com seu conteúdo.

* **Aprimore consultas de gráfico de dados em tempo real com a pesquisa de contato pronta para uso**
  Consulte Gráficos de dados unificados usando chaves de contato comuns, como email e números de telefone, independentemente de suas regras específicas de resolução de identidade. Antes, consultar Gráficos de dados exigia identificadores específicos definidos em regras de resolução de identidade. Com a Pesquisa de contato pronta para uso (OOTB), você pode recuperar Gráficos de dados em tempo real usando um único endereço de email ou número de telefone por solicitação.

* **Dimensionar sua arquitetura com limites de gráfico de dados maiores**
  Crie arquiteturas de dados mais abrangentes criando até 25 Gráficos de dados em uma única implementação. Anteriormente, o limite de 10 Gráficos de dados restringiu sua capacidade de escalar em vários departamentos ou fluxos de trabalho especializados. Com essa maior capacidade, você pode implementar arquiteturas multilíngues e Gráficos de dados especializados para diferentes agentes de IA para garantir que cada caso de uso tenha a estrutura de dados necessária.

* **Adote o streaming para atualizações de gráfico de dados mais rápidas**
  Mantenha seus dados atualizados com Gráficos de dados de streaming que são atualizados assim que os dados subjacentes mudam. Antes, você precisava determinar manualmente a frequência de atualização para seus Gráficos de dados, o que às vezes levava a dados obsoletos. Agora, as alterações de dados do objeto de modelo de dados (DMO) subjacente acionam automaticamente atualizações e fornecem atualizações mais rápidas quase em tempo real. Esse comportamento de atualização previsível torna seus SLAs mais confiáveis e dá aos agentes Agentforce ou mecanismos de personalização acesso aos perfis Customer 360 mais atualizados.

* **Criar transformações de dados em lote usando código personalizado com extensão de código**
  Com a extensão de código no Data 360, você pode criar transformações de dados em lote usando seu código do Python personalizado. Se as transformações de dados em lote nativas não atenderem aos seus requisitos de negócios, use a extensão de código para criar, depurar e implementar sua lógica de transformação e, em seguida, crie transformações de dados em lote que usem a lógica implantada.

* **Crie modelos preditivos com o novo tempo de execução padrão**
  Use o novo tempo de execução padrão ao criar modelos preditivos no Data 360. O novo tempo de execução oferece suporte a novos algoritmos, como agrupamento e previsão, e é a base para recursos de criação de modelo de longo prazo.

* **Proporcionar resultados mais ricos com modelos multiclasse**
  Tome decisões orientadas por dados altamente direcionadas no Data 360 usando modelos multiclasse. Diferentemente de modelos binários que preveem apenas dois resultados, modelos multiclasse classificam dados em até 50 categorias distintas. Essa funcionalidade, que agora está disponível ao público em geral, inclui aprimoramentos desde a versão beta.

* **Prever tendências futuras com previsões de série temporal (disponível ao público em geral)**
  Melhore o planejamento de demanda e as estimativas de receita identificando tendências e sazonalidade em seus dados com previsões no Data 360. Essa funcionalidade agora está disponível ao público em geral.

* **Melhorar o engajamento com a análise de sentimento (disponível ao público em geral)**
  Obtenha percepções mais profundas sobre o feedback do cliente com a análise de sentimento no Data 360 para analisar texto, como análises, pesquisas, emails e transcrições de chat. Descubra como os clientes se sentem sobre sua marca, produtos e experiências. Esse recurso agora está disponível ao público em geral e inclui algumas alterações desde a versão beta.

* **Promova percepções acionáveis com classificação de tópico (disponível ao público em geral)**
  Extraia percepções relevantes de texto não estruturado usando um modelo pré-treinado no Data 360 para classificação de tópico de zero. Essa funcionalidade agora está disponível ao público em geral e inclui algumas alterações desde a versão beta.

* **Obtenha percepções mais profundas com o agrupamento estruturado (beta)**
  Vá além da segmentação básica com modelos de agrupamento no Data 360. Agrupe automaticamente clientes, descubra padrões em dados estruturados e valide os resultados com métricas integradas.

* **Monitorar o desvio do modelo preditivo (beta)**
  Use o monitoramento de desvio de modelo preditivo (beta) no Data 360 para rastrear desvios em inferências ativas em comparação aos dados de treinamento. Você pode detectar turnos, entender variáveis relevantes e treinar novamente um modelo antes de a precisão cair.

* **Knowledge da empresa para conteúdo unificado**
  Use o Enterprise Knowledge para unificar seu conteúdo isolado. Com o Conhecimento unificado, você pode ingerir conteúdo no Data 360, harmonizá-lo em um objeto de modelo de dados harmonizado (HDMO) consistente e obter percepções valiosas sobre a atividade do usuário. Depois que o conteúdo estiver no Enterprise Knowledge, use-o para impulsionar as decisões do agente de IA e o gerenciamento de caso do agente de serviço.

* **Processe mais tipos de arquivo em um contexto inteligente**
  Contexto inteligente permite uma variedade de tipos de arquivo para criar um índice de pesquisa preciso. Carregue os seguintes tipos de arquivo para qualquer espaço de trabalho de Contexto inteligente: .docx, .html, .jpeg, .pdf, .png, .pptx, .txt. Em seguida, crie e publique seu índice de pesquisa para melhorar a precisão da pesquisa.

* **Estenda o Data 360 usando código personalizado com extensão de código**
  Com a extensão de código, você pode levar seu código do Python personalizado para o Data 360 para estender os recursos nativos do Data 360. Se os recursos nativos do Data 360 não atenderem aos seus requisitos de negócios, implemente sua lógica personalizada em recursos compatíveis do Data 360, como transformações de dados em lote. Por exemplo, se você precisar de transformações de dados avançadas para seu caso de uso de negócios, poderá implementar a lógica de negócios personalizada no Data 360 para implementar seus requisitos. O Salesforce CLI com o plugin Extensão de código e o SDK do Python de Código personalizado de dados funcionam juntos como sua cadeia de ferramentas local para Extensão de código.

* **Ativar segmentos usando a publicação rápida em destinos do Data 360**
  Use a ativação rápida para publicar segmentos a intervalos de 1 ou 4 horas para destinos do Data 360. O suporte para destinos do Data 360 permite que fluxos acionados por ativação se conectem a qualquer destino baseado em API externo.

* **Personalizar caminhos de arquivo de destino da ativação do Amazon S3 e nomes de arquivo para integrações perfeitas**
  Obtenha controle sobre como seus dados de segmento são entregues ao Amazon S3. Com o novo destino da ativação do Amazon S3 recomendado, você pode personalizar nomes de arquivo, definir caminhos de pasta específicos e gerenciar conexões centralmente com autenticação global usando autenticação baseada em IDP. O novo destino da ativação do Amazon S3 oferece suporte a ativações de segmento, mas não oferece suporte a DMO em lote ou ativações de API.

* **Ativar DMOs em lote para plataformas de parceiros estratégicas**
  Envie conjuntos de dados de DMO completos para plataformas de marketing e publicidade, como Google, Meta e LinkedIn. As plataformas de parceiros estratégicos unem o suporte existente para Marketing Cloud Engagement, destinos de ativação do Data Cloud e destinos de hiperescala, dando às suas equipes mais flexibilidade em onde elas entregam dados de DMO.

* **Filtrar ativações de DMO de streaming com atributos de gráfico de dados**
  Use DMOs em seu gráfico de dados para definir critérios de associação para ativações de DMO de streaming, indo até dois saltos do DMO ativado. Crie públicos mais direcionados com base nos relacionamentos que você já modelou, sem ser limitado apenas aos atributos do DMO ativado.

* **Implementar componentes de extensão de código usando kits de dados**
  Use um kit de dados DevOps para mover extensões de código ou transformações de dados criadas usando extensões de código do sandbox para produção. Quando você adiciona uma transformação de dados criada usando uma extensão de código ao seu kit de dados, a extensão de código associada é incluída automaticamente no kit de dados. Quando sua extensão de código faz referência a objetos de data lake ou objetos de modelo de dados, você deve adicionar manualmente os objetos referenciados ao kit de dados.

* **Ativar públicos correspondentes com quartos limpos**
  Use a ativação de sala limpa para enviar públicos correspondentes diretamente para o bucket do S3 de um provedor. O provedor pode ativar o público correspondente para sua plataforma de publicidade. Melhore seu gasto de anúncio com taxas de correspondência mais altas e exposição de dados limitada.

* **Gerenciar operações de sala de atualização de dados**
  Simplifique tarefas de conectividade e gerenciamento de colaboração de sala de limpeza de dados programaticamente com a API do Connect. Use esses novos pontos de extremidade para gerenciar os principais fluxos de trabalho de sala de limpeza em configuração, manutenção e validação:

> 📄 **Notas Completas:** consulte os detalhes completos na página do tópico [C360 TRUTH](./releases/summer_26/c360_truth.md).
</details>

* 📄 **CHANGE LOG RN CHANGE LOG**: Acesse o arquivo de notas de versão em [./releases/summer_26/change_log_rn_change_log.md](./releases/summer_26/change_log_rn_change_log.md).
<details>
<summary><b>📄 COMMERCE (Clique para expandir 88 alterações)</b></summary>

* **Cronograma de implantação do B2C Commerce 2026**
  Para manter nosso compromisso com a confiança do cliente e garantir que os lançamentos do B2C Commerce atendam aos nossos rigorosos padrões, implantamos as versões principais do B2C Commerce para os clientes em quatro fases. A tabela de implantação lista quais instâncias estão incluídas em cada fase principal da versão.

* **Crie experiências de compra personalizadas no B2C Commerce com o Agentforce Marketing**
  Crie consentimentos e notificações do comprador com tecnologia Agentforce Marketing, Data 360 e Personalização. Adicione mensagens de consentimento à sua loja (virtual) para coletar endereços de e-mail e criar seu público de marketing opcional. Envie notificações de carrinho abandonado por e-mail, SMS ou WhatsApp. Você também pode acionar campanhas de marketing pós-venda quando os compradores concluírem uma compra. Ao integrar-se com personalização, você pode incluir recomendações personalizadas nas notificações pós-pedido.

* **Desbloquear compras com agentes e experiências entre nuvens conectando o B2C Commerce ao Salesforce**
  Com apenas alguns cliques, crie uma troca de dados confiável entre o B2C Commerce e uma Salesforce org dedicada. Ao conectar sua instância do B2C Commerce a uma Salesforce org, você pode acessar experiências entre nuvens, como Agente do comprador, Agente do comerciante, Sincronização de perfil do comprador e Notificações do comprador.

* **Estabelecer contas pessoais para compradores com a sincronização de perfil do comprador**
  A sincronização de perfil do comprador conecta os dados de compradores do B2C Commerce com registros de conta para uso em outros aplicativos Salesforce. Essa integração nativa substitui código customizado e ferramentas manuais por um sistema automatizado que sincroniza compradores registrados como contas pessoais ou contatos. A sincronização adiciona ou atualiza IDs de contato e conta no perfil do comprador no B2C. Ao ancorar as identidades dos compradores em toda a plataforma Salesforce, você fornece os dados fundamentais necessários para habilitar ações do Agentforce, atendimento personalizado e programas de fidelidade.

* **Simplificar as migrações de produtos com replicação automatizada de imagens**
  As imagens do produto agora são incluídas quando você replica produtos de Staging a Production. A replicação granular agrupa imagens internas do produto em um arquivo zip e coloca as imagens em seus locais corretos durante o processo de importação. Anteriormente, as imagens do produto não eram transferidas, então era preciso movê-las manualmente.

* **Melhorar a capacidade de resposta do Storefront com tempos limite de HTTP mais rápidos**
  As chamadas HTTP agora expiram após 5 segundos por padrão, evitando travamentos de conexão e mantendo sua loja (virtual) responsiva. Anteriormente, as chamadas expiravam após 30 segundos se o valor de tempo limite estivesse ausente ou definido como zero. Você pode ajustar manualmente o tempo limite em suas configurações do Business Manager ou de script.

* **Aumentar a produtividade com aplicativos e navegação personalizáveis**
  Crie aplicativos e espaços de trabalho personalizados usando modelos de Merchandising, Administração e Ferramentas do comerciante. Você pode então combinar suas opções personalizadas em uma única visualização unificada.

* **Criar seu próprio espaço de trabalho com o aplicativo de merchandising**
  Acesse módulos do Business Manager adaptados às suas tarefas específicas de merchandising usando a opção personalizada do aplicativo Merchandising. Anteriormente, você tinha que navegar pelo conjunto completo de módulos do Business Manager, incluindo ferramentas fora de suas responsabilidades principais. O aplicativo Merchandising fornece um espaço de trabalho focado organizado em torno de suas tarefas. Você pode personalizar ainda mais o aplicativo para priorizar as ferramentas que você mais usa.

* **Criar e gerenciar conteúdo reutilizável com blocos de conteúdo**
  Os blocos de conteúdo são unidades modulares e reutilizáveis de conteúdo que você cria no Page Designer e gerencia centralmente usando o módulo Blocos de conteúdo no Business Manager. Esta versão apresenta o módulo Blocos de conteúdo para gerenciamento centralizado do ciclo de vida e um painel de componentes aprimorado no Page Designer.

* **Identifique problemas de segurança do sistema antecipadamente com a Detecção de anomalias.**
  Identifique regressões de desempenho e anomalias de segurança, como picos de erro ou logons com falha, anteriormente executando um log de Detecção de anomalias. Anteriormente, a detecção de problemas exigia investigação manual. Agora, o sistema analisa padrões de log e mostra anomalias em tempo real.

* **Usar recursos de CDN integrada para On-Demand Sandboxes**
  Provisione um nome de host de domínio padrão com recursos completos de rede de distribuição de conteúdo (eCDN) integrada do B2C Commerce para instâncias de On-Demand Sandbox (ODS) recém-provisionadas. Use os recursos da eCDN, como cache de borda e firewalls de aplicativos Web, e teste as configurações e as regras de segurança do Storefront em uma sandbox que reproduza de forma fiel sua configuração de produção.

* **Avaliar a taxa de cliques nos resultados da pesquisa**
  Monitore a frequência com que os compradores clicam em um resultado após a pesquisa. Use a nova métrica Taxa de cliques no painel Pesquisa no site – Mais pesquisados para revisar o engajamento dos resultados da pesquisa e identificar tendências e priorizar oportunidades de conversão.

* **Manter seu catálogo pronto para o Storefront com insights de prontidão do produto**
  Identifique produtos que não estão prontos para a loja (vritual) usando os insights de prontidão do produto na página inicial de Ferramentas do comerciante do Business Manager. Verifique rapidamente quais produtos estão incompletos ou não receberam categorias nos catálogos da sua loja.

* **Simplificar a manutenção do catálogo com ações de produtos em massa e mais opções de exportação**
  Reduza o tempo gasto nas operações diárias do catálogo copiando, excluindo e exportando produtos diretamente de uma lista de produtos. Copie até 1.000 produtos e exclua até 200 produtos por vez, usando menos etapas para manter seu catálogo de produtos. Ao exportar, escolha extrair produtos específicos, resultados de pesquisa ou catálogos inteiros para um formato CSV ou XML.

* **A cota da lista de preços para um Storefront agora é de 5.000**
  Introduza mais estratégias de precificação entre regiões, promoções e sortimentos e escale operações complexas de precificação sem reestruturar a configuração de sua loja (virtual). Agora você pode manter até 5.000 listas de preços por site.

* **Receber notificações quase em tempo real com a nova estrutura de eventos (piloto)**
  Reaja às alterações de dados e processamento no B2C Commerce usando a estrutura de eventos do B2C Commerce. Na versão 26.6, a estrutura de eventos apresenta suporte para duas novas notificações de eventos assíncronos relacionadas a replicações. O B2C Commerce planeja adicionar suporte para mais eventos em versões posteriores.

* **Gerenciar endereços IP confiáveis da eCDN em regras personalizadas do Web Application Firewall (WAF) após a migração**
  A partir do B2C Commerce 26.6, o Salesforce migra suas configurações de endereço IP confiáveis existentes de regras de acesso legadas do Cloudflare para regras personalizadas do WAF e listas de IPs gerenciados. Após a migração, gerencie essas regras pelo Business Manager para obter um controle mais granular sobre o tráfego confiável. As regras de segurança também oferecem suporte à definição no nível da conta, aplicando-se a todas as zonas do realm sem configuração por zona. Fazer referência a listas de IPs gerenciados por regras no nível da zona e no nível da conta.

* **Atualizar cookies personalizados para estar em conformidade com os padrões RFC 6265**
  Para fechar brechas de segurança, o B2C Commerce atualizou bibliotecas de terceiros para cumprir a conformidade de cookies definida pelo RFC 6265. O código personalizado da loja (virtual) que gera cookies não compatíveis, como um atributo de domínio com ponto inicial ou caracteres inválidos, agora falha. Atualize o código de tratamento de cookies nas suas instâncias de On-Demand Sandbox para que esteja em conformidade com o padrão RFC 6265.

* **Iniciar campanhas promocionais mais rapidamente com importações de código de cupom de maior capacidade**
  Execute importações de códigos de cupom definidos pelo comerciante sem a pausa estendida na inicialização que atrasava execuções anteriores e processe um número muito maior de códigos por execução. Lance promoções com códigos personalizados maiores em prazos mais curtos. Continue a usar códigos gerados pelo sistema quando uma campanha exigir milhões de códigos exclusivos.

* **Notas da versão 26.6 da B2C Commerce API**
  Confira os recursos e atualizações mais recentes da B2C Commerce API.

* **Composable**
  Confira os recursos e atualizações mais recentes do Progressive Web App (PWA) Kit e do Managed Runtime.

* **SFRA**
  Confira os recursos e atualizações mais recentes do Storefront Reference Architecture (SFRA).

* **Proporcionar experiências de compra personalizadas em escala com o Storefront Next (GA - disponibilidade geral).**
  Storefront Next é um framework React full-stack que combina renderização no servidor com navegação no lado do cliente para entregar experiências de compra de alto desempenho e personalizadas. Economize tempo e esforço usando um fluxo de trabalho automatizado no Business Manager para configurar sua loja (virtual). Com o B2C Developer Toolkit e as habilidades de agente, obtenha ajuda com o desenvolvimento da loja (virtual) e converta seu design do Figma em código. Os comerciantes podem personalizar a loja (virtual) no Page Designer, que renderiza os componentes do React de forma nativa. Os clientes podem conversar com o Agente do comprador para encontrar produtos.

* **Obter desempenho otimizado do Storefront com uma nova arquitetura**
  O Storefront Next usa o modo de framework do React Router 7, que renderiza páginas no servidor para carregamentos iniciais e reduz o processamento pesado no lado do cliente no navegador. A personalização do lado do servidor do Storefront Next entrega conteúdo e dados personalizados sem sacrificar o desempenho. O Storefront Next usa Tailwind e shadcn/ui para estilização CSS e componentes, o que resulta em pacotes da loja (virtual) menores e melhor desempenho nos Core Web Vitals.

* **Criar um Storefront mais rápido com a configuração automatizada no Business Manager**
  não é necessário configurar manualmente clientes de API, projetos e ambientes do Managed Runtime (MRT) nem realizar a implantação inicial da loja (virtual) — a configuração da loja (virtual) faz tudo isso para você. A configuração automatizada cria uma loja (virtual) com um domínio e certificado padrão do eCDN. Escolha ter o código da sua loja (virtual) armazenado em um repositório do GitHub e autentique-se no GitHub. Após a conclusão da instalação, você pode exibir, clonar, excluir seu ambiente MRT e editar algumas configurações. Se você tiver lojas (virtuais) PWA-Kit criadas anteriormente no MRT, poderá exibi-las no Business Manager e ter todas as suas lojas (virtuais) disponíveis em uma interface.

* **Gerenciar ambientes pré-configurados com a eCDN**
  Os ambientes MRT (Managed Runtime) que a configuração da loja (virtual) ou você cria no Business Manager são pré-configurados com a rede de distribuição de conteúdo (eCDN) incorporada. O suporte nativo da eCDN para o Storefront Next oferece melhor desempenho e segurança, um domínio padrão para sua loja (virtual) e recursos de segurança da eCDN. O domínio padrão, *.my.cc.salesforce.com, é mapeado automaticamente para o domínio MRT *.exp-delivery.com e você não precisa configurar um proxy.

* **Proporcione experiências de compra mais ricas com o modelo Storefront Next Market Street**
  O template de varejo Market Street oferece uma página Minha Conta aprimorada, uma Página de listagem de produtos (PLP) e uma Página de detalhes do produto (PDP). O modelo fornece um plano comprovado, que economiza tempo de implementadores e comerciantes e permite que eles se concentrem na diferenciação e integração da marca em vez do design da página. As páginas de produtos incluem componentes para uma lista de desejos, localizador de lojas, retirada na loja, status do inventário, blocos de produtos enriquecidos e um pop-up para adicionar um produto ao carrinho. Você também pode incluir avaliações e classificações de produtos conectando-se a um serviço de terceiros. A página Minha Conta contém pedidos recentes, lista de desejos, métodos de pagamento, além de outros novos recursos.

* **Gerenciar o conteúdo de páginas do Storefront Next no Page Designer.**
  Os comerciantes agora podem usar o Page Designer para adicionar e personalizar estas páginas do Storefront Next: Página inicial, Sobre nós, Página de detalhes do produto (PDP) e Página de listagem de produtos (PLP). Essas páginas incluem componentes de layout e conteúdo. Depois que um administrador configurar a loja (virtual) no Business Manager, os comerciantes podem definir propriedades de componentes e direcionar campanhas e promoções em configurações de componentes.

* **Criar e testar componentes de IU no Storefront Next com o Storybook**
  O Storefront Next inclui o Storybook, uma ferramenta front-end de código aberto para criar, visualizar, testar e documentar componentes da IU do React. Use o Storybook para explorar os componentes internos do Storefront Next, criar componentes isoladamente, executar testes automatizados e criar documentação de componentes. Usar o Storybook para desenvolvimento de componentes facilita a descoberta de componentes, acelera o desenvolvimento, melhora a qualidade dos componentes e reduz regressões.

* **Visualize seu Storefront no Business Manager com o Contexto do comprador**
  Verifique a aparência da sua loja com base no contexto do comprador, incluindo grupos de clientes, data e hora, acionadores de código-fonte e qualificadores. Use o recurso de pré-visualização para testar alterações em produtos, preços e estratégias de marketing antes de fazer a implantação em Production. Esse processo ajuda você a verificar se o seu site é exibido corretamente em cenários como promoções futuras ou campanhas sazonais.

* **Criar e administrar o Storefront Next com agentes de IA e a CLI**
  Use o Agentic B2C Developer Toolkit para criar sua loja (virtual) e gerenciar tarefas de administração com agentes de IA, uma CLI e um servidor MCP. O kit de ferramentas inclui habilidades de agente e plug-ins que permitem que você execute tarefas escrevendo um prompt em seu agente de codificação de IA preferido. Exemplos de agentes compatíveis incluem Agentforce Vibes, Claude Code, Cursor e GitHub Copilot (VS Code e CLI). Com habilidades de agentes, os agentes de IA podem criar lojas (virtuais), implantar cartridges, gerenciar tarefas, criar sandboxes e executar muitas outras tarefas a partir do terminal ou diretamente dentro do seu IDE. Não há necessidade de escrever código do zero, memorizar comandos da CLI ou navegar pelo Business Manager. Use a CLI a partir do terminal para automatizar tarefas de administração repetitivas.

* **Gerar componentes do Storefront Next a partir dos designs do Figma**
  Modifique rapidamente os componentes da sua loja (virtual) com o conjunto de ferramentas Figma-to-Component do servidor MCP (Model Context Protocol) de B2C DX. Em vez de fazer alterações no código da loja (virtual), modifique o arquivo de design do Figma gerado pela configuração da loja (virtual) no Business Manager. Em seguida, use o servidor B2C DX MCP para converter o arquivo de design em componentes do Storefront Next. Você também pode combinar tokens com temas e analisar componentes.

* **Proteger o acesso ao Storefront via Business Manager**
  Controle o acesso às suas lojas (virtuais) usando a configuração do site Business Manager. Conceda acesso aos ambientes de Managed Runtime associados às suas lojas (virtuais) somente a usuários com uma senha de autenticação básica.

* **Simplificar o checkout com o preenchimento automático de endereços no Storefront Next**
  Reduza as digitações e os erros dos compradores na etapa do checkout com maior risco de abandono com preenchimento automático de endereço. Durante o checkout, um comprador agora só precisa inserir três caracteres de seu endereço de envio ou cobrança para receber recomendações instantâneas do Google. Quando o comprador seleciona um endereço na lista de recomendações, o Google preenche os campos de endereço restantes.

* **Impulsionar a conversão de checkout no Storefront Next**
  Ofereça aos compradores uma experiência de checkout simplificada e reduza o abandono do carrinho. Quando um comprador faz checkout pela primeira vez, ele pode salvar suas informações de envio e pagamento para uso futuro e criar uma conta em sua loja. Quando um comprador registrado retorna para fazer outra compra, ele só precisa inserir seu e-mail e um código de verificação para finalizar a compra. Suas informações de envio e pagamento são preenchidas automaticamente. Os compradores sempre têm a opção de fazer o checkout como visitante.

* **Planificação de implementação do Account Manager para 2026**
  A planificação de implementação do Account Manager lista todas as datas de lançamento planejadas para 2026.

* **Account Manager remove funções descontinuadas**
  O Account Manager remove automaticamente funções descontinuadas do sistema e as desassocia de todos os usuários. Essas funções não fornecem mais acesso aos serviços do B2C Commerce e sua remoção não afeta a funcionalidade ou o acesso do usuário. As funções afetadas foram descontinuadas pela primeira vez na Account Manager 1.46.0 e receberam o rótulo “DESCONTINUADO” na interface do usuário desde o Account Manager 3.7.

* **Recursos do Salesforce B2B Commerce lançados mensalmente**
  Muitos recursos e alterações do B2B são lançados mensalmente, portanto, volte em breve para ver as soluções mais recentes. A versão do Verão 2026 (EUA) inclui atualizações acontecendo de maio a agosto de 2026.

* **Habilitar compras e checkout no agente para compradores B2B**
  Melhore o engajamento do cliente exibindo componentes da IU da loja, como categorias de produtos e detalhes do produto, diretamente nas interações do agente com os compradores. A moeda exibida é baseada na localidade do comprador. Os compradores também podem adicionar produtos simples ao carrinho, ver o resumo do carrinho e limpar o carrinho sem sair do agente.

* **Adaptar sua estratégia de preços às necessidades de cada loja B2B**
  Todas as lojas não precisam mais aderir ao mesmo procedimento de precificação. Você agora pode criar planos de procedimento personalizados que vinculam definições de contexto específicas às suas regras de precificação e atribuí-los a lojas individuais. Adicione lógica personalizada antes e depois de um procedimento de precificação para automatizar a precificação sem depender de soluções alternativas manuais.

* **Exibir precificação contratual em uma loja B2B**
  Exiba os preços dos contratos negociados diretamente em sua loja B2B. Compradores com contratos veem suas taxas negociadas, enquanto outros compradores continuam a ver preços padrão. Os compradores podem concluir compras de forma independente a preços de contrato, minimizando discrepâncias de preço e a necessidade de intervenção de representantes de vendas.

* **Personalizar uma página de registro da B2B Commerce Store usando ferramentas nativas do Salesforce**
  Crie uma experiência de registro personalizada para lojas B2B Commerce com componentes web Lightning customizados e lógica Apex. Substitua o formulário de cadastro padrão por uma interface personalizada, automatize os fluxos de provisionamento de compradores e integre com sistemas externos, tudo isso sem integrações de terceiros. Certifique-se de conceder aos usuários visitantes acesso à classe Apex utilizada pelo seu componente personalizado.

* **Melhorar a eficiência do comprador usando múltiplos carrinhos**
  Os compradores das suas lojas B2B agora podem simplificar compras complexas ao preparar produtos em múltiplos carrinhos independentes. Embora o checkout esteja, por enquanto, simplificado por meio do carrinho padrão, os compradores podem categorizar projetos futuros com facilidade ou salvar listas selecionadas para referência futura sem perder o controle dos itens.

* **Novos carrinhos agora têm uma convenção de nomenclatura com carimbos de data/hora**
  Os carrinhos agora são criados com nomes com carimbo de data/hora com o padrão, Carrinho sem título - [Data] [Hora] em vez do nome padrão anterior, Default_cart_name. Esse aprimoramento ajuda a identificar o tempo de criação do carrinho e melhora a organização ao gerenciar carrinhos. Se sua implementação depende de nomes de carrinho, revise e atualize sua lógica. Para diferentes convenções de nomenclatura, use triggers no objeto WebCart para personalizar os nomes dos carrinhos de acordo com os requisitos do seu negócio.

* **Reordenar produtos configuráveis em um clique**
  Reordene produtos e pacotes configuráveis comprados anteriormente sem reconfiguração manual. Quando os compradores fazem o pedido novamente, suas seleções originais fluem diretamente para o carrinho. Esse processo com um clique economiza tempo para pedidos repetidos e reduz o risco de erros de configuração.

* **Transforme cotações em pedidos com o Self-Service Checkout (finalização de compra autônoma)**
  Acelere o processo de compra permitindo que os compradores B2B façam a transição de uma cotação para o carrinho de checkout. Um comprador pode mover cotações aprovadas para comprar itens a preços negociados sem a assistência de um representante de vendas ou copiar itens de cotações não aprovadas para comprá-los a preço de tabela. Obtenha a atenção do comprador mais cedo fornecendo aos usuários autenticados e aos usuários visitantes não autenticados uma opção para solicitar cotações diretamente da página do produto.

* **Validar pedidos com chamadas para serviços externos durante o checkout**
  Use a extensão de Validação de criação de pedido para conectar seu fluxo de checkout a sistemas externos por meio de chamadas síncronas do Apex para serviços externos durante o checkout simplificado. Valide os detalhes do pedido, como disponibilidade de inventário ou situação de crédito do cliente, em um ERP ou outro sistema externo antes de concluir uma transação.

* **Componentes novos e alterados de loja LWR do Commerce**
  Crie experiências de loja (virtual) mais ricas e dinâmicas com os componentes de loja Lightning Web Runtime (LWR). Novos componentes melhoram a experiência do usuário, fornecendo aos merchandisers maiores opções de personalização para simplificar os fluxos de trabalho. Os componentes atualizados oferecem suporte a layouts mais flexíveis, acessibilidade aprimorada e definições de configuração adicionais.

* **Controlar quais produtos aparecem primeiro nos resultados da pesquisa**
  Influencie quais produtos aparecem primeiro nos resultados de pesquisa atribuindo pesos a campos pesquisáveis padrão e personalizados. Pesos mais altos priorizam produtos que correspondam a esses campos. Por exemplo, atribuir o maior valor de peso 10 ao campo SKU do produto influencia o comportamento de ranqueamento e pode fazer com que correspondências de SKU apareçam primeiro. Anteriormente, todos os campos pesquisáveis não semânticos eram ranqueados de forma igual.

* **Promover e rebaixar mais produtos com limites de regras mais altos**
  Controle o que os compradores veem primeiro com a expansão dos limites da regra de Boost & Bury. Crie até 75 regras de palavras-chave de pesquisa e 75 regras de categoria para promover produtos prioritários, destacar novos lançamentos e reduzir a relevância de itens com baixo desempenho, proporcionando uma experiência de compra mais relevante e personalizada.

* **Expandir a descoberta de produtos com limites ampliados de indexação de categorias**
  Garanta que os seus produtos apareçam em todas as pesquisas e visualizações de categorias relevantes, aproveitando os limites de indexação ampliados. O mecanismo de pesquisa agora processa até 500 associações de categorias por produto, o dobro do limite anterior de 250.

* **Automatize assinaturas com gateways de terceiros e métodos de pagamento salvos**
  Os compradores agora podem usar seu gateway de pagamento de terceiros preferido para compras baseadas em assinatura. Use métodos de pagamento salvos como tokens seguros para processar renovações automatizadas sem a necessidade de intervenção manual. Os compradores agora podem concluir compras recorrentes, gerenciar preferências de pagamento e receber notificações de pagamento sem inserir repetidamente os detalhes de pagamento.

* **Gerenciar assinaturas e ver o histórico sem entrar em contato com a Salesforce**
  Agora, os compradores podem alterar e renovar assinaturas e visualizar o histórico de assinaturas diretamente sem exigir que o administrador entre em contato com o executivo de contas da Salesforce. Os compradores também podem renovar várias assinaturas em massa sem entrar em contato com a Salesforce.

* **Crie Storefronts B2B headless mais rapidamente usando o aplicativo Reference React**
  Crie lojas B2B personalizadas headless usando as Commerce Connect REST APIs e qualquer framework de front-end. Comece com um manual de headless, um aplicativo de referência baseado no React e um repositório de código aberto. A implementação de exemplo inclui jornadas completas de comprador e padrões de loja para descoberta de produtos, gerenciamento de carrinho, checkout e histórico de pedidos.

* **Chatter está desativado por padrão em novas orgs**
  Chatter é desativado por padrão em todas as novas orgs. Para quaisquer recursos nessas organizações que exijam acesso à funcionalidade Chatter ou às Chatter APIs, ative Chatter.

* **Reduzir problemas da cadeia de suprimentos com alertas de atendimento proativo**
  Gerencie interrupções na cadeia de suprimentos antes que elas afetem seus clientes. O Agentforce monitora continuamente seus pedidos para sinalizar locais de risco para que você possa intervir com antecedência. Obtenha alterações recomendadas em sua lógica de roteamento de pedidos para ajudar a corrigir as causas básicas da interrupção de pedidos. Com alertas proativos, reduza as correções de última hora, economize o tempo de seus representantes no tratamento de exceções e proteja as promessas de entrega de seus clientes.

* **Usar a lógica de regra de roteamento personalizada para estimativas de entrega**
  Forneça aos clientes estimativas de entrega mais precisas usando a lógica de roteamento personalizada de sua loja para calcular a estimativa. Atribua um grupo de regras de roteamento como lógica de roteamento, e as estimativas de entrega usam essa lógica ao determinar o tempo de envio.

* **Gerenciar a lógica de roteamento de pedidos com regras baseadas na interface do usuário**
  Atualize a lógica de roteamento e atendimento diretamente na IU e reduza as atualizações manuais e demoradas no Salesforce Flow. Crie um grupo de regras e adicione regras personalizadas ou regras pré-configuradas: disponibilidade de inventário, proximidade de localização, estoque excedente e otimização de divisão. Adicione pesos às regras em seu grupo para maior personalização do roteamento.

* **Expandir a cobertura de região e remessa para estimativas de entrega**
  Agora você pode fornecer estimativas de entrega para clientes no Reino Unido e Canadá. Também adicionamos o Royal Mail e o Canada Post à lista de operadoras compatíveis.

* **Configurar caminhos nos objetos de Pedido em devolução e Remessa**
  Configure um caminho na parte inferior dos objetos Pedido em devolução e Remessa para que os representantes de atendimento ao cliente possam acompanhar o progresso de uma tarefa.

* **Definir o campo Reservado na localização em relatórios padrão**
  A opção de definir “Reservado na localização” é compatível em todos os relatórios padrão.

* **Solucionar interrupções de atendimento com o Agentforce**
  Gerencie exclusões de localização e redirecionamento de pedidos por meio de uma interface conversacional. Agora, seus representantes podem usar um único prompt de texto para bloquear localizações específicas por um tempo definido e redirecionar pedidos. Reduza a necessidade de atualizar manualmente a lógica de roteamento por meio de fluxos para que seus representantes possam responder mais rapidamente a problemas da cadeia de suprimentos.

* **Recursos do Salesforce Point of Sale lançados mensalmente**
  A versão do Verão 2026 (EUA) inclui atualizações acontecendo de abril a julho de 2026. Consulte as notas de versão da Primavera 2026 para os meses anteriores.

* **Aumentar a receita de complementos e acelerar o checkout com complementos de produtos pré-selecionados**
  Aumente as taxas de venda conjunta com opções de produtos adicionais ativadas por padrão na página de detalhes do produto. As alternâncias pré-selecionadas reduzem o atrito na transação e aceleram o checkout sem exigir que os atendentes selecionem manualmente cada produto adicional.

* **Elimine acompanhamentos manuais e feche pagamentos mais rapidamente com o Relatório de Pagamento Remoto por Link**
  Visualize todas as atividades de pagamento remoto em um relatório consolidado no aplicativo POS. Alertas visuais na fila notificam os associados quando um cliente conclui um pagamento remoto, eliminando a necessidade de acompanhamentos manuais. Identifique rapidamente links de pagamento com falha ou expirados para resolver problemas rapidamente e manter as transações em movimento.

* **Aumentar as vendas na loja ao oferecer suporte a trocas de pedidos online**
  Processe trocas de pedidos de compra online com devolução na loja diretamente no aplicativo POS. Anteriormente, o sistema bloqueava a adição de novos itens ao carrinho para devoluções online. Agora você pode ajudar os clientes a trocar compras online por diferentes itens pessoalmente, mantendo a receita em suas lojas e reduzindo os custos de frete de devolução.

* **Proporcionar experiências de checkout consistentes com seleção de data para todos os métodos de atendimento de pedido**
  Ofereça a seleção de datas de entrega e retirada para envios baseados nas lojas e retiradas com roteamento automático, e não apenas para o envio padrão. O componente seletor de data agora aceita todos os métodos de atendimento de pedido do Omnichannel no nível do grupo de entrega. Esse suporte estendido ao seletor de datas elimina a necessidade de implementações personalizadas de seleção de datas e permite configurar agendas para atender aos requisitos do seu negócio.

* **Sincronizar dados de taxa de reabastecimento com Salesforce Order Management**
  Elimine a reconciliação manual e mantenha seus registros de pedido e pagamento precisos postando os detalhes da taxa de reabastecimento diretamente no Salesforce Order Management. Obtenha visibilidade precisa dos atributos de pagamento personalizados durante todo o processo de reembolso, fornecendo às suas equipes de finanças e operações os dados em tempo real de que precisam para agir mais rapidamente e fechar os livros com confiança.

* **Criar uma visão completa do cliente com recursos aprimorados de perfil do Customer 360**
  Customer 360 agora exibe informações mais detalhadas sobre os clientes e atividades de compras entre canais. Configure as tags PS para mostrar a ID do governo e os detalhes da empresa, incluindo IDs fiscais e endereços comerciais. Você também pode visualizar as listas de desejos dos clientes a partir do seu sistema Commerce e adicionar esses itens diretamente ao carrinho.

* **Dimensionar operações globais com configuração granular de impostos**
  Gerencie várias contas fiscais em uma grande organização configurando códigos de referência no nível da loja. Esta atualização permite que lojas em diferentes regiões ou sob marcas diferentes realizem cálculos de imposto que usam perfis separados. Ao especificar um campo de registro de loja para esses códigos, você obtém controle localizado sobre a auditoria de impostos e, ao mesmo tempo, mantém uma alternativa global para administração simplificada.

* **Simplificar os reembolsos globais isentos de impostos da Blue e mantenha-se em conformidade na Itália**
  Ative a emissão com isenção fiscal do Global Blue na Itália e gere automaticamente números de documentos sequenciais para os formulários fiscais do Global Blue, garantindo conformidade com os requisitos de fiscalização para o fluxo de isenção fiscal. Esta atualização permite que os comerciantes na Itália mantenham a numeração consecutiva obrigatória em todos os documentos de isenção fiscal diretamente no POS. Os comerciantes também podem acompanhar esses documentos ao longo de todo o seu ciclo de vida, com os registros armazenados permanentemente no pedido associado.

* **Rastreie pedidos em várias lojas de forma mais eficiente com o ID da loja nos números dos pedidos**
  Inclua identificadores de loja diretamente nos números dos pedidos para acelerar o rastreamento e o atendimento de pedidos. Você pode personalizar o prefixo do número do pedido para adicionar o ID da loja automaticamente a cada pedido online, eliminando etapas de pesquisa extras ao processar pedidos de várias localizações.

* **Automatize o monitoramento de promoções de franquias e elimine a supervisão manual**
  Monitore alterações em promoções em toda a sua rede de franquias com acionadores de eventos automatizados. Os acionadores automatizados capturam eventos de criação, atualização e exclusão e enviam os dados de promoção modificados para seus sistemas downstream. Essa integração orientada a eventos elimina a sincronização manual e fornece estratégias promocionais consistentes entre localizações.

* **Aumentar a receita de garantia e reduzir atrito no Point of Sale**
  Dê aos vendedores da loja a flexibilidade para oferecer a cobertura de garantia certa no momento certo, sem criar problemas de gerenciamento de pedidos. O sistema de POS calcula automaticamente as opções de garantia com base nos subtotais elegíveis do carrinho. Com a política de aprovação correta, os vendedores podem ajustar a cobertura de garantia para produtos específicos no Point of Sale. Além disso, você pode exigir verificações de garantia antes de concluir o checkout. Essa funcionalidade se integra a um novo SPI de recuperação de garantias, permitindo uma forma simples de conectar seu catálogo atual de garantias à experiência do POS.

* **Melhorar o fluxo de checkout com pagamentos confiáveis em cartão armazenado**
  Mantenha as filas de checkout em movimento oferecendo aos vendedores da loja acesso instantâneo aos métodos de pagamento armazenados dos clientes, inclusive durante vendas com vários métodos de pagamento. Quando um vendedor seleciona um perfil de cliente com cartão de crédito salvo, o POS recupera as informações do cartão por meio de tokens do perfil para facilitar transações seguras pelo terminal da Adyen. Essa estrutura atualizada atenua cenários anteriores que desabilitavam transações de cartão armazenado. O checkout do visitante ainda requer um cartão físico. Durante o fluxo do Point of Sale, confirme a identidade do comprador antes do pagamento.

* **Eliminar interrupções no checkout em cenários não tributáveis com o Vertex**
  Evite erros de cálculo de impostos em casos em que uma região ou item não está sujeito à tributação e nenhuma regra de isenção está configurada. Anteriormente, transações envolvendo regiões ou itens não tributáveis, sem uma regra de isenção, resultavam em falhas no cálculo. Essas falhas interrompiam a experiência de checkout e exigiam intervenção manual ou abertura de um chamado de suporte para o Vertex.

* **Simplificar o checkout remoto com a sincronização de pagamentos em tempo real**
  Libere os vendedores de loja do acompanhamento manual para que possam se concentrar nos clientes. O sistema POS atualiza automaticamente os status do pedido e envia um recibo eletrônico ao cliente após o pagamento bem-sucedido. Anteriormente, os vendedores passavam tempo verificando o status dos pagamentos e emitindo recibos. Os gerentes de loja também podem monitorar o status do pagamento remoto no aplicativo POS. Anteriormente, links de pagamento expirados bloqueavam reservas de estoque e exigiam intervenção manual para serem resolvidos.

* **Garantir preços BOGO precisos e simplificar as devoluções com descontos de preço mais baixo**
  Elimine inconsistências de precificação no checkout e simplifique devoluções e trocas aplicando descontos Compre um, Ganhe um (BOGO) ao item qualificado de menor preço no carrinho. Anteriormente, o Point of Sale aplicava descontos ao primeiro item qualificado adicionado, o que causava discrepâncias de preço durante devoluções e trocas, levando a atrito com o cliente e possível perda de receita. Agora, o Point of Sale calcula automaticamente o desconto com base no item qualificado de menor preço, garantindo precificação precisa em todos os casos, reduzindo erros de caixa e proporcionando uma experiência fluida ao cliente em compras, devoluções e trocas.

* **Reduzir os custos de atendimento e melhorar a satisfação do cliente cancelando pedidos BOFIS até o momento do envio**
  Evite custos de envio desnecessários e melhore a satisfação do cliente cancelando pedidos Compre online e tenha o pedido atendido pela loja (BOFIS, Buy Online, Fulfill In Store) a qualquer momento antes do envio, inclusive após a embalagem. Anteriormente, o POS removia a opção de cancelamento quando um pedido era embalado ou marcado como pronto para envio, forçando os vendedores a concluir e enviar pedidos indesejados, aumentando custos e complicando devoluções. Agora, você pode cancelar até o momento do envio, reduzindo esforços de atendimento (fulfillment) desperdiçados, cortando despesas desnecessárias de envio e atendendo rapidamente e com eficiência solicitações de cancelamento de última hora de clientes.

* **Reduzir a perda de vendas devido à compatibilidade com vale-presente**
  Conecte seu aplicativo Point of Sale, anteriormente Retail Cloud Modern POS, a qualquer fornecedor de vale-presente usando o novo SPI de vale-presente. Agora você pode integrar provedores especializados para verificar saldos, ativar cartões e processar resgates diretamente no POS. Essa SPI garante que seu processo de checkout seja compatível com serviços específicos de vale-presente que seu negócio exige.

* **Configurar integrações isentas de impostos mais rapidamente para todas as lojas**
  Para economizar tempo, carregue um arquivo CSV para definir as configurações isentas de impostos para o Global Blue em todas as suas localizações. Agora você pode gerenciar IDs de loja, credenciais de API e IDs de balcão em massa, em vez de editar cada loja individualmente. O sistema valida seus dados e os mapeia para a loja correta automaticamente.

* **Expandir para novos mercados com SPIs fiscais**
  Expanda sua presença global conectando mecanismos fiscais locais ao seu fluxo de trabalho de varejo. As SPIs fiscais conectam seu aplicativo Point of Sale, anteriormente Retail Cloud Modern POS, a sistemas que tratam de impostos e requisitos fiscais específicos de cada país, para que você possa concluir o checkout sem interrupções.

* **Reduza o risco de conformidade com permissões de inventário granulares**
  Restrinja o acesso a módulos de inventário específicos configurando permissões para transferências, ajustes e contagens de ciclos. Essa alteração substitui a permissão de inventário único por configurações de permissão separadas para cada módulo de inventário, dando a você a flexibilidade de definir acesso para diferentes funções. Ao limitar o acesso a módulos específicos, você evita riscos operacionais e mantém um controle mais rígido sobre os dados da loja.

* **Melhorar as vendas no modo offline com imagens precisas do produto**
  Exiba imagens de produtos no aplicativo POS durante transações offline. Anteriormente, o modo offline mostrava apenas uma imagem padrão em vez da imagem do produto, o que dificultava a identificação de itens. Agora, você pode encontrar produtos mais rapidamente e continuar atendendo clientes sem interrupção durante transações offline.

* **Capacitar gerentes de franquia com controle de acesso por escopo e gerenciamento independente do POS**
  Elimine a exposição não autorizada de dados e reduza a dependência operacional de administradores corporativos ao conceder aos gerentes de franquia controle direto sobre as funções de suas lojas. Você pode criar funções e usuários específicos da franquia, vincular os vendedores da loja diretamente à franquia e impor visibilidade granular o CMS. Esse recurso garante que usuários de franquia vejam apenas os dados relevantes às suas localidades, promove autonomia operacional no nível da loja, reduz a carga administrativa e protege a integridade dos dados em toda a sua rede de franquias.

* **Priorizar pedidos e reduzir atendimentos atrasados**
  Obtenha a visibilidade de que você precisa para lidar com pedidos de coleta e envio na ordem correta. O aplicativo POS agora destaca pedidos sensíveis ao tempo na lista de processamento de pedidos. Um indicador verde mostra que um pedido está dentro do prazo, um indicador laranja indica que está próximo do prazo, e um indicador vermelho mostra que o prazo já foi ultrapassado.

* **Simplifique o Checkout com os campos de envio dinâmicamente ocultos**
  Facilite o Checkout para seus compradores que estão comprando serviços e mercadorias digitais pedindo apenas as informações necessárias, como detalhes de faturamento. A página de pagamento agora oculta dinamicamente os campos de endereço de envio para compras que não exigem um endereço de envio.

* **Acelere pagamentos do tipo Pagar agora com autenticação por senha única**
  Os compradores agora podem salvar seu endereço de envio e informações de pagamento para uma experiência de checkout mais rápida. Os compradores podem optar por fazer login com uma senha de uso único (OTP) e recuperar seus detalhes de pagamento e informações de contato salvos.

> 📄 **Notas Completas:** consulte os detalhes completos na página do tópico [COMMERCE](./releases/summer_26/commerce.md).
</details>

* 📄 **COMPLIANCE DOCS**: Acesse o arquivo de notas de versão em [./releases/summer_26/compliance_docs.md](./releases/summer_26/compliance_docs.md).
<details>
<summary><b>📄 CUSTOMIZATION (Clique para expandir 20 alterações)</b></summary>

* **Recursos de personalização lançados por mês**
  Alguns recursos e alterações de Personalização são lançados com frequência mensal, portanto, volte para ver as atualizações mais recentes. A versão Summer '26 inclui atualizações que ocorrem de abril de 2026 a julho de 2026.

* **Não há suporte para novas páginas de login do Trialforce com marca no Cloudforce.com**
  Não é mais possível criar páginas de login com marca que terminem em .cloudforce.com para a Organização de origem (TSO) do Trialforce da solução do AgentExchange. Páginas de login com marca criadas antes da versão Summer '26 nesse nome de host permanecem ativas. Não há data definida para a descontinuação completa do nome de host .cloudforce.com, portanto, verifique as notas de versão futuras para atualizações sobre essas páginas.

* **Crie integrações mais robustas com o suporte de serviços externos para enumerações**
  Agora você pode incluir enumerações na especificação OpenAPI que você usa para criar um serviço externo. Quando você adiciona o serviço externo a um elemento de ação de Fluxo, a enumeração aparece como uma lista de opções. Em outros elementos de Fluxo e no Apex, a enumeração aparece como seu tipo base. Você pode usar a string ou o número como o tipo de valor de enumeração. O suporte para enumerações está disponível apenas em registros de serviço externo criados após a versão Summer '26.

* **Faça mais com as melhorias de arquivo binário de Serviços externos**
  Os Serviços externos agora fornecem um limite de tamanho de arquivo de 100 MB para operações de arquivo binárias, entrada de nome de arquivo personalizado opcional no Flow Builder e resolução de nome de arquivo mais inteligente com uma ordem de prioridade definida.

* **Oferecer suporte a mais fusos horários**
  Mantenha a precisão global dos dados com suporte para todos os fusos horários canônicos da Autoridade de atribuição de números de Internet (IANA). Obtenha mapeamentos regionais mais precisos e convenções de nomenclatura padronizadas em toda a plataforma, ajudando seus usuários a se manterem sincronizados independentemente de seu local. As novas informações de fuso horário estão disponíveis automaticamente nas configurações de fuso horário. As informações de fuso horário anteriores permanecem disponíveis por meio do Apex e das APIs para compatibilidade com versões anteriores.

* **Expanda traduções do idioma do usuário final para catalão e basco (beta)**
  Melhore a experiência dos falantes de catalão e basco com o suporte a idiomas da interface do usuário para nuvens selecionadas. O texto da IU catalão e basco, agora disponível como idiomas com suporte beta, volta para o espanhol quando as traduções não estão disponíveis.

* **Revise traduções atualizadas de rótulos**
  Para aprimorar a precisão e a experiência de seus usuários, atualizamos as traduções de alguns nomes de objetos, guias e campos padrão para estes idiomas: Chinês (simplificado), holandês, finlandês, alemão, hebraico, italiano, japonês, coreano, norueguês, russo, espanhol e espanhol (México).

* **Habilitar os formatos de localidade de ICU (atualização de versão)**
  Com essa atualização, os formatos de localidade de Componentes Internacionais para Unicode (ICU) substituem os formatos de localidade do Java Development Kit (JDK) da Oracle no Salesforce. As localidades controlam o formato de datas, horas, moedas, endereços, nomes, valores numéricos e o dia de início da semana. O ICU define o padrão internacional para esses formatos. Os formatos de localidade ICU fornecem uma experiência consistente na plataforma e melhoram a integração com os aplicativos em conformidade com o ICU em todo o mundo. Essa atualização foi disponibilizada inicialmente na versão Winter '20. As organizações que ainda não mudaram para os formatos de localidade ICU são incentivadas a atualizar manualmente.

* **Revise o acesso ao campo entre perfis, conjuntos de permissões e grupos de conjuntos de permissões**
  Poupe tempo revisando a segurança em nível de campo para um campo específico em todos os perfis, conjuntos de permissões e grupos de conjuntos de permissões. Em vez de ir para páginas de Configuração individuais, você pode visualizar essas informações em um só lugar no Resumo de acesso ao campo no Gerenciador de objetos.

* **Rastrear dependências de permissão mais facilmente**
  Ao atualizar permissões ou aplicativos na interface de usuário de perfil avançada, você verá quaisquer alterações adicionais necessárias para manter as permissões dependentes alinhadas após atualizações anteriores. Antes, essas alterações ocorriam em segundo plano, mas estavam visíveis apenas na Trilha de auditoria de configuração.

* **Habilitar filtragem de perfil (atualização de versão)**
  Para melhorar a segurança da sua organização do Salesforce, a configuração Filtragem de perfil está habilitada por padrão. A filtragem de perfil impede que os usuários visualizem nomes de perfil que não sejam os próprios, a menos que tenham a permissão Visualizar todos os perfis. Se o papel de um usuário exigir que ele veja todos os nomes de perfil, atribua a ele a permissão Visualizar todos os perfis antes da imposição dessa atualização de versão. Essa atualização está disponível da versão Summer '26 em diante.

* **Monitore alterações administrativas em perfis com políticas de segurança da transação**
  Gere eventos de rastreamento quando os administradores do Salesforce modificam ou criam perfis de usuário que incluem permissões críticas. Bloqueie alterações não autorizadas em permissões de perfil críticas. Use Políticas de segurança da transação para monitorar, alertar e bloquear atualizações de permissão em tempo real. Essas políticas ajudam você a monitorar privilégios de segurança aprimorados e manter uma estrutura de auditoria robusta. Você também pode rastrear a remoção específica da permissão de isenção de TransactionSecurity de perfis.

* **Crie integrações mais seguras com suporte de adaptador entre organizações para credenciais nomeadas**
  O adaptador entre organizações do Salesforce Connect agora oferece suporte a credenciais nomeadas para autenticação. A chamada SOAP login() está sendo descontinuada e a autenticação por senha e a autenticação OAuth 2.0 não terão suporte no futuro, portanto, recomendamos migrar qualquer fonte de dados externa do adaptador entre organizações para usar credenciais nomeadas, um método de autenticação mais robusto e seguro.

* **O agente legado para configuração não pode mais ser habilitado**
  A Configuração com Agentforce (beta) substituiu o Agente para Configuração que foi lançado anteriormente em março de 2025. A Configuração com Agentforce suporta muitas mais tarefas de Configuração e é atualizada automaticamente com novas funcionalidades. O Agente para configuração não está mais sendo atualizado e não pode ser habilitado em novas organizações do Salesforce. Para organizações que habilitaram o Agente para Configuração anteriormente, o agente ainda está disponível, mas recomendamos que você comece a usar Configuração com Agentforce quando possível.

* **Escolher se deseja conceder acesso usando hierarquias de papéis para filas**
  Use a nova configuração Conceder acesso usando hierarquias para restringir o compartilhamento de registro apenas a membros da fila especificados. Antes, os registros compartilhados com uma fila sempre eram compartilhados com os superiores dos membros da fila na hierarquia de papéis. Essa configuração oferece maior controle sobre o acesso ao registro dos usuários e impede que os superiores recebam notificações por email desnecessárias.

* **Atualize padrões organizacionais de modo mais rápido e confiável**
  Para processar alterações a padrões organizacionais mais rapidamente, as regras de compartilhamento baseadas em critérios relacionados agora são recalculadas em paralelo, em vez de em sequência. Essa melhoria será mais perceptível se você tiver muitas regras de compartilhamento. Você pode monitorar o progresso do recálculo na página Trabalhos em segundo plano.

* **Ampliar o acesso para usuários de licença de funcionário unificado**
  Gerencie o acesso de compartilhamento do usuário com o grupo Todos os funcionários restritos, que inclui apenas usuários com a Licença de funcionário unificado. Ao usar esse grupo, você pode rapidamente estender o acesso para usuários com uma Licença de funcionário unificada.

* **Atualize o Apex code e os fluxos para alterar o comportamento de recálculo de compartilhamento (atualização de versão)**
  Para otimizar o desempenho após atualizações em grande escala em grupos ou papéis, o Salesforce agora realiza alguns recálculos de compartilhamento de modo assíncrono. Se o Apex code e os fluxos exigirem que os registros de compartilhamento sejam atualizados imediatamente, o código e os fluxos poderão ser interrompidos quando essa atualização de versão for imposta. Atualize classes, testes e fluxos do Apex que atualizam a associação ao grupo ou papéis se eles dependem de recálculo de compartilhamento síncrono. Essa atualização foi disponibilizada inicialmente na versão Spring '26.

* **Faça mais com campos personalizados em entidades padrão**
  Agora você pode usar campos personalizados como chaves de junção em entidades padrão ao criar uma lista relacionada em um relacionamento de objeto de modelo de dados (DMO) direto. Você também pode incluir campos personalizados em entidades padrão ao realizar implantações de mesclagem de sandbox em ambientes de produção.

* **Gerenciar compartilhamento e edição de modo de exibição de lista com permissões granulares**
  Atribua a nova permissão de usuário Gerenciar modos de exibição de lista compartilhados para que os usuários possam compartilhar seus modos de exibição de lista pessoais com papéis, grupos e territórios dos quais eles são membros. Antes, para compartilhar exibições de lista, um usuário precisava da permissão de usuário Gerenciar exibições de lista públicas, que concedia acesso amplo para editar ou excluir qualquer exibição de lista pública no Salesforce. Agora, os usuários podem compartilhar seus próprios modos de exibição de lista sem acesso para gerenciar cada modo de exibição de lista público.

> 📄 **Notas Completas:** consulte os detalhes completos na página do tópico [CUSTOMIZATION](./releases/summer_26/customization.md).
</details>

<details>
<summary><b>📄 DEVELOPMENT (Clique para expandir 91 alterações)</b></summary>

* **O desenvolvedor local agora é a visualização ativa**
  Para refletir melhor a natureza em tempo real do componente, do site do Experience e das visualizações do aplicativo Lightning, o desenvolvedor local agora se chama Visualização em tempo real.

* **Visualizar um único componente da Web Lightning no seu navegador (disponível ao público em geral)**
  Use a Visualização ativa de componente único para executar uma visualização em tempo real de um componente da Web Lightning em seu navegador. Esse recurso, que agora está disponível ao público em geral, inclui algumas alterações desde a versão beta.

* **Visualizar um único componente da Web Lightning no Visual Studio Code (disponível ao público em geral)**
  Para executar uma visualização em tempo real de um componente da Web Lightning diretamente no Visual Studio Code (VS Code) ou no Criador de código, use a extensão Visualização em tempo real VS Code. Essa extensão agora está disponível ao público em geral para componentes da Web Lightning.

* **Simplificar interações de dados com gerentes de estado para LWC (disponível ao público em geral)**
  Agrupe e gerencie dados e sua lógica relacionada com mais eficiência em seus aplicativos com gerentes de estado. Esse recurso, que agora está disponível ao público em geral, inclui algumas alterações desde a versão beta.

* **Alterações de distorção da API no Lightning Web Security**
  O Lightning Web Security (LWS) inclui novas proteções de segurança com mais distorções para APIs da Web. Regras do ESLint que correspondem às distorções também estão disponíveis.

* **Esquema de URI de data: de blocos de distorção de HTMLAnchorElement**
  A nova distorção em HTMLAnchorElement.prototype.href bloqueia URLs que usam o esquema de URI de data:. O esquema de URI de data: pode ser usado para criar links de download de texto simples, mas essa abordagem gera vários problemas de segurança. Em vez disso, use o esquema de URI de blob:.

* **Visualizar recursos com o Gerenciador de versão do Salesforce (beta)**
  Com o Salesforce Release Manager, sua organização pode visualizar e testar os recursos futuros em sandboxes usando o canal Desenvolver (Dev). O Gerenciador de versão do Salesforce acelera a inovação, melhora a qualidade de longo prazo e fornece maior controle sobre o consumo de recursos. Seu feedback nos ajuda a melhorar a qualidade do recurso e moldar o futuro do produto.

* **Carregar listas grandes dinamicamente (visualização do desenvolvedor)**
  Lide com grandes quantidades de dados sem desacelerar seu navegador da Web. Quer você esteja mostrando 50 ou 5.000 itens, as listas dinâmicas oferecem uma experiência de usuário tranquila usando a virtualização para renderizar itens conforme você rola.

* **Melhore o encapsulamento em componentes de base com alterações de método interno**
  A Salesforce está atualizando a implementação interna de vários componentes básicos do Lightning para usar métodos privados. Esse esforço está alinhado com os padrões da Web modernos e não afeta a API pública dos componentes de base.

* **Elementos de detalhes do grupo com o nome Atributo**
  Atualize a versão da API para seus componentes para aproveitar os novos recursos e melhorias. O controle de versão garante que os componentes existentes não sejam afetados quando o Salesforce envia novos recursos, correções de bugs e melhorias de desempenho que alteram o comportamento existente. O controle de versões também ajuda o Salesforce a descontinuar os recursos legados.

* **Melhorar o desempenho de recarregamento de módulo hot**
  Atualize a versão da API para seus componentes para aproveitar os novos recursos e melhorias. O controle de versão garante que os componentes existentes não sejam afetados quando o Salesforce envia novos recursos, correções de bugs e melhorias de desempenho que alteram o comportamento existente. O controle de versões também ajuda o Salesforce a descontinuar os recursos legados.

* **Remover campos não públicos de dados de objeto personalizado em respostas de ação do Aura (atualização de versão)**
  Para melhorar a segurança, o Salesforce está removendo campos do sistema não públicos de dados de objetos personalizados retornados em respostas de ação do Aura. Essa atualização filtra os campos internos do sistema que não fazem parte da API pública do Salesforce. Revise os componentes do Lightning que processam dados de objetos personalizados para evitar erros de JavaScript ou dados ausentes. Use apenas campos compatíveis com API em seus componentes para garantir que seus dados sejam exibidos corretamente.

* **Crie experiências móveis com tipos personalizados do Lightning**
  O SDK do Agentforce Mobile agora oferece suporte a tipos personalizados do Lightning. Use esses tipos para estruturar, validar e exibir dados complexos do agente em seus aplicativos móveis, dando a você mais controle sobre como as informações aparecem para os usuários.

* **Atribuir tipos personalizados do Lightning ao SDK móvel do Agentforce**
  Defina tipos personalizados do Lightning para o SDK do Agentforce móvel para controlar como os dados do agente são estruturados e exibidos em seus aplicativos móveis. Crie e gerencie esses tipos usando a IU de configuração de Tipos do Lightning.

* **Atualizações de modelos de componentes do Sistema de design do Salesforce Lightning**
  Use a nova variante de lightning-combobox para criar um estilo em forma de pílula em forma de botão. Para fornecer um contexto visual melhor para seus usuários, você também pode adicionar ícones ao contêiner da caixa combinada e a opções de caixa combinada individuais.

* **Obtenha orientação de design mais rápida com SLDS MCP Tools (beta)**
  Acelere o desenvolvimento da interface do usuário com o gancho de estilo instantâneo do Salesforce Lightning Design System (SLDS) e a orientação de projeto de componente.

* **Usar o modo escuro em mais edições e recursos (beta)**
  Habilite o modo escuro para temas do Salesforce Lightning Design System 2 (SLDS 2) em organizações Performance e Unlimited Edition. E em todas as edições em que o modo escuro está disponível, você agora pode carregar uma versão de modo escuro do logotipo da sua empresa para temas SLDS 2. O modo escuro mostra texto em cores claras e elementos visuais em um fundo escuro, o que estabelece as bases para oportunidades de tema mais ricas e mais personalização dos componentes de base do Lightning. Com o modo escuro habilitado, seus usuários podem selecionar uma aparência que reduza o esforço ocular em condições de pouca luz e melhore a legibilidade.

* **Operações de banco de dados são executadas no modo de usuário por padrão, não no modo do sistema**
  Aproveite um modelo de segurança do Apex aprimorado que protege seus dados através da imposição de acesso em nível de objeto e campo padrão. Operações de banco de dados do Apex, como consultas SOSL e SOQL, instruções DML e métodos de banco de dados, agora são executadas no modo de usuário por padrão. No modo de usuário, as operações de banco de dados aplicam as regras de compartilhamento, a segurança em nível de campo e as permissões de objeto do usuário atual. Em versões anteriores da API, as operações de banco de dados usam como padrão o modo do sistema, o que significa que o usuário atual pode acessar todos os dados independentemente de suas permissões.

* **Classes do Apex aplicam regras de compartilhamento por padrão**
  Aproveite um modelo de segurança do Apex aprimorado que protege seus dados por meio da imposição de acesso de registro padrão. Classes do Apex sem uma declaração de compartilhamento explícita agora usam como padrão o modo with sharing, que aplica configurações de compartilhamento para toda a organização e regras de compartilhamento personalizadas. Em versões anteriores da API, classes do Apex sem uma declaração de compartilhamento explícita usam como padrão o modo without sharing, com algumas exceções. O modo without sharing ignora as regras de compartilhamento e permite que o usuário atual acesse todos os registros.

* **A cláusula SOQL WITH SECURITY_ENFORCED foi removida**
  Para executar uma consulta SOQL ou SOSL no modo de usuário, use a cláusula WITH USER_MODE em vez da cláusula WITH SECURITY_ENFORCED. Classes do Apex definidas como a API versão 67.0 e posterior que incluem WITH SECURITY_ENFORCED não são compiladas.

* **Acionadores do Apex sempre são executados no modo do sistema**
  Os acionadores do Apex agora sempre são executados no modo do sistema, o que significa que ignoram as regras de compartilhamento, a segurança em nível de campo e as permissões de objeto do usuário atual. Antes, acionadores aninhados impedia regras de compartilhamento em determinados casos de borda. Não é possível declarar acionadores do Apex com modos de compartilhamento ou acesso explícitos. Em vez disso, para aplicar as configurações de acesso a dados, delegue a lógica de negócios para separar manipuladores de acionador, em que você pode definir os modos de compartilhamento e acesso.

* **Escrever testes de integração para Agentforce e Data 360 no Apex (Visualização do desenvolvedor)**
  Escreva testes do Apex completos que fazem chamadas para o Agentforce e o Data 360. Os testes de integração relaxam as restrições de chamadas e a semântica de reversão de transações, para que você possa validar interações reais de serviço e afirmar efeitos colaterais reais em sua organização teste, sem chamadas simuladas.

* **Evite interrupções de fluxo de trabalho habilitando limites elásticos para trabalhos assíncronos (beta)**
  Evite falhas de execução abruptas e limite as exceções se sua organização exceder seu limite diário de trabalho assíncrono. Agora você pode colocar em fila trabalhos de método enfileiráveis e futuros até um novo limite elástico, que é o dobro do limite diário licenciado da sua organização. Os trabalhos assíncronos que excedem o limite diário licenciado são processados a uma taxa limitada.

* **Bloquear a execução de código anônimo do Apex de pacotes gerenciados (atualização de versão)**
  Para reforçar a segurança da organização assinante, bloqueie IDs de sessão de pacote gerenciado de autenticar código do Apex anônimo. Se você habilitar essa atualização, os pacotes gerenciados instalados não poderão mais usar o UserInfo.getSessionId() para obter um ID da sessão e, em seguida, usar o ID da sessão para executar o Apex anônimo.

* **Escreva código mais limpo usando strings de várias linhas**
  Declare strings do Apex que abrangem várias linhas sem usar concatenação de string repetida. Para interpolar valores em strings regulares e multilinhas, use o novo método de instância String.template() em vez do método estático String.format() existente. Esses recursos facilitam a gravação, a leitura e a manutenção do Apex code, especialmente quando você cria cargas úteis HTTP e outros blocos de texto grandes.

* **Trabalhar com Apex code no console da Web (beta)**
  Crie, depure e implemente o Apex no Web Console, um IDE do lado do cliente integrado diretamente no Salesforce. O Console da Web oferece uma moderna experiência de desenvolvedor em que você pode criar consultas SOQL, configurar sinalizadores de rastreamento e níveis de registro de depuração e executar Apex anônimo. O Console da Web também é aberto automaticamente quando você acessa itens do Apex por meio das páginas Classes do Apex, Acionadores do Apex ou Trabalhos do Apex em Configuração, para que você possa implementar modificações sem interromper seu fluxo de trabalho.

* **Obtenha as principais métricas do Apex em configuração com Agentforce (beta)**
  O painel Integridade e uso da organização atualizado agora fornece métricas do Apex em Agente para configuração. O painel mostra classes do Apex em versões de API desatualizadas, erros de compilação do Apex e uso atual de trabalho assíncrono do Apex.

* **Usar o Visualforce PDF Rendering Service com Apex Blob.toPdf() (atualização de versão)**
  Com essa atualização habilitada, o método Apex Blob.toPdf() para renderização em PDF usa o mesmo serviço de renderização que o Visualforce. O serviço de renderização de PDF do Visualforce oferece melhorias, como fontes adicionais e suporte a caracteres de vários bytes. Essa alteração torna a renderização de PDF mais consistente na Salesforce Platform.

* **Personalizar a configuração de ação do Apex no Flow Builder**
  Os aprimoramentos de metadados InvocableActionExtension oferecem mais ferramentas para melhorar a experiência de configuração dos usuários e reduzir erros de entrada no Flow Builder. Agora você pode definir valores de lista de opções, atribuir tipos de metadados e adicionar editores de propriedade personalizados para parâmetros de entrada especificados. Você também pode adicionar cabeçalhos personalizados ao editor de propriedade padrão.

* **Forneça construtores visíveis sem argumentos para classes personalizadas do Apex usadas como parâmetros de ação invocáveis**
  Classes do Apex usadas para parâmetros de ação invocáveis devem ter um construtor sem argumento visível. O construtor deve ser público para classes não empacotadas ou global para classes empacotadas invocadas de fora do pacote. Use a API versão 65.0 ou anterior com a atualização de versão desabilitada para manter o comportamento anterior.

* **Conecte agentes de IA ao Salesforce com segurança com servidores MCP hospedados (disponibilidade geral)**
  Conecte qualquer cliente de IA compatível com MCP, incluindo Claude, ChatGPT, Cursor ou agentes personalizados, à sua organização do Salesforce usando o padrão de Protocolo de contexto de modelo (MCP) aberto. Seus agentes de IA agora podem interagir com dados e automação do Salesforce de maneira segura e controlada com a autenticação OAuth padrão. Os servidores MCP hospedados não exigem nenhuma infraestrutura para gerenciar. Acesse operações do sObject, consultas do Data 360, análises do Tableau e APIs de produto e crie ferramentas personalizadas usando suas próprias ações do Apex, fluxos e consultas nomeadas sem escrever código de integração.

* **Permitir que os assistentes de IA localizem e criem metadados do Salesforce com mais eficiência (beta)**
  O servidor de MCP de Contexto da API do Salesforce agora tem cinco ferramentas de MCP de Contexto da API de metadados em vez de uma. Essas ferramentas mais granulares significam que as consultas do agente de IA podem ser direcionadas, os tempos de resposta são mais rápidos e seu uso de token pode ser mais eficiente. As ferramentas de MCP Contexto da API de metadados fornecem informações contextuais sobre tipos de metadados do Salesforce para ajudar a gerar arquivos de metadados do Salesforce precisos. Essas ferramentas fornecem definições de campo completas, valores válidos, restrições e exemplos para tipos de metadados.

* **Criar ações do agente usando a API de consulta nomeada (disponível ao público em geral)**
  Defina e exponha consultas SOQL personalizadas como ações escalonáveis para clientes da API REST e agentes de IA usando a API de consulta nomeada. Uma consulta nomeada pode recuperar dados de forma rápida e mais eficiente do que os processos existentes do Fluxo ou do Apex.

* **As versões 31.0 a 40.0 da API da Salesforce Platform estão sendo descontinuadas**
  As versões da API da Salesforce Platform das versões 31.0 a 40.0 estão sendo descontinuadas e descontinuadas.

* **Restringir o acesso de login à API SOAP**
  Aprimore a segurança controlando quem pode autenticar usando o login() da API SOAP com a nova permissão Qualquer autenticação da API. A permissão é imposta por padrão em organizações recém-criadas. Você pode optar por habilitá-lo em organizações existentes.

* **Usar tokens de acesso baseados em JWT com a API SOAP**
  A API SOAP agora oferece suporte a tokens de acesso baseados em JWT de fluxos do OAuth do Salesforce. Esse recurso fornece paridade com os mecanismos de autenticação da API REST e habilita o compartilhamento seguro de token com serviços externos.

* **Consultar o Data 360 com mais precisão**
  Use a nova cláusula SET OPTIONS em consultas SOQL para especificar espaços de dados do Data 360 e controlar como valores de string NULL e vazios são tratados. Ao consultar objetos do Data 360 Data Lake, adicione a cláusula no fim da consulta SOQL para obter resultados mais precisos.

* **Calcular valores em uma cláusula SOQL WHERE (piloto)**
  Realize cálculos aritméticos diretamente em suas cláusulas SOQL WHERE usando a nova função FORMULA(). Compare valores entre campos sem exigir campos de fórmula ou lógica de pós-processamento e torne suas consultas mais eficientes e expressivas.

* **Obtenha mais visibilidade do uso da API do seu agente com rastreamento aprimorado**
  O EventLogFiles de Uso total da API agora diferencia entre as chamadas REST do Apex e AuraEnabled do Apex, facilitando o monitoramento e a análise do comportamento do agente. Novas entradas no EventLogFiles de Uso total da API refletem o rastreamento atualizado.

* **Atualizar URLs instanciados no tráfego de API (atualização de versão)**
  Para evitar interrupções quando o Salesforce encerrar o suporte para tráfego de API que use um URL instanciado incorreto, certifique-se de que o tráfego de API para sua organização use o URL de login do Meu domínio da organização. Inicialmente disponível na versão Summer '25, essa atualização de versão estava agendada para imposição na versão Spring '26, mas adiamos a imposição para a versão Winter '27.

* **Seja notificado sobre solicitações de API composta com tipos de evento EventLogFile**
  Consulte o objeto EventLogFile para os tipos de evento CompositeApi e CompositeApiSubrequest para obter detalhes sobre solicitações e subsolicitações da API de gráfico composto e API composta.

* **Outros aprimoramentos na geração de um documento OpenAPI para a API REST sObjects (beta)**
  Com a versão mais recente da especificação OpenAPI, você pode consultar todos os recursos disponíveis e usar um caractere curinga em URIs.

* **Migrar seus eventos de plataforma de volume padrão para eventos de plataforma de alto volume**
  A partir da versão Winter '27, o Salesforce não oferece mais suporte a eventos de plataforma de volume padrão. Para ajudá-lo a fazer a transição de seus eventos de plataforma de volume padrão para eventos de plataforma de alto volume, o Salesforce criou uma ferramenta de migração. Se você não executar a ferramenta de migração, seus eventos de plataforma de volume padrão não serão migrados para eventos de plataforma de alto volume. Você pode usar a API do conjunto de ferramentas ou a API de metadados para executar a migração, que geralmente leva cerca de 10 a 15 minutos para ser concluída, mas pode ser executada por até 24 horas em situações raras. Antes de iniciar uma migração, garanta que toda a atividade de publicação tenha sido interrompida e que todos os assinantes, incluindo acionadores e fluxos, tenham concluído o processamento. Enquanto a migração estiver em execução, as publicações não funcionarão e você não poderá criar novos acionadores ou fluxos até que a migração seja concluída. Você receberá um email quando a migração estiver concluída.

* **Usar novos métodos EventBus.publishWithAccessLevel() para melhor controle de acesso**
  A classe EventBus tem um novo conjunto de métodos publishWithAccessLevel() que simula os métodos publish() existentes e usa um parâmetro AccessLevel não nulo obrigatório. Esses novos métodos são recomendados em comparação com os métodos publish() existentes porque eles definem mais claramente o tipo de acesso necessário pelo Apex code.

* **Chamadas para ações invocáveis são validadas para requisitos de visibilidade do construtor na API versão 66.0 e posteriores**
  A partir da versão 66.0 da API, as chamadas à API REST validam que as classes do Apex personalizadas usadas como parâmetros de ação invocáveis têm construtores sem argumento visíveis. Se o construtor não estiver visível com modificadores de acesso adequados, a chamada de API falhará. Essa alteração com controle de versão se aplicará ao Salesforce se você não tiver habilitado a atualização de versão Impor construtor sem argumento. Antes, as chamadas à API eram bem-sucedidas mesmo que o construtor não estivesse visível. Na API versão 66.0 e posteriores, a chamada de API falhará se o construtor não tiver modificadores de acesso adequados.

* **A chamada de login() da API SOAP nas versões da API SOAP 31.0 a 64.0 está sendo descontinuada (atualização de versão)**
  Na versão Summer '27, a chamada de login() da API SOAP nas versões da API SOAP 31.0 a 64.0 não terá mais suporte e não estará mais disponível.

* **Aplicar um período de expiração a upgrades por push personalizados**
  Agora você pode configurar upgrades por push personalizados para expirar após um determinado número de dias. Com upgrades por push personalizados, os parceiros concedem aos clientes selecionados a capacidade de bloquear upgrades por push. Atualizações por push personalizadas são especialmente úteis para ambientes altamente regulados em que protocolos de conformidade e validação rígidos exigem o controle do tempo de atualização e da supervisão de versão.

* **Validar a prontidão de produção durante uma atualização de versão usando um sandbox que não seja de pré-visualização**
  Durante a transição de uma versão principal do Salesforce para outra, os sandboxes são atualizados em diferentes linhas do tempo com base no tipo de versão. Os sandboxes de visualização fornecem acesso antecipado a novos recursos e são atualizados aproximadamente seis semanas antes das organizações de produção, enquanto os sandboxes não de visualização são atualizados à medida que a atualização da versão principal é concluída. Entre a conclusão de uma atualização de versão principal e o início da próxima atualização de versão, tentamos criar sandboxes de visualização por padrão quando você cria ou atualiza um sandbox. Agora, você pode escolher criar um sandbox sem pré-visualização durante essa janela de tempo. Antes, você podia criar um sandbox sem pré-visualização durante essa janela de tempo apenas entrando em contato com o Suporte ao cliente da Salesforce.

* **O limite de armazenamento da organização teste aumentou**
  O limite de armazenamento de dados para uma organização teste agora é de 500 MB. Antes, o limite era de 200 MB.

* **Servidor Salesforce DX MCP**
  O Salesforce DX MCP Server é uma implementação especializada de Protocolo de contexto de modelo (MCP) que facilita a interação entre LLMs e organizações do Salesforce. Use o servidor DX MCP e suas ferramentas para inserir avisos de linguagem natural em seu IDE para executar tarefas DX padrão, como sincronizar metadados, executar testes do Apex e do agente e criar organizações teste.

* **Extensões do Salesforce para Visual Studio Code**
  O pacote de Extensão do Salesforce inclui ferramentas para desenvolver na Salesforce Platform no editor do VS Code leve e extensível. Essas ferramentas fornecem recursos para trabalhar com organizações de desenvolvimento (organizações teste, sandboxes e organizações DE), Apex, componentes da Web Lightning, componentes do Aura e Visualforce.

* **IDE do Agentforce Vibes**
  O Agentforce Vibes IDE é um ambiente de desenvolvimento integrado baseado na Web que tem todo o poder e flexibilidade do Visual Studio Code, Extensões do Salesforce para VS Code e Salesforce CLI em seu navegador da Web.

* **Criar, depurar e implementar diretamente no Salesforce (beta)**
  O Console da Web é um IDE moderno baseado em navegador integrado diretamente no Salesforce. Parar de alternar entre guias e ferramentas externas: fique no seu fluxo e gerencie todo o seu fluxo de trabalho sem sair da plataforma.

* **Extensão de Vibes do Agentforce**
  Agentforce Vibes é uma ferramenta de desenvolvedor desenvolvida com IA disponível como uma extensão do Visual Studio Code no VS Code Desktop e no Agentforce Vibes IDE. O Agentforce Vibes é criado com modelos de IA CodeGen e xGen-Code, protegidos e personalizados da Salesforce. Ela está habilitada por padrão nas edições Enterprise, Performance, Unlimited, Partner Developer e Developer.

* **Acompanhe os aprimoramentos mais recentes do Agentforce DX**
  Mantenha-se atualizado com estes aprimoramentos recentes do Agentforce DX.

* **Acompanhe os aprimoramentos mais recentes do Salesforce CLI**
  Mantenha-se atualizado sobre os aprimoramentos recentes do Salesforce CLI.

* **Planejar e teste de carga máxima com Teste de escala**
  Use a interface simplificada Teste de escala para executar testes em grande escala com maior precisão. Um fluxo de agendamento remodelado agora integra dados de Precisão da execução de teste para melhores previsões de carregamento. Aproveite dados de hotspot de produção para cenários realistas com a criação de teste de sandbox.

* **Implementar aplicativos dimensionáveis com o Centro de escala**
  O Centro de escala é mais poderoso com a disponibilidade geral de Visão geral da organização, Insights de banco de dados e Insights de desempenho LEX. Agora você pode visualizar tendências de solicitação para recomendações de pico prescritivas e detectar consultas SOQL caras com planos de execução integrados por meio do Analisador de plano. Você pode ativar o Centro de escala para cinco usuários Padrão (não SysAdmin) por organização.

* **Otimize o código com o ApexGuru**
  O ApexGuru introduz o suporte disponível ao público em geral no DX MCP. Detecte e corrija antipadrões diretamente em fluxos de trabalho de IDE agentes. Essa atualização adiciona a detecção habilitada para GPT-4.1 para antipadrões avançados, como SOQL redundante, DML em loops e SOQL em loops. Além disso, os novos Insights de caso de teste ajudam a identificar códigos de teste ineficientes para melhorar a cobertura e a qualidade gerais. A extensão do Salesforce Code Analyzer habilita a leitura em tempo real durante o ciclo de vida do desenvolvimento.

* **O Salesforce Functions será descontinuado**
  O Salesforce Functions não está mais disponível para compra ou renovação. Você pode continuar usando sua assinatura durante o prazo do pedido existente. Para preservar os recursos que o Salesforce Functions forneceu à sua organização, implemente uma solução alternativa antes do término do prazo do pedido existente.

* **Proteger seu aplicativo conectado e soluções de aplicativo cliente externo**
  Todos os parceiros da AgentExchange devem cumprir os novos requisitos de segurança para as soluções Connected App (CA) e External Client App (ECA) para garantir o mais alto nível de Trust e segurança para os Dados do cliente. Esses requisitos se aplicam a qualquer Aplicativo conectado ou Aplicativo cliente externo que seja incluído ou usado em conexão com uma Solicitação de parceiro, fornecida ou criada pelo parceiro e em uso por mais de duas organizações de produção do cliente. Essas atualizações incluem a habilitação obrigatória de Chave de comprovação para troca de código (PKCE) e Ativação de rotação de token (RTR) para evitar interceptação de código de autorização e roubo de token. A implementação desses padrões garante que esses CAs ou ECAs atendam aos protocolos de segurança mais recentes do Salesforce e protejam os dados do cliente. A não conformidade pode resultar na deslistação do AgentExchange da Solicitação de parceiro e/ou na suspensão temporária ou permanente pela Salesforce da interoperabilidade da Solicitação de parceiro com os serviços da Salesforce.

* **Encontre soluções mais rapidamente com o novo AgentExchange**
  Apresentamos o novo AgentExchange, um destino unificado para agentes, aplicativos e especialistas no Salesforce e no Slack. Combinamos o AppExchange, o AgentExchange e o Slack Marketplace em um único mecanismo de soluções para ajudá-lo a encontrar e implementar ferramentas mais rapidamente. Novos recursos de pesquisa semântica e recomendações personalizadas no Agentforce Builder ajudam você a encontrar as soluções certas para suas necessidades de negócios específicas.

* **Componentes da Web do Lightning novos e alterados**
  Crie a interface do usuário facilmente com componentes novos e alterados.

* **Módulos novos e alterados para componentes da Web do Lightning**
  Faça mais com estes módulos novos e alterados para o LWC.

* **Componentes Aura alterados**
  Resumo não disponível para este artigo.

* **Namespace da ConnectApi**
  Essas classes, enums e interfaces são novas ou foram alteradas.

* **Namespace de DocumentAI**
  Essas classes, enums e interfaces são novas ou foram alteradas.

* **namespace de hlthcrbilling**
  Essas classes, enums e interfaces são novas ou foram alteradas.

* **Namespace invocável**
  Essas classes, enums e interfaces são novas ou foram alteradas.

* **Namespace do sistema**
  Essas classes, enums e interfaces são novas ou foram alteradas.

* **Alterações no limite de taxa do ConnectApi**
  Para evitar limites de taxa de ConnectApi potencialmente restritivos por usuário, por namespace e por hora, migramos organizações para o limite de taxa da API da Salesforce Platform por organização, por 24 horas. Somente chamadas de método que exigem Chatter estão sujeitas ao limite de taxa por usuário, por namespace, por hora.

* **Novo Connect em classes do Apex**
  Esses novos métodos estão na classe ConnectApi.CommerceCart.

* **Classes de saída do Connect no Apex alteradas**
  Resumo não disponível para este artigo.

* **Alteradas enumerações do Connect no Apex**
  Para obter informações sobre essas enumerações, consulte Enumerações de ConnectApi no Guia de referência do Apex.

* **Objetos novos e alterados**
  Acesse mais dados por meio desses objetos padrão novos e alterados.

* **Eventos de plataforma padrão novos e alterados**
  Receba notificações em tempo real do Salesforce assinando os canais desses eventos de plataforma padrão novos e alterados.

* **API de metadados**
  Acesse mais metadados por meio desses tipos de metadados novos e alterados.

* **API SOAP**
  Essas chamadas são novas, alteradas ou descontinuadas na API REST versão 67.0.

* **Objetos novos e alterados na API do conjunto de ferramentas**
  Acesse mais metadados por meio desses objetos novos e alterados da API do conjunto de ferramentas.

* **API do GraphQL**
  Resumo não disponível para este artigo.

* **Alterações no limite de taxa da API REST do Connect**
  Integre aplicativos móveis, sites de intranet e aplicativos da Web de terceiros ao Salesforce usando a API REST do Connect.

* **Recursos novos e alterados da API REST do Connect**
  Integre aplicativos móveis, sites de intranet e aplicativos da Web de terceiros ao Salesforce usando a API REST do Connect.

* **Corpos de solicitação da API REST do Connect alterados**
  Integre aplicativos móveis, sites de intranet e aplicativos da Web de terceiros ao Salesforce usando a API REST do Connect.

* **Corpos de resposta da API REST do Connect alterados**
  Integre aplicativos móveis, sites de intranet e aplicativos da Web de terceiros ao Salesforce usando a API REST do Connect.

* **Recursos da API REST do CRM Analytics novos e alterados**
  Usando a API REST do CRM Analytics, obtenha informações de estágio para nós de trabalho de fluxo de dados e filtre campos do conjunto de dados replicados com propriedades avançadas.

* **Corpos de solicitação da API REST do CRM Analytics alterados**
  Usando a API REST do CRM Analytics, obtenha informações de estágio para nós de trabalho de fluxo de dados e filtre campos do conjunto de dados replicados com propriedades avançadas.

* **Corpos de resposta da API REST do CRM Analytics alterados**
  Usando a API REST do CRM Analytics, obtenha informações de estágio para nós de trabalho de fluxo de dados e filtre campos do conjunto de dados replicados com propriedades avançadas.

* **Recursos alterados:**
  A API de download do Analytics tem novos parâmetros para funcionalidades aprimoradas.

* **Recursos novos e alterados da API Interface do usuário**
  Crie a IU do Salesforce para aplicativos móveis nativos e aplicativos da Web personalizados.

* **Corpos de resposta alterados da API Interface do usuário**
  Crie a IU do Salesforce para aplicativos móveis nativos e aplicativos da Web personalizados.

* **Objetos com suporte**
  Crie a IU do Salesforce para aplicativos móveis nativos e aplicativos da Web personalizados.

> 📄 **Notas Completas:** consulte os detalhes completos na página do tópico [DEVELOPMENT](./releases/summer_26/development.md).
</details>

<details>
<summary><b>📄 EINSTEIN (Clique para expandir 17 alterações)</b></summary>

* **Observabilidade do Agentforce: Análise de agente refinada e poncionadores personalizados (beta)**
  Obtenha uma visão unificada do desempenho do agente com o Refined Agent Analytics, que combina o Agente de serviço Analytics e o Agente do funcionário Analytics em um só lugar com mais de 40 métricas. Use Poncionadores personalizados (beta) para avaliar sessões em relação aos seus próprios KPIs junto com as métricas de qualidade padrão do Salesforce.

* **Desbloqueie a interoperabilidade do agente com MCP para Agentforce**
  Capacite seus agentes com funcionalidades entre provedores com o Protocolo de contexto de modelo (MCP) para Agentforce. O MCP é um padrão aberto para conectar perfeitamente modelos de IA a sistemas externos. Criamos um cliente MCP no Agentforce, assim, o trabalho complexo e manual de integração de sistemas, incluindo conectividade de API, autenticação e acesso a dados, é feito para você. O MCP para Agentforce e seu conjunto de recursos facilitam o registro e o gerenciamento de servidores MCP, criam políticas para governar o comportamento do agente e dão aos seus agentes acesso seguro às ferramentas do servidor MCP.

* **Proteja conexões com suas APIs externas e servidores MCP com Políticas Agentforce**
  Crie políticas para proteger conexões com seus servidores externos de API e MCP para que as ferramentas de agente possam acessar esses serviços de modo seguro e adequado. Controle o acesso, defina limites de uso e dê suporte a padrões de governança.

* **Criar e implementar agentes habilitados para Voice no novo Agentforce Builder**
  Agora você pode criar, personalizar e implementar agentes de serviço habilitados para voz no novo Agentforce Builder. Use scripts de agente e fluxos de trabalho de várias etapas no novo criador para criar seus agentes habilitados para voz.

* **Extensão do suporte a idiomas globais com Agentforce Voice (beta)**
  Agora, o Agentforce Voice oferece suporte a mais idiomas globais além do inglês e do francês, permitindo que você alcance um público mais amplo. No momento, há suporte para estes idiomas no beta.

* **O provedor de pesquisa OpenAI na ação Pesquisar o agente da Web agora está disponível ao público em geral**
  Obtenha resultados de pesquisa da Web relevantes em tempo real em seus agentes de IA usando o OpenAI como provedor de pesquisa. A OpenAI como provedor de pesquisa, que agora está disponível ao público em geral, inclui uma atualização ao modelo de pesquisa da Web subjacente desde a versão beta.

* **Aumente o Trust com citações em Traga seu próprio canal**
  Crie Trust em respostas geradas por IA fornecendo referências de origem nas mensagens de saída Traga seu próprio canal. Os usuários finais do Messaging agora podem verificar as respostas do agente de serviço Agentforce com base em artigos do Knowledge ou outras fontes diretamente na sua interface do usuário personalizada. Com links de origem e deslocamentos de caracteres na carga útil da mensagem de saída, os parceiros podem renderizar marcadores em linha ou uma seção de origens dedicada.

* **Atualize facilmente os agentes do Criador legado para o Criador novo**
  Atualize um agente do Agentforce Builder legado em Configuração para o novo Agentforce Builder no Agentforce Studio com apenas alguns cliques. Antes, era preciso recriar manualmente seu agente no novo criador. Agora, você simplesmente especifica o agente e a versão que deseja atualizar e então criamos uma nova versão no novo criador para você. O agente atualizado inclui todos os subagentes, ações, mensagens e configurações do sistema, dados e conexões do agente original, convertidos em script do agente. Além disso, depois de atualizar, o Agentforce pode otimizar seu agente para o Script do agente para melhorar a confiabilidade e o desempenho do agente.

* **Crie um agente avançado com script do agente para terminar com o Guia de implementação atualizado**
  O Guia de implementação do Agentforce é nosso recurso prático mais abrangente para criar agentes na Salesforce Platform. Atualizamos o guia para o novo Agentforce Builder no Agentforce Studio. Siga em frente para criar um agente mais determinista com o Script do agente e veja o poder do raciocínio híbrido em ação. Aproveite os novos recursos de teste com a experiência de visualização e depuração aprimorada no Agentforce Builder e no novo central de testes do Agentforce no Agentforce Studio. Além disso, saiba como aproveitar ao máximo seu agente com um guia atualizado de Observabilidade. Conclua o guia de implementação para obter um agente voltado para o cliente totalmente funcional que possa responder a perguntas do cliente, criar e atualizar casos e escalar para um representante de suporte.

* **Encaminhe chamadas de voz do Agentforce usando SIP**
  Aproveite a conexão virtual flexível e econômica da Internet. Encaminhe chamadas para um agente de serviço Agentforce usando o Protocolo de início de sessão (SIP). Esse protocolo transmite chamadas pela Internet. Anteriormente, você podia rotear essas chamadas apenas com um número de telefone da Rede telefônica de alternância pública (PSTN).

* **Orquestrar outros agentes (beta)**
  Estenda as capacidades do seu agente com a Orquestração multifator para Agentforce (beta). Conecte seu agente do Agentforce a outros agentes especializados do Agentforce na sua organização do Salesforce. Juntos, eles podem colaborar perfeitamente em tarefas complexas. Ao fornecer um único ponto de contato unificado, os subagentes conectados ajudam seus usuários a realizar mais sem complicar várias sessões desconectadas.

* **Prepare-se para o modelo atualizado para a opção hospedada pela AWS no Agentforce**
  A opção AWS-Hosted para Agentforce usará o Anthropic Claude Haiku 4.5 no Amazon Bedrock mais tarde neste mês. No momento, ele usa o Claude Sonnet 4, que está no estado Legado no Amazon Bedrock.

* **Ações e subagentes padrão do agente novos e alterados**
  Adicione rapidamente funcionalidades avançadas a um agente com ações e subagentes padrão novos e alterados do agente.

* **Gerenciar bibliotecas de dados do Agentforce com a API ADL Connect (beta)**
  As Bibliotecas de dados do Agentforce (ADL) aumentam a precisão dos recursos de IA, como agentes do Agentforce, conectando-os às suas fontes de dados confiáveis. Com o lançamento da API do ADL Connect (beta), os clientes podem programaticamente criar e gerenciar bibliotecas de dados, permitindo que os desenvolvedores automatizem e integram o provisionamento de ADL diretamente em seus fluxos de trabalho e aplicativos.

* **Personalizar modelos de prompts gerenciados com substituições**
  Personalize modelos de prompts entregues por meio de pacotes gerenciados criando suas próprias versões. Quando um modelo é configurado como substituível, crie e ative versões locais do modelo sem modificar o modelo empacotado original.

* **Governar idiomas de resposta de prompt**
  Gerencie idiomas de resposta de prompts com controles automáticos e manuais no Criador de prompts. Restrinja respostas usando idiomas permitidos ou permita instruções de prompt para definir o idioma quando necessário. Mantenha a conformidade e a consistência em todo o conteúdo gerado.

* **Preparar-se para a data de redirecionamento do Claude Sonnet 4**
  As solicitações de modelo Claude Sonnet 4 serão redirecionadas para Claude Sonnet 4.6 em 26 de maio de 2026 porque Claude Sonnet 4 está no estado Legado na Amazon Bedrock. Recomendamos que você teste seus avisos e aplicativos com o novo modelo no Criador de prompts e Modelos de IA assim que possível, pois as respostas esperadas podem mudar.

> 📄 **Notas Completas:** consulte os detalhes completos na página do tópico [EINSTEIN](./releases/summer_26/einstein.md).
</details>

<details>
<summary><b>📄 EXPERIENCES (Clique para expandir 11 alterações)</b></summary>

* **Outras alterações**
  Aprenda sobre outros recursos disponíveis para sites do Experience Cloud.

* **Configurar experiências de autoatendimento assistido por IA em sites do Aura e do LWR**
  Configure e implemente um pacote de componentes de Autoatendimento com suporte de IA em seu site do Experience Cloud, incluindo o Agentforce Orchestrator, a barra de instruções, temas de sugestão, blocos de conteúdo dinâmico, a barra lateral do Concierge e o histórico de chat. Juntos, esses componentes fornecem experiências de Autoatendimento conversacionais personalizadas para usuários autenticados e convidados.

* **Habilite o Chatter para recursos dependentes do Chatter em sites do Aura e do LWR em novas organizações**
  O Chatter está desativado por padrão em todas as organizações do Salesforce criadas na versão Summer '26 e posteriores. Para criar um site do Aura usando o modelo Atendimento ao cliente ou adicionar feeds a um site do Aura ou do LWR nessas organizações, habilite o Chatter. Essa alteração não afeta organizações criadas antes da versão Summer '26.

* **Mantenha páginas privadas do LWR indisponíveis até que a configuração ou redefinição de senha seja concluída**
  Os visitantes agora precisam concluir a configuração ou redefinir a senha para poderem acessar páginas privadas em um site do LWR. Esse recurso, que alcança a paridade com sites do Aura, é habilitado por padrão para todos os sites do LWR, exceto aqueles que usam páginas personalizadas do Visualforce para gerenciamento de senhas. Nesses casos, habilite manualmente esse recurso.

* **Verificar arquivos para malware no Salesforce Files (disponível ao público em geral)**
  Para maior segurança na sua organização, os arquivos são verificados quanto a malware no Salesforce Files. Esse recurso, que agora está disponível ao público em geral, inclui algumas alterações desde a versão beta. A configuração "Verificar arquivos para vírus ou malware" agora aparece na nova página de Verificação de malware em Configuração. Nessa página, uma nova configuração habilita as notificações sobre arquivos maliciosos para usuários com a permissão Gerenciar arquivos maliciosos. Além disso, agora você pode atribuir a permissão Gerenciar arquivos maliciosos a qualquer usuário padrão. Antes, apenas administradores tinham essa permissão.

* **Visualizar e vincular registros relacionados de tabelas de dados de fluxo de tela**
  Mostre nomes de registro em vez de IDs do Salesforce em colunas de pesquisa da Tabela de dados em fluxos de tela que você adiciona a sites do Aura e do LWR. Para facilitar a navegação, transforme o nome do registro em um link que abre o registro relacionado em uma nova guia do navegador.

* **Personalizar fluxos de tela com mais substituições de estilo**
  Personalize fluxos de tela para seu público com opções de estilo expandidas. Agora você pode personalizar a aparência de mais componentes de fluxo de tela. Os novos componentes com suporte são Botão de ação, Endereço, Pesquisa de opção, Listas de opções dependentes, Email, Pesquisa, Nome, Telefone, Seletor, Alternância e URL.

* **Usar imagens de recurso estático para exibir texto em fluxos de tela (disponível ao público em geral)**
  Procure e carregue facilmente imagens de recursos estáticos diretamente de dentro do componente Texto de exibição. No componente Texto de exibição, você pode pesquisar imagens existentes, carregar novas imagens e adicionar texto alternativo, tudo dentro do fluxo de tela.

* **Reduza a rolagem em fluxos de tela com grupos de botões de opção empilhados**
  Use o componente Grupo de botões de opção para adicionar opções empilhadas horizontal ou verticalmente a seus fluxos de tela que você adiciona a sites do Aura e do LWR. Esse layout reduz a rolagem e fornece uma alternativa moderna e fácil de ler a botões de opção tradicionais ou listas suspensas.

* **Carregar arquivos maiores para sites do Experience Cloud**
  Agora você pode carregar arquivos de até 10 GB em um site do LWR por meio do componente Carregamento de arquivo. Antes, o limite era de 2 GB.

* **Permitir que todos os usuários do site enviem emails**
  O Salesforce agora exige a verificação no nível do domínio e no nível do usuário para enviar emails. Permita que usuários cujos domínios de email você não possa verificar enviem emails de seus sites. Por exemplo, habilite pessoas que usam serviços de email públicos como yahoo.com ou icloud.com para enviar mensagens de um site.

> 📄 **Notas Completas:** consulte os detalhes completos na página do tópico [EXPERIENCES](./releases/summer_26/experiences.md).
</details>

<details>
<summary><b>📄 FIELDSERVICE (Clique para expandir 28 alterações)</b></summary>

* **Notas de versão mensal do Field Service**
  Veja o que há de novo no Agentforce Field Service and Operations (antigo Field Service) para ajudar sua equipe a oferecer desempenho e atendimento ao cliente. Os recursos são lançados com frequência mensal, portanto, verifique aqui as informações mais recentes.

* **Simplificar a descoberta e a configuração de recursos do Field Service**
  Acelere a prontidão operacional com uma configuração simplificada para o Novo console de agendamento, criado para agendamento de alto desempenho, e para o Agentforce Builder, otimizado para a criação de agentes do Field Service Scheduling. Complemente essas ferramentas de agendamento com fluxos baseados em geografia acionados por locais de técnicos em tempo real e modelos de planilha de tempo para relatórios de trabalho padronizados. Para necessidades específicas do setor, você também pode configurar uma Solução residencial especializada para fluxos de trabalho de alto volume. Essas atualizações centralizadas fornecem uma estrutura que elimina a engenharia personalizada e simplifica a implantação.

* **Notas de patch mensais do desktop**
  Visualize as notas de patch mensais para a plataforma Field Service e o pacote gerenciado.

* **Notas de patch mensais móveis**
  Visualize as notas de patch móvel para o aplicativo Field Service Mobile para iOS e Android.

* **Criar agentes de agendamento do Field Service no novo Agentforce Builder**
  O novo Agentforce Builder agora dá suporte a agentes do Field Service Scheduling, para que você possa criar agentes para auxiliar seus clientes e seus funcionários. Os agentes criados aparecem nos modos de exibição de lista de agentes no aplicativo Agentforce Studio e nas páginas Configuração de agentes do Agentforce. Independentemente de onde você os inicia, esses agentes sempre são abertos no novo criador para garantir uma experiência consistente.

* **Expanda o agendamento autônomo para clientes potenciais**
  Permita que clientes potenciais reservem compromissos sem precisar de uma conta existente, transformando o Agentforce em uma poderosa ferramenta de geração de leads. Antes, apenas usuários autenticados podiam acessar o agente de agendamento.

* **Permitir que os trabalhadores gerenciem compromissos com Agentforce Employee Agent**
  Capacite seus funcionários a agendar e reagendar compromissos com Agentforce Employee Agent. Por exemplo, esse recurso permite que os trabalhadores móveis lidem com visitas de acompanhamento ou alterações de agenda de última hora diretamente no aplicativo Field Service Mobile, reduzindo a sobrecarga e aumentando a produtividade.

* **Personalizar porta-arquivos pré-trabalho com mais flexibilidade e velocidade**
  Personalize seus resumos pré-trabalho para incluir dados específicos de objetos como Comentários de caso ou Tipos de trabalho sem escrever Apex code personalizado. Novas opções de configuração simplificam sua configuração, permitindo que você implemente o contexto de trabalho relevante para seus trabalhadores móveis mais rapidamente, reduzindo a necessidade de lógica personalizada complexa. A detecção de alteração automática também atualiza os avisos pré-trabalho apenas quando os dados mudam, mantendo o alto desempenho do sistema enquanto mantém a precisão das informações.

* **Resolva problemas mais rapidamente com resumos interativos pré-trabalho**
  Capacite os trabalhadores móveis a fazer perguntas de acompanhamento, esclarecer detalhes do trabalho e solicitar documentação específica diretamente por meio de um widget interativo de Resumo pré-trabalho. Acionados pelo Agentforce, os usuários recebem respostas fundamentadas com base no histórico de ordens de trabalho, guias de solução de problemas e dados de ativos sem voltar manualmente ao contexto. Os trabalhadores móveis permanecem no fluxo de trabalho enquanto acessam os procedimentos ou documentos relevantes, a conformidade do site do cliente e dados de caso históricos por meio de texto simples.

* **Simplifique o suporte remoto roteando o Assistente remoto visual por meio do Omni-Channel**
  Melhore a eficiência da distribuição da carga de trabalho gerenciando sessões de VRA no fluxo de trabalho do Omni-Channel unificado. Ao integrar a VRA, o Omni-Channel usa rastreamento de capacidade e presença em tempo real para dar suporte à disponibilidade do representante do call center e encaminhar sessões apenas para aqueles com capacidade para processá-las. Os representantes do call center podem lidar com essas interações de vídeo ao vivo por meio de seu fluxo de trabalho padrão, proporcionando uma melhor experiência do cliente.

* **Oferecer suporte a sessões seguras de vários aplicativos no Assistente remoto visual**
  Promova um ambiente de suporte seguro e focado com seleção de aplicativo específica para sessões de VRA de vários aplicativos. Os representantes de call center agora podem iniciar sessões que oferecem suporte a vários aplicativos do cliente enquanto os clientes selecionam um único aplicativo para exibição. Essa seleção direcionada de aplicativo garante a privacidade expondo apenas os dados relevantes, reforçando a segurança da sessão e fornecendo solução de problemas mais eficiente para clientes que gerenciam vários aplicativos. Antes, os representantes do call center podiam iniciar sessões que ofereciam suporte a apenas um aplicativo.

* **Gerenciar participantes da sessão para melhor colaboração e segurança no Assistente remoto visual (VRA)**
  Obtenha sessões de VRA de vários participantes mais eficientes com recursos aprimorados de gerenciamento de sessão. Os representantes do call center agora têm um controle mais granular sobre a composição da sessão, aprovando novos colaboradores e removendo participantes desnecessários. Essa abordagem fornece uma colaboração mais focada durante interações por vídeo enquanto fortalece a segurança e a privacidade da sessão.

* **Aumente a produtividade com fluxos de captura de dados pré-preenchidos de uma fonte de dados usando repetidores**
  Reduza a fadiga de toque e melhore a precisão dos dados fornecendo aos trabalhadores móveis listas pré-preenchidas no componente Repetidor. Ao mapear uma variável de coleção como uma fonte de dados, os trabalhadores móveis podem verificar e atualizar registros existentes, como inspeções de ativo ou itens de inventário, sem adicionar linhas manualmente.

* **Expanda atualizações e exclusões de registro e obtenha mais flexibilidade para atribuir elementos em loops**
  Agora você pode atualizar ou excluir até 250 registros em uma única operação usando os elementos Atualizar e Excluir registro em fluxos de captura de dados. Além disso, com a remoção das restrições de validação, você pode usar elementos de Atribuição seguindo as operações Criar, Atualizar ou Excluir em um loop.

* **Aprimore a usabilidade personalizando o estilo e o layout da tela em fluxos de captura de dados**
  Aumente a produtividade do usuário personalizando as telas de fluxo para que correspondam aos seus processos de negócios exclusivos. Use seções e colunas para organizar a entrada de dados complexa e aplique estilos granulares a componentes individuais para uma interface profissional e intuitiva. Com o novo suporte para largura no nível do componente e alinhamento vertical em fluxos de captura de dados, você pode criar layouts precisos que garantem uma experiência consistente para os trabalhadores móveis.

* **Melhore a precisão do local com edições de mapa e atualizações offline**
  Permita que os trabalhadores móveis criem e atualizem registros do Salesforce diretamente do mapa para capturar dados de localização precisos para ordens de trabalho, objetos como ativos e objetos personalizados. Os mapas offline permanecem atualizados com atualizações automáticas com base na agenda de 24 horas futuras do usuário. Além disso, no Android, os downloads de mapas agora continuam em segundo plano para que o progresso não seja perdido se você alternar aplicativos ou a rede for interrompida.

* **Impulsionar a eficiência operacional com Insights móveis (beta)**
  O recurso Insights móveis fornece visibilidade do engajamento do técnico rastreando o uso ativo em relação às licenças atribuídas ao longo do tempo. Os gerentes podem usar esses dados para identificar baixas taxas de adoção em regiões específicas ou verificar se a equipe migrou com sucesso para a versão mais recente do aplicativo. Monitore a estabilidade do aplicativo na guia Telemetria rastreando percentuais de sessão sem falha e total de falhas de sessão em dispositivos iOS e Android. Essa funcionalidade garante que sua estratégia móvel se alinhe ao comportamento real do técnico, levando a decisões de investimento de hardware e software mais bem informadas.

* **Identifique o Console do supervisor legado com seu nome de guia atualizado**
  Diferencie facilmente a interface de despacho legada, agora renomeada como Console de despacho clássico, do novo Console de agendamento. Essa alteração se aplica ao nome da guia Field Service no aplicativo Field Service. Se você tiver personalizado anteriormente esse rótulo de guia, sua nomenclatura específica não será afetada.

* **Transforme sua experiência de agendamento com o novo console de agendamento**
  Capacite sua equipe a gerenciar operações complexas de agendamento do Field Service com um console intuitivo e elegante integrado a Componentes da Web Lightning para maior usabilidade e produtividade. Projetada para reduzir a carga cognitiva, essa interface de alto desempenho oferece suporte a configurações de várias telas, garantindo que seus supervisores permaneçam eficientes, focados e responsivos.

* **Melhore a qualidade do roteamento com o objetivo de serviço do mesmo site aprimorado**
  Maximize a produtividade e reduza o tempo de deslocamento definindo como os compromissos de serviço são agrupados em um único local. Agora você pode escolher entre agrupar compromissos dentro de uma proximidade próxima de até um segundo do tempo de deslocamento ou agrupar apenas aqueles com coordenadas idênticas. A correspondência de local exata garante que os trabalhadores móveis concluam todos os compromissos de serviço em um local específico, como um único prédio, antes de migrar para compromissos em um prédio próximo. Essa funcionalidade é específica para sites complexos, como campus ou fazendas, em que existem vários compromissos sem estradas de conexão tradicionais. Antes, nesses cenários, o objetivo tratava todos os prédios nas proximidades como um "mesmo site" devido a tempo de deslocamento zero, possivelmente resultando em roteamento "zigzag" entre estruturas adjacentes em um campus ou fazenda.

* **Aumentar a eficiência do trabalhador móvel agrupando compromissos de serviço nas proximidades**
  Garanta que os trabalhadores móveis maximizem sua presença em áreas de alto volume concluindo todos os compromissos em uma área específica antes de passar para a próxima. O objetivo de serviço Agrupar compromissos próximos é projetado especificamente para organizações com um grande número de compromissos por recurso, em que vários trabalhadores normalmente começam o dia no mesmo local base e cobrem a mesma área geográfica. Ao priorizar esse objetivo, você elimina a sobreposição de caminhos redundantes para que um trabalhador móvel "pertença" à área do dia, maximizando a produtividade. Antes, o mecanismo de agendamento priorizava o tempo de deslocamento geral mais curto para compromissos individuais. Essa lógica geralmente resultava em trabalhadores móveis "coletando" compromissos no caminho de um cluster, o que inadvertidamente fazia com que os compromissos restantes naquela área fossem divididos entre vários trabalhadores.

* **Acelere os tempos de chegada ao serviço excluindo a viagem residencial no Agendamento e otimização aprimorados**
  Melhore a velocidade de resposta e garanta que o trabalhador móvel com o menor tempo de deslocamento para o local seja despachado, independentemente de seu local de base no início ou no fim do turno. Agora você pode excluir deslocamento de casa, deslocamento de casa ou ambos dos cálculos do objetivo de serviço Minimizar deslocamento ao usar o Agendamento e otimização aprimorados. Essa funcionalidade é essencial para indústrias de alta urgência, como Assistência rodoviária e Serviços ambulatorios, em que a chegada rápida a um local supera o tempo de deslocamento adicional para um trabalhador voltar para casa. Antes, o mecanismo calculava o aumento total de deslocamento para todo o dia, incluindo a viagem de volta ao domicílio, o que geralmente penalizava o trabalhador móvel mais próximo se o domicílio deles estivesse longe do local. Ao excluir a viagem domiciliar, o mecanismo se concentra apenas no deslocamento entre compromissos de serviço, garantindo que o trabalhador móvel mais próximo seja despachado.

* **Melhore a precisão da agenda com estimativas de tempo de deslocamento personalizáveis para caminhões**
  Aprimore a precisão do agendamento e personalize como seus trabalhadores móveis navegam em rotas exclusivas aplicando um Fator de escala do tempo de deslocamento a seus perfis de modo de viagem de caminhão. Embora o roteamento de caminhão padrão ofereça uma base robusta, esse aprimoramento permite que você ajuste as estimativas de deslocamento para veículos comerciais com base em suas condições operacionais específicas, como aceleração mais lenta, limites de velocidade menores e condições de estrada complexas. Alinhe suas ETAs de veículo comercial aos tempos de deslocamento do mundo real para atender às suas necessidades para uma melhor satisfação do cliente.

* **Obter recomendações de agendamento com Insights de compromisso (disponível ao público em geral)**
  Entenda por que os compromissos de serviço não podem ser agendados durante a otimização e quais alterações você pode fazer para qualificar mais períodos e candidatos para agendamento. Por exemplo, considere remover uma regra personalizada que impede o agendamento.

* **Melhore as recomendações de agendamento com a API de Insights de compromisso (disponível ao público em geral)**
  Entenda por que um compromisso de serviço não pode ser agendado durante a otimização e quais regras de trabalho estão impedindo seu agendamento com a API de Insights de compromisso. O novo método do Apex getAppointmentInsights, na classe do Apex ScheduleService, retorna dados sobre por que um compromisso de serviço específico não pode ser agendado no Gantt, ajudando a ajustar sua política de agendamento.

* **Revise o histórico de solicitações de agendamento e otimização com relatórios de atividade (disponível ao público em geral)**
  Use Relatórios de atividade para obter informações sobre agendamento e otimização que você executou. Você pode gerar um relatório de atividade para um tipo de solicitação específico e identifique facilmente se ela obteve sucesso ou falhou. Por exemplo, gere um relatório sobre uma solicitação de Otimização global que falhou. A saída do relatório detalha os motivos da falha, permitindo que você aja e solucione o problema rapidamente.

* **Mantenha compromissos importantes agendados durante a otimização (disponível ao público em geral)**
  Proteja compromissos de serviço importantes, como aqueles com compromissos de cliente, prevenindo que sejam removidos da agenda durante a otimização global e no dia. Defina que compromissos manter agendados usando Manter critérios agendados. Por exemplo, garanta que os compromissos de emergência continuem inalterados. Durante a otimização, esses compromissos podem ir para um recurso ou horário diferente no SLA. Antes, você só podia detectar compromissos, limitando a capacidade de criar a agenda mais ideal. Você também pode manter compromissos agendados por meio da API usando o método atualizado Otimizar do Apex global, que é útil quando você quer agendar execuções de otimização e não está usando ações manuais.

* **Corrija sobreposições de agendamento facilmente com um fluxo de agendamento automatizado (disponível ao público em geral)**
  Enfrente os desafios de agendamento com um fluxo automatizado que otimiza os agendamentos de recursos para resolver sobreposições que ocorrem devido ao término tardio de um compromisso. Use as recomendações do modelo de fluxo ou ajuste o modelo para se adequar ao seu caso de uso.

> 📄 **Notas Completas:** consulte os detalhes completos na página do tópico [FIELDSERVICE](./releases/summer_26/fieldservice.md).
</details>

<details>
<summary><b>📄 GENERAL (Clique para expandir 25 alterações)</b></summary>

* **Gire seus certificados com mais frequência**
  Se você usa recursos que dependem de certificados, atualize os certificados relacionados com mais frequência. Uma alteração do setor diminui a vida útil máxima permitida do certificado de Segurança de camada de transporte (TLS) nos próximos três anos. A partir de 15 de março de 2026, a vida máxima de novos certificados é de 200 dias. Além disso, a Salesforce planeja interromper os anúncios públicos de rotação de certificado em 6 de julho de 2026.

* **Validar informações de domínio com mais frequência**
  Se você usa recursos que dependem de certificados, prepare-se para realizar Validação de controle de domínio (DCV) com mais frequência. Uma próxima mudança do setor diminui o período máximo de reutilização de validação de domínio para certificados de Segurança de camada de transporte (TLS) nos próximos três anos. A partir de 15 de março de 2026, o período máximo para reutilização de validação de domínio para novos certificados é de 200 dias.

* **Atualizar seus certificados mTLS**
  Se você usar certificados publicamente confiáveis para mTLS (segurança de camada de transporte mútua) e a CA raiz pública (autoridade de certificação) estiver na Lista raiz confiável do Chrome, mude para hierarquias de certificados separadas. O Google Chrome está aplicando alterações de política que limitam o uso desses certificados apenas à autenticação de servidor TLS (segurança de camada de transporte).

* **Preparar-se para IPv6**
  Para ajudar a mitigar a escassez de endereço IP do IPv4, o Salesforce está trabalhando nos bastidores para dar suporte ao IPv6. Se você usar listas de permissões de IP para restringir o tráfego de rede ou o acesso ao Salesforce, prepare-se para essa mudança. Use uma alternativa preferencial, como listas de permissões de domínio, ou atualize suas listas de permissões para incluir endereços IPv6.

* **Localize e implemente soluções facilmente com marcas de categoria e seleção guiada**
  Identifique as soluções mais adequadas ao seu negócio usando as marcas de categoria. A marcação de início rápido representa soluções que fornecem tudo o necessário para começar no dia 1, enquanto as soluções marcadas como Acelerador fornecem metadados de recurso. As soluções do Pacote de dados fornecem dados suplementares, incluindo dados de amostra e modelos. Personalize soluções para suas necessidades comerciais selecionando quais recursos e conjuntos de dados instalar.

* **Chatter é desativado por padrão em novas organizações**
  Em organizações do Salesforce criadas na versão Summer '26 e posteriores, o Chatter está desativado por padrão. Se você tiver recursos que exigem acesso à funcionalidade ou às APIs do Chatter, habilite o Chatter em Configuração. Por exemplo, ative o Chatter para usar o Feed do caso, inclua o Chatter em um site do Experience Cloud ou use o Chatter em organizações em que não há suporte para o Slack. Essa alteração não afeta organizações criadas antes da versão Summer '26.

* **Habilitar aprimoramentos de acessibilidade para cabeçalhos de página e janelas modais quando o zoom for maior que 200% (atualização de versão)**
  Para ajudar a cumprir as Diretrizes de acessibilidade de conteúdo da Web (WCAG) 2.2 para redimensionar e refluir, habilite o Lightning Experience para adaptar o comportamento de cabeçalhos de página e janelas modais quando visualizados em alta ampliação. Esse é o início do nosso esforço para cumprir as diretrizes de redimensionamento e refluxo do WCAG 2.2. Espere aprimoramentos de acessibilidade a outros elementos da IU em futuras atualizações de versão.

* **Habilitar aprimoramentos de acessibilidade para seletores de data, popovers, barras de utilitários inferior, cabeçalhos de registro (atualização de versão)**
  Para ajudar a cumprir as Diretrizes de acessibilidade de conteúdo da Web (WCAG) 2.2 para Redimensionar e Redefinir o fluxo, habilite o Lightning Experience para adaptar o comportamento dos seletores de data, pop-overs, barras de utilitários inferiores e cabeçalhos de registro quando visualizados em alta ampliação. Essa atualização de versão depende da atualização de versão Habilitar aprimoramentos de acessibilidade para cabeçalhos de página e janelas modais quando o zoom é maior que 200%. Certifique-se de habilitar essa atualização primeiro.

* **Habilitar aprimoramentos de acessibilidade para cartões, contêineres encaixados, listas de menus e painéis (atualização de versão)**
  Para ajudar a cumprir as Diretrizes de acessibilidade de conteúdo da Web (WCAG) 2.2 para Redimensionar e Redefinir o fluxo, habilite o Lightning Experience para adaptar o comportamento de cartões, contêineres acoplados, listas de menus e painéis quando visualizados em alta ampliação. Essa atualização de versão depende da atualização de versão Habilitar aprimoramentos de acessibilidade para cabeçalhos de página e janelas modais quando o zoom é maior que 200%. Certifique-se de habilitar essa atualização primeiro.

* **Habilite os aprimoramentos de acessibilidade para listas de tarefas e listas duplas do Lightning quando o zoom for maior que 200% (atualização de versão)**
  Para ajudar a cumprir as Diretrizes de acessibilidade de conteúdo da Web (WCAG) 2.2 para redimensionar e refluir, habilite o Lightning Experience para adaptar o comportamento de listas de tarefas e caixas de lista duplas do Lightning quando visualizadas em alta ampliação. Isso faz parte do nosso esforço para cumprir as diretrizes de redimensionamento e refluxo do WCAG 2.2.

* **Monitore o progresso do arquivo com novos status de atividade**
  Gerencie trabalhos de arquivamento com mais precisão com três novos status de atividade. O status Descartado indica uma importação abandonada e que os registros foram movidos para a Lixeira. Os status Interrupto e Máximo de interrupções rastreiam a recuperação quando o sistema retoma trabalhos automaticamente de pontos de verificação salvos. .

* **Gerenciar dados com mais eficiência com as novas configurações do aplicativo Arquivar**
  Gerencie seu ciclo de vida de dados com mais controle usando novas opções de configuração no aplicativo Arquivo. Agora você pode importar dados do Heroku diretamente, desarquivar conteúdo em bibliotecas privadas e habilitar novas tentativas automáticas para erros de validação de endereço de email.

* **Renomear recursos do aplicativo de arquivo para se alinhar aos padrões do Salesforce**
  Os recursos do aplicativo Arquivar têm novos nomes para alinhar com os produtos principais do Salesforce. O widget agora é o componente Arquivo e o SDK Arquivo agora é Arquivar Apex. Essas atualizações criam uma experiência consistente para administradores e desenvolvedores que trabalham em toda a plataforma.

* **Prepare-se para a descontinuação de seu próprio pacote gerenciado de arquivo e arquivo legado**
  O Salesforce descontinua o pacote gerenciado Arquivo próprio e os produtos Arquivo legado para priorizar uma solução de arquivamento nativa. A transição lida com limitações de escalabilidade e visibilidade de erros e melhora o desempenho. Para manter os recursos de arquivamento, migre para o Arquivo 2.0 antes que a assinatura atual termine.

* **Priorizar seus principais leads com pontuação de pessoas em fundamentos**
  Pare de adivinhar quais clientes potenciais estão prontos para se tornar clientes. A Pontuação de pessoas avalia o quão bem os leads e os contatos se encaixam no seu perfil de cliente ideal e o quão ativos eles estão se engajando com seu marketing. Ao atribuir pontos para comportamentos específicos e características demográficas, você pode criar segmentos mais inteligentes e garantir que você esteja enviando a mensagem certa para a pessoa certa no momento certo.

* **Transformar o tráfego da Web em percepções acionáveis com rastreamento da Web**
  Crie um panorama mais perceptivo das jornadas de seus clientes acompanhando o engajamento de páginas da Web internas e externas. Ao capturar atividades do visitante em tempo real, você pode criar segmentos de alta intenção e proporcionar experiências de marketing mais personalizadas.

* **Aumente o desempenho e a confiabilidade com o Inspetor de receita de pipelines de dados do Salesforce**
  Use o inspetor de receita para solucionar problemas e melhorar o desempenho. Aprofunde-se nos trabalhos de receita para visualizar as informações detalhadas em cada estágio do fluxo. Monitore o desempenho e o status de nós individuais. Você pode identificar rapidamente uma junção lenta ou um nó de transformação que falhou em fazer correções imediatamente.

* **Exportar agendas de receita para seu calendário externo para fácil rastreamento**
  Exporte suas agendas de receita de Pipelines de dados do Salesforce como formato de calendário (ICS) para referência rápida e visibilidade em seu calendário. Por exemplo, compartilhe a agenda de execução de uma receita com as partes interessadas em outras equipes para coordenar a prontidão dos dados e os prazos de relatório.

* **Simplifique o backup de receita com upload e download diretos no Gerenciador de dados**
  Economize tempo e cliques acessando seu JSON de receita de Pipelines de dados do Salesforce para backups ou edição. Agora você pode carregar e baixar suas receitas diretamente do Gerenciador de dados sem abrir o editor de receita.

* **Melhore o desempenho da receita de dados de instantâneo com ações de inserção e inserção e exclusão otimizadas (disponível ao público em geral)**
  Reduza o tempo de processamento com execuções de receita de dados mais rápidas. Em vez de processar todas as linhas nos dados de instantâneo, as ações de inserção e atualização e exclusão otimizadas são executadas incrementalmente em subconjuntos dos dados, resultando em execuções mais rápidas. Esse recurso agora está disponível ao público em geral.

* **Exportar dados de pipelines de dados do Salesforce para o Azure Data Lake (disponível ao público em geral)**
  Grave seus dados de Pipelines de dados do Salesforce no Azure Data Lake da Microsoft com o conector de saída do Azure Data Lake. Escreva conjuntos de dados de saída de receita como um ou mais arquivos .csv em seu data lake, melhorando seus processos de negócios gerais com dados melhores. Por exemplo, você pode gerar dados de atendimento ao cliente processados e transformados para ajudar sua equipe a melhorar a satisfação do cliente. Esse recurso agora está disponível ao público em geral.

* **Mostrar a posição específica da categoria em cartões do participante da lista de espera**
  Alinhe os cartões do participante da lista de espera com seu pedido de serviço específico do negócio mapeando um campo personalizado para o período de sequência do cartão. Quando você mapeia um campo personalizado, o cabeçalho do cartão mostra o valor desse campo em vez do índice global gerado pelo sistema. Por exemplo, um participante que está primeiro na fila para uma categoria de serviço pode aparecer em quarto na sequência global. O mapeamento de um campo personalizado para o período de sequência corrige essa incompatibilidade e os recepcionistas do lobby veem a posição que corresponde à ordem de chamada real. Antes, os cartões sempre mostravam um número sequencial global que não refletia a prioridade específica da categoria.

* **Ajude os usuários a resolver erros de compromisso mais rapidamente com mensagens de validação personalizadas**
  Quando uma ação de compromisso falha, forneça aos usuários uma mensagem clara de por que a ação foi bloqueada. Você pode definir mensagens para as ações Iniciar compromisso, Encerrar compromisso e Aceitar compromisso. Antes, a IU mostrava uma mensagem de erro genérica mesmo quando você configurava a lógica de validação personalizada, deixando os usuários sem orientação.

* **Mantenha componentes de lobby personalizados sincronizados com seleções de território**
  Mantenha a precisão dos dados no painel Gerenciamento de lobby agora que os componentes personalizados podem ser atualizados quando um recepcionista altera o território de serviço ativo. O Salesforce Scheduler agora publica uma mensagem padrão do Lightning Message Service (LMS) que mantém as listas de espera, os compromissos e os modos de exibição de dados personalizados consistentes. Antes, os componentes personalizados não tinham uma maneira padronizada de detectar uma alteração de território.

* **Mantenha-se atualizado com o Salesforce My Trust Center (disponível ao público em geral)**
  Monitore incidentes, versões principais, versões de patch e atualizações de manutenção. Melhore a colaboração global com rótulos localizados e mensagens padrão em idiomas de plataforma com suporte. Visualize as datas no formato preferencial do navegador e revise os horários do sistema em notação de 24 horas.

> 📄 **Notas Completas:** consulte os detalhes completos na página do tópico [GENERAL](./releases/summer_26/general.md).
</details>

<details>
<summary><b>📄 HYPERFORCE (Clique para expandir 3 alterações)</b></summary>

* **Acessar o Salesforce em mais regiões com o Hyperforce**
  O Hyperforce está disponível em 18 países, dando a você mais escolha e controle sobre a residência de dados. A Salesforce abriu uma nova região do Hyperforce em Cidade do Cabo, África do Sul, em maio de 2026.

* **Novos produtos e recursos disponíveis na Defesa do Government Cloud**
  Obtenha recursos adicionais para sua organização de Defesa do Government Cloud com produtos e recursos recém-disponíveis.

* **A continuidade avançada entre regiões alcança objetivos de recuperação mais rápidos**
  A Continuidade avançada entre regiões (ACRC) do Salesforce agora oferece objetivos de ponto de recuperação e tempo de recuperação (RTO/RPO) aprimorados de 12 horas e 4 horas, reduzindo o tempo máximo de inatividade e a possível perda de dados após uma catástrofe regional extraordinária.

> 📄 **Notas Completas:** consulte os detalhes completos na página do tópico [HYPERFORCE](./releases/summer_26/hyperforce.md).
</details>

<details>
<summary><b>📄 INDUSTRIES (Clique para expandir 283 alterações)</b></summary>

* **Simplificar a descoberta e a configuração de recursos do Gerenciamento de ciclo de vida do ativo**
  Com o Salesforce Go, você pode descobrir, configurar, configurar recursos de Gerenciamento de ciclo de vida do serviço do ativo e rastrear o uso de recursos, tudo em um único local em Configuração. Saiba mais sobre recursos e obtenha ajuda com configuração acessando links e recursos de conteúdo. Explore mais produtos e recursos de Gerenciamento de ciclo de vida do ativo e, se você tiver ativado o aplicativo Sua conta, poderá comprar licenças de complemento para alguns recursos diretamente do Salesforce Go.

* **Editar e excluir planilhas usando o Agentforce**
  Os técnicos de campo podem editar e excluir planilhas de horários e entradas de planilhas usando comandos de linguagem natural por meio do Agentforce. Atualize várias planilhas de horário de uma só vez editando campos, alterando categorias em massa ou removendo entradas, tudo em uma única conversa.

* **Gerenciar planilhas de horários da equipe no campo**
  Os leads da equipagem podem criar e gerenciar quadros de horários para os membros da equipe diretamente no aplicativo Field Service Mobile. Inicie e encerre turnos para membros da equipe selecionados, envie planilhas de horários em nome deles e visualize as solicitações de folga do membro da equipe e o histórico da planilha de horários. Quando os membros da equipe registram planilhas de horário para o dia, o cartão da equipe preenchido aparece abaixo do cartão de resumo das planilhas, dando aos leads da equipe visibilidade rápida das entradas de horário da equipe.

* **Criar várias planilhas de horários para um intervalo de datas**
  Gere várias planilhas de horários para um intervalo de datas diretamente do seu aplicativo móvel. Uma planilha de tempo separada é criada para cada dia no intervalo, com a prevenção de duplicação integrada para garantir a precisão dos dados.

* **Revisar planilhas de horários com visualizações de resumo aprimoradas**
  Revise os resumos da planilha de horários com informações mais abrangentes antes de enviá-los para aprovação. Veja os detalhes de horário regular, hora e metade e horário duplo. Filtre resumos agregados por período de pagamento e semana.

* **Criar entradas automáticas do cronograma ocioso**
  Preencha automaticamente as lacunas entre as entradas da planilha de horários com o tempo ocioso para garantir que os registros sejam completos para o processamento da folha de pagamento. Crie entradas de planilha de horário ociosas em vez de estender entradas existentes, ajudando a manter registros precisos de tempo de trabalho produtivo versus tempo ocioso ou de transição entre tarefas.

* **Editar e reenviar planilhas de horários rejeitadas**
  Corrija erros em planilhas de horários rejeitadas usando os mesmos recursos que planilhas de horários verificadas, corrija problemas identificados pelos supervisores e envie novamente para processamento. Isso simplifica o fluxo de trabalho de correção e reduz os atrasos no processamento da planilha de horas e na folha de pagamento.

* **Atualize dados da planilha de horas em dispositivos móveis com um gesto de pull-down**
  Atualize os dados da planilha usando o gesto de pull-down familiar na página inicial, detalhes da planilha, ordens de trabalho, refeições e presentes, histórico e páginas de folga.

* **Simplifique solicitações de reparo de boa vontade com um processo de serviço predefinido**
  Simplifique a admissão e o cumprimento de solicitações de reparo de goodwill usando um processo de serviço predefinido baseado em Omni, melhorando a experiência do cliente e reduzindo os custos. Os revendedores ou fabricantes de equipamento original podem usar o processo de serviço de Reparo de boa vontade para selecionar facilmente veículos ou ativos para um cliente, revisar os detalhes de cobertura de garantia existentes, selecionar uma ordem de trabalho e adicionar comentários relacionados a essas ordens de trabalho a serem usadas para lidar com a solicitação de boa vontade. Um caso é criado com os detalhes da solicitação para o revendedor, em que ele pode visualizar ordens de trabalho anteriores de um cliente, determinar as porcentagens de contribuição de boa vontade a serem aplicadas a itens de linha e justificar suas decisões. Depois que uma reivindicação é gerada, os valores da reivindicação e os registros de detalhes do pagamento são atualizados automaticamente. Um email é enviado ao cliente com os detalhes relevantes, melhorando a eficiência do serviço.

* **Acelere a configuração de recursos automotivos com pacotes de soluções**
  Acelere a instalação e a configuração de recursos, como Ativos conectados, Veículos conectados e Processos de serviço, usando pacotes de soluções do Salesforce GO. Gerencie definições de contexto, falha crítica, definições de telemetria e definições de ação e alertas de serviço configurando Ações remotas e outros recursos relacionados de um único local. Configure processos de serviço, como Adiamento do pagamento e Modificação da data de vencimento do pagamento, em um fluxo.

* **Aprimorar percepções automotivas com o Tableau Next Analytics**
  Use o Automotive Insights, um aplicativo de análise habilitado pelo Tableau para Automotive, para fornecer aos revendedores e fabricantes de equipamento original uma visualização abrangente em 360 graus de leads, portfólio e percepções de veículos, volumes planejados, vendas reais e desempenho do revendedor. Analise tendências de vendas de veículo, inventário, requisitos da parte interessada e outras percepções por meio dos painéis Insights do portfólio de veículos, Desempenho do revendedor, Desempenho do fabricante de equipamento original e Inteligência de leads. Integre e analise tendências e desempenho com mais eficiência, fornecendo percepções mais profundas sobre vendas de produto e satisfação do cliente.

* **Expanda o acesso a dados automotivos usando novos objetos de modelo de dados**
  Para oferecer suporte a experiências em fluxos de dados predefinidos e percepções calculadas, use novos objetos de modelo de dados (DMOs) para ingerir metadados no Data 360. Dê suporte a análises mais recentes usando o Tableau Unified Analytics e outros casos de uso relevantes no Data Cloud.

* **Importar dados de veículo e produto em massa usando modelos**
  Carregue grandes volumes de dados de produto, ativo e veículo de arquivos CSV usando modelos predefinidos do Mecanismo de processamento de dados (DPE). Você pode preencher rapidamente seus registros mapeando dados CSV para vários objetos ao mesmo tempo, reduzindo a entrada manual para conjuntos de dados grandes. Crie registros de veículo de maneira mais simplificada agora, em vez de criar produtos, definições de veículo e ativos separadamente, como antes. Lide com relacionamentos de objeto complexos, como conectar Veículos a ativos ou Produtos a definições de veículo, e acelere sua configuração inicial e garanta a consistência dos dados em operações automotivas.

* **Objetos novos e alterados para Agentforce Automotive**
  Faça mais com objetos novos e atualizados do Agentforce Automotive, anteriormente Automotive Cloud.

* **Gerenciar declarações de garantia e cobertura com a assistência de IA**
  Resuma as declarações enviadas de tipos como declarações de garantia ou declarações de goodwill, verifique o status dessas declarações e valide as informações de garantia de seus veículos, ativos ou peças usando o agente Assistência de declarações de garantia automotiva. Os clientes e os representantes de serviço em Fabricantes de equipamento original e Revendedores podem confirmar facilmente a cobertura para declarações de garantia por meio de uma interface conversacional robusta dos portais da Comunidade de clientes. Melhore as percepções de qualidade do produto, a experiência do usuário e a fidelidade do cliente fornecendo atualizações de garantia em tempo real.

* **Aprimorar a produtividade de vendas para revendedores**
  Transforme a jornada de compra de veículo em uma experiência conversacional orientada por dados para usuários parceiros usando o agente do Automotive Sales Concierge para parceiros. Os representantes de vendas de concessionárias podem usar linguagem natural para pesquisar definições de veículo, produtos ou peças, bem como acessórios relacionados a veículos selecionados. Eles podem capturar oportunidades de vendas de veículo, criar cotações, agendar compromissos de test drive e iniciar avaliações de troca facilmente, melhorando significativamente a eficiência. Eles também podem criar rascunhos de emails de resumo para clientes usando a assistência de IA, ajudando a criar Trust e fomentar a fidelidade dos clientes.

* **Estenda com eficiência a duração dos contratos de assinatura**
  Simplifique a admissão e o cumprimento de solicitações de extensão de assinatura para assinaturas do Automotive usando um processo de serviço predefinido. Os representantes de serviço podem rapidamente iniciar uma solicitação de processo de serviço em nome dos clientes usando o modelo Extensão de assinatura do Catálogo unificado, melhorando a qualidade do atendimento ao cliente e reduzindo o tempo de processamento. Visualize resumos de assinatura atuais, calcule pagamentos mensais atualizados para novos prazos, automatize verificações de elegibilidade e carregue os documentos de seguro necessários, tudo em um fluxo. Os clientes podem acessar o formulário baseado em OmniScript no site do Experience Cloud e registrar uma solicitação para estender seus contratos de assinatura.

* **Simplificar solicitações de reembolso e disputas de transação**
  Gerencie pagamentos excedentes, cobranças duplicadas e outros problemas relacionados à transação usando um processo de serviço predefinido. Os representantes de serviço podem fornecer uma experiência do cliente tranquila e resolver disputas rapidamente em nome dos clientes usando o modelo de Disputa de transação do Catálogo unificado, melhorando a eficiência operacional. Automatize a ingestão inicial coletando dados financeiros do cliente, capturando a lista obrigatória de transações e categorizando disputas com base em motivos predefinidos. Os usuários também podem carregar a documentação de suporte e preencher os questionários de avaliação necessários no mesmo fluxo para garantir uma resolução mais rápida.

* **Resolver solicitações financeiras automotivas automaticamente com agentes de IA**
  Implemente agentes autônomos para lidar com solicitações de serviço de rotina para empréstimos e assinaturas do Automotive, eliminando o contato humano com consultas repetitivas de alto volume, o que otimiza a equipe e melhora as taxas de resolução de primeiro contato. Verifique usuários, entenda os requisitos e resolva problemas como atualizações de endereço ou reembolsos de taxas instantaneamente. Essa automação reduz o custo de serviço enquanto fornece aos clientes a disponibilidade imediata de suporte.

* **Acelerar a validação de documentos com IA**
  Valide documentos de KYC em relação a dados em registros do Salesforce para empréstimos e assinaturas do Automotive usando a assistência de IA. Identifique rapidamente inconsistências entre o documento e seus registros para acelerar a tomada de decisão e reduzir a verificação manual de documentos, que costuma ser lenta e sujeita a supervisão.

* **Gerenciar passivos financeiros granulares com acúmulos avançados**
  Obtenha mais controle sobre seus relatórios financeiros acompanhando acúmulos de descontos granulares independentemente de suas agendas de pagamento. Com Acúmulos avançados em Desconto e Gerenciamento de acúmulos avançado, você obtém visibilidade profunda de passivos financeiros para garantir previsões precisas conforme as vendas ocorrem. Use ajustes manuais para manter o controle fiscal total e aproveite o rastreamento granular por membro e tipo de desconto para entender melhor o gasto de incentivo. Esses cálculos de alto volume são desenvolvidos com mecanismos de processamento de dados (DPE) de alto desempenho no Data 360.

* **Traduzir dados em percepções com o Kit de dados de gerenciamento de receita de canal**
  Obtenha dados do programa de desconto unificados, precisos e padronizados usando o kit de dados de Gerenciamento de receita de canal. Transmita automaticamente os dados do Salesforce Core para o Data 360 e mapeie definições do programa de desconto diretamente para objetos de modelo de dados (DMOs) padrão, criando uma única fonte de dados incentivadores. Essa arquitetura unificada serve como a base para os painéis do Tableau Next, habilitando análises interativas integradas que aceleram a tomada de decisão.

* **Otimizar o processamento de alto volume com DPEs no Data 360**
  Melhore o desempenho do sistema e solucione os limites do pipeline de dados no nível da organização executando cálculos complexos de incentivo diretamente no Data Cloud. Fabricantes com operações de alto volume, como Descontos, Rotação de estoque e Inventário de canais, exigem um mecanismo de processamento robusto para transformação de dados em grande escala. Ao executar definições do Mecanismo de processamento de dados (DPE) no Data Cloud, você pode dar suporte ao processamento de incentivo complexo em escala com maior velocidade e eficiência.

* **Acelerar a configuração com o Salesforce Go**
  O Salesforce Go expande seu suporte para funcionalidades de Acúmulos avançados em Gerenciamento de acúmulos e descontos avançado, fornecendo uma experiência de configuração única e personalizada. Acesse o conteúdo de ajuda e os recursos de configuração para aprender rapidamente os recursos e concluir a configuração.

* **Objetos alterados para gerenciamento de receita de canal**
  Faça mais com os objetos atualizados de Gerenciamento de receita de canal.

* **O Assistente de uso e faturamento foi descontinuado**
  O Assistente de uso e faturamento foi descontinuado na versão Summer '26. Você não poderá mais usar o Assistente de uso e faturamento em organizações de comunicações na versão Summer '26 e posteriores.

* **Automatize a cotação corporativa com ações invocáveis para fluxos assistidos pelo agente**
  Desbloqueie a experiência de cotação assistida pelo agente no Gerenciamento de vendas Enterprise implementando ações invocáveis predefinidas. Você pode usar essas ações de invocação para criar e acionar tópicos e ações personalizadas do agente com instruções específicas. Ao automatizar tarefas de rotina, como início de negócio e agrupamento de vários locais, suas equipes podem acelerar a velocidade do negócio e reduzir a sobrecarga operacional.

* **Novas ações invocáveis no Gerenciamento de vendas Enterprise**
  Faça mais com as novas ações invocáveis no Gerenciamento de vendas Enterprise.

* **Automatize recriações de cotação complexas usando APIs de clone profundo**
  Replicar cotações corporativas, de vários sites e de um único site usando uma API invocável para eliminar a recriação manual de estruturas de negócios complexas. Capacite seus administradores e representantes de vendas a realizar clones profundos que preservam todos os itens de linha, substituições de precificação e relacionamentos hierárquicos sem usar uma interface do usuário. Integre essas ações a fluxos de trabalho automatizados personalizados para criar experiências agentes em alta escala.

* **Lide com várias criações e envios de subpedido simultaneamente**
  Maximize sua taxa de transferência processando várias conversões de cotação para pedido simultaneamente em várias contas comerciais. O sistema agrupa de modo inteligente solicitações por conta para permitir a criação e o envio simultâneos de vários subpedidos, reduzindo os atrasos no processamento.

* **Atribuir valores de membro a atributos somente leitura e ocultos em cotações corporativas**
  A Vinculação de membro da cotação (QMB) em cotações corporativas agora dá suporte ao mapeamento de dados para atributos somente leitura e ocultos, desde que os mapeamentos sejam definidos explicitamente na configuração do Mecanismo de regras de negócios. Isso acelera a criação da cotação removendo o trabalho manual.

* **Capture e reutilize configurações de produto com modelos de carrinho**
  Padronize seu processo de vendas convertendo configurações de produto existentes de um carrinho em modelos reutilizáveis. Os representantes de vendas podem usar esses modelos pré-configurados ao criar cotações corporativas, tornando o processo de cotação mais rápido e consistente.

* **Controlar ações do Visualizador do ativo com uma permissão personalizada**
  Simplifique e aprimore a segurança entre fluxos de trabalho do ativo gerenciando o acesso para duas ações do usuário por meio da permissão personalizada Adicionar ativos a cotações empresariais no Gerenciamento de vendas Enterprise: a ação Alterar para cotação na tabela Visualizador de ativo e a ação Adicionar ativo na tabela Resumo.

* **Ler dados mais facilmente com layouts de tabela otimizados**
  Leia dados mais facilmente com larguras de coluna responsivas e espaçamento otimizado dentro de tabelas no Gerenciamento de vendas Enterprise.

* **Cotação rápida do Einstein para o Gerenciamento de vendas corporativas está programada para descontinuação**
  A descontinuação da Cotação rápida do Einstein para Gerenciamento de vendas corporativas está agendada para a versão Winter '27. Você não poderá mais usar a Cotação rápida do Einstein em organizações de Gerenciamento de vendas corporativas na versão Winter '27 e posteriores.

* **Outras alterações no Gerenciamento de vendas Enterprise**
  Prepare-se para a descontinuação dos recursos do Gerenciamento de vendas Enterprise na versão Winter '27.

* **Gerenciar cotações e pedidos com o editor de linha aprimorado**
  Melhore a visibilidade com o layout de grade única simplificado e a interface de planilha limpa no Editor de linha de transação de vendas. Os representantes de vendas podem filtrar e classificar linhas de cotação e pedido e usar um painel lateral para visualizar detalhes e aplicar promoções. Se você tiver implementado a configuração para o editor de linha antes da versão Summer '26, recomendamos usar o Editor de linha de transação de vendas na página de registro de pedido e cotação.

* **Objetos novos e alterados no Revenue Cloud para comunicações**
  Faça mais com os objetos novos e atualizados do Revenue Cloud para comunicações.

* **Atualizar o namespace para upload de fluxo CSV**
  Atualize suas integrações para refletir o novo namespace para o fluxo Carregar CSV. Essa alteração garante que seus processos permaneçam compatíveis com as atualizações de arquitetura mais recentes. Seus administradores devem usar o namespace runtime_rev_mltrcpnt para chamar esse fluxo com êxito.

* **Refinar o acesso a vários sites com novas configurações**
  Dê aos seus representantes de vendas acesso ao recurso de vários sites habilitando as novas configurações de Cotação baseada em local e Pedido. Habilitar essa configuração ajuda a alinhar sua implementação existente a requisitos de negócios baseados em local específicos. Essa alteração garante que os representantes mantenham o acesso necessário para gerenciar suas transações específicas do local.

* **Refinar o acesso de vários assinantes com novas configurações**
  Dê aos seus representantes de vendas acesso ao recurso Assinante múltiplo habilitando as novas configurações de Cotação baseada em assinante e Pedido. Habilitar essa configuração ajuda a alinhar sua implementação aos requisitos de negócios baseados em assinante. Essa alteração garante que os representantes mantenham o acesso necessário para gerenciar suas transações específicas do assinante.

* **Adicionar vários assinantes a cotações e pedidos**
  Os representantes de vendas podem rapidamente adicionar dados do assinante automatizando o processo por meio de uploads de arquivo CSV. Você pode carregar um arquivo CSV com dados do assinante na guia Assinantes de uma cotação ou pedido. O Salesforce mapeia automaticamente as colunas do arquivo. Os representantes de vendas também podem mapear manualmente colunas do arquivo carregado para campos nos objetos destinatário do item de linha de cotação ou destinatário do produto do pedido. Como alternativa, os representantes também podem adicionar dados do assinante manualmente.

* **Procurar catálogos de produtos e atribuir produtos a assinantes**
  Os representantes de vendas podem explorar os catálogos de produtos na página de registro de pedido ou cotação. Com base nas seleções de assinante, os representantes podem atribuir os produtos a toda a seleção de uma só vez. Você também pode revisar e editar os assinantes selecionados na página de catálogos de produtos.

* **Criar e gerenciar grupos de assinantes para simplificar ofertas**
  Os representantes de vendas podem configurar e aplicar uma oferta a um grupo de assinantes sem clonar a oferta para cada assinante. Isso melhora a escalabilidade, a usabilidade e o desempenho para itens de linha de cotação gerenciando a oferta em uma única representação dos itens de linha de cotação associados a vários assinantes.

* **Criar e gerenciar um grupo de assinantes vazio para simplificar ofertas**
  Os representantes de vendas podem criar um grupo sem adicionar assinantes. Você pode configurar e aplicar uma oferta ao grupo vazio sem clonar a oferta para cada assinante. Isso melhora a escalabilidade, a usabilidade e o desempenho para itens de linha de cotação gerenciando a oferta em uma única representação associada a vários assinantes, mesmo quando nenhum assinante é adicionado inicialmente.

* **Criar vários pedidos a partir de uma única cotação**
  Aprimore a eficiência dos representantes de vendas automatizando a criação de vários pedidos de uma única cotação com base em diferentes critérios, como assinantes, campos ou grupos. Personalize a criação do pedido para suas necessidades comerciais exclusivas, garantindo que cada pedido seja preciso e alinhado aos seus requisitos específicos. Isso melhora a escalabilidade e a eficiência operacional.

* **Objetos novos e alterados para vários assinantes**
  Faça mais com os objetos Revenue Cloud para comunicações atualizados para assinantes.

* **Atualize sua definição de contexto para usar novos recursos de promoção**
  Aprimore as transações de vendas usando o nó atualizado SalesTransactionItemPriceAdjustment na definição de contexto do Contexto de vendas do consumidor. Se você tiver estendido a definição de contexto do Contexto de vendas do consumidor na versão Spring '26, certifique-se de estender as definições de contexto atualizadas do Contexto de vendas do consumidor para usar os recursos de promoção.

* **Aplicar promoções ao carrinho em vendas do consumidor para impulsionar as vendas**
  Aumente as vendas integrando o Gerenciamento de promoções globais (GPM) ao pacote de API de vendas do consumidor. Configure facilmente os detalhes da promoção, incluindo tipo, duração e elegibilidade, e adicione cupons para promoções manuais. Esse aprimoramento fornece detalhes consistentes de promoção e desconto do carrinho até o pedido e o ativo finalizados durante a ativação. Sua equipe de vendas tem a flexibilidade de fechar todos os negócios com a melhor oferta.

* **Objetos novos e alterados para vendas do consumidor**
  Faça mais com os objetos novos e alterados para vendas do consumidor.

* **APIs REST do Connect novas e alteradas para vendas do consumidor**
  Use os recursos novos e alterados disponíveis com Vendas do consumidor para atender aos seus requisitos de negócios.

* **Transformar a experiência financeira do estudante**
  Forneça aos alunos uma visão clara de suas obrigações financeiras por meio de um painel unificado para faturamento em tempo real, pagamentos seguros e auxílios ou bolsas de estudo desembolsados. Reduza consultas administrativas oferecendo um único local para os alunos acessarem faturas, saldos em execução e históricos de pagamento completos. Economize o tempo da sua equipe com a reconciliação de conta automatizada que oferece controle e visibilidade granulares.

* **Gerenciar contas financeiras com visibilidade aprimorada**
  Forneça um fluxo de trabalho para sua equipe de contas do estudante para gerar faturas para os alunos com base em agendas de faturamento aprovadas. Simplifique a cobrança de débitos e melhore o fluxo de caixa institucional usando o processamento de pagamento seguro integrado. Os consultores de estudantes atualizam o status da conta e a propriedade de modo rápido e preciso, fornecendo um controle financeiro proativo para sua universidade.

* **Aumente a transparência do auxílio financeiro com novos componentes da Web Lightning**
  Atenda à crescente demanda por transparência em informações de ajuda financeira fornecendo uma experiência de autoatendimento simplificada para estudantes potenciais, solicitantes e alunos atuais. Os novos componentes da Web do Lightning de ajuda financeira permitem criar um portal abrangente de ajuda financeira.

* **Gerenciar dados de ajuda financeira com o Kit de dados de educação**
  Estabeleça um sistema de gerenciamento de dados centralizado para registros de ajuda financeira do estudante usando o Kit de dados de educação, que inclui sete novos objetos de modelo de dados (DMOs). Os novos DMOs resolvem o problema de dados de ajuda financeira fragmentados, fornecendo a estudantes e funcionários uma visão unificada para ajudar com decisões de ajuda financeira. Use os DMOs com os novos componentes da Web Lightning de percepções de ajuda financeira para permitir que os usuários acompanhem rapidamente o status de solicitações e desembolsos.

* **Avaliar créditos de transferência não articulados e automatizar a criação de regra de equivalência**
  Dê aos seus professores e administradores um espaço de trabalho estruturado para revisar o aprendizado anterior complexo, como experiência militar e portfólios. Avalie créditos de transferência não articulados usando fluxos de trabalho unificados e converta essas decisões em regras institucionais permanentes. Automatize o processo de correspondência de aprendizado anterior para candidatos futuros para acelerar o tempo para a graduação e garantir uma correspondência de crédito mais precisa em todos os registros de alunos.

* **Medir o impacto de relacionamentos corporativos**
  Avalie e comunique o impacto institucional em uma estrutura padronizada orientada por dados. Novos objetos e campos conectam programas acadêmicos, relacionamentos do empregador e análises de Gestão de resultados para rastrear como as parcerias se traduzem em estágios e posicionamentos de emprego. Os fluxos de trabalho automatizados agregam essas percepções para ajudar as instituições a identificar quais colaborações oferecem suporte mais eficaz aos resultados da equipe.

* **Aprimorar a descoberta de curso com pesquisa avançada**
  Dê suporte aos alunos para realizar pesquisas intuitivas e direcionadas para identificar cursos e seções adequados às suas agendas e necessidades acadêmicas. Configure vários critérios de pesquisa ao mesmo tempo, incluindo dias de reunião e disponibilidade da seção ou da lista de espera, para mostrar apenas resultados correspondentes. Os alunos podem limitar as opções e se registrar nos cursos certos de maneira eficiente.

* **Orientar os alunos para agendas de curso sem conflitos**
  Elimine a adivinhação do registro do curso mostrando aos alunos quais seções do curso se sobrepõem. As verificações automáticas alertam os alunos sobre conflitos de agendamento no carrinho de registro. Ative a imposição opcional de conflitos de tempo para bloquear o registro de seções sobrepostas.

* **Otimizar operações de curso com o Tableau Next**
  Forneça aos registradores e às equipes de operações uma visualização integrada da disponibilidade do curso, da eficiência do agendamento e dos padrões de inscrição. Com um painel centralizado, a equipe pode criar agendas, gerenciar recursos e equilibrar a demanda com mais eficiência sem depender de processos manuais. Preveja tendências de inscrição e tome medidas oportunas para otimizar a capacidade do curso e as cargas de trabalho do corpo docente.

* **Monitorar os indicadores-chave de desempenho do sucesso do aluno com o Tableau Next**
  Dê aos consultores acesso às principais métricas sobre os dados acadêmicos, de bem-estar e de engajamento dos alunos. Os consultores podem identificar os alunos em risco mais cedo, personalizar o suporte e acompanhar os resultados da retenção sem contar com suporte de TI ou agregação de dados manual. Meça a eficácia dos programas de consultoria e tome decisões confiantes orientadas por dados.

* **Unificar dados institucionais com atualizações de modelo semântico**
  Mantenha uma visualização confiável dos dados de estudantes, acadêmicos e de progresso em toda a sua instituição. Atualizações coordenadas a modelos semânticos de Educação preparam suas equipes para adotar novas estruturas de dados e definições padronizadas. Estabeleça uma base confiável em toda a instituição para relatórios consistentes, percepções confiáveis e dados prontos para IA. O modelo de dados semântico agora está disponível em um kit de dados e com seu aplicativo Tableau Next.

* **Capture a filantropia do paciente com registros de engajamento pessoal agradável**
  Acompanhe as expressões de gratidão dos pacientes e o suporte filantrópico resultante para cuidados excepcionais recebidos em hospitais universitários e centros médicos. Forneça às equipes de tratamento uma maneira padronizada e em conformidade de encaminhar pacientes agradecidos à equipe de angariamento de recursos. Crie registros de engajamento pessoal agradecidos para registrar a filantropia do paciente e o reconhecimento da equipe de tratamento.

* **Estender dados institucionais para conformidade com a Agência de estatísticas de ensino superior (HESA)**
  Implemente uma estrutura de dados padronizada para dar suporte às necessidades de conformidade no Reino Unido. Ative Conformidade e configuração do Reino Unido para adicionar campos e metadados em conformidade aos objetos do Agentforce Education que estejam alinhados com a especificação HESA Data Futures. Essa base integrada prepara sua instituição para validar envios e executar análises futuras sem contar com mapeamentos de dados manuais ou armazéns de dados externos.

* **Objetos novos e alterados no Agentforce Education**
  Faça mais com os objetos novos e atualizados de Educação.

* **APIs REST do Connect novas e alteradas para Educação**
  Faça mais com as APIs REST do Connect novas e alteradas para Educação.

* **Simplifique o suporte com o novo agente de consulta de ajuda financeira**
  Use o Agente de pesquisa de ajuda financeira para auxiliar estudantes potenciais, solicitantes, estudantes atuais e funcionários com consultas relacionadas a ajuda financeira, incluindo perguntas sobre apólices, processos, status de solicitação e requisitos pendentes. O agente fornece respostas imediatas e precisas a perguntas comuns sobre ajuda financeira, fornecendo informações confiáveis para ajudar os usuários a tomar decisões de ajuda financeira mais rapidamente.

* **Capacitar os alunos com ferramentas de planejamento financeiro de autoatendimento**
  Dê aos seus alunos ferramentas inteligentes de autoatendimento para planejar proativamente suas finanças usando o Student Financials Agent. Reduza o estresse financeiro e as consultas administrativas conforme seus alunos gerenciam pagamentos e visualizam saldos da conta em tempo real.

* **Aprimorar o gerenciamento colaborativo de cursos e o suporte ao aluno no Slack**
  Ajude o corpo docente a gerenciar cursos, interagir com alunos e assistentes de ensino e coordenar o suporte ao aluno no Slack, em que a colaboração já ocorre. Configure o Agente de operações de curso para que os instrutores recebam alertas avançados sobre cargas de curso, colaborem em canais de curso criados automaticamente com telas de currículo e identifiquem alunos em risco. Quando os professores identificam necessidades de suporte, eles podem rapidamente engajar equipes de consultoria e criar canais dedicados para coordenar intervenções oportunas.

* **Agente de recrutamento de estudantes para a Educação Agentforce (disponível ao público em geral)**
  Use o agente de recrutamento de estudantes, agora disponível ao público em geral, para ajudar sua instituição a avaliar e recrutar novos alunos. O agente pode responder perguntas sobre sua instituição, programas e processos de admissões. O agente também pode ajudar os alunos a se inscreverem.

* **Fornecer estimativas de crédito de transferência a estudantes potenciais com Agentforce (disponível ao público em geral)**
  Ajude os alunos potenciais com decisões de solicitação tornando estimativas de crédito de transferência prontamente acessíveis no Agente de crédito de transferência, agora disponível ao público em geral. Estime créditos transferíveis para uma instituição ou programa de aprendizado diretamente em uma sessão do agente para reduzir o tempo de resposta para avaliações. Salve estimativas anteriores para dar aos alunos acesso contínuo.

* **Descubra os cursos certos facilmente com o Agente de pesquisa de curso (disponível ao público em geral)**
  Melhore o autoatendimento do aluno e reduza a carga de trabalho da equipe de consultoria com o Agente de pesquisa de curso, agora disponível ao público em geral. Ajude os alunos a encontrar os cursos mais adequados aos seus interesses, agendas e requisitos do programa de graduação sem fazer compromissos com consultores. Ajude os consultores a pesquisar o catálogo de cursos e orientar os alunos de modo eficaz durante as principais estações de registro.

* **Defina e atinja metas de carreira e vida com o Agentforce: Metas do aluno (disponível ao público em geral)**
  Ajude os alunos a obter recomendações de meta específicas, mensuráveis, alcançáveis, relevantes e com prazo definido (SMART) com orientação habilitada por IA com base em seus perfis, preferências e percepções de avaliação usando o Agente de metas do estudante, que agora está disponível ao público em geral. Ajude os alunos a obter recomendações de recursos do campus, incluindo cursos, programas de suporte e grupos de engajamento que podem manter os alunos no caminho certo para atingir suas metas.

* **Interagir com agentes enquanto você trabalha**
  Colabore e obtenha percepções de seus agentes em uma barra lateral sem sair da página no aplicativo móvel Consumer Goods Cloud em tablets. Execute visitas ao cliente e consulte simultaneamente o histórico de interações do agente para se manter informado.

* **Implementar painéis do Tableau Next com o Salesforce Go**
  Inicie o Tableau Next para Consumer Goods por meio do Salesforce Go para monitorar e promover a Execução do varejo de uma interface centralizada. Essa visualização unificada elimina a navegação pela página de configurações de Execução do varejo, simplificando a configuração e o gerenciamento contínuo.

* **Outros aprimoramentos no Gerenciamento de sincronização**
  Analise e resolva problemas de sincronização mais facilmente com as novas configurações de sincronização padrão. Os KPIs de sincronização agora estão em registros de modo de rastreamento, tornando mais fácil analisar e resolver problemas de sincronização rapidamente.

* **Redefinir seleções e filtros de produto com um único clique**
  Faça a transição facilmente entre o planejamento de produto fixo e dinâmico. Com o botão Limpar tudo, os gerentes de conta-chave podem redefinir todas as seleções de produto e filtrar critérios para uma promoção com um único clique. O botão está ativo durante as fases de planejamento, preparação e modelagem. Você também pode personalizá-lo usando os EARights.

* **Visualizar o impacto da fatura de materiais em P&Ls agregando valores de componente**
  Configure a definição de KPI para agregar valores de componente BOM, como volume ou gasto, diretamente em produtos padrão em um plano de negócios do cliente. Forneça percepções valiosas sobre agregação no nível do plano do cliente para usuários que gerenciam grandes volumes de exibições de BOM. Obtenha rastreamento preciso de P&L, mesmo quando promoções específicas excluem produtos padrão.

* **Objetos alterados no Gerenciamento de promoção comercial**
  Faça mais com os objetos atualizados de Gerenciamento de promoção comercial.

* **APIs alteradas no Gerenciamento de promoção comercial**
  Faça mais com as APIs alteradas na versão 67.0 e posteriores.

* **Gerenciar marcos para novas conexões de utilitário**
  Gerencie novas solicitações de conexão de grade da admissão da solicitação até a ativação com rastreamento de marco automatizado e gerenciamento de conformidade do acordo de nível de serviço.

* **Receber notificações do Slack para sincronização automática de dados de cotação e cotação de vários sites**
  Os representantes de vendas recebem uma notificação do Slack quando a sincronização de dados de cotação ou cotação automática de vários sites é concluída. Essa integração com o Slack mantém os representantes informados sem interromper o trabalho deles.

* **Fornecer autoatendimento e comparação de tarifa assistida**
  Dê aos clientes potenciais a capacidade de comparar as taxas de serviço de utilitários e tomar decisões bem informadas sobre suas compras diretamente em seu portal de clientes. Os clientes atuais podem procurar produtos de energia, comparar ofertas personalizadas e concluir a inscrição online. Durante o processo de inscrição, os clientes podem atualizar o endereço de cobrança. Além disso, o sistema pode capturar novos detalhes de endereço para os clientes estabelecerem automaticamente os registros de local e ponto de serviço necessários.

* **Unificar o ciclo de vida da reunião consultor-cliente com o Concierge da reunião**
  Gerencie o ciclo de vida da reunião entre consultores e clientes, da preparação ao acompanhamento, em uma única interface. O Concierge de reunião elimina a necessidade de consultores financeiros alternarem entre calendários, ferramentas de anotação e sistemas de custódia. Acionados pelo Agentforce, seus consultores recebem resumos de preparação de reunião gerados por IA, reprodução de vídeo com transcrições ao vivo e rascunhos de acompanhamento automatizados após a reunião.

* **Comece mais rapidamente com um modelo predefinido para Gerenciamento de reclamação**
  Proporcione uma experiência de serviço consistente levando o gerenciamento de reclamações diretamente para o Catálogo unificado com um novo modelo predefinido. Capture cada reclamação do cliente por meio do modelo com atributos de dados predefinidos e um formulário de admissão guiada. O registro de reclamação pública criado após o envio de links diretamente para seus produtos, serviços e contas financeiras. A vinculação automática elimina o mapeamento de dados manual para que suas equipes obtenham análises precisas, análise de tendência mais rápida e relatórios de auditoria confiáveis.

* **Automatizar tarefas de investigação de disputa com planos de ação**
  Conclua todas as tarefas e etapas repetíveis em um caso de disputa definindo modelos de plano de ação para registros de disputa e item de disputa. Os usuários podem acionar o plano diretamente de uma página de registro para que eles nunca percam uma tarefa ou verificação necessária. Defina um modelo uma vez e reutilize-o de modo consistente em várias disputas.

* **Mova dados diretamente para conta financeira e objetos relacionados com a licença de usuário de integração do Salesforce**
  Mova dados de sistemas externos diretamente para a Conta financeira e objetos relacionados por meio da API sem atribuir licenças adicionais do Agentforce Financial Services. Os usuários de integração agora têm as permissões padrão Criar, Ler, Atualizar, Excluir, Visualizar todos e Visualizar todos os campos nos objetos padrão de Gerenciamento de conta financeira.

* **Rastrear interações no Calendário do Salesforce para Serviços financeiros**
  Ajude os consultores financeiros a planejar suas agendas e se preparar para engajamentos futuros do cliente visualizando as datas da interação diretamente no Calendário do Salesforce. A visualização centralizada permite que os usuários acompanhem de perto reuniões e acompanhamentos sem alternar entre as solicitações.

* **Objetos novos e alterados de Serviços financeiros**
  Faça mais com objetos novos e atualizados do Agentforce Financial Services, anteriormente o Financial Services Cloud.

* **Automatize emails de serviço de rotina com o Suporte ao cliente do Serviço bancário**
  Transforme a experiência de suporte com resoluções de email instantâneas para consultas de rotina do cliente e menos casos na fila de seus representantes de serviço. O Atendimento ao cliente do Serviço bancário agora interage diretamente com os clientes por meio de conversas de email para esclarecer detalhes e resolver tarefas bancárias, como verificações de transações, consultas de balanceamento, sem intervenção humana.

* **Expanda o autoatendimento bancário com novos subagentes de atendimento ao cliente do Serviço bancário**
  Aprimore a experiência de autoatendimento habilitada por IA e acelere a resolução de solicitações para seus clientes com os novos subagentes para o Suporte ao cliente do Serviço bancário. Os clientes agora podem fazer pedidos independentemente para perguntas bancárias avançadas, como extratos de pagamento de empréstimo, ativações de cartão, admissão de disputa de transação, diretamente das conversas do Agentforce.

* **Resolva consultas bancárias mais rapidamente com os novos subagentes de assistência ao funcionário do Serviço bancário**
  Aumente a produtividade e elimine a navegação em várias telas para seus representantes de serviço com os novos subagentes na Assistência do funcionário de serviço bancário. Os representantes de serviço podem lidar com uma gama mais ampla de consultas bancárias complexas, como adiamentos de pagamento, ativações de cartão, instruções fixas, diretamente das conversas do Agentforce.

* **Estender a assistência de serviço bancário ao canal do Voice**
  Use o Agentforce Voice para fornecer suporte telefônico seguro e inteligente 24 horas por dia, 7 dias por semana, para clientes bancários. O agente habilitado para voz lida com tarefas de rotina usando instruções de linguagem natural e verificação de OTP falada, escalando chamadas financeiras complexas para a equipe ativa de modo conversacional.

* **Comece a usar o Commercial Banking mais rapidamente**
  Reduza o esforço de configuração manual com um pacote pronto para uso de configurações pré-configuradas, metadados e dados de amostra para Commercial Banking. Evite a sobrecarga de configurar recursos individuais separadamente. Instale a Solução de relacionamento com Commercial Banking com um único clique em sua organização de sandbox ou de avaliação. Use os dados de amostra incluídos para explorar recursos ou traga seus próprios dados para validar em relação aos seus requisitos. Demonstre a solução para suas partes interessadas de negócios ou use-a como ponto de partida para suas próprias personalizações.

* **Comece mais rapidamente com o Gerenciamento de disputa de transação**
  Reduza o esforço de configuração manual com um pacote pronto para uso de configurações pré-configuradas, metadados e dados de amostra para Gerenciamento de disputa de transação. Evite a sobrecarga de configurar recursos individuais separadamente. Instale a Solução de gerenciamento de disputa de transação com um único clique em sua organização de sandbox ou de avaliação. Use os dados de amostra incluídos para explorar recursos ou traga seus próprios dados para validar em relação aos seus requisitos. Demonstre a solução para suas partes interessadas de negócios ou use-a como ponto de partida para suas próprias personalizações.

* **Melhorar a precisão da verificação de documentos com IA**
  Reduza o esforço manual e melhore a precisão usando IA generativa para verificar documentos enviados pelo usuário. Identifique discrepâncias entre o conteúdo do documento carregado e os registros do Salesforce, destacando diferenças específicas para revisão imediata. A verificação mais rápida ajuda seus usuários a acelerar fluxos de trabalho de integração e conformidade enquanto mantém altos padrões de dados.

* **Prepare sua organização do Salesforce para Empréstimo digital em poucos cliques**
  A Configuração inicial Empréstimo digital no Salesforce Go simplifica a configuração para novas organizações. Ele ativa automaticamente os recursos básicos Empréstimo digital, como Conheça seu cliente e Discovery Framework. Suas equipes obtêm um ambiente de origem de empréstimo consistente pronto para uso imediatamente.

* **Simplifique a origem da conta de depósito de varejo com o modelo do Discovery Framework**
  Oriente os solicitantes pelas origens da conta de depósito com um modelo do OmniScript predefinido. Capture informações pessoais, de emprego e de origem de fundos enquanto acelera o processo usando os novos recursos de Origem digital.

* **Mostrar métricas de distribuição de resumo em hierarquias flexíveis para Insights de nível executivo**
  Ajude os líderes de negócios a tomar decisões mais rápidas com base em dados durante revisões de negócios ativas fornecendo visibilidade de métricas agregadas diretamente nos nós da hierarquia. Os usuários podem comparar valores de métrica entre nós da hierarquia, de contas individuais a totalizações filho e agregados totais, para descobrir tendências de desempenho e promover a responsabilidade entre equipes.

* **Visualize a rede completa de contas com contatos diretos e indiretos**
  Mostre todos os contatos diretos e indiretos de um nó de conta diretamente da página de hierarquia para ajudar suas equipes de vendas e serviço a identificar quem influencia cada conta. Essa visualização centralizada ajuda as equipes a entender a dinâmica de relacionamento sem navegar em vários registros. Contatos diretos têm um relacionamento principal com uma conta, enquanto contatos indiretos são associados principalmente a outras contas, mas ainda podem influenciar esse relacionamento.

* **Solucionar problemas de validações de hierarquia com Insights no nível do registro**
  Identifique e resolva erros de validação de hierarquia diretamente de registros no nível do registro que mostram quais hierarquias foram processadas e por que falharam, reduzindo o tempo gasto pesquisando registros do sistema. Exporte esses erros para um arquivo CSV para um processo de auditoria eficiente. Um relatório detalhado dos registros de execução de trabalho de validação de hierarquia flexível e de item de execução de trabalho de validação ajuda as equipes a gerenciar recursos do sistema e agendar trabalhos pesados.

* **Explorar hierarquias com visualizações de gráfico e grade aprimoradas**
  Os usuários podem expandir uma hierarquia para tela inteira em visualizações de gráfico e grade para uma perspectiva mais ampla de seus dados. A visualização de grade inclui a funcionalidade de pesquisa com resultados roláveis e destaque de nó, para que os usuários possam encontrar registros específicos em estruturas complexas mais rapidamente. Quando os usuários selecionam um nó no modo de exibição de grade, a página de detalhes do nó é aberta enquanto mantém o contexto da hierarquia visível para que eles possam evitar alternar entre o modo de exibição e a guia do navegador. Para maior visibilidade dos dados, os ícones de advertência identificam nós excluídos e registros que o usuário não tem permissão para acessar.

* **Corpos de resposta da API REST do Connect alterados**
  Use a nova propriedade em Serviços financeiros para rastrear o status de uma solicitação de validação de hierarquia de massa assíncrona.

* **Acelere a configuração do Agentforce Health com o Salesforce Go**
  O Salesforce Go continua a evoluir oferecendo suporte de configuração para Gerenciamento de indicação, Gerenciamento de cuidados integrado e Central de contato. Ao centralizar esses fluxos de trabalho clínicos complexos em um único local de configuração, o Salesforce Go ajuda você a implementar com maior velocidade e precisão. Essa abordagem simplificada facilita a escala de operações, reduz o tempo de configuração até o tratamento e melhora os resultados do paciente.

* **Comparar planos de seguro e gerar cotações com o Seguro de saúde digital**
  Ajude corretores de grupo pequeno e executivos de conta do pagador a avaliar e selecionar os planos de seguro certos e gerar cotações por meio de uma experiência guiada. Compare planos de seguro de saúde lado a lado com percepções sobre prêmios, deduções e custos de fora do bolso e use os resumos gerados por IA para simplificar a tomada de decisão. Use captura de dados padronizada e fluxos de trabalho estruturados para reduzir o esforço manual, melhorar a precisão e entregar recomendações mais rápidas e confiáveis para os empregadores.

* **Rastrear versões e automatizar lógica para planos e modelos de ação**
  Mantenha as trilhas de auditoria e os relatórios históricos usando o campo Número da versão em modelos de plano de ação. Capture o tipo de modelo para acionar a automação a jusante e aplicar a lógica de processamento entre programas de cuidados. O plano de ação captura os valores como um instantâneo estático, mantendo a precisão mesmo que o modelo mude.

* **Veja o consumo da API athenahealth em Digital Wallet**
  Monitore seu uso de direitos e consumo de crédito em tempo real usando a Digital Wallet e aproveite essas percepções orientadas por dados para planejar e expandir suas operações de saúde. O Digital Wallet para Agentforce Health fornece transparência de preços para operações da API athenahealth e ajuda a evitar excedentes inesperados.

* **Recursos novos e alterados da API REST do Connect no Health Cloud**
  As APIs REST do Connect ajudam clientes e parceiros a se integrarem ao software e às UIs do Salesforce.

* **Ações invocáveis novas e alteradas no Agentforce Health**
  Use as novas ações invocáveis no Agentforce Health (anteriormente Health Cloud).

* **Objetos novos e alterados no Agentforce Health**
  Armazene e acesse mais dados com esses objetos novos e alterados do Agentforce Health (antigo Health Cloud).

* **Usar intervalos de página para extrair informações relevantes de documentos**
  Extraia dados com mais precisão de seções específicas de um documento com a IA do documento para saúde. Investigadores de saúde pública e especialistas em admissão de caso agora podem selecionar intervalos de página para processar apenas as informações relevantes. Após a extração, mapeie os valores para os registros existentes para garantir que os dados estejam associados corretamente, reduzindo as correções manuais. Revise os dados extraídos diretamente na página de registro para validar as informações mais rapidamente.

* **Automatizar a extração de documentos de alto volume usando um modelo em lote**
  Processe grandes volumes de documentos com a IA de documento para saúde usando um modelo em lote que contém atributos predefinidos para extração consistente. Padronize a captura de dados em lotes de documentos e reduza o esforço manual. Conecte-se a pastas de conteúdo do Salesforce para importar documentos e dar suporte a processamento escalonável.

* **Configure Agentforce para autorização prévia e status da rede do provedor rapidamente**
  Ajude os representantes da central de contato do contribuinte a serem produtivos desde o primeiro dia usando a configuração guiada aprimorada para configurar o Agentforce para autorização prévia e status da rede de provedores e pesquisa. Revise fluxos e configure subagentes e ações seguindo etapas fáceis de entender. Links diretos para as páginas de configuração no aplicativo e artigos de ajuda abrangentes mantêm você focado e no caminho certo.

* **Revisar dados de autorização prévia mais rapidamente usando ferramentas de cópia zero do Data 360**
  Com as ferramentas do Data 360, os agentes agora podem buscar registros de autorização prévia diretamente de sistemas externos por meio da integração de cópia zero. Em seguida, os agentes podem usar os registros para fornecer aos representantes da central de contato do contribuinte acesso rápido a resumos de alto nível e detalhes de autorização prévia específicos, como status ou motivos de recusa.

* **Usar ações do agente para melhorar as pesquisas na rede do provedor**
  Ajude os representantes da central de contato do contribuinte a encontrar rapidamente os status da rede de provedores e pesquisar provedores na rede. Novas ações do agente se conectam a sistemas externos por meio da Integração do sistema FHIR em tempo real usando o aplicativo de API do cliente FHIR genérico para que os representantes da central de contato do contribuinte possam responder com precisão a perguntas comuns sobre detalhes da rede de provedores.

* **Fornecer cuidados eficazes centrados no paciente com sugestões de avaliação inteligentes**
  Economize tempo e reduza o atrito no processo de entrega de cuidados aproveitando sugestões de avaliação habilitadas por IA com base no perfil de um paciente. Inicie proativamente avaliações relevantes e contextuais sugeridas de maneira inteligente analisando os dados completos dos membros no Agentforce Health (anteriormente Health Cloud), Data 360 e fontes externas sem cópia. As sugestões inteligentes de avaliação reduzem a necessidade de pesquisas manuais e recomendam avaliações que atendem às necessidades específicas de um paciente.

* **Otimizar o engajamento do membro em vários canais com o alcance do paciente e do membro**
  Ajude seus membros a tomar decisões de saúde melhores permitindo que suas equipes de marketing se comuniquem proativamente com eles em vários canais. Melhore a adesão ao plano de cuidados engajando automaticamente os membros com uma ou mais lacunas de cuidados abertas por meio de emails personalizados e lembretes de SMS. Gerencie de modo eficaz campanhas de alcance do membro com o aplicativo Engajamento de saúde.

* **Capacitar membros com o autoatendimento agente**
  Melhore o engajamento e reduza a sobrecarga da central de contato permitindo que os membros concluam tarefas de autoatendimento. Agentforce ajuda os membros a encontrar provedores na rede, verificar seus benefícios de plano de saúde e acessar seu histórico de saúde. Essa experiência agente reduz os custos operacionais enquanto gera melhores resultados de saúde e maior satisfação por meio de um suporte inteligente e personalizado.

* **Automatizar o faturamento para visitas de cuidados domiciliares concluídas**
  Gere automaticamente faturas quando as ordens de trabalho forem concluídas para capturar todos os custos associados, incluindo serviços de saúde, viagens e inventário, e convertê-los em transações faturáveis. Melhore a precisão usando catálogos de preços com dados de custo reais e garanta que cada visita seja faturada para evitar vazamento de receita. Agende essas faturas em frequências definidas ou gere-as sob demanda.

* **Salvar uma avaliação de cuidados domiciliares em andamento para concluir mais tarde**
  Dê suporte à entrega ininterrupta de cuidados permitindo que os clínicos concluam as avaliações na hora certa, em vez de em uma única sessão. Os clínicos agora podem capturar respostas parciais durante visitas, pausar quando necessário e retomar perfeitamente em dispositivos móveis ou desktop sem perder dados. Reduza envios precipitados, incentive informações mais completas e confiáveis do paciente e melhore a confiabilidade do campo independentemente do local.

* **Encontre avaliações com mais eficiência com uma experiência de pesquisa unificada**
  Encontre avaliações da Diretriz de cuidados Milliman (MCG) e avaliações internas baseadas no Discovery Framework em uma única pesquisa usando a Experiência de pesquisa unificada no componente Avaliação Lightning. Os gerentes de cuidados podem encontrar rapidamente avaliações de diferentes origens usando uma barra de pesquisa global e filtros configuráveis. Os resultados da pesquisa são exibidos em uma única lista unificada que mantém a identidade visual para avaliações do MCG para identificação imediata.

* **Melhore os resultados do paciente com acesso histórico para avaliações internas**
  Obtenha uma compreensão melhor da jornada de saúde de um paciente acessando avaliações internas concluídas com base no Discovery Framework, independentemente da versão atual. Abra avaliações concluídas no modo de visualização para renderizar respostas históricas no contexto original. Essa visibilidade ajuda os gerentes de cuidados a acompanhar o progresso do paciente, comparar os resultados clínicos ao longo do tempo e fornecer a documentação necessária para auditorias clínicas.

* **Fornecer cuidados eficazes centrados no paciente com sugestões de avaliação inteligentes**
  Economize tempo e reduza o atrito no processo de entrega de cuidados aproveitando sugestões de avaliação habilitadas por IA com base no perfil de um paciente. Inicie proativamente avaliações relevantes e contextuais sugeridas de maneira inteligente analisando os dados completos dos membros no Agentforce Health (anteriormente Health Cloud), Data 360 e fontes externas sem cópia. As sugestões inteligentes de avaliação reduzem a necessidade de pesquisas manuais e recomendam avaliações que atendem às necessidades específicas de um paciente.

* **Acelerar a configuração de Gerenciamento de encaminhamento e acesso do paciente**
  Aprimore seu ecossistema de encaminhamento e reduza a sobrecarga administrativa usando uma configuração guiada para implementar recursos de Acesso do paciente. Ajude seus coordenadores de admissão a se preparar para triagem de casos rapidamente com a pontuação de prioridade habilitada por IA e o processamento automatizado de documentos. Revise regras de indicação pré-configuradas e estabeleça a extração de dados de origens de fax não estruturadas seguindo as instruções claras e passo a passo. Links diretos para páginas de configuração e artigos de ajuda detalhados o conduzem por todos os estágios da jornada de configuração.

* **Triage indicações com pontuação habilitada por IA e recebimento automatizado**
  Gerencie toda a jornada de indicação em um processo centralizado para reduzir a entrada de dados manual e aumentar o engajamento do paciente. Ajude seus usuários a colocar indicações na fila atribuindo pontuações de inteligência preditiva com base no tempo na fila e na urgência clínica. Além disso, converta encaminhamentos de fax não estruturados em registros estruturados usando a IA de documento para saúde.

* **Acelerar a configuração inicial para seguro**
  Comece a usar a Administração de apólice, o Gerenciamento de reivindicações e a Intermediação de seguro com uma configuração de sandbox de um dia simplificada. Ative as configurações, conclua a configuração necessária e crie definições e dados de negócios para explorar recursos rapidamente e validar as soluções de acordo com seus requisitos de negócios.

* **Aprimorar seus fluxos de trabalho de CI/CD para a versão e implementar dados de seguro**
  Exporte modelos de produto do Insurance e outros dados de referência da sua organização usando um plug-in do Salesforce CLI. Versione os dados exportados e importe-os para outra organização para replicar sua configuração do Insurance sem recriar manualmente os registros.

* **Simplifique a admissão de reivindicações com Agentforce**
  Use o agente Assistência de serviço de declarações para ajudar os representantes de atendimento ao cliente a criar um primeiro aviso de perda (FNOL) quando os clientes relatam uma perda ou incidente. O agente recupera informações sobre a apólice e orienta os representantes pelos detalhes para solicitar o FNOL com base no tipo de apólice. O agente reduz o esforço manual para os representantes e os ajuda a capturar informações de admissão completas e consistentes.

* **Reforce a avaliação da regra de assinatura com o Mecanismo de regras de restrição**
  Defina regras de assinatura complexas usando modelagem baseada em restrições para refletir seu apetite de risco, metas de negócios e requisitos de conformidade. Avalie as regras com o Mecanismo de regras de restrição para melhor desempenho. Com base nos resultados da avaliação da regra, execute fluxos personalizados para automatizar decisões de assinatura ou marcar a cotação para revisão do subscritor.

* **Calcular e adicionar taxas ao preço de produtos de seguro**
  Configure cobranças específicas para produtos de seguro usando uma estrutura de cálculo integrada flexível que agora dá suporte à contagem de impostos e taxas. Defina a ordem exata das operações para calcular tarifas com precisão junto com o prêmio da apólice e os impostos durante a cotação. Revise um detalhamento detalhado dos prêmios, impostos e tarifas para uma cotação e capture os valores cobrados quando você emitir a apólice.

* **Objetos novos e alterados em Seguro**
  Faça mais com os objetos novos e atualizados de Seguro.

* **Novas APIs REST do Connect em Seguro**
  Simplifique o faturamento de seguro calculando valores de apólice divididos proporcionalmente e executando distribuições de dados para apólices específicas para operadoras de seguro.

* **Corpos de solicitação da API REST do Connect alterados**
  Use a nova propriedade em seguro para processar limites de apólice para registros de detalhes de pagamento específicos associados a itens de perda durante o processamento da reivindicação. Especifique detalhes adicionais específicos da empresa ao calcular o valor ajustado para um item de perda da declaração ou recalcular o valor ajustado para um registro de detalhes de pagamento de cobertura da declaração existente. Aprimore o processo de assinatura definindo detalhes específicos da regra na solicitação para direcionar restrições precisas para cláusulas de produto de seguro e controlar como as regras de assinatura são avaliadas. Calcule o faturamento ao emitir, aprovar e renovar apólices de seguro, incluindo o gerenciamento de apólices de várias raízes, quando o Faturamento de carreira estiver habilitado em sua organização.

* **Corpos de resposta da API REST do Connect alterados**
  Use as novas propriedades em seguro para identificar a cobertura pai de qualquer cobertura de apólice relacionada, simplificando o mapeamento da hierarquia de cobertura e rastreando os limites da apólice.

* **Ações invocáveis alteradas no seguro**
  Especifique campos padrão ou personalizados adicionais específicos da empresa ao calcular ou recalcular os valores ajustados para um item de perda de reivindicação.

* **Novos tipos de metadados em seguro**
  Use o novo tipo de metadados para configurar como as regras de consumo de limite de apólice se aplicam a um produto de apólice de seguro, incluindo o modo de consumo e a vinculação do produto.

* **Novo objeto da API do conjunto de ferramentas em Seguro**
  Use a nova API do conjunto de ferramentas para configurar como as regras de consumo de limite de apólice se aplicam a um produto de apólice de seguro, incluindo o modo de consumo e a vinculação do produto.

* **Ofereça benefícios empacotados e flexíveis com estruturas de cobertura de vários níveis**
  Mantenha hierarquias de cobertura aninhadas em todo o ciclo de vida da apólice para dar suporte a ofertas de seguro empacotadas. Preserve relacionamentos de cobertura pai-filho de até quatro níveis em emissão de apólice, aprovações, reintegrações e renovações. Feche a lacuna entre cotação e administração de apólice para garantir que as estruturas de cobertura empacotadas permaneçam consistentes entre as transações de apólice.

* **Renovar apólices em escala com o processamento em massa para apólices únicas e de várias raízes**
  Renove um grande volume de apólices em um único processo em massa que oferece suporte a políticas de raiz única e de várias raízes. Gerencie cargas de renovação de alta eficiência com um fluxo de trabalho comum para diferentes estruturas de apólice. Gere cotações de renovação, faça atualizações de apólice e renove apólices para prazos anuais e personalizados.

* **Processe declarações em coberturas filho com consumo de limite hierárquico**
  Ajuste o pagamento para uma reivindicação em uma cobertura filha com base na moeda e conte os saldos de limite para as coberturas relacionadas na hierarquia. Aplique o máximo de dedutivo, copay, co-seguro e fora do bolso para a cobertura filho. Ao finalizar o pagamento, deduza o pagamento dos saldos de limite em cada nível da hierarquia de cobertura e acompanhe com precisão o consumo.

* **Usar mais dados contextuais em cálculos de limite de apólice e ajuste de reivindicações**
  Passe detalhes contextuais, como tipos de rede e códigos de desconto, para sua lógica de cálculo personalizada para ajustar o valor da reivindicação ou rastrear o consumo do limite da apólice. Antes, você podia enviar apenas o valor reivindicado, o valor ajustado e o limite de contagem para sua lógica de cálculo.

* **Automatizar o faturamento com a integração de ciclo de vida da apólice**
  Conecte eventos de ciclo de vida da apólice, como Emitir, Aprovar, Renovar, Cancelar e Reiniciar, com o faturamento para operadoras de seguro gerarem transações e faturas automaticamente. Reduza a reconciliação manual, melhore a precisão do faturamento, acelere a receita e proporcione uma experiência de faturamento clara para os titulares da apólice.

* **Processar aprovações de alteração de preço para faturamento de marco**
  Processe alterações de preço de aprovação de médio prazo com transações delta geradas automaticamente. Mantenha os planos de marco e as agendas de faturamento precisos enquanto minimiza os ajustes manuais de faturamento.

* **Processar aprovações de alteração de preço para faturamento inicial e baseado em prazo**
  Garanta faturamento preciso e consistente para alterações de precificação de aprovação gerando e aplicando transações de delta com base no modelo de faturamento.

* **Reinstalar apólices canceladas na intermediação de seguro**
  Restaure apólices canceladas diretamente do registro da apólice e retome a cobertura a partir de uma data especificada. A ação Reinstalar cria uma nova versão da política com base no último estado cancelado, ajudando você a recuperar rapidamente as políticas enquanto mantém a continuidade e o histórico de auditoria.

* **Visualizar detalhes da apólice na intermediação de seguro**
  Obtenha uma visualização unificada da estrutura da apólice diretamente no registro da apólice. O componente Apólice de seguro exibe dados da apólice em uma árvore hierárquica, mostrando ativos, coberturas, participantes e prêmios totalizados para entender rapidamente a apólice completa em um só lugar.

* **Aprimore os benefícios do plano com validação de atributo e suporte de tipo de dados**
  Crie benefícios do plano com maior precisão usando regras de atributo impostas e suporte de tipo de dados expandido. Os atributos necessários são validados na interface do usuário e na API, os valores padrão são preenchidos previamente durante a criação e novos tipos de dados, como caixa de seleção, data e data e hora, garantem a captura de dados correta.

* **Lidar com aprovações de alteração de preço com o Billing de marco**
  Processe facilmente alterações de preço de médio prazo gerando transações de delta para aprovações de apólice. Crie planos de marco e agendas de faturamento precisos e reduza a necessidade de ajustes manuais.

* **Gerenciar aprovações de alteração de preço para faturamento inicial e baseado em prazo**
  Gere transações delta, garanta faturamento preciso e consistente entre tratamentos de faturamento. Quando uma política é aprovada com alterações de precificação, o sistema gera transações de delta e as aplica com base no modelo de venda.

* **Configurar o engajamento do cliente de biociências usando uma solução predefinida**
  Comece rapidamente com objetos predefinidos, configurações e dados de amostra. A Solução de engajamento do cliente do Life Sciences do Agentforce ativa as configurações e instala os metadados principais, as configurações do sistema, os FlexiPages, os layouts de página e os registros de negócios necessários para testar a funcionalidade principal do Engajamento do cliente do Life Sciences. Usando dados de amostra, explore recursos para personalidades principais, como usuários de campo, gerentes de conta e ligações de ciência médica. Ou use seus próprios dados comerciais para validar a solução de acordo com seus requisitos específicos.

* **Tornar as solicitações de alteração de dados acessíveis na página de registro**
  Ajude os representantes de campo a economizar tempo permitindo que rastreiem e gerenciem solicitações de alteração de dados diretamente na guia Relacionado da página de registro.

* **Recursos novos e alterados da API REST do Connect no Life Sciences Cloud**
  As APIs REST do Connect ajudam clientes e parceiros a se integrarem ao software e às UIs do Salesforce.

* **Objetos novos e alterados para biociências**
  Faça mais com os objetos novos e alterados de Ciências Biológicas.

* **Tipos de metadados de biociências novos e alterados**
  Aproveite ao máximo os tipos de metadados novos e alterados do Life Sciences Cloud.

* **Transformar dados da conta em Insights prontos para visita**
  Ajude seus usuários a se preparar para visitas agendadas de profissionais de saúde (HCP) e organizações de saúde (HCO) fornecendo a eles percepções de conta inteligentes e personalizadas. Configure o Resumo da conta para agregar os principais dados da conta com visitas agendadas para que o Field Insights possa criar resumos de áudio contextuais selecionados que incluam histórico da visita, tendências de prescrição e pontos importantes de conversa. Os usuários podem acessar essas apresentações como podcasts por meio do leitor de áudio integrado do aplicativo móvel Life Sciences Cloud.

* **Simplifique seu planejamento estratégico para gerenciar melhor as contas-chave**
  Consolide dados diferentes em uma única fonte da verdade para planejamento estratégico com os novos objetos de modelo de dados de Gerenciamento de conta principal. Encontre modelos mais rapidamente com o novo filtro de pesquisa Versão do modelo do plano de ação.

* **Otimizar a seleção de horário para território de folga**
  Simplifique o registro de tempo de inatividade para representantes de campo com um fluxo de trabalho mais simplificado e opções de agendamento predefinidas. Modos de entrada de folga flexíveis, como períodos e entrada manual de data e hora, ajudam os representantes de campo a registrar o tempo mais rapidamente.

* **Realizar visitas remotas com o Microsoft Teams (disponível ao público em geral)**
  Proporcione uma experiência de reunião flexível e segura para representantes de vendas e profissionais de saúde (HCPs) usando o Microsoft Teams como a plataforma de videoconferência para visitas remotas, agora disponível ao público em geral. Gere automaticamente links para reuniões do Microsoft Teams, envie convites por email e mantenha os calendários sincronizados quando os representantes de vendas agendam, atualizam ou cancelam visitas remotas. Para reduzir o atrito e alinhar-se aos requisitos organizacionais, os HCPs podem unir sessões remotas com suas contas do Microsoft Teams existentes. Os representantes de vendas realizam reuniões diretamente no aplicativo Microsoft Teams, enquanto o Engajamento do cliente de biociências gerencia registros de visita e captura métricas de engajamento para o conteúdo compartilhado, melhorando a precisão dos dados e economizando tempo dos usuários.

* **Registrar engajamentos com mais precisão com a Captura de organização de saúde automatizada**
  Capture e associe automaticamente a organização de saúde (HCO) em que a interação de um profissional de saúde (HCP) ocorre para melhorar a integridade dos dados. Quando um representante de campo seleciona um HCP e um endereço de visita, o aplicativo recomenda o HCO correspondente com base na correspondência de endereços de ponto de contato. Para locais com várias organizações afiliadas, os usuários podem selecionar o departamento correto em um menu suspenso filtrado. As visitas filho herdam essas associações para manter a consistência entre engajamentos de grupo.

* **Registrar visitas com registro de visita baseado em voz (piloto)**
  Capture detalhes de engajamento do profissional de saúde (HCP) usando um assistente de voz desenvolvido com IA no aplicativo móvel Life Sciences Cloud. Mesmo sem uma conexão com a Internet, a transcrição no dispositivo e o mapeamento inteligente de entidade podem preencher automaticamente cabeçalhos da visita, mensagens do produto e reações. Melhore a precisão do jargão médico com preparação contextual. Crie e atualize visitas carregando áudio (somente em inglês).

* **Sincronizar dados mais rapidamente com otimizações de sincronização móvel**
  Melhore o desempenho do aplicativo móvel e reduza o uso de dados com um modelo de sincronização mais eficiente. Ative a sincronização periódica em segundo plano durante horários ociosos para que os representantes de campo tenham os dados mais atuais sempre disponíveis para os representantes de campo.

* **Exibir isenções de assinatura com base no país e no idioma de um profissional de saúde**
  Mantenha a conformidade regulatória exibindo dinamicamente os isentos de responsabilidade de assinatura corretos com base nos atributos de um profissional da saúde (HCP), como país e idioma. Os representantes de campo podem apresentar declarações legais específicas do país e adequadas ao idioma durante os desembolsos de amostra, mesmo ao trabalhar entre fronteiras e em regiões multilíngues. Os registros de isenção de responsabilidade são filtrados automaticamente usando atributos account ou account–territory, mantendo a consistência com os fluxos de trabalho Gerenciamento de consentimento e Consulta médica.

* **Adicionar canais de comunicação durante a captura de consentimento**
  Adicione endereços de email, números de telefone ou manipuladores de mídia social diretamente da tela de gerenciamento de consentimento. Agora você pode adicionar novos valores de canal enquanto registra o consentimento, em vez de navegar para guias diferentes.

* **Fornecer aos usuários uma experiência de Insights médicos consistente na Web e em dispositivos móveis**
  Dê aos representantes de vendas acesso mais rápido a percepções contextuais habilitando uma guia de feed Insights médicos no aplicativo da Web Commercial de biociências por meio de uma IU personalizada, trazendo a mesma visualização estruturada para ambas as plataformas. Agrupe percepções relacionadas em uma hierarquia de pai e filho no aplicativo móvel Life Sciences Cloud. Vincule atribuições de meta a um registro de percepção médica pai e use a definição de meta que você criou para preencher as definições de meta.

* **Gerar contas de médico institucionais automaticamente**
  Reduza a entrada manual de dados, poupe tempo e garanta a precisão dos dados gerando contas de Doutor Institucional (no documento) automaticamente. Padronize nomes de conta e mantenha a integridade dos dados com um modelo de nomenclatura personalizado.

* **Obter uma visualização unificada de todas as atividades da conta**
  Os representantes de vendas agora podem ver o histórico de atividades completo de um Doutor Institucional (Ins Docs) relacionado nas páginas de conta Profissional de saúde (HCP) e Organização de saúde (HCO). Listas relacionadas dedicadas nas contas de HCP ou HCO ajudam os representantes de vendas a acessar rapidamente uma conta de Documento interno relacionada, se necessário.

* **Gerenciar percepções, consultas e visitas para contas de médicos institucionais**
  Os representantes de vendas agora podem registrar percepções, rastrear consultas e agendar visitas para uma conta de Doutor Institucional (Ins Docs). Os representantes podem acessar as consultas e percepções de uma conta do Ins Docs na página de conta do Ins Docs. Eles também podem usar o Calendário para agendar visitas.

* **Identificar contas de médicos institucionais com precisão**
  Para evitar classificação incorreta, o Salesforce exclui por padrão os registros de Doutor Institucional (Ins Docs) dos resultados da pesquisa da organização de saúde (HCO). Configure um filtro de pesquisa para ajudar o representante de vendas a localizar com precisão as contas do Ins Document. Para manter a governança de dados, impeça os representantes de vendas de criar manualmente contas do Ins Document ou excluir afiliações ativas.

* **Entregue apresentações interativas no site para desktop**
  As equipes de campo agora podem acessar as mesmas ferramentas de apresentação poderosas no site para desktop que antes estavam disponíveis apenas no aplicativo móvel Life Sciences Cloud. Para se preparar para interações, os usuários de campo podem criar apresentações personalizadas, marcar como favoritos ou revisar apresentações recomendadas para o público na biblioteca de conteúdo. Durante sessões ao vivo, os usuários de campo podem destacar conteúdo com um ponteiro a laser e ferramentas de desenho, capturar classificações de conteúdo e acompanhar o envio de materiais de apresentação por email. Os recursos de conteúdo dinâmico funcionam de modo consistente entre dispositivos, e o rastreamento de engajamento de apresentação permanece sincronizado para que você possa otimizar o conteúdo com cada interação.

* **Mantenha seu contexto de apresentação em foco no Console de serviço**
  O reprodutor de apresentação agora é aberto como uma subguia, em vez de uma janela de página inteira no Console de serviço. Os representantes de vendas obtêm uma visualização uniforme na experiência de Engajamento de visita com menos alternância de página e menos cliques. Eles podem navegar entre materiais de apresentação, detalhes da visita e registros de caso ou contas relacionados sem fechar a janela ativa para proporcionar uma experiência de vendas mais informada e personalizada.

* **Expanda Insights do Data 360 com fluxos de dados de modelo de email**
  Aprimore suas integrações do Data 360 com o novo pacote de Modelo de email pronto para uso no Kit de dados de biociências. Esse pacote fornece mapeamentos predefinidos para estes principais objetos de modelo de dados de biociências: Modelo de email, Fragmento de modelo de email, Fragmento relacionado de modelo de email e Instantâneo de modelo de email.

* **Controlar a criação de tarefa ad hoc no Gerenciamento avançado de terapia**
  Mantenha sequências de terapia e evite desvios não planejados no tratamento do paciente impedindo que os usuários criem tarefas ad hoc durante a progressão da etapa da ordem de trabalho.

* **Gerencie visitas domiciliares de forma eficiente com o Home Health para Agentforce Life Sciences**
  Agende, atribua e gerencie visitas domiciliares usando o Home Health. Visualize os detalhes do paciente junto com a disponibilidade, as habilidades e o território do médico no Console do supervisor ou na página de registro da Conta para atribuir visitas. Transmita visitas não atribuídas a clínicos disponíveis e gerencie agendas de visitas recorrentes e baseadas em necessidade. Os clínicos podem visualizar os detalhes do paciente no Cartão do paciente e os cuidadores podem solicitar alterações às visitas por meio de um portal de autoatendimento.

* **Simplificar a conformidade do engajamento do provedor com modelos**
  Crie modelos de conformidade para economizar tempo e esforço na definição de ciclos sempre que criar um plano de conformidade para uma conta. Em seguida, associe o modelo a todas as contas que precisam de monitoramento. Quando você cria um plano de conformidade para uma conta, o Salesforce gera os ciclos de conformidade personalizados da conta com base no modelo associado e nas datas do plano de conformidade da conta.

* **Acompanhe a conformidade do engajamento do provedor com mais eficiência com atualizações automatizadas**
  Identifique o status do ciclo de conformidade de uma conta, como Pronto, usando indicadores codificados por cores. Os representantes de vendas agora podem criar uma visita para um ciclo com apenas alguns cliques. O Salesforce automaticamente marca um ciclo como concluído quando os representantes de vendas somam a descoberta para a visita associada. Para manter registros de conformidade precisos, os representantes podem fornecer um motivo quando ignoram um ciclo. Com base na configuração do modelo, o Salesforce exclui ou recria ciclos automaticamente quando os representantes de vendas param ou reiniciam uma conformidade.

* **Gerar conversão de pedido mais rápida de amostras**
  Converta solicitações de amostra em pedidos de vendas com um único clique, reduzindo o esforço manual e acelerando o processamento. Mapeie automaticamente detalhes da conta, endereços de envio e quantidades de produto de uma Solicitação de amostra para um novo Pedido de vendas, eliminando etapas intermediárias. Esse processo simplificado permite que as equipes de cumprimento atuem rapidamente e movam os clientes potenciais da amostragem para a entrega confirmada com mais eficiência.

* **Simplificar operações de aquisição para recebimento do distribuidor**
  Gerencie a aquisição do distribuidor por meio de um sistema unificado para criar pedidos de compra e lidar com recibos de mercadorias. Ao gerenciar o fluxo de trabalho de ponta a ponta do pedido até o recebimento em um único sistema, os distribuidores podem atender com precisão à demanda do cliente posterior enquanto mantêm uma única fonte de verdade com o fabricante. Esse processo integrado dá suporte a produtos padrão, serializados e em lote e sincroniza o inventário com base nas quantidades recebidas, garantindo maior precisão e controle operacional.

* **Traduzir dados em percepções com o Datakit de gerenciamento de garantia**
  Transmita dados do Salesforce Core para o Data 360 e mapeie-os para objetos de modelo de dados (DMOs) padrão para criar dados de garantia unificados e padronizados. Essa base de dados consistente e confiável capacita os painéis do Tableau Next, habilitando análises interativas integradas que dão suporte a uma tomada de decisão mais rápida.

* **Simplificar a configuração de manufatura com o Salesforce Go**
  Descubra as funcionalidades de Gerenciamento de distribuidor e os aplicativos Tableau Next no Salesforce Go e aproveite a capacidade de configuração expandida em todos os recursos de Manufatura para uma experiência de configuração única e personalizada. Acesse o conteúdo de ajuda e os recursos de configuração para aprender rapidamente os recursos e concluir a configuração.

* **Padronizar o início da declaração de boa vontade com o modelo de processo de serviço predefinido**
  Apresenta um modelo de processo de serviço pré-configurado para iniciar reivindicações de boa vontade por meio de uma experiência guiada do OmniScript. Dá suporte a solicitações iniciadas pelo revendedor e do call center OEM para captura consistente de solicitação de declaração de goodwill. Reduz o esforço de configuração manual fornecendo um fluxo de interface do usuário e orquestração pronto para ativação.

* **Aumente a eficiência do parceiro com o Gerenciamento de canal aprimorado**
  O Gerenciamento de receita de canal agora usa o Data Cloud para aprimorar o gerenciamento de desconto e acúmulo, melhorando a escalabilidade, a precisão financeira e o desempenho do sistema.

* **Objetos novos e alterados para manufatura**
  Faça mais com os objetos novos e atualizados de Manufatura.

* **Gerenciar declarações de garantia e cobertura**
  Gerencie perfeitamente diversas interações relacionadas a declarações com a garantia conduzida por IA e resumo, validação e rastreamento de declarações de goodwill. Ao usar o agente Assistência de declarações de garantia, os representantes de serviço em fabricantes de equipamento original e revendedores podem rapidamente lidar com consultas de declarações e validar a cobertura de garantia de produtos e peças, aprimorando a experiência do usuário e a satisfação do cliente.

* **Simplificar operações de vendas do revendedor**
  Aumente a produtividade de vendas do revendedor usando a assistência de IA para coordenar de modo rápido e eficaz várias tarefas de vendas. O Concierge de vendas para parceiros do setor permite que os representantes de vendas do revendedor pesquisem ativos, peças e acessórios, criem oportunidades, gerem cotações, capturem solicitações de avaliação de troca e enviem emails aos clientes com informações relevantes.

* **Rastrear contas-chave e o desempenho do acordo de vendas**
  Obtenha o aplicativo Insights de manufatura para avaliar a integridade geral dos negócios, analisar o desempenho da conta e medir a realização da receita. Use os painéis Início do gerente de contas principal, Desempenho do acordo da conta e Visão geral dos acordos de vendas para comparar metas planejadas com os resultados reais. Identifique lacunas de receita, acompanhe a integridade do acordo e detecte oportunidades de espaço em branco em portfólios de conta. Painéis integrados permitem a detecção mais rápida de problemas de desempenho e dão suporte a ações corretivas oportunas.

* **Analisar seus fluxos de receita de serviço**
  Obtenha visibilidade abrangente de seus fluxos de receita de serviço usando o aplicativo Service Revenue Analytics. Use o painel Service Revenue Analytics para avaliar a combinação de receita recorrente e não recorrente, identificar os principais fatores de receita e rastrear oportunidades de crescimento entre clientes e ativos. Conecte operações de serviço a resultados financeiros para promover um crescimento de receita mais previsível e diversificado.

* **Crie propostas de mídia mais rapidamente com o Agente de proposta de anúncio**
  Acelere a jornada de vendas da pesquisa para uma apresentação finalizada em um único fluxo de trabalho com um agente de IA. Seus executivos de conta podem usar o agente para resumir oportunidades, encontrar produtos correspondentes e gerar propostas de mídia. Além disso, o agente cria apresentações diretamente de modelos de biblioteca.

* **Simplificar a configuração de publicidade e gerenciamento de assinantes**
  Descubra e configure seus novos recursos de mídia e assinante mais rapidamente com o Salesforce Go. Poupe tempo configurando seus agentes de IA para propostas de anúncio de um só local em Configuração. Além disso, descubra novos recursos para planejamento de mídia linear e gerenciamento de ciclo de vida do assinante diretamente nesse espaço.

* **Melhore a eficiência do planejamento de mídia com ações em massa no Gerenciamento de vendas de publicidade**
  Otimize seus fluxos de trabalho de campanha com os novos recursos de atualização em massa na grade de planejamento de mídia. Os planejadores de mídia agora podem selecionar e atualizar vários itens de linha simultaneamente. Ao eliminar configurações tediosas linha a linha, esse recurso reduz o esforço manual, permitindo que seus representantes de vendas finalizem planos de mídia de forma rápida e com maior precisão.

* **Migrar dados de direcionamento de anúncio com modelos do Mecanismo de processamento de dados (beta)**
  Elimine o carregamento de dados manual e scripts personalizados frágeis ao lidar com migrações de dados para direcionamento de anúncio. Use os modelos integrados do Mecanismo de processamento de dados para exportar e importar configurações de direcionamento de anúncio entre ambientes.

* **Manter atualizações de item de linha entre guias**
  Preserve suas alterações de configuração de item de linha automaticamente ao alternar entre guias. Um salvamento automático é acionado sempre que você sai de uma guia com atualizações não salvas. Suas alterações são salvas em todas as guias automaticamente.

* **Verificar o inventário entre vários servidores de anúncio**
  Consulte vários servidores de anúncio ao mesmo tempo para obter uma visualização abrangente do inventário disponível. Ao rotear solicitações por meio de um serviço de orquestração, seus usuários recebem dados de inventário precisos em todas as plataformas integradas. Essa atualização habilita credenciais nomeadas separadas para a API de disponibilidade por registro de servidor de anúncio.

* **Depurar falhas com novos logs de erro detalhados**
  Identifique a causa-raiz de falhas em trabalhos assíncronos e resolva problemas rapidamente usando novos registros de objeto de erro. Quando operações como Verificar disponibilidade, Aplicar modelo de plano de mídia, Emendar plano de mídia e Copiar plano de mídia falham, o sistema agora gera logs de erro e aviso detalhados. Revise esses registros para detectar links do servidor de anúncio ausentes, problemas de acesso em nível de campo (FLS) e exceções genéricas instantaneamente.

* **Personalizar a lógica de precificação de mídia usando planos de procedimento**
  Defina etapas de execução para seus produtos de mídia usando ganchos do Apex e regras condicionais. Esses planos se integram aos procedimentos de precificação existentes para dar a você controle preciso sobre a lógica de cálculo complexa. Essa estrutura dedicada ajuda você a automatizar sequências de precificação complexas sem substituir a lógica existente.

* **Objetos novos e alterados no Agentforce Media**
  Faça mais com os objetos novos e atualizados do Agentforce Media.

* **APIs REST do Connect novas e alteradas no Agentforce Media**
  Saiba mais sobre os novos recursos disponíveis com Agentforce Media.

* **Novas ações invocáveis no Agentforce Media**
  Faça mais com as novas ações invocáveis no Agentforce Media.

* **Agende locais de anúncios de TV e rádio com o calendário de pontos**
  Use o calendário spot para distribuir anúncios de TV e rádio em períodos diários, semanais ou de transmissão. Seus representantes de vendas podem substituir manualmente as distribuições para equilibrar os pontos no voo da campanha. Os representantes de vendas podem exportar distribuições atuais para compartilhamento com parceiros externos ou para análise offline. Essa ferramenta inclui validações integradas para evitar erros de agendamento e manter contagens de pontos precisas em todo o plano de mídia.

* **Criar planos de mídia mesclados com classificações de demonstração**
  Ajude seus planejadores de mídia a projetar campanhas de televisão e rádio usando dados de classificação projetados armazenados diretamente em itens de linha de cotação. Configure cálculos personalizados para mostrar aos clientes como o inventário do anúncio atende aos objetivos do público para alcance, Pontos de classificação bruta e métricas personalizadas. Essa adição simplifica o processo de planejamento centralizando os dados do público que os usuários gerenciavam anteriormente em planilhas externas.

* **Gerenciar a precificação para posicionamentos de mídia linear com cartões de frequência**
  Use cartões de frequência centralizados para definir preços e métricas de base em canais de televisão, canais de rádio e estações. Personalize os cartões de taxa base usando atributos de mídia lineares, como comprimento do ponto, posição do intervalo do anúncio e dia da semana. Os administradores de precificação também podem definir critérios personalizados para ajustar a precificação de acordo com suas estratégias de publicidade.

* **Feche negócios mais rapidamente com cupons e promoções configuráveis**
  Dê aos seus representantes de vendas a flexibilidade de aplicar promoções personalizadas e cupons manuais diretamente no configurador ou no Editor de linha de transação de vendas. Você pode definir facilmente a elegibilidade e a duração para garantir que as melhores ofertas alcancem os clientes certos. Aplique promoções diretamente a cotações, pedidos, emendas e renovações. As promoções aplicadas a uma cotação são transferidas automaticamente durante a geração do pedido.

* **Capture a participação no mercado de assinatura com recursos de vendas B2C**
  Capitalize o crescente mercado de assinaturas usando uma jornada de vendas baseada em carrinho projetada para usuários residenciais e de pequena empresa. Aumente sua receita oferecendo promoções configuráveis. A experiência de carrinho para ativo de primeira API fornece uma interface digital em que os compradores anônimos podem facilmente localizar, configurar e comprar produtos. Simplesmente atribua o conjunto de permissões Usuário de vendas do consumidor para conceder a seus representantes de vendas acesso preciso às APIs e objetos REST do Connect necessários.

* **Simplificar a cotação e a ordenação baseadas em assinante**
  Alinhe-se aos requisitos de negócios do assinante habilitando as configurações de cotação e pedido baseadas em assinante. Aumente a eficiência do representante de vendas automatizando a entrada de dados do assinante, aplicando ofertas a grupos de assinantes e gerando vários pedidos de uma única cotação. Simplifique seus fluxos de trabalho de cotação e pedido permitindo que os representantes de vendas adicionem dados do assinante por meio de uploads de arquivo CSV automatizados ou entrada manual rapidamente. Atribua produtos a todas as seleções de assinante simultaneamente na página do catálogo de produtos. Aumente o desempenho aplicando ofertas a grupos de assinantes em uma única representação. Esse recurso elimina a exigência de clonar ofertas para cada assinante individual. Aumente a eficiência automatizando a criação de vários pedidos a partir de uma única cotação. Use critérios específicos, como assinantes, campos ou grupos, para garantir que cada transação seja precisa e personalizada para seu negócio.

* **Aplicar promoções ao carrinho em vendas do consumidor para impulsionar as vendas**
  Aumente as vendas integrando o Gerenciamento de promoções globais (GPM) ao pacote de API de vendas do consumidor. Configure facilmente os detalhes da promoção, incluindo tipo, duração e elegibilidade, e adicione cupons para promoções manuais. Esse aprimoramento fornece detalhes consistentes de promoção e desconto do carrinho até o pedido e o ativo finalizados durante a ativação. Sua equipe de vendas tem a flexibilidade de fechar todos os negócios com a melhor oferta.

* **Gerenciar cotações e pedidos com o editor de linha aprimorado**
  Melhore a visibilidade com o layout de grade única simplificado e a interface de planilha limpa no Editor de linha de transação de vendas. Os representantes de vendas podem filtrar e classificar linhas de cotação e pedido e usar um painel lateral para visualizar detalhes e aplicar promoções. Se você tiver implementado a configuração para o editor de linha antes da versão Summer '26, recomendamos usar o Editor de linha de transação de vendas na página de registro de pedido e cotação.

* **Gere registros de uso de energia estimados gerenciando de modo inteligente lacunas de dados**
  Reduza o esforço manual usando regras de preenchimento de lacuna de dados automatizadas para criar registros de uso de energia para ativos fixos. Defina critérios de ativo específicos e selecione métodos de lógica de preenchimento predefinidos para gerar dados estimados com antecedência. Adicione recursos de estimativa proativos a atividades existentes de preenchimento de lacunas para manter a completude dos dados. Priorize os dados de uso reais em relação a espaços reservados para que seus relatórios finais sejam baseados nos fatos mais confiáveis.

* **Melhorar a precisão dos cálculos de emissões baseadas em mercado**
  Ajuste sua contabilidade de carbono para se alinhar melhor às interpretações e diretrizes do protocolo de gases do efeito estufa (GEE) para relatórios de sustentabilidade substituindo o mapeamento de dados manual pela ingestão automatizada. Para cumprir melhor os padrões globais, aplique mecanismos de mercado, como certificados de energia renovável, apenas em relação ao valor total de CO2e sem alterar cálculos de gás de componente específicos. Essa abordagem substitui o método anterior de derivar o local do escopo 2 e as emissões baseadas em mercado de gases de componentes individuais, como CO2, CH4 e N2O. Para atualizar as emissões que foram calculadas com o método anterior, clique em Recalcular em seus registros de pegada.

* **Simplificar a descoberta e a configuração de recursos**
  Com o Salesforce Go, você pode descobrir, configurar e configurar recursos do Hub de divulgação e conformidade e descobrir recursos adicionais do Net Zero em um único local em Configuração. Saiba mais sobre recursos e obtenha ajuda com configuração acessando links e recursos de conteúdo.

* **Objetos novos e alterados no Net Zero**
  Faça mais com os objetos novos e alterados do Net Zero.

* **Simplificar a descoberta e a configuração de recursos**
  Descubra, configure e configure recursos de Captação de recursos, Gerenciamento de programa e Gerenciamento de caso em um único local em Configuração. Use o Salesforce Go para rastrear todo o uso de recursos desse hub centralizado. Você também pode aprender mais sobre recursos específicos e obter ajuda com a configuração. Basta acessar os recursos e links de conteúdo fornecidos para começar.

* **Recurso atualizado para o pacote gerenciado de Gerenciamento de concessões**
  Verifique o status de imposto sem fins lucrativos com uma integração de API modernizada. O glossário de pesquisa de status de imposto do Gerenciamento de concessões agora protege a estabilidade de suas ferramentas de due diligence usando o modelo de API direto ao provedor mais recente. Esse novo sistema fornece uma maneira mais eficiente de obter dados de conformidade essenciais. Seus usuários mantêm a mesma experiência familiar enquanto se beneficiam de uma arquitetura técnica mais segura e sustentável.

* **API REST do Connect para Nonproft alterada**
  Saiba mais sobre a API de conexão alterada disponível em Nonprofit.

* **Simplificar a descoberta e a configuração de recursos para o setor público**
  Forneça agentes baseados em papel que automatizam processos para funcionários do setor público e fornecem serviço consistente aos clientes em canais digitais. O Salesforce Go oferece suporte adicional para o Agentforce Public Sector, anteriormente Soluções do setor público. Em um único local de configuração, crie e implemente agentes para dar suporte ao Gerenciamento de conformidade, Licenciamento e permissão e Gerenciamento de recrutamento de talentos.

* **Coletar tarifas para serviços do setor público com pagamentos de entrada**
  Ajude os clientes a pagar por serviços, como solicitações de licença e permissão, diretamente em seu portal voltado para o público. Ao usar Pagamentos de entrada, você pode integrar um fluxo de checkout seguro ao seu site do Experience Cloud. Essa integração ajuda os clientes a liquidar tarifas digitalmente e dá aos funcionários da agência visibilidade em tempo real do status de pagamento, reduzindo a reconciliação manual e garantindo a conformidade antes da aprovação da solicitação.

* **Acompanhe pagamentos do setor público de saída e desembolsos financeiros**
  Centralize o rastreamento de transações financeiras para programas de benefícios, Seguro social e gestão de provedores. Use o modelo de dados Pagamentos de saída e a ação invocável Gerar instruções de pagamento para gerar instruções de pagamento para sistemas financeiros externos. O rastreamento preciso de pagamentos ajuda a sua agência a manter uma trilha de auditoria detalhada e a melhorar a transparência dos pagamentos aprovados no Setor Público Agentforce.

* **Melhore a entrega de serviço com um perfil do público unificado para gerenciamento de benefício**
  Ajude os trabalhadores do caso a tomar decisões mais rápidas e mais bem informadas consolidando os dados de benefícios do público em uma visualização. O Perfil unificado de clientes apresenta resumos gerados pelo Einstein, percepções do Data 360 e alertas de prioridade para casos abertos para ajudar sua equipe a identificar problemas urgentes e fornecer os serviços certos no momento certo.

* **Obtenha percepções mais rapidamente com painéis do Tableau Next**
  Monitore as operações de licenciamento, permissão e inspeção da sua agência com painéis do Tableau Next predefinidos habilitados pela análise orientada por IA. Acesse os painéis Resumo executivo, Insights da conta, Resumo do departamento e Insights de conformidade para ajudar sua agência a tomar decisões orientadas por dados mais rapidamente com o desempenho nativo e os recursos de análise avançados do Tableau.

* **Acelere o contratação do setor público com a colaboração de recrutamento no Slack**
  A colaboração baseada no Slack integra registros específicos do Salesforce ao Slack para que os usuários possam visualizar e editar esses registros sem sair do Slack. Predefinimos três fluxos que criam automaticamente um canal do Slack e adicionam partes interessadas importantes ao canal do Slack quando um registro de solicitação de recrutamento é criado. Os fluxos podem ser personalizados para uso com outros objetos de Gerenciamento de recrutamento de talentos, como registros de formulário de solicitação.

* **Permitir que funcionários internos solicitem trabalhos por meio de portais de autoatendimento**
  Ajude as agências do setor público a gerenciar o recrutamento interno fornecendo aos funcionários um portal de autoatendimento para pesquisar posições abertas e enviar solicitações. O Portal do funcionário inclui pesquisa de trabalho com filtros para local, grau e profissão e envio de solicitação online com upload de documento usando a Estrutura de formulário com seções de solicitação.

* **Simplifique os serviços do funcionário com agentes habilitados por IA**
  Ajude os funcionários do setor público a resolver reclamações, encontrar candidatos qualificados e acessar informações de licenciamento por meio de agentes desenvolvidos com IA adaptados de Soluções do setor público. Esses agentes Agentforce ajudam a equipe de RH e gerentes de contratação com fluxos de trabalho de resolução de reclamações, aquisição de candidatos baseada em habilidades e orientação de políticas de licenças e permissões. Os funcionários podem interagir com agentes no Portal da experiência do funcionário para um autoatendimento mais rápido e processos de RH simplificados.

* **Aprimorar o autoatendimento do funcionário com agentes de serviço de RH e TI**
  Ajude funcionários do setor público a acessar serviços de RH por meio de agentes habilitados por IA adaptados do Serviços do funcionário para trabalhar com usuários da plataforma (titulares de licença de usuário da Plataforma do Lightning - One App). Esses agentes ajudam os funcionários com o gerenciamento de depósitos diretos, solicitações de licença, envios de despesas, atualizações de perfil e programas de capacitação. Todos os recursos do Serviço de RH, incluindo agentes e recursos de suporte, agora estão disponíveis para usuários da plataforma para dar suporte a casos de uso de experiência do funcionário do PSS. Os funcionários podem interagir com agentes no Portal da experiência do funcionário, no Slack ou no Microsoft Teams para um autoatendimento mais rápido.

* **Aproveite o serviço de TI da Agentforce para o setor público**
  Conclua a conformidade e reduza o risco padronizando como você fornece serviços de suporte de TI em todos os canais. Use a IA e a automação de processos para otimizar operações de TI, reduzir custos e melhorar a eficiência dos serviços públicos para cada agência do governo.

* **Preencher previamente formulários de solicitação com a IA de documento do Data Cloud**
  Reduza a entrada de dados manual para candidatos a emprego extraindo automaticamente informações de currículos carregados e preenchendo previamente os formulários de solicitação. A IA de documento do Data Cloud usa grandes modelos de linguagem (LLMs) para capturar dados estruturados de documentos não estruturados, como currículos, fragmento de pagamento, declarações de impostos e relatórios de laboratório, ajudando os solicitantes a preencher formulários mais rapidamente e com menos erros.

* **Leve facilmente os dados do setor público do Agentforce para o Data 360**
  Ficou mais fácil usar fluxos de dados pré-configurados para trazer dados do Setor público do Agentforce para o Data 360. Em vez de instalar um kit de dados para instalar fluxos de dados, agora você pode configurar fluxos de dados em Configuração. Simplifique e acelere sua implementação com fluxos de dados que incluem mapeamentos prontos para objetos de modelo de dados. Transmita dados apenas para as soluções necessárias, como Licenciamento e permissão, Gerenciamento de programa social e Gerenciamento de recrutamento de talentos. Em seguida, combine esses dados com fontes externas para criar uma visão unificada dos clientes, obter novas percepções e fundamentar suas ações do Agentforce.

* **Objetos novos e alterados no setor público Agentforce**
  Faça mais com os objetos novos e alterados do Agentforce Public Sector, antigamente Soluções do setor público.

* **Ações invocáveis novas e alteradas no setor público Agentforce**
  Use a nova ação invocável no Agentforce Public Sector.

* **OmniStudio para Indústrias**
  Muitos produtos de Indústrias incluem acesso a recursos do OmniStudio. Use esses recursos para estender e personalizar seu produto com base nas necessidades de seus negócios.

* **Processe atualizações de registro em escala com upload de CSV**
  Lide com atualizações de registro em grande escala carregando um arquivo CSV de identificadores exclusivos diretamente para um trabalho em lote. Ignore os limites tradicionais de consulta de banco de dados usando o processamento assíncrono para lidar com até 50.000 registros por upload sem lógica de filtro complexa.

* **Refinar a seleção de registro com o suporte aprimorado ao operador IN**
  Processe registros específicos diretamente de fluxos de trabalho de negócios passando uma coleção de IDs de registro para um trabalho em lote. Substitua variáveis de texto simples por variáveis de coleção dinâmica usando o operador IN para aumentar a precisão de filtragem e direcionar apenas os registros selecionados para o fluxo de trabalho de negócios. Passe uma lista de até 200 registros selecionados diretamente para uma execução de trabalho em lote para fazer atualizações de dados precisas e reduzir o risco de alterações indesejadas.

* **Conceder aos usuários comerciais acesso ao Gerenciamento em lote**
  Forneça aos usuários de negócios a capacidade de executar e monitorar suas próprias tarefas de alto volume. Remova a restrição anterior que limitava o Gerenciamento em lote a administradores do sistema para descentralizar operações diárias. Permita que usuários de negócios descubram e executem trabalhos em lote de forma independente enquanto mantêm a segurança administrativa.

* **Objetos do conjunto de ferramentas da API alterados para Gerenciamento em lote**
  Saiba mais sobre os tipos de metadados alterados no Gerenciamento em lote.

* **Objetos alterados para Monitorar serviço de fluxo de trabalho**
  Faça mais com os objetos atualizados Monitorar serviços de fluxo de trabalho.

* **Editar várias tarefas de uma só vez para os planos de ação e modelos de plano de ação**
  Evite editar cada campo de tarefa individualmente. Edite os valores da tarefa no modo de exibição de lista de tarefas em planos de ação e modelos de plano de ação.

* **Aprimorar o controle e a conformidade com o controle de versão da tabela de decisão**
  Mantenha o controle total sobre suas regras de negócios e simplifique a conformidade com controle de versão para tabelas de decisão baseadas em CSV. Crie novas versões para testar alterações com segurança sem afetar regras ativas. Para uma implantação simplificada, ative versões específicas com uma classificação personalizada para gerenciar conflitos quando várias versões estiverem ativas.

* **Escalabilidade aprimorada no Mecanismo de regras de negócios**
  Obtenha escalabilidade aprimorada com limites aprimorados em tabelas de decisão baseadas em CSV.

* **Melhor transparência em explicações de decisão**
  O Decision Explainer agora rastreia todas as execuções do Mecanismo de regras de negócios em relação a um registro de serviço de contexto. Visualize explicações aprimoradas rastreando a execução específica do Mecanismo de regras de negócios para cada decisão.

* **Melhore a agilidade com variáveis de lista locais em conjuntos de expressões**
  Crie variáveis de lista locais diretamente no criador de Conjunto de expressões para armazenar valores provisórios para o cálculo, de uma definição de contexto, em vez de modificar a definição de contexto. Variáveis de lista locais são recursos hierárquicos, enquanto variáveis e constantes são recursos simples. Essas variáveis têm o escopo definido para uma versão específica do conjunto de expressões e existem apenas durante a execução, mantendo suas definições de contexto globais limpas.

* **Migrar o mecanismo de regras de negócios com 2GP**
  Os componentes do Mecanismo de regras de negócios agora podem ser empacotados nos pacotes gerenciados de segunda geração (2GP).

* **Novos objetos no Mecanismo de regras de negócios**
  Faça mais com esse novo objeto Mecanismo de regras de negócios.

* **Ações invocáveis alteradas no Mecanismo de regras de negócios**
  Faça mais com essa ação invocável do Mecanismo de regras de negócios alterada.

* **Gerar classes do Apex para definições de contexto**
  Crie classes do Apex usando definições de contexto para espelhar os metadados e a hierarquia da definição no Salesforce Flow sem codificação.

* **Aumente a escalabilidade do tempo de design com limites maiores de definição de contexto**
  Crie e gerencie estruturas de dados mais complexas com maiores limites de tempo de design para definições de contexto. Agora você pode incluir até 80 nós por definição e até 1.600 atributos por definição. Além disso, o limite de atributos por nó agora é de 600 e você pode criar até cinco níveis de hierarquia em uma estrutura de definição de contexto.

* **Transforme dados de contexto em escala com o Mecanismo de processamento de dados**
  Aprimore seus processos de negócios, como a geração de documentos, usando o poder do Mecanismo de processamento de dados (DPE) para transformar dados de contexto. Use DPE para ler dados diretamente de objetos de contexto, aplicar lógica complexa, como totalizações ou agrupamentos hierárquicos, e gravar os resultados de volta em uma estrutura JSON.

* **Adicionar várias condições de ordem de classificação em filtros de contexto**
  Você pode adicionar duas condições de ordem de classificação no filtro de contexto.

* **Objetos de serviço de contexto novos e alterados**
  Faça mais com esses objetos novos e alterados do Serviço de contexto.

* **Novas ações invocáveis para serviço de contexto**
  Faça mais com essas ações invocáveis novas e alteradas para o Serviço de contexto.

* **APIs de serviço de contexto novas e alteradas**
  Faça mais com essas APIs alteradas para o Serviço de contexto.

* **Transformar dados de contexto e gravar dados em JSON com o Mecanismo de processamento de dados**
  Use o Mecanismo de processamento de dados (DPE) para ler dados de definições de contexto e gravá-los no JSON para dar suporte a transformações de dados de alto volume para processos como geração de documento. Use DPE no lugar de plug-ins do Apex para dimensionar transformações para hierarquias e agrupamentos de produtos complexos sem atingir limites de regulador.

* **Solucionar problemas de definições do Mecanismo de processamento de dados com o modo de depuração**
  Detecte e resolva problemas em definições do Mecanismo de processamento de dados (DPE) mais rapidamente depurando-os diretamente no criador de DPE para o tempo de execução do CRM Analytics. Em vez de aguardar execuções completas de writeback ou criar nós temporários, reduza o tempo de solução de problemas inspecionando conjuntos de dados filtrados e estágios de transformação intermediários antes do writeback final.

* **Validar lógica e depurar definições de tempo de execução do Data 360 mais rapidamente com a visualização de dados**
  Valide as definições durante a fase de design visualizando as transformações de dados no nível do nó. Confirme se as configurações atendem às necessidades de negócios e identifique erros de lógica com antecedência. A visualização de dados está disponível para definições do Data 360 e do CRM Analytics. Depure configurações em um ambiente controlado antes de salvar ou executar definições.

* **Agregue dados de modo eficiente entre registros relacionados com agregação hierárquica**
  Implante valores entre hierarquias de pai e filho de vários níveis, como de contas filho a uma conta pai, para definições com o tempo de execução do CRM Analytics. Agregue dados, como total de ativos ou receita, de registros filho em qualquer nível de uma hierarquia para o registro pai.

* **Criar conjuntos de dados direcionados com junções de pesquisa de valor único e de vários valores**
  Crie um conjunto de dados exclusivo unindo uma origem de dados primária e secundária com o tipo de junção Pesquisa. Preserve todos os registros da origem primária e adicione dados correspondentes da origem secundária com base em um critério comum. Por exemplo, combine registros de oportunidade (principal) com os detalhes da conta correspondentes (secundário) usando um ID da conta. Se a origem secundária tiver várias correspondências, inclua dados apenas do primeiro registro correspondente ou de todos os registros correspondentes no conjunto de dados resultante para nós downstream. Não há suporte para pesquisas de múltiplos valores para definições de tempo de execução do Data 360.

* **Selecionar tipos de operação de write-back para objetos do Data 360**
  Escolha o tipo de operação de write-back que atende às necessidades de processamento de dados para objetos de modelo de dados (DMOs) e objetos de data lake (DLOs). Selecione Inserir, Inserir e atualizar ou Sobrescrever como o tipo de operação de write-back para o destino no nó Objeto de write-back. Essas opções atendem a mais requisitos de negócios, como anexar novos dados de engajamento ou atualizar registros de perfil existentes sem substituir todo o conjunto de dados.

* **Atribuir categorias de objeto de modelo de dados para compatibilidade com o Data 360**
  Categorize objetos de modelo de dados (DMOs) durante o write-back para garantir que funcionem perfeitamente com recursos do Data 360 downstream. O Mecanismo de processamento de dados (DPE) atribuiu anteriormente a categoria Outro a todos os DMOs que criou. Agora, selecione a categoria que corresponde à finalidade do objeto, como Perfil para detalhes do cliente ou Engajamento para interações. A categorização precisa é essencial para funcionalidades do Data 360, como resolução de identidade e segmentação.

* **Apresentar formulários multilíngues com tradução de dados de entidade**
  Armazene perguntas e respostas de avaliação em vários idiomas para mostrar automaticamente os formulários na localidade do usuário. Essa estrutura simplifica o gerenciamento de formulários multilíngues usando a estrutura de Tradução de dados de entidade (EDT) para versões de pergunta enquanto mantém rótulos personalizados para elementos de IU estáticos.

* **Melhore a experiência de doador com um agente de suporte a doadores por autoatendimento**
  Dê aos seus doadores o poder de gerenciar seus próprios presentes recorrentes em um site do Experience Cloud. O Agente de suporte de doador ajuda os doadores a lidar com solicitações comuns, como alterar o valor e a frequência de um presente recorrente. Recupere o tempo da sua equipe para se concentrar em criar relacionamentos enquanto fornece aos doadores a experiência rápida e moderna que eles esperam.

* **Simplifique as migrações de dados gerenciando validações de presentes**
  Obtenha mais controle sobre seus dados de Captação de recursos pausando validações de presente durante importações iniciais e carregamentos de delta. Para evitar erros de migração e reduzir o retrabalho manual, desative algumas validações para transações de presente, compromisso e agendas. Pause validações de presente em Configurações de Captação de recursos ou com a API de processo de negócios. Depois de concluir sua migração, habilite facilmente novamente essas regras para preservar a integridade de dados contínua enquanto faz referência a uma nova lista abrangente de todos os requisitos de validação de presente.

* **Processe compromissos de presente recorrentes ao mesmo tempo**
  Para continuar a dar suporte ao gerenciamento de doadores, o processamento em lote de compromisso do NextGen automatiza a lógica e lida com as transições de ciclo de vida. Por exemplo, o processamento do NextGen fecha automaticamente compromissos concluídos ou alerta a equipe sobre parcelas perdidas, sem os gargalos do processamento sequencial legado.

* **Capture a filantropia do paciente com registros de engajamento pessoal agradável**
  Acompanhe as expressões de gratidão dos pacientes e o suporte filantrópico resultante para cuidados excepcionais recebidos em hospitais universitários e centros médicos. Forneça às equipes de tratamento uma maneira padronizada e em conformidade de encaminhar pacientes agradecidos à equipe de angariamento de recursos. Crie registros de engajamento pessoal agradecidos para registrar a filantropia do paciente e o reconhecimento da equipe de tratamento.

* **Objetos e campos alterados para Captação de recursos**
  Faça mais com os objetos atualizados de Captação de recursos.

* **Gerenciar a migração da API de carrinho padrão com controle de modo misto**
  Proporcione uma experiência de usuário aprimorada alternando entre os modos Padrão e Classic durante operações de navegação de API de alto desempenho. Essa atualização se aplica às APIs Obter itens do carrinho, Obter itens do carrinho por IDs e Obter produtos do carrinho. Essa implementação reduz os riscos de migração e permite uma abordagem em fases para melhorar o desempenho do sistema. Além disso, esse controle granular mantém o modo Classic para processos de checkout personalizados.

* **Refinar a descoberta de produto com as interfaces de disponibilidade e elegibilidade**
  Proporcione uma experiência de navegação sem esforço aos usuários e representantes de vendas. Simplifique o processo de descoberta de produto usando as interfaces integradas Disponibilidade e Elegibilidade na API Obter lista de produtos. A interface Disponibilidade filtra produtos indisponíveis para entrega com base em aspectos geográficos ou físicos. A interface Elegibilidade verifica se você está qualificado para comprar produtos com base em dados e regras de negócios específicos. Os representantes de vendas podem usar esse processo dinâmico de duas etapas para identificar as promoções mais relevantes e acelerar o processo de Checkout.

* **Carregue carrinhos grandes de modo eficiente com o modo de transferência de API**
  Aprimore o processamento de dados de carrinho grande com a API atualizada GetCartItems, apresentada no Modo de transferência da API. Você pode escolher de modo conveniente os campos desejados para mostrar nos pedidos, cotações ou oportunidades. Ao reduzir os metadados e simplificar os registros de precificação, a nova API Obter itens do carrinho otimiza o uso de memória e CPU para evitar falhas de tamanho de heap, de modo que até mesmo cargas úteis de carrinho em massa possam ser processadas com confiança. Os representantes de vendas obtêm uma experiência eficaz enquanto interagem com pacotes em grande escala e configurações complexas.

* **Melhorar a escalabilidade e o suporte para promoções grandes na precificação de compilação**
  Otimize o consumo de heap enquanto compila a precificação para promoções contendo pacotes grandes e configurações complexas. Um novo registro de resposta da API armazenado em cache facilita uma consulta de dados de produto mais eficiente representando a hierarquia de produtos de oferta compilada. Os representantes de vendas agora podem trabalhar com mais eficiência com produtos de promoção contendo até 15 itens de linha, garantindo alto desempenho mesmo durante tarefas de configuração complicadas.

* **Automatizar a remoção de produtos em pacotes de vários produtos**
  Mantenha suas cotações e pedidos precisos excluindo automaticamente produtos dependentes apenas dentro do contexto de pacote específico. Os representantes de vendas podem atualizar um item com a nova regra, que identifica o item de linha exclusivo a remover, em vez de limpar produtos semelhantes do carrinho. Essa atualização elimina inconsistências de configuração e reduz a necessidade de lógica personalizada complexa.

* **Salvar e reutilizar configurações do carrinho com modelos**
  Expanda a precisão da cotação ou do pedido usando modelos de configuração pré-configurados e aprovados dos carrinhos existentes. Os modelos são Obter, Pesquisar, Aplicar, Salvar e Excluir. Esses modelos armazenam hierarquias de produtos, atributos e ajustes de preço específicos para garantir ajustes consistentes. A configuração manual do pacote causa preços inconsistentes e retarda o ciclo de vendas. Os modelos capturam as práticas recomendadas de especialistas para simplificar operações de integração e escala de modo eficaz. Os representantes de vendas podem preencher rapidamente novas cotações e pedidos, reduzindo a entrada manual repetitiva de dados.

* **Automatize recriações de cotação complexas que usam clonagem de cotação de precisão**
  Replicar cotações corporativas, de vários sites e de um único site usando uma API invocável para eliminar a recriação manual de estruturas de negócios complexas. Capacite seus administradores e representantes de vendas a realizar clones profundos que preservam todos os itens de linha, substituições de precificação e relacionamentos hierárquicos sem usar uma interface do usuário. Aproveite nossa lógica Apex em grande escala por meio de duas interfaces distintas: use a ação remota para procedimentos de integração personalizados e OmniScripts ou use as APIs invocáveis para habilitar fluxos automatizados e ações de agente para Agentforce.

* **Objetos novos e alterados no pacote gerenciado CME**
  Faça mais com os novos objetos personalizados do Pacote gerenciado do CME.

* **Objetos atualizados do Gestão de resultados**
  Faça mais com os objetos atualizados de Gestão de resultados.

* **Extrair cláusulas de regulamentação e apólice com IA generativa**
  Reduza o tempo e o esforço necessários para digitalizar documentos regulatórios extraindo e criando registros de cláusulas de regulamentação e política no Process Compliance Navigator com IA generativa. A extração manual de cláusulas de conformidade de PDFs regulatórios longos é propensa a erros e reduz a capacidade da equipe de responder a requisitos novos ou atualizados. Carregue um PDF para extrair as principais informações e descrições enquanto ignora seções irrelevantes, como definições e perguntas frequentes. Os agentes de conformidade revisam os dados extraídos antes de finalizar as versões da cláusula para que você possa acelerar a digitalização de documentos legados e a implantação de proteções operacionais atualizadas.

* **Impor requisitos de conformidade com a assistência de conformidade**
  Navegue pelo complexo panorama de requisitos legais e internos com precisão usando o Agente de assistência de conformidade para o Navegador de conformidade do processo. O agente verifica os repositórios internos quanto a cláusulas regulatórias e de política, de modo que todas as respostas são adquiridas na documentação verificada. O Agente de assistência de conformidade fornece respostas instantâneas citadas diretamente no fluxo de trabalho para que os funcionários possam resolver perguntas de política sem consultar manuais manuais. Essa integração elimina o atrito de alternar entre aplicativos para que a equipe possa agir de modo rápido e com maior precisão.

* **Automatizar controles de conformidade com modelos de prompt**
  Capacite sua estratégia de conformidade usando o Criador de prompts para criar controles de conformidade automatizados usando linguagem natural. Foque avisos em dados da organização em tempo real para garantir que cada resposta de IA esteja alinhada a requisitos regulatórios específicos. A Camada de Trust do Einstein mascara automaticamente informações confidenciais antes de chegar ao LLM para que você mantenha uma integridade de dados rígida durante todo o processo. Por exemplo, para identificar riscos de conformidade sem revisão manual, verifique textos não estruturados, como emails e materiais de marketing. O sistema sinaliza possíveis violações no fluxo de trabalho existente e registra todos os eventos de conformidade para fins de auditoria.

* **Simplificar o mapeamento de conformidade com a análise de impacto**
  Identifique como as alterações nas cláusulas da política de conformidade e regulamentação afetam sua estrutura de conformidade usando a Análise de impacto para o Navegador de conformidade do processo. Identificar manualmente como cláusulas de regulamentação e política novas ou atualizadas se relacionam a registros existentes é demorado. Isso deixa as organizações vulneráveis a lacunas de conformidade. A Análise de impacto automatiza a descoberta desses relacionamentos para que você possa visualizar como as atualizações afetam todo o seu ecossistema de conformidade. Os Modelos de prompt fornecem instruções e restrições específicas para garantir que o LLM identifique correlações relevantes entre cláusulas, controles e processos.

* **Simplifique tarefas administrativas com o agente de gerenciamento de participantes aprimorado**
  Aumente a produtividade do gerente de caso usando o Agentforce para automatizar tarefas de documentação e acompanhamento diretamente do seu espaço de trabalho diário. Essa atualização migra o agente de Gerenciamento de participantes para o novo Agentforce Builder. O agente ajuda os usuários a registrar notas, criar tarefas e gerenciar benefícios no Slack.

* **Prepare-se para reuniões com o cliente mais rapidamente com Resumos do participante preparados pelo agente**
  Revise o histórico de um participante e o engajamento no programa em segundos usando o subagente Resumo do participante do agente de Gerenciamento de participantes. O subagente analisa notas de interação recentes, desembolsos de benefício, tarefas futuras e registros relacionados para fornecer uma visualização consolidada do progresso de um cliente. Use essas percepções para promover conversas mais empáticas e focar seu tempo nas necessidades imediatas do participante, em vez de pesquisar manualmente.

* **Gerenciar fluxos de trabalho complexos com mais condições de transição de estágio**
  Configure até 20 condições por transição de estágio, aumentando o limite anterior para cinco. Forneça um controle mais granular para fluxos de trabalho de negócios complexos, especificamente aqueles em setores regulados. Ao aumentar a contagem de critérios, você garante que os registros atendam a todas as verificações de elegibilidade antes de progredirem no ciclo de vida do registro.

* **Visualizar tarefas e eventos na linha do tempo vertical**
  Melhore a visibilidade da atividade incluindo Tarefas e eventos como fontes de dados em suas configurações de Linha do tempo verticais entre setores. Campos padrão, como Atribuído a, agora são exibidos como links clicáveis em vez de IDs de registro, facilitando a navegação entre registros relacionados. Expanda a visualização cronológica das interações habilitando Tarefas e eventos para linha do tempo por meio da API da interface do usuário. Para ver os campos personalizados de Tarefa em sua linha do tempo, adicione-os aos layouts de página.

* **Acelere a configuração de recebimento de serviço com o Criador de processos de serviço aprimorado**
  Defina atributos e organize coleções de produtos associadas em um espaço de trabalho intuitivo. Os designers de processos de serviço podem adicionar atributos do tipo de processo selecionado, além de definições de contexto e origens personalizadas. Reduza o atrito de configuração e prepare as entradas de serviço mais rapidamente configurando atributos e produtos em uma página.

* **Implemente vários processos de serviço na biblioteca de modelos**
  Crie seu catálogo de serviços mais rapidamente selecionando vários modelos predefinidos para instalar de uma só vez. Os designers podem visualizar modelos, personalizar detalhes do processo de serviço e ativar processos na criação. O sistema gera automaticamente um processo de serviço de modo assíncrono para cada modelo e rastreia o progresso na guia Histórico de instalação. Você pode tentar instalar novamente modelos com falha para garantir que seu catálogo esteja completo.

* **Implemente processos e dependências de serviço em organizações com mais segurança**
  Elimine a complexidade de migrar dados e metadados do processo de serviço. Use o Salesforce CLI para lidar com a transformação de ID de registro e o carregamento de dependência. Em vez de exportar manualmente registros e remapear IDs, agrupe um processo e seus fluxos de suporte em um arquivo .zip para implementação instantânea. Essa automação mantém a integridade de seus testes garantindo que a configuração exata do seu sandbox atinja as organizações de destino.

* **Padronizar o cumprimento de sua solicitação de serviço**
  Aumente a colaboração criando planos de ação que definem sequências de tarefas específicas e repetíveis para solicitações de serviço no Catálogo unificado, como pedidos de equipamento ou solicitações de acesso. Os usuários agora podem contar com atribuições automatizadas e prazos para garantir que cada solicitação siga um processo em conformidade e documentado. Antes, os planos de ação estavam disponíveis apenas para casos e incidentes.

* **Rastrear o desempenho da solicitação de serviço e a conformidade com SLA**
  Use dados de solicitação de serviço para medir o desempenho da sua equipe em relação às principais métricas de serviço. Ao sincronizar dados de solicitação de serviço com o Data 360, você pode visualizar resumos de resolução e alterações de status junto com seus dados de incidente e caso existentes.

* **Obter detalhes do processo de serviço**
  Use a ação de fluxo Obter detalhes do processo de serviço para recuperar valores de atributo e solicitações de produto relacionadas para um processo de serviço vinculado a um Caso, Incidente ou Solicitação de serviço. Essa ação de utilitário dá suporte a fluxos de processamento disponibilizando dados da seção de solicitação de produto na guia Atributos e produtos a elementos de fluxo downstream.

> 📄 **Notas Completas:** consulte os detalhes completos na página do tópico [INDUSTRIES](./releases/summer_26/industries.md).
</details>

<details>
<summary><b>📄 MARKETING PARENT (Clique para expandir 43 alterações)</b></summary>

* **Criar e expandir seu público**
  Agora ficou ainda mais fácil criar formulários de inscrição para seus canais de marketing com um modelo de fluxo pronto para uso que oferece uma configuração guiada. Além disso, os profissionais de marketing agora podem focar pessoas específicas e contornar a lógica complexa de segmento criando listas acionáveis.

* **Criar e projetar conteúdo com facilidade**
  Obtenha mais controle sobre a aparência, a leitura e o alcance de seus conteúdos de marketing para públicos globais. Reforce a consistência da marca com fontes da Web personalizadas, use o multilíngue com variantes de conteúdo e aproveite dados do Salesforce ativos para uma personalização mais profunda. Além disso, capture o consentimento de rastreamento da Web com banners personalizáveis no Salesforce CMS e expanda seu alcance com o suporte de email de texto simples.

* **Aprimore suas mensagens com serviços de comunicação avançados**
  Adicione serviços de comunicação avançada (RCS) à sua estratégia de marketing multicanal para oferecer experiências móveis interativas com marca aos seus clientes. Depois de configurar o RCS e verificar suas identidades de remetente, os profissionais de marketing podem usar o tipo de conteúdo Mensagem do RCS no Salesforce CMS para criar mensagens de alto engajamento com texto, mídia, cartões avançados e sugestões interativas.

* **Alinhar equipes de marketing e vendas**
  Identifique grupos de compra e promova oportunidades com o novo Agentforce Account Nurturing Agent. Mantenha a consistência de tom, voz e marca com aprimoramentos ao Distributed Marketing e alertas. Além disso, os usuários de vendas podem usar o novo Agente de marketing distribuído para encontrar os modelos de email certos e obter percepções de engajamento em mensagens distribuídas.

* **Visualizar o engajamento de marketing em registros de oportunidade**
  Monitore como os contatos relacionados a uma oportunidade interagiram com seus ativos de campanha de marketing diretamente no registro de oportunidade. Os representantes de vendas podem usar esse painel Histórico de engajamento unificado para visualizar dados relacionados a emails, formulários e exibições de página.

* **Gerar vendas com ferramentas de marketing automatizadas**
  Aumente as conversões usando acionadores de marketing personalizados para os principais comportamentos e eventos do usuário. Na Índia, você pode promover ainda mais os resultados enviando links de pagamento integrados diretamente em chats do WhatsApp. Você também pode incluir ofertas promocionais diretamente no conteúdo do email.

* **Expanda e gerencie suas operações de marketing**
  Os administradores de marketing agora podem gerenciar um negócio em crescimento e os profissionais de marketing podem disponibilizar conteúdo de uma unidade de negócios para outras com essas atualizações que estamos lançando para a versão Summer '26.

* **Expanda a personalização de email com objetos de marketing, suporte a idioma AMPscript e novos auxiliares de script**
  Armazene dados de marketing em objetos de marketing de alto rendimento. Personalize mensagens usando AMPscript e controles para recuperar dados do destinatário e incluir conteúdo reutilizável programaticamente. Valide seu código diretamente no editor visual, que identifica erros de sintaxe e fornece sugestões imediatas para correções.

* **Outras alterações no Marketing Cloud Next**
  Saiba mais sobre outras alterações feitas na versão Summer '26.

* **Carregar modelos de DLT para enviar mensagens SMS na Índia**
  Para enviar mensagens SMS na Índia e cumprir os regulamentos da Autoridade Reguladora de Telecomunicações da Índia (TRAI), carregue modelos de Tecnologia do Razão Distribuído (DLT) para o Marketing Cloud Next. Reduza o spam e melhore a capacidade de entrega de mensagens, garantindo que suas campanhas de SMS na Índia alcancem os clientes sem atrasos.

* **Simplificar o gerenciamento de consentimento entre produtos de marketing**
  Mantenha as preferências de comunicação dos clientes consistentes e em conformidade sincronizando dados de consentimento entre o Account Engagement do Marketing Cloud e o Marketing Cloud Next. Comece mapeando listas públicas estáticas no Account Engagement para assinaturas no Marketing Cloud Next. Quando a preferência de um cliente muda em um produto, seu status no outro produto é atualizado automaticamente.

* **Gerenciar emails com mais eficiência**
  Acesse novos recursos de email no Marketing Cloud Next, incluindo destinatários de cópia de carbono (CC) e arquivamento. Adicionar destinatários CC ajuda a manter os colegas envolvidos em trocas de negócios, enquanto o arquivamento de email fornece uma maneira mais econômica de manter registros de seus envios.

* **Visualizar atividade de engajamento em registros de oportunidade**
  Acesse rapidamente os dados de engajamento associados a um negócio. Adicione um painel Histórico de engajamento unificado ao registro Oportunidade para visualizar como os contatos estão interagindo com seus emails, formulários e exibições de página.

* **Organizar suas jornadas e aprimorar o desempenho**
  Melhore o desempenho da jornada com novas recomendações de configuração e gerencie suas jornadas com mais eficiência usando a seleção em massa no Painel da jornada.

* **Otimizar campanhas do WhatsApp com rastreamento de anúncio e pagamentos no Chat**
  Feche negócios com rapidez e precisão para medir a eficácia do gasto de anúncio com os novos recursos de integração do WhatsApp. Agora você pode rastrear automaticamente conversas do WhatsApp recebidas de seus anúncios do Meta e enviar opções de pagamento a clientes na Índia diretamente em um chat.

* **Explorar novos recursos de IA**
  Expanda suas opções de IA com o Protocolo de contexto do modelo, disponível progressivamente a partir de julho de 2026.

* **Outros recursos**
  Aprenda sobre outras alterações que fizemos na versão Summer '26.

* **Notas de versão arquivadas**
  As notas de versão do Marketing Cloud Engagement da versão Spring '24 e anteriores estão disponíveis para download em PDF. Para localizar atualizações da versão Summer '24 até nossa última versão, selecione uma versão no menu suspenso na barra de ferramentas.

* **Compartilhar códigos de SMS de engajamento com o Marketing Cloud Next**
  Agora você pode usar códigos curtos e códigos longos de SMS dos Estados Unidos e do Canadá no Marketing Cloud Next. Não é mais necessário executá-los novamente, assim, você pode unificar sua estratégia de mensagens e gerenciar o tráfego de saída e entrada para o Journey Builder e o Flow Builder de um só código.

* **Gerenciar consentimento com mais flexibilidade**
  Os profissionais de marketing agora podem mapear o consentimento de listas de Engajamento do Marketing Cloud e listas de publicação para assinaturas de comunicação no Marketing Cloud Next. Depois de mapear as listas, o status de um assinante é sincronizado sempre que ele atualiza seu consentimento. Essa alteração permite que você mantenha a conformidade ao enviar mensagens de qualquer um dos aplicativos.

* **Unificar seus dados de marketing para visibilidade completa do desempenho**
  Reúna mídia paga, canais de propriedade e percepções de CRM em uma única estrutura de inteligência. Analise modelos de atribuição, acompanhe o impacto do pipeline e entenda como o marketing gera receita sem costuração manual de dados.

* **Obtenha percepções mais profundas com o gerenciamento de dados aprimorado**
  Obtenha maior controle, visibilidade e eficiência em seus dados de marketing com conexões simplificadas, pipelines automatizados e percepções mais profundas sobre a qualidade dos dados e as jornadas do cliente.

* **Ative as percepções de marketing mais rapidamente com Agentforce**
  Use a análise habilitada por IA e alertas proativos para monitorar o desempenho da campanha e otimizar os resultados em seu fluxo de trabalho diário. Faça perguntas sobre dados com o Tableau Next Analytics, acompanhe o ritmo com o Tableau Next Inspector e otimize mídia paga diretamente no Slack em canais como LinkedIn e Snapchat.

* **Explorar jornadas e desempenho do cliente com painéis mais inteligentes**
  Visualize como os clientes se movem entre canais, identifique caminhos de alto desempenho para conversão e aprimore painéis com resumos de campanha gerados por IA que são atualizados automaticamente com seus filtros.

* **Recursos de personalização lançados por mês**
  Os recursos e alterações de Personalização do Salesforce e de Personalização do Marketing Cloud são lançados com frequência mensal, portanto, volte em breve para ver as atualizações mais recentes.

* **Rastrear pontos e criar subtipos para moedas baseadas em atividade**
  Identifique transações de acúmulo que atuam como a origem de pontos consumidos durante resgates para moedas com o modelo de expiração baseado em atividade. Ao vincular essas transações, você pode rastrear a responsabilidade em várias promoções e parceiros. Você também pode criar subtipos de moeda para controlar quais pontos são acumulados ou resgatados. Antes, você podia rastrear pontos e criar submoedas apenas para moedas com o modelo de expiração de duração fixa.

* **Encontre e entenda facilmente as configurações de rastreabilidade com rótulos atualizados**
  Para melhorar a capacidade de descoberta e se alinhar melhor com os recursos mais recentes do Gerenciamento de fidelidade, os nomes e descrições da configuração de rastreabilidade foram atualizados.

* **Definir atividades elegíveis para estender a validade de pontos baseados em atividade**
  Especifique as atividades elegíveis que estendem a validade de pontos de moedas resgatáveis baseadas em atividade usando tipos e subtipos de diário. Por exemplo, estenda as datas de atividade dos membros quando houver transações apenas com o tipo Acúmulo e o subtipo Compra. A definição do Mecanismo de processamento de dados, Identificar e atualizar datas de atividade para membros do programa de fidelidade, usa esses registros para calcular e atualizar as datas de expiração de pontos dos membros.

* **Dê aos membros mais tempo para usar pontos baseados em atividade**
  Dê aos membros mais flexibilidade adicionando um período de tolerância às datas de expiração dos pontos ou isentando os pontos da expiração. Defina janelas de restauração para que os representantes de atendimento ao cliente possam facilmente restabelecer pontos que expiraram dentro de um período. Defina diferentes períodos de tolerância e janelas de restauração com base no tipo de moeda e no nível.

* **Validar a integridade de dados do programa de fidelidade**
  Identifique discrepâncias em seus dados importados executando definições predefinidas do Mecanismo de processamento de dados. Use as definições para validar saldos de pontos do membro e registros de rastreabilidade do razão de fidelidade para pontos resgatáveis com um modelo de expiração de duração fixa.

* **Controlar a expiração do nível com datas e fórmulas personalizadas**
  Para recompensar realizações como participar de um programa de parceiros, agora você pode atualizar membros para níveis mais altos por uma duração específica. Ao usar o modelo de processo Alterar nível do membro ou a ação invocável Alterar nível, os gerentes e administradores do programa de fidelidade podem definir manualmente uma data de expiração ou usar uma fórmula para calcular uma dinamicamente.

* **Acelere a integração com a Google Wallet usando o aplicativo de amostra do SDK para Android**
  Use o aplicativo de referência atualizado no SDK móvel do Android para implementar rapidamente a funcionalidade do Google Wallet para seu programa de fidelidade. Na página Meu perfil do aplicativo, os membros agora podem vincular seus cartões de associação às contas do Google Wallet usando o botão Adicionar à carteira do Google. Após a vinculação, o aplicativo sincroniza automaticamente os vouchers associados aos cartões de associação com suas contas do Google Wallet.

* **Objetos novos e alterados para Gerenciamento de fidelidade**
  Faça mais com estes objetos novos e atualizados do Gerenciamento de fidelidade.

* **APIs REST do Connect novas e alteradas no Gerenciamento de fidelidade**
  Saiba mais sobre os recursos novos e alterados disponíveis com Gerenciamento de fidelidade e Gerenciamento de promoções globais.

* **Ações invocáveis novas e alteradas no Gerenciamento de fidelidade**
  Use as ações invocáveis novas e atualizadas no Gerenciamento de fidelidade.

* **Gerenciar e organizar orçamentos de promoção**
  Defina orçamentos de campanha e promoção e reconcilie fundos alocados com o gasto real. Crie uma hierarquia de orçamentos com base em seus requisitos de negócios. Por exemplo, aninhe orçamentos específicos da promoção em um orçamento no nível da campanha pai. Use os recursos da Salesforce Platform para reconciliar os orçamentos alocados com o gasto real e controlar a responsabilidade.

* **Gerenciar a responsabilidade da promoção com eficiência usando limites de promoção aprimorados**
  Controle seu passivo da promoção e execute com confiança eventos de alto volume, como vendas instantâneas, usando a nova estrutura de limite. Permita que os gerentes de marketing restrinjam o número total de vouchers emitidos e pontos creditados por promoção. Durante a execução da promoção, a estrutura verifica o uso em tempo real para cada voucher emitido e ponto creditado para garantir que os limites sejam estritamente aplicados.

* **Inscrever clientes em promoções específicas**
  Aumente o engajamento exigindo a inscrição do cliente para promoções de precificação. Os gerentes de marketing então usam os dados de inscrição para acionar comunicações de acompanhamento direcionadas e prever de modo eficaz os requisitos de inventário de recompensa. Aproveite a API de inscrição na promoção para integrar os recursos de inscrição. Antes, a inscrição era necessária apenas para promoções de fidelidade.

* **Simplificar a manutenção do catálogo de produtos ignorando itens não sincronizados**
  Mantenha sua vitrine funcionando sem problemas mesmo quando seu inventário externo e o catálogo de produtos do Salesforce não estiverem sincronizados. As APIs Promoções elegíveis e Avaliação e execução da promoção não rejeitam mais itens que ainda não estão sincronizados com o catálogo do Salesforce. Em vez disso, as APIs ignoram os produtos não sincronizados em um carrinho e aplicam promoções no nível da linha e no nível cruzado apenas aos itens sincronizados.

* **Automatizar a criação do procedimento de precificação para avaliação da promoção**
  Economize tempo e reduza erros de configuração manual usando o Salesforce Go para criar automaticamente o procedimento de precificação necessário para avaliação e execução da promoção.

* **Objetos novos e alterados no Gerenciamento de promoções globais**
  Faça mais com os objetos novos e atualizados de Gerenciamento de promoção global

* **Gerenciar e organizar orçamentos de promoção**
  Defina orçamentos de campanha e promoção e reconcilie fundos alocados com o gasto real. Crie uma hierarquia de orçamentos com base em seus requisitos de negócios. Por exemplo, aninhe orçamentos específicos da promoção em um orçamento no nível da campanha pai. Use os recursos da Salesforce Platform para reconciliar os orçamentos alocados com o gasto real e controlar a responsabilidade.

* **Objetos novos e alterados no marketing de indicações**
  Faça mais com o novo objeto no Gerenciamento de indicação.

> 📄 **Notas Completas:** consulte os detalhes completos na página do tópico [MARKETING PARENT](./releases/summer_26/marketing_parent.md).
</details>

<details>
<summary><b>📄 MOBILE (Clique para expandir 10 alterações)</b></summary>

* **Conclua tarefas diretamente de notificações telefônicas personalizadas (disponível ao público em geral)**
  Melhore a produtividade do usuário adicionando botões a notificações por push personalizadas. Com notificações acionáveis, os usuários podem reagir a alterações de negócios em tempo real sem sair da tela de bloqueio ou do centro de notificação do dispositivo móvel. Por exemplo, um usuário pode aceitar um lead, aprovar um desconto ou adiar uma tarefa para mais tarde, tudo com um só toque.

* **Personalizar sua página inicial do aplicativo móvel (beta)**
  Proporcione aos usuários uma experiência de página inicial nova e personalizada no aplicativo móvel do Salesforce. Embora a página inicial antiga permita personalização de usuário final individual, essa nova versão concede a você controle administrativo total para configurar e gerenciar o layout centralmente. Seus usuários agora podem ver as informações mais importantes em uma visão geral com cartões para Relatórios fixados, Recentes, Favoritos, Meu calendário, Eventos do Salesforce e Tarefas.

* **Aprimorar reuniões presenciais com a Transcrição de IA móvel**
  Concentre-se inteiramente em seu cliente com a transcrição móvel segura habilitada por IA que captura e sincroniza automaticamente notas confidenciais de reunião presencial com o Salesforce, eliminando a inserção de dados manual tediosa. Após a reunião, assim que seus dados forem sincronizados, o Einstein Conversation Insights criará resumos e destacará detalhes importantes, como preocupações do cliente ou menções de concorrentes. Também o ajuda a se manter organizado configurando tarefas de acompanhamento e personalizando seu alcance.

* **Fazer login no aplicativo Salesforce móvel com email por padrão**
  O aplicativo Salesforce móvel agora usa como padrão a autenticação baseada em email para minimizar o atrito de login e reduzir a sobrecarga administrativa. Ao priorizar a autenticação por email, sua experiência de login é mais simplificada, permitindo que você acesse seus dados mais rapidamente.

* **Gerenciar seus projetos de aplicativo móvel com renomeamento e arquivamento**
  Mantenha seu desenvolvimento de aplicativo móvel organizado gerenciando facilmente sua lista de projetos. Agora você pode renomear projetos existentes para refletir melhor sua finalidade ou arquivar projetos que não estão mais em uso ativo, garantindo que seu espaço de trabalho permaneça focado nas prioridades atuais.

* **Acelere aprovações da App Store e do Google Play com a permissão do aplicativo Salesforce móvel**
  Coloque seus aplicativos Salesforce móveis com marca nas mãos dos usuários mais rapidamente com a expansão de Permissões do aplicativo para funcionalidades do dispositivo. Antes disponíveis apenas para aplicativos do Experience Cloud, essas configurações de permissão personalizáveis agora estão disponíveis para o aplicativo Salesforce móvel. Ao fornecer justificativas claras para acesso a dispositivos, como câmera, fotos e localização, diretamente em seu projeto do Mobile Publisher, você garante a conformidade com as diretrizes de privacidade mais recentes da Apple e do Google, reduzindo o risco de rejeições de aplicativos.

* **Conclua tarefas diretamente de notificações telefônicas personalizadas (disponível ao público em geral)**
  Melhore a produtividade do usuário adicionando botões a notificações por push personalizadas. Com notificações acionáveis, os usuários podem reagir a alterações de negócios em tempo real sem sair da tela de bloqueio ou do centro de notificação do dispositivo móvel. Por exemplo, um usuário pode aceitar um lead, aprovar um desconto ou adiar uma tarefa para mais tarde, tudo com um só toque.

* **Adicione o Voice ao seu aplicativo móvel com o Agentforce Voice**
  O Agentforce Voice agora está disponível ao público em geral e, com o Agentforce Mobile SDK, você pode integrar uma experiência completa de agente de IA de voz para voz diretamente em qualquer aplicativo iOS ou Android. Em vez de rotear clientes por meio de um sistema de telefone, os usuários do aplicativo móvel podem tocar em um botão e falar naturalmente com um agente que entenda sua intenção, execute ações em dados ativos e atenda a um humano com contexto completo quando necessário.

* **Integre o Agentforce aos seus aplicativos móveis usando o React Native**
  Implemente agentes inteligentes para iOS e Android de um único projeto usando o Mobile SDK Agentforce para React Native. Você pode incorporar dados e ações do Salesforce aos seus aplicativos entre plataformas sem escrever código nativo separado para cada ambiente. Escolha entre uma interface de chat personalizável ou um processo em segundo plano para atender aos seus requisitos de negócios específicos

* **Personalize respostas do Agentforce móvel com tipos do Lightning**
  Defina estruturas JSON personalizadas para ações do agente para retornar dados que seu aplicativo móvel pode processar e exibir usando tipos personalizados do Lightning. O SDK do Agentforce Mobile agora oferece suporte a esses tipos por meio de substituições nativas da plataforma (SwiftUI e Jetpack Compose) ou Componentes da Web Lightning otimizados para dispositivos móveis, permitindo que você crie renderizadores personalizados e editores de entrada. Essa flexibilidade garante que seus usuários interajam com dados precisos e estruturados por meio de uma interface de alto desempenho personalizada para seus requisitos móveis específicos.

> 📄 **Notas Completas:** consulte os detalhes completos na página do tópico [MOBILE](./releases/summer_26/mobile.md).
</details>

<details>
<summary><b>📄 MULESOFT (Clique para expandir 5 alterações)</b></summary>

* **Inteligência de integração do MuleSoft**
  Maximize o tempo de atividade e otimize o desempenho com a Inteligência de integração. Estenda o valor da sua telemetria do MuleSoft com a Inteligência de integração para fornecer análises de longo prazo. Centralize métricas, registros e rastreamentos no Salesforce Data 360. Obtenha visibilidade de tendências históricas e padrões sistêmicos que vão além do monitoramento em tempo real. Use o aplicativo Inteligência de integração Lightning para acessar painéis pré-criados e personalizados do Tableau Next para obter Insights sobre solicitações e API unificadas. Use a análise assistida por agente para encontrar rapidamente a causa dos problemas. Acesse essas percepções operacionais diretamente da Anypoint Platform com login único.

* **Mapear seus agentes para ferramentas do servidor MCP**
  Use o Catálogo de API para mapear seus agentes para ferramentas em seus servidores personalizados do Salesforce MCP. Disponibilize rapidamente seus agentes existentes para uso como parte de servidores MCP.

* **Trazer servidores MCP do MuleSoft para o catálogo de API (disponível ao público em geral)**
  Sincronize servidores do Protocolo de contexto do modelo (MCP) do Anypoint Exchange e disponibilize-os para uso no Salesforce.

* **Descubra servidores MCP registrados manualmente no catálogo de API (disponível ao público em geral)**
  No seu catálogo, veja seus servidores de Protocolo de contexto de modelo (MCP) que você registra manualmente no Agentforce Registry ou instala de pacotes do AgentExchange.

* **Visualizar APIs de consulta nomeadas no catálogo de API e ativar ações (disponível ao público em geral)**
  A capacidade de trazer suas APIs de consulta nomeada para o Catálogo de API e ativar suas ações para uso no Agentforce agora está disponível ao público em geral.

> 📄 **Notas Completas:** consulte os detalhes completos na página do tópico [MULESOFT](./releases/summer_26/mulesoft.md).
</details>

<details>
<summary><b>📄 OMNISTUDIO (Clique para expandir 10 alterações)</b></summary>

* **Retomar OmniScripts entre usuários com salvamento aprimorado para mais tarde**
  Proporcione jornadas do cliente consistentes e colaborativas em que diferentes usuários possam iniciar, salvar e retomar o mesmo OmniScript. Antes, Salvar para mais tarde tinha limitações que geralmente resultavam em restrições de uso. Na versão Summer '26, essas limitações foram removidas. Agora você pode compartilhar registros de sessão salva do OmniScript com a opção Compartilhamento. Por exemplo, um representante de serviço interno pode iniciar uma solicitação em nome de um cliente e compartilhar um link com o cliente para concluí-la. Da mesma forma, um usuário convidado pode salvar seu progresso e retomá-lo posteriormente como um usuário autenticado.

* **Otimizar a consistência da implementação com controle de versão do Data Mapper**
  Gerencie diferentes versões de seus Mapeadores de dados habilitando o controle de versões. Ele ativa os Mapeadores de dados padrão existentes na versão 1 e bloqueia componentes ativos para manter a consistência em suas implementações. Você pode criar novas versões para fazer alterações em vez de editar componentes ativos, mantendo Mapeadores de dados consistentes com outros componentes do OmniStudio. Por padrão, o controle de versões do Data Mapper está desabilitado.

* **Alternar entre designers e tempos de execução de pacote padrão e gerenciado na mesma organização**
  Use o OmniStudio Hybrid para acessar designers padrão e de pacote gerenciado na mesma organização. Se você estiver em um tempo de execução e designer de pacote gerenciado, poderá criar todos os novos componentes diretamente no designer padrão e no tempo de execução padrão para ter um layout atualizado e desempenho aprimorado. Por padrão, o OmniStudio Hybrid está habilitado para usuários do pacote gerenciado para manter a consistência dos metadados enquanto fornece um caminho confiável para fluxos de trabalho modernos. Continue gerenciando seus componentes legados existentes no designer de pacotes gerenciados enquanto cria seus novos componentes no designer padrão.

* **Migrar para o tempo de execução padrão do OmniStudio usando o Assistente de migração do OmniStudio**
  Automatize e simplifique sua migração de componente do OmniStudio com o novo Assistente de migração do OmniStudio, um plug-in do Salesforce CLI. Migre FlexCards, OmniScripts, Mapeadores de dados, Procedimentos de integração, números automáticos globais, rótulos personalizados e objetos relacionados, como classes do Apex e FlexiPages. Você pode migrar esses componentes dos pacotes Vlocity Industries ou OmniStudio Foundation com modelo de dados personalizado ou padrão para o tempo de execução padrão do OmniStudio.

* **Acelere o desenvolvimento do FlexCard com o OmniStudio MCP (beta)**
  Use o servidor Protocolo de contexto de modelo (MCP) do OmniStudio para fechar a lacuna entre IA e desenvolvimento com baixa codificação. Essa implementação do MCP funciona como um caminho controlado para conectar agentes de IA diretamente ao seu ciclo de vida de desenvolvimento do OmniStudio. Use IA para converter rapidamente requisitos, como texto simples, capturas de tela ou mapeamentos de UX, em modelos funcionais do FlexCard. Em seguida, itere, simule e teste seus componentes antes da implantação.

* **Chamar fluxos iniciados automaticamente em FlexCards do OmniStudio (piloto)**
  Simplifique seu processo de desenvolvimento e use fluxos existentes ou novos iniciados automaticamente em FlexCards. Reutilize a lógica de negócios existente usando fluxos iniciados automaticamente como uma origem de dados nativa em FlexCards, levando o poder da automação em segundo plano do Fluxo para suas experiências digitais.

* **Obter orientação acionável para mensagens de erro do OmniStudio na Ajuda do Salesforce**
  Encontre causas acionáveis e soluções para erros. Corrija problemas relacionados ao design do componente, ao desempenho do tempo de execução, ao acesso e a outros cenários comuns.

* **Abrir ações do FlexCard em uma nova janela ou guia do navegador**
  Dê aos usuários mais controle sobre a experiência de navegação permitindo que eles abram destinos de ação do FlexCard em uma nova janela ou guia do navegador. Seus usuários agora podem iniciar OmniScripts ou páginas da Web externas sem perder seu lugar atual no Salesforce ou em um site do Experience Cloud.

* **Aprimoramentos de acessibilidade no OmniStudio**
  Proporcione experiências digitais mais inclusivas com aprimoramentos abrangentes de acessibilidade, usabilidade e consistência em componentes de tempo de execução do OmniStudio. Essas atualizações seguem as melhores práticas das Diretrizes de acessibilidade de conteúdo da Web (WCAG) 2.0 para melhorar a navegação para usuários de leitor de tela e teclado.

* **Versões secundárias do OmniStudio**
  Saiba mais sobre correções de bugs, pequenas atualizações e problemas conhecidos sobre o OmniStudio feitos após a versão Summer '25 e antes da versão Winter '26.

> 📄 **Notas Completas:** consulte os detalhes completos na página do tópico [OMNISTUDIO](./releases/summer_26/omnistudio.md).
</details>

* 📄 **OTHER PRODUCTS**: Acesse o arquivo de notas de versão em [./releases/summer_26/other_products.md](./releases/summer_26/other_products.md).
* 📄 **PARTNER CLOUD**: Acesse o arquivo de notas de versão em [./releases/summer_26/partner_cloud.md](./releases/summer_26/partner_cloud.md).
<details>
<summary><b>📄 REVENUE (Clique para expandir 80 alterações)</b></summary>

* **Simplifique a coleta de receita com a Solução de orquestração Dunning**
  Acelere seu processo de cobranças e reduza faturas vencidas com uma experiência de redução automatizada. Com a Solução de orquestração Dunning, você pode gerenciar automaticamente lembretes de pagamento usando modelos do Orquestrador dinâmico de receita. Projete jornadas de redução baseadas em segmento para focar grupos de clientes específicos para uma recuperação de receita mais eficiente.

* **Descubra mais recursos de gerenciamento de receita**
  Use o Salesforce Go para configurar recursos adicionais de Gerenciamento de preço e Orquestrador de receita dinâmica com facilidade.

* **Crie transações mais rapidamente com a Descoberta baseada em regra**
  Crie cotações e pedidos sem sair do catálogo de produtos. Os representantes de vendas veem atualizações de transações em tempo real, recebem recomendações de produtos compatíveis e adicionam produtos diretamente a cotações ou pedidos. Antes, os representantes de vendas exibiam várias páginas para verificar a compatibilidade do produto e visualizar o progresso das transações.

* **Aplicar seleção de rampa consistente durante a descoberta e configuração do produto**
  Selecione se deseja adicionar produtos a grupos atuais ou subsequentes antes de visualizar a lista de produtos. Agora, quando você adiciona produtos a grupos atuais ou subsequentes na Descoberta de produtos, o Configurador cumpre a seleção e aplica o grupo de rampa correto ao salvar a transação. Antes, o configurador armazenava produtos apenas no grupo atual. Essa transferência tranquila elimina o retrabalho manual ao estruturar negócios de rampa complexos.

* **Expanda suas ofertas de produto com variações de produto**
  Agrupe produtos que compartilham um design, mas diferem em atributos específicos em um produto pai. Durante a descoberta do produto, os representantes de vendas podem visualizar as variações pai e configurar as propriedades da variante para selecionar uma variante de produto específica. Eles então podem adicionar o produto configurado diretamente a uma cotação ou pedido. Antes, os representantes de vendas pesquisavam cada variação de produto como um produto individual. Ao agrupar produtos relacionados, os representantes de vendas passam menos tempo pesquisando no catálogo e criando cotações mais rapidamente.

* **Mostrar precificação precisa e consistente com suporte decimal estendido**
  Configure até seis casas decimais para padronizar os preços no nível da unidade e os campos de desconto que aparecem nas páginas Descoberta de produto, Cotação e Pedido. Essa formatação garante que os preços sejam exibidos de maneira consistente na interface do usuário sem alterar os valores de banco de dados subjacentes. Antes, essas páginas mostravam de modo inconsistente valores de banco de dados completos ou valores truncados em duas casas decimais.

* **Novas APIs REST do Connect no Gerenciamento de catálogo de produtos**
  Lista e pesquise classificações de produto que se originam de fontes de catálogo de Catálogo de produtos Enterprise (EPC) ou Gerenciamento de catálogo de produtos (PCM). Além disso, gerencie várias variantes de um produto com mais eficiência localizando e configurando diferentes propriedades antes de fazer a cotação ou o pedido.

* **APIs REST do Connect novas e alteradas na Descoberta de produtos**
  Verifique se cada transação é precisa executando regras de configuração que identificam problemas e fornecem mensagens de regra na resposta da API. Esse feedback imediato ajuda você a entender as restrições durante a fase de descoberta e evitar problemas durante o processamento da transação. Você também pode usar recomendações baseadas em regra para orientar os compradores para os produtos adequados para suas necessidades específicas.

* **Ações invocáveis novas e alteradas na Descoberta de produtos**
  Certifique-se de que cada opção de produto em sua automação seja válida executando regras de configuração com base em uma transação ou um ID de contexto específico. Você pode identificar problemas durante as fases de descoberta e pesquisa.

* **runtime_industries_cpq Namespace**
  Integre verificações de configuração em tempo real às classes do Apex para detectar violações de produtos durante a descoberta e seleção. O namespace runtime_industries_cpq inclui uma nova propriedade que habilita regras de configuração para um ID de transação ou ID de contexto da transação específico.

* **Usar tabelas de decisão baseadas em CSV em procedimentos de precificação**
  Integre grandes conjuntos de dados à sua lógica de precificação pesquisando dados em tabelas de decisão baseadas em CSV. Essa alternativa a origens de objeto padrão ou personalizadas oferece suporte a todos os elementos em tipos de uso de precificação. Gerencie até 100.000 linhas para tabelas sem controle de versão e com controle único importando suas definições de CSV.

* **Sincronizar tabelas de decisão para qualquer receita de precificação**
  Mantenha seus dados de precificação atualizados sincronizando todas as tabelas de decisão para qualquer receita de precificação. Antes, você podia sincronizar apenas a receita padrão.

* **Mapear mais variáveis no elemento de item de linha de mapa**
  Obtenha um controle mais granular sobre itens principais e sublinhados mapeando até 100 variáveis no elemento Item de linha de mapa. Antes, o limite era 50.

* **APIs REST do Connect alteradas na precificação do Salesforce**
  Sincronize dados de precificação para uma receita de precificação e visualize o código de moeda usado durante a execução da precificação em registros de log da API.

* **Definir restrições para grupos de cotações e segmentos de rampa**
  No Mecanismo de regras de restrição, defina as restrições que se aplicam a produtos em um grupo para obter um controle mais preciso sobre cotações complexas. Defina restrições para um segmento específico em um negócio de rampa para combinações de produto, validação e precificação precisas em um grupo de cotações ou um segmento de rampa.

* **Carregar padrões de produto em restrições**
  Agora você pode incluir dinamicamente padrões de produto, como atributos, valores de atributo, campos personalizados e campos padrão definidos no Gerenciamento de catálogo de produtos (PCM) quando você importa produtos do PCM para uma restrição. Incluir padrões resulta em cotações mais rápidas e precisas, maior consistência entre cotações e uma experiência de usuário aprimorada para os representantes de vendas.

* **Atualizações no fluxo de configurador de produto padrão**
  O fluxo Configurador de produto padrão tem novos atributos. Se você tiver clonado o fluxo Configurador de produto padrão antes da versão Summer '26, mapeie manualmente os novos atributos em seu fluxo personalizado ou clone o fluxo padrão e aplique suas personalizações novamente.

* **API REST do Connect alterada no Product Configurator**
  Agrupe mensagens do Product Configurator por um valor específico. Por exemplo, você pode agrupar problemas de restrição em um conjunto de itens de linha relacionados.

* **Aprimorar a visibilidade de atributo no editor de linha de transação de vendas**
  Seus representantes de vendas agora podem visualizar até 200 atributos de produto para cada linha de cotação no painel lateral do Editor de linha de transação de vendas. Os atributos usam nomes de exibição definidos e os atributos marcados como ocultos são excluídos para melhorar a clareza.

* **Trabalhe com mais eficiência com o editor de linha de transação de vendas aprimorado**
  O Editor de linha de transação de vendas (STLE) não tem mais um limite fixo de altura, proporcionando mais espaço para trabalhar. O STLE agora é dimensionado para preencher a janela do navegador, maximizando o patrimônio da página para fornecer uma visualização maior e mais abrangente de cotações e pedidos. Seus representantes de vendas podem visualizar e editar com eficiência mais itens de linha em uma só visualização, com menos rolagem de página.

* **Clonar cotações e pedidos com todos os registros relacionados**
  Seus representantes de vendas agora podem clonar cotações e pedidos enquanto retêm todos os registros relacionados, incluindo objetos personalizados, pacotes, linhas independentes, rampas e ações associadas para cotações de emenda, renovação e cancelamento. Esse aprimoramento reduz o retrabalho manual e mantém a consistência com a transação original.

* **Vender variações de produto em cotações e pedidos**
  Os representantes de vendas agora podem vender diferentes versões de um único produto de base, como tamanho ou cor, depois de você configurar variações de produto em seu catálogo. Encontre e adicione variações de produto a cotações e pedidos usando Procurar catálogo e Adição rápida no Editor de linha de transação de vendas (STLE). Os representantes de vendas podem visualizar os atributos de variação específicos no painel lateral para garantir a precisão antes de salvar.

* **Simplifique a cotação de vários anos usando uma agenda de rampa guiada**
  Use um fluxo guiado para gerar agendas de rampa de vários anos em vez de clonar segmentos manualmente. Inclua períodos de avaliação e selecione se deseja colocar segmentos divididos proporcionalmente no início ou no fim de um contrato para se alinhar às necessidades do cliente. Os representantes de vendas podem visualizar e ajustar toda a agenda antes de salvar as alterações à cotação.

* **Renovar ativos perdidos antecipadamente para garantir receita futura**
  Reforce proativamente os relacionamentos com o cliente e aumente o valor da vida útil renovando agendas de rampa de vários anos antes de elas expirarem. Os representantes de vendas podem selecionar ativos aprimorados para renovação antecipada para encerrar segmentos existentes e consolidar assinaturas em uma única agenda de rampas prospectiva. Obtenha relatórios financeiros precisos gerando linhas de crédito para períodos encerrados enquanto seus representantes negociam novos termos para o período de renovação.

* **Lide com configurações de produto complexas com mais atributos**
  Gerencie cotações complexas e altamente configuráveis em transações padrão aumentando o número de atributos do produto para até 10.000 em todas as linhas de cotação.

* **Processe mais registros para cada transação**
  Aumente o número de registros persistidos para cada transação para reduzir os ciclos de economia e melhorar a eficiência para operações de alto volume.

* **Fortaleça o Criador de documentos com uma robusta arquitetura de serviço**
  Criador de documentos agora é executado em uma estrutura robusta e em grande escala projetada para lidar com suas necessidades de documentos de negócios mais complexos. Essa evolução arquitetônica garante desempenho e confiabilidade consistentes à medida que o volume de ordens de trabalho e compromissos de serviço da sua organização aumenta.

* **Acompanhe dados de cotação e imposto com a visibilidade de objeto aprimorada**
  Agora você pode acompanhar alterações de negócio e processos comerciais com mais eficiência com relatórios sobre registros de Histórico de item de linha de cotação e Ação de cotação. Melhore a transparência fiscal e visualize, edite e adicione valores de imposto personalizados usando o novo objeto Item de imposto do item de cotação. Personalize o modo de exibição de lista Cotação adicionando botões personalizados e ações rápidas para gerenciar atualizações em massa ou criação automatizada de cotação.

* **Proteger o acesso a dados para precificação com permissões elevadas**
  Tenha continuidade de negócios durante a precificação da transação de vendas enquanto protege dados confidenciais contra acesso não autorizado. Ative Acesso a dados elevado para cotações e pedidos de precificação e orquestração de plano de procedimento para precificação e restrinja campos do contexto usando ganchos personalizados do Apex. O mecanismo de precificação acessa os dados internamente para garantir que o preço da transação esteja correto, mas os usuários sem segurança em nível de campo não podem consultar, visualizar ou modificar os campos usados para calcular a precificação.

* **API REST do Connect alterada no Gerenciamento de transações**
  Consulte um conjunto específico de campos em um sObject em vez de todos os campos para melhorar o desempenho. Use a API de Transação de vendas de leitura aprimorada para aceitar um nome de sObject junto com os nomes de campo específicos para consulta.

* **Mantenha as aprovações se movendo no Slack**
  Leve seus fluxos de trabalho de aprovação para o Slack. Os revisores podem aprovar ou rejeitar solicitações e adicionar comentários diretamente no Slack, e os remetentes recebem notificações em tempo real quando as solicitações são enviadas e revisadas. O componente Rastreamento de aprovação no registro relacionado monitora as ações do Slack, dando às equipes uma visão clara do status e do histórico do item de trabalho.

* **Visualizar dependências da etapa de aprovação para seu envio**
  Mostre aos usuários as dependências entre as etapas de aprovação. A janela de visualização organiza os itens de trabalho pela ordem sequencial. Essa visibilidade também ajuda os usuários a estimar a linha do tempo de aprovação.

* **Personalize e automatize ações de aprovação com Fluxo e Apex**
  Dê mais flexibilidade às suas aprovações usando ações invocáveis de fluxos iniciados automaticamente e Apex. Por exemplo, crie um fluxo iniciado automaticamente para revisar itens de trabalho de aprovação ou use acionadores do Apex para cancelar aprovações pendentes quando um registro relacionado for atualizado.

* **API REST do Connect alterada em Advanced Approvals**
  Use a API avançada Visualizar aprovação para obter visibilidade de seus processos de negócios visualizando informações do estágio e detalhes do designado. Gerencie aprovações complexas de várias etapas e atribuições de tarefa.

* **Orquestre negócios de vários anos com ativos de cumprimento com conhecimento em tempo**
  Divida itens de linha do pedido de negócios complexos de vários anos em itens de linha de cumprimento com base em configurações de ativo de cumprimento, como valores de quantidade e atributo, para um período específico. Essa decomposição baseada em linha do tempo alinha o cumprimento com datas efetivas em vez de instantâneos estáticos, oferecendo suporte a adições, cancelamentos e renovações sem soluções alternativas complexas.

* **Agendar etapas de orquestração com atrasos negativos**
  Inicie ações proativas com base em datas de contexto personalizadas, como enviar lembretes ou iniciar verificações antes de uma data de vencimento da fatura. Ao usar valores de atraso negativos, você pode agendar etapas de orquestração de data futura para ocorrer antes de um evento específico.

* **Melhorar o comportamento da etapa de tarefa automática aprovando parâmetros personalizados**
  Passe valores de configuração personalizados específicos da etapa diretamente de tarefas automáticas do Orquestrador de receita dinâmica (DRO) para o Salesforce Flow. Crie modelos de fluxo reutilizáveis com lógica de ramificação condicional em vez de criar fluxos separados com pequenas variações. Por exemplo, você pode enviar conteúdo de email diferente, como lembretes amigáveis ou difíceis, ou aprovar durações de marco específicas usando o valor de configuração.

* **Obter visibilidade operacional com relatórios de cumprimento**
  Monitore seus processos de orquestração com relatórios sobre objetos relacionados a processamentos. Essa visibilidade ajuda a rastrear proativamente vários cenários, como monitorar pedidos de data futura ou gerenciar o provisionamento de data futura e o desprovisionamento de ativos. Para atualizações diárias, use a edição em linha e assinaturas de relatório.

* **Migrar dados de condição do Orquestrador de receita dinâmica**
  Extraia, armazene e migre a condição em seus ambientes com facilidade. Agora você pode realizar inserções em massa de regras e condições de Regra de decomposição de cumprimento do produto, Cenário de cumprimento do produto, Definição da etapa de cumprimento e Regra de atribuição de tarefa em uma única transação.

* **Objetos novos e alterados no Orquestrador de receita dinâmica**
  Aumente sua produtividade com esses objetos novos e alterados do Orquestrador de receita dinâmica.

* **API REST do Connect alterada no Orquestrador de receita dinâmica**
  Promova a lógica de descomposição e ativação e obtenha uma visualização abrangente dos atributos do produto e seus metadados associados.

* **Novo tipo de metadados no Orquestrador de receita dinâmica**
  Use o novo tipo de metadados para conectar os dados de negócios de um objeto à lógica de orquestração.

* **Reduza o tempo de configuração para produtos de uso com um fluxo de trabalho guiado**
  Use a interface de usuário aprimorada para configurar produtos de uso de âncora e pacote. O fluxo de trabalho guiado o conduz pela definição de produtos, recursos e políticas de base. As validações integradas para cada registro de uso ajudam a garantir a integridade dos dados antes de ativar o produto e os registros relacionados.

* **Nova API REST do Connect no Gerenciamento de uso**
  Simplifique sua configuração ativando um produto de uso e seus registros relacionados em uma única solicitação de API. Essa atualização elimina o esforço manual de navegar em várias páginas para ativar cada registro separadamente.

* **Cargas úteis simplificadas para a API de criação de agendas de faturamento independentes**
  Seus desenvolvedores agora podem usar a API aprimorada Criar agendas de faturamento independentes para passar solicitações mínimas baseadas em intenção para essas operações: emendas à frequência de faturamento, data de término, campo, preço e quantidade, renovações e cancelamentos. Se você não passar os dados para os campos obrigatórios de faturamento, como preço unitário e preço total em caso de emendas, o Billing agora poderá calcular automaticamente esses detalhes com base no contexto da transação histórica ou no ID do grupo da agenda de faturamento.

* **Objetos novos e alterados para faturamento**
  Armazene e acesse mais dados com esses novos objetos de Faturamento e alterações a objetos de Faturamento existentes.

* **API REST do Connect alterada no Billing**
  A API Criar agendas de faturamento independentes agora oferece suporte à troca de dados simplificada. Se você estiver realizando uma alteração ou renovação de preço, poderá enviar detalhes de solicitação de alto nível enquanto o sistema gerencia os ajustes de faturamento granulares. Você também pode alterar as frequências de faturamento no meio da assinatura, incluindo turnos de prazos anuais para mensais, diretamente no nível do grupo de agenda de faturamento. Esse aprimoramento lida com divisão proporcional complexa e calcula os valores corretos do período de faturamento quando as frequências de precificação e faturamento diferem.

* **Tipos de metadados alterados no Billing**
  Reconcilie os saldos restantes para refletir o estado da transação mais recente, especialmente quando seus clientes alterarem ou cancelarem um pedido.

* **Ações invocáveis novas e alteradas no Billing**
  Forneça extratos de conta mais detalhados incluindo campos personalizados para atender a requisitos de relatórios exclusivos. Além disso, automatize o processo de reembolso e inicie notificações rápidas para liquidar faturas não pagas sem intervenção manual.

* **Resumir transações de faturamento em um extrato de conta**
  Obtenha uma visualização consolidada de todas as transações de faturamento para uma conta e suas contas relacionadas usando a ação rápida Gerar extrato de conta. Você pode criar extratos de conta diretamente de registros de Conta, além de usar a API Gerar extrato de conta.

* **Gerenciar todas as transações de faturamento na Central de liquidações de faturamento**
  Obtenha uma visualização unificada de todas as suas transações de faturamento: faturas, pagamentos, avisos de crédito e avisos de débito. Obtenha visibilidade em tempo real de saldos abertos. Aplique pagamentos e créditos e liquide faturas na mesma interface.

* **Visualizar todos os relacionamentos de acordo de faturamento de registros de conta e fatura**
  Visualize os relacionamentos de acordo de faturamento de propriedade e faturado diretamente nos registros de Fatura e Conta. Em registros de Conta, a lista relacionada Grupos de propriedade dos agendamentos de faturamento mostra grupos de propriedade de uma conta e a lista relacionada Grupos de agendamento de faturamento com acordo de faturamento mostra grupos em que a conta é a conta de faturamento em acordos de faturamento ativos. Em registros de fatura, a lista relacionada Faturas relacionadas com o mesmo acordo de faturamento mostra que todas as faturas faturadas com base no mesmo acordo de faturamento, tornando fácil identificar e ir para faturas de divisão relacionadas.

* **Gerenciar consultas de faturamento de modo eficiente com métricas e criação de caso assistida**
  Capacite seus representantes de atendimento ao cliente a iniciar disputas de faturamento diretamente em nome de seus clientes para acelerar o processo de recebimento de solicitação de serviço, o tempo de processamento e resolução. Obtenha notificações em tempo real para novos casos de faturamento, visualize a lista de casos de faturamento recentes para uma conta e rastreie métricas de caso no Console de operações de faturamento. Ao usar esses aprimoramentos, seus representantes de atendimento ao cliente podem rastrear e analisar de modo eficiente casos de faturamento e padrões de disputa, além de gerar relatórios. A criação de caso assistida gera resoluções mais rápidas enquanto também minimiza o esforço do cliente processando o envio e o rastreamento para ele.

* **Alinhar o faturamento a cancelamentos em pedidos e cotações datados no futuro**
  Obtenha agendas de faturamento precisas para cotações e pedidos que são cancelados antes do início de um pedido ou cotação de data futura agendado. Esse aprimoramento tem suporte em produtos com prazo definido e únicos e elimina a necessidade de reconciliação manual.

* **Dar suporte a planos de marco para emendas**
  Aplique planos de marco a agendas de faturamento alteradas. Quando você ativa um pedido de emenda com um plano de marco negociado ou um tratamento de faturamento habilitado para marco, o Billing vincula o plano de marco às agendas de faturamento atualizadas e recalibra o plano com base no valor e na data da emenda.

* **Mudar de frequências de faturamento mais altas para mais baixas em novos pedidos de vendas e cotações**
  Seus representantes de vendas podem atualizar a frequência de faturamento em novos pedidos de vendas e cotações, de prazos de precificação mais longos, como semestral ou anual, a ciclos de faturamento mais curtos, como mensal ou trimestral, e vice-versa. Quando o pedido é ativado, o Billing gera automaticamente agendas de faturamento precisas com valores de período de faturamento adequados com base na frequência de faturamento atualizada.

* **Tome decisões de cobrança mais inteligentes com pontuações de risco de fatura preditivas (piloto)**
  Identifique faturas com risco de atraso no pagamento e concentre os esforços de cobrança nos pontos mais importantes. Classifique faturas em níveis de risco para orientar acompanhamentos e reduzir pagamentos vencidos. Use essas percepções para promover ações oportunas e melhorar a visibilidade do fluxo de caixa.

* **Transfira faturas mais rapidamente com execuções de lote de fatura atualizadas**
  Faturas agora fluem para o Salesforce quando uma execução em lote da fatura começa. As equipes de faturamento podem começar a revisar, enviar e cobrar pagamentos em faturas imediatamente, sem esperar a conclusão de todo o trabalho. Além disso, ao monitorar execuções em lote de fatura, agora você vê um único trabalho de gerenciamento em lote, em vez de três etapas de processamento separadas.

* **Iniciar agendas de fatura diárias e semanais em dias úteis**
  Configure execuções de fatura diárias e semanais para começar nos dias úteis. Junto com agendas mensais, as execuções de fatura diárias e semanais agora podem começar em um dia útil se a data original cair em um feriado ou fim de semana.

* **Agrupar faturas de uma conta em uma única solicitação de pagamento**
  Combine várias faturas de uma conta em uma única solicitação de pagamento. As faturas são agrupadas com base na moeda, na forma de pagamento salva e na janela de data de vencimento. Quando você gera faturas, o Billing gera automaticamente uma única agenda de pagamento e um item de agenda de pagamento para as faturas. Esse aprimoramento ajuda seus clientes a economizar taxas de transação fazendo uma única solicitação de pagamento para várias faturas.

* **Iniciar reembolsos automatizados em faturas negativas e canceladas**
  Seus clientes agora podem iniciar reembolsos automaticamente em transações canceladas ou com alterações negativas. O Billing calcula o valor correto do reembolso com base na fatura original e na fatura de emenda ou cancelamento e, em seguida, liquida a fatura original com um aviso de crédito.

* **Envie dados de Nível 2 e Nível 3 para pagamentos feitos por meio de adaptadores do Apex**
  Agora você pode incluir dados aprimorados de Nível 2 e Nível 3 em suas solicitações de pagamento para gateways de pagamento. Esse recurso permite que o Billing passe informações detalhadas sobre transações, como itens de linha, detalhes de envio e metadados fiscais, diretamente para gateways de pagamento por meio de adaptadores do Apex. Quando o mecanismo de pagamentos em lote é executado, ele inclui automaticamente os metadados aprimorados nos registros do gateway de pagamento. Ao fornecer esses dados granulares, sua empresa pode se qualificar para tarifas de troca menores para transações.

* **Gerar links de Pagar agora e associar pagamentos a contas comerciais**
  Associe pagamentos de fatura à conta comercial correta gerando links Pagar agora. O pagamento e quaisquer formas de pagamento salvas são associados automaticamente à conta comercial correta no Billing. Quando os clientes pagam como convidados usando uma nova forma de pagamento, eles podem salvá-la para uso futuro.

* **Expanda suas opções de pagamento por meio do Portal de faturamento**
  Os clientes agora podem salvar e processar pagamentos com um conjunto adicional de formas de pagamento. Além de cartões de crédito e Central de compensação automatizada (ACH), o portal Billing agora oferece suporte a carteiras digitais, como Apple Pay e Google Pay, e métodos de débito bancário, como débito SEPA e débito BACS. Ele também oferece suporte a opções de compra agora, pagamento posterior, incluindo Klarna e Afterpay. Esses métodos estão disponíveis por meio de gateways de pagamento Stripe e Adyen. Os clientes podem pagar faturas e salvar um método de pagamento para uso futuro para simplificar pagamentos repetidos.

* **Automatize fluxos de trabalho de redução usando modelos dinâmicos do Orquestrador de receita**
  Agora você pode automatizar toda a jornada de envio de lembretes de email para recuperação manual em coletas de pagamento. Ao usar os modelos prontos para uso do Orquestrador de receita dinâmica, você pode enviar automaticamente lembretes de pagamento para faturas vencidas e vencidas. Você também pode personalizar o fluxo de trabalho diminuindo conforme suas necessidades de negócios e segmentos de clientes para simplificar a coleta de receita e tornar o alcance mais eficaz.

* **Extraia dados de contrato de repositórios externos em massa**
  Extraia campos de contrato e cláusulas de grandes volumes de documentos armazenados em repositórios externos, como Amazon S3 e Google Cloud Storage, sem copiar arquivos para o Salesforce. Envie vários documentos em uma única solicitação e processe-os por meio de um pipeline de extração projetado para contratos criados fora do Salesforce. Defina descrições baseadas em prompt em modelos de extração para extrair metadados e cláusulas dos detalhes do contrato. Selecione o pipeline de processamento adequado, como IA do documento para arquivos menores ou Extração inteligente para documentos grandes, e revise os resultados nos relatórios de extração em massa.

* **Extraia dados de contratos externos com pipelines de extração única flexíveis**
  Extraia campos de contrato e cláusulas de documentos externos e importe-os para o Salesforce como dados estruturados. Execute a extração única sem uma licença do AWS Textract usando IA do documento ou APIs multimodais para arquivos menores e Extração inteligente para documentos grandes. Configure e teste a extração de cláusula com modelos de prompt e selecione o modelo adequado ao seu caso de uso. Armazene avisos em atributos de contexto para manter as configurações em todas as alterações de mapeamento e revise os resultados com a experiência de visualização de modelo aprimorada.

* **Rotear aprovações de contrato com Advanced Approvals**
  Gerencie fluxos de trabalho complexos de aprovação de contrato usando Advanced Approvals com Salesforce Contracts. Encaminhe aprovações por cadeias de vários níveis, roteamento condicional com base em campos de contrato, como valor do contrato, e grupos de aprovação, como equipes jurídicas ou financeiras. Os aprovadores recebem notificações e aprovam ou rejeitam contratos diretamente por email.

* **Gerar documentos na localidade do usuário**
  Gere documentos que reflitam as configurações regionais e de idioma específicas do usuário, incluindo texto traduzido, moeda específica da localidade e formatos de data e hora. Controle a localização para solicitações de geração de documento para aplicar formatação consistente entre saídas. Para um controle mais granular, gerencie a localização de definições de contexto para aplicar seletivamente traduções ou reter valores originais. A renderização do documento depende da fonte selecionada, portanto, selecione fontes que oferecem suporte aos idiomas necessários ou use modelos específicos do idioma quando necessário. Se a localização estiver desativada, os dados do documento seguirão o idioma padrão e as configurações regionais da organização.

* **Preserve tokens não resolvidos com tokens de contornação**
  Aplique tokens de desvio para manter tokens específicos inalterados em documentos gerados quando nenhum valor for fornecido. Por exemplo, um token de assinatura do Adobe Sign {{Sig_es_:signer1:signature}} agora permanece no documento gerado quando nenhum valor é fornecido, em vez de ser removido e quebrar o fluxo de trabalho de assinatura. Defina uma lista de desvio de tokens para ignorar a substituição durante a geração do documento. Os tokens na lista de desvio permanecem inalterados, a menos que um valor seja fornecido, enquanto outros tokens continuam seguindo o comportamento padrão e são substituídos por valores vazios.

* **Objetos novos e alterados na geração de documentos e contratos**
  Faça mais com esses objetos novos e alterados de Geração de documento e Contratos.

* **APIs REST do Connect alteradas em Salesforce Contracts**
  Configure modelos de documento com um nome de transformação de contexto e especifique entrada adicional para mapeamentos de contexto de extração. Use a resposta para verificar a entrada usada durante a extração.

* **Gerar documentos com pacotes hierárquicos e dados agrupados**
  Transforme dados para capturar relacionamentos hierárquicos, agrupamentos e valores calculados em documentos gerados. Por exemplo, crie pacotes de produtos aninhados e organize grupos de linhas de cotação com seus itens de linha associados para obter uma saída de documento mais clara. Aplique lógica de agrupamento, como agrupamento por modelo de venda, intervalo de preços ou condições de quantidade, para apresentar dados em seções significativas. Aplique fórmulas para derivar valores calculados. Melhore a precisão do documento usando os Serviços de contexto e o Mecanismo de processamento de dados (DPE) para processar conjuntos de dados grandes.

* **Proteger e categorizar documentos com marcação d'água dinâmica**
  Proteja seus documentos e indique seu status adicionando marcas d'água de texto dinâmico durante o processo de geração de documento. Rotule automaticamente os documentos como Rascunho, Somente interno ou com dados de registro específicos e reduza o risco de compartilhamento não autorizado ou uso acidental de versões obsoletas. Esse recurso está disponível apenas para texto simples.

* **Navegue em documentos complexos com um índice automatizado**
  Proporcione uma experiência de leitura superior atualizando automaticamente tabelas de conteúdo (ToC) precisas e clicáveis para seus documentos DOCX e PDF. O ToC automatizado elimina a formatação manual reconhecendo hierarquias de documentos e calcula números de página após a mesclagem de dados e expansão dinâmica de conteúdo.

* **Gerar documentos de páginas e fluxos de registro**
  Gere e visualize documentos diretamente de páginas de registro ou fluxos usando o Componente da Web do Lightning Gerar documento. Adicione o componente a uma página de registro do Lightning para gerar e anexar documentos do Microsoft Word, Microsoft PowerPoint e PDF. Simplifique a configuração, remova as dependências de licenciamento do OmniStudio e estenda a geração de documentos para mais casos de uso conduzidos por IU. Esse componente oferece suporte à mesclagem de até 10 arquivos PDF.

* **Adicionar solicitações de processo de geração de documento a lotes ativos**
  Adicione solicitações de Processo de geração de documento (DGP) a um Processo em lote de geração de documento (DGBP) mesmo após a execução do lote. Continue atualizando os lotes no status Novo, Em andamento ou Em fila sem esperar a conclusão dos lotes. Esse aprimoramento fornece flexibilidade para cargas de trabalho grandes ou em andamento e reduz a exigência de recriar lotes. Não é possível atualizar um DGBP com DGPs adicionais depois que o status do lote muda para concluído. Antes, você podia apenas atualizar lotes no novo estado.

* **Gerenciar cobranças com a assistência do funcionário de faturamento**
  Transforme as cobranças e as operações de faturamento usando o gerenciamento de cobranças de faturamento, agora disponível no Agente de assistência ao funcionário de faturamento. Identifique percepções de faturamento com base no histórico de pagamentos, disputas e saldos pendentes. Simplifique os resumos de integridade de faturamento de conta e obtenha recomendações para estratégias de redução com backup de dados personalizando o modelo de prompt global padrão.

* **Resolver consultas de faturamento com o agente de assistência de serviço de faturamento**
  Forneça o Agente de assistência de serviço de faturamento a clientes, parceiros e representantes de vendas. O agente lida com consultas de faturamento comuns, como verificar saldos da conta, verificar datas de pagamento futuras, acessar documentos de fatura e revisar planos de pagamento para faturas específicas. As equipes de suporte podem visualizar percepções financeiras em tempo real e detalhes de cobrança de fatura, o que reduz significativamente o volume de casos de faturamento.

* **Visualizar o impacto financeiro do uso do cliente com o agente de consumo**
  O Agente de consumo agora aplica taxas de excedentes a dados de uso e calcula um valor monetário em tempo real para os recursos sobreutilizados, ajudando os representantes de vendas a identificar oportunidades de alto valor. Use as informações para gerar uma cotação, que você pode revisar e revisar. Você não precisa mais converter manualmente unidades técnicas ou tokens em moeda.

> 📄 **Notas Completas:** consulte os detalhes completos na página do tópico [REVENUE](./releases/summer_26/revenue.md).
</details>

* 📄 **RU**: Acesse o arquivo de notas de versão em [./releases/summer_26/ru.md](./releases/summer_26/ru.md).
<details>
<summary><b>📄 SALES (Clique para expandir 37 alterações)</b></summary>

* **Aumentar a conversão de clientes potenciais com a disponibilidade de calendário de grupo**
  Torne mais fácil para um cliente potencial agendar uma reunião em um horário conveniente para ele habilitando o agendamento de grupo para o agente de Nutrição de lead e Geração de lead de entrada. Ao agendar uma reunião, os clientes potenciais visualizam todos os períodos disponíveis dos usuários do Inbox com um email conectado no grupo selecionado.

* **Alterar o comportamento do agente de fomento de lead e geração de lead de entrada mais rapidamente**
  Depois de configurar e ativar um agente de Geração de lead de entrada ou Nutrição de lead, talvez você queira fazer alterações a ele mais tarde. Para editar um agente existente, agora você pode criar uma nova versão do agente com as mesmas configurações ou atualizar uma versão existente.

* **Continuar engajamento de lead com transferência de agente**
  Garanta o engajamento contínuo com clientes potenciais automatizando as transferências de leads entre os agentes de vendas de Geração de lead de entrada e Orientação de leads. Clientes potenciais criados pelo agente de Geração de lead de entrada que não agendam uma reunião podem ser atribuídos automaticamente ao agente de Nutrição de leads para um acompanhamento mais rápido e maximizar as taxas de conversão.

* **Qualifique contatos e contas pessoais com Agentforce**
  Qualifique contatos e contas pessoais perfeitamente para criar um pipeline mais forte com o Agentforce para vendas. Esse aprimoramento permite que seu agente determine o quão adequado um cliente potencial está com base na conversa e em como ele atende ao seu Perfil de cliente (ICP) ideal. A qualificação ajuda os representantes de vendas a se concentrarem em negócios de alto potencial, melhorando a eficiência geral e as taxas de conversão.

* **Veja percepções mais detalhadas e acionáveis sobre a atividade do agente de fomento de leads**
  Na Central de controle do agente remodelada, os gerentes de vendas podem ver mais detalhes sobre a saúde geral, o desempenho e a atividade dos clientes potenciais da equipe e garantir que eles estejam progredindo sem problemas em seu funil. Acompanhe o alcance do cliente potencial dos agentes de Orientação de leads e monitore quantos leads, contatos ou contas pessoais foram atribuídos ao agente, quantos foram enviados por email, respondidos, agendados para uma reunião e muito mais.

* **Um novo conjunto de permissões foi adicionado ao grupo de conjuntos de permissões de usuário de Gerenciamento de vendas**
  O Grupo do conjunto de permissões do usuário de gerenciamento de vendas agora inclui o conjunto de permissões Gerenciar usuários de gerenciamento de vendas não medidos. Essa alteração simplifica a atribuição de permissão e reduz problemas de faturamento inesperados porque você não atribui mais manualmente a permissão de IA baseada em usuário não medido aos usuários.

* **Controlar quais campos recebem atualizações autônomas**
  Especifique os campos individuais que o agente de Gerenciamento de vendas pode atualizar em nome do vendedor modificando o fluxo Processar sugestões de atualização de campo. Dê ao seu agente a capacidade de atualizar determinados campos sozinho enquanto ele continua gerando sugestões para outros campos.

* **Obter resumos gerados por IA para seus negócios**
  Obtenha respostas rápidas e resumos sobre seus negócios sem pesquisar por emails ou transcrições de chamada. Use IA para acompanhar atividades recentes, identificar bloqueadores de negócios e se preparar para reuniões fazendo perguntas específicas ou usando botões sugeridos.

* **Gerenciar estratégia de vendas e atualizar registros diretamente no Gemini (beta)**
  Os vendedores podem pesquisar leads, criar planos de conta e atualizar registros do Salesforce, tudo desenvolvido com dados de CRM seguros, precisos e em tempo real enquanto trabalham no Gemini. O acesso a dados do Salesforce em tempo real no Gemini ajuda sua equipe a manter registros precisos e fechar negócios mais rapidamente.

* **Personalizar a pesquisa de conta de vendas com mapeamento de campo personalizado**
  Obtenha mais valor de seus avisos de Pesquisa de conta mapeando os resultados para campos de texto personalizados em Contas ou Planos de conta. Antes, a Pesquisa de conta salvava apenas os resultados em campos padrão do Salesforce. Agora, seus representantes podem preencher os campos exatos necessários para seus casos de uso de negócios exclusivos.

* **Impulsione a produtividade e a automação do CRM com o Einstein Conversation Insights que move dados para a Salesforce Platform**
  Estamos migrando dados do Einstein Conversation Insights (ECI) para a Salesforce Platform para todos os clientes ECI que não estão na plataforma. Com essa migração, seus dados de ECI, incluindo transcrições de chamada e percepções geradas por IA, são armazenados nativamente na Salesforce Platform. Processe suas transcrições rapidamente e use ferramentas de automação do CRM como Fluxo, Apex e Criador de prompts.

* **Usar transcrições de chamada de Gong**
  Agora você pode usar transcrições de chamadas de Gong com o Insights de conversas do Einstein e a IA do Salesforce. Crie um nível com resumos automáticos, um painel de sinais relevantes e percepções sobre as objeções do cliente, as próximas etapas e palavras-chave relevantes. Use transcrições de Gong com nossos agentes prontos para uso, como agente de Nutrição de leads, agente de Gerenciamento de vendas e em toda a plataforma.

* **Obter transcrições e recursos de ECI para reuniões presenciais**
  As reuniões presenciais não exigem mais anotações manuais. As equipes de vendas podem capturar reuniões presenciais em um dispositivo móvel e processá-las com o Einstein Conversation Insights (ECI). Evite a entrada manual de dados e foque seu cliente com uma transcrição de IA móvel segura e confidencial.

* **Dados do Engajamento de vendas agora são nativos da Salesforce Platform**
  As métricas do Engajamento de vendas para novos clientes são armazenadas nativamente na Salesforce Platform. Para clientes atuais, a migração de dados está agendada para começar em junho. Com essa alteração, o painel Desempenho do Engajamento de vendas será descontinuado em outubro. As métricas são mostradas em um relatório personalizado.

* **O Centro de prospecção está agendado para descontinuação**
  A descontinuação do Centro de prospecção está agendada para 1o de abril de 2026.

* **Identificar e gerenciar contatos ativos na Inspeção do pipeline**
  Identifique lacunas da parte interessada e concentre-se em negócios que precisam de mais atenção vendo quais contatos estão ativamente engajados em um negócio. Localize a nova coluna Contatos para ver uma contagem de pessoas envolvidas em atividades, como emails e reuniões, nos últimos 30 dias.

* **Medir rapidamente a integridade do relacionamento na Inspeção do pipeline**
  Dê aos seus vendedores a capacidade de avaliar os níveis de engajamento sem rolar pela linha do tempo da atividade. A Inspeção do pipeline agora inclui uma coluna Atividade com um mapa de calor que rastreia atividades de entrada e saída, como chamadas de voz, videochamadas, eventos e emails, em um período de 30 dias.

* **Salesforce Spiff**
  Descubra os aprimoramentos mais recentes que melhoram suas experiências de gerenciamento de compensação de incentivo.

* **Personalizar a otimização de rota com perfis de roteamento avançado**
  Maximize a produtividade representativa de campo personalizando as restrições e penalidades usadas pelo mecanismo de roteamento. Em vez de uma abordagem adequada para todos, os administradores agora podem criar perfis que priorizam KPIs de negócios específicos, como minimizar o tempo de deslocamento ou maximizar o tempo na loja. Essa flexibilidade reduz os custos operacionais e garante que as contas de alta prioridade recebam a atenção necessária.

* **Trabalhe mais rapidamente com uma interface de planejamento de território modernizada**
  Experimente um design mais intuitivo e consistente no Planejamento de vendas que simplifica seus fluxos de trabalho diários. Os padrões de design modernizados reduzem cliques para ações-chave, como atribuir e bloquear unidades a áreas específicas. Simplifique seus alinhamentos de território e gerencie conjuntos de dados complexos com maior velocidade.

* **Evite conflitos de regra com a visibilidade de regra de segmento aprimorada**
  Garanta alinhamentos de território precisos visualizando critérios de segmento e regras herdadas diretamente na interface de planejamento. Essa atualização detecta regras de segmento pai e sinaliza conflitos de atribuição em nível de área no cabeçalho, permitindo que você resolva sobreposições antes que elas afetem seus dados.

* **Diferenciar metas de vendas com metas de moeda e quantidade**
  Obtenha flexibilidade em seu processo de planejamento definindo se as metas são baseadas em moeda ou quantidade. Estilize metas para refletir métricas específicas, como crescimento de receita na moeda padrão ou contagens de unidades para novos logotipos. Isso garante que suas metas sejam apresentadas de maneira clara e precisa em todas as visualizações do Planejamento de vendas.

* **Verificar a propriedade do seu domínio de email**
  Para evitar interrupções nos emails enviados do Salesforce, verifique os domínios de sua propriedade com uma chave DomainKeys Identified Mail (DKIM) ou um domínio de email autorizado. Como parte de nossos esforços contínuos para reforçar a segurança de nossos serviços de email, a verificação de domínio de email agora é obrigatória. O Salesforce não entrega mais emails de domínios não verificados, mesmo que o endereço de email esteja verificado.

* **Manter o fluxo de email para usuários com domínios não verificados**
  Permita que usuários cujos domínios de email você não possa verificar, como usuários com endereços de email públicos, consultores e usuários do site, enviem emails do Salesforce. Com seu endereço de email substituto, o nome de exibição do usuário permanece inalterado, mas o endereço De usa email@UniqueId.sfcustomeremail.com, em que UniqueId é seu ID da organização ou ID do site do Experience Cloud. Essa opção também se aplica a emails gerados pelo sistema e emails enviados por meio de contas de email compartilhadas com um domínio não verificado.

* **Notificar usuários sobre domínios de email não verificados**
  Como parte do requisito de verificação de domínio de email, o Salesforce envia notificações por email a usuários cujos endereços de email usam um domínio não verificado. Os usuários receberão uma notificação se emails enviados recentemente do Salesforce não tiverem sido entregues ou se não puderem enviar email do Salesforce quando a verificação de domínio de email for imposta. Para controlar se o Salesforce enviará um desses emails quando sua organização receber a versão Summer '26, atualize uma configuração de Capacidade de entrega.

* **Verificar o status de verificação do seu domínio**
  Para evitar falhas de entrega de email para emails enviados do Salesforce, verifique o status de verificação do seu domínio. O Salesforce agora envia emails apenas de domínios verificados.

* **Adote domínios de email autorizados (atualização de versão)**
  Se você já trabalhou com o Suporte ao cliente da Salesforce para desabilitar verificações de alteração de email, configure os domínios de email autorizados. A Salesforce está descontinuando o processo de isenção existente para desabilitar esse recurso, e os domínios de email autorizados oferecem o mesmo benefício. Disponível inicialmente na versão Spring '26, essa atualização é imposta na versão Winter '27.

* **Assinaturas DKIM protegem o cabeçalho de resposta**
  Quando você assina o email enviado pelo Salesforce com uma chave de Email identificado por DomainKeys (DKIM), a configuração de assinatura agora inclui o cabeçalho Responder a. Para proteger contra o sequestro de conversas, essa alteração impede a modificação do endereço Responder a durante a entrega. Se você usar chaves DKIM, receberá esse benefício automaticamente. Caso contrário, configure chaves DKIM para assinar emails enviados pelo Salesforce.

* **Atualize a Captura de atividades do Einstein e migre email antes da atualização automática**
  Atualize a Captura de atividades do Einstein e migre emails capturados anteriormente para dados de atividade do Salesforce antes da migração automática. Quando você atualiza e migra seu email, todos os emails novos e capturados anteriormente são sincronizados, armazenados e estão disponíveis para ferramentas e operações de plataforma. Se você não concluir o processo, atualizaremos automaticamente a Captura de atividades do Einstein e migraremos seu email.

* **Atualize o Microsoft 365 Authentication na Captura de atividades do Einstein para o Microsoft Graph**
  Faça a transição da autenticação do Microsoft Office 365 da Captura de atividades do Einstein para o Microsoft Graph até 3 de agosto de 2026, para manter sua sincronização de dados sem interrupções quando a Microsoft descontinuar o Exchange Web Services (EWS) em outubro de 2026. O Microsoft Graph é o novo padrão seguro e escalável para autenticação. Notificações proativas e uma ferramenta de clique único facilitam o processo de atualização.

* **Dados de evento agora são armazenados na Salesforce Platform**
  Os dados de evento sincronizados por meio da Captura de atividades do Einstein agora são armazenados na plataforma. Essa atualização é automática e não requer nenhuma ação da sua parte. Convidados para reunião incluídos em eventos anteriores que não têm um registro de contato, lead ou usuário não aparecem mais no Resumo da reunião. No entanto, convidados sem registros incluídos em eventos futuros aparecem no Resumo da reunião. Além disso, usuários fora de uma configuração de Captura de atividades do Einstein não veem mais dados de evento na linha do tempo de atividade. Se você mover esses usuários para uma configuração, os dados dos 180 dias anteriores preencherão a linha do tempo.

* **Prepare-se para a descontinuação de relatórios do Activity 360, métricas de atividade e painéis do Analytics de atividades**
  Antes da descontinuação dessas ferramentas, recomendamos ativar Sincronizar email como atividade do Salesforce para a Captura de atividades do Einstein e configurar relatórios para explorar dados capturados de email.

* **Migrar do Lightning Sync com os Serviços da Web do Microsoft® Exchange para a Captura de atividades do Einstein antes de agosto de 2026**
  A Microsoft anunciou a descontinuação do Exchange Web Services (EWS) para o Microsoft Office 365 a partir de outubro de 2026. As configurações do Lightning Sync que usam o EWS não capturarão nem sincronizarão dados após essa descontinuação. Para evitar interrupções de serviço, use a ferramenta de migração Lightning Sync para migrar para a Captura de atividades do Einstein e atualizar para o método de autenticação do Microsoft Graph antes de agosto de 2026.

* **Prepare-se para a descontinuação do Lightning Sync e migre para a Captura de atividades do Einstein**
  Na versão Winter '21, anunciamos que o Lightning Sync não estava mais disponível em novas organizações. Se você usar o Lightning Sync, migre para a Captura de atividades do Einstein para continuar sincronizando contatos e eventos entre aplicativos Microsoft® ou Google e o Salesforce. Se você tiver o Lightning Sync com o Microsoft Office 365 e usar o Exchange Web Service como método de autenticação, faça o upgrade até agosto de 2026 para evitar interrupções. Todas as outras integrações do Lightning Sync devem ser migradas antes da descontinuação do Lightning Sync em abril de 2027.

* **O Salesforce para Outlook será descontinuado em dezembro de 2027**
  Para a Integração ao Microsoft Outlook mais recente, recomendamos migrar para os produtos da próxima geração: a Integração ao Outlook e a Captura de atividades do Einstein. Esses produtos substituem os recursos do Salesforce para Outlook e dão aos usuários novas capacidades. Continuamos introduzindo aprimoramentos para esses produtos a cada versão.

* **Acesse o Agentforce a partir da sua integração com o Outlook**
  Aproveite o poder do Agentforce diretamente da sua integração com o Outlook para se preparar para reuniões, resumir registros e acionar ações personalizadas.

* **O Salesforce para Salesforce está sendo descontinuado (atualização de versão)**
  O Salesforce para Salesforce será descontinuado na versão Spring '27. O Salesforce tem soluções mais eficientes e integradas alinhadas às necessidades de negócios modernas. Para evitar interrupções quando o Salesforce encerrar o suporte para o produto Salesforce para Salesforce, migre suas integrações para uma destas soluções recomendadas: Partner Cloud, Data Cloud One, MuleSoft Anypoint ou MuleSoft para Fluxo.

> 📄 **Notas Completas:** consulte os detalhes completos na página do tópico [SALES](./releases/summer_26/sales.md).
</details>

<details>
<summary><b>📄 SECURITY (Clique para expandir 32 alterações)</b></summary>

* **Revisão da integridade de segurança**
  Gere relatórios de postura de segurança sob demanda e obtenha orientação de remediação passo a passo com o agente de avaliações de saúde. Avalie sua organização em relação às práticas recomendadas de segurança do Salesforce em autenticação, permissões, segurança de dados, configurações de API e conformidade. Faça perguntas sobre descobertas específicas, obtenha orientação de remediação e acompanhe o progresso entre as verificações.

* **Revisar e cumprir os requisitos de segurança novos e futuros**
  Para proteger contra ameaças à cibersegurança em evolução, o Salesforce reforça os controles de segurança. O Salesforce exige a verificação de domínio de email para enviar email. A partir de junho de 2026, o Salesforce impõe outros controles, incluindo autenticação multifator (MFA) para todos os usuários, MFA resistente a phishing para administradores do Salesforce e restrições de endereço IP de login. E na versão Winter '27, o Salesforce descontinua o fluxo de nome de usuário e senha do OAuth 2.0 para aplicativos conectados.

* **Adote a Salesforce Edge Network para seu domínio**
  Para reforçar a segurança, o Salesforce exige que você encaminhe seus URLs de domínio pela Salesforce Edge Network.

* **Visualizar valores de referência de classe de contexto de autenticação (ACR) no histórico de login e eventos de login**
  Agora você pode usar o histórico de login e os eventos de login para ver os valores de Referência de classe de contexto de autenticação (ACR) enviados pelo provedor de identidade de Single Sign On (SSO). Use essas informações para determinar se seu provedor de identidade usa um método de autenticação forte ou fraco. Logins de SSO com valores de ACR fortes podem ignorar a ativação do dispositivo.

* **Descontinuação do fluxo de nome de usuário e senha do OAuth 2.0 para aplicativos conectados (atualização de versão)**
  Na versão Winter '27, deixaremos de dar suporte ao fluxo de nome de usuário e senha do OAuth 2.0 para aplicativos conectados. Essa atualização interromperá todas as integrações de aplicativo conectado que usam esse fluxo. Para maior segurança, atualize suas integrações para usar o fluxo de servidor da Web OAuth 2.0 ou o fluxo de credenciais do cliente OAuth 2.0.

* **Migrar para uma estrutura SAML de ajustes múltiplos (atualização da versão)**
  Se você visualizar essa atualização de versão, sua instância do Salesforce estará usando nossa estrutura SAML de ajustes únicos original, que oferece suporte a Single Sign On (SSO) com apenas um provedor de identidade. Estamos lhe dando um lembrete final de que, com a versão Summer '26, não oferecemos mais suporte à estrutura SAML de ajustes únicos. Para garantir que suas configurações de SSO não falhem, migre para nossa estrutura SAML de configuração múltipla mais recente, que oferece suporte a SSO com vários provedores de identidade, em vez de apenas um. Se você não migrar, suas configurações de SSO SAML deixarão de funcionar quando essa atualização de versão for imposta na versão Summer '26.

* **O logon único triplo DES para SAML não tem mais suporte**
  O algoritmo Triple Data Encryption Standard (Triple DES) não tem mais suporte para Single Sign On (SSO) SAML. Se sua configuração ainda usa o DES triplo, os usuários não poderão fazer login por meio de SSO. Esta alteração se aplica a todas as configurações de SSO que usam o algoritmo Triple DES, esteja você usando o Salesforce como provedor de identidade ou como provedor de serviços. Para melhorar a segurança, use os algoritmos do Padrão avançado de criptografia (AES), AES 128 ou AES 256, em vez disso.

* **Descontinuação do provedor de autenticação Gerenciado pelo Salesforce X (antigo Twitter) (atualização de versão)**
  O aplicativo gerenciado pelo Salesforce para o provedor de autenticação X (antigo Twitter) está sendo descontinuado. Essa atualização interrompe qualquer configuração de Single Sign On (SSO) que use o aplicativo X gerenciado pelo Salesforce. Para evitar interrupções, crie um aplicativo X personalizado e atualize suas configurações de SSO.

* **Rótulos da IU do provedor de autenticação são atualizados**
  Para melhorar a usabilidade, alteramos o nome de alguns rótulos nas páginas do provedor de autenticação em Configuração.

* **URL de retorno de chamada do provedor de autenticação externo usa Meu domínio**
  Quando você cria um provedor de identidade de autenticação externo, um URL de retorno é gerado para o sistema externo redirecionar de volta para ele. Agora, o URL de retorno é criado usando o nome do Meu domínio da organização. Em vez do URL https://login.salesforce.com/services/extidp/callback, o URL de retorno agora é https://<my_domain_name>/services/extidp/callback. Se o provedor de identidade de autenticação externo estiver associado a um pacote gerenciado, o URL de retorno será criado usando o namespace do pacote.

* **Novos sinais para pontuações de verificação de integridade**
  A Verificação de integridade de segurança tem vários novos sinais que podem afetar sua pontuação atual. Atualize suas linhas de base personalizadas com esses novos sinais e solucione todas as configurações fora de conformidade para manter sua segurança.

* **Notificações semanais por padrão**
  Os administradores agora recebem notificações semanais de Verificação de integridade do lançamento para novas organizações de produção. Esses alertas mantêm os administradores informados sem a necessidade de monitoramento manual. Para recusar, desative manualmente as notificações por meio das configurações de Verificação de integridade de segurança em Configuração.

* **Visualizar e exportar fragmentos de dados confidenciais nos resultados da varredura de detecção de dados**
  Identifique rapidamente os tipos de dados confidenciais em seus registros visualizando um "extrato" de fragmentos de "valor encontrado" diretamente nos resultados da verificação. Desfrute de uma revisão de dados mais fácil com controles de segurança importantes.

* **Ler campos criptografados para dados confidenciais na Detecção de dados**
  Agora, você pode ampliar seu alcance de privacidade de dados lendo campos baseados em texto criptografados. A Detecção de dados oferece suporte à leitura de texto, área de texto longo, área de rich text, campos de área de texto e texto (criptografado) com a Criptografia em nível de campo ou a Criptografia clássica. A leitura de campos criptografados leva mais tempo. Se você incluir campos criptografados em sua verificação, seu tempo total de verificação poderá aumentar aproximadamente um e meio.

* **Habilitar a varredura precisa para palavras-chave e frases exatas com a Detecção de dados**
  Agora você pode estender os recursos de Detecção de dados para leitura precisa de palavras-chave e frases, aprimorando a qualidade e a conformidade dos dados do Salesforce. Você pode definir um dicionário de até 1.000 termos específicos, como termos de marketing proibidos ou códigos internos proprietários. Verifique com eficiência milhões de registros entre objetos e campos detectando correspondências exatas. Melhore significativamente a adesão à conformidade e a moderação de conteúdo usando um método eficiente para aplicar políticas de conteúdo e analisar resultados detalhados em um painel ou por meio da exportação.

* **Automatizar o monitoramento de dados confidenciais com verificações recorrentes na Detecção de dados**
  Automatize o monitoramento de dados confidenciais para conformidade contínua. Defina intervalos de recorrência semanais, mensais ou anuais usando o fuso horário do criador da agenda. Sempre que uma verificação recorrente é executada, ela usa a versão mais recente da política associada. Todas as agendas de verificação existentes podem ser facilmente visualizadas, editadas ou desativadas.

* **Obtenha percepções mais profundas com eventos de consulta do GraphQL**
  Os arquivos de log de evento de consulta do GraphQL contêm informações sobre consultas executadas, incluindo o tempo total de execução, o número de invocações e quaisquer erros relatados. Esses dados de evento melhoram a capacidade de observação do administrador, aprimorando o desempenho e a segurança da organização.

* **Permissão Modificar política de segurança da transação**
  A nova permissão Modificar política de segurança da transação (TSP) fornece uma camada extra de controle e segurança para suas políticas. Essa permissão é necessária para criar, excluir e atualizar TSPs e oferece suporte à Autenticação em etapas para segurança adicional. Usuários com apenas a permissão Personalizar aplicativo agora estão restritos ao acesso somente visualização.

* **Novos IDs de perfil e papel**
  ID do perfil e ID do papel foram adicionados como novos campos a todos os eventos em tempo real. Esse aprimoramento oferece percepções do usuário mais profundas, permitindo que você crie Políticas de segurança da transação (TSPs) de modo mais rápido e declarativo.

* **Política de segurança da transação de exportação de relatório**
  Uma nova Política de segurança da transação (TSP) está disponível para aprimorar a proteção de dados em todas as organizações. Essa política monitora eventos de relatório e aciona a Autenticação avançada se um usuário tentar exportar mais de 10 mil registros por meio da interface do usuário.

* **Alteração no requisito de notificação de TSP**
  O requisito para um usuário de notificação em Políticas de segurança da transação (TSPs) agora é opcional. Apólices existentes não são aplicadas.

* **Monitore alterações administrativas em perfis com políticas de segurança da transação**
  Mantenha uma estrutura de auditoria robusta e monitore privilégios de segurança elevados usando Políticas de segurança da transação. Gere eventos de rastreamento e bloqueie alterações não autorizadas em tempo real quando os administradores do Salesforce modificam ou criam perfis de usuário com permissões críticas. Acompanhe a remoção específica da permissão de isenção de TransactionSecurity.

* **Downloads do Explorador de histórico de campo**
  Os downloads estão sendo adicionados à página do Explorador de histórico de campo (FHE). Isso permite que os usuários façam download de alterações de histórico de campo para qualquer registro diretamente da página para casos de uso de auditoria.

* **Gerenciar criptografia em nível de campo com uma IU atualizada**
  Agora você pode configurar e manter sua política de Criptografia em nível de campo (FLE) diretamente no aplicativo Shield. A nova IU facilita a revisão de bloqueadores de criptografia, a ativação ou desativação da criptografia para campos e a atualização de esquemas de criptografia. As UIs legadas para gerenciar o FLE ainda estão disponíveis em Configuração e no pacote gerenciado Extensão do Shield.

* **Prepare-se para uma experiência de criptografia em nível de campo consolidado na versão Winter '27**
  A Salesforce planeja descontinuar a experiência legada de Criptografia em nível de campo (FLE) da Configuração na versão Winter '27. Quando essa alteração ocorrer, os usuários serão redirecionados para a nova experiência de FLE no aplicativo Shield, que estará disponível a partir da versão Summer '26. Sua política de FLE existente e todas as funcionalidades relacionadas serão preservadas enquanto implementarmos esses aprimoramentos da IU.

* **Limite de registro maior para sincronização de criptografia**
  Agora você pode executar criptografia de segundo plano de autoatendimento em objetos contendo até 40 milhões de registros. O limite maior significa que você pode esperar menos atrasos ao sincronizar dados com sua chave ativa.

* **Novas métricas de alerta**
  Alertas da Central de segurança têm várias novas métricas para aprimorar a postura de segurança da sua organização.

* **Focar investigações de segurança com a triagem de anomalia (beta)**
  Veja anomalias de segurança relacionadas consolidadas em uma única investigação. O agente de segurança correlaciona anomalias da mesma sessão do usuário ou atividade do usuário em 24 horas, criando uma investigação apenas quando identifica uma ameaça exclusiva. Essa abordagem reduz a fadiga do alerta e direciona sua equipe de segurança para o incidente principal.

* **Seguir linhas do tempo do incidente para investigações (beta)**
  Entenda todo o contexto de um incidente de segurança vendo atividades relacionadas em uma Linha do tempo de incidente. O agente de segurança analisa os registros de Monitoramento de evento para fornecer uma visão completa do que aconteceu antes, durante e após a detecção de uma anomalia. Esse contexto elimina a correlação de dados manual e acelera o processo de investigação.

* **Obter planos de remediação para incidentes de segurança (beta)**
  Veja a orientação passo a passo padronizada para resolver incidentes de segurança após a investigação. O agente de segurança fornece um plano de remediação personalizado para a anomalia detectada, guiando você pelas etapas necessárias para conter a ameaça e reduzir o risco de que ela ocorra novamente.

* **Seguir a orientação de tamanho para cabeçalhos de CSP**
  Proporcione uma experiência confiável quando sites externos apresentarem conteúdo da sua organização em um iFrame. Foque um cabeçalho de Política de segurança de conteúdo (CSP) abaixo de 12 KB para reduzir falhas causadas por limites de infraestrutura no tamanho do cabeçalho HTTP. Os clientes relatam problemas conforme os cabeçalhos se aproximam de 16 KB, e o processamento de terceiros pode aumentar o tamanho do cabeçalho.

* **Identificar e remover URLs confiáveis malformados**
  O Salesforce agora exclui URLs malformados dos cabeçalhos HTTP da Política de segurança de conteúdo (CSP) gerados. Para manter sua lista de URLs confiáveis precisa, remova todas as entradas malformadas.

> 📄 **Notas Completas:** consulte os detalhes completos na página do tópico [SECURITY](./releases/summer_26/security.md).
</details>

<details>
<summary><b>📄 SERVICE (Clique para expandir 153 alterações)</b></summary>

* **Notas de versão mensal do serviço**
  Aprenda sobre os recursos mais recentes de Serviço. Os recursos de serviço são lançados com frequência mensal, portanto, verifique aqui as informações mais recentes.

* **Transfira suas conversas do agente do Agentforce do Salesforce Voice para um representante de serviço nas centrais de contato do Agentforce**
  Garanta que seus clientes sempre recebam a ajuda necessária escalando problemas complexos de um agente de IA para um representante de serviço em canais do Salesforce Voice. Usando o tópico Escalonamento e um fluxo do Omni-Channel de saída, seus agentes do Agentforce agora podem rotear facilmente conversas do Salesforce Voice junto com seu histórico completo para o destino certo. As centrais de contato Agentforce no modelo Salesforce Voice (Telefonia nativa) agora oferecem suporte total a esses recursos de escalação.

* **Melhore a experiência do representante evitando chamadas antes que os representantes estejam prontos**
  Impeça que o Omni-Channel atribua trabalho a seus representantes de serviço antes que o conector de telefonia seja totalmente carregado. A Verificação de prontidão do conector de voz informa aos representantes que o Salesforce ainda está trabalhando para disponibilizá-los e os impede de receber trabalho. Quando o login único (SSO) estiver concluído e o conector do Voice estiver pronto, as chamadas serão implantadas.

* **Fornecer um serviço melhor com retornos de chamada agendados flexíveis**
  Dê aos clientes mais controle permitindo que eles solicitem um retorno de chamada em um horário que funcione para eles. Antes, no Salesforce Voice (Telefonia nativa) e em centrais de contato que roteiam chamadas com roteamento unificado do Omni-Channel, os retornos de chamada eram roteados com base apenas na disponibilidade do representante. Agora você pode definir um comportamento de retorno de chamada e tempo específico por meio de sua configuração de IVR ou lógica de roteamento personalizada.

* **Visualizar solicitação de retorno antes de discar**
  Os representantes agora podem visualizar uma solicitação de retorno antes de fazer a chamada de saída. Quando uma solicitação de retorno de chamada é roteada para os representantes, eles podem revisar os detalhes do contato primeiro e, em seguida, iniciar a chamada usando o recurso Clique para discar ou transferir a chamada para um representante diferente. Esse recurso dá aos representantes tempo e contexto antes de se conectarem ao cliente.

* **Gerencie chamadas de voz com o fone de ouvido em Centros de contato do Agentforce facilmente**
  Os representantes podem gerenciar chamadas de voz de modo mais eficiente e conveniente usando um fone de ouvido para aceitar, recusar, silenciar, manter e encerrar chamadas. Esse recurso oferece suporte a vários fones de ouvido, como Plantronics, Sennheiser, Jabra, Yealink e VBeT. Antes, com suporte no Salesforce Voice com provedores de telefonia, esse recurso agora tem suporte total no Salesforce Voice (telefonia nativa).

* **Mantenha a continuidade dos negócios com a portabilidade de número do Voice fácil**
  Mantenha sua identidade comercial estabelecida movendo números de telefone existentes diretamente para o Salesforce. Envie uma Carta de autorização e a documentação necessária para agendar sua entrada para uma data e hora específicas. Essa flexibilidade garante que sua configuração de telefonia se alinhe à linha do tempo da migração sem interrupções de serviço.

* **Aumentar a resolução da primeira chamada transferindo chamadas de saída**
  Proporcione uma experiência de atendimento ao cliente aprimorada permitindo que os representantes passem facilmente as conversas de saída. Os representantes de serviço podem mover chamadas de saída ativas para supervisores ou outros departamentos usando transferências quentes ou frias. Resolver consultas em uma única sessão proativa aumenta a eficiência da equipe e mantém uma imagem de marca profissional.

* **Expanda as comunicações globais com idiomas expandidos de IVR e perfis de voz**
  Dê suporte aos chamadores no idioma local com uma biblioteca expandida de 11 novos dialetos regionais: inglês (Reino Unido), alemão (Alemanha), francês (França), espanhol (Espanha), italiano (Itália), holandês (Países Baixos), português (UE), japonês (Japão), hindi (Índia), inglês (Austrália) e finlandês (Finlândia). Acesse perfis de voz baseados em gênero e ferramentas de configuração simplificadas para proporcionar interações personalizadas de texto para voz. Os perfis padrão automatizados garantem que os chamadores sempre escutem uma voz natural, mesmo que um perfil específico não seja selecionado manualmente.

* **Simplifique fluxos de IVR com a seleção de mídia baseada em variável**
  Crie jornadas de IVR mais flexíveis permitindo que o nó Aviso de reprodução busque ativos de mídia com base em valores de variável em tempo real. Quer você esteja alternando avisos para uma campanha de marketing específica ou um dialet local, um só nó agora pode lidar com vários resultados de áudio. Essa abordagem elimina ramificações redundantes, facilitando o gerenciamento e a escala dos fluxos de IVR em diferentes segmentos do cliente.

* **Desfrute de chamadas ininterruptas com a restauração automática de sessão**
  Proteja conversas ativas contra recarregamentos acidentais do navegador e desvios de rede inesperados. Os representantes de serviço recuperam as chamadas ativas, o status de presença e as sessões de softphone sem precisar fazer login novamente. Antes, caídas súbitas exigiam que os representantes se autentiquem manualmente novamente, mas agora as sessões são restauradas em segundos para manter as operações funcionando sem problemas

* **Gerenciar assinaturas de número com métricas de uso detalhadas**
  Visualize direitos baseados em uso para assinaturas de número de voz dos EUA e do Canadá para gerenciar suas operações da central de contato com mais eficiência. A seção Direitos baseados em uso em Informações sobre a empresa agora reflete os números consumidos para licenças de código longo e de código livre depois de serem vinculados a um canal de voz. Use essas percepções para informar o momento da aquisição e garantir que sua central de contato tenha os recursos necessários para escala.

* **Vincule chamadas de voz aos registros de origem automaticamente nas centrais de contato Agentforce**
  Quando você inicia uma chamada de saída usando o recurso Clique para discar de um objeto personalizado ou de um objeto padrão, como Conta, Caso, Contato, Lead, CollectionPlan, ContactRequest, WorkOrder ou Oportunidade, o registro VoiceCall resultante estabelece automaticamente um relacionamento de pesquisa com o registro de origem. Essa alteração elimina a necessidade de vinculação manual e reduz a necessidade de personalização com fluxos ou acionadores do Apex. Antes disponível apenas para o Salesforce Voice com provedores de telefonia, essa vinculação automática agora tem suporte total em Centros de contato Agentforce.

* **Vincular chamadas de voz a ordens de trabalho diretamente**
  O campo RelatedId no objeto VoiceCall agora oferece suporte a WorkOrder, de modo que os representantes podem vincular diretamente chamadas de voz a ordens de trabalho sem nenhum desenvolvimento personalizado. Isso proporciona aos representantes o histórico completo de chamadas diretamente do registro WorkOrder, economizando tempo e esforço manual.

* **Aprimorar o desempenho da transcrição de voz**
  Aumente a precisão da transcrição de chamada, suporte às necessidades de idioma específicas dos negócios e reduza a latência de transcrição selecionando um modelo de fala para texto preferencial no nível da organização. Ajude as equipes de suporte a fornecer suporte multilíngue aprimorado e uma experiência de serviço mais confiável.

* **Gerenciar áudio de telefonia diretamente no Salesforce**
  Simplifique a administração de telefonia hospedando arquivos .mp3 e .wav no Salesforce para implantação instantânea em avisos de IVR e anúncios de fila. Proporcione uma experiência de chamador consistente em todos os fluxos de roteamento com um repositório unificado que fornece aos administradores validação de arquivo em tempo real.

* **Crie relacionamentos mais fortes com o cliente com o roteamento do último representante de suporte**
  Reforce os relacionamentos com o cliente reconectando os chamadores com o último representante de serviço com quem eles conversaram para preservar o contexto e reduzir as conversas repetidas. Além disso, ofereça um retorno com o mesmo representante se estiver indisponível. Melhore a resolução da primeira chamada e reduza os tempos de atendimento encaminhando chamadas de entrada para o mesmo representante usando um fluxo. Forneça suporte mais rápido e personalizado enquanto reduz o esforço desnecessário para clientes e representantes.

* **Acelere o contato com o cliente proativo com chamada de saída automatizada**
  Entre em contato com os clientes antes de eles ligarem iniciando chamadas de voz de saída automatizadas diretamente de fluxos. Acione lembretes de compromisso, pesquisas, atualizações de entrega, acompanhamentos de pagamento e conversas de serviço conduzidas por IA sem ferramentas de terceiros ou integrações personalizadas. Configure o ID do chamador, inicie chamadas instantaneamente e a próxima etapa do chamador por meio de avisos de IVR, entrada do cliente, conversas do agente de serviço Agentforce ou conclusão automática da chamada. Melhore as taxas de resposta e proporcione interações com o cliente mais oportunas e personalizadas enquanto reduz chamadas manuais. Reforce a eficiência do serviço, reduza o volume de chamadas recebidas e crie o Trust do cliente por meio de engajamento consistente e automatizado.

* **Priorizar chamadas urgentes do cliente com roteamento baseado em SLA**
  Melhore o desempenho em nível de serviço roteando chamadas de voz com base em quando elas devem ser aceitas. Configure datas de vencimento de aceitação em um fluxo para priorizar chamadas urgentes em relação a chamadas mais antigas com prazos posteriores. Dê aos supervisores mais visibilidade de chamadas que se aproximam ou violam metas de SLA por meio de visualizações e relatórios de pendências integrados. Aumente a velocidade de resposta, reforce a satisfação do cliente e proporcione experiências de serviço mais consistentes alinhando o roteamento às prioridades de negócios.

* **Personalizar o Salesforce Voice usando a API do kit de ferramentas**
  O recurso da API do kit de ferramentas fornece APIs, métodos e eventos para criar e personalizar componentes habilitados para voz usando o LWC ou o Aura. Você pode controlar ações de chamada, assinar eventos de ciclo de vida de telefonia e acessar dados de chamada em tempo real.

* **Acompanhe seus modelos de telefonia com novos nomes do Salesforce Voice**
  Conforme o Service Cloud Voice se torna o Salesforce Voice para aproveitar as mais recentes inovações e recursos de IA, também estamos renomeando seus modelos de telefonia subjacentes. Agrupamos esses modelos como o Salesforce Voice com provedores de telefonia para distingui-los do Salesforce Voice nativo. Os nomes de modelo de telefonia atualizados aparecem automaticamente para você e fornecem uma experiência de terminologia consistente em toda a sua configuração.

* **Acompanhe seus conjuntos de permissões e licenças com novos nomes do Salesforce Voice**
  Conforme o Service Cloud Voice se torna o Salesforce Voice para aproveitar as mais recentes inovações e recursos de IA, também estamos renomeando os conjuntos de permissões e as licenças do conjunto de permissões. Os nomes atualizados aparecem automaticamente para você e fornecem uma experiência de terminologia consistente em toda a sua configuração.

* **Melhore a segurança da central de contato com aplicativos cliente externos**
  Alinhe suas centrais de contato aos padrões de plataforma mais recentes usando Aplicativos cliente externos (ECA) para autenticação. Antes, o Salesforce usava Aplicativos conectados para lidar com o gerenciamento de identidade entre o Salesforce e o provedor de telefonia. Agora, novas centrais de contato usam uma ECA gerenciada, e as centrais de contato criadas manualmente usando um arquivo XML exigem que você crie uma ECA local. Suas centrais de contato preexistentes não são afetadas e continuam funcionando com segurança com suas configurações atuais do Aplicativo conectado.

* **Faça mais com o roteamento unificado usando retornos de chamada, Transferência para fluxo e API de chamada de rota do Voice**
  Aprimore o Salesforce Voice com Telefonia do parceiro com funcionalidades estendidas de Roteamento unificado. Agora você pode usar a API de chamada de voz de rota para tomar decisões de roteamento inteligente e transferir chamadas ativas diretamente para fluxos do Omni-Channel para mapeamento de destino dinâmico. Além disso, a nova API Solicitar retorno de chamada oferece aos clientes a opção de solicitar um retorno em vez de esperar em espera.

* **Simplifique a recuperação de desastres com a migração automatizada de status**
  Migre automaticamente os status do representante para uma central de contato de backup ao ativar a Recuperação de desastres para o Amazon Connect. Além disso, a ativação da recuperação de desastres é desabilitada até que sua replicação do Amazon Connect esteja concluída, permitindo uma transição contínua para a central de contato de backup.

* **Gerencie diretamente sua identidade do chamador com a atribuição de número de telefone autônomo**
  Seus representantes podem adquirir e atribuir números de telefone da empresa locais ou padrão a eles mesmos sem aguardar a assistência do administrador. Eles podem liberar um número de telefone e liberá-lo para outros quando ele não for mais necessário. Os representantes também têm a flexibilidade de alternar entre números com base nos requisitos de negócios específicos.

* **Registrar saudações de correio de voz personalizadas para chamadas de entrada**
  Proporcione experiências de chamada personalizadas com saudações de correio de voz pré-gravadas que são executadas quando seus representantes não conseguem atender a uma chamada de entrada. Os representantes podem registrar até dez saudações para cumprir requisitos específicos. Todas as mensagens deixadas pelos chamadores são armazenadas na caixa de correio de voz pessoal do representante para revisão a qualquer momento. Se seus representantes tiverem atribuído números de telefone a si mesmos, eles poderão vinculá-los a saudações de correio de voz específicas para fornecer a mensagem mais relevante.

* **Aumente a produtividade do representante com o Voicemail Drop para chamadas de saída**
  Quando uma chamada de saída chega ao correio de voz, seus representantes podem deixar uma mensagem pré-gravada e desconectar a chamada. Eles podem soltar uma gravação padrão ou selecionar entre várias opções para entregar a mensagem mais relevante. Conforme ele funciona em segundo plano, seus representantes podem ir para a próxima tarefa imediatamente, aumentando a produtividade.

* **Obter os aprimoramentos mais recentes à Central de contato do Amazon Connect**
  Atualize sua central de contato para a versão 21 para desbloquear os recursos mais recentes do Voice. Esta versão introduz uma lógica de nova tentativa robusta para lidar com a limitação de taxa perfeitamente, controles avançados para retornos de chamada agendados e geração de token de segurança dinâmica para transferências do Protocolo de início da sessão (SIP). Para testar as atualizações antes de elas ficarem ativas em produção, implante-as primeiro no seu sandbox.

* **Mantenha uma trilha de auditoria de alterações de registro de chamada de voz (piloto)**
  Rastreie alterações em campos no objeto VoiceCall. Selecione e monitore até 20 campos. Quando um campo rastreado muda, uma entrada de registro captura o valor antigo, o novo valor, o usuário que fez a alteração e a data e hora.

* **Melhorar a segurança para Telefonia do parceiro migrando para um aplicativo cliente externo**
  Aplicativos cliente externos (ECAs) são a próxima geração de aplicativos conectados, projetados para melhorar a segurança e lidar com problemas de distribuição e empacotamento. Embora os aplicativos conectados existentes para integrações do Salesforce Voice com Telefonia do parceiro continuem funcionando, você não poderá criar novos aplicativos conectados sem primeiro solicitar a capacidade do Suporte do Salesforce. Como a Salesforce planeja, por fim, substituir aplicativos conectados por ECAs, considere migrar para um aplicativo cliente externo para o Salesforce Voice com Telefonia do parceiro.

* **Rastrear o uso do modelo de email em registros de caso**
  Monitore a frequência e a última vez que os usuários aplicam modelos de email específicos. Agora, os campos Data e horas da última utilização são atualizados em modelos de email quando usados no compositor de email do Lightning em casos.

* **Crie agentes de serviço Agentforce melhores para email no novo Agentforce Builder**
  Crie agentes de serviço Agentforce inteligentes para email com maior controle e maior confiabilidade usando o novo Agentforce Builder. A plataforma introduz o Agent Script, uma nova linguagem de programação que combina instruções de linguagem natural com expressões de programação. Esse raciocínio híbrido lhe dá mais controle sobre o comportamento do agente. Tanto o Agentforce Builder legado quanto o novo Agentforce Builder funcionam na mesma organização. Você pode editar agentes criados no criador legado apenas no criador legado e pode editar agentes criados no novo criador apenas no novo criador.

* **Simplificar as permissões do Agentforce para serviço por email**
  O processo de configuração do Agentforce para serviço por email ficou mais simples agora que o requisito de permissão Personalizar aplicativo para o Usuário de caso automatizado em Configurações de suporte foi removido. Sua implementação agora é mais segura e fácil de gerenciar.

* **Migrar para o WhatsApp unificado mais rapidamente**
  Para reduzir o tempo de inatividade da migração de dois ou mais dias para menos de quatro horas, migre sua conta comercial do WhatsApp (WABA) primeiro para o WhatsApp unificado e escolha adicionar seu número de telefone mais tarde. Antes, você podia migrar sua WABA apenas com um número de telefone, o que estabeleceu um tempo de inatividade de 1 a 2 dias antes de migrar modelos.

* **Encerrar sessões de mensagens inativas automaticamente**
  Para limpar rapidamente as sessões com um usuário final ocioso, configure um canal de mensagens para encerrar ou desativar automaticamente e encerrar as sessões após um período especificado. Antes, você podia desativar sessões automaticamente em um canal, mas o encerramento automático não era uma opção.

* **Simplificar o gerenciamento de modelos do WhatsApp**
  Crie e gerencie modelos do WhatsApp de utilitários e de marketing diretamente no Salesforce. Agora você pode criar, editar, enviar para aprovação, publicar e excluir esses tipos de modelo no Criador de componentes de mensagens. Ao gerenciar modelos do WhatsApp diretamente no Salesforce, você economiza tempo e minimiza problemas de sincronização com sua Conta comercial do WhatsApp (WABA). Antes, você precisava criar os modelos do WhatsApp e gerenciá-los em sua conta comercial do WhatsApp e então importá-los para o Salesforce.

* **Permitir que os representantes de serviço visualizem a versão de conteúdo avançado de um componente de mensagens de notificação**
  Os modelos do WhatsApp (configurados como um componente de mensagens de notificação) agora renderizam conteúdo avançado completo no Console de serviço. Isso permite que os representantes de serviço vejam o cabeçalho (incluindo arquivos de mídia), o corpo, o rodapé e as opções de botão, fornecendo contexto valioso para o chat e reduzindo o tempo de processamento estendido que pode resultar de perguntas esclarecidas. Antes, os representantes podiam ver apenas o nome interno de um componente de notificação no Console de serviço.

* **Concluir o trabalho de encerramento após uma transferência**
  Dê aos seus representantes de serviço o tempo necessário para registrar notas ou atualizar registros após transferir uma conversa. Para permitir o Trabalho após a conversa (ACW) para transferências, configure o componente Conversa aprimorada para manter as guias de mensagens ativas após uma transferência, em vez de fechar automaticamente.

* **Gerar relatórios sobre sessões de mensagens relacionadas a um caso**
  Selecione Sessões de mensagens como um objeto relacionado no objeto Casos em um tipo de relatório personalizado. Antes, não era possível visualizar sessões de mensagens por caso usando um tipo de relatório personalizado.

* **Rastrear o tempo da primeira resposta do representante de serviço automaticamente**
  Elimine soluções alternativas complexas, mantenha os KPIs de satisfação do cliente e garanta a conformidade do SLA com uma nova métrica que captura exatamente o momento em que um representante de serviço envia sua primeira resposta em uma sessão de mensagens. O Tempo da primeira resposta do representante de serviço agora é um valor no campo MessagingSessionMetricType do objeto MessagingSessionMetrics. Antes, identificar o momento real em que um representante enviou sua primeira mensagem exigia um desenvolvimento complexo do LWC ou chamadas de API para o objeto ConversationEntry.

* **Usar novos campos de DMO de Engajamento de mensagens**
  Usuários do WhatsApp unificado podem acessar os seguintes novos campos no Objeto de modelo de dados (DMO) de engajamento de mensagens.

* **Prepare-se para alterações de nome de usuário do WhatsApp**
  Em breve, os usuários do WhatsApp poderão selecionar um nome de usuário e ocultar seu número de telefone. Esse recurso de privacidade da Meta é opcional, mas as empresas devem estar prontas para identificar e se comunicar com os usuários por meio de um novo identificador chamado ID de usuário no escopo de negócios (BSUID).

* **Canais do Facebook Messenger padrão deixarão de funcionar em junho**
  Se você ainda não atualizou seus canais do Facebook Messenger padrão para canais aprimorados, faça o upgrade agora para evitar uma interrupção de serviço. Esses canais, que foram descontinuados em 14 de fevereiro de 2026, deixarão de funcionar durante a semana de 1o de junho de 2026.

* **Canais de SMS padrão deixarão de funcionar em julho**
  Se você ainda não atualizou seus canais de SMS padrão para canais aprimorados, faça o upgrade agora para evitar uma interrupção de serviço. Esses canais, que foram descontinuados em 14 de fevereiro de 2026, deixarão de funcionar durante a semana de 1o de julho de 2026.

* **Encerrar sessões de mensagens abandonadas automaticamente**
  Libere a capacidade do representante e melhore a produtividade movendo automaticamente sessões de mensagens abandonadas de ativas ou em espera para inativas. Defina a duração do tempo limite nas configurações do seu canal de mensagens.

* **O Chat legado está sendo descontinuado**
  O chat legado está agendado para descontinuação em 14 de fevereiro de 2026 e está na unidade do modo de manutenção nesse momento. Você pode continuar usando o chat até essa data, mas recomendamos a transição para o Messaging no aplicativo e para Web para comunicação modernizada com o cliente. O Messaging oferece muitos dos recursos de chat que você adora, além de conversas assíncronas que podem ser selecionadas novamente a qualquer momento.

* **Liberar a capacidade do representante fechando o trabalho do agente de modo programático**
  Impeça que itens de trabalho sejam encravados e garanta que as conversas com o cliente sejam processadas prontamente usando uma API no lado do servidor para fechar itens de trabalho do agente em Traga seu próprio canal. Antes, o fechamento do trabalho do agente era possível apenas com mecanismos no lado do cliente. Essa nova API libera a capacidade do representante desativando sessões de mensagens ou ignorando o Trabalho após a conversa (ACW) se um representante perder a conexão ou fechar o navegador durante uma conversa.

* **Aumente a transparência com citações de resposta de IA**
  Crie Trust em respostas geradas por IA fornecendo referências de origem em suas mensagens de saída de Traga seu próprio canal. Os usuários finais do Messaging agora podem verificar as respostas do agente de serviço Agentforce com base em artigos do Knowledge ou outras fontes diretamente na sua interface do usuário personalizada. Com links de origem e deslocamentos de caracteres na carga útil da mensagem de saída, os parceiros podem renderizar marcadores em linha ou uma seção de origens dedicada.

* **Dê aos representantes tempo de trabalho após a conversa após uma transferência**
  Dê aos seus representantes de serviço o tempo necessário para registrar notas ou atualizar registros após transferir uma conversa. Para permitir o Trabalho após a conversa (ACW) para transferências, configure o componente Conversa aprimorada para manter as guias de mensagens ativas após uma transferência, em vez de fechar automaticamente.

* **Instalar soluções de configuração inicial predefinidas e acelerar a configuração de conformidade de TI**
  Acelere o tempo para o valor do Serviço de TI do Agentforce com configurações de práticas recomendadas que simplificam a configuração do sandbox no primeiro dia. Escolha entre uma solução padrão para automatizar a instalação de metadados e a habilitação de recursos ou use uma solução personalizada para implementar seletivamente recursos específicos personalizados para sua organização. Use o novo conjunto de recursos Acelerar a Trust com Risco e conformidade unificados para configurar facilmente os principais recursos de conformidade de TI, como Gerenciamento de risco, Gerenciamento de regulamentação, Controles de conformidade, Gerenciamento de apólice, Gerenciamento de evidência, Gerenciamento de problemas e Gerenciamento de apólice M365.

* **Objetos novos e alterados para o Serviço de TI do Agentforce**
  Faça mais com os objetos novos e alterados do Serviço de TI do Agentforce.

* **Acompanhe com precisão o inventário de hardware com locais baseados em ativos**
  Monitore seus dispositivos com base em estados de ciclo de vida específicos, em vez de uma única métrica de Quantidade disponível. Diferencie seu inventário de gerenciamento de ativo de TI do inventário de produto serializado padrão. Você também pode visualizar vários campos de quantidade em registros de item de produto, como disponível, alocado, em trânsito, danificado e em espera, para obter uma imagem precisa dos ativos implantáveis.

* **Obter visibilidade de inventário granular com rastreamento de quantidade baseado em estado**
  Rastreie com precisão o estado e a condição específicos do seu inventário em operações de Gerenciamento de ativos de TI, Field Service e cadeia de suprimentos. Use vários campos de quantidade baseados em estado no objeto Item de produto, como Quantidade disponível e Quantidade danificada, em vez de depender de uma única quantidade agregada. Categorize o estoque conduzido pelo mapeamento automatizado de status do ativo para evitar atrasos de cumprimento e evitar ativos promissores demais.

* **Sincronizar contagens de inventário com o mapeamento de status do ativo**
  Mantenha suas totalizações de item de produto perfeitamente sincronizadas com o estado real do hardware. Quando você mapeia status de ativo para categorias de quantidade específicas, o sistema atualiza automaticamente campos como Quantidade disponível ou Quantidade danificada sempre que o estado de um ativo muda, evitando discrepâncias de estoque.

* **Gerenciar transições de ciclo de vida do ativo de hardware em massa**
  Recupere, atualize ou descarte um grande grupo de ativos simultaneamente com apenas alguns cliques. Filtre e selecione rapidamente ativos diretamente em um modo de exibição de lista ou processe transições de alto volume carregando um arquivo CSV.

* **Implantação de hardware em escala com pedidos de cumprimento**
  Implemente ativos físicos para seus funcionários com uma estrutura de logística moderna. Agrupe vários produtos solicitados em um único pedido com base no local de origem usando os objetos Pedido de cumprimento e Item de linha do pedido de cumprimento. Substitua transferências de produto único por esse novo modelo de dados para dar suporte a automações conduzidas por IA escalonáveis.

* **Simplificar a recuperação de ativos com pedidos de devolução**
  Simplifique a logística de recuperação de hardware dos funcionários usando os objetos Pedido de devolução e Item de linha do pedido de devolução. Antes, retornar ativos dependia de registros de Transferência de produto projetados para movimentação de estoque para estoque. Agora você pode rastrear o retorno do hardware ao inventário, rotear dispositivos para vários locais ao mesmo tempo e automatizar atualizações de quantidade de inventário após o recebimento.

* **Evitar estoques de inventário com reservas flexíveis**
  Reserve o inventário para fontes de demanda específicas antes de um dispositivo físico ser selecionado da prateleira. As reservas suaves reduzem imediatamente a contagem de inventário disponível para evitar a reserva dupla de estoque, fornecendo visibilidade granular do estado do seu inventário e melhorando a precisão do cumprimento.

* **Proteger o fim da vida útil do hardware de TI com fluxos de trabalho de descarte de ativos**
  Garanta a segurança de dados, a responsabilidade ambiental e a conformidade regulatória ao descartar hardware. Os gerentes de ativos agora podem agrupar ativos descontinuados em pedidos de descarte abrangentes e impor tarefas de predisposição críticas, como limpeza de dados. Eles também podem carregar certificados oficiais de descarte para proteger uma trilha de auditoria.

* **Otimizar os ciclos de vida do hardware de TI com solicitações de serviço**
  Substitua casos por solicitações de serviço para simplificar seus fluxos de trabalho de ciclo de vida de hardware essenciais. Os funcionários podem iniciar solicitações por meio de vários canais de autoatendimento, incluindo o Portal do funcionário do Agentforce, o Slack e o Microsoft Teams. Para acelerar a entrega e a recuperação de hardware, os processadores de TI podem usar regras de roteamento automatizado, modelos de catálogo de serviços e origem de vários locais.

* **Alinhar ativos e itens de configuração com a sincronização de campo bidirecional**
  Mantenha seus registros de Gerenciamento de ativos de TI (ITAM) e Banco de dados de gerenciamento de configuração (CMDB) perfeitamente alinhados com a sincronização bidirecional conduzida por evento no nível de campo. Defina mapeamentos de campo, estabeleça uma fonte da verdade e configure traduções de valor de campo para resolver conflitos de dados entre sistemas. Esses recursos de sincronização eliminam a entrada de dados manual, reduzem o desvio de dados e fornecem dados precisos aos seus atendentes de TI.

* **Acompanhe o uso do Gerenciamento de ativos de hardware de TI com o Billing baseado em assinatura**
  Monitore o uso do Gerenciamento de ativos de hardware de TI com base no número de ativos de hardware de TI gerenciados elegíveis em sua organização. O consumo é medido por meio do Salesforce Digital Wallet, proporcionando visibilidade das contagens de ativos e das tendências de uso ao longo do tempo.

* **Acelere o processamento de hardware com o agente de origem**
  Simplifique os processos de processamento de hardware usando avaliações autônomas de restrições logísticas e de inventário em tempo real. O Agente de origem determina o caminho de origem mais econômico para solicitações de hardware aprovadas, recomendando se deseja cumprir com base no estoque existente ou iniciar uma nova aquisição.

* **Centralize o gerenciamento de apólice e mapeie os requisitos regulatórios**
  Gerencie políticas internas e vincule-as diretamente aos requisitos regulatórios em um espaço de trabalho unificado. Crie um rascunho de cláusulas, importe estruturas regulatórias e rastreie versões detalhadas da política enquanto gerencia mapeamentos no nível da cláusula. Quando as normas mudam, você pode identificar imediatamente o escopo do impacto para ver exatamente quais cláusulas da política precisam de ajuste.

* **Acelere a criação de políticas com o rascunho assistido por IA**
  Inicie rapidamente o processo de criação e aplique linguagem padronizada usando IA generativa para elaborar suas políticas de conformidade. Os autores de política agora podem gerar automaticamente cláusulas de política estruturadas e aplicáveis diretamente de requisitos regulatórios selecionados. Mantenha o alinhamento com normas internas e normas externas enquanto reduz drasticamente o tempo de rascunho manual.

* **Crie e sincronize cláusulas de política diretamente no Microsoft Word**
  Crie e edite suas políticas de TI em um ambiente familiar usando o complemento do Salesforce para o Microsoft Word. Gere cláusulas de política de alta qualidade com IA baseada em seu contexto de conformidade específico e sincronize atualizações bidirecionalmente entre o Word e o Salesforce para manter um sistema rígido de registro. Mantenha o controle de versão completo enquanto usa as ferramentas de colaboração e formatação avançadas do Word.

* **Promover a conformidade com campanhas e aprovações de políticas direcionadas**
  Crie campanhas de confirmação estruturadas vinculadas diretamente a versões da política publicadas para manter sua equipe informada. Distribua políticas a usuários ou grupos de funcionários específicos por meio de canais direcionados, incluindo o portal do funcionário, o Slack e o Microsoft Teams. Ao controlar estritamente o acesso e direcionar grupos de funcionários específicos, você garante que as políticas sigilosas alcancem apenas o público-alvo.

* **Simplifique o ciclo de vida do gerenciamento de risco com fluxos de trabalho e avaliações aprimorados**
  Simplifique o ciclo de vida de risco de ponta a ponta e substitua planilhas fragmentadas por um processo formal e auditável. Forneça às partes interessadas uma visão precisa da postura de risco da sua organização e acelere a implementação usando uma biblioteca centralizada de cenários de risco, controles de conformidade relacionados e monitoramento em segundo plano autônomo. Use o Mecanismo de regras de negócios para atualizar instantaneamente as pontuações de risco inerentes e residuais com base em pesquisas integradas da parte interessada.

* **Padronizar tarefas de remediação com planos de ação predefinidos**
  Elimine respostas inconsistentes e documentação ausente atribuindo tarefas de remediação predefinidas à sua equipe de conformidade. Os modelos de plano de ação predefinidos abrangem estratégias padrão, como Mitigar, Transferir, Aceitar ou Evitar, de modo que cada falha de controle siga um protocolo comprovado. Ao substituir a criação manual de tarefas por fluxos de trabalho padronizados, você mantém uma estrutura estruturada para ações corretivas e uma trilha confiável pronta para auditoria para cada lacuna.

* **Simplificar a coleta de evidências e a verificação de conformidade**
  Substitua planilhas e threads de email desagrupados por um sistema centralizado e auditável para criar, atribuir e rastrear solicitações de evidência. Especialistas no assunto atendem às solicitações carregando arquivos ou vinculando documentos seguros, enquanto mecanismos de verificação e bloqueio integrados garantem que os auditores recebam dados somente leitura precisos. Reduza o esforço manual e acelere a prontidão para a auditoria fornecendo às partes interessadas visibilidade em tempo real do seu status de conformidade.

* **Resolver lacunas de conformidade com o Gerenciamento de problemas**
  Identifique, rastreie e resolva problemas de conformidade em toda a sua organização diretamente de um sistema unificado. Crie problemas diretamente de políticas, riscos, controles ou descobertas de auditoria e atribua-os às equipes ou proprietários certos. As equipes podem acompanhar perfeitamente o progresso da remediação por meio de planos e tarefas de ação estruturados e garantir a resolução oportuna usando políticas de SLA.

* **Rastrear a conformidade regulatória e priorizar a exposição de risco**
  Gerencie ativamente suas políticas internas e avaliações de risco para manter a conformidade. Analise as principais métricas, como status do ciclo de vida da apólice e tendências de risco residual, para identificar lacunas de conformidade e focar a atenção da liderança em vulnerabilidades materiais.

* **Simplificar aprovações de alteração com painéis consultivos de alteração**
  Padronize revisões e aprovações de alteração organizando solicitações com painéis consultivos de alteração (CAB). Automatize aprovações de solicitação de alteração por meio de processos CAB estruturados, como agendamento e realização de revisões formais e integração de reuniões diretamente com o Calendário de serviços de TI. Use canais de notificação existentes para manter as partes interessadas informadas.

* **Gerenciar mais operações de TI e negócios com modelos do Catálogo de serviços**
  Estenda seu catálogo de serviços com modelos de solicitação e fluxos de processamento para operações de TI e negócios. Use modelos de solicitação para gerenciamento de acesso, provisionamento de infraestrutura, segurança e serviços de local de trabalho. Os modelos incluem fluxos de trabalho de aprovação e cumprimento quando aplicáveis. Os modelos padronizados para as principais áreas de serviço ajudam a acelerar a adoção do catálogo, reduzir o esforço de configuração e garantir que as solicitações sigam fluxos de trabalho regulados.

* **Conectar conversas de email a incidentes com encadeamento avançado**
  Evite incidentes duplicados e conversas fragmentadas vinculando automaticamente respostas de email ao registro original. O sistema identifica com segurança o incidente usando um ID exclusivo no assunto, no corpo ou nos metadados do email para manter o encadeamento preciso. Todas as conversas permanecem conectadas na cadeia de email e também estão disponíveis no feed de registro do incidente. Com uma visualização unificada da conversa completa, tanto os representantes de serviço quanto os funcionários têm todo o contexto necessário para responder rapidamente.

* **Configurar o comportamento do campo para uma criação de registro mais eficiente**
  Controle como os campos são preenchidos e exibidos ao criar registros relacionados para relacionamentos de incidente a problema, incidente a alteração, problema a alteração e alteração a problema. Mapeie campos padrão e personalizados para preencher dados automaticamente ou especifique campos adicionais para entrada manual durante o processo de criação. Os campos obrigatórios continuam sendo exibidos mesmo que os mapeamentos sejam removidos, garantindo a integridade dos dados.

* **Criar incidentes para outros sem sair do seu fluxo de trabalho**
  Crie incidentes em nome de outros diretamente no Slack, no Microsoft Teams, no portal do funcionário ou no console. Os incidentes capturam o usuário que cria o registro e o usuário afetado pelo problema, de modo que as equipes podem registrar pedidos com precisão sem trocar de sistemas. Crie uma triagem de problemas mais rápida, estabeleça uma propriedade clara e melhore a eficiência da resolução capturando detalhes no ponto de descoberta.

* **Melhore a precisão dos relatórios com dados de incidente e alteração capturados automaticamente**
  Quando você fecha uma solicitação de alteração, a Data de fechamento é definida automaticamente. Isso ajuda a reduzir inconsistências nos dados de fechamento e resolução que afetam os cálculos e os relatórios de KPI. Para incidentes, o campo Resolvido por é preenchido na resolução e limpo se o incidente for reaberto, enquanto as notas de resolução são retidas para o contexto.

* **Automatizar fluxos de trabalho do Catálogo de serviços com novos conectores externos**
  Estenda a automação do catálogo de serviços com novos conectores externos em sistemas de identidade, colaboração, DevOps, operações de TI e infraestrutura. Use modelos e ações conduzidas por API para melhorar a cobertura de automação completa em seus sistemas.

* **Organizar itens de configuração com marcas para pesquisar e filtrar mais rapidamente**
  Adicione e gerencie marcações em itens de configuração para melhorar a pesquisa, a filtragem e a categorização. Use marcações em exibições de lista, importações e APIs para agrupar itens relacionados e localizar rapidamente dados relevantes. Aplique marcações durante a importação ou atualização de itens existentes para manter uma classificação consistente e melhorar a visibilidade em todo o CMDB.

* **Acelere a integração de dados com a importação de CI aprimorada**
  Reduza o tempo de configuração e melhore a precisão dos dados importando itens de configuração (CIs) e relacionamentos de CI em um único fluxo de trabalho. Inclua relacionamentos de CI e marcas diretamente em arquivos de importação para criar dados conectados e aprimorados em uma única etapa. Faça download de modelos de importação predefinidos para tipos de item de configuração e relacionamentos de item de configuração para padronizar a formatação de dados e reduzir o esforço de configuração.

* **Exportar itens de configuração filtrados de modos de exibição de lista para análise externa**
  Filtre, pesquise e exporte itens de configuração (CIs) diretamente de exibições de lista para simplificar a análise e os relatórios. Use opções de filtragem avançadas e atributos pesquisáveis para restringir rapidamente os resultados. Exporte as CIs filtradas como um arquivo CSV para análise externa ou compartilhamento para dar suporte a decisões operacionais e melhorar a visibilidade dos dados do CMDB.

* **Infraestrutura complexa de modelo com componentes de CI configuráveis**
  Defina e gerencie componentes para tipos de item de configuração para representar relacionamentos de infraestrutura complexos. Use a guia Componentes no Gerenciador de tipo de CI para associar componentes relacionados a tipos de CI pai. Modele as dependências e a estrutura com mais precisão para dar suporte à descoberta, ao mapeamento de relacionamento e à análise de impacto em todo o CMDB.

* **Gerenciar e atualizar dados de configuração do CMDB com pacotes de dados**
  Mantenha-se atualizado com o modelo de configuração do CMDB mais recente revisando as versões disponíveis do pacote de dados. Atualize os dados de configuração quando novas versões estiverem disponíveis para manter os tipos de item de configuração, atributos e relacionamentos atualizados.

* **Analisar o desempenho operacional e o inventário do ativo de TI com o painel do CMDB Analytics**
  Analise seu inventário de ativos de TI e tendências operacionais para entender a composição do ambiente de TI usando o painel do CMDB Analytics. Acompanhe as principais métricas de item de configuração (CI), como as principais CIs por volume de incidentes ou contagem de problemas, para identificar problemas de alto impacto e priorizar seus esforços de resolução.

* **Descubra software instalado em dispositivos MacOS**
  Descubra o software instalado em dispositivos MacOS para melhorar a visibilidade do ativo e dar suporte a auditorias de segurança e verificações de licença. Use métodos de descoberta sem agente e baseados em agente para coletar detalhes do software, como nome, versão, data de instalação, local de instalação e editor. Leve o inventário de software do MacOS para o CMDB junto com dados do Windows e Linux para relatórios mais completos.

* **Acelere o suporte de TI com agentes especializados**
  Os modelos de suporte tradicionais muitas vezes dependem de agentes genéricos que carecem de profundo Knowledge de domínio ou exigem lógica de roteamento manual complexa. Automatize o suporte de TI roteando solicitações de funcionários para agentes especializados predefinidos projetados para domínios específicos. Esses agentes especializados são pré-configurados para lidar com tipos de solicitação distintos, como solução de problemas de rede ou processamento de hardware, por meio de uma interface conversacional. Encaminhe solicitações para o agente especializado mais qualificado para resolver problemas mais rapidamente. Quando as solicitações são entregues, o Agentforce compartilha o contexto para que os funcionários não tenham que repetir as informações.

* **Converter solicitações de serviço complexas em experiências conversacionais**
  Transforme solicitações de serviço estáticas complexas em conversas guiadas entre um funcionário e um agente de IA. Em vez de preencher formulários longos, os funcionários usam o chat Agentforce para preencher solicitações por meio de interações dinâmicas sensíveis ao contexto. Essa abordagem cria experiências dimensionáveis que mantêm a integridade dos dados, reduzem o esforço manual e melhoram a eficiência.

* **Simplificar o gerenciamento de CMDB com IA conversacional**
  Gerencie seu ciclo de vida do Banco de dados de gerenciamento de configuração (CMDB) no Slack, no Microsoft Teams ou no Salesforce usando linguagem natural. Os proprietários do Item de configuração (CI) e os gerentes do CMDB agora podem localizar, atualizar, excluir e gerenciar registros em massa por meio de uma interface conversacional habilitada por IA.

* **Acelere a tomada de decisão com resumos de aprovação gerados por IA**
  Os gerentes agora podem tomar decisões mais rápidas e mais bem informadas visualizando resumos para solicitações de aprovação pendentes no Slack, no Microsoft Teams ou no portal do funcionário. A Agentforce apresenta justificativas de negócios e histórico de solicitações em solicitações de serviço, RH e aquisições para resumir todos os itens de trabalho abertos ou aprofundar-se em solicitações específicas. Transforme dados de registro densos em percepções acionáveis, permitindo que os gerentes finalizem aprovações ou rejeições por meio de uma interface de chat simples.

* **Agende reuniões diretamente em conversas**
  Gerencie reuniões do Google ou do Outlook usando linguagem natural diretamente em seu fluxo conversacional. As equipes de TI agora podem agendar reuniões sem abrir um aplicativo de calendário nem sair da interface de chat. Ao automatizar o agendamento por meio do Agentforce, as equipes de TI podem localizar e reservar instantaneamente os períodos disponíveis durante uma interação de suporte.

* **Acelere a mitigação de risco com resumos gerados por IA**
  Use IA para criar resumos de risco abrangentes diretamente em registros e avaliações de risco. Esses resumos gerados por IA destilam informações densas em percepções claras e conversacionais, permitindo que sua equipe identifique descobertas críticas e fatores de risco instantaneamente. Obtenha uma visão clara e de alto nível dos principais metadados, impactos, controles e progresso da avaliação combinados com o feedback da parte interessada para destacar as principais descobertas e as próximas etapas recomendadas em um único widget. As equipes de TI podem evitar a alternância de guias e tomar decisões mais rápidas e bem informadas ao longo do ciclo de vida do risco.

* **Triagem automática de incidentes com IA**
  Quando um funcionário relata um incidente, a IA o testa automaticamente antes de a equipe de TI se envolver. Processos automatizados analisam o incidente em relação a incidentes anteriores, notas de resolução e artigos do Knowledge, para identificar campos incompletos, detectar registros duplicados e identificar relacionamentos com incidentes importantes ativos. As notificações são enviadas ao funcionário por meio do Slack, do feed do Chatter ou do email para que os funcionários possam adicionar comentários ou fechar o incidente com base nos resultados da triagem.

* **Controle o acesso a recursos de IA no Portal do funcionário do Agentforce**
  Restrinja os recursos de IA a usuários autorizados. Os recursos Pergunta dinâmica e Resposta e Resumo do Knowledge no Portal do funcionário do Agentforce agora exigem uma licença de complemento de IA. Para garantir a segurança, esses componentes aparecem apenas para usuários com a permissão necessária.

* **Acelere sua transição para o licenciamento de funcionários unificado com a migração em massa**
  Faça a transição de seus usuários funcionários existentes de licenças da Comunidade de clientes Plus (CCP) para a Licença unificada de funcionários (UEL) em escala. Use a ferramenta de migração em massa para mover todos os funcionários em uma operação, em vez de atualizá-los individualmente, preservando os IDs de usuário e a propriedade do registro existentes. Realize validações pré-migração obrigatórias, mapeie perfis de CCP existentes para novos perfis de Funcionário unificado e acompanhe o progresso por meio de relatórios de status. Observe que essa alteração é permanente e, assim que o processo de migração começar, não será mais possível criar novos usuários com perfis CCP.

* **Personalizar o portal com páginas personalizáveis de detalhes do pedido**
  Substitua layouts de portal predefinidos por layouts de página totalmente personalizáveis para atender a necessidades específicas do departamento. Implemente rapidamente novos tipos de registro para pedidos, como incidentes de TI ou solicitações de integração de RH, sem escrever código personalizado nem exigir largura de banda de engenharia. Especifique exatamente quais campos aparecem no painel Detalhes com base no objeto. A interface atribui dinamicamente o layout correto com base no perfil de usuário e no tipo de registro específico para garantir uma experiência altamente contextual para seus funcionários.

* **Centralize tarefas de conformidade no Portal do funcionário**
  Forneça aos seus funcionários uma maneira perfeita de gerenciar todas as suas responsabilidades de conformidade em um só lugar. Os funcionários podem facilmente pesquisar apólices ativas, concluir confirmações necessárias e cumprir solicitações de evidência diretamente no portal de autoatendimento. Garanta que seus funcionários sempre acessem os padrões mais atuais, pois o portal de autoatendimento publica automaticamente políticas ativas em tempo real. Forneça às suas equipes de conformidade alta visibilidade da adesão à política e do cumprimento da solicitação de evidência.

* **Associar artigos externos e visualizar sugestões em incidentes**
  Os representantes de serviços de TI podem localizar e vincular Knowledge de sistemas externos diretamente a incidentes usando o Enterprise Knowledge, desenvolvido com o Data 360. Crie uma base de Knowledge abrangente para seu balcão de serviços de TI usando o Knowledge nativo e externo do Salesforce. Visualize essas associações em uma lista relacionada no registro de Incidente para minimizar a alternância de contexto e ajudar a resolver problemas de TI com mais precisão. Para acelerar ainda mais a resolução, o aplicativo exibe automaticamente os artigos sugeridos com base nos detalhes do incidente.

* **Acelere a configuração do Microsoft Teams com configuração automatizada**
  Acelere sua integração com o Microsoft Teams com etapas de configuração automatizadas que reduzem o esforço manual e os erros de configuração. Simplifique as principais etapas configurando automaticamente as configurações de Compartilhamento de recurso entre origens (CORS), pontuando pontos de extremidade necessários na lista de permissões e fornecendo suporte do OAuth para autenticação segura. Torne a experiência de configuração mais rápida e consistente para administradores e reduza a sobrecarga típica de tarefas de rede manuais complexas.

* **Rastrear ativos no Microsoft Teams**
  Os funcionários podem rastrear e gerenciar o hardware atribuído no aplicativo Microsoft Teams. Ao fornecer aos funcionários uma visão clara dos dispositivos atribuídos, junto com links diretos para solicitar assistência, você garante que as equipes de TI recebam dados precisos específicos do ativo para cada pedido de suporte. Os funcionários agora podem acessar os detalhes do ativo e relatar problemas em um só lugar, reduzindo a necessidade de navegar em várias ferramentas.

* **Autenticar usuários do Microsoft Teams com Single Sign On**
  Acesse o Serviço de TI do Agentforce no Microsoft Teams usando as credenciais da Microsoft existentes para proporcionar uma experiência de autenticação segura e unificada. A experiência de login único elimina a necessidade de vários avisos de login e reduz a fadiga de senha para seus funcionários. Os funcionários permanecem produtivos em sua ferramenta principal de colaboração sem enfrentar barreiras repetitivas de acesso, enquanto você pode conectar com segurança seu provedor de identidade ao seu ambiente do Salesforce.

* **Automatizar a sincronização do usuário com o Microsoft Entra ID**
  Automatize os ciclos de vida do usuário sincronizando criações, atualizações e exclusões do ID de entrada da Microsoft com o Salesforce para manter os usuários funcionários consistentes entre plataformas. Use essa sincronização nativa para manter uma única fonte da verdade, refletindo alterações em tempo real sem a necessidade de licenças adicionais do conector de fluxo. Ao eliminar conectores de terceiros, você reduz a complexidade arquitetônica e os custos de licenciamento enquanto garante que o acesso do funcionário seja revogado ou atualizado automaticamente durante as transições de ciclo de vida. Mantenha a integridade de dados para registros históricos e forneça às equipes de TI controles de acesso atualizados e confiáveis.

* **Acessar o suporte de TI diretamente no Microsoft 365**
  Gerencie problemas de TI em seu fluxo de trabalho diário usando registros do Agentforce IT Service no Microsoft 365. Use o Microsoft Copilot e aplicativos do Office integrados para localizar Knowledge, gerenciar pedidos e solicitar itens de catálogo por meio de uma interface conversacional unificada. Essa integração reduz a alternância de contexto e impulsiona o autoatendimento levando o suporte de TI para ferramentas de produtividade diárias.

* **Configure notificações de modo consistente em mais fluxos de trabalho**
  Configure notificações para um conjunto mais amplo de registros em serviços de TI, gerenciamento de ativos de hardware e fluxos de trabalho de conformidade de TI. As notificações agora dão suporte a objetos adicionais, como convites para pesquisa de avaliação de risco e ordens de trabalho, que estendem a cobertura para mais casos de uso operacionais e de governança. Equipes de TI e funcionários ficam informados e agem sem depender de rastreamento manual em diferentes processos.

* **Fique a par de SLAs com notificações de vários canais**
  Assuma o controle de seus contratos de nível de serviço para registros de serviço (SLAs) enviando notificações para canais como Email, Slack, No aplicativo e Teams. Configure ações de marco de SLA para enviar notificações sobre avisos, violações e eventos de conclusão a um público especificado. As equipes de TI não monitoram mais os temporizadores e podem responder proativamente a prazos se aproximando ou violados.

* **Validar a entrega e a precisão da notificação antes da ativação**
  Teste suas notificações com relação a registros de amostra antes da ativação para garantir que elas entrem nos destinatários certos por meio dos canais corretos. Valide como as notificações são renderizadas em canais selecionados para que sejam precisas e completas. Verificar sua configuração ajuda a evitar erros, reduzir o retrabalho e manter as notificações prontas para uso em produção.

* **Gerenciar mapeamentos de regra de atribuição com mais flexibilidade**
  Os administradores agora podem mapear ou remover o mapeamento de regras de atribuição para registros de serviço com suporte diretamente na configuração Regras de atribuição. Antes, a remoção de mapeados exigia a reconfiguração da configuração. Esse aprimoramento simplifica o gerenciamento de regras, reduz as despesas operacionais e ajuda os administradores a ajustar a lógica de roteamento conforme as necessidades evoluem.

* **Colocar a IA agente para trabalhar em tarefas de RH comuns com uma biblioteca de agentes pré-criada**
  Automatize tarefas de RH comuns usando agentes dedicados da biblioteca de agentes predefinida. Seus funcionários podem visualizar automaticamente a folha de pagamento e atualizar informações pessoais, enquanto os gerentes podem aprovar de modo eficiente solicitações de licença e gerenciar metas de desempenho. Esses agentes ajudam os usuários a concluir tarefas mais rapidamente e reduzem o trabalho administrativo manual.

* **Rascunho de respostas de email de vários artigos do Knowledge**
  Gere rascunhos abrangentes de emails de serviço com base em artigos do Knowledge relevantes. Você pode selecionar até três artigos do Knowledge mais relevantes para que sua resposta de email seja apoiada por informações precisas. O Knowledge Grounded Email Response (KGER) reduz o tempo de rascunho manual de email fornecendo um ponto de partida detalhado que você pode revisar e editar antes do envio.

* **Gerar resumos aprimorados no idioma de sua preferência**
  Gere Resumos aprimorados no idioma definido nas configurações de localidade, independentemente do idioma usado durante as interações com o cliente. Com resumos baseados em localidade, você pode revisar e entender o conteúdo gerado por IA em seu próprio idioma antes de salvá-lo. O recurso Resumos aprimorados agora oferece suporte a dinamarquês, holandês, finlandês, coreano, norueguês, português (brasileiro), português (europeu), russo, sueco e tailandês, além dos idiomas com suporte anteriormente.

* **Gerar resumos de trabalho no idioma de sua preferência**
  Gere Resumos de trabalho do Einstein para sessões de mensagens aprimoradas e chamadas de voz no idioma definido nas configurações de localidade, independentemente do idioma usado durante as interações com o cliente. Com resumos baseados em localidade, você pode revisar e entender o conteúdo gerado por IA em seu próprio idioma antes de salvá-lo. O recurso Resumos do trabalho para sessões de mensagens aprimoradas e chamadas de voz agora oferece suporte a dinamarquês, holandês, finlandês, coreano, norueguês, português (brasileiro), português (europeu), russo, sueco e tailandês, além dos idiomas com suporte anteriormente.

* **O recurso Resumos do trabalho para caso (beta) está sendo descontinuado**
  O recurso Resumos do trabalho para caso (beta) está agendado para descontinuação em 30 de junho de 2026 e está no modo de manutenção até lá. Você pode continuar usando Resumos de trabalho para caso (beta) até essa data, mas recomendamos fazer a transição para Resumos aprimorados. O recurso Resumos aprimorados oferece resumos específicos do papel e mais recursos de resumo, o que ajudará seus representantes de serviço a trabalhar de modo mais eficiente.

* **Crie comentários de caso contextuais instantaneamente com Agentforce**
  Seus representantes de serviço agora podem gerar comentários de caso profissionais e contextuais usando avisos de linguagem natural. Os modelos prontos para uso proporcionam comunicação consistente fundamentando respostas em histórico de caso, interações com o cliente e artigos do Knowledge. Reduza o tempo que seus usuários passam escrevendo manualmente e garanta uma abordagem padronizada ao gerenciamento de caso.

* **Encontre especialistas em caso instantaneamente com ações do Agentforce**
  Seus representantes de serviço agora podem identificar os melhores especialistas disponíveis para casos complexos usando uma ação Agentforce especializada. Localizar especialista em caso analisa o contexto do caso, padrões de resolução históricos e disponibilidade em tempo real para sugerir três a cinco profissionais classificados com raciocínio específico. Essas recomendações ajudam seus representantes a resolver problemas mais rapidamente facilitando a colaboração imediata por meio do Slack ou reatribuição de caso contínua.

* **Atribuir casos de comunidade automaticamente com regras de atribuição padrão**
  Regras de atribuição de caso padrão agora são executadas de modo automático e consistente para todos os registros criados por meio de sites do Experience Cloud. Elimine a necessidade de código personalizado ou fluxos complexos para rotear casos de autoatendimento. Agora você pode gerenciar toda a lógica de roteamento em um local padrão para garantir que os casos entrem nos agentes certos imediatamente.

* **Mesclar casos duplicados não abertos em filas do Omni-Channel (beta)**
  Resolva casos duplicados com mais eficiência mesclando-os mesmo enquanto estão ativos em uma fila do Omni-Channel. Antes, não era possível mesclar casos que estavam sendo roteados ou atribuídos no momento, exigindo intervenção manual para removê-los da fila primeiro. Agora, você pode permitir a mesclagem de casos duplicados que não foram abertos por um representante, reduzindo as pendências sem interromper o trabalho ativo.

* **Ilustre problemas complexos do cliente com descrições de caso em rich text (beta)**
  Os representantes de suporte agora podem usar um editor de rich text para capturar instruções de problema detalhadas com facilidade. Os representantes podem adicionar imagens, formatar texto com marcadores e numeração e incluir tabelas ou links de URL diretamente na descrição do caso. Essas descrições aprimoradas fornecem um contexto melhor para o Assistente de serviço e o Resumo do caso para gerar resultados precisos.

* **Gerenciar casos duplicados proativamente com a Mesclagem de casos aprimorada (beta)**
  Ajude seus representantes a manter um banco de dados limpo e aumentar a produtividade identificando e consolidando casos duplicados. Crie regras de correspondência personalizadas que ajudam você a detectar casos potenciais para mesclagem de caso proativamente ao carregar o caso. Adicione o componente da Web Lightning Casos duplicados à página de caso para que seus representantes também possam ver e agir em sugestões em tempo real diretamente na página de caso

* **Promova decisões de serviço mais rápidas com Insights de sentimento em tempo real**
  Capacite sua equipe de serviço a responder às necessidades do cliente mais rapidamente expondo dados de sentimento em tempo real para caso, chat e voz no Service Assistant. Os agentes ficam informados sobre os níveis de sentimento do cliente durante chamadas e chats ativos, enquanto os supervisores usam dados de tendência para tomar decisões de pessoal informadas orientadas por dados. Essa visibilidade ajuda sua equipe a manter a consistência do serviço e lidar com interações de alta pressão com confiança.

* **Agrupar motivos de contato para percepções mais claras do atendimento ao cliente**
  Agrupar motivos para contato em clusters deriva percepções acionáveis de dados granulares de motivo para contato. Essa granularidade melhora a visibilidade das preocupações do cliente, facilitando intervenções oportunas. Os administradores podem ajustar manualmente os clusters com base nas necessidades de negócios.

* **Alcançar a conformidade de SLA quase perfeita com marcos agentes (beta)**
  Use a IA generativa para concluir de modo autônomo as comunicações de rotina vinculadas a Acordos de nível de serviço (SLAs) para casos. O Agentforce elabora e envia primeiras respostas contextualmente relevantes e atualizações de status periódicas aos seus clientes com base no progresso da resolução. Ao descarregar essas comunicações repetitivas, seus representantes de serviço podem se concentrar na solução de problemas complexos enquanto mantêm quase 100% de conformidade com o SLA para marcos de propriedade de agentes digitais.

* **Prever e prevenir violações de SLA com a pontuação de risco proativa**
  Ajude seus representantes de serviço a ficarem à frente de possíveis atrasos e violações do acordo de nível de serviço (SLA) prevendo a probabilidade de um caso perder seu SLA. Esse recurso fornece uma pontuação de risco quantificável em registros de caso com base em dados em tempo real, como prioridade, status e atividade recente. Ao identificar casos de alto risco com antecedência, os representantes de serviço podem priorizar sua carga de trabalho e prevenir violações.

* **Migre perfeitamente seus funcionários da Comunidade de clientes Plus para a licença de funcionário unificada**
  Substitua o licenciamento fragmentado e simplifique a administração migrando seus funcionários para a Licença unificada de funcionário (UEL). Essa migração de aceitação somente de identidade preserva IDs de usuário, nomes de usuário e propriedade de registro. Unificar sua personalidade de funcionário reduz inconsistências de identidade em Serviço de TI, Serviço de RH e Slack. Depois de migrar seus funcionários para a UEL, você não poderá voltar para a Comunidade de clientes Plus (CCP).

* **Personalizar a experiência do funcionário com aprimoramentos do portal unificado**
  Acompanhe aprovações, relate conduta incorreta e acesse dados do funcionário com mais eficiência com layouts de registro atualizados. Veja o histórico de aprovação completo de uma solicitação diretamente no registro, e os gerentes atribuídos a um pedido podem usar o botão Revisar para identificar quem está processando uma solicitação. Para habilitar relatórios de conduta incorreta discreta, marque a caixa de seleção Casos confidenciais em um pedido. O registro é sinalizado automaticamente e roteado apenas para representantes de RH autorizados. Modos de exibição de perfil remodelados também separam dados profissionais de detalhes pessoais para melhor visibilidade.

* **Instalar uma solução predefinida para iniciar rapidamente seus serviços de RH**
  Acelere o tempo para valor para o Serviço de RH com configurações recomendadas que simplificam a configuração do dia um. A Solução básica de serviço de RH habilita as configurações e instala os metadados e os dados de amostra necessários para testar os recursos de RH. Para testar o autoatendimento do funcionário e o gerenciamento de caso de RH em um ambiente seguro, primeiro implemente esses ativos pré-configurados em um sandbox antes de migrar para a produção. Descubra e configure recursos adicionais de recursos, como provisionamento de funcionários e programas de enablement, tudo em um só local em Configuração.

* **Automatizar solicitações de acesso de RH e simplificar o provisionamento com conectores de fluxo**
  Use conectores externos em fluxos de entrada e cumprimento para automatizar solicitações de serviço de RH de alta frequência, como consultar dados de terceiros para software disponível, desbloquear contas e provisionar acesso seguro. Elimine erros manuais na coleta de dados e reduza a carga de trabalho da central de ajuda e os tempos de espera do usuário. Itens do catálogo de serviços com integração de API direta simplificam a configuração complexa.

* **Implemente fluxos de trabalho de RH mais rapidamente com modelos de serviço predefinidos**
  Permita que seus funcionários gerenciem com eficiência suas necessidades de RH com uma biblioteca de fluxos de trabalho de serviço de RH predefinidos. Esses modelos abrangem funções padronizadas de alta demanda, como folha de pagamento, solicitações de licença e benefícios. Você pode implementar esses fluxos de trabalho como processos de serviço independentes ou conectá-los a sistemas de RH de terceiros.

* **Colocar a IA agente para trabalhar em tarefas de RH comuns com uma biblioteca de agentes pré-criada**
  Automatize tarefas de RH comuns usando agentes dedicados da biblioteca de agentes predefinida. Seus funcionários podem visualizar automaticamente a folha de pagamento e atualizar informações pessoais, enquanto os gerentes podem aprovar de modo eficiente solicitações de licença e gerenciar metas de desempenho. Esses agentes ajudam os usuários a concluir tarefas mais rapidamente e reduzem o trabalho administrativo manual.

* **Refine fluxos de trabalho de Respostas de serviço existentes com o botão Ocultar publicação**
  Agora você tem a opção de expor o botão Publicar no componente Respostas de serviço. Quando o botão Publicar está oculto, os representantes de serviço colocam a resposta no chat e a modificam antes do envio.

* **Traduzir para mais idiomas com Traduzir respostas de serviço**
  O recurso Traduzir respostas de serviço agora oferece suporte a dinamarquês, holandês, finlandês, hebraico, coreano, norueguês, português, russo, sueco e tailandês. Você precisa de pelo menos 1.000 transcrições de chat fechadas em um idioma para entregar respostas nesse idioma.

* **Conhecimento unificado está sendo descontinuado**
  O Conhecimento unificado está programado para ser descontinuado na versão Summer '27. Você pode continuar a usá-lo até lá, mas recomendamos migrar para o Salesforce Enterprise Knowledge, habilitado pelo Data 360. Usando conectores do Data 360, você pode ingerir seu Knowledge externo no Salesforce e integrá-lo ao seu Salesforce Knowledge nativo, criando uma única base de Knowledge abrangente. O Salesforce Enterprise Knowledge inclui muitos dos recursos que você adora do Conhecimento unificado, além de tratamento de arquivos de tamanho aprimorado, inovação aprimorada e melhores recursos de armazenamento de dados e pipeline.

* **Transfira suas conversas do agente do Agentforce do Salesforce Voice para um representante de serviço nas centrais de contato do Agentforce**
  Garanta que seus clientes sempre recebam a ajuda necessária escalando problemas complexos de um agente de IA para um representante de serviço em canais do Salesforce Voice. Usando o tópico Escalonamento e um fluxo do Omni-Channel de saída, seus agentes do Agentforce agora podem rotear facilmente conversas do Salesforce Voice junto com seu histórico completo para o destino certo. As centrais de contato Agentforce no modelo Salesforce Voice (Telefonia nativa) agora oferecem suporte total a esses recursos de escalação.

* **Controlar o acesso à fila para superiores na hierarquia de papéis**
  Para controlar melhor o compartilhamento de registro, use a configuração Conceder acesso usando hierarquias em filas para escolher se os registros compartilhados com membros da fila também são compartilhados com seus superiores. Antes, os superiores sempre eram adicionados a filas por padrão e frequentemente recebiam notificações por email em excesso.

* **O Omni-Channel padrão está agendado para descontinuação**
  O Omni-Channel padrão está agendado para descontinuação na versão Summer '26. Para garantir que seus usuários mantenham seus fluxos de trabalho de roteamento e obtenham acesso aos recursos mais recentes, o Salesforce atualiza automaticamente sua organização para o Omni-Channel aprimorado durante a distribuição da Summer '26.

* **Agendar itens de trabalho para roteamento em uma data e hora específicas**
  Agora você pode definir uma data e hora específicas para os itens de trabalho serem roteados no futuro, em vez de adicioná-los imediatamente à pendência de roteamento. Essa alteração ajuda suas equipes a gerenciar retornos de chamada e acompanhamentos combinando o trabalho com os representantes disponíveis apenas quando o tempo agendado passar. Os supervisores também podem rastrear esses itens agendados diretamente no backlog do Command Center para serviço.

* **Rotear trabalho com base na data da solicitação original**
  Priorize os itens de trabalho com base em quando eles foram solicitados pela primeira vez, em vez de quando entraram em uma fila. Use carimbos de data e hora de registro originais para manter tarefas mais antigas na frente da fila. Isso ajuda a priorizar itens de trabalho transferidos ou novas tentativas de retorno com base no horário da solicitação inicial.

* **Melhore a experiência do representante evitando chamadas antes que os representantes estejam prontos**
  Impeça que o Omni-Channel atribua trabalho a seus representantes de serviço antes que o conector de telefonia seja totalmente carregado. A Verificação de prontidão do conector de voz informa aos representantes que o Salesforce ainda está trabalhando para disponibilizá-los e os impede de receber trabalho. Quando o login único (SSO) estiver concluído e o conector do Voice estiver pronto, as chamadas serão implantadas.

* **Configurar o Agentforce Orchestrator para suas interações do site do Experience Cloud**
  Configure o Agentforce Orchestrator para rotear interações do seu site do Experience Cloud para os agentes de IA e fluxos de trabalho de serviço corretos. Defina atribuições de agente, sinais de personalização e configurações de roteamento que dão suporte a experiências de autoatendimento conduzidas por IA em seu site.

* **Encaminhe conversas do site do Experience Cloud para o Agentforce Orchestrator com o Omni-Channel**
  Use as Configurações de mensagens do Omni-Channel para associar seu site do Experience Cloud a uma configuração do Agentforce Orchestrator. Conecte conversas do site aos agentes de IA apropriados, sinais de personalização e fluxos de trabalho de back-end sem desenvolvimento personalizado.

* **Fornecer recomendações personalizadas aos usuários do site do Experience Cloud**
  Forneça saudações personalizadas, sugestões de prompt e recomendações a usuários autenticados. As recomendações são baseadas nos dados de engajamento que o Data 360 captura do seu site do Experience Cloud.

* **Guie seus usuários com uma barra de avisos inteligente no site do Experience Cloud**
  Forneça um campo de entrada unificado em seu site do Experience Cloud em que os usuários possam pesquisar informações, iniciar conversas ou acionar ações automatizadas. A barra de instruções interpreta a intenção do usuário e retorna respostas, ações ou conversas na mesma interface.

* **Detecte sugestões de prompts em seu site do Experience Cloud com Temas de sugestão**
  Mostre sugestões de prompt em seu site do Experience Cloud usando temas de sugestão. Os usuários podem selecionar uma sugestão para iniciar uma solicitação ou recuperar informações.

* **Ajude os usuários a navegar em seu site do Experience Cloud com a barra lateral do Concierge**
  Forneça um painel de navegação persistente em seu site do Experience Cloud que combine a navegação tradicional do site com ações recomendadas e recursos de chat.

* **Iniciar a experiência inicial do Concierge em seu site do Experience Cloud**
  Forneça uma página inicial dedicada que combine a barra de instruções, sugestões e componentes de navegação em uma interface unificada com suporte de IA.

* **Oriente os usuários para resolver solicitações com blocos de conteúdo dinâmico**
  Mostre blocos interativos que orientam os usuários por meio de ações, como gerenciamento de caso, aprovações ou recuperação de informações. Os blocos apresentam opções relevantes para que os usuários possam concluir tarefas com menos etapas conversacionais.

* **Criar e gerenciar modelos de bloco com o Criador de bloco dinâmico**
  Use o Criador de bloco dinâmico para criar e gerenciar modelos de bloco de uma interface visual centralizada. Conecte o comportamento de bloco a agentes de IA, automações de catálogo ou fluxos de trabalho híbridos para ajudar seus usuários a agir diretamente nos resultados da pesquisa.

* **Fornecer assistência de IA em páginas de registro do site do Experience Cloud**
  Mostre recomendações e ações de IA contextuais diretamente em páginas de detalhes de registro, como casos, pedidos ou registros.

* **Retomar conversas com o histórico de bate-papo no site do Experience Cloud**
  Você pode visualizar e retomar conversas anteriores com o concierge de IA em sessões e dispositivos. Cada interação é armazenada como um segmento de conversa vinculado à conta do usuário, capturando mensagens, carimbos de data e hora e ações de bloco concluídas.

* **Acompanhe o engajamento do usuário no site do Experience Cloud com a Análise de autoatendimento**
  Capture análises sobre interações em seu site do Experience Cloud para medir o engajamento e melhorar as recomendações de IA.

* **Revisar tarefas e aprovações de um site do Experience Cloud**
  Forneça uma interface unificada para funcionários e gerentes revisarem tarefas, aprovações e ações necessárias.

* **Configurar ações e agentes para pesquisa do agente em seu site do Experience Cloud**
  Defina quais agentes lidam com tópicos de pesquisa e quais ações os usuários podem realizar diretamente nos resultados da pesquisa em seu site do Experience Cloud.

* **Inserir URLs de artigo do Knowledge Enterprise em emails de caso (beta)**
  Controle como os links de artigos do Knowledge são abertos em respostas de email de caso direcionando os clientes a artigos no site do Experience Cloud.

> 📄 **Notas Completas:** consulte os detalhes completos na página do tópico [SERVICE](./releases/summer_26/service.md).
</details>

<details>
<summary><b>📄 SLACK APPS (Clique para expandir 2 alterações)</b></summary>

* **Desfrute da colaboração habilitada pelo Slack em novas organizações do Salesforce**
  Os canais do Salesforce levam o Slack diretamente para o Salesforce e agora estão ainda mais acessíveis. Os canais do Salesforce estão configurados e prontos para uso em organizações criadas na versão Summer '26 e posteriores, sem necessidade de configuração manual.

* **Acessar canais do Salesforce no painel do Slack**
  O novo painel do Slack oferece uma maneira simplificada de visualizar e colaborar em canais do Salesforce. Você pode abrir e fechar o painel com um clique, de modo que ele consome menos espaço em uma página de registro quando você não o está usando.

> 📄 **Notas Completas:** consulte os detalhes completos na página do tópico [SLACK APPS](./releases/summer_26/slack_apps.md).
</details>


---

