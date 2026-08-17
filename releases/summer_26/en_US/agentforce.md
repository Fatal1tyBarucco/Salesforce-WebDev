<div style="padding:8px 12px;margin-bottom:16px;border:1px solid #d0d7de;border-radius:6px;background:#f6f8fa;font-family:system-ui,sans-serif;font-size:14px;"><strong>Idioma:</strong> <a href="../en_US/agentforce.md" style="text-decoration:none;font-weight:bold;">🇺🇸 English</a> &nbsp;|&nbsp; <a href="../pt_BR/agentforce.md" style="text-decoration:none;">🇧🇷 Português</a></div>
## Agentforce

> **68 features** | 🔴 17 alto impacto | 🟡 17 médio | 🟢 3 baixo

A release Summer '26 expande significativamente o ecossistema Agentforce, consolidando a transição para arquiteturas de IA totalmente autônomas e multimodais. Os destaques incluem o avanço das capacidades do Agentforce Voice, a introdução da interoperabilidade via Model Context Protocol (MCP) e o aprimoramento das ferramentas de governança, observabilidade e gerenciamento do ciclo de vida dos agentes e modelos de prompt.

| Feature | Descrição | Impacto |
| :--- | :--- | :---: |
| **Transcrição mais nítida e voz mais natural para Agentforce Voice (usuários)** — _usuários_ | Melhora a precisão do reconhecimento de fala e a síntese de voz (TTS) em interações do Agentforce Voice, reduzindo a lat… | 🟡 médio |
| **Converse com Agentforce em mais 24 idiomas (beta) (admins)** — _admins_ | Expande a capacidade nativa de processamento de linguagem natural do Agentforce para mais 24 idiomas, permitindo atendim… | 🔴 alto |
| **Obtenha percepções sobre o consumo de IA generativa e Agentforce (admins)** — _admins_ | Oferece painéis analíticos e relatórios detalhados sobre o uso de tokens, execuções de agentes e custos associados à IA … | 🔴 alto |
| **Criar agentes no Criador novo apenas a partir de julho de 2026 (admins)** — _admins_ | Define o encerramento do legado do Agent Builder, exigindo que todos os novos agentes sejam construídos exclusivamente n… | 🔴 alto |
| **Editar subagentes na biblioteca de ativos (admins)** — _admins_ | Permite modularizar e reutilizar subagentes gerenciando-os e editando-os diretamente através de uma biblioteca central d… | 🟡 médio |
| **Observabilidade do Agentforce: Análise de agente refinada e poncionadores personalizados (beta) (admins)** — _admins_ | Introduz métricas detalhadas de execução passo a passo e permite criar acionadores personalizados para alertar sobre com… | 🔴 alto |
| **Desbloqueie a interoperabilidade do agente com MCP para Agentforce (admins)** — _admins_ | Habilita a integração com o Model Context Protocol (MCP), permitindo que agentes do Agentforce consumam ferramentas e co… | 🔴 alto |
| **Proteja conexões com suas APIs externas e servidores MCP com Políticas Agentforce (config)** — _config_ | Permite aplicar políticas robustas de autorização, autenticação e controle de limites de taxa para requisições de agente… | 🔴 alto |
| **Criar e implementar agentes habilitados para Voice no novo Agentforce Builder (admins)** — _admins_ | Centraliza o design, teste e publicação de agentes baseados em voz diretamente na interface visual do novo Agentforce Bu… | 🔴 alto |
| **Extensão do suporte a idiomas globais com Agentforce Voice (beta) (usuários)** — _usuários_ | Amplia os idiomas e dialetos suportados para interações de áudio em tempo real com o Agentforce Voice. | 🟡 médio |
| **O provedor de pesquisa OpenAI na ação Pesquisar o agente da Web agora está disponível ao público em geral (admins)** — _admins_ | Disponibiliza em GA o uso da API de pesquisa da OpenAI como provedor de grounding para pesquisas na web realizadas por a… | 🟡 médio |
| **Aumente o Trust com citações em Traga seu próprio canal (config)** — _config_ | Exibe citações e referências de fontes de dados Grounded em integrações BYOC (Bring Your Own Channel) como WhatsApp, Cus… | 🟡 médio |
| **Atualize facilmente os agentes do Criador legado para o Criador novo (admins)** — _admins_ | Fornece assistentes de migração automatizada para converter agentes criados na ferramenta antiga para a nova estrutura d… | 🔴 alto |
| **Crie um agente avançado com script do agente para terminar com o Guia de implementação atualizado (admins)** — _admins_ | Atualização das diretrizes e padrões de arquitetura para desenvolvimento de scripts de agentes complexos e fluxos determ… | 🟡 médio |
| **Encaminhe chamadas de voz do Agentforce usando SIP (admins)** — _admins_ | Permite a integração direta de chamadas de voz do Agentforce via protocolo SIP com PABX/CCaaS legados da empresa. | 🔴 alto |
| **Transforme sua experiência do cliente com agentes habilitados para Voice no Chat v2 aprimorado (admins)** — _admins_ | Habilita a alternância fluida entre mensagens de texto e interações por áudio/voz na nova geração do widget de Chat (Cha… | 🔴 alto |
| **Aprimore suas implantações do Chat v2 aprimoradas com mais personalização e confiabilidade (admins)** — _admins_ | Adiciona novos recursos de branding, tratamento de erros e reconexão automática para o componente de conversação Chat v2… | 🟡 médio |
| **Orquestrar outros agentes (beta) (admins)** — _admins_ | Permite que um agente principal (agente orquestrador) invoque e gerencie a execução de subagentes especializados para re… | 🔴 alto |
| **Prepare-se para o modelo atualizado para a opção hospedada pela AWS no Agentforce (admins)** — _admins_ | Atualizações de infraestrutura e versão de modelos fundamentais na opção de implantação do Agentforce sob a AWS. | 🟡 médio |
| **Funcionalidade de script do agente nova e alterada (admins)** — _admins_ | Atualizações nas sintaxes, métodos de execução e tratamento de exceções nos scripts controladores de comportamento dos a… | 🟡 médio |
| **Ações e subagentes padrão do agente novos e alterados (config)** — _config_ | Inclusão de ações nativas prontas para uso e ajustes nas permissões padrão fornecidas pela plataforma para criação de ag… | 🟡 médio |
| **Desenvolvimento do Agentforce** | Conjunto de melhorias nas ferramentas de desenvolvedor, SDKs e CLI do Salesforce para criação, teste e implantação progr… | 🟡 médio |
| **Gerenciar bibliotecas de dados do Agentforce com a API ADL Connect (beta) (admins)** — _admins_ | API dedicada para conectar, sincronizar e gerenciar programaticamente bibliotecas de dados (Agent Data Libraries) usadas… | 🔴 alto |
| **Criador de prompts** | Visão geral e aprimoramentos estruturais no Prompt Builder para criação, gestão e teste de modelos de prompt generativo … | 🟢 baixo |
| **Crie modelos inteligentes de prompts com lógica condicional (beta) (usuários)** — _usuários_ | Permite adicionar declarações condicionais (IF/ELSE) diretamente no template do Prompt Builder para dinamizar a instruçã… | 🔴 alto |
| **Escreva avisos mais rapidamente com o Editor de bloco (beta) (usuários)** — _usuários_ | Interface visual modular baseada em blocos para drag-and-drop de recursos de dados, instruções e contextos no Prompt Bui… | 🟡 médio |
| **Usar atalhos de teclado no Criador de prompts (usuários)** — _usuários_ | Adiciona atalhos de teclado para agilizar a navegação, inserção de recursos e testes dentro do Prompt Builder. | 🟢 baixo |
| **Visualizar dependências de modelo de prompts em toda a sua organização (usuários)** — _usuários_ | Fornece visualização clara de quais fluxos, agentes, campos ou Apex referenciam um modelo de prompt específico antes de … | 🟡 médio |
| **Implemente e controle de versão modelos de prompt com a API de metadados (usuários)** — _usuários_ | Suporte completo na Metadata API para rastreamento de versão e implantação ALM automatizada de Prompt Templates entre am… | 🔴 alto |
| **Personalizar modelos de prompts gerenciados com substituições (usuários)** — _usuários_ | Permite que administradores sobreponham partes de Prompt Templates empacotados por ISVs ou gerenciados sem perder a capa… | 🔴 alto |
| **Governar idiomas de resposta de prompt (usuários)** — _usuários_ | Fornece controles de governança para forçar ou restringir o idioma em que o LLM gera as respostas, independentemente do … | 🟡 médio |
| **Modelos com suporte** | Atualização da lista de Grandes Modelos de Linguagem (LLMs) homologados e suportados nativamente pela Plataforma Einstei… | 🟢 baixo |
| **Use o Gemini 3.5 Flash na Plataforma Einstein (admins)** — _admins_ | Adiciona o modelo Gemini 3.5 Flash ao catálogo de LLMs nativos da Plataforma Einstein, oferecendo alta velocidade e baix… | 🔴 alto |
| **Limites maiores para solicitações de geração de modelo de idioma grande (admins)** — _admins_ | Eleva as cotas padrão e os limites de caracteres/tokens para requisições de IA generativa por organização na Plataforma … | 🟡 médio |
| **Usar o Nemotron 3 Super 120B na Plataforma Einstein (beta) (config)** — _config_ | Disponibiliza o modelo altamente otimizado NVIDIA Nemotron 3 Super 120B na Plataforma Einstein para tarefas analíticas e… | 🟡 médio |
| **Claude Opus 4.6 está disponível ao público em geral (admins)** — _admins_ | Disponibiliza em GA o modelo Claude Opus 4.6 na Plataforma Einstein, oferecendo o mais avançado nível de raciocínio, aná… | 🔴 alto |
| **Preparar-se para a data de redirecionamento do Claude Sonnet 4 (admins)** — _admins_ | Aviso sobre a depreciação de versões anteriores do Claude Sonnet e o redirecionamento automático de requisições para a v… | 🟡 médio |

## 🎓 Related Trailhead Modules

- [Agentforce Basics](https://trailhead.salesforce.com/content/learn/modules/agentforce-basics) — 1 hr 30 mins | 300 pts
- [Build an Agent with Agentforce](https://trailhead.salesforce.com/content/learn/projects/build-an-agent-with-agentforce) — 1 hr 30 mins | 500 pts
- [Agentforce for Developers](https://trailhead.salesforce.com/content/learn/modules/agentforce-for-developers) — 2 hrs | 400 pts

## 📚 Resources

- [📄 Release in a Box PDF](./release-in-a-box.pdf)
- [🔗 Feature Impact Page](https://help.salesforce.com/s/articleView?id=release-notes.rn_feature_impact.htm&release=262&type=5&language=en_US)
- [📋 Release Notes](https://help.salesforce.com/s/articleView?id=release-notes.rn_release_notes.htm&release=262&type=5&language=en_US)
