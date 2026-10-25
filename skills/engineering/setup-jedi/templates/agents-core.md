<!-- setup-jedi: core v1 -->
# <Projeto>
<uma linha de escopo>. Vocabulário: <arquivo do glossário>; termos em pt-BR, código em inglês.

## Ao implementar
Prefira o simples (KISS): sem abstração para um uso só, funções pequenas e com uma responsabilidade, pouca repetição, módulos que dependem uns dos outros só no sentido das camadas. Atente-se à complexidade: se está difícil de ler, simplifique antes de seguir. Decida e siga, sem pedir confirmação do que é reversível.

## Camadas
<bloco Camadas da stack>

## Testes
- Só no seam do spec; poucos por AC, cada um ligado a um AC.
- Visual: valide no browser-harness (é um teste de confirmação, feito visualmente).
- Suíte completa uma vez, no fim: `<comando com paralelismo>`.
<!-- /setup-jedi -->
