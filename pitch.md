---
marp: true
theme: default
paginate: true
size: 16:9
backgroundColor: "#1a1a2e"
color: "#ffffff"
style: |
  section {
    font-family: -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    padding: 60px 80px;
  }
  h1 {
    color: #FFD700;
    font-size: 1.8em;
    border-bottom: 2px solid #FFD700;
    padding-bottom: 8px;
    margin-bottom: 24px;
  }
  h2 {
    color: #4A90D9;
    font-size: 1.3em;
  }
  strong {
    color: #FFD700;
  }
  table {
    font-size: 0.85em;
    border-collapse: collapse;
  }
  th {
    background: #2a2a4e;
    color: #FFD700;
    padding: 8px 12px;
  }
  td {
    padding: 6px 12px;
    border-bottom: 1px solid #444;
  }
  code {
    background: #2a2a4e;
    color: #5BA85A;
    padding: 2px 6px;
    border-radius: 3px;
  }
  blockquote {
    border-left: 4px solid #FFD700;
    color: #cccccc;
    font-style: italic;
    padding-left: 20px;
  }
  .center {
    text-align: center;
  }
  .big {
    font-size: 3em;
    color: #FFD700;
    text-align: center;
    margin: 0.5em 0;
  }
  .small {
    font-size: 0.7em;
    color: #888;
  }
---

<!-- _class: lead -->

<div class="center">

# Banco Master OSINT
## Mapeando o colapso com dados públicos

<br>

projeto de investigação reproduzível em Python
maio / 2026

</div>

---

# A pergunta

<br>

Quando o BACEN puxou o plug do Banco Master em **18 de novembro de 2025**, o banco tinha:

<div class="big">R$ 80 bilhões em ativos</div>

<div class="big" style="color:#E85D5D">R$ 4 milhões em caixa</div>

<br>

> O resto está numa fraude de R$ 52 bilhões — a maior da história bancária brasileira.

<br>

**A pergunta:** dá pra mapear quem operava esse esquema usando só dados públicos?

---

# O caso em 30 segundos

- **Banco Master**, controlado por **Daniel Bueno Vorcaro**, oferecia CDB a **140% do CDI** (vs ~100% do mercado)
- Triangulação com **Tirreno** (empresa de fachada do próprio Vorcaro) vendia carteiras fictícias ao **BRB** por R$ 12,2 bi
- BRB tentou comprar 58% do Master em mar/2025 — BACEN bloqueou em nov/2025
- Esquema-pirâmide: **novos CDBs pagando os antigos** + reinvestimento nos próprios CDBs Master
- **Operação Compliance Zero** (PF) — 6 fases até mai/2026
- **R$ 40 bi já desembolsados pelo FGC** para cobrir depositantes

<br>

<div class="small">

Fontes: Wikipedia, CNN Brasil, Agência Pública, CartaCapital, ICL Notícias

</div>

---

# A tese técnica

<br>

> Reportagem trabalha com fonte humana sob anonimato.
> OSINT trabalha com cadastro público sob auditoria.

<br>

Cada CNPJ no Brasil deixa **rastro estruturado** em pelo menos 3 bases públicas:

1. **Receita Federal** — QSA, situação cadastral
2. **CVM** — papéis em fundos (admin/gestor/custodiante), composição diária da carteira, sanções
3. **BACEN** — instituições financeiras autorizadas, balanços

Quem souber **costurar essas bases** consegue mapear um conglomerado inteiro sem ouvir ninguém.

---

# O método em 5 etapas

```
1. Coleta Receita ─► QSA das entidades-semente (BFS profundidade 2)
                    via API Minha Receita

2. Coleta CVM ────► Cadastro de fundos (cad_fi.csv)
                    Informe diário (PL, cotistas, resgate)
                    Composição da carteira (CDA)
                    Processo Sancionador (PAS)

3. SQLite ───────► Consolidação em 7 tabelas relacionais
                    (empresas, pessoas, participações,
                     papéis_fundo, inf_diario, carteira,
                     cvm_processos+acusados)

4. Análise pandas ► Queries cruzadas; séries temporais;
                    Random Forest Proximity para detectar
                    clusters de sócios

5. Documentação ──► RELATORIO.md auditável, queries
                    reproduzíveis, fontes hyperlinkadas
```

