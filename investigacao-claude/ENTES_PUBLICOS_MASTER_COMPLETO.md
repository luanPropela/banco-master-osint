# Dinheiro público × Banco Master — inventário COMPLETO (validado vs. notícias)

> Meta: rastrear **toda** relação de dinheiro público com produtos do Master (LF, CDB, cotas). Ground truth =
> notícias; checagem = bases (DAIR/CADPREV). Esta é a versão **corrigida** após validar a completude.

## Correção de método (por que a 1ª passada subcontava)
A Letra Financeira do Master aparece no DAIR sob **muitos nomes** — e o principal, **"ETRA FINANCEIRA MASTER" /
"MASTER - LF…"** (o "L" de "Letra" é cortado na fonte), **não contém a palavra "BANCO"**. O filtro estrito
(`BANCO MASTER`) perdia esses. Também havia **falsos positivos** de "Master" genérico (SAFRA DI MASTER, BB RENDA
FIXA MASTER, BANRISUL MASTER, Brasil Capital Master…) que **não** são o Banco Master.

**Filtro corrigido:** Tier-1 = renda fixa emitida por IF com "master" no nome **ou** "banco master" (qualquer
variante) → LF/CDB do Banco Master; Tier-2 = fundos da rede Reag (nome Reag/CBSF/SDG II/Hans 95… ou CNPJ da
rede); **exclui** fundos "Master" de outros bancos. Resultado: de R$ 530 mi (errado) para **R$ 1,53 bi**.

## Inventário Tier-1 — LF/CDB DIRETO do Banco Master: **18 RPPS, pico somado R$ 1,53 bi**

| RPPS | UF | Pico | % carteira | Entrada | Destino pós-liquidação |
|---|---|---|---|---|---|
| **Governo do Estado do RJ** | RJ | **R$ 568 mi** | 2,7% | 11/2023 | 💥 baixado a zero |
| **Governo do Estado do Amapá (Amprev)** | AP | **R$ 435 mi** | 2,5% | 07/2024 | 🔒 congelado |
| Maceió | AL | R$ 121 mi | 6,9% | 12/2023 | 🔒 congelado |
| **São Roque** | SP | R$ 108 mi | **18,7%** 🚩 | 04/2024 | mantido |
| Cajamar | SP | R$ 107 mi | 10,6% | 10/2023 | 💥 baixado a zero |
| Itaguaí | RJ | R$ 68 mi | 11,4% | 06/2024 | 🔒 congelado |
| Aparecida de Goiânia | GO | R$ 49 mi | 4,6% | 06/2024 | 🔒 congelado |
| Araras | SP | R$ 34 mi | 6,2% | 03/2024 | 🔒 congelado |
| Brodowski, Sto Antônio de Posse, Fátima do Sul (14,8%), Paulista/PE, São Gabriel do Oeste, Jateí/MS, Angélica, Campo Grande, Santa Rita, Tacuru | — | < R$ 12 mi cada | — | 2024 | misto |

Tier-2 (fundos da rede **Reag**, exposição indireta): **+15 RPPS**, ~R$ 73 mi (Campos dos Goytacazes, Embu das
Artes, São Bernardo, Camaçari, Gov. Rondônia, Santa Luzia, Birigui, Santos…). **Total: 33 entes públicos.**
→ `dados/dair_rpps_master_DEFINITIVO.csv` (lista) + `dair_follow_the_money_DEFINITIVO.csv` (mês a mês).

## Distribuição temporal (follow-the-money agregado)
R$ 35 mi (out/2023) → **R$ 1,29 bi (jul/2024, 16 RPPS)** → platô **R$ 1,5 bi** em 2025 → liquidação (18/11/2025)
→ R$ 669 mi (dez/2025) → ~R$ 0 (mar/2026). Pico **R$ 1,505 bi (out/2025)**.
→ `dados/dair_distribuicao_temporal.png` · grafo `dados/grafo_financiamento_publico.png`.

## Reconciliação com as notícias (ground truth)
| Notícia | Na base (DAIR)? |
|---|---|
| "18 RPPS, R$ 1,87 bi em LF" | ✅ **18 RPPS, R$ 1,53 bi** (resto ≈ RioPrev, fora do DAIR) |
| São Roque R$ 107 mi / 18,7% | ✅ R$ 108 mi / 18,7% |
| Amprev (Amapá) R$ 426 mi / 4,7% | ✅ "Gov. Estado do Amapá" R$ 435 mi |
| Maceió, Cajamar | ✅ confirmados |
| RioPrevidência ~R$ 960 mi (LF) | ❌ **não está no DAIR** (ver gaps) |

## GAPS — o que falta para ter "tudo" (e onde buscar)
1. **RioPrevidência (RJ)** — ~R$ 960 mi em LF (+ R$ 2,01 bi em fundos). Autarquia estadual **fora do DAIR**.
   → Fonte: **TCE-RJ** / portal da própria RioPrev / autos da Op. Barco de Papel (PF).
2. **Bancos públicos** — relação diferente (compraram ativos do Master, não investiram em LF):
   **BRB** comprou R$ 12,2 bi em carteiras (via Tirreno). → Fonte: **BACEN IF.data** (estava em HTTP 500, re-tentar)
   + fato relevante CVM + decisão judicial. Checar também outros (Banese, Banrisul, BRDE…).
3. **Outras autarquias estaduais de previdência** estruturadas como a RioPrev (ex.: SPPREV/SP) podem estar fora
   do DAIR — varrer por nome.
4. **EFPC (fundos fechados de estatais)** — a imprensa diz que os grandes ficaram de fora; confirmar via PREVIC.
5. **CDB (pessoa física/PJ)** e depositantes — sigilo bancário; só o lado institucional (fundos/RPPS) é público.

## Como reproduzir
```bash
source ~/miniconda3/etc/profile.d/conda.sh && conda activate master-osint
python -u investigacao-claude/recon/baixar_carteira_dair.py       # Carteira 2023-2026 (DAIR/SERPRO)
python -u investigacao-claude/recon/dair_master_v2.py             # inventário DEFINITIVO (filtro corrigido)
python -u investigacao-claude/recon/dair_viz_definitivo.py        # distribuição temporal + grafo
```

**Status da meta:** o canal **RPPS está mapeado e validado** (33 entes, R$ 1,53 bi Tier-1, série mensal completa).
Faltam, com fonte já identificada: **RioPrevidência (TCE-RJ)** e **bancos públicos/BRB (IF.data)**.

**Fontes:** DAIR/CADPREV (Sec. Previdência); InfoMoney; NeoFeed; BM&C; Seu Dinheiro; Agência Brasil; Metrópoles; CVM/FNET.
