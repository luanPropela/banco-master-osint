# Documentação — Caso Banco Master / Daniel Vorcaro

Documento autocontido. Combina **(a)** síntese do caso a partir de fontes públicas até maio/2026, **(b)** estado do projeto OSINT, **(c)** setup cross-platform para Windows / Arch Linux / Parrot OS.

Última revisão: 13/05/2026.

---

## 1. O caso em uma página

O Banco Master, controlado por Daniel Bueno Vorcaro, teve sua liquidação extrajudicial decretada pelo Banco Central em **18/11/2025**, um dia depois de o próprio BC derrubar a venda do banco a um consórcio liderado pela Fictor Holding Financeira.

Quando foi liquidado, o Master tinha **R$ 80 bilhões em ativos declarados e R$ 4 milhões em caixa**. As investigações apontam que um esquema de fraude foi montado para esconder um rombo da ordem de **R$ 50 a R$ 52 bilhões**, dos quais cerca de **R$ 40 bilhões já foram desembolsados pelo FGC** (Fundo Garantidor de Crédito) para cobrir os depósitos garantidos dos correntistas.

O caso é tratado pela imprensa como **a maior fraude bancária da história brasileira**.

## 2. Mecânica da fraude (segundo a investigação da PF e BC)

Estrutura em 6 elementos:

### 2.1 CDB acima do mercado (a "isca")

O Master comercializou CDBs com retornos **de 140% do CDI**, enquanto o mercado pagava ~100%. Esse retorno **artificialmente alto** atraía investidor pessoa física buscando rendimento, mas era economicamente insustentável.

### 2.2 Pirâmide via CDB

A Polícia Federal indica que o banco **emitia novos CDBs para pagar os antigos** — caracterização clássica de pirâmide financeira. Em algum momento, **valores já inflados foram reinvestidos em CDBs do próprio Master**, fechando o ciclo.

### 2.3 Triangulação com BRB via TIRRENO

A Tirreno foi identificada pela PF como **empresa de fachada criada pelo próprio Vorcaro**. O mecanismo:

1. Master "vende" carteiras de crédito para a Tirreno
2. Tirreno revende as mesmas carteiras para o **Banco de Brasília (BRB)** por **R$ 12,2 bilhões**, com prêmio embutido
3. Master não precisava pagar a Tirreno à vista — mas **recebia do BRB à vista**
4. As carteiras de crédito nunca existiram efetivamente — os contratos teriam sido **fabricados**

### 2.4 Salvação amiga via BRB (frustrada)

Em **março/2025**, o BRB (banco público estadual do DF) anunciou compra de **58% do Master**. A operação foi vista pelo mercado como possível socorro indireto com dinheiro público. O BC **bloqueou a operação** meses depois, mas o BRB já havia adquirido as carteiras podres mencionadas em 2.3.

O governador Ibaneis Rocha, do DF, foi citado nas reportagens como ligado à crise do Master via BRB.

### 2.5 Negligência regulatória

Reportagens apontam que o ex-presidente do BC **Roberto Campos Neto** (saiu em jan/2025, hoje no conselho do Nubank) **ignorou alertas sobre o crescimento acelerado do Master** e permitiu uma "solução particular" às custas do contribuinte. Senadores em **mai/2026** questionaram formalmente por que o BC negou e depois aprovou a venda do Master.

### 2.6 Financiamento de operações clandestinas

A PF aponta que Vorcaro **financiava grupos responsáveis por ameaças, espionagem ilegal, invasões cibernéticas e obtenção de informações confidenciais**. Não é só fraude bancária — é estrutura de captura institucional.

## 3. Cronograma da Operação Compliance Zero

| Fase | Data | Marco |
|---|---|---|
| 1 | nov/2025 | Vorcaro preso; bloqueio de R$ 12,2 bilhões em contas; apreensão de carros de luxo, obras de arte e relógios |
| 2 | nov-dez/2025 | Liquidação extrajudicial decretada; FGC paga depositantes |
| 3-4 | dez/2025-jan/2026 | Liquidação da Reag (operações conjuntas) |
| 5 | abr/2026 | Divulgada lista de políticos que receberam recursos do Master |
| **6** | **14/05/2026** | **Pai de Daniel Vorcaro é preso** |

## 4. Atores principais

### Bancos e instituições financeiras

