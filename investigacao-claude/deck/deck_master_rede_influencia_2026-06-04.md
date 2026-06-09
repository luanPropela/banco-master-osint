---
marp: true
theme: oboya
paginate: true
size: 16:9
header: 'Rede de Influência do Banco Master · material para a equipe de pesquisa'
footer: 'by Luan Carvalho'
---

<!-- _class: cover -->

<div class="wordmark">REDE MASTER · OSINT</div>

# A Rede de Influência do Banco Master

## Entendendo o caso e desenhando um motor de grafos sobre dados públicos

by **Luan Carvalho**

<div class="legend">
Material para a equipe de pesquisa: <strong>o que é o caso</strong> (com exemplos), <strong>a virada conceitual dos dois grafos</strong> e <strong>o que vamos construir</strong>.
</div>

---

# O que vamos pesquisar

Não é "ler a reportagem". É **reconstruir e medir**, a partir de **dado público**, a rede de influência do Banco Master — e mostrar, com método reproduzível, **onde** estavam as fraudes.

<div class="cols">
<div class="ba-after">
<span class="lbl">A PERGUNTA</span>

Dá para sair da *narrativa jornalística* e chegar à *prova em dado público* — mapeando a rede como um **grafo** e detectando as fraudes por suas **assinaturas** estruturais?
</div>
<div class="ba-after">
<span class="lbl">POR QUE IMPORTA</span>

A fraude foi desenhada para **não aparecer** nos controles do regulador. Reconstruí-la a partir de fontes abertas é um exercício de transparência — e um método replicável para o "próximo Master".
</div>
</div>

> Fio condutor do deck: **caso → a virada dos dois grafos → prova de conceito (SDG II) → o motor que vamos construir.**

---

# Conceitos-chave — nivelando a equipe

Para acompanhar o caso é preciso dominar alguns instrumentos. Definição **funcional** (o que faz na prática), não jurídica.

| Termo | O que é (definição funcional) |
|---|---|
| **CDB** (Certif. de Depósito Bancário) | Título que o banco emite para captar dinheiro do público; o investidor empresta ao banco e recebe juros. Garantido pelo FGC até **R$ 250 mil por CPF**. |
| **Letra Financeira (LF)** | Dívida de longo prazo emitida por bancos. **Sem cobertura do FGC** — quem compra assume o risco do banco. |
| **FIDC** | Fundo que compra "direitos a receber" (empréstimos, duplicatas). Quem aplica vira **cotista** e carrega o risco dos créditos. |
| **FIDC-NP** (Não Padronizado) | FIDC de regras frouxas: aceita créditos problemáticos, restrito a investidor profissional, **pouca transparência pública**. |
| **CCB** (Céd. de Crédito Bancário) | Documento que formaliza um empréstimo; pode ser **cedido** (vendido) a um fundo. |
| **Cessão de crédito** | Vender um empréstimo a receber a terceiros. Quem vende é o **cedente** e recebe caixa agora. |
| **Cotista / Lastro** | Cotista = quem investe no fundo. Lastro = a garantia real do crédito (*existe mesmo o devedor e a dívida?*). |
| **Administrador vs. Gestor** | Administrador responde legalmente pelo fundo; gestor decide os investimentos. **Empresas diferentes** — o que dilui a responsabilização. |

---

# O caso em uma página

Banco Master (controlado por Daniel Vorcaro) entrou em liquidação extrajudicial pelo Banco Central em **18/11/2025** — tratada como a maior fraude bancária da história do Brasil.

<div class="metrics">
<div class="metric"><span class="num">R$ 80 bi</span><span class="cap">ativos declarados</span></div>
<div class="metric"><span class="num">R$ 4 mi</span><span class="cap">em caixa real</span></div>
<div class="metric"><span class="num">R$ 50–52 bi</span><span class="cap">rombo estimado</span></div>
<div class="metric"><span class="num">~R$ 40 bi</span><span class="cap">pagos pelo FGC</span></div>
</div>

