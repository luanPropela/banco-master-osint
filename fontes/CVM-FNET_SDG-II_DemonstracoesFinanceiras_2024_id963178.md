# Fonte primária — Demonstrações Financeiras auditadas do SDG II (exercício 2024)

Documento que **materializa a fraude** descrita pela matéria: a carteira nominal do SDG II
(cedentes, devedores, debêntures) e o parecer de auditoria.

## Metadados

| Campo | Valor |
|---|---|
| Fundo | SDG II Fundo de Investimento em Direitos Creditórios Não Padronizados |
| CNPJ | 46.909.301/0001-33 |
| Administrador | Reag Trust DTVM S.A. / CBSF DTVM (CNPJ 34.829.992/0001-86) |
| Documento | Demonstrações Financeiras — exercício findo em 31/12/2024 |
| Parecer | **Abstenção de opinião** (auditor não conseguiu validar ~62% dos direitos creditórios) |
| Origem | FNET (B3/CVM), documento id **963178**, entregue 08/08/2025 |
| Download | `https://fnet.bmfbovespa.com.br/fnet/publico/downloadDocumento?id=963178&cvm=true` |
| Captura | 03/06/2026 |

## Integridade

| Arquivo | `CVM-FNET_SDG-II_DemonstracoesFinanceiras_2024_id963178.pdf` |
|---|---|
| SHA-256 | `ef525a0ff5247d04cde7f947a2f0771f445bcc8d1b1d3c3ca3c96e6685f8a19a` |

```bash
sha256sum -c fontes/CVM-FNET_SDG-II_DemonstracoesFinanceiras_2024_id963178.pdf.sha256
```

## Reprodução

API pública do FNET (sem login):

```bash
# listar documentos do fundo
curl 'https://fnet.bmfbovespa.com.br/fnet/publico/pesquisarGerenciadorDocumentosDados?cnpjFundo=46909301000133&l=30&o[0][dataEntrega]=desc'
# baixar o documento
curl -o sdg2_df_2024.pdf 'https://fnet.bmfbovespa.com.br/fnet/publico/downloadDocumento?id=963178&cvm=true'
```

Ver `analise/recon/probe_fnet.py` e `analise/recon/fnet_download.py`.

## Trechos-chave (texto extraído — `data/fnet_docs/SDG2_DemonstracoesFinanceiras_A_963178.txt`)

- **Abstenção de opinião** — base: "ausência de estudos de recuperabilidade dos direitos creditórios e
  ausência parcial de lastro"; "não recebemos a documentação comprobatória do lastro de aproximadamente
  **62%** desses direitos creditórios" (montante de **R$ 6.533.566 mil**).
- **Banco Master S.A. cede direitos creditórios ao SDG II:** 27/02/2024 CCB Lormont R$ 102.438 mil;
  19/12/2024 R$ 192.941 mil; 19/12/2024 R$ 936.222 mil.
- **Lormont Participações S.A.** — 6 CCBs (Carriet R$ 325.452; Master R$ 102.438; B-ROL R$ 41.417;
  CIB-K R$ 40.572; Del Rey R$ 43.107; Runeard R$ 43.953 mil).
- **Banvox Holding Financeira S.A.** — 4ª emissão de debêntures R$ 400.000 mil; Fundo adquiriu
  R$ 380.346 mil em 22/11/2023.
- **Super Empreendimentos e Participações S.A.** — cessão de R$ 22.012 mil em 06/03/2023.
- **Anna FICFIDC-NP** — integraliza cotas do SDG II em 30/09/2024 (pagamento em cártulas BESC).
- Fundos investidos incluem **"FI MMASTER CP"** e **"FIDC Lancia"** (R$ 1.288.087 mil ≈ 40% do PL).
