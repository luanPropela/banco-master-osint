# Entes públicos que financiaram o Master + follow-the-money temporal

> Branch `analise-reconstrucao-claude`. Lado-**passivo** do grafo (quem "consumiu"/financiou o Master),
> restrito a **entes públicos**, com dado aberto. Tudo em polars, ambiente `master-osint`.

## Fonte (nova, confirmada e baixada)
**DAIR — Demonstrativo das Aplicações e Investimentos dos Recursos**, declaração mensal obrigatória de
todo RPPS, publicada pela Secretaria de Previdência (drive SERPRO). Baixei a **Carteira 2023–2026**
(`recon/baixar_carteira_dair.py`) — por competência: `Ente`, `UF`, `Identificação do Ativo` (CNPJ),
`Nome do Fundo/Banco`, `Tipo de Ativo`, `Valor Total Atual`, **`Percentual de Recursos do RPPS`**.

## 1. Inventário — temos (e vai além das notícias)
A imprensa nomeou ~5 RPPS; o DAIR revela **~30 entes** tocando a rede Master/Reag:

- **Tier-1 — Letra Financeira do próprio Banco Master (dinheiro público DIRETO no Master): 15 RPPS**,
  pico somado **~R$ 530 mi**. Principais:

| RPPS | UF | Pico em LF Master | % da carteira | Período |
|---|---|---|---|---|
| Maceió | AL | R$ 120,9 mi | 8,31% | 12/2023–02/2026 |
| Gov. do Estado do Amapá (Amprev) | AP | R$ 119,3 mi | 1,27% | 07/2024–12/2025 |
| Cajamar | SP | R$ 107,2 mi | **11,41%** | 10/2023–03/2026 |
| Itaguaí | RJ | R$ 67,6 mi | **11,41%** | 06/2024–02/2026 |
| Aparecida de Goiânia | GO | R$ 48,6 mi | 4,97% | 06/2024–01/2026 |
| Araras | SP | R$ 34,1 mi | 6,92% | 03/2024–02/2026 |
| Fátima do Sul | MS | R$ 8,2 mi | **20,46%** 🚩 | 06/2024–01/2026 |
| + Brodowski, Sto Antônio de Posse, São Gabriel do Oeste, Angélica, Campo Grande… | | | | |

- **Tier-2 — via fundos do grupo Reag** (ex.: "REAG MULTI ATIVOS IMOBILIÁRIOS FII"): **+15 RPPS** (exposição
  indireta — sinalizada à parte, pois é o grupo administrador, não LF do Master).

Saída: `dados/dair_rpps_expostos_master.csv`. O **% da carteira** é o sinal de concentração (detector de
Herfindahl do motor de grafos): municípios pequenos com 8–20% num único banco quebrado.

> **Achado honesto:** a **RioPrevidência** (a maior, ~R$3 bi) **NÃO está no DAIR** (0 linhas por CNPJ
> `03.066.219/0001-81` ou nome). Sendo autarquia estadual, não consta na base de carteira dos RPPS —
> para ela o dado público é **TCE-RJ / autos da PF (Op. Barco de Papel)**, não o DAIR. É um limite a
> declarar: o DAIR cobre muito (municípios + alguns estados), mas não esse ente específico.

## 2. Follow-the-money temporal — Maceió (eleito por ter série longa e exposição direta)
A RioPrev ficou fora do DAIR, então pilotei num ente bem capturado. A trajetória mensal **mostra o dinheiro
entrar, inflar e congelar na fraude**:

| Marco | Competência | Posição em LF Master |
|---|---|---|
| Entrada | 12/2023 | R$ 80,5 mi (8,29% da carteira) |
| Reforço | 05/2024 | R$ 102 mi (3º papel) |
| Pico | 10/2025 | R$ 120,9 mi |
| **Liquidação do Master (18/11/2025)** | 11/2025→02/2026 | **congela em R$ 120,87 mi** (estático) |

Leitura: dinheiro de aposentadoria entrou em **Letras Financeiras do Master (sem FGC, venc. 2033-2034)**,
acumulou juros no papel (2024-2025) e, **no mês da liquidação, a posição parou de se mover** — preso,
valor incerto. Saída: `dados/dair_follow_maceió_master_timeline.csv`.

## 3. Como isso liga à fraude (os dois grafos)
Este é o **lado-passivo**: RPPS → `emitiu/aportou` → **Letra Financeira do Banco Master**. É o *combustível*.
Do **lado-ativo** (já reconstruído), esse caixa virou empréstimos a fachadas e foi parar nos FIDC — ex.:
Master cede ao **SDG II** R$ 1,129 bi (19/12/2024) e a CCB do Lormont R$ 102,438 mi (27/02/2024); auditor
do SDG II em **abstenção de opinião (62% sem lastro)**. O nó de solda é o **Banco Master**:

```
[passivo] RPPS (Maceió, Cajamar, Itaguaí…) ──compram LF──▶ BANCO MASTER ──origina/cede──▶ FIDC (SDG II) [ativo]
```

Note o que o dado mostra e o que **não** mostra: o DAIR prova **quem pôs dinheiro e quanto/quando** (passivo);
ele **não** rastreia o real específico até um crédito podre específico (sigilo bancário) — o elo é o *ciclo*,
soldado no Master. Honestidade metodológica preservada.

## Como reproduzir
```bash
source ~/miniconda3/etc/profile.d/conda.sh && conda activate master-osint
python -u investigacao-claude/recon/baixar_carteira_dair.py     # baixa Carteira 2023-2026 (DAIR/SERPRO)
python -u investigacao-claude/recon/dair_master_analise.py      # inventário + timeline (polars)
```

## Limites e próximos passos
- RPPS com **valor 0** (Santa Rita d'Oeste, Gov. RJ, Tacuru): têm o papel listado mas valorado em 0 —
  posição zerada/baixada a confirmar.
- Tier-2 (fundos Reag) é exposição **indireta** — não confundir com LF do Master.
- **Próximos:** anos 2021-2022; cruzar com **BACEN IF.data** (balanço do Master) para o contrafactual;
  montar o **grafo de financiamento público** (`aportou_em`) ligado ao nó Master.

**Fontes:** DAIR/CADPREV (Secretaria de Previdência); Agência Brasil; InfoMoney; NeoFeed; BM&C; CVM/FNET (lado-ativo).
