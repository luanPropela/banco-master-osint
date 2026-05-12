# BancoMaster OSINT

Mapeamento da rede societária do conglomerado **Banco Master** a partir de
dados públicos da Receita Federal, com visualização interativa em grafo
para análise OSINT.

## Contexto

Em novembro de 2025 o Banco Central decretou a liquidação extrajudicial do
Banco Master e de suas controladas após o estouro do escândalo de manobras
contábeis e operações suspeitas com CDBs. A **Operação Compliance Zero**,
da Polícia Federal, mira o controlador Daniel Vorcaro e o entorno
societário do grupo. Este projeto pega o QSA (Quadro de Sócios e
Administradores) das empresas do conglomerado e desenha as relações
pessoa↔empresa para facilitar a leitura jornalística e didática.

> ⚠️ **Fins educacionais e jornalísticos.** Todos os dados utilizados são
> públicos, obtidos via [Minha Receita](https://minhareceita.org), que
> expõe o cadastro da Receita Federal. CPFs vêm mascarados na origem.

## Instalação

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

pip install -r requirements.txt
```

Requisitos: Python 3.10+ (foi desenvolvido em 3.14).

## Uso básico

```bash
python main.py
```

Na primeira execução, o script bate na API Minha Receita e cacheia o
resultado em `data/cnpjs.json`. Nas execuções seguintes, ele carrega do
cache — apague o arquivo (ou chame `carregar_ou_coletar(forcar=True)`)
para forçar uma nova coleta.

Ao final, dois HTMLs são abertos automaticamente no navegador:

- `grafo_master.html` — grafo completo sócio → empresa
- `grafo_pessoas.html` — projeção pessoa-pessoa (sócios em comum)

## Estrutura do projeto

| Arquivo | Responsabilidade |
|---|---|
| `config.py` | Seeds, profundidade do BFS, cores e caminhos de cache |
| `coleta.py` | Consulta à API Minha Receita e cache em disco |
| `grafo.py` | Construção do `DiGraph` e projeção pessoa-pessoa |
| `analise.py` | Métricas (graus, betweenness), componentes, busca por nome |
| `visualizacao.py` | Renderização PyVis (HTML interativo) e Matplotlib (PNG) |
| `main.py` | Pipeline completo (ponto de entrada) |
| `data/` | Cache da coleta e exports estáticos |

Cada módulo tem responsabilidade única — quem quiser usar só a coleta,
por exemplo, pode importar `coleta.carregar_ou_coletar` sem trazer
PyVis junto.

## Adicionando novos seeds

Os seeds vivem em `config.py`. Para investigar outro conglomerado, basta
adicionar pares `CNPJ → razão social`:

```python
SEEDS = {
    "33923798000100": "Banco Master S.A.",
    "12345678000199": "Nova Empresa S.A.",   # ← novo seed
    ...
}
```

A coleta segue automaticamente sócios pessoa jurídica até a profundidade
definida em `MAX_DEPTH`. Pessoas físicas não são expandidas porque o
CPF vem mascarado pela Receita.

## Métricas exibidas

- **in_degree**: número de sócios que apontam para o nó (entrada). Para
  uma empresa, é o tamanho do QSA. Para uma pessoa, normalmente é 0.
- **out_degree**: número de empresas em que o nó participa (saída). Para
  uma pessoa, conta quantas empresas ela é sócia. Para uma empresa,
  conta quantas outras ela é sócia.
- **betweenness centrality**: fração dos caminhos mais curtos do grafo
  que passam por aquele nó. Nós com betweenness alta são "pontes" entre
  comunidades — costumam ser o alvo mais interessante numa investigação
  OSINT, porque cortá-los desconecta partes da rede.

O grafo também é analisado quanto a:

- **Componentes desconexos** — blocos isolados podem ser veículos
  paralelos do mesmo grupo.
- **Pontos de articulação** — nós cuja remoção fragmenta o grafo, ou
  seja, "costuram" subgrupos.

## Fontes de dados

- API [Minha Receita](https://minhareceita.org) — proxy aberto do
  cadastro da Receita Federal (CNPJ, QSA, CNAE, situação cadastral).
- Cobertura noticiosa da Operação Compliance Zero (Folha, Estadão, Veja,
  Valor) — usada apenas para selecionar os seeds iniciais.

## Roadmap

- [ ] Persistir o grafo em formato `gexf` / `graphml` para abrir no Gephi
- [ ] Exportar tabela de métricas em CSV
- [ ] Adicionar detecção de comunidades (Louvain / Leiden)
- [ ] Cruzar com dados do Portal da Transparência (sanções, CEIS, CNEP)
- [ ] Histórico do QSA (entradas/saídas de sócios ao longo do tempo)
- [ ] Anotações manuais de relações fora do QSA (familiares, operações PF)
- [ ] Dashboard web (Streamlit) para navegação interativa

## Aviso legal

Este projeto utiliza exclusivamente **dados públicos** já disponíveis no
cadastro da Receita Federal, replicados pela API Minha Receita. Foi
construído com fins **educacionais, de pesquisa e jornalísticos**. Não
há tentativa de identificação de pessoas naturais a partir de CPFs
mascarados, nem coleta de informações sensíveis.
