# CLAUDE.md — investigação `investigacao-claude/`

Contexto completo (fontes, scripts, convenções, fatos-âncora) em **@AGENTS.md**. Leia-o primeiro.

Abaixo só as regras operacionais que, se ignoradas, causam erro nesta pasta (Windows + conda + CVM/FNET).

## Regras que evitam erro

- **Rode da RAIZ do repo**, via conda, nunca de dentro da pasta:
  `conda run -n master-osint --no-capture-output python investigacao-claude/recon/<x>.py`
  (os scripts gravam cache em `data/` na raiz). Crie o env com `environment.yml`.
- **YOU MUST: nunca passe script multilinha em `conda run ... python -c "..."`** — falha com
  *"scripts where arguments contain newlines not implemented"*. **Escreva o script em arquivo** e rode-o.
- **IMPORTANT: dependências só via `environment.yml`** (recrie/atualize o env); não use `pip install`
  fora do conda env, senão quebra o isolamento.
- **Chrome headless no Windows** exige **caminho Windows absoluto** em `--print-to-pdf` (`C:\...\x.pdf`);
  caminho relativo estilo Unix falha com erro *"não pode encontrar o caminho"* e o PDF não é gerado.
- **FIDC ≠ FI:** para carteira/dados de FIDC use o **Informe Mensal de FIDC** e o **FNET**, nunca o
  `cda_fi` (universo FI/555 não cobre FIDC-NP). Ver @AGENTS.md.
- **FNET** limita após rajadas de download (timeouts) → use retry/backoff e cache; se travar, caia para o
  agente de navegador.
- **Páginas de imprensa (ICL etc.) dão 403** a WebFetch/curl → capture via Chrome real (headless
  print-to-pdf ou subagente de navegador).
- **Push:** sem acesso a `origin` (lyMartins) — push **sempre no remote `fork`** (luanPropela) e PR via
  `gh`. Commits em PT-BR, terminando com `Co-Authored-By: Claude ...`.
- **IMPORTANT: não afirme valores sem rastrear à fonte.** `fontes/` tem as DFs com SHA-256; toda cifra
  reconstruída sai de um documento citável.

## Ao concluir

Rode `investigacao-claude/recon/reconstruir_sdg2.py` e mostre o **scorecard** (matéria × reconstruído)
como evidência — é a verificação de que a reconstrução fecha.
