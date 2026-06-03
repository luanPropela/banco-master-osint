# Análise técnica — o dataset reconstrói a fraude do SDG II?

> Branch `analise-reconstrucao-claude`. Análise de par sobre o estado do projeto em 03/06/2026, focada na pergunta que o Luan levantou no grupo: **"com isso aí, para aquele fundo da matéria, dá para reconstruir o que a matéria fala?"**
>
> Tudo aqui é verificável rodando `python analise/verificacao_reconstrucao.py` sobre os CSVs versionados.

---

## TL;DR — o veredito

**Hoje, não.** Mas a lacuna é única, conhecida e barata de fechar.

O projeto tem **duas camadas** sobrepostas que estão sendo confundidas como se fossem uma:

| Camada | O que é | Estado | Fonte real |
|---|---|---|---|
| **A. Societária / cadastral** | quem controla/é sócio de quem | ✅ **reconstruída e reproduzível** | QSA Minha Receita + cad_fi CVM |
| **B. Fluxo financeiro** | a *carteira* do SDG II (créditos cedidos pelo Master, debêntures Banvox, R$553 mi Lormont…) | ❌ **não reconstruída** | — (não coletada) |

O **grafo de fraude** (`09_grafo_fraude_nodes.csv` / `10_grafo_fraude_edges.csv`) — 53 nós, 78 arestas — é a **camada B**, mas hoje ele é **transcrição da reportagem**, não reconstrução a partir de dado. Prova empírica:

- **0 das 78 arestas** vêm do dado público estruturado que o pipeline baixa. 72 vêm da matéria ICL/Folha; 6 de consulta manual no CVMWeb (03/06).
- A carteira (CDA) efetivamente coletada cobre **4 fundos**: 3 FMP-FGTS (PL ~R$1,4 mi, ações Petrobras — irrelevantes) + KATCH FIDC. **Nenhum** dos 7 fundos do núcleo da fraude (SDG II, Anna, Hans 95, Lancia!, Termópilas, Gold Style, Maranta) tem carteira no dataset.

Ou seja: sabemos **que as entidades existem** e **como se relacionam societariamente**, mas **não temos o dado que prova o dinheiro circulando** — que é justamente o que a matéria afirma.

---

## 1. O que JÁ está reconstruído de dado público (o trabalho que vale)

Isto é sólido e o Carlyle merece crédito — é reproduzível por qualquer um com Python:

1. **Perímetro societário completo.** 134 empresas, 133 pessoas, 214 participações com data e cargo, via QSA da Minha Receita a partir de 47 seeds. Os CNPJs cadastrais de **20/20** nós do grafo que têm CNPJ estão no perímetro coletado — incluindo SDG II (`46909301000133`), Anna, Hans 95, Lancia!, Termópilas, Lormont, Super Empreendimentos, DV Holding, Banvox.
2. **As pontes societárias da matéria SÃO checáveis agora**, sem coletar mais nada:
   - Vorcaro → DV Holding (controlador) · Vorcaro → Super Empreendimentos · Quadrado → Banvox · Augusto Lima → NGV · Nelson Tanure → Lormont.
   - Essas arestas hoje estão marcadas `fonte: ICL/Folha`, mas **deveriam ser cruzadas com `03_participacoes_socio_empresa.csv`** e re-rotuladas como `fonte: QSA` quando baterem. Isso converte asserção em prova com o dado que já existe.
3. **Cruzamento QSA × PAS-CVM** (processos sancionadores): 14 matches de pessoas do perímetro Master que aparecem como acusadas na CVM. Camada inédita e legítima.
4. **O único achado de fluxo genuinamente derivado de dado: KATCH → UPPER.** Na CDA, o KATCH FIDC carregava **R$ 32,6 mi (~99% do PL) em cotas do UPPER FIDC**, marcado `EMISSOR_LIGADO = S` pela própria CVM. Isso é uma operação intragrupo confirmada por dado estruturado — o tipo de evidência que queremos para o SDG II. **Só que é outro fundo, não o da matéria.**

