<!-- setup-jedi: testing v1 -->
# Testes

Um modelo por camada; use o menor que prova o AC.

| Camada | Modelo |
|---|---|
| Regra de negócio (services) | Unitário com stub; sem IO. |
| Rota + banco | Contrato HTTP e restrições do banco (índice único etc.) por integração. |
| Repositório | Sem suíte própria; é coberto pela integração. |
| Tela | Sem teste automatizado; valide no browser-harness. |

Comando da suíte: `<comando com paralelismo>`. Armadilhas da stack: `<preencher ao descobrir>`.
<!-- /setup-jedi -->
