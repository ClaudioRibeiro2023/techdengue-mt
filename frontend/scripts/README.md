# Frontend Scripts

Scripts utilitários para o frontend.

## generate-pwa-icons-simple.py

Gera os ícones PWA (192x192 e 512x512) a partir de código Python usando Pillow.

### Uso

```bash
pip install pillow
python scripts/generate-pwa-icons-simple.py
```

### Saída

- `public/pwa-192x192.png` - Ícone 192x192 para PWA
- `public/pwa-512x512.png` - Ícone 512x512 para PWA (maskable)

Os ícones são gerados com:
- Fundo azul (#0ea5e9)
- Representação abstrata de mosquito (círculos + linhas)
- Texto "TechDengue" na parte inferior

### Customização

Se desejar ícones personalizados:

1. **Opção 1**: Edite `public/pwa-icon.svg` e use um conversor online (ex: https://cloudconvert.com/svg-to-png)

2. **Opção 2**: Substitua diretamente os arquivos PNG em `public/`:
   - pwa-192x192.png
   - pwa-512x512.png

3. **Opção 3**: Edite o script Python `generate-pwa-icons-simple.py` para alterar cores, formas, etc.

## Ícones atuais

Os ícones PWA já foram gerados e estão prontos para uso:

```
frontend/public/
├── pwa-192x192.png  ✓
├── pwa-512x512.png  ✓
└── manifest.webmanifest  ✓
```

O manifest já está configurado e linkado no `index.html`.