<p class="small">Fonte: BACEN; Folha de S.Paulo; Agência Brasil.</p>

---

# A isca: o CDB a 140% do CDI

O Master captou volumes crescentes pagando muito acima do mercado. Por que é um sinal de alerta?

**Exemplo:** com o CDI a ~**10% a.a.**, um CDB a 100% paga R$ 10 por R$ 100; a **140%, paga R$ 14** — 40% a mais. Para honrar isso, o banco precisaria emprestar a tomadores que pagassem ainda mais caro — carteiras de altíssimo risco ou **inexistentes**.

<div class="metrics">
<div class="metric"><span class="num">~140%</span><span class="cap">do CDI — oferecido pelo Master</span></div>
<div class="metric"><span class="num">~100%</span><span class="cap">do CDI — média de mercado</span></div>
<div class="metric"><span class="num">R$ 250 mil</span><span class="cap">teto do FGC por CPF</span></div>
</div>

> Sem ativos rentáveis suficientes, o banco emite **CDB novo para pagar o CDB que vence** — pirâmide financeira clássica. O FGC dava conforto ao investidor PF, que não percebia o risco.

<p class="small">Fonte: Polícia Federal; CartaCapital; Seu Dinheiro.</p>

---

# A mecânica da fraude em 5 passos

1. <span class="pill warm">ISCA</span> Capta caixa real vendendo **CDB a 140% do CDI** (e Letras Financeiras)
2. <span class="pill">CRÉDITO</span> Empresta a **empresas-fachada** (Tirreno, MKS, Banvox, Lormont…)
3. <span class="pill">ESTRUTURA</span> As fachadas aplicam o dinheiro em **FIDC**
4. <span class="pill">CICLO</span> O fundo **recompra os empréstimos** que o próprio Master concedeu
5. <span class="pill alert">FRAUDE</span> O risco de calote **sai do balanço do banco** — some dos controles do BC

> Resultado: no papel o banco fica "saudável" e abre espaço para captar ainda mais CDB. O calote fica escondido no fundo, sobre o cotista.

<p class="small">Fonte: ICL/Folha (26/05/2026); CNN Brasil.</p>

---

# A tese: não foi só nos fundos próprios

> "O Master era o **MOTOR** — originava os empréstimos fictícios e a pirâmide de CDB. Os terceiros eram a **LAVANDERIA** e a porta de saída. O risco foi empurrado para fora do balanço regulado, para dentro de veículos 'independentes' de terceiros, para o calote não aparecer no Banco Central."

<div class="cols">
<div class="ba-after">
<span class="lbl">PRÓPRIO DO MASTER</span>

- Originação dos empréstimos fictícios
- Pirâmide de CDB a 140% do CDI
- Master S/A Corretora administrando parte dos fundos
</div>
<div class="ba-before">
<span class="lbl">TERCEIROS (a teia)</span>

- Gestora Reag/CBSF — administrou os FIDC-núcleo
- BRB (banco público) — R$ 12,2 bi
- RioPrevidência R$ 3,6 bi + 18 RPPS R$ 1,86 bi
- Fachadas: Tirreno, MKS, Banvox, Lormont, Super, NGV
</div>
</div>

<p class="small">Fonte: Folha de S.Paulo; Agência Brasil; CNN Brasil.</p>

---

# A teia: quem são os terceiros envolvidos

O esquema não operava isolado: uma rede de gestoras, bancos, previdências e fachadas dava **aparência de legalidade** e abastecia o caixa.

