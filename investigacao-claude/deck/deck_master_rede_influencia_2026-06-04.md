---
marp: true
theme: oboya
paginate: true
size: 16:9
header: 'Rede de Influência do Banco Master · motor de grafos sobre dado público'
footer: 'by Luan Carvalho'
---

<!-- _class: cover -->

<div class="wordmark">REDE MASTER · OSINT</div>

# A Rede de Influência do Banco Master

## Um motor de grafos sobre dados públicos para mapear — e medir — a fraude

by **Luan Carvalho**

<div class="legend">
Do caso à reconstrução: <strong>o que aconteceu</strong>, <strong>como mapear</strong> e — principalmente — <strong>o que vamos construir</strong>.
</div>

---

# O Caso em Uma Página

Banco Master (controlado por Daniel Vorcaro) entrou em liquidação extrajudicial pelo Banco Central em **18/11/2025** — tratada como a maior fraude bancária da história do Brasil.

<div class="metrics">
<div class="metric"><span class="num">R$ 80 bi</span><span class="cap">ativos declarados</span></div>
<div class="metric"><span class="num">R$ 4 mi</span><span class="cap">em caixa real</span></div>
<div class="metric"><span class="num">R$ 50–52 bi</span><span class="cap">rombo estimado</span></div>
<div class="metric"><span class="num">~R$ 40 bi</span><span class="cap">pagos pelo FGC</span></div>
</div>

<p class="small">Fonte: BACEN; Folha de S.Paulo; Agência Brasil.</p>

---

# A Mecânica em 5 Passos

1. <span class="pill warm">ISCA</span> CDB a **140% do CDI** — mercado pagava ~100%
2. <span class="pill">CRÉDITO</span> Banco empresta a **empresas-fachada** (Tirreno, MKS, Banvox…)
3. <span class="pill">ESTRUTURA</span> Fachadas aplicam recursos em **FIDC**
4. <span class="pill">CICLO</span> Os fundos **recompram os empréstimos** do próprio Master
5. <span class="pill alert">FRAUDE</span> Risco de calote **sai do balanço** — some dos controles do BC

<p class="small">Fonte: ICL/Folha (26/05/2026); CNN Brasil.</p>

---

# A Tese: Não Foi Só nos Fundos Próprios

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

# A Virada Conceitual: São Dois Grafos

A fraude não cabe num grafo só. Ela vive nos **dois lados do balanço do Master** — e é a soma deles que fecha o caso.

| | Grafo da teia | Grafo de financiamento |
|---|---|---|
| **Lado do balanço** | Ativo — para onde o dinheiro foi e onde o crédito podre se escondeu | Passivo — de onde veio o dinheiro (o combustível) |
| **Arestas** | cedeu_crédito · é_cotista · administra/gere · possui_debênture | emitiu_CDB/LF · aportou_em |
| **Exemplos** | SDG II ← CCB Lormont; Anna → Hans 95; admin Reag/CBSF | RioPrevidência / fundos / PF seguram CDB/LF do Master |
| **Responde** | *"como esconderam o rombo?"* | *"quem pagou a conta?"* |

---

# Grafo da Teia (o ATIVO): como esconderam o rombo

Onde o crédito podre foi **enterrado** — uma rede de fundos de terceiros, não um cofre só.

<div class="flow">
<div class="step"><span class="k">Fachadas</span><span class="v">Lormont, Banvox, Super, NGV</span></div>
<div class="step"><span class="k">cedem créditos</span><span class="v">CCBs e debêntures</span></div>
<div class="step"><span class="k">SDG II (FIDC)</span><span class="v">recebe e "guarda" o risco</span></div>
<div class="step"><span class="k">Reag / CBSF</span><span class="v">administra e gere o fundo</span></div>
</div>

Cotistas do SDG II: **Anna**, controlado pelo **Hans 95** — fundo central da teia (um dos 6 apontados pelo BC).

<p class="small">Arestas: cedeu_crédito · é_cotista · administra/gere. Fonte: DF do SDG II (FNET); CVM.</p>

---

# Grafo do Financiamento (o PASSIVO): quem pagou a conta

O combustível: o Master captava caixa **emitindo CDB a 140% do CDI** e Letras Financeiras — comprados por terceiros.

<div class="metrics">
<div class="metric"><span class="num">R$ 12,2 bi</span><span class="cap">BRB — carteiras (fonte de caixa)</span></div>
<div class="metric"><span class="num">R$ 3,6 bi</span><span class="cap">RioPrevidência</span></div>
<div class="metric"><span class="num">R$ 1,86 bi</span><span class="cap">18 RPPS estaduais/municipais</span></div>
<div class="metric"><span class="num">+ fundos</span><span class="cap">ex.: Hans 95 negociou CDB do Master</span></div>
</div>

<p class="small">Arestas: emitiu_CDB/LF · aportou_em. Fonte: Agência Brasil; CNN Brasil; Metrópoles; CVM.</p>

---

# O Master Liga Tudo: o ciclo fecha o laço

Não são grafos separados — são uma engrenagem só, soldada no **Banco Master**.

