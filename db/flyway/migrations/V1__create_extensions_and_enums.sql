-- Create extensions if available
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM pg_available_extensions WHERE name = 'postgis') THEN
    EXECUTE 'CREATE EXTENSION IF NOT EXISTS postgis';
  END IF;
  IF EXISTS (SELECT 1 FROM pg_available_extensions WHERE name = 'postgis_topology') THEN
    EXECUTE 'CREATE EXTENSION IF NOT EXISTS postgis_topology';
  END IF;
  IF EXISTS (SELECT 1 FROM pg_available_extensions WHERE name = 'uuid-ossp') THEN
    EXECUTE 'CREATE EXTENSION IF NOT EXISTS "uuid-ossp"';
  END IF;
END$$;

-- Enums
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'papel') THEN
    CREATE TYPE papel AS ENUM ('GESTOR', 'VIGILANCIA', 'CAMPO', 'ADMIN');
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'atividade_status') THEN
    CREATE TYPE atividade_status AS ENUM ('CRIADA', 'EM_ANDAMENTO', 'ENCERRADA');
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'atividade_origem') THEN
    CREATE TYPE atividade_origem AS ENUM ('MANUAL', 'DENUNCIA', 'ALERTA');
  END IF;
END$$;
