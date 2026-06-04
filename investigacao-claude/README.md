# Investigação — reconstrução da fraude do SDG II a partir de dado público

Pasta única e autocontida com **tudo** desta investigação: relatórios, scripts, dados-fonte
(CSV), dados adquiridos (Informe Mensal de FIDC + Demonstrações Financeiras do FNET),
resultados e fontes primárias arquivadas com hash.

## Conclusão em uma linha

A partir de documentos públicos da CVM, **10 das 11 afirmações quantitativas** da reportagem
Folha/ICL sobre o fundo SDG II foram **reproduzidas** (a 11ª — MKS como cotista — provou-se
**não pública**). Detalhes e scorecard em [`RECONSTRUCAO_SDG2.md`](RECONSTRUCAO_SDG2.md).

## Mapa da pasta

```
investigacao-claude/
├── README.md                       este índice
├── AGENTS.md / CLAUDE.md           guia para agentes de IA (fontes, ambiente, gotchas, fatos-âncora)
├── RECONSTRUCAO_SDG2.md            relatório final — scorecard matéria × dado público
├── INVESTIGACAO_ADMIN_GESTOR.md    onde vive admin/gestor e como pegar programaticamente (registro_fundo.csv)
├── ANALISE_RECONSTRUCAO.md         diagnóstico inicial (por que o grafo não reconstruía)
├── environment.yml                 ambiente conda isolado (master-osint)
├── verificacao_reconstrucao.py     verificação reprodutível sobre os CSVs do Carlyle
│
├── recon/                          SCRIPTS da investigação
│   ├── explore_fidc.py             acha os fundos da teia no Informe Mensal de FIDC
│   ├── sdg2_series.py              série PL/ativo/dir.cred./cotistas do SDG II
│   ├── sdg2_cotistas.py            tipo de cotistas + snapshot dez/2025
│   ├── probe_fnet.py               lista documentos do SDG II via API do FNET
│   ├── fnet_download.py            baixa as Demonstrações Financeiras (PDF)
│   ├── fnet_cotistas.py            procura o 2º cotista em atas/trimestrais
│   ├── pdf_extract.py              extrai texto das DFs e busca entidades/valores
│   ├── montar_dataset_fidc.py      gera o CSV tidy dos fundos-alvo (abaixo)
│   ├── exportar_sqlite_para_csv.py exporta tabelas do master.db p/ CSV
│   ├── reconstruir_sdg2.py         RECONCILIAÇÃO final + gera os CSVs de resultado
│   └── output/                     RESULTADOS
│       ├── sdg2_cessoes_reconstruidas.csv   cessões/debêntures (cedente→devedor→valor→fonte)
│       └── sdg2_scorecard.csv               cada afirmação da matéria × status × fonte
│
├── fontes/                         FONTES PRIMÁRIAS (verificáveis por SHA-256)
│   ├── ICL_master-usou-fundo-54bi_2026-05-28.pdf(.md/.sha256)   a reportagem-âncora
│   ├── CVM-FNET_SDG-II_DemonstracoesFinanceiras_2024_id963178.pdf(.md/.sha256)  a DF auditada
│   └── README.md                   índice de fontes + a fonte manual (CVMWeb fundosreg)
│
└── dados/                          DADOS
    ├── registro_admin_gestor_fundos.csv     ← admin + gestor de 66 fundos do perímetro (registro_fundo RCVM 175)
    ├── fidc_mensal_fundos_master.csv        ← adquirido: Informe Mensal FIDC (SDG II, Anna, Lancia!, Gold Style)
    ├── fnet/                                ← adquirido: DFs do SDG II (PDF + texto extraído)
    ├── dataset_carlyle_csv/                 ← fonte: os 18 CSVs exportados pelo Carlyle (empresas, QSA,
    │                                           participações, grafo de fraude, carteira CDA, PAS-CVM…)
    └── master_db_export/                    ← export bruto das tabelas do data/master.db (versão parcial)
```

> Os ~41 MB de zips brutos do mercado inteiro (Informe Mensal de FIDC, todos os fundos) **não** são
> versionados — são re-baixáveis por `recon/explore_fidc.py`. O que está aqui é o **extrato dos
> fundos-alvo** (`dados/fidc_mensal_fundos_master.csv`), que é o dado útil.

## Como reproduzir do zero

```bash
conda env create -f investigacao-claude/environment.yml      # cria env master-osint
# 1) dado aberto: Informe Mensal de FIDC
conda run -n master-osint python investigacao-claude/recon/explore_fidc.py
conda run -n master-osint python investigacao-claude/recon/sdg2_series.py
conda run -n master-osint python investigacao-claude/recon/montar_dataset_fidc.py
# 2) documentos do FNET (Demonstrações Financeiras)
conda run -n master-osint python investigacao-claude/recon/probe_fnet.py
conda run -n master-osint python investigacao-claude/recon/fnet_download.py
conda run -n master-osint python investigacao-claude/recon/pdf_extract.py data/fnet_docs/SDG2_DemonstracoesFinanceiras_A_963178.pdf
# 3) reconciliação final (gera os CSVs de resultado)
conda run -n master-osint python investigacao-claude/recon/reconstruir_sdg2.py
```

> Os scripts usam `data/` (na raiz do repo) como cache de download — rodar sempre a partir da raiz do repo.

## As duas fontes públicas da reconstrução

1. **Informe Mensal Estruturado de FIDC** — `dados.cvm.gov.br/dataset/fidc-doc-inf_mensal` (agregados).
2. **Demonstrações Financeiras (FNET, API pública)** — `fnet.bmfbovespa.com.br/fnet/publico/` (carteira nominal).
3. Reserva manual: **CVMWeb fundosreg** (sem API) — ver `fontes/README.md`.
