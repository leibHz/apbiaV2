CREATE OR REPLACE FUNCTION get_participantes_projeto(p_projeto_id bigint)
RETURNS TABLE (
  id bigint,
  nome_completo character varying,
  email character varying,
  bp character varying
) AS $$
BEGIN
  RETURN QUERY
  SELECT u.id, u.nome_completo, u.email, u.bp
  FROM usuarios u
  INNER JOIN participantes_projetos pp ON u.id = pp.participante_id
  WHERE pp.projeto_id = p_projeto_id;
END;
$$ LANGUAGE plpgsql;

-- Função para buscar orientadores de um projeto
CREATE OR REPLACE FUNCTION get_orientadores_projeto(p_projeto_id bigint)
RETURNS TABLE (
  id bigint,
  nome_completo character varying,
  email character varying
) AS $$
BEGIN
  RETURN QUERY
  SELECT u.id, u.nome_completo, u.email
  FROM usuarios u
  INNER JOIN orientadores_projetos op ON u.id = op.orientador_id
  WHERE op.projeto_id = p_projeto_id;
END;
$$ LANGUAGE plpgsql;