<div class="cycle">
<div class="node"><span class="t">Investidores · RioPrevidência · fundos</span><span class="s">compram CDB / LF</span></div>
<div class="node master"><span class="t">BANCO MASTER</span><span class="s">capta caixa (passivo) e origina</span></div>
<div class="node"><span class="t">Empréstimos a empresas-fachada</span><span class="s">MKS, Lormont, Banvox…</span></div>
<div class="node"><span class="t">Fachadas aplicam em fundos da teia</span><span class="s">Anna / Hans 95</span></div>
<div class="node"><span class="t">SDG II recompra os créditos do próprio Master</span><span class="s">o risco sai do balanço (ativo)</span></div>
</div>

<div class="loop">↩ o crédito podre fica enterrado no fundo — o CDB é a entrada de caixa, o SDG II é a saída</div>

---

# O CDB "chega" no SDG II?

<div class="cols">
<div class="ba-before">
<span class="lbl">DIRETO (como ativo): NÃO</span>

- O SDG II guarda **créditos** (R$ 3,36 bi), não CDB
- Na DF, o Master só aparece como **cedente** — nunca como emissor de CDB
- ~R$ 50 mi em CDB (dez/2024), zero em vários meses — não identificado como do Master
- O CDB do Master vive em **outros** veículos (Hans 95) e nos financiadores externos
</div>
<div class="ba-after">
<span class="lbl">INDIRETO (pelo ciclo): SIM</span>

- O SDG II está na **ponta-ativo** do mesmo laço que o CDB financia
- O caixa do CDB virou os **R$ 1,1 bi** cedidos direto pelo Master — que o SDG II recomprou
- É o elo essencial entre os dois grafos
</div>
</div>

> O CDB não **entra** no SDG II. O CDB **paga** pelo que o SDG II esconde.

<p class="small">Fonte: CVM Informe Mensal de FIDC; DF do SDG II (FNET).</p>

---

# Prova de Conceito: reconstruímos o SDG II

Reportagem da Folha/ICL descreve o **Fundo SDG II** como receptor de créditos podres do Master. Reproduzimos **10 das 11 afirmações quantitativas** a partir exclusivamente de dados públicos da CVM.

<div class="pill alert">10 de 11 afirmações reproduzidas a partir de fonte pública</div>

**Fontes utilizadas:**

- **Informe Mensal de FIDC** — dados abertos e agregados (CVM)
- **Demonstrações Financeiras via API FNET** — carteira nominal (id 963178)

<p class="small">Fonte: CVM; FNET; Folha de S.Paulo / ICL.</p>

---

<!-- _class: dense -->

# Os Números Batem

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

# O Carimbo da Fraude

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

# O Motor: a tese vira um problema de grafo

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

# Modelo de Grafo: nós e arestas tipadas

| Tipo de nó | Identificador |
|---|---|
| Pessoa física | CPF |
| Empresa | CNPJ |
| Fundo (FI / FIDC / FIP / FII) | CNPJ CVM |
| Instituição financeira | CNPJ / ISPB |
| Prestador (admin · gestor · custodiante · auditor) | CNPJ |
| Órgão público / RPPS | CNPJ |
| Título (CDB · LF · debênture · CCB · cota) | ISIN / código |

| Aresta | Semântica |
|---|---|
| `é_sócio_de` · `administra` · `gere` · `custodia` | controle e governança |
| `é_cotista_de` · `aportou_em` | participação em fundo |
| `cedeu_crédito_a` · `é_devedor_de` · `sacado` | fluxo de crédito |
| `possui_título_de` · `emitiu` · `comprou_carteira_de` | instrumento financeiro |
| `punido_em` | evidência regulatória |

<p class="small">Cada aresta carrega: <strong>data · valor · fonte · carimbo de evidência</strong> — público / reportagem / restrito.</p>

---

<!-- _class: dense -->

# Os Detectores: onde está a fraude

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

# Fontes de Dados — tudo público e programático

| Fonte | O que dá | Status |
|---|---|---|
| Minha Receita / Receita QSA | Sócios, capital, fachadas | Público |
| CVM `registro_fundo.csv` (RCVM 175) | Administrador + gestor de todos os fundos (incl. FIDC) | Público |
| CVM Informe Mensal de FIDC | Carteira agregada, nº de cotistas, inadimplência | Público |
| CVM CDA (FI/555) | Carteira por ativo + flag `emissor_ligado` | Público |
| CVM Informe Diário | PL / captação / resgate diário | Público |
| CVM PAS | Processos sancionadores | Público |
| FNET (API) | Demonstrações Financeiras = carteira nominal + parecer | Público |
| BACEN IF.data | Balanços trimestrais (Master, BRB, Letsbank) | Público |
| CADPREV / DAIR | Aplicações dos RPPS (RioPrevidência etc.) | Público |
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

# Rigor e Limitações

- <span class="pill">Estrutura ≠ culpa</span> O grafo mostra relações cadastrais; o score sinaliza; a Demonstração Financeira e o PAS **confirmam**.
- <span class="pill">Score é triagem</span> Não acusa — validado com ground truth (precisão/recall nos fundos já confirmados).
- <span class="pill alert">Sigilo bancário</span> Empréstimo Master → fachada não é público; aflora **apenas** via carteira de FIDC.
- <span class="status ok">Rastreabilidade</span> Carimbo de evidência em toda aresta: `público` / `reportagem` / `restrito`.
- Nomes de cotistas de FIDC restrito **não são públicos**; dados são snapshot, sem histórico completo.
- 100% reprodutível — Python + fontes abertas, em ambiente isolado.

> "Mostrar evidência, não asserção — toda cifra rastreável a um documento público citável."

---

# Fontes & Referências

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
