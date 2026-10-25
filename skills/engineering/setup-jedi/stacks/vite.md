# Vite + React

## Create
Needs Node 20.19+ or 22.12+. The template ships Oxlint, which has a `complexity` rule.
```bash
pnpm create vite <name> --template react-ts --no-interactive
pnpm install
pnpm add -D vitest
```

## Tests
```bash
pnpm vitest run
```
Smoke test: `src/smoke.test.ts` with one passing test.

## Fast checks (run with lint)
```bash
pnpm lint
```
```json
// .oxlintrc.json, under rules
"complexity": ["error", { "max": 10 }]
```

## Slow checks (PR, listed in `quality.md`)
Same tools and reasons as `nextjs.md`, over `src`, with `pnpm build` (`tsc -b && vite build`).

## Camadas (text for `AGENTS.md`)
```
Componentes de tela → hooks/serviços → cliente de API. O próximo recurso copia esse trio.
```

## Suggest, do not install by default
`react-router`, `@tanstack/react-query`, `zod`, `react-hook-form` (só com formulários).

## Look up
vite.dev/guide, oxc.rs, vitest.dev