---

## 2. O que FALTA — e por quê (a causa-raiz técnica)

A matéria do SDG II se prova na **carteira do FIDC**: quais direitos creditórios ele carrega, quem foi o **cedente/originador** (o Banco Master), quais debêntures (Banvox R$380 mi), quais créditos a receber (Lormont R$553 mi, Super R$22 mi) e quem são os **cotistas** (MKS + Anna). Nada disso está no dataset.

**Por quê?** O coletor de carteira (`coleta/cvm_carteira.py`) baixa:

```
https://dados.cvm.gov.br/dados/FI/DOC/CDA/DADOS/cda_fi_{AAAAMM}.zip
```

Esse é o dataset de CDA do universo **FI (fundos 555 / FIF)**. **FIDC não reporta carteira aí.** FIDC tem dataset próprio:

```
Informe Mensal de FIDC
https://dados.cvm.gov.br/dataset/fidc-doc-inf_mensal
https://dados.cvm.gov.br/dados/FIDC/DOC/INF_MENSAL/DADOS/inf_mensal_fidc_{AAAAMM}.zip
```

O SDG II e o Anna são **FIDC-NP** → só aparecem no Informe Mensal de FIDC. Logo, rodar o pipeline atual mais 100 vezes **nunca** traz a carteira deles. É dataset errado, não volume insuficiente.

> ⚠️ **Nuance que precisa ser checada, não assumida:** Hans 95, Lancia! e Maranta estão cadastrados como **FI Multimercado Crédito Privado** (não FIDC) — pela regra deveriam estar no `cda_fi`. Estão ausentes mesmo assim. Duas hipóteses: (a) são fundos **restritos/exclusivos**, e fundos restritos frequentemente **não publicam CDA** no dado aberto da CVM; (b) os 3 meses amostrados (`202504, 202508, 202511`) não os pegaram. **Ação:** baixar mais meses de `cda_fi` e conferir. Se continuarem ausentes, é restrição de disclosure — e aí a fonte vira CVMWeb manual / Informe Mensal.

---

## 3. Aresta por aresta: o que dá para reconstruir do núcleo SDG II

Núcleo da matéria (ICL/Folha 28/05), classificado por **reconstrutibilidade com dado público**:

| Aresta da matéria | Valor | Reconstruível? | Com qual fonte |
|---|---|---|---|
| Master → SDG II (cessão de crédito direta) | R$ 1,1 bi | 🟡 **provável** | Informe Mensal FIDC — campo cedente/originador dos direitos creditórios |
| SDG II ⟶ tem cotistas MKS + Anna | — | 🟡 **provável** | Informe Mensal FIDC (cotistas) / CVMWeb cadastral |
| SDG II → crédito a receber Lormont | R$ 553 mi | 🟡 **provável** | Informe Mensal FIDC (carteira de direitos creditórios) |
| SDG II → debêntures Banvox | R$ 380 mi | 🟡 **provável** | Informe Mensal FIDC (carteira — valores mobiliários) |
| SDG II → crédito a receber Super Empr. | R$ 22 mi | 🟡 **provável** | Informe Mensal FIDC |
| Anna ← controlado por Hans 95 | — | 🟡 **parcial** | cotistas do Anna (Informe Mensal FIDC) |
| Lancia! → debêntures NGV SPE | R$ 30 mi | 🟡 **parcial** | `cda_fi` (se público) ou Informe Mensal |
| Vorcaro → DV Holding / Super; Quadrado → Banvox; A. Lima → NGV; Tanure → Lormont | — | ✅ **agora** | `03_participacoes` (QSA) — já no dataset |
| Banvox → DV Holding (transferência das debêntures) | R$ 380 mi | 🔴 **não** | mercado secundário / inquérito — sem dado público estruturado |
| Master → MKS (empréstimo simulado) | — | 🔴 **não** | sigilo bancário — só via carteira do FIDC se MKS for cedente |

