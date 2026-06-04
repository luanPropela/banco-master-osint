# Onde vive "quem administra/gere o fundo" — e como pegar isso programaticamente

> Pergunta: a informação de administrador/gestor (Reag→CBSF) está **só nas atas de assembleia** ou
> em outro lugar? Objetivo: obter isso da forma mais programática possível, para **qualquer fundo**.

## Resposta curta

**Não está só nas atas.** Administrador e gestor de **qualquer fundo (inclusive FIDC)** estão num
**dataset cadastral aberto e estruturado** da CVM — um único download cobre os ~88 mil fundos. As atas
de assembleia só serviam para o *histórico da troca* (quando o gestor mudou); o estado atual é uma
consulta de CSV.

## As 3 camadas onde a informação aparece (da melhor para a pior)

| Fonte | Tem admin? | Tem gestor? | Cobre FIDC? | Como pegar |
|---|---|---|---|---|
| **`registro_fundo.csv`** (cadastro unificado RCVM 175) | ✅ | ✅ | ✅ | 1 download, programático |
| **Informe Mensal de FIDC** (Tab I) | ✅ | ❌ | ✅ (só FIDC) | ZIP mensal, programático |
| **Atas de Assembleia** (FNET) | ✅ | ✅ | ✅ | PDF, leitura manual/scraping |
| ~~`cad_fi.csv`~~ | ✅ | ✅ | ❌ **não cobre FIDC-NP** | — |

### Fonte canônica: `registro_fundo.csv`

```
https://dados.cvm.gov.br/dados/FI/CAD/DADOS/registro_fundo_classe.zip
   └── registro_fundo.csv   (88.579 fundos; FI, FIDC, FIP, FII)
```

Colunas relevantes: `CNPJ_Fundo, Tipo_Fundo, Denominacao_Social, Situacao, Patrimonio_Liquido,
Diretor, CNPJ_Administrador, Administrador, CPF_CNPJ_Gestor, Gestor`.

Exemplo (SDG II), direto do CSV — **sem ler ata nenhuma**:

```
Administrador : REAG TRUST DTVM            (34.829.992/0001-86)
Gestor        : CBSF TRUST ADM. DE RECURSOS (23.863.529/0001-34)
Situação      : Em Funcionamento Normal
```

> Importante: o **`cad_fi.csv`** (registro antigo, universo FI/555) tem coluna de gestor mas **não
> inclui o SDG II nem outros FIDC-NP** — foi por isso que o gestor "não aparecia" antes. O
> `registro_fundo.csv` (pós-RCVM 175) é o que unificou tudo e cobre FIDC.

### Cross-check grátis

O **administrador** pode ser validado em duas fontes abertas independentes que concordam: o
`registro_fundo.csv` e a coluna `ADMIN` do **Informe Mensal de FIDC** (Tab I). O script já faz esse
cruzamento (coluna `admin_informe_fidc`).

## O que isso revela ao rodar para todo o perímetro (66 fundos)

Resultado em `dados/registro_admin_gestor_fundos.csv`. A concentração sai sozinha do dado:

- **Núcleo da fraude** (SDG II, Anna, Hans 95, Lancia!, Gold Style, Termópilas, Maranta, Stern, Abbiamo):
  administrados por **REAG TRUST DTVM / CBSF Trust** e geridos por gestoras da **família Reag**
  (CBSF Trust, REAG Jus Gestão de Ativos Judiciais, REAG Portfólio Solutions, WNT). É a "teia Reag→CBSF".
- **Perímetro Master mais amplo**: **Master S/A Corretora** figura como **administradora de dezenas**
  de fundos (hoje cancelados), com gestoras Máxima (11), Catálise (7), MAM (5), Tercon (5) — o modelo
  de administração concentrada no grupo Master.

Ou seja: a ligação "SDG II → teia Reag/Master" não depende de nenhuma ata — ela é **reproduzível por um
join de CSV** e ainda escala para descobrir o mesmo padrão em todos os outros fundos.

## Receita programática (escalável a qualquer fundo)

```bash
# baixa registro_fundo_classe.zip e cruza com os CNPJs do perímetro
conda run -n master-osint python investigacao-claude/recon/mapear_admin_gestor.py
# saída: investigacao-claude/dados/registro_admin_gestor_fundos.csv
```

Scripts de investigação desta etapa:
- `recon/probe_admin_gestor.py` — testa onde admin/gestor existem (informe vs cad_fi vs diretórios).
- `recon/probe_registro_rcvm175.py` — acha o `registro_fundo.csv` no cadastro unificado.
- `recon/mapear_admin_gestor.py` — **o mapeador reutilizável** (admin+gestor de N fundos + concentração).

## Quando ainda é preciso scraping/manual

Só para o que **não** está no cadastro estruturado: nomes de **cotistas** (fundo restrito não publica) e
o **histórico/data exata** de troca de gestor (aí sim, ata de assembleia no FNET) — ver
`fontes/README.md` (CVMWeb fundosreg) e `RECONSTRUCAO_SDG2.md`.
