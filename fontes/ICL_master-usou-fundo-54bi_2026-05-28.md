# Fonte-âncora — matéria do fundo SDG II

Referência verificável da reportagem que serve de *ground truth* para o grafo de fraude
(`data/csv/09_grafo_fraude_nodes.csv` / `10_grafo_fraude_edges.csv`, rótulo `ICL/Folha 2026-05-28`).

## Metadados

| Campo | Valor |
|---|---|
| Título | **Master usou fundo de R$ 5,4 bi para esconder dívidas de empresas ligadas ao banco** |
| Linha fina | Manobra permitia ao banco 'limpar' o balanço, excluindo a inadimplência |
| Autor | Lucas Marchesini (**Folhapress**) — apuração original da Folha de S.Paulo |
| Publicação | 26/05/2026 07h01 (atualizado 26/05/2026 07h34) |
| Veículo (espelho usado no chat) | ICL Notícias |
| URL ICL | https://iclnoticias.com.br/master-usou-fundo-54-bi-para-esconder-dividas/ |
| Data de captura | 03/06/2026 |
| Período das operações descritas | 2020 a 2024 |

> ⚠️ O grafo rotula a fonte como `2026-05-28`, que é a data em que o link foi compartilhado no grupo (msg do Túlio, 28/05). A **data real de publicação é 26/05/2026**. Recomendo corrigir o rótulo para `ICL/Folhapress 2026-05-26` ou separar `data_publicacao` de `data_coleta`.

## Arquivo arquivado (evidência visual)

| Arquivo | `ICL_master-usou-fundo-54bi_2026-05-28.pdf` |
|---|---|
| Tamanho | 4 663 747 bytes |
| SHA-256 | `1c6539e4fb09f328bc7f1ac6f56c217c61537de597ef76283c870875b5f1de1d` |

Verificar integridade:

```bash
sha256sum -c fontes/ICL_master-usou-fundo-54bi_2026-05-28.pdf.sha256
# ou
sha256sum fontes/ICL_master-usou-fundo-54bi_2026-05-28.pdf
```

## Como reproduzir o arquivo (determinístico)

PDF gerado a partir da página real renderizada, via Chrome headless:

```bash
chrome --headless=new --disable-gpu --virtual-time-budget=20000 \
  --user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36" \
  --print-to-pdf="fontes/ICL_master-usou-fundo-54bi_2026-05-28.pdf" \
  "https://iclnoticias.com.br/master-usou-fundo-54-bi-para-esconder-dividas/"
```

> Observação: WebFetch/curl retornam **HTTP 403** (o ICL bloqueia user-agents não-navegador). Por isso a captura é feita com um navegador real (headless ou MCP). O texto abaixo foi extraído da página renderizada e confere com o PDF.

---

## Mapeamento: cada aresta do grafo ↔ trecho exato da matéria

Isto é o que torna o grafo **auditável**: toda relação financeira do núcleo SDG II tem uma frase de origem.