| Entidade | Papel | Status atual |
|---|---|---|
| Banco Master S/A | banco múltiplo principal | em liquidação extrajudicial (BACEN) |
| Banco Master Múltiplo S/A | braço bancário paralelo | em liquidação |
| Banco Master de Investimento S/A | banco de investimento | em liquidação |
| Banco Letsbank S/A | fintech adquirida | em liquidação |
| Master S/A Corretora CCTVM | administradora fiduciária de 57 fundos | em liquidação |
| Viking Participações Ltda | holding pessoal do Vorcaro | ativa |
| **Tirreno** | empresa de fachada para triangulação | sob investigação |
| **Fictor Holding Financeira** | consórcio que tentou comprar o Master | sob investigação |
| **BRB (Banco de Brasília)** | comprador frustrado de 58% do Master + adquirente de R$ 12,2 bi em carteiras | banco público estadual operacional |
| **Reag** | parceiro em operações | liquidado em jan/2026 |
| **Banco Pleno** | presidido por ex-sócio do Master | liquidado em fev/2026 (efeito-contágio) |

### Pessoas (identificadas em reportagem)

- **Daniel Bueno Vorcaro** — controlador, preso em nov/2025
- **Pai de Daniel Vorcaro** — preso em 14/05/2026 (6ª fase)
- **Roberto Campos Neto** — ex-presidente BACEN, citado por negligência
- **Michel Temer** — ex-presidente, recebeu recursos
- **ACM Neto** — ex-prefeito de Salvador, recebeu recursos
- **Antônio de Rueda** — então presidente do União Brasil, recebeu recursos
- **Ciro Nogueira** — esquema mencionado em apuração da CNN
- **Ibaneis Rocha** — governador do DF, ligado via BRB

### Dataset interno (master.db) — pessoas mapeadas

104 pessoas no QSA das 47 CNPJs raiz (após expansão de SEEDS). Top 10 por número de empresas:

| Nome | Empresas | Cargo |
|---|---|---|
| Angelo Antonio Ribeiro da Silva | 4 entidades Master | Diretor |
| Luiz Antonio Bull | 4 entidades Master | Diretor/Presidente |
| Alexandre Jorge Chaia | trio Carmel | Sócio-Administrador |
| Gustavo Augusto Vasconcelos Biava | dupla ID Gestora | Sócio-Administrador |
| José Roberto Giancoli Filho | dupla ID Gestora | Sócio-Administrador |
| Daniel Bueno Vorcaro | 3 entidades Master | Presidente / Sócio |
| Ademir Silva Oliveira | trio Carmel | Sócio-Administrador |
| Mauricio Antonio Quadrado | Letsbank + Trustee | Presidente |
| Guaraci Sillos Moreira | trio Carmel | Sócio |
| Renata Ferraz de Andrade | trio Squalo | Sócio-Administrador |

## 5. Achados próprios do projeto OSINT (a partir do dataset)

Resultados verificados no `data/master.db` que adicionam camadas à narrativa pública:

1. **Maurício Quadrado é a ponte Letsbank-Trustee** — Presidente do Letsbank desde 01/11/2024, é também sócio da Trustee Holding Financeira S/A e da Trustee DTVM. A Trustee DTVM administra ao menos um dos fundos do escopo Master.
2. **KATCH FIDC → UPPER FIDC** — operação intragrupo confirmada pela CVM. O KATCH (administrado pela Master Corretora, gerido pela Harbour Capital) manteve **R$ 32,6 milhões (99% do PL) em cotas do UPPER FIDC**, marcado como `EMISSOR_LIGADO=S` na CVM. KATCH com situação CANCELADA; UPPER fora do `cad_fi.csv`.
3. **STERN FIP Multiestratégia** — veículo criado em 15/08/2024 que entra na Viking (holding do Vorcaro) em **29/09/2025**, exatas 4 semanas antes da liquidação. Junto entra **Adriano Garzon Correa** como Administrador. Movimento sugestivo de reorganização patrimonial pré-colapso.
4. **Cronograma de degradação dos FMP-FGTS** — Maxima FMP-FGTS Petrobras opera até 12/11/2025 (3 dias antes da liquidação); dois Banestes FMP-FGTS param de reportar em **06/08/2025** (3 meses antes); MAXIMA FMP-FGTS Vale do Rio Doce nem aparece em 2025.
5. **Histórico CVM da Máxima Asset** — processo administrativo sancionador NUP 19957003200201708 (2017) contra MÁXIMA S/A CCTVM, MÁXIMA ASSET MANAGEMENT e dois indivíduos por descumprimento da Instrução CVM 409. Máxima é a maior gestora parceira do Master no nosso dataset (11 fundos).
6. **Modelo de admin terceirizada confirmado** — nenhuma das 18 gestoras parceiras (Máxima, Catálise, Tercon, MAM, Acura, Bluemac, Squalo, Menestys, Carmel etc.) compartilha sócio PF com o grupo Master. Estruturas societárias verdadeiramente independentes.

