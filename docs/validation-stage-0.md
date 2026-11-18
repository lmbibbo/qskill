# Validación de la etapa 0

> Change: `skill-foundation` · Fecha de la última corrida: 2026-11-17 · Resultado: 17/17 PASS
> Esta es la checklist para reproducir la validación en una sesión nueva.

## 0. Preparar la sesión

`uv` está instalado con `pip --user`, así que no está en el PATH por defecto.

```powershell
$env:PATH += ";C:\Users\palob\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0\LocalCache\local-packages\Python312\Scripts"
uv --version    # esperado: uv 0.13.x
```

Si prefieres no repetirlo cada vez, añade esa carpeta al PATH de usuario en
*Variables de entorno* (requiere reabrir la terminal).

```powershell
uv sync --all-extras
```

## 1. Validación rápida

```powershell
uv run python scripts/skill_lint.py
uv run python scripts/run_snippets.py
uv run python evals/run.py --list
openspec validate skill-foundation
```

| Comando | Esperado |
|---|---|
| `skill_lint.py` | `Summary: 6 skills, 0 errors, 15 warnings`, exit **0** |
| `run_snippets.py` | `Summary: 0 blocks, ...`, exit **0** |
| `evals/run.py --list` | `0 cases found`, exit **0** |
| `openspec validate` | `Change 'skill-foundation' is valid` |

Los 15 warnings son colisiones de trigger entre las skills `openspec-*` y están
documentadas como excepción conocida en `docs/conventions.md`.

## 2. Validación completa (fixtures)

Cada fixture prueba un camino de fallo. Si un check deja de fallar, la
herramienta está rota.

| Comando | Exit esperado |
|---|---|
| `uv run python scripts/skill_lint.py evals/fixtures/lint/bad-frontmatter` | 1 |
| `uv run python scripts/skill_lint.py evals/fixtures/lint/bad-links` | 1 |
| `uv run python scripts/skill_lint.py evals/fixtures/lint/oversized` | 1 |
| `uv run python scripts/skill_lint.py evals/fixtures/lint/bad-name` | 1 |
| `uv run python scripts/skill_lint.py evals/fixtures/lint/collision` | 0 + warning |
| `uv run python scripts/run_snippets.py evals/fixtures/snippets/broken` | 1 |
| `uv run python scripts/run_snippets.py evals/fixtures/snippets/skip` | 0 |
| `uv run python evals/run.py --cases evals/fixtures/evals/pass` | 0 |
| `uv run python evals/run.py --cases evals/fixtures/evals/fail` | 1 |

### Scaffolder

```powershell
uv run python scripts/new_skill.py demo                    # 0, crea 3 archivos
uv run python scripts/skill_lint.py .agents/skills/demo     # 0
uv run python scripts/new_skill.py demo                     # 1, no sobrescribe
uv run python scripts/new_skill.py Bad_ID                   # 2, ID inválido
Remove-Item -Recurse -Force .agents\skills\demo             # limpiar
```

## 3. Corrida automática (todo de una vez)

Pega esto en PowerShell desde la raíz del repo. Imprime PASS/FAIL por prueba y
limpia el `demo` al final.

