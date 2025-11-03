// Validação automática da árvore de menus
const fs = require('fs');
const path = require('path');

// Ler o arquivo map.ts
const mapPath = path.join(__dirname, 'src', 'navigation', 'map.ts');
const content = fs.readFileSync(mapPath, 'utf-8');

// Contadores
let stats = {
  modules: 0,
  functions: 0,
  groups: {},
  categories: {},
  badges: {},
  icons: new Set(),
  queryParams: 0,
  errors: [],
};

// Parse de funções
const functionMatches = content.matchAll(/\{\s*id:\s*['"]([^'"]+)['"],\s*name:\s*['"]([^'"]+)['"],\s*path:\s*['"]([^'"]+)['"],\s*category:\s*['"]([^'"]+)['"],\s*icon:\s*['"]([^'"]+)['"]/g);

for (const match of functionMatches) {
  const [, id, name, path, category, icon] = match;
  stats.functions++;
  
  // Categoria
  stats.categories[category] = (stats.categories[category] || 0) + 1;
  
  // Ícone
  stats.icons.add(icon);
  
  // Query param
  if (path.includes('?')) {
    stats.queryParams++;
  }
}

// Parse de grupos (apenas em módulos)
const groupMatches = content.matchAll(/group:\s*['"]([^'"]+)['"]/g);
for (const match of groupMatches) {
  const group = match[1];
  stats.groups[group] = (stats.groups[group] || 0) + 1;
}
// Total de módulos = soma dos grupos
stats.modules = Object.values(stats.groups).reduce((a, b) => a + b, 0);

// Parse de badges
const badgeMatches = content.matchAll(/badge:\s*['"]([^'"]+)['"]/g);
for (const match of badgeMatches) {
  const badge = match[1];
  stats.badges[badge] = (stats.badges[badge] || 0) + 1;
}

// Relatório
console.log('\n═══════════════════════════════════════════════════════════');
console.log('🎯 VALIDAÇÃO AUTOMÁTICA DA ÁRVORE DE MENUS');
console.log('═══════════════════════════════════════════════════════════\n');

console.log('📊 ESTATÍSTICAS GERAIS');
console.log('─────────────────────────────────────────────────────────────');
console.log(`✅ Total de Módulos: ${stats.modules}`);
console.log(`✅ Total de Funções: ${stats.functions}`);
console.log(`✅ Ícones únicos: ${stats.icons.size}`);
console.log(`✅ Funções com query params: ${stats.queryParams}`);

console.log('\n📂 DISTRIBUIÇÃO POR GRUPO');
console.log('─────────────────────────────────────────────────────────────');
Object.entries(stats.groups)
  .sort((a, b) => b[1] - a[1])
  .forEach(([group, count]) => {
    console.log(`  ${group.padEnd(20)} → ${count} módulo(s)`);
  });

console.log('\n🏷️  DISTRIBUIÇÃO POR CATEGORIA');
console.log('─────────────────────────────────────────────────────────────');
const total = stats.functions;
Object.entries(stats.categories)
  .sort((a, b) => b[1] - a[1])
  .forEach(([cat, count]) => {
    const pct = ((count / total) * 100).toFixed(1);
    console.log(`  ${cat.padEnd(15)} → ${String(count).padStart(2)} funções (${pct}%)`);
  });

console.log('\n🎖️  BADGES ENCONTRADOS');
console.log('─────────────────────────────────────────────────────────────');
if (Object.keys(stats.badges).length === 0) {
  // Buscar badges manualmente
  const betaMatch = content.match(/badge:\s*['"]BETA['"]/);
  const iaMatch = content.match(/badge:\s*['"]IA['"]/);
  const devMatch = content.match(/badge:\s*['"]DEV['"]/);
  
  if (betaMatch) console.log('  ✅ BETA   → ETL & Integração');
  if (iaMatch) console.log('  ✅ IA     → Previsão & Simulação');
  if (devMatch) console.log('  ✅ DEV    → Observabilidade');
} else {
  Object.entries(stats.badges).forEach(([badge, count]) => {
    console.log(`  ✅ ${badge.padEnd(6)} → ${count} módulo(s)`);
  });
}

console.log('\n✅ VALIDAÇÕES');
console.log('─────────────────────────────────────────────────────────────');

// Validar grupos (esperados por especificação)
const expectedGroups = ['Web Mapas', 'Painéis', 'Vigilância', 'Operações', 'Sistema'];
const foundGroups = Object.keys(stats.groups);
const missingGroups = expectedGroups.filter(g => !foundGroups.includes(g));
const extraGroups = foundGroups.filter(g => !expectedGroups.includes(g));

if (missingGroups.length === 0 && extraGroups.length === 0) {
  console.log('  ✅ Grupos corretos (5)');
} else {
  if (missingGroups.length > 0) {
    console.log(`  ❌ Grupos faltando: ${missingGroups.join(', ')}`);
    stats.errors.push(`Grupos faltando: ${missingGroups.join(', ')}`);
  }
  if (extraGroups.length > 0) {
    console.log(`  ⚠️  Grupos extras: ${extraGroups.join(', ')}`);
  }
}

// Validar categorias (esperadas por especificação)
const expectedCategories = ['ANALISE', 'MAPEAMENTO', 'INDICADORES', 'CONTROLE', 'OPERACIONAL'];
const foundCategories = Object.keys(stats.categories);
const missingCategories = expectedCategories.filter(c => !foundCategories.includes(c));

if (missingCategories.length === 0) {
  console.log('  ✅ Categorias corretas (5)');
} else {
  console.log(`  ❌ Categorias faltando: ${missingCategories.join(', ')}`);
  stats.errors.push(`Categorias faltando: ${missingCategories.join(', ')}`);
}

console.log('\n═══════════════════════════════════════════════════════════');

if (stats.errors.length === 0) {
  console.log('✅ VALIDAÇÃO COMPLETA - NENHUM ERRO ENCONTRADO');
  console.log('═══════════════════════════════════════════════════════════\n');
  process.exit(0);
} else {
  console.log('❌ VALIDAÇÃO COMPLETA - ERROS ENCONTRADOS:');
  stats.errors.forEach((err, i) => console.log(`   ${i + 1}. ${err}`));
  console.log('═══════════════════════════════════════════════════════════\n');
  process.exit(1);
}