---

## 6. Setup do projeto (cross-platform)

Reproduzível em Windows, Arch Linux ou Parrot OS. Requisitos mínimos:

- Python 3.10+ (testado em 3.12 e 3.14)
- Git
- ~500 MB de espaço em disco (caches CVM + DB)
- Conexão com internet (para coleta inicial; depois roda offline com cache)

### 6.1 Instalação por sistema operacional

#### Windows 10/11

```powershell
# Python (se não tiver)
winget install Python.Python.3.12

# Git (se não tiver)
winget install Git.Git

# Clone
cd $HOME\PycharmProjects   # ou onde preferir
git clone https://github.com/lyMartins/banco-master-osint.git
cd banco-master-osint

# Ambiente virtual
python -m venv .venv
.venv\Scripts\activate

# Dependências
pip install -r requirements.txt
```

#### Arch Linux

```bash
# Pacotes do sistema
sudo pacman -S python python-pip git base-devel

# Clone
cd ~/projects
git clone https://github.com/lyMartins/banco-master-osint.git
cd banco-master-osint

# Ambiente virtual
python -m venv .venv
source .venv/bin/activate

# Dependências
pip install -r requirements.txt
```

#### Parrot OS (ou Debian/Ubuntu/Kali em geral)

```bash
# Pacotes do sistema
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git build-essential

# Clone
cd ~/projects
git clone https://github.com/lyMartins/banco-master-osint.git
cd banco-master-osint

# Ambiente virtual
python3 -m venv .venv
source .venv/bin/activate

# Dependências
pip install -r requirements.txt
```

### 6.2 Pipeline de coleta — passo a passo

Cada comando independente. A ordem importa porque a fase 2 precisa da fase 1 etc.

```bash
# 1. QSA via Minha Receita (Fase 1 + expansão de seeds)
python -m coleta.receita

# 2. Cadastro CVM dos fundos com vínculo Master (Fase 2)
python -m grafo.b2b

# 3. Consolidar caches em SQLite
python -m db

# 4. Informe diário CVM (FMP-FGTS no caso base)
python -m coleta.cvm_diario

# 5. Processo Sancionador CVM
python -m coleta.cvm_sancoes

# 6. Composição da Carteira CVM (CDA)
python -m coleta.cvm_carteira
```

> No Windows, use `python` em vez de `python3` em todos os comandos. Em Linux, dependendo da distro, `python3` é o canônico — mas dentro do venv ativado, ambos funcionam.

### 6.3 Análise — formas de interagir

| Modo | Comando | Quando usar |
|---|---|---|
| Pipeline completo de grafo | `python pipeline.py` | gera grafo PyVis + visualização |
| Notebook geral (hub) | `jupyter notebook hub_analise.ipynb` | exploração ampla, RF Proximity |
| Notebook focado Vorcaro | `jupyter notebook vorcaro_circulo.ipynb` | só o círculo próximo (11 pessoas) |
| **Notebook de estudo (este projeto)** | `jupyter notebook estudo_master.ipynb` | tour didático pelos dados |
| Consultas pandas avulsas | `python -c "from consultas import *; print(participacoes_de('VORCARO'))"` | consultas rápidas no terminal |
| SQL direto | abrir `data/master.db` no DBeaver/DB Browser | exploração ad-hoc |

### 6.4 Estrutura do repositório

