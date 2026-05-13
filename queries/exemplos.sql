-- queries de exploração sobre data/master.db
-- abre no DBeaver, DB Browser ou sqlite3 cli


-- empresas onde Vorcaro participa
SELECT e.razao_social, p.qualificacao
FROM participacoes p
JOIN pessoas s   ON s.id = p.socio_pessoa_id
JOIN empresas e  ON e.cnpj = p.empresa_cnpj
WHERE s.nome LIKE '%VORCARO%';


-- pessoas presentes em N entidades do grupo Master
SELECT s.nome, COUNT(*) AS quantas
FROM participacoes p
JOIN pessoas s ON s.id = p.socio_pessoa_id
GROUP BY s.nome
HAVING quantas >= 3
ORDER BY quantas DESC;


-- top gestoras parceiras da Master (por nº de fundos sob gestão)
SELECT prestador_nome, COUNT(*) AS n_fundos
FROM papeis_fundo
WHERE papel = 'gestor' AND prestador_nome IS NOT NULL
GROUP BY prestador_nome
ORDER BY n_fundos DESC
LIMIT 10;


-- fundos com nome sugestivo de dinheiro público / FGTS
SELECT DISTINCT e.cnpj, e.razao_social
FROM empresas e
JOIN papeis_fundo p ON p.fundo_cnpj = e.cnpj
WHERE e.fonte = 'cvm'
  AND (UPPER(e.razao_social) LIKE '%FGTS%'
       OR UPPER(e.razao_social) LIKE '%FMP%'
       OR UPPER(e.razao_social) LIKE '%PETROBRAS%'
       OR UPPER(e.razao_social) LIKE '%BANESTES%');


-- fundos onde Master Corretora administra E gestor é externo
SELECT e.razao_social AS fundo, pf.prestador_nome AS gestor
FROM papeis_fundo pa
JOIN papeis_fundo pf ON pf.fundo_cnpj = pa.fundo_cnpj AND pf.papel = 'gestor'
JOIN empresas e ON e.cnpj = pa.fundo_cnpj
WHERE pa.papel = 'admin'
  AND pa.prestador_cnpj = '33886862000112';


-- evolução do PL e cotistas dos FMP-FGTS (últimos 30 dias de cada)
SELECT fundo_cnpj, data, ROUND(pl,2) AS pl, cotistas,
       ROUND(captacao_dia,2) AS captacao, ROUND(resgate_dia,2) AS resgate
FROM inf_diario
ORDER BY fundo_cnpj, data DESC;


-- resgates atípicos (> 50k em um único dia)
SELECT fundo_cnpj, data, ROUND(resgate_dia,2) AS resgate,
       cotistas, ROUND(pl,2) AS pl_pos
FROM inf_diario
WHERE resgate_dia > 50000
ORDER BY resgate_dia DESC;


-- variação de cotistas mês a mês por fundo
SELECT fundo_cnpj,
       SUBSTR(data, 1, 7) AS mes,
       MIN(cotistas) AS cot_min,
       MAX(cotistas) AS cot_max,
       ROUND(AVG(pl)/1e6, 2) AS pl_med_milhoes
FROM inf_diario
GROUP BY fundo_cnpj, SUBSTR(data, 1, 7)
ORDER BY fundo_cnpj, mes;