<div class="grid3">
<div class="tile"><span class="lbl">Reag / CBSF</span><p>Gestora independente; administrava os FIDC centrais (SDG II, Hans 95, Anna). Liquidada pelo BC em 15/01/2026; alvo da Operação Carbono Oculto. "Um entre centenas de clientes" — mas no núcleo das estruturas.</p></div>
<div class="tile"><span class="lbl">BRB — Banco de Brasília</span><p>Banco público do DF. Comprou <strong>R$ 12,2 bi</strong> em carteiras que o Master pegou da fachada Tirreno por R$ 6,7 bi sem pagar. Foi a principal fonte de caixa real.</p></div>
<div class="tile"><span class="lbl">RioPrevidência + 18 RPPS</span><p>Previdência de servidores. RioPrev aplicou <strong>R$ 3,6 bi</strong>; outros 18 regimes próprios, <strong>R$ 1,86 bi</strong>. Aposentadoria pública exposta ao risco do banco.</p></div>
<div class="tile"><span class="lbl">Empresas-fachada</span><p>Tirreno, MKS, Lormont (Nelson Tanure), Banvox (Maurício Quadrado), Super, NGV — cedentes/compradoras nos FIDC. O <strong>lastro real</strong> dessas cessões é o que se investiga.</p></div>
</div>

<p class="small">Fonte: Agência Brasil; CNN Brasil; Metrópoles; Folha de S.Paulo.</p>

---

# A virada conceitual: por que DOIS grafos?

Uma fraude bancária se esconde nos **dois lados de um balanço**. Para enxergá-la, separamos a rede em dois grafos complementares — e depois os reconectamos.

<div class="cols">
<div class="ba-after">
<span class="lbl">GRAFO DA TEIA → o ATIVO</span>

Para **onde o dinheiro foi** e onde o crédito podre foi enterrado. Responde: *"como esconderam o rombo?"*
</div>
<div class="ba-after">
<span class="lbl">GRAFO DE FINANCIAMENTO → o PASSIVO</span>

**De onde veio o dinheiro** que abasteceu tudo (o combustível). Responde: *"quem pagou a conta?"*
</div>
</div>

> Cada grafo responde uma pergunta diferente. **Só juntos** — e soldados no nó Banco Master — explicam a fraude. Os próximos slides destrincham cada um e o ponto de solda.

---

# Os dois lados do mesmo balanço

| | **Grafo da teia** (ativo) | **Grafo de financiamento** (passivo) |
|---|---|---|
| **Lado do balanço** | Para onde o dinheiro foi; onde o crédito podre se escondeu | De onde veio o dinheiro (o combustível) |
| **Arestas** | cedeu_crédito · é_cotista · administra/gere · possui_debênture | emitiu_CDB/LF · aportou_em (quem comprou o CDB) |
| **Exemplos** | SDG II ← CCB Lormont; Anna → Hans 95; admin Reag/CBSF | RPPS / fundos / PF → seguram CDB/LF do Master |
| **Pergunta que responde** | *"como esconderam o rombo?"* | *"quem pagou a conta / financiou a pirâmide?"* |

<p class="small">É a mesma rede vista por dois ângulos contábeis — ativo e passivo.</p>

---

# Grafo da teia (o ATIVO): como esconderam o rombo

É o lado **onde o crédito podre foi enterrado** — não num cofre só, mas numa **rede de fundos de terceiros**. As arestas são relações de **crédito e controle**: quem cedeu crédito a quem, quem é cotista de qual fundo, quem administra/gere.

<div class="flow">
<div class="step"><span class="k">Fachadas</span><span class="v">Lormont, Banvox, Super, NGV</span></div>
<div class="step"><span class="k">cedem créditos</span><span class="v">CCBs e debêntures</span></div>
<div class="step"><span class="k">SDG II (FIDC)</span><span class="v">recebe e "guarda" o risco</span></div>
<div class="step"><span class="k">Reag / CBSF</span><span class="v">administra e gere o fundo</span></div>
</div>

**Lendo o exemplo:** a CCB do **Lormont** é cedida ao **SDG II** (aresta `cedeu_crédito`); o **Anna** é cotista do SDG II e é controlado pelo **Hans 95** (aresta `é_cotista`); tudo administrado pela **Reag/CBSF** (aresta `administra/gere`).