```
banco-master-osint/
├── DOCUMENTACAO.md            este arquivo
├── README.md
├── requirements.txt
├── .gitignore
│
├── config.py                  SEEDS_MASTER + SEEDS_EXPANSAO
├── pipeline.py                orquestra Fase 1 + grafo + viz
├── db.py                      caches JSON → SQLite
├── consultas.py               funções pandas de consulta
├── vorcaro.py                 ego-grafo standalone
│
├── coleta/
│   ├── receita.py             Fase 1 — Minha Receita
│   ├── cvm_diario.py          Informe diário (517 linhas, 4 FMP-FGTS)
│   ├── cvm_sancoes.py         Processo Sancionador CVM
│   └── cvm_carteira.py        CDA — Composição da Carteira
│
├── grafo/
│   ├── societario.py          NetworkX DiGraph
│   ├── b2b.py                 Fase 2 — cad_fi.csv CVM
│   ├── analise.py             métricas de grafo
│   └── visualizacao.py        PyVis + matplotlib
│
├── queries/
│   └── exemplos.sql           queries documentadas
│
├── hub_analise.ipynb          notebook geral (104 pessoas)
├── vorcaro_circulo.ipynb      notebook focado (11 pessoas)
├── estudo_master.ipynb        notebook didático ← este projeto adiciona
│
└── data/                      caches e db (gitignored)
    ├── cnpjs.json             QSA Receita
    ├── fundos_b2b.json        CVM cad_fi
    ├── master.db              SQLite consolidado
    ├── cvm_diario/            zips mensais Informe Diário
    ├── cvm_carteira/          zips mensais CDA
    └── cvm_sancao.zip         PAS CVM
```

### 6.5 Apresentação / pitch

Há um deck pronto em `pitch.md`, formato **Marp** (markdown com diretivas).

**Renderizar via CLI (qualquer sistema):**

```bash
# instala o Marp CLI (uma vez)
npm install -g @marp-team/marp-cli

# exporta para PDF
marp pitch.md --pdf -o pitch.pdf

# exporta para HTML standalone
marp pitch.md --html -o pitch.html

# exporta para PowerPoint
marp pitch.md --pptx -o pitch.pptx

# preview ao vivo enquanto edita
marp pitch.md --server
```

**Renderizar via VSCode (mais fácil):**

1. Instalar extensão **"Marp for VS Code"**
2. Abrir `pitch.md`
3. Clicar no ícone de preview (canto superior direito)
4. Exportar pelo menu da extensão (PDF/HTML/PPTX)

Os 16 slides cobrem: hook, contexto do caso, dataset, método, 4 achados-bomba, RF Proximity, limites, próximos passos, repositório.

### 6.6 Solução de problemas comuns

**Erro: `ModuleNotFoundError: No module named 'pandas'`**
→ Ambiente virtual não foi ativado, ou `pip install -r requirements.txt` falhou. Confirme com `which python` (Linux) ou `where python` (Windows) — deve apontar pra `.venv/`.

**Erro: `FileNotFoundError: data/cnpjs.json`**
→ A Fase 1 ainda não rodou. Execute `python -m coleta.receita` primeiro.

**Erro: `sqlite3.OperationalError: no such table: ...`**
→ O `master.db` ainda não foi populado. Execute `python -m db` depois das fases anteriores.

**Coleta CVM mensal demora muito**
→ Os zips do CDA têm 25 MB cada. Os do informe diário, 11 MB. Tudo fica cacheado em `data/cvm_*/` após o primeiro download.

**Notebook Jupyter não abre em Linux sem GUI**
→ Use `jupyter lab --no-browser --port 8888` e acesse via `ssh -L 8888:localhost:8888`.

**`gh` não disponível para PR**
→ Instalar:
- Windows: `winget install GitHub.cli`
- Arch: `sudo pacman -S github-cli`
- Parrot/Debian: `sudo apt install gh`

---

## 7. Fontes utilizadas (junho/2026)

### Reportagens e cobertura jornalística

