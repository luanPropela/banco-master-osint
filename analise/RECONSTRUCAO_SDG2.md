# Reconstrução da fraude do SDG II a partir de dado público

> Branch `analise-reconstrucao-claude`. Resposta executável à pergunta do grupo:
> **"dá para reconstruir o que a matéria fala?"** — Sim. Abaixo, 10 das 11 afirmações
> quantitativas da reportagem Folha/ICL reproduzidas a partir de documentos públicos da CVM,
> com cada número rastreado à sua fonte. Ambiente isolado em `analise/environment.yml`
> (conda `master-osint`). Tudo reproduzível.

## Resultado — scorecard

| Afirmação da matéria | Citado | Reconstruído (fonte pública) | Status |
|---|---|---|---|
| Tamanho do fundo | R$ 5,4 bi | Ativo **R$ 5,455 bi** (dez/2025) | ✅ exato |
| Nº de cotistas | 2 | **2** (jan/2025–jan/2026) | ✅ exato |
| Cotista Anna (Hans 95 via Anna) | — | **Anna** integraliza cotas do SDG II em 30/09/2024 | ✅ confirmado |
| Cotista MKS Soluções | — | 2º cotista classificado como **fundo** no informe; MKS não nomeada nos docs públicos | ⚠️ **não confirmado** |
| Créditos podres absorvidos | R$ 3,6 bi | Dir. creditórios **R$ 3,36 bi** (dez/2025) / **R$ 6,53 bi** (DF, jan/2024) | ✅ compatível |
| Vendido **direto pelo Master** | ≥ R$ 1,1 bi | **R$ 1,129 bi** (2 cessões de 19/12/2024); total Master **R$ 1,232 bi** | ✅ exato |
| Lormont (total no fundo) | ~R$ 553 mi | **R$ 597 mi** (6 CCBs) | ✅ compatível |
| Lormont cedido pelo Master | R$ 102 mi | **R$ 102,438 mi** (CCB, 27/02/2024) | ✅ exato |
| Debênture Banvox | R$ 380 mi | **R$ 380,346 mi** adquirido (emissão R$ 400 mi) | ✅ exato |
| Super Empreendimentos | R$ 22 mi | **R$ 22,012 mi** (cessão 06/03/2023) | ✅ exato |
| Indício de fraude (lastro) | implícito | **Abstenção de opinião** do auditor; **62%** dos dir. creditórios sem lastro comprovado | ✅ confirmado |

CSVs da reconstrução: `analise/recon/output/sdg2_cessoes_reconstruidas.csv` e `sdg2_scorecard.csv`.

## As duas fontes públicas usadas

1. **Informe Mensal Estruturado de FIDC** — dados abertos CVM
   `https://dados.cvm.gov.br/dados/FIDC/DOC/INF_MENSAL/DADOS/inf_mensal_fidc_AAAAMM.zip`
   Dá os **agregados** mês a mês: PL/ativo, **nº de cotistas**, direitos creditórios (a vencer,
   vencidos, inadimplentes, provisão), valores mobiliários (debêntures), cotas de outros FIDC.
   O SDG II (CNPJ 46.909.301/0001-33) reporta de **jan/2025 a mar/2026** (para de reportar em abr/2026 —
   coerente com a liquidação). É por isso que a checagem inicial só no mês de abr/2026 deu "ausente".

2. **Demonstrações Financeiras auditadas (exercício 2024)** — via **FNET (B3/CVM)**
   `https://fnet.bmfbovespa.com.br/fnet/publico/...` — **tem API pública** (`pesquisarGerenciadorDocumentosDados`
   + `downloadDocumento?id=`). O SDG II tem 106 documentos; baixei a DF auditada (id 963178).
   Dá o **detalhe nominal** que o informe agregado não traz: **quem cedeu, quem deve, quanto, quando**,
   e o **parecer do auditor**.

> Observação sobre o pedido de "pegar manual via Chrome": o FNET acabou sendo **acessível por API**,
> então a coleta foi feita de forma programática e reproduzível (melhor que cliques manuais).
> O caminho manual (browser + subagente) fica de reserva caso a CVM exija navegação interativa para
> algum documento específico. As DFs centrais já estão arquivadas em `fontes/` com hash.

## A mecânica da fraude, reconstruída (o que os documentos mostram)

O SDG II é um **FIDC-NP fechado e exclusivo**, administrado pela **Reag Trust DTVM / CBSF DTVM**
(mesmo CNPJ 34.829.992/0001-86 — confirma "CBSF DTVM ex-Reag Trust"). A DF de 2024 mostra o ciclo:

- **Banco Master S.A. cede direitos creditórios diretamente ao SDG II:**
  - 27/02/2024 — CCB do **Lormont** → R$ 102,438 mi
  - 19/12/2024 — direitos creditórios → R$ 192,941 mi
  - 19/12/2024 — direitos creditórios → R$ 936,222 mi
  - As duas de 19/12 somam **R$ 1,129 bi** = os "pelo menos R$ 1,1 bi vendidos diretamente pelo Master".
- **Lormont (Nelson Tanure)** entra por **6 CCBs** cedidas por uma teia de FIDCs (Carriet, B-ROL, CIB-K,
  Del Rey, Runeard) **+ o próprio Master** — total **R$ 597 mi** (a matéria diz ~R$ 553 mi).
- **Banvox (ex-Quadrado):** o fundo adquiriu, em 22/11/2023, **R$ 380,346 mi** da 4ª emissão de debêntures
  da Banvox Holding Financeira S.A. (emissão de R$ 400 mi).
- **Super Empreendimentos** (braço de Vorcaro) cedeu **R$ 22,012 mi** ao fundo em 06/03/2023.
- **Anna FICFIDC-NP** integralizou cotas do SDG II (30/09/2024), pagando em ativos (cártulas BESC) — é o
  cotista-fundo que a matéria descreve ("Hans 95 entra via Anna").
- O fundo ainda investe em cotas de **"FI MMASTER CP"** e **"FIDC Lancia"** (R$ 1,29 bi, ~40% do PL).

**O carimbo da fraude:** o auditor emitiu **ABSTENÇÃO DE OPINIÃO** sobre a DF de 2024 — entre os motivos,
**ausência de comprovação de lastro de ~62%** dos R$ 6,53 bi em direitos creditórios, ausência de estudos
de recuperabilidade e de controles internos. Em linguagem de auditoria, é o mais próximo de "não
conseguimos confirmar que esses créditos existem de verdade".

## As duas ressalvas honestas

1. **MKS Soluções como cotista — não confirmado em fonte pública.** O informe mensal mostra os 2 cotistas
   classificados como **fundos** (1 "cota FIDC" = Anna + 1 "outro FI"), e a DF não nomeia a MKS. A matéria
   afirma que a MKS é cotista direta; isso pode vir de fonte de inquérito/CVM restrita, ou a MKS pode
   participar via um fundo-veículo. Fica como o único ponto a fechar (provável via CVMWeb/processo).
2. **Lormont R$ 597 mi vs R$ 553 mi:** soma dos valores de aquisição das 6 CCBs (R$ 597 mi) vs. o valor
   "mapeado no fundo" pela Folha (R$ 553 mi) — diferença esperada por amortização/provisão/data-base.

## Como reproduzir

```bash
conda env create -f analise/environment.yml          # cria env master-osint
conda run -n master-osint python analise/recon/explore_fidc.py        # acha os fundos no informe FIDC
conda run -n master-osint python analise/recon/sdg2_series.py         # série PL/ativo/dircred/cotistas
conda run -n master-osint python analise/recon/sdg2_cotistas.py       # tipo de cotistas + snapshot dez/2025
conda run -n master-osint python analise/recon/probe_fnet.py          # lista documentos FNET do SDG II
conda run -n master-osint python analise/recon/fnet_download.py       # baixa as DFs (PDF)
conda run -n master-osint python analise/recon/pdf_extract.py data/fnet_docs/SDG2_DemonstracoesFinanceiras_A_963178.pdf
conda run -n master-osint python analise/recon/reconstruir_sdg2.py    # scorecard + CSVs
```

## Fontes arquivadas (verificáveis por hash)

- `fontes/CVM-FNET_SDG-II_DemonstracoesFinanceiras_2024_id963178.pdf` (+ `.sha256`) — a DF auditada.
- `fontes/ICL_master-usou-fundo-54bi_2026-05-28.pdf` — a reportagem-âncora.

## Próximos alvos (mesma receita)

- **Lancia! → NGV SPE (R$ 30 mi em debêntures, balanço 30/06/2024):** Lancia! também está no informe
  mensal de FIDC e tem DF no FNET. Repetir o processo fecha mais uma aresta.
- **Gold Style, Anna:** presentes no informe mensal; DFs no FNET.
- **MKS como cotista:** resolver via CVMWeb fundosreg / autos do processo.