<p class="small">Fonte: Demonstração Financeira do SDG II (FNET); CVM registro_fundo.</p>

---

# Grafo do financiamento (o PASSIVO): quem pagou a conta

É o **combustível**. Para manter a roda girando, o Master precisava de **caixa real** — e o captava **emitindo CDB (140% do CDI) e Letras Financeiras**. As arestas: `emitiu_CDB/LF` (Master emite) e `aportou_em` (o investidor compra). Quem segura esses papéis aparece nas **carteiras públicas** de fundos e previdências.

<div class="metrics">
<div class="metric"><span class="num">R$ 12,2 bi</span><span class="cap">BRB — compra de carteiras (caixa)</span></div>
<div class="metric"><span class="num">R$ 3,6 bi</span><span class="cap">RioPrevidência</span></div>
<div class="metric"><span class="num">R$ 1,86 bi</span><span class="cap">18 RPPS estaduais/municipais</span></div>
<div class="metric"><span class="num">+ fundos</span><span class="cap">ex.: Hans 95 negociou CDB do Master</span></div>
</div>

> Diferença crucial: o financiador (a previdência, o investidor PF) pôs **dinheiro de verdade**. Esse caixa é que alimentou a originação dos empréstimos fictícios.

<p class="small">Fonte: Agência Brasil; CNN Brasil; Metrópoles; CVM.</p>

---

# O Master liga tudo: o ciclo fecha o laço

Os dois grafos **não vivem separados** — o ponto de solda é o próprio banco. O caixa entra pelo CDB (passivo), é emprestado às fachadas, vira aplicação nos fundos da teia, e o fundo **recompra o crédito do Master** — fechando o ciclo.

<div class="cycle">
<div class="node"><span class="t">Investidores · RioPrevidência · fundos</span><span class="s">compram CDB / LF</span></div>
<div class="node master"><span class="t">BANCO MASTER</span><span class="s">capta caixa (passivo) e origina</span></div>
<div class="node"><span class="t">Empréstimos a empresas-fachada</span><span class="s">MKS, Lormont, Banvox…</span></div>
<div class="node"><span class="t">Fachadas aplicam em fundos da teia</span><span class="s">Anna / Hans 95</span></div>
<div class="node"><span class="t">SDG II recompra os créditos do próprio Master</span><span class="s">o risco sai do balanço (ativo)</span></div>
</div>

<div class="loop">↩ O CDB é a <strong>entrada</strong> de caixa; o SDG II é a <strong>saída</strong> onde o crédito podre é enterrado. Master = motor · terceiros = lavanderia.</div>

---

# Exemplo trabalhado: seguindo o dinheiro

Cada peça abaixo é **real e pública**. Juntas, mostram o mecanismo do começo ao fim.

<div class="cycle">
<div class="node"><span class="t">1 · Captação (passivo)</span><span class="s">RioPrevidência aplica R$ 970 mi em Letras Financeiras do Master (out/2023–jul/2024) → Master tem caixa</span></div>
<div class="node master"><span class="t">2 · Originação</span><span class="s">o Master concede crédito a empresas ligadas — ex.: Lormont (de Nelson Tanure)</span></div>
<div class="node"><span class="t">3 · Ocultação (ativo)</span><span class="s">27/02/2024 — o próprio Banco Master cede ao SDG II uma CCB do Lormont por R$ 102,438 mi: o crédito sai do balanço</span></div>
<div class="node"><span class="t">4 · O risco vira do fundo</span><span class="s">o eventual calote agora é do cotista do SDG II — não do Master, não aparece no BC</span></div>
<div class="node"><span class="t">5 · Pode não valer nada</span><span class="s">o auditor não comprova o lastro de 62% dos créditos do SDG II → abstenção de opinião</span></div>
</div>

