# Laboratorio de Estándares de Codificación — Python (Sección A)

**Software Engineering II · ESPOL – FIEC · 2026**

Sistema de gestión de calificaciones de estudiantes (*Student Grade Management System*).
Partiendo de un código base defectuoso a propósito, se usó **Pylint** para detectar
las violaciones a los estándares de codificación y se reescribió el programa para que
cumpla buenas prácticas y **todos** los requisitos funcionales del taller.

| | Código base (`test.py`) | Código final |
|---|---|---|
| Calificación Pylint | **0.91 / 10** | **10.00 / 10** |
| Errores (E) | 3 | 0 |
| Advertencias (W) | 2 | 0 |
| Convenciones (C) | 13 | 0 |
| Flake8 (PEP 8) | 1 aviso | 0 avisos |
| ¿Se ejecuta? | No (`TypeError`) | Sí, sin fallos |
| Pruebas unitarias | — | 19 / 19 pasan |

Reportes HTML: [`reports/initial_report.html`](reports/initial_report.html) ·
[`reports/final_report.html`](reports/final_report.html)

---

## Estructura del repositorio

```
.
├── .github/workflows/pylint.yml   # Challenge: Pylint en cada pull request a main
├── reports/
│   ├── initial_report.html        # Reporte inicial (código base)
│   ├── initial_report.json
│   ├── final_report.html          # Reporte final (código corregido)
│   └── final_report.json
├── student_grades.py              # Código final
├── test_student_grades.py         # Pruebas unitarias (unittest)
├── requirements-dev.txt           # Versiones fijas de las herramientas
├── .gitignore
└── README.md
```

El código base original (`test.py`) está en el primer commit del historial.

## Requisitos

- Python 3.10 o superior
- Visual Studio Code con las extensiones **Python** y **Pylint** (`ms-python.pylint`)

## Cómo usarlo

```bash
# Ejecutar la demostración (cubre todos los requisitos, incluidos los errores)
python student_grades.py

# Ejecutar las pruebas unitarias
python -m unittest -v

# Instalar las herramientas de análisis
python -m pip install -r requirements-dev.txt

# Analizar el código con Pylint
python -m pylint student_grades.py test_student_grades.py

# Generar el reporte HTML (JSON de Pylint -> HTML)
python -m pylint --load-plugins=pylint_json2html --output-format=jsonextended --output=reports/final_report.json student_grades.py test_student_grades.py
pylint-json2html -f jsonextended -o reports/final_report.html reports/final_report.json
```

## Herramienta elegida: Pylint

- Es el analizador más completo para Python: detecta **errores reales** (atributos o
  métodos inexistentes, argumentos mal declarados), **advertencias** (variables sin
  usar, *built-ins* sobrescritos) y **convenciones PEP 8** (nombres, docstrings).
- Da una **calificación de 0 a 10**, lo que permite medir el avance entre iteraciones.
- Se integra en VS Code (extensión oficial `ms-python.pylint`) y marca los problemas
  en el panel *Problems* mientras se escribe.
- Exporta a JSON, que se convierte a **HTML** con `pylint-json2html`.
- Corre igual en local y en GitHub Actions, sin servidor externo.

Además se usó **Flake8** como segunda verificación de estilo PEP 8 (0 avisos al final).

## Problemas detectados en el código base y cómo se corrigieron

| Código Pylint | Problema | Corrección |
|---|---|---|
| E0213 `no-self-argument` | `__init__(s, id, name)` usaba `s` en vez de `self` | Se usa `self` |
| E1101 `no-member` | `checkHonor` llamaba a `calcAverage` (no existe) | Se unificó en `calculate_average()` |
| E1101 `no-member` | `report` usaba `self.letter` (nunca se definió) | Propiedad `letter_grade` calculada |
| W0622 `redefined-builtin` | El parámetro `id` sobrescribía la función `id()` | Renombrado a `student_id` |
| W0612 `unused-variable` | `avg` se calculaba y nunca se devolvía | `calculate_average()` devuelve el promedio |
| C0103 `invalid-name` (×5) | `student`, `isPassed`, `addGrades`, `checkHonor`, `deleteGrade` | `Student` (PascalCase) y `snake_case` en métodos y atributos |
| C0114/C0115/C0116 (×8) | Faltaban docstrings de módulo, clase y funciones | Docstrings en todo el código |