---

# O dataset

| Tabela | Linhas | O que é |
|---|---:|---|
| `empresas` | **100** | Master + gestoras parceiras + fundos CVM |
| `pessoas` | **104** | PFs do QSA |
| `participacoes` | **164** | sócio → empresa |
| `papeis_fundo` | **156** | admin/gestor/custodiante de 57 fundos |
| `inf_diario` | **517** | série diária dos 4 FMP-FGTS |
| `cvm_processos` | **543** | PAS-CVM histórico |
| `cvm_acusados` | **1.934** | acusados em PAS-CVM |
| `carteira` | **36** | CDA de 3 meses estratégicos |

<br>

**Reproduzível**: qualquer pessoa com Python roda os scripts e chega no mesmo dataset.

---

<!-- _backgroundColor: "#2a1a1e" -->

# Achado #1

## KATCH FIDC → UPPER FIDC

A CVM publica, mês a mês, em quais ativos cada fundo investiu. E marca uma flag:

<div class="big" style="font-size:2em">EMISSOR_LIGADO = "S"</div>

<br>

Em **31/08/2025** e **30/11/2025**, o KATCH FIDC (administrado pela Master Corretora, gerido pela Harbour Capital) declarou:

| Data | Ativo | % do PL | Valor |
|---|---|---:|---:|
| 31/08/2025 | UPPER FIDC | **99,5%** | R$ 32.658.172 |
| 30/11/2025 | UPPER FIDC | **99,5%** | R$ 31.002.312 |

**KATCH** está com situação **CANCELADA** na Receita. **UPPER FIDC** nem aparece no `cad_fi.csv` da CVM.

---

<!-- _backgroundColor: "#1e2a1a" -->

# Achado #2

## A ponte Letsbank ↔ Trustee

**Mauricio Antonio Quadrado** assume a Presidência do Banco Letsbank em **01/11/2024**.

O que descobrimos puxando o QSA dele em todas as empresas:

```
Mauricio Antonio Quadrado é sócio de:

  ▼ BANCO LETSBANK S/A          (grupo Master, liquidado)
  ▼ TRUSTEE HOLDING FINANCEIRA S/A
  ▼ TRUSTEE DTVM                (administra fundo do escopo Master)
```

<br>

> A Trustee DTVM aparecia no `cad_fi.csv` como **prestadora externa**.
> Não era. Tem ligação societária direta com o grupo via o Presidente do Letsbank.

<br>

**Veículo candidato a continuidade administrativa** dos fundos órfãos pós-liquidação.

---

<!-- _backgroundColor: "#2a2a1e" -->

# Achado #3

## Cronograma de degradação

```
2024-11-01  ★ Quadrado vira Presidente Letsbank
            (3 diretores entram no mesmo dia)

2025-04-10  ★ Resgate atípico R$ 254 mil
            no MAXIMA FMP-FGTS Petrobras
            (20% do PL num dia, 2 cotistas saem)

2025-08-06  ★ Os 2 BANESTES FMP-FGTS PARAM
            de reportar (mesmo dia, ambos)

2025-08-12  ★ Vorcaro vira Presidente do
            Banco Master de Investimento
            (6 dias depois)

2025-09-29  ★ STERN FIP + Adriano Garzon
            entram na Viking (holding pessoal)
            (4 semanas antes da liquidação)

2025-11-18  ▼ LIQUIDAÇÃO BACEN
```

A frequência **acelera** de mensal para quinzenal nos últimos 3 meses.

---

<!-- _backgroundColor: "#1a2a2e" -->

# Achado #4

## STERN FIP — veículo recém-construído

<br>

