# Lightning Web Components (LWC) — Spring '25

> **Release:** Spring '25
> **Gerado em:** 2026-06-12 20:52 UTC
> **Fonte:** https://help.salesforce.com/s/articleView?id=release-notes.salesforce_release_notes.htm&release=254&type=5&language=pt_BR

---

## Lightning Web Components (LWC) — Spring '25



### Enable LWC Stacked Modals (Release Update)

Como parte da migração interna do Salesforce do Aura para LWC, mais modais no Lightning Experience agora são renderizados usando o LWC. Essa atualização fornece desempenho aprimorado, especialmente ao trabalhar com inúmeros campos em um modal de criação ou edição de registro. Agora você também pode usar Formulários dinâmicos em um modal aberto de um campo Criar da pesquisa na maioria das páginas de registro habilitadas para LWC. Quando você habilita essa atualização, espere pequenas mudanças no comportamento do modal. Essa atualização foi disponibilizada inicialmente na versão Summer '24.


[🔗 Leia mais no conteúdo original](https://help.salesforce.com/s/articleView?id=release-notes.rn_general_lwc_modals.htm&language=pt_BR&release=254&type=5)



### LWC API Version 63.0

Atualize a versão da API de seus componentes para usar novos recursos e melhorias. A versão dos componentes da Web Lightning garante que os componentes existentes não sejam afetados quando o Salesforce envia novos recursos, correções de bugs e melhorias de desempenho que alteram o comportamento existente. O controle de versões também ajuda o Salesforce a descontinuar os recursos legados.


[🔗 Leia mais no conteúdo original](https://help.salesforce.com/s/articleView?id=release-notes.rn_lwc_versioning.htm&language=pt_BR&release=254&type=5#rn_lwc_versioning)



### Custom Components Must Specify an API Version

A chave apiVersion é um elemento obrigatório para todos os componentes personalizados. Componentes personalizados que foram salvos antes sem uma chave apiVersion no arquivo de ajustes do componente .js-meta.xml têm uma chave apiVersion adicionada ao arquivo de ajustes automaticamente quando o componente é recuperado do Salesforce.


[🔗 Leia mais no conteúdo original](https://help.salesforce.com/s/articleView?id=release-notes.rn_lwc_api_version_required.htm&language=pt_BR&release=254&type=5)



### Wire Adapters Have Improved Type Checking

A partir da versão Spring '25, os usuários do TypeScript terão uma melhor verificação de tipo de configuração de @wire e valores de propriedade. A verificação de tipo também resolve propriedades reativas para o tipo usado pelo componente. Por exemplo, uma string que começa com $ como $reactiveProp.


[🔗 Leia mais no conteúdo original](https://help.salesforce.com/s/articleView?id=release-notes.rn_lwc_wire_type_check.htm&language=pt_BR&release=254&type=5)



### Update JavaScript Selectors to Remove Extra Whitespace

Revise seus seletores JavaScript para ignorar espaços em branco (espaços, guias etc.). Essa alteração elimina inconsistências na renderização de espaço em branco extra.


[🔗 Leia mais no conteúdo original](https://help.salesforce.com/s/articleView?id=release-notes.rn_lwc_style_class.htm&language=pt_BR&release=254&type=5)



### Develop Lightning Web Components Faster in a Real-Time Preview of...

O Desenvolvedor local agora está disponível ao público em geral para aplicativos Lightning. Fizemos algumas alterações desde a versão beta. Ao usar o Local Dev, você pode desenvolver seus componentes da Web Lightning em uma visualização em tempo real do aplicativo Lightning sem implementar código nem atualizar manualmente o navegador. O desenvolvedor local está em beta para sites do Lightning Web Runtime.


[🔗 Leia mais no conteúdo original](https://help.salesforce.com/s/articleView?id=release-notes.rn_lwc_local_dev.htm&language=pt_BR&release=254&type=5)



### New and Changed Lightning Web Components

Crie a interface do usuário facilmente com componentes novos e alterados.


[🔗 Leia mais no conteúdo original](https://help.salesforce.com/s/articleView?id=release-notes.rn_lwc_components.htm&language=pt_BR&release=254&type=5)



### New and Changed Modules for Lightning Web Components

Do more with Lightning web components by using modules.


[🔗 Leia mais no conteúdo original](https://help.salesforce.com/s/articleView?id=release-notes.rn_lwc_modules.htm&language=pt_BR&release=254&type=5)