| Aresta no grafo | Valor | Trecho literal da matéria |
|---|---|---|
| `SDG_II` é FIDC ativo | R$ 5,4 bi | "O fundo SDG II continua ativo, com R$ 5,4 bilhões" |
| `MASTER → SDG_II` (absorção) | R$ 3,6 bi | "O fundo SDG II comprou R$ 3,6 bilhões em empréstimos ligados à fraude de Daniel Vorcaro" |
| `MASTER → SDG_II` CESSAO_CREDITO direta | R$ 1,1 bi | "pelo menos R$ 1,1 bilhão são de direitos creditórios vendidos diretamente pelo Master ao fundo" |
| `SDG_II → ANNA` TEM_COTISTA | — | "tem dois cotistas... Um deles é o Hans 95... por meio do fundo Anna" |
| `SDG_II → MKS` TEM_COTISTA | — | "O outro é a empresa MKS Soluções Integradas, uma das 36 companhias que... fizeram empréstimos simulados no Master" |
| `ANNA ← HANS_95` CONTROLADO_POR | — | "A participação do Hans 95 se dá por meio do fundo Anna, um dos seis fundos fraudulentos identificados pelo BC" |
| `SDG_II → LORMONT` CREDITO_A_RECEBER | R$ 553 mi | "A companhia que mais recebeu é a Lormont Participações, com quase R$ 553 milhões" |
| `MASTER → LORMONT` CESSAO_CREDITO | R$ 102 mi | "Desse total, R$ 102 milhões pelo menos foram vendidos ao fundo pelo Master. A empresa é ligada ao empresário Nelson Tanure" |
| `SDG_II → BANVOX` POSSUI_DEBENTURE | R$ 380 mi | "O SDG II possui uma debênture do Banvox no valor de R$ 380 milhões" |
| `BANVOX → DV_HOLDING` TRANSFERENCIA_DIVIDA | R$ 380 mi | "Hoje essas debêntures estão em nome da DV Holding... A troca aconteceu quando Quadrado saiu do Master" |
| `SDG_II → SUPER_EMPR` CREDITO_A_RECEBER | R$ 22 mi | "O fundo tem R$ 22 milhões em créditos a receber da empresa [Super]. A Super funcionava como o braço financeiro de Vorcaro" |
| `LANCIA → NGV_SPE` POSSUI_DEBENTURE | R$ 30 mi | "duas debêntures diferentes que o fundo [Lancia!] possui da NGV SPE, totalizando R$ 30 milhões" |
| `NGV_SPE → LANCIA` PRORROGACAO_CONTRATUAL | — | "os pagamentos foram sendo adiados... Em um último aditivo ao contrato, em 5 de abril de 2022..." |
| universo dos 82 FIDCs | R$ 65,5 bi | "O SDG II faz parte de um grupo de 82 FIDCs... possuem R$ 65,5 bilhões em ativos. O SDG II é o quarto maior" |

**Pistas operacionais para a coleta** (datas de balanço citadas — dizem qual competência puxar no Informe Mensal de FIDC):
- SDG II: balanço mostra os R$ 3,6 bi (competência não datada na matéria → puxar série).
- **Lancia!: "último balanço do fundo, de 30 de junho de 2024"** → competência `202406`.

---

## Transcrição integral (texto extraído da página renderizada)

> Master usou fundo de R$ 5,4 bi para esconder dívidas de empresas ligadas ao banco
> Manobra permitia ao banco 'limpar' o balanço, excluindo a inadimplência
> Lucas Marchesini (Folhapress) — 26/05/2026

(Folhapress) - O fundo SDG II comprou R$ 3,6 bilhões em empréstimos ligados a fraude de Daniel Vorcaro, em uma manobra para limpar o balanço do Master e se desfazer de créditos de má qualidade.

A venda desses créditos melhorou no papel a situação do Master, que passou a ter mais espaço financeiro para fazer novos empréstimos e também para captar recursos via CDB (Certificados de Depósito Bancário). Isso porque o impacto de um eventual calote saiu das contas do banco e ficou para os cotistas do SDG II. Depois da operação, a tarefa de cobrar os empréstimos também passou a ser do fundo.

Segundo apurações sobre a conduta do Master, o uso dos fundos fechava o ciclo de fraudes que funcionaria da seguinte maneira: 1. o banco captava dinheiro com CDBs; 2. o montante captado era emprestado para empresas de fachada, que aplicavam os valores em fundos; 3. os fundos por sua vez usavam parte do dinheiro para comprar os empréstimos feitos pelo Master para as companhias de fachada.

Esses empréstimos não eram cobrados, beneficiando empresas que não pagavam o que deviam. O calote, em vez de recair sobre as contas do Master - o que apareceria nos controles do BC (Banco Central) -, ficava no fundo, cuja denominação técnica é FIDC (Fundo de Investimentos em Direitos Creditórios).

O fundo SDG II continua ativo, com R$ 5,4 bilhões, e tem dois cotistas, segundo dados da CVM (Comissão de Valores Mobiliários).

Um deles é o Hans 95, fundo central na teia de fraudes do Master. A participação do Hans 95 se dá por meio do fundo Anna, um dos seis fundos fraudulentos identificados pelo BC no início das investigações contra o Master. O outro é a empresa MKS Soluções Integradas, uma das 36 companhias que, segundo as investigações, fizeram empréstimos simulados no Master.