Legenda: ✅ reconstruível com o que já existe · 🟡 reconstruível baixando o Informe Mensal de FIDC · 🔴 não reconstruível por dado público (fica como citação de reportagem, devidamente rotulada).

**Conclusão honesta para a apresentação:** o grafo final terá arestas de **dois status epistemológicos** — "verificado em dado público" e "afirmado por reportagem". Misturar os dois sem rótulo é o maior risco metodológico do trabalho. Separá-los explicitamente (campo `evidencia: dado_publico | reportagem | manual`) é o que dá credibilidade jornalística.

---

## 4. Caminho de reconstrução — priorizado até 15/06

**Passo 0 (1h, sem coletar nada): converter o que já dá.**
Cruzar `09/10_grafo_fraude` com `03_participacoes` e re-rotular como `fonte=QSA` toda aresta societária que bater. Resultado imediato: parte do grafo deixa de ser "segundo a matéria" e passa a ser "verificável no dado".

**Passo 1 (meio dia, o que move o ponteiro): novo coletor `coleta/cvm_fidc_mensal.py`.**
Baixar `inf_mensal_fidc_{AAAAMM}.zip` (2025-01 → 2026-04) e filtrar pelos CNPJs de SDG II, Anna, Termópilas (FIDC-NP). Extrair, por mês:
- **carteira de direitos creditórios** (valor, aging/atraso, cedente, sacado) → prova Master como cedente, os R$3,6 bi, Lormont, Super;
- **valores mobiliários em carteira** → debêntures Banvox/NGV;
- **cotistas** (nº e concentração) → MKS + Anna como os 2 cotistas do SDG II;
- **PL, inadimplência, provisão**.

**Passo 2 (rápido): completar o `cda_fi`** com mais meses e confirmar Hans 95 / Lancia! / Maranta. Se ausentes → marcar como "fundo restrito, sem CDA pública" (limite legítimo, documentar).

**Passo 3 (manual, o gargalo real que o Carlyle já começou): CVMWeb `fundosreg`** para o que o dado aberto não der (cadastro completo, diretor responsável, administrador/gestor — CBSF DTVM, CBSF Trust). Ele já puxou PL/carteira do SDG II manualmente em 03/06 → **estruturar isso numa tabela** (`carteira_manual_cvmweb`) com os mesmos campos do Passo 1, para o grafo tratar igual.

**Passo 4 (identificação): MKS, NGV SPE, Tirreno, Mídias Promotora** ainda sem CNPJ. Buscar via Minha Receita por razão social; se não vier, extrair o CNPJ do próprio Informe Mensal (aparecem como cedente/sacado/emissor na carteira do fundo). Isso fecha os 6 nós-empresa órfãos.

**Definição de "deu certo" para a banca:** *"a partir de dado público da CVM, reconstruímos a carteira do SDG II e mostramos que ≥X das relações financeiras descritas pela Folha aparecem nos números oficiais — com cada aresta rotulada por sua fonte de evidência."* Um fundo totalmente fechado vale mais que dez pela metade.

---

## 5. Riscos e limites a declarar (não escondê-los reforça o trabalho)

- **FIDC-NP é restrito a investidor profissional** → disclosure público é menor; alguns campos podem vir agregados ou ausentes. O Informe Mensal ainda traz carteira, mas confirme granularidade antes de prometer os números exatos.
- **Snapshot vs. histórico.** A matéria fala de operações 2020–2024; o dado aberto pode só refletir competências recentes. Coletar a série mensal mais longa possível mitiga.
- **Mercado secundário some.** A transferência Banvox→DV Holding das debêntures não tem rastro estruturado público — assumir isso como limite, citar como reportagem.
- **CPF mascarado / homônimos** (já no README) seguem valendo.

---

## 6. Arquivos desta branch

```
analise/
├── ANALISE_RECONSTRUCAO.md          este documento
└── verificacao_reconstrucao.py      verificação reprodutível (roda só com os CSVs)
```

Sem alterar nenhum dado ou script existente do Carlyle — é uma camada de leitura por cima.