<p class="small"><strong>Honestidade metodológica:</strong> não afirmamos que o real específico da RioPrev virou o crédito específico do Lormont — o elo é o <em>ciclo</em>, soldado no Master. Cada cifra tem fonte pública (CVM/FNET; Agência Brasil).</p>

---

# O CDB "chega" no SDG II?

Pergunta natural — e a resposta exige precisão. São **dois sentidos**:

<div class="cols">
<div class="ba-before">
<span class="lbl">DIRETO (como ativo do fundo): NÃO</span>

- O SDG II guarda **créditos** (R$ 3,36 bi), não CDB
- Na DF, o Master só aparece como **cedente** — nunca como emissor de CDB
- ~R$ 50 mi em CDB (dez/2024), zero em vários meses — não identificado como do Master
- O CDB do Master vive em **outros** veículos (ex.: Hans 95) e nos financiadores externos
</div>
<div class="ba-after">
<span class="lbl">INDIRETO (pelo ciclo): SIM</span>

- O SDG II está na **ponta-ativo** do mesmo laço que o CDB financia
- O caixa do CDB virou os **R$ 1,1 bi** cedidos direto pelo Master — que o SDG II recomprou
- É o **elo essencial** entre os dois grafos
</div>
</div>

> O CDB não **entra** no SDG II. O CDB **paga** pelo que o SDG II esconde.

<p class="small">Fonte: CVM Informe Mensal de FIDC; DF do SDG II (FNET).</p>

---

# Prova de conceito: reconstruímos o SDG II

A reportagem (Folha/ICL) descreve o **SDG II** como o receptor dos créditos podres. Nós reproduzimos, **só com dado público da CVM**, 10 das 11 afirmações quantitativas da matéria.

<div class="pill alert">10 de 11 afirmações reproduzidas a partir de fonte pública</div>

**Duas fontes, dois níveis:**

- **Informe Mensal de FIDC** (dados abertos) → os **agregados** (PL, nº de cotistas, inadimplência)
- **Demonstrações Financeiras via API do FNET** → a **carteira nominal** (cedente, devedor, debênture)

<p class="small">Fonte: CVM; FNET; Folha de S.Paulo / ICL.</p>

---

<!-- _class: dense -->

# Os números batem

| Afirmação da matéria | Reconstruído (fonte pública) |
|---|---|
| Tamanho do fundo R$ 5,4 bi | Ativo R$ **5,455 bi** (dez/2025) |
| 2 cotistas | **2 cotistas** (jan/2025–jan/2026) |
| Vendido direto pelo Master ≥ R$ 1,1 bi | **R$ 1,129 bi** — 2 cessões em 19/12/2024 |
| Lormont via Master R$ 102 mi | **R$ 102,438 mi** (CCB, 27/02/2024) |
| Debênture Banvox R$ 380 mi | **R$ 380,346 mi** |
| Super Empreendimentos R$ 22 mi | **R$ 22,012 mi** |
| Cotista MKS | <span class="status attention">NÃO confirmado</span> — nome de cotista não é público |

<p class="small">Fonte: CVM Informe Mensal de FIDC; Demonstrações Financeiras (FNET, id 963178).</p>

---

# O carimbo da fraude

O auditor emitiu **ABSTENÇÃO DE OPINIÃO** sobre a Demonstração Financeira de 2024 do SDG II.

<div class="metrics">
<div class="metric"><span class="num">62%</span><span class="cap">dos R$ 6,53 bi em direitos creditórios SEM comprovação de lastro</span></div>
</div>

**Estrutura do fundo — terceiro independente, não o Master:**

<div class="grid3">
<div class="tile"><span class="lbl">Administrador</span><p>Reag Trust DTVM (= CBSF DTVM)<br>CNPJ 34.829.992/0001-86</p></div>
<div class="tile"><span class="lbl">Gestor</span><p>CBSF Trust Adm. de Recursos<br>CNPJ 23.863.529/0001-34</p></div>
<div class="tile"><span class="lbl">Grupo</span><p>Reag / CBSF<br>Não o próprio Master</p></div>
</div>