```powershell
$env:PATH += ";C:\Users\palob\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0\LocalCache\local-packages\Python312\Scripts"
$results = New-Object System.Collections.ArrayList
function T($name, $expected, [scriptblock]$block) {
  & $block *> $null
  $code = $LASTEXITCODE
  $state = if ($code -eq $expected) { "PASS" } else { "FAIL" }
  [void]$results.Add(("{0}  {1}  (esperado {2}, obtenido {3})" -f $state, $name, $expected, $code))
}
T "openspec validate" 0 { openspec validate "skill-foundation" }
T "lint .agents/skills" 0 { uv run python scripts/skill_lint.py }
T "lint bad-frontmatter" 1 { uv run python scripts/skill_lint.py evals/fixtures/lint/bad-frontmatter }
T "lint bad-links" 1 { uv run python scripts/skill_lint.py evals/fixtures/lint/bad-links }
T "lint oversized" 1 { uv run python scripts/skill_lint.py evals/fixtures/lint/oversized }
T "lint bad-name" 1 { uv run python scripts/skill_lint.py evals/fixtures/lint/bad-name }
T "lint collision (solo warning)" 0 { uv run python scripts/skill_lint.py evals/fixtures/lint/collision }
T "snippets broken" 1 { uv run python scripts/run_snippets.py evals/fixtures/snippets/broken }
T "snippets skip" 0 { uv run python scripts/run_snippets.py evals/fixtures/snippets/skip }
T "snippets .agents/skills" 0 { uv run python scripts/run_snippets.py }
T "evals --list (0 casos)" 0 { uv run python evals/run.py --list }
T "evals fixture pass" 0 { uv run python evals/run.py --cases evals/fixtures/evals/pass }
T "evals fixture fail" 1 { uv run python evals/run.py --cases evals/fixtures/evals/fail }
T "scaffold demo" 0 { uv run python scripts/new_skill.py demo }
T "lint demo" 0 { uv run python scripts/skill_lint.py .agents/skills/demo }
T "scaffold duplicado" 1 { uv run python scripts/new_skill.py demo }
T "scaffold ID invalido" 2 { uv run python scripts/new_skill.py Bad_ID }
Remove-Item -Recurse -Force .agents\skills\demo -ErrorAction SilentlyContinue
$results
```

## 4. Revisión humana

1. Sigue `README.md` §"Add a skill" como si no conocieras el repo.
2. Compara la tabla de reglas de `docs/conventions.md` con la salida del linter:
   deben coincidir una a una.
3. Abre `docs/skill-template/SKILL.md` y confirma que la description placeholder
   es claramente reemplazable.
4. Revisa `evals/schema.md` pensando en los casos de la etapa 1 (Bell state,
   VQE, Grover): ¿el formato alcanza?
5. Rompe algo a mano en una **copia** de un skill (descripción de 30 caracteres,
   link a `references/nada.md`) y comprueba que el linter falla.

## 5. Estado de OpenSpec

```powershell
openspec status --change skill-foundation
openspec instructions apply --change skill-foundation --json
```

Esperado: `4/4 artifacts complete`, `progress 25/25`, `state all_done`.

## 6. Registro de la corrida

Marca lo que pase y anota lo que falle:

- [ ] `uv sync --all-extras` sin errores
- [ ] validación rápida §1 (4 comandos)
- [ ] fixtures de lint (5 comandos)
- [ ] fixtures de snippets (2 comandos)
- [ ] fixtures de evals (2 comandos)
- [ ] scaffolder (5 comandos)
- [ ] `openspec validate` y `status`
- [ ] revisión humana §4

### Si algo falla

| Síntoma | Causa probable / qué hacer |
|---|---|
| `uv: command not found` | falta el PATH del paso 0 |
| `ModuleNotFoundError: yaml` | falta `uv sync --all-extras` (o al menos `--extra dev`) |
| lint sale 0 donde se esperaba 1 | una regla del linter quedó desactivada; comparar con `docs/conventions.md` |
| warnings de `trigger-collision` | esperado en las skills `openspec-*` |
| `demo` aparece como skill disponible | normal mientras exista; se elimina al final del script |

## 7. Criterio de cierre

La etapa 0 se considera validada si:

- [ ] las 17 comprobaciones automáticas pasan,
- [ ] `openspec validate skill-foundation` es `valid`,
- [ ] estás de acuerdo con las reglas de `docs/conventions.md` (son el contrato
      de todas las skills futuras),
- [ ] el README permite crear un skill sin ayuda.

Con eso, el siguiente paso es archivar el change (`openspec-archive-change`) y
proponer la etapa 1 (`core-quantum-skills`).
