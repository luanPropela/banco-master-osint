# Brief de Deep Research — rastrear TODO dinheiro público ligado ao Banco Master

> Cole isto como prompt para um agente de pesquisa profunda (OSINT financeiro). Idioma: PT-BR.
> Objetivo do prompt: achar os dados que ainda faltam e descobrir relações públicas escondidas.

---

## Papel
Você é um investigador OSINT financeiro. Sua tarefa é produzir a lista **exaustiva e com fontes** de
**todo ente público** (e todo dinheiro público) que teve relação financeira com o **Banco Master** e sua
rede de fraude — com valor, data, instrumento e fonte verificável para cada item. Use notícias como ponto
de partida (ground truth) e **valide em base primária** (CVM, BACEN, TCE, PREVIC, portais de transparência).

## Contexto (caso)
Banco Master (controlador Daniel Vorcaro) teve liquidação extrajudicial decretada pelo Banco Central em
**18/11/2025** — tratada como a maior fraude bancária do Brasil (rombo ~R$ 50–52 bi; FGC ~R$ 40 bi). Mecânica:
captava caixa vendendo **CDB a 140% do CDI e Letras Financeiras (LF)**; emprestava a empresas-fachada; os
empréstimos eram recomprados por **FIDCs** (SDG II, Hans 95, Anna, Lancia!, Gold Style…) administrados pela
gestora **Reag / CBSF Trust DTVM** (CNPJ admin 34.829.992/0001-86; gestor 23.863.529/0001-34); vendeu
**R$ 12,2 bi em carteiras fictícias ao BRB** via a fachada **Tirreno**. Operações: Compliance Zero, Barco de
Papel (RioPrevidência), Carbono Oculto (Reag/PCC). CNPJ Banco Master S/A: 33.923.798/0001-00.

## O que JÁ temos (NÃO refazer — partir daqui)
- **DAIR/CADPREV (Carteira 2023–2026):** 33 RPPS mapeados. **Tier-1 (LF/CDB direto do Master): 18 RPPS, R$ 1,53 bi**
  — inclui **RioPrevidência** (arquivada como "Governo do Estado do RJ", CNPJ 42.498.600/0001-71, R$ 568 mi em LF,
  zerada em 12/2025), **Amprev/Amapá** (R$ 435 mi), Maceió, São Roque (18,7%), Cajamar, Itaguaí, Araras, Fátima
  do Sul, Aparecida de Goiânia, Paulista/PE, Jateí… **Tier-2 (fundos Reag): +15 RPPS** (~R$ 73 mi). Série mensal.
- Lado-ativo (carteira do SDG II) reconstruído via CVM (Informe Mensal FIDC) + FNET (Demonstrações Financeiras).
- **Priorize achar o que está FORA dessa base.**

## ALVOS PRIORITÁRIOS (gaps a preencher) — com fontes sugeridas
**P1. RioPrevidência — confirmar e completar.** (a) Confirmar que o ente "Governo do Estado do RJ" (CNPJ
42.498.600/0001-71) no CADPREV é gerido pela RioPrevidência (autarquia CNPJ 03.066.219/0001-81). (b) Achar os
**~R$ 2,01 bi em FUNDOS estruturados** do grupo Master/Reag que a Folha atribui à RioPrev (além dos R$ 568 mi em
LF que já temos): **quais fundos (CNPJ), quando entraram, valor**. Fontes: **TCE-RJ**, portal da RioPrevidência,
CADPREV cadastral, autos da **Operação Barco de Papel** (PF/Justiça do RJ), Folha de S.Paulo.

**P2. BRB (Banco de Brasília).** Detalhar a compra de **R$ 12,2 bi em carteiras** do Master (via Tirreno):
datas, tranches, contabilização; + qualquer LF/CDB do Master no balanço do BRB. Fontes: **BACEN IF.data**
(balanços trimestrais), **CVM** (ITR/DFP, fatos relevantes — BRB é listado, tickers BSLI3/BSLI4), decisão
judicial citada por **Metrópoles/CNN**, RI do BRB.

**P3. Outros bancos públicos.** Algum **comprou carteiras** do Master ou **carrega LF/CDB** do Master?
Verificar: **Banestes (ES)** [atenção: os fundos "Banestes FMP-FGTS" orbitavam a Máxima/Master], **Banese (SE),
Banrisul (RS), BRDE, BNB, Banpará (PA), BDMG (MG), BRB, Banco do Brasil, Caixa**. Fontes: IF.data, CVM, sites de
RI, Diário Oficial, imprensa.