> "Em linguagem de auditoria, é o mais próximo de 'não conseguimos confirmar que esses créditos existem'."

<p class="small">Fonte: Demonstrações Financeiras SDG II (FNET, exercício 2024); CVM registro_fundo.</p>

---

# O motor: a tese vira um problema de grafo

<div class="stack">
<div class="band top"><span class="t">Ingestão</span><span class="s">Fontes públicas: CVM · BACEN · Receita Federal</span></div>
<div class="band mid"><span class="t">Resolução de entidades</span><span class="s">Normalizar CNPJ/CPF; resolver renomeações (ex.: Reag → CBSF)</span></div>
<div class="band mid"><span class="t">Grafo tipado</span><span class="s">NetworkX/igraph para análise; Neo4j para exploração interativa</span></div>
<div class="band mid"><span class="t">Detectores</span><span class="s">Ciclo · concentração · comunidade · betweenness · anomalia temporal</span></div>
<div class="band mid"><span class="t">Verificação adversarial</span><span class="s">Confronto contra Demonstração Financeira e reportagem</span></div>
<div class="band base"><span class="t">Saída</span><span class="s">Ranking de suspeitos por score de anomalia + grafo interativo</span></div>
</div>

> **FRAUDE** não é um nó — é uma **assinatura topológica + financeira** sobre o grafo. O motor **rankeia** veículos/fluxos suspeitos e **valida** contra casos já provados (SDG II).

---

# Modelo de grafo: nós e arestas tipadas

| Tipo de nó | Identificador |
|---|---|
| Pessoa física · Empresa | CPF · CNPJ |
| Fundo (FI / FIDC / FIP / FII) | CNPJ CVM |
| Instituição financeira · Prestador (admin/gestor/custodiante/auditor) | CNPJ / ISPB |
| Órgão público / RPPS · Título (CDB/LF/debênture/CCB/cota) | CNPJ · ISIN |

| Aresta | Semântica |
|---|---|
| `é_sócio_de` · `administra` · `gere` · `custodia` | controle e governança |
| `é_cotista_de` · `aportou_em` | participação / financiamento |
| `cedeu_crédito_a` · `é_devedor_de` · `sacado` | fluxo de crédito |
| `possui_título_de` · `emitiu` · `comprou_carteira_de` | instrumento financeiro |

<p class="small">Cada aresta carrega: <strong>data · valor · fonte · carimbo de evidência</strong> (público / reportagem / restrito).</p>

---

<!-- _class: dense -->

# Os detectores: onde está a fraude

| Assinatura de fraude | Algoritmo | Exemplo no caso |
|---|---|---|
| Ciclo de triangulação | Detecção de ciclos (Johnson) | CDB → Master → fachada → fundo → recompra |
| Auto-negócio (parte ligada) | Flag `emissor_ligado = S` | KATCH → UPPER (R$ 32,6 mi = 99% do PL) |
| Concentração anômala | Índice de Herfindahl | SDG II (2 cotistas); Maranta (97% Lormont) |
| Cluster de prestadores | Comunidade (Louvain / Leiden) | Núcleo inteiro sob Reag / CBSF |
| Lastro ausente / inadimplência | Tab. VII + parecer do auditor | Abstenção SDG II (62% sem lastro) |
| Pontes críticas | Betweenness / articulação | Anna — ponte Hans 95 → SDG II |
| Anomalia temporal | Event-study vs. liquidação | Reag cresceu 14× em 5 anos |

<p class="small">Cada candidato passa por <strong>verificação adversarial</strong> contra a DF / reportagem antes de ser apontado.</p>

---

<!-- _class: dense -->

# Fontes de dados — tudo público e programático

