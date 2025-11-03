-- V015__add_fk_denuncias_atividade.sql
-- Adiciona FK denuncias_publicas.atividade_id -> atividades(id)

DO $$
BEGIN
  -- Garante que a tabela existe
  IF EXISTS (
    SELECT 1 FROM information_schema.tables 
    WHERE table_schema = 'public' AND table_name = 'denuncias_publicas'
  ) THEN
    -- Só cria a constraint se ainda não existir
    IF NOT EXISTS (
      SELECT 1 FROM information_schema.table_constraints 
      WHERE constraint_schema = 'public'
        AND table_name = 'denuncias_publicas'
        AND constraint_name = 'fk_denuncia_atividade'
    ) THEN
      ALTER TABLE public.denuncias_publicas
        ADD CONSTRAINT fk_denuncia_atividade
        FOREIGN KEY (atividade_id)
        REFERENCES public.atividades(id)
        ON DELETE SET NULL;
    END IF;
  END IF;
END$$;
