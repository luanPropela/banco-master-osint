# banco-master-osint

Coleta e análise de dados públicos sobre a rede societária e operacional do conglomerado Banco Master, liquidado pelo BACEN em nov/2025.

Pesquisa OSINT a partir de cadastros públicos da Receita Federal (via API Minha Receita) e da CVM (cadastro de fundos, informe diário). Saída principal é um SQLite (`data/master.db`) com 5 tabelas para consulta direta.

## Estrutura

```
banco-master-osint/
├── config.py                 constantes (seeds, cores, caminhos)
├── pipeline.py               orquestra fase 1 (coleta -> grafo -> visualização)
├── db.py                     fase 3: consolida caches JSON em SQLite
├── vorcaro.py                ego-grafo standalone focado em uma pessoa
├── coleta/
│   ├── receita.py            fase 1: BFS Minha Receita -> data/cnpjs.json
│   └── cvm_diario.py         fase 4: informe diário CVM -> tabela inf_diario
├── grafo/
│   ├── societario.py         construção do DiGraph (fase 1)
│   ├── b2b.py                fase 2: coleta CVM + grafo b2b -> data/fundos_b2b.json
│   ├── analise.py            métricas (betweenness, componentes, articulação)
│   └── visualizacao.py       pyvis e matplotlib
├── queries/
│   └── exemplos.sql          queries de exploração sobre data/master.db
├── data/                     caches, db e zips (gitignored)
├── requirements.txt
└── README.md
```

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate            # windows
source .venv/bin/activate         # linux/mac
pip install -r requirements.txt
```

## Pipeline

Todos os módulos rodam a partir da raiz do projeto via `python -m`. Cada fase é independente — pode rodar sozinha desde que a anterior já tenha gerado seu cache.

### Fase 1 — QSA das entidades Master

```bash
python -m coleta.receita
```

BFS via Minha Receita expandindo sócios PJ até `MAX_DEPTH` (`config.py`). Salva `data/cnpjs.json`.

### Fase 2 — Cadastro CVM e grafo B2B

```bash
python -m grafo.b2b
```

Baixa `cad_fi.csv` da CVM (~46k fundos), filtra os com vínculo Master (~57), enriquece com QSA das 6 entidades. Salva `data/fundos_b2b.json` e gera `grafo_b2b.html`.

### Fase 3 — Camada relacional

```bash
python -m db
```

Lê os dois caches JSON e popula `data/master.db` com:
- `empresas`, `pessoas`, `participacoes`, `papeis_fundo`

A tabela `inf_diario` (fase 4) é preservada se já existir.

### Fase 4 — Informe diário CVM (caso base)

```bash
python -m coleta.cvm_diario
```

Caso base: 4 fundos FMP-FGTS, janela 2025-01 a 2026-04. Zips ficam cacheados em `data/cvm_diario/`. Para expandir, editar `FUNDOS_ALVO` e `PERIODO` no script.

### Pipeline completo (fase 1 + grafo + viz)

```bash
python pipeline.py
```

## Exploração via SQL

Apontar DBeaver ou DB Browser pra `data/master.db`. Queries prontas em `queries/exemplos.sql`. Algumas amostras:

```sql
-- empresas onde Vorcaro participa
SELECT e.razao_social, p.qualificacao
FROM participacoes p
JOIN pessoas s   ON s.id = p.socio_pessoa_id
JOIN empresas e  ON e.cnpj = p.empresa_cnpj
WHERE s.nome LIKE '%VORCARO%';

-- top gestoras parceiras
SELECT prestador_nome, COUNT(*) AS n
FROM papeis_fundo
WHERE papel = 'gestor' AND prestador_nome IS NOT NULL
GROUP BY prestador_nome ORDER BY n DESC LIMIT 10;

-- ultimos dias de cada FMP-FGTS
SELECT fundo_cnpj, data, pl, cotistas, captacao_dia, resgate_dia
FROM inf_diario
ORDER BY fundo_cnpj, data DESC;
```

## Estado atual do banco

```
empresas        82    (7 seeds + 57 fundos + 18 prestadores)
pessoas         19
participacoes   30
papeis_fundo   156
inf_diario     517    (caso base: 4 FMP-FGTS, 16 meses)
```

## Fontes

- Minha Receita — https://minhareceita.org
- CVM Dados Abertos — https://dados.cvm.gov.br
- Cadastro de fundos — https://dados.cvm.gov.br/dataset/fi-cad
- Informe diário — https://dados.cvm.gov.br/dataset/fi-doc-inf_diario

## Limites declarados

- Snapshot, não histórico. Mudanças anteriores à coleta não aparecem nos cadastros.
- CPFs vêm mascarados na origem. Pessoas com nomes idênticos seriam fundidas.
- O grafo mostra relação cadastral, não imputa culpa.
- A coleta diária cobre só os 4 FMP-FGTS no caso base.
- Cadastro de FII na CVM retornou 404 nas tentativas — só FI foi processado.

## Aviso

Pesquisa educacional e jornalística sobre dados públicos. Todos os scripts são reproduzíveis: qualquer pessoa com Python e internet roda e chega nos mesmos resultados.