### Buenas prácticas que la herramienta no detecta (revisión manual)

| Problema en el código base | Corrección |
|---|---|
| `avg = t / 0` → división por cero | Promedio = suma / cantidad, y 0.0 si no hay notas |
| `"Fifty"` se aceptaba como nota → `TypeError` | Validación: solo números (no `bool`, no `NaN`) entre 0 y 100 |
| `"Grades Count: " + len(...)` → `TypeError` | Reporte con *f-strings* y formato alineado |
| `deleteGrade(5)` → `IndexError` | Eliminación por índice y por valor con errores controlados |
| Nombre vacío `""` aceptado | Validación de nombre e ID no vacíos |
| `honor = "?"` / `"yep"` y `isPassed = "NO"` como texto | `is_honor_roll` y `has_passed` son **booleanos** calculados |
| Números mágicos (`90`, …) | Constantes: `PASSING_AVERAGE`, `HONOR_ROLL_AVERAGE`, `LETTER_GRADE_THRESHOLDS` |
| Lista de notas pública y modificable | `_grades` privada; `grades` devuelve una tupla de solo lectura |
| `print` mezclado con la lógica | Lógica en `Student`; mensajes en una capa de presentación aparte |
| El programa se cerraba con cualquier error | Excepciones propias (`InvalidInputError`, `GradeNotFoundError`) capturadas en `main()` |
| `startrun()` se ejecutaba al importar | `if __name__ == "__main__": main()` |
| `gradez`, `t`, `x`, `a`, `g` | Nombres descriptivos |

## Requisitos funcionales

| # | Requisito | Implementación |
|---|---|---|
| 1 | Crear estudiantes con nombre e ID | `Student(student_id, name)` |
| 2 | Varias notas numéricas en 0–100 | `add_grade()` + `validate_grade()` |
| 3 | Promedio | `calculate_average()` |
| 4 | Letra A/B/C/D/F | `letter_grade` / `letter_for_average()` |
| 5 | Passed / Failed (≥ 60) | `has_passed` y `pass_status` |
| 6 | Validar entradas sin que el sistema se caiga | `validate_text()`, `validate_grade()` y mensajes `[ERROR]` |
| 7 | Cuadro de honor (≥ 90) como booleano | `is_honor_roll` → `True` / `False` |
| 8 | Eliminar nota por valor o por índice | `remove_grade_by_value()` y `remove_grade_by_index()` |
| 9 | Reporte resumen por estudiante | `summary_report()` |

Cada requisito tiene pruebas en `test_student_grades.py` (incluye los límites 59.99/60,
89.99/90, etc.).

## Challenge: GitHub Actions

El workflow [`.github/workflows/pylint.yml`](.github/workflows/pylint.yml) se ejecuta en
**cada pull request hacia `main`** (y también a mano con *Run workflow*):

1. Instala Python 3.12 y las herramientas de `requirements-dev.txt`.
2. Corre Pylint sobre todos los archivos `.py`; si hay **cualquier** problema, el check falla.
3. Genera el reporte HTML y lo sube como artefacto `pylint-report`.
4. Ejecuta las pruebas unitarias.

## Nota sobre el código base

El código del PDF, copiado literalmente, tiene la indentación rota: Python no puede
interpretarlo (`IndentationError`) y Pylint solo reporta `E0001 syntax-error`, sin
analizar nada más. Por eso el primer commit (`test.py`) contiene el código base con
**únicamente la indentación corregida**; todo lo demás está tal como se entregó.

## Autor

- **Nombre:** _Jeremy Lopez_
- **Repositorio:** _https://github.com/jeremylopezarteaga04-pixel/Workshop-Coding-Standards_