As operações analisadas pela Folha aconteceram de 2020 a 2024.

Procurado por meio de sua assessoria de imprensa desde o último dia 8, o Banco Master não respondeu aos questionamentos da reportagem.

O balanço do SDG II mostra que, dos R$ 3,6 bilhões em ativos ligados à fraude do Master, pelo menos R$ 1,1 bilhão são de direitos creditórios vendidos diretamente pelo Master ao fundo. Não é possível saber quem tomou o empréstimo que originou essa operação.

A companhia que mais recebeu é a Lormont Participações, com quase R$ 553 milhões. Desse total, R$ 102 milhões pelo menos foram vendidos ao fundo pelo Master. A empresa é ligada ao empresário Nelson Tanure.

Tanure informou via assessoria de imprensa que foi cliente do Master "nas mesmas condições em que foi e segue sendo atendido por outras instituições financeiras, numa relação de operações financeiras corriqueiras que fazem parte do cotidiano da vida profissional de empresários e investidores de todo mercado de valores mobiliários".

"O empresário não tem conhecimento sobre hipotética cessão de crédito entre as próprias instituições financeiras", acrescentou.

Em segundo lugar entre as empresas que tomaram empréstimos depois repassados ao fundo vem o Banvox, que foi de Maurício Quadrado, ex-sócio de Vorcaro no Master. O SDG II possui uma debênture do Banvox no valor de R$ 380 milhões.

Hoje essas debêntures estão em nome da DV Holding, empresa de Vorcaro. A troca aconteceu quando Quadrado saiu do Master, entregando suas ações no banco. Nesse processo, as debêntures da Banvox, emitidas para a compra da participação no Master, passaram a se referir à DV.

"As eventuais operações de compra e venda dessas debêntures foram realizadas exclusivamente entre os respectivos detentores/credores dos papéis no mercado secundário, sem participação da Banvox", disse a assessoria de imprensa da empresa. "A Banvox Holding não vendeu nenhum ativo para qualquer FIDC ligado ao Master ou a terceiros".

Uma debênture é um título de dívida. Quem emite o papel se compromete a pagar um valor determinado em certo prazo. Em troca, recebe recursos.

Outra empresa que aparece no balanço do SDG II é a Super Empreendimentos e Participações. O fundo tem R$ 22 milhões em créditos a receber da empresa. A Super funcionava como o braço financeiro de Vorcaro e, como revelou a Folha, era dona da casa que o ex-banqueiro utilizava em Brasília.

O SDG II faz parte de um grupo de 82 FIDCs que fazem parte da rede do Master identificados pela Folha. Ao todo, eles possuem R$ 65,5 bilhões em ativos. O SDG II é o quarto maior da lista.

Outro fundo do grupo é o Lancia!, que ilustra bem como as empresas cujos empréstimos eram repassados aos fundos se livravam de ter que pagar a dívida.

No último balanço do fundo, de 30 de junho de 2024, há informações sobre duas debêntures diferentes que o fundo possui da NGV SPE, totalizando R$ 30 milhões. A empresa é ligada a Augusto Lima, que foi sócio de Vorcaro no Master.

As primeiras debêntures foram emitidas em 2018, com vencimento do valor principal em 10 de abril de 2022. Os juros começariam a ser pagos a partir de 10 de abril de 2020, mas os pagamentos foram sendo adiados. Em um último aditivo ao contrato, em 5 de abril de 2022, o vencimento da primeira parcela de juros foi para 10 de abril de 2024, e o pagamento do principal para 10 de abril de 2026. Não há mais informações sobre a debênture.

A segunda debênture tinha 16 de abril de 2020 como data de vencimento da primeira parcela. Em 2 de abril daquele ano, um aditivo jogou o prazo para 16 de abril de 2022. Em 5 de abril de 2022, onze dias antes da data do primeiro pagamento, uma mudança no contrato levou a data para 16 de abril de 2024.

Lima não respondeu aos questionamentos da reportagem.
