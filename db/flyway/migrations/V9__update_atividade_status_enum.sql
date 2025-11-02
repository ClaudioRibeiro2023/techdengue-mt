-- V9: Update atividade_status enum to add CONCLUIDA and CANCELADA

-- Add new enum values if they don't exist
DO $$
BEGIN
    -- Add CONCLUIDA
    IF NOT EXISTS (
        SELECT 1 FROM pg_enum 
        WHERE enumtypid = 'atividade_status'::regtype 
        AND enumlabel = 'CONCLUIDA'
    ) THEN
        ALTER TYPE atividade_status ADD VALUE 'CONCLUIDA';
    END IF;
    
    -- Add CANCELADA
    IF NOT EXISTS (
        SELECT 1 FROM pg_enum 
        WHERE enumtypid = 'atividade_status'::regtype 
        AND enumlabel = 'CANCELADA'
    ) THEN
        ALTER TYPE atividade_status ADD VALUE 'CANCELADA';
    END IF;
END$$;

-- Optional: Update existing ENCERRADA records to CONCLUIDA (if any)
-- UPDATE atividade SET status = 'CONCLUIDA' WHERE status = 'ENCERRADA';

-- Add IMPORTACAO to atividade_origem enum
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_enum 
        WHERE enumtypid = 'atividade_origem'::regtype 
        AND enumlabel = 'IMPORTACAO'
    ) THEN
        ALTER TYPE atividade_origem ADD VALUE 'IMPORTACAO';
    END IF;
END$$;

COMMENT ON TYPE atividade_status IS 'Status: CRIADA, EM_ANDAMENTO, CONCLUIDA, CANCELADA, ENCERRADA (deprecated)';
COMMENT ON TYPE atividade_origem IS 'Origem: MANUAL, IMPORTACAO, ALERTA, DENUNCIA (deprecated)';