| Dado | Valor |
|---|---|
| CNPJ | 56823324000184 |
| Razão | STERN FIP Multiestratégia |
| Constituído | **15/08/2024** |
| Capital social | R$ 0 (próprio de FIP) |
| Aparece no `cad_fi.csv` CVM? | **NÃO** |
| Entra na Viking (holding Vorcaro) | **29/09/2025** |
| Dias antes da liquidação BACEN | **49** |

<br>

> Um FIP criado **13 meses antes** entra como sócio da holding pessoal do controlador **menos de 7 semanas antes** do BACEN liquidar o banco.

<br>

**Hipótese a confirmar:** veículo de blindagem patrimonial ou capital de socorro tardio.

---

# A camada matemática: Random Forest Proximity

<br>

**Problema clássico** com 104 pessoas: como agrupar sem rótulo?

**Solução de Breiman (2001)** adaptada:

1. Constrói matriz de features (presença em cada empresa + qualificações + ano)
2. Gera dataset sintético permutando cada coluna
3. Treina RandomForest para distinguir real vs sintético
4. Para cada par de pessoas, conta em quantas das 500 árvores caem na mesma folha
5. Resultado: matriz de proximidade [0, 1]

<br>

**O que isso revelou:** Vorcaro fica em cluster próprio (proximidade ≤ 0.20 com qualquer outro). Os diretores formam **duplas e trios simétricos**. Famílias (Piana, Lanzetti) e times de gestoras (Carmel, ID) emergem como blocos compactos no dendrograma.

---

# O que o método NÃO faz

<br>

**Limites declarados** (importantes para o pitch ser defensável):

- Mapeia **relação cadastral**, não imputa culpa.
- Trabalha com **snapshot**, não histórico do QSA.
- CPFs vêm **mascarados** — risco de homônimo (baixo no nosso conjunto).
- Falta a camada de **propriedade acionária** (BACEN IF.data — pendente).
- Cobertura de **fundos pelo CDA** ainda parcial (3 meses dos 24 possíveis).
- **Não substitui reportagem**. Funciona como dossiê estruturado para o jornalista que vai checar.

<br>

> *"Quem te questionar tecnicamente vai ter que apontar onde o método quebra; quem te questionar moralmente esbarra no fato de que os dados estão abertos pra qualquer um repetir o exercício."*

---

# O que vem na próxima rodada

<br>

| Frente | Custo | Ganho esperado |
|---|---|---|
| **Tirreno** — achar CNPJ e puxar QSA | 5 min | Fecha a tríade Master–Tirreno–BRB |
| **BACEN IF.data** | 1-2h scraping | Composição acionária dos bancos |
| **Portal Transparência** (CEIS/CNEP) | 30 min com token | Sanções administrativas |
| **CDA expandido** — todos os 24 meses | 30 min | Histórico completo do emissor ligado |
| **Fundos órfãos pós-liquidação** | 1h | Quem assumiu admin dos 57 fundos |
| **Cruzamento offshore** (OpenCorporates, ICIJ) | 2h | Estruturas internacionais dos sócios |

---

# Repositório aberto

<br>

<div class="center">

## github.com/lyMartins/banco-master-osint

<br>

```
17 scripts Python    │  ~2.500 linhas comentadas
2 notebooks Jupyter  │  104 pessoas mapeadas
1 SQLite             │  7 tabelas relacionais
3 markdowns          │  documentação completa
17 fontes citadas    │  jornalismo + dados oficiais
```

<br>

Rodável em **Windows · Arch Linux · Parrot OS**
Reproduzível em < 1 hora com `pip install -r requirements.txt`

</div>

---

<!-- _class: lead -->

<div class="center">

# Obrigado

<br>

**Banco Master OSINT**
método aberto, dados públicos, achados auditáveis

<br>

<div class="small">

Pesquisa educacional e jornalística sobre dados públicos.
Mapeia relação cadastral, não imputa culpa.

</div>

</div>
