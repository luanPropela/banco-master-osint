# fontes/ — referências verificáveis

Arquivo de fontes primárias do caso, capturadas e com integridade conferível por hash.
Objetivo: toda afirmação do grafo de fraude deve poder ser rastreada até uma fonte
arquivada aqui, não até um link que pode sair do ar ou mudar.

## Índice

| Arquivo | Fonte | Papel |
|---|---|---|
| `ICL_master-usou-fundo-54bi_2026-05-28.pdf` | Folhapress via ICL Notícias, 26/05/2026 | **Matéria-âncora** do fundo SDG II — ground truth do grafo de fraude |
| `ICL_master-usou-fundo-54bi_2026-05-28.md` | idem | Proveniência + transcrição integral + mapeamento aresta↔trecho |
| `CVM-FNET_SDG-II_DemonstracoesFinanceiras_2024_id963178.pdf` | DF auditada SDG II (FNET id 963178) | **Documento que materializa a fraude** — carteira nominal + abstenção de opinião |
| `CVM-FNET_SDG-II_DemonstracoesFinanceiras_2024_id963178.md` | idem | Proveniência + trechos-chave + reprodução via API FNET |
| `*.pdf.sha256` | — | Hash de integridade dos PDFs |

> A reconstrução que usa estas fontes está em `analise/RECONSTRUCAO_SDG2.md` (10 de 11 afirmações
> da matéria reproduzidas a partir de dado público da CVM).

### Verificar integridade de todos os PDFs

```bash
cd fontes && sha256sum -c *.sha256
```

---

## Fonte de extração MANUAL (sem dado aberto / sem API)

> Identificada a pedido: é a fonte que o Carlyle citou no grupo (msgs 398–403, 03/06/2026)
> dizendo *"essa tem que pegar manualmente, não tem nas fontes que eu já tinha"*.

**CVMWeb — Consulta de Fundos Registrados (`fundosreg`)**

```
https://cvmweb.cvm.gov.br/swb/default.asp?sg_sistema=fundosreg
```

- Sistema legado da CVM em ASP. **Não tem API nem dataset em dados.cvm.gov.br** — a navegação
  é por formulário (escolher o fundo, abrir documentos), daí a extração manual.
- É a porta para o que **não** está no Portal de Dados Abertos: cadastro completo do fundo,
  **administrador/gestor/custodiante**, diretor responsável, e os **documentos/balanços**
  de fundos restritos (FIDC-NP fechados como o SDG II).
- Foi por aqui que o Carlyle puxou, em 03/06, o CNPJ do SDG II (`46909301000133`), o PL e a
  carteira (msgs 407–408: *"peguei os cnpjs e os valores pelo site — PL, carteira, etc."*).
  As 6 arestas do grafo com `fonte = CVMWeb consulta manual 03/06/2026` vêm daqui
  (administradora CBSF DTVM, gestor CBSF Trust, diretores Diego Nascimento e Marcos F. Costa).

**Implicação para a reconstrução:** o dado de fluxo do SDG II vive em dois lugares —
(a) **Informe Mensal de FIDC** (dado aberto, `dados.cvm.gov.br/dataset/fidc-doc-inf_mensal`),
que o pipeline ainda **não** coleta; e (b) **CVMWeb fundosreg** (manual), para o que o aberto
não expõe. Estruturar a coleta manual numa tabela com os mesmos campos do Informe Mensal
deixa as duas origens comparáveis no grafo. Ver `analise/ANALISE_RECONSTRUCAO.md`, Passos 1 e 3.

---

## Método de captura

Páginas de imprensa que bloqueiam bots (ICL retorna **HTTP 403** para curl/WebFetch) são
capturadas com um **navegador real** (Chrome headless `--print-to-pdf`, ou navegador MCP).
O comando exato de reprodução fica no `.md` de cada fonte. O texto transcrito no `.md`
confere com o PDF — o PDF é a evidência visual, o `.md` é a versão pesquisável e diffável.
