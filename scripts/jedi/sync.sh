#!/usr/bin/env bash
# Copia os scripts canônicos (scripts/jedi/*.py) para dentro de cada skill que os usa.
# Motivo: o instalador (npx skills) só leva a pasta da skill; scripts na raiz do repo não chegam ao usuário.
# Edite SEMPRE em scripts/jedi/ e rode este script antes de commitar.
set -e
cd "$(dirname "$0")/../.."
E=skills/engineering
put() { # put <script> <skill>...
  s=$1; shift
  for k in "$@"; do mkdir -p "$E/$k/scripts"; cp "scripts/jedi/$s" "$E/$k/scripts/$s"; done
}
put check_spec.py    to-spec to-tickets finish-spec
put check_tickets.py implement finish-spec
put context_gate.py  implement
echo "scripts copiados"
