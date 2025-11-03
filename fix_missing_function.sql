-- Criar função update_updated_at_column que falta

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Confirmar criação
SELECT 'Função update_updated_at_column() criada com sucesso!' as status;