| Fonte | O que dá | Status |
|---|---|---|
| Minha Receita / Receita QSA | Sócios, capital, fachadas | Público |
| CVM `registro_fundo.csv` (RCVM 175) | Administrador + gestor de todos os fundos (incl. FIDC) | Público |
| CVM Informe Mensal de FIDC | Carteira agregada, nº de cotistas, inadimplência | Público |
| CVM CDA (FI/555) | Carteira por ativo + flag `emissor_ligado` | Público |
| CVM Informe Diário · PAS | PL/captação/resgate diário · processos sancionadores | Público |
| FNET (API) | Demonstrações Financeiras = carteira nominal + parecer | Público |
| BACEN IF.data · CADPREV/DAIR | Balanços trimestrais · aplicações dos RPPS | Público |
| Empréstimo Master → fachada | — | Sigilo bancário *(aflora via FIDC)* |

<p class="small">Nem tudo do Master foi fraude — por isso o método <strong>PONTUA</strong> suspeita, não rotula.</p>

---

# Roadmap — o que vamos entregar

<div class="grid3">
<div class="tile"><span class="lbl">1 · Motor de detecção</span><p>Grafo + detecção de ciclos + comunidade + score de suspeição, validado nos casos já provados: SDG II, fundos <em>'95'</em> e Anna.</p></div>
<div class="tile"><span class="lbl">2 · Balanço contrafactual</span><p>Via BACEN IF.data: o balanço reportado vs. a versão <em>"se fosse lícito"</em> — re-incorporar créditos podres, zerar ativos fictícios → medir alavancagem real e o rombo.</p></div>
<div class="tile"><span class="lbl">3 · Grafo do financiamento do CDB</span><p>Varrer CDA dos fundos + DAIR dos RPPS por emissor = Banco Master → mapa de quem financiou a pirâmide, ligado ao nó Master.</p></div>
</div>

> Entregas sequenciais: **Motor → Balanço contrafactual → Grafo de financiamento.** A fraude é o *ciclo fechado* que atravessa as duas camadas.

<p class="small">Métrica-alvo do bloco 2: <strong>reportado − fictício/circular = patrimônio real</strong> (quão alavancado e quão golpista).</p>

---

# Rigor e limitações

- <span class="pill">Estrutura ≠ culpa</span> O grafo mostra relações cadastrais; o score sinaliza; a Demonstração Financeira e o PAS **confirmam**.
- <span class="pill">Score é triagem</span> Não acusa — validado com ground truth (precisão/recall nos fundos já confirmados).
- <span class="pill alert">Sigilo bancário</span> Empréstimo Master → fachada não é público; aflora **apenas** via carteira de FIDC.
- <span class="status ok">Rastreabilidade</span> Carimbo de evidência em toda aresta: `público` / `reportagem` / `restrito`.
- Nomes de cotistas de FIDC restrito **não são públicos**; dados são snapshot, sem histórico completo.
- 100% reprodutível — Python + fontes abertas, em ambiente isolado.

> "Mostrar evidência, não asserção — toda cifra rastreável a um documento público citável."

---

# Fontes & referências

**Dados públicos**
- CVM Dados Abertos — `registro_fundo.csv`, Informe Mensal de FIDC, CDA, Informe Diário, PAS
- FNET (B3/CVM) — Demonstrações Financeiras de fundos
- Receita Federal / Minha Receita — QSA e CNPJ
- BACEN IF.data — balanços trimestrais; CADPREV / Min. Previdência — DAIR dos RPPS

**Reportagens**
- Folha de S.Paulo / ICL Notícias · CNN Brasil · Agência Brasil · Metrópoles · NeoFeed

**Métodos & algoritmos**
- Blondel et al. (2008) — comunidades Louvain · Johnson (1975) — ciclos em grafos direcionados · Índice de Herfindahl-Hirschman

<p class="small">by Luan Carvalho · análise sobre dados públicos · 2026</p>
