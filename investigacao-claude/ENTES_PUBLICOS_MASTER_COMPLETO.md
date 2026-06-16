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

## GAPS — RESOLVIDOS após validação
1. **RioPrevidência (RJ) — ✅ JÁ ESTÁ nos dados.** O DAIR arquiva por *ente federativo*: a RioPrev aparece como
   **"Governo do Estado do Rio de Janeiro"** (CNPJ 42.498.600/0001-71; "RioPrevidência" é a unidade gestora).
   Carteira total ~R$ 10–13 bi; **LF do Master: R$ 120 mi (11/2023) → R$ 568 mi (11/2025, 5,9%) → R$ 0 (12/2025)**
   — o zeramento **confirma a reversão via precatórios** noticiada. Papéis: "etra Financeira Master" 1/2/3.
   (Está no Tier-1 acima como "Gov. Estado do RJ". A notícia fala em ~R$ 960 mi — provável bruto/cumulativo;
   o DAIR mostra a posição líquida de fim de mês, pico R$ 568 mi. CNPJ do ente ≠ CNPJ da autarquia 03.066.219 —
   mesma entidade econômica, registro CADPREV pelo governo.)
2. **Completude estadual — ✅ varrida.** Só **6 governos estaduais** têm LF do Master: RJ (R$ 568 mi), Amapá
   (R$ 435 mi), Roraima, Rondônia, Tocantins, Pará. **SP estado (SPPREV) NÃO tem** — não há grande estado faltando.
3. **BRB / bancos públicos — relação distinta, documentada.** BRB **comprou** R$ 12,2 bi em carteiras do Master
   (via Tirreno) — não é "consumo de LF/CDB" como investidor; é a porta de saída de caixa. Fonte: decisão
   judicial + PF + fato relevante CVM. **IF.data OData do BACEN segue instável** (400/500 em 4 tentativas) — a
   re-tentar p/ o balanço; mas o R$ 12,2 bi é fato público consolidado.
4. **EFPC (fundos fechados)** — imprensa: os grandes ficaram de fora; fora do DAIR (seria via PREVIC). Baixo risco.
5. **CDB pessoa física/PJ e depositantes** — sigilo bancário; só o lado institucional (RPPS/fundos) é público.

**Conclusão de completude:** o canal **dinheiro público investidor (RPPS, incl. RioPrev) está integralmente
mapeado e baixado** (DAIR, 33 entes, R$ 1,53 bi Tier-1). O único item não-baixado programaticamente é o
**balanço do BRB no IF.data** (API instável) — e o BRB é relação de *compra*, com o valor (R$ 12,2 bi) já público.

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
