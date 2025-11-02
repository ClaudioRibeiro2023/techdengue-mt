"""
ETL EPI Persistence Service
Handles database operations for validated EPI records
"""
from typing import List
from datetime import datetime, date
import hashlib
import psycopg2
from psycopg2.extras import execute_values

from app.schemas.etl_epi import EPIRecordCSV
from app.services.etl_validator import calcular_faixa_etaria


def competencia_to_date(competencia: str) -> date:
    """Convert YYYYMM string to first day of month as date.
    Example: '202401' -> date(2024, 1, 1)
    """
    year = int(competencia[:4])
    month = int(competencia[4:6])
    return date(year, month, 1)


def build_dedup_key(record: EPIRecordCSV, comp_date: date) -> str:
    """Build a deterministic SHA-256 key to deduplicate identical records.
    Uses competencia (as date) and key record fields to compose the fingerprint.
    """
    def _d(v):
        if v is None:
            return ""
        if hasattr(v, "isoformat"):
            try:
                return v.isoformat()
            except Exception:
                pass
        return str(v)

    parts = [
        _d(comp_date),
        _d(record.municipio_cod_ibge),
        _d(record.dt_sintomas),
        _d(record.dt_notificacao),
        _d(record.sexo),
        _d(record.idade),
        _d(record.gestante),
        _d(record.classificacao_final),
        _d(record.criterio_confirmacao),
        _d(record.febre),
        _d(record.cefaleia),
        _d(record.dor_retroocular),
        _d(record.mialgia),
        _d(record.artralgia),
        _d(record.exantema),
        _d(record.vomito),
        _d(record.nausea),
        _d(record.dor_abdominal),
        _d(record.plaquetas_baixas),
        _d(record.hemorragia),
        _d(record.hepatomegalia),
        _d(record.acumulo_liquidos),
        _d(record.diabetes),
        _d(record.hipertensao),
        _d(record.evolucao),
        _d(record.dt_obito),
        _d(record.dt_encerramento),
    ]
    raw = "|".join(parts)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class EPIPersistence:
    """Handles persistence of validated EPI records to PostgreSQL"""
    
    def __init__(self, db_connection_string: str):
        """
        Initialize with database connection string.
        
        Args:
            db_connection_string: PostgreSQL connection string
                Example: "postgresql://user:pass@host:port/dbname"
        """
        self.conn_str = db_connection_string
    
    def insert_records(self, records: List[EPIRecordCSV], competencia: str, arquivo_origem: str) -> int:
        """
        Insert validated EPI records into indicador_epi table.
        
        Args:
            records: List of validated EPIRecordCSV objects
            competencia: Competência YYYYMM (e.g., "202401" for Jan/2024)
            arquivo_origem: Original filename for audit trail
            
        Returns:
            Number of records inserted
        """
        if not records:
            return 0
        
        comp_date = competencia_to_date(competencia)
        
        conn = psycopg2.connect(self.conn_str)
        try:
            with conn.cursor() as cur:
                # Prepare values for bulk insert
                values = []
                for record in records:
                    faixa_etaria = calcular_faixa_etaria(record.idade).value
                    dedup_key = build_dedup_key(record, comp_date)
                    
                    # Build tuple matching indicador_epi table columns
                    values.append((
                        comp_date,                            # competencia (PK part 1) - converted to date
                        record.municipio_cod_ibge,            # municipio_cod_ibge
                        record.dt_sintomas,                   # dt_sintomas
                        record.dt_notificacao,                # dt_notificacao
                        record.sexo,                          # sexo
                        record.idade,                         # idade
                        faixa_etaria,                         # faixa_etaria (calculated)
                        record.gestante,                      # gestante
                        record.classificacao_final,           # classificacao_final (already string)
                        record.criterio_confirmacao,          # criterio_confirmacao (already string)
                        record.febre,                         # febre
                        record.cefaleia,                      # cefaleia
                        record.dor_retroocular,               # dor_retroocular
                        record.mialgia,                       # mialgia
                        record.artralgia,                     # artralgia
                        record.exantema,                      # exantema
                        record.vomito,                        # vomito
                        record.nausea,                        # nausea
                        record.dor_abdominal,                 # dor_abdominal
                        record.plaquetas_baixas,              # plaquetas_baixas
                        record.hemorragia,                    # hemorragia
                        record.hepatomegalia,                 # hepatomegalia
                        record.acumulo_liquidos,              # acumulo_liquidos
                        record.diabetes,                      # diabetes
                        record.hipertensao,                   # hipertensao
                        record.evolucao,                      # evolucao (already string)
                        record.dt_obito,                      # dt_obito
                        record.dt_encerramento,               # dt_encerramento
                        arquivo_origem,                       # arquivo_origem
                        datetime.utcnow(),                    # dt_importacao
                        dedup_key                             # dedup_key
                    ))
                
                # Bulk insert with ON CONFLICT DO NOTHING (idempotent)
                insert_sql = """
                    INSERT INTO indicador_epi (
                        competencia, municipio_cod_ibge, dt_sintomas, dt_notificacao,
                        sexo, idade, faixa_etaria, gestante,
                        classificacao_final, criterio_confirmacao,
                        febre, cefaleia, dor_retroocular, mialgia, artralgia,
                        exantema, vomito, nausea, dor_abdominal,
                        plaquetas_baixas, hemorragia, hepatomegalia, acumulo_liquidos,
                        diabetes, hipertensao,
                        evolucao, dt_obito, dt_encerramento,
                        arquivo_origem, dt_importacao, dedup_key
                    ) VALUES %s
                    ON CONFLICT (competencia, dedup_key) DO NOTHING
                """
                
                execute_values(cur, insert_sql, values, page_size=1000)
                inserted_count = cur.rowcount
                conn.commit()
                
                return inserted_count
        finally:
            conn.close()
    
    def get_existing_competencias(self) -> List[str]:
        """Get list of competências already loaded in the database"""
        conn = psycopg2.connect(self.conn_str)
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT DISTINCT competencia FROM indicador_epi ORDER BY competencia DESC")
                return [row[0] for row in cur.fetchall()]
        finally:
            conn.close()
    
    def get_record_count(self, competencia: str) -> int:
        """Get count of records for a specific competência"""
        comp_date = competencia_to_date(competencia)
        conn = psycopg2.connect(self.conn_str)
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM indicador_epi WHERE competencia = %s", (comp_date,))
                return cur.fetchone()[0]
        finally:
            conn.close()

    def delete_competencia(self, competencia: str) -> int:
        """Delete all records for a specific competência (overwrite semantics)
        Returns number of rows deleted
        """
        comp_date = competencia_to_date(competencia)
        conn = psycopg2.connect(self.conn_str)
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM indicador_epi WHERE competencia = %s", (comp_date,))
                deleted = cur.rowcount
                conn.commit()
                return deleted
        finally:
            conn.close()
