# AGENTS.md — investigação `investigacao-claude/`

Guia para agentes de IA que trabalham nesta pasta. README para humanos é o `README.md` ao lado.

## O que é

Reconstrução, **a partir de dado público da CVM**, do esquema de fraude do **fundo SDG II** (FIDC do
conglomerado Banco Master / Daniel Vorcaro), validando a reportagem Folha/ICL de 26/05/2026. É uma
camada de análise por cima do projeto OSINT do Carlyle (`lyMartins/banco-master-osint`), vive na branch
`analise-reconstrucao-claude` e não altera os scripts/dados originais dele.

Resultado: **10 das 11 afirmações quantitativas da matéria reproduzidas** de fonte pública (a 11ª —
MKS como cotista — provou-se não pública). Ver `RECONSTRUCAO_SDG2.md`.

## Ambiente

- **conda env `master-osint`** (Python 3.12), definido em `environment.yml` (fonte autoritativa de
  dependências — adicione pacotes lá e recrie o env; não use `pip` fora do conda).
  ```bash
  conda env create -f investigacao-claude/environment.yml
  ```
- **Manipulação de dados: use `polars` (não pandas)** — é o padrão do projeto.
- **Rode sempre da RAIZ do repo, com `conda activate` (NUNCA `conda run` — ele bufferiza o output)**;
  use `python -u` para saída ao vivo. Os scripts usam `data/` (na raiz, gitignored) como cache:
  ```bash
  source ~/miniconda3/etc/profile.d/conda.sh && conda activate master-osint
  python -u investigacao-claude/recon/<script>.py
  ```

## Fontes de dados (mapa) — qual usar para quê

| Preciso de… | Fonte | Como |
|---|---|---|
| Sócios / QSA (societário) | Minha Receita | API `minhareceita.org/<cnpj>` |
| Agregados de FIDC (PL, nº cotistas, dir. creditórios, inadimplência) | **CVM Informe Mensal de FIDC** | ZIP mensal `dados.cvm.gov.br/dados/FIDC/DOC/INF_MENSAL/DADOS/` (17 tabelas; Tab I/IV/X) |
| **Administrador + gestor** de qualquer fundo (inclui FIDC) | **CVM `registro_fundo.csv`** (RCVM 175) | `dados.cvm.gov.br/dados/FI/CAD/DADOS/registro_fundo_classe.zip` |
| Carteira **nominal** de FIDC (cedente, devedor, debêntures) | **FNET — Demonstrações Financeiras** | API pública (abaixo) |
| Nome de cotista / histórico de troca de gestor | FNET (atas) / CVMWeb `fundosreg` | atas via FNET; fundosreg é manual (sem API) |

**FNET (API pública, sem login):**
```
listar docs:  GET fnet.bmfbovespa.com.br/fnet/publico/pesquisarGerenciadorDocumentosDados?cnpjFundo=<14d>&l=200
baixar doc:   GET fnet.bmfbovespa.com.br/fnet/publico/downloadDocumento?id=<id>&cvm=true   (PDF)
```

> ⚠️ **Não use `cda_fi` para carteira de FIDC.** O `cda_fi` (`FI/DOC/CDA/`) é do universo FI/555 e **não
> cobre FIDC-NP** (SDG II, Anna etc.). Esse foi o erro original que fazia o grafo não reconstruir nada.

## Scripts (`recon/`, exceto onde indicado)

| Script | Faz |
|---|---|
| `explore_fidc.py` | acha os fundos da teia no Informe Mensal de FIDC (por CNPJ e por nome) |
| `sdg2_series.py` / `sdg2_cotistas.py` | série temporal e snapshot do SDG II (PL, cotistas, dir.cred.) |
| `probe_fnet.py` / `fnet_download.py` / `fnet_cotistas.py` | lista, baixa e varre documentos do FNET |
| `pdf_extract.py` | extrai texto de PDF (pdfplumber) e busca entidades/valores |
| `montar_dataset_fidc.py` | gera `dados/fidc_mensal_fundos_master.csv` |
| `mapear_admin_gestor.py` | admin+gestor de N fundos via `registro_fundo.csv` → `dados/registro_admin_gestor_fundos.csv` |
| `reconstruir_sdg2.py` | reconciliação final matéria × dado → `recon/output/*.csv` |
| `../verificacao_reconstrucao.py` | (na raiz da pasta) checa as afirmações sobre os CSVs do Carlyle |
| sondas/utilitários | `probe_admin_gestor.py`, `probe_registro_rcvm175.py` (descoberta de fonte), `exportar_sqlite_para_csv.py` (master.db → CSV) |

## Dados (`dados/`)

Mapa completo no `README.md`. Em resumo: `dataset_carlyle_csv/` (18 CSVs-fonte do Carlyle, incl. grafo de
fraude, carteira CDA, PAS), `fidc_mensal_fundos_master.csv` e `registro_admin_gestor_fundos.csv`
(reconstruídos), `fnet/` (DFs do SDG II em PDF+texto), `master_db_export/` (tabelas do master.db).
Resultados da reconciliação em `recon/output/`.

## Verificação

`reconstruir_sdg2.py` imprime o **scorecard** (matéria × reconstruído) — é o "teste" de que a reconstrução
fecha. Rode-o após qualquer mudança em dados/valores e mostre a saída como evidência.

## Convenções

- **Rastreabilidade:** todo valor reconstruído deve apontar para o documento-fonte. Fontes primárias
  (matéria, DFs) ficam em `fontes/` com `.sha256`. Resultados em `recon/output/` e `dados/`.
- **Dados:** dumps brutos grandes (zips do mercado inteiro, PDFs) ficam em `data/` (raiz, gitignored) e
  **não** são versionados — só os **extratos curados** entram em `investigacao-claude/dados/`.
- **Honestidade epistemológica:** distinga "verificado em dado público" de "afirmado pela reportagem" de
  "não público" (ex.: nome de cotista). Não infle.
- **Reprodutibilidade:** tudo roda só com Python + internet; sem fontes confidenciais.

## Git / PR

- Branch de trabalho: `analise-reconstrucao-claude`.
- **Sem acesso de escrita** ao `origin` (`lyMartins`). Fluxo: push no fork `luanPropela/banco-master-osint`
  (remote `fork`) e PR para `lyMartins:main` via `gh` (`gh pr list --repo lyMartins/banco-master-osint`
  para ver o PR aberto).
- Mensagens de commit em PT-BR, descritivas; terminam com a linha `Co-Authored-By: Claude ...`.

## Fatos-âncora (sanity-check de qualquer texto)

> - **SDG II**: CNPJ `46.909.301/0001-33`.
> - **Administrador**: CNPJ `34.829.992/0001-86` — "Reag Trust DTVM" no `registro_fundo`, **a mesma
>   entidade renomeada para "CBSF DTVM"** no Informe Mensal (rename Reag→CBSF).
> - **Gestor**: `CBSF Trust Administradora de Recursos Ltda.`, CNPJ `23.863.529/0001-34` (entidade
>   distinta do administrador).
> - Reconstruído: ativo **R$ 5,455 bi** (dez/2025); **2 cotistas**; direto do Master **R$ 1,129 bi**
>   (2 cessões 19/12/2024); Lormont via Master **R$ 102,438 mi**; debênture Banvox **R$ 380,346 mi**;
>   Super **R$ 22,012 mi**; parecer do auditor: **abstenção de opinião, 62% dos dir. creditórios sem lastro**.
