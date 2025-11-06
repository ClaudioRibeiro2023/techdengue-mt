param(
  [string]$RepoRoot
)

if (-not $RepoRoot) {
  $RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot ".."))
}

$ShpDir = Join-Path $RepoRoot "dados-mt\IBGE\MT_Municipios_2024_shp_limites"
$SqlPath = Join-Path $RepoRoot "sql\transfer_shapefile.sql"

if (-not (Test-Path $ShpDir)) { Write-Error "Shapefile dir not found: $ShpDir"; exit 1 }
if (-not (Test-Path (Join-Path $ShpDir "MT_Municipios_2024.shp"))) { Write-Error "Shapefile not found: MT_Municipios_2024.shp"; exit 1 }
if (-not (Test-Path $SqlPath)) { Write-Error "SQL transfer file not found: $SqlPath"; exit 1 }

$PgConn = 'PG:host=db port=5432 user=techdengue password=techdengue dbname=techdengue'

# Pull image explicitly
$GdalImage = 'osgeo/gdal:latest'
Write-Host "Pulling $GdalImage..."
docker pull $GdalImage | Out-Null

# Import shapefile into temp table
Write-Host "Importing shapefile via GDAL/ogr2ogr..."
docker run --rm --network infra_default -v "${ShpDir}:/data" $GdalImage ogr2ogr -f PostgreSQL "$PgConn" -nln temp_shapefile_mt -nlt MULTIPOLYGON -overwrite -t_srs EPSG:4326 -s_srs EPSG:4674 /data/MT_Municipios_2024.shp
if ($LASTEXITCODE -ne 0) { Write-Error "ogr2ogr import failed"; exit 1 }

# Copy transfer SQL into DB container
Write-Host "Copying transfer SQL to db container..."
docker cp "$SqlPath" infra-db-1:/tmp/transfer_shapefile.sql
if ($LASTEXITCODE -ne 0) { Write-Error "docker cp failed"; exit 1 }

# Apply transfer SQL
Write-Host "Applying transfer SQL..."
docker exec -i infra-db-1 psql -U techdengue -d techdengue -v ON_ERROR_STOP=1 -f /tmp/transfer_shapefile.sql
if ($LASTEXITCODE -ne 0) { Write-Error "psql apply failed"; exit 1 }

Write-Host "Shapefile import completed."
