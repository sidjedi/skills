# Next.js (pnpm)

## Create
Creation can take minutes. Skip `--reset-preferences`: it prompts. `create-next-app` writes its own `AGENTS.md` block (`nextjs-agent-rules`); keep it and add the template around it.
Biome is one tool for lint and format, with a cognitive-complexity rule built in; `vitest` runs TypeScript with no extra setup.
```bash
pnpm create next-app <name> --ts --app --biome --tailwind --use-pnpm --yes --disable-git
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
// biome.json, under linter.rules
"complexity": { "noExcessiveCognitiveComplexity": { "level": "error", "options": { "maxAllowedComplexity": 15 } } }
```

## Slow checks (PR, listed in `quality.md`)
`dependency-cruiser` turns the layer order into a failing check. Write `.dependency-cruiser.cjs` with `forbidden` rules (`from.path`, `to.path`) by hand; `--init` is interactive. `jscpd` finds copy-paste.
```bash
pnpm add -D dependency-cruiser
pnpm depcruise app src
pnpm dlx jscpd app src --min-lines 8 --threshold 3
pnpm build
```

## Camadas (text for `AGENTS.md`)
```
Caminho de uma requisição: route handler / server action → services → repositories. O próximo recurso copia esse trio.
```

## Suggest, do not install by default
`zod` (validação), `drizzle-orm` + `drizzle-kit` ou `prisma` (banco), `@tanstack/react-query` (dados no cliente), `better-auth` (login).

## Look up
nextjs.org/docs, biomejs.dev, vitest.dev. Docs of the installed version: `node_modules/next/dist/docs/`.