**P4. Tesourarias e RPPS fora do DAIR.** (a) RPPS que não filtram no DAIR ou reportam tarde; (b) **tesourarias
estaduais/municipais (caixa, não-previdência)** com CDB/LF do Master; (c) outras **autarquias estaduais de
previdência** estruturadas como a RioPrev. Fontes: **TCEs estaduais**, portais de transparência, CADPREV.

**P5. EFPC (fundos de pensão fechados de estatais).** Previ (BB), Petros (Petrobras), Funcef (Caixa), Postalis
(Correios), Funpresp, Real Grandeza (Furnas), Fundação CESP etc. — têm exposição a Master/Reag? A imprensa diz
que "os grandes ficaram de fora" — **confirmar ou refutar com dado**. Fontes: **PREVIC**, relatórios anuais das
EFPC, CVM.

**P6. SOEs / agências de fomento / consórcios públicos** com caixa em produtos do Master. Fontes: demonstrações
financeiras das estatais, TCEs.

**P7. Fundos federais.** FAT, FI-FGTS (gerido pela Caixa), FGTS, fundos constitucionais (FNE/FNO/FCO) — qualquer
vínculo com Master/Reag? Fontes: Caixa, BNDES, CGU, TCU.

## Universo a varrer (ultrathink — todas as possibilidades de "dinheiro público → Master")
Para CADA tipo de relação, pergunte "onde o dado público mora?":
1. **Investiu em produto do Master** (LF, CDB, cota de fundo): RPPS→DAIR; EFPC→PREVIC; bancos/SOEs→balanços.
2. **Comprou ativos/carteiras do Master** (ex.: BRB): balanço do comprador + judicial.
3. **Foi cedente/sacado/garantidor** em FIDC do Master: Demonstrações Financeiras dos FIDC (FNET).
4. **Recebeu recursos do Master** (políticos, empresas): autos da PF (fora do escopo "ente público investidor",
   mas anotar se for órgão público).
5. **Garantiu/socorreu** (FGC; tentativa BRB de compra de 58%): FGC, fatos relevantes.

## Metodologia exigida
- Notícia → **validar em fonte primária** antes de afirmar. Diferencie: `verificado_oficial` /
  `reportagem` / `indício`.
- Para cada item: **ente · esfera (fed/est/mun) · tipo de ente · tipo de relação · produto · valor · data/período
  · % da carteira (se houver) · FONTE (URL + data de acesso) · confiança**.
- Marque o **vínculo Reag** (mesmo grupo administrador) vs **Master direto**.
- **Não invente.** Se um dado não for público, diga onde estaria (sigilo? processo?) e pare.
- Priorize o que **NÃO** está no nosso DAIR (ver "o que já temos").

## Entregável
1. **Tabela/CSV** com as colunas acima, ordenada por valor, separando "novos achados" de "já conhecidos".
2. **Resumo executivo:** total de dinheiro público identificado, nº de entes, por esfera e por tipo de relação;
   destaques (maiores, maiores % de carteira, casos com indício de reversão/baixa).
3. **Lista de fontes** consultadas (URLs) e **lacunas remanescentes** (o que segue não-público e por quê).

## Fontes-chave (ponto de partida)
- **CVM:** dados.cvm.gov.br (Informe Mensal FIDC, CDA, registro_fundo, PAS) · FNET fnet.bmfbovespa.com.br
  (Demonstrações Financeiras, fatos relevantes) · cvmweb.cvm.gov.br (fundosreg).
- **BACEN:** IF.data www3.bcb.gov.br/ifdata + olinda.bcb.gov.br/olinda/servico/IFDATA (OData; estava instável).
- **Previdência:** CADPREV/DAIR (gov.br/previdencia) · **PREVIC** (EFPC).
- **Controle externo:** TCE-RJ, TCE-AP, demais TCEs · TCU · CGU/Portal da Transparência.
- **Receita/societário:** Minha Receita (QSA), B3 (debêntures/LF).
- **Imprensa:** Folha de S.Paulo, Valor, CNN Brasil, Agência Brasil, Agência Pública, Metrópoles, NeoFeed, ICL,
  Seu Dinheiro, InfoMoney, BM&C. **Operações:** Compliance Zero, Barco de Papel, Carbono Oculto.