- [Wikipedia — Escândalo do Banco Master](https://pt.wikipedia.org/wiki/Esc%C3%A2ndalo_do_Banco_Master)
- [CNN Brasil — Entenda a "teia" de fraudes envolvendo o Banco Master](https://www.cnnbrasil.com.br/economia/macroeconomia/entenda-a-teia-de-fraudes-envolvendo-o-banco-master/)
- [CNN Brasil — PF deflagra nova fase da operação Compliance Zero](https://www.cnnbrasil.com.br/politica/pf-deflagra-nova-fase-da-operacao-compliance-zero-pai-de-vorcaro-e-preso/)
- [CartaCapital — Como funcionava o esquema que inflou a liquidez do Banco Master](https://www.cartacapital.com.br/economia/como-funcionava-o-esquema-que-inflou-a-liquidez-do-banco-master/)
- [Agência Brasil — BC decreta liquidação do Banco Pleno, presidido por ex-sócio do Master](https://agenciabrasil.ebc.com.br/economia/noticia/2026-02/bc-decreta-liquidacao-do-banco-pleno-presidido-por-ex-socio-do-master)
- [Agência Brasil — Entenda as liquidações do Banco Master e da Reag](https://agenciabrasil.ebc.com.br/economia/noticia/2026-01/entenda-liquidacoes-do-banco-master-e-da-reag)
- [Agência Brasil — Pai de Daniel Vorcaro é preso na 6ª fase](https://agenciabrasil.ebc.com.br/geral/noticia/2026-05/pai-de-daniel-vorcaro-e-preso-na-6a-fase-da-operacao-compliance-zero)
- [Agência Pública — Banco Master: a reconstrução completa de como uma fraude capturou a República](https://apublica.org/2026/03/banco-master-a-reconstrucao-completa-de-como-uma-fraude-capturou-a-republica/)
- [Agência Pública — BRB, rombo bilionário e a questão Ibaneis Rocha](https://apublica.org/2026/02/brb-como-ibaneis-rocha-esta-ligado-a-crise-do-banco-master/)
- [Brasil de Fato — A reconstrução completa](https://www.brasildefato.com.br/2026/03/13/banco-master-a-reconstrucao-completa-de-como-uma-fraude-capturou-a-republica/)
- [Seu Dinheiro — Como o Banco Master entra em 2026](https://www.seudinheiro.com/2026/empresas/como-o-banco-master-entra-em-2026-da-corrida-por-cdbs-turbinados-a-liquidacao-investigacoes-e-pressao-sobre-o-bc-miql/)
- [ISTOÉ — Como funcionava o esquema](https://istoe.com.br/como-funcionava-o-esquema-do-banco-master-segundo-a-investigacao)
- [Senado — Senadores questionam como BC negou e depois aprovou venda](https://www12.senado.leg.br/noticias/materias/2026/05/19/senadores-questionam-como-bc-negou-e-depois-aprovou-venda-do-master-a-vorcaro)
- [NeoFeed — Após Banco Master, próximo escândalo será com fundos](https://neofeed.com.br/negocios/apos-banco-master-proximo-escandalo-sera-com-os-fundos-de-investimento-diz-mercadante/en/)
- [ICL Notícias — Roberto Campos Neto e o Banco Master](https://iclnoticias.com.br/roberto-campos-neto-o-fiador-da-salvacao-amiga-do-banco-master-com-o-brb/)
- [Gazeta do Paraná — Soltura de Vorcaro e executivos](https://gazetadoparana.com.br/artigo/entenda-a-soltura-de-daniel-vorcaro-e-executivos-do-banco-master)
- [Wikipedia EN — Daniel Vorcaro](https://en.wikipedia.org/wiki/Daniel_Vorcaro)

### Bases de dados públicas usadas pelo pipeline

- [Minha Receita](https://minhareceita.org) — espelho aberto do cadastro Receita Federal
- [CVM Dados Abertos](https://dados.cvm.gov.br) — cadastros, informes diários e mensais, sanções
- [Portal da Transparência](https://www.portaldatransparencia.gov.br) — CEIS, CNEP (não usado ainda; bloqueado por token)
- [BACEN IF.data](https://www3.bcb.gov.br/ifdata) — composição acionária de bancos (não usado ainda; SPA)

### Bases para investigação manual

- [JusBrasil](https://www.jusbrasil.com.br) — processos judiciais por CPF/CNPJ
- [Diário Oficial da União](https://www.in.gov.br) — atos BACEN, CVM, PF
- [JUCESP](https://www.jucesponline.sp.gov.br) — atos societários SP (cobra por documento)
- [TCE-ES](https://www.tce.es.gov.br) — fiscalização do Banestes
- [OpenCorporates](https://opencorporates.com) — estruturas internacionais
- [ICIJ Offshore Leaks DB](https://offshoreleaks.icij.org) — Panama/Pandora Papers

---

## 8. Limites metodológicos declarados

- **Snapshot, não histórico** — os cadastros consultados representam o estado atual; mudanças anteriores não aparecem.
- **CPFs vêm mascarados** pela Receita Federal — pessoas com nomes idênticos seriam fundidas em um único nó (risco baixo no nosso conjunto, mas existe).
- **O grafo mostra relação cadastral, não imputa culpa** — aparecer como sócio/gestor/custodiante é fato administrativo público, não acusação.
- **A análise não usa fontes confidenciais.** Apenas dados que qualquer pessoa com Python e acesso à internet pode reproduzir.
- **Síntese baseada em fontes de imprensa de mai/2026** — dados podem ter evoluído. Confirme datas e valores antes de publicar.

## 9. Aviso

Pesquisa educacional e jornalística sobre dados públicos. Todos os scripts são reproduzíveis: qualquer pessoa com Python e internet roda e chega nos mesmos resultados.
