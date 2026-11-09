# Analizador de logs en Python

**Actividad:** IA como Herramienta, no como Autor: Desarrollo Guiado y Validado de un Script en Python.

Proyecto de consola que lee un archivo de registros (`.txt` o `.log`), identifica niveles de severidad, comprueba la validez de las fechas y detecta líneas mal formateadas o incompletas. Está construido con **Python y su biblioteca estándar**, sin instalaciones adicionales.

> **Nota académica:** El código y esta documentación fueron preparados con asistencia de IA. Antes de entregar, el estudiante debe ejecutar las pruebas, revisar las reglas de `config/reglas.json`, confirmar que está de acuerdo con ellas y adaptar la reflexión técnica a su experiencia real. No se deben atribuir a una persona decisiones o correcciones que no realizó.

## 1. Estructura del repositorio

```text
analizador-logs-python/
├── analizador_logs.py               # Script principal
├── config/
│   └── reglas.json                  # Decisiones configurables de validación
├── pruebas/
│   ├── log_bien_formado.txt         # Caso correcto
│   └── log_con_errores.txt          # Caso con inconsistencias
├── tests/
│   ├── __init__.py
│   └── test_analizador_logs.py      # 14 pruebas unitarias
├── evidencias/
│   ├── salida_log_bien_formado.txt  # Ejecución real de un caso correcto
│   ├── salida_log_con_errores.txt   # Ejecución real de un caso incorrecto
│   └── pruebas_unitarias.txt        # Resultado real de 14 pruebas
├── documentacion/
│   ├── REFLEXION_TECNICA_BORRADOR.md
│   └── REFLEXION_TECNICA_BORRADOR.pdf
├── .gitignore
└── README.md
```

## 2. Requisitos

- Python **3.10 o superior**.
- Una terminal (PowerShell, CMD, Bash) y, opcionalmente, VS Code.
- No se requiere `pip install` ni bibliotecas externas.

## 3. Cómo ejecutar el programa

Abra la terminal en la carpeta principal del proyecto y escriba:

```powershell
python analizador_logs.py
```

El programa preguntará qué archivo desea analizar. Por ejemplo:

```text
Escriba la ruta del archivo que desea analizar: pruebas/log_bien_formado.txt
```

También puede indicar el archivo directamente, sin pregunta interactiva:

```powershell
python analizador_logs.py --archivo pruebas/log_bien_formado.txt
python analizador_logs.py --archivo pruebas/log_con_errores.txt --detalles
```

**En Windows:** si `python` no está disponible, pruebe `py`. **En macOS o Linux:** puede necesitar `python3`.

Para consultar los parámetros:

```powershell
python analizador_logs.py --help
```

Para analizar un archivo externo, utilice la ruta completa entre comillas:

```powershell
python analizador_logs.py --archivo "C:\Users\Usuario\Downloads\mi_log.txt" --detalles
```

## 4. Reglas de validación propuestas (revisar antes de entregar)

Las reglas explícitas se encuentran en `config/reglas.json`:

```json
{
  "fecha_obligatoria": true,
  "contar_lineas_vacias": true
}
```

| Regla | Comportamiento predeterminado | Qué puede cambiar el estudiante |
|---|---|---|
| `fecha_obligatoria` | `true`: una línea sin fecha se considera incompleta. | `false`: un mensaje sin fecha se acepta si tiene severidad y mensaje válidos. |
| `contar_lineas_vacias` | `true`: cada línea vacía se cuenta como evento mal formado. | `false`: se omite y se informa en «Líneas vacías ignoradas». |

**Otras reglas visibles en el código:**

1. Solo se reconocen `INFO`, `WARNING` y `ERROR`, escritos en mayúsculas y encerrados en corchetes, al inicio de la línea.
2. La fecha debe aparecer inmediatamente después de la severidad, con formato exacto `AAAA-MM-DD`, y corresponder a un día real del calendario.
3. El mensaje no puede quedar vacío, incluso cuando la severidad y la fecha son válidas.
4. Las líneas con problemas **se cuentan**, no detienen el programa. Cuando se reconoce una severidad, cuenta en su categoría aunque la línea tenga otros errores.
5. El total incluye todos los eventos analizados. Si se activó la opción de omitir líneas vacías, estas no forman parte del total y se informan aparte.
6. Una fecha ausente y una fecha inválida no son lo mismo: con `fecha_obligatoria=false`, la primera puede aceptarse; la segunda siempre genera error.
7. Una línea puede tener **varios motivos de error**, pero cuenta **una sola vez** como línea mal formada.

Los niveles son fijos por requisito de la actividad; las dos decisiones configurables se dejan expresamente a revisión del estudiante. El código maneja fechas imposibles, años bisiestos, registros vacíos, severidades desconocidas, mensajes faltantes y rutas inexistentes. **No intenta** interpretar múltiples formatos de fecha, niveles adicionales, archivos binarios ni logs multilínea.

## 5. Formato esperado de los logs

```text
[INFO] 2025-01-10 Usuario inició sesión
[WARNING] 2025-01-10 Intento de acceso fallido
[ERROR] 2025-01-10 Error de conexión
```

La validación de una fecha no utiliza solo una expresión regular; también utiliza `datetime.strptime()` para impedir que fechas aparentemente bien escritas, como `2025-02-30`, sean aceptadas.

## 6. Evidencias de las pruebas

Se ejecutaron ambos archivos de prueba con la configuración predeterminada.

| Comprobación | Esperado | Obtenido | Estado |
|---|---:|---:|---|
| Archivo correcto: total | 6 | 6 | Correcto |
| Archivo correcto: válidos | 6 | 6 | Correcto |
| Archivo correcto: mal formados | 0 | 0 | Correcto |
| Archivo con errores: total | 10 | 10 | Correcto |
| Archivo con errores: válidos | 3 | 3 | Correcto |
| Archivo con errores: mal formados | 7 | 7 | Correcto |

**Distribución por severidad:**

| Archivo | INFO | WARNING | ERROR | Sin nivel reconocido |
|---|---:|---:|---:|---:|
| Correcto | 3 | 2 | 1 | 0 |
| Con errores | 2 | 2 | 3 | 3 |

**Fechas detectadas:**

| Archivo | Válidas | Inválidas | Ausentes |
|---|---:|---:|---:|
| Correcto | 6 | 0 | 0 |
| Con errores | 5 | 2 | 3 |

En el archivo con errores se incluyeron los siguientes casos: fecha imposible (`2025-02-30`), fecha ausente, severidad `[DEBUG]`, mensaje vacío, encabezado incorrecto, línea vacía y fecha con separadores `/`. También se incluyó `2024-02-29` como fecha válida de un año bisiesto.

Los **resultados reales de consola** están en `evidencias/salida_log_bien_formado.txt` y `evidencias/salida_log_con_errores.txt`.

## 7. Ejecutar las pruebas automatizadas

```powershell
python -m unittest discover -s tests -v
```

**Resultado verificado al preparar este repositorio:** 14 pruebas ejecutadas, 14 correctas (`OK`). Puede consultar la salida original en `evidencias/pruebas_unitarias.txt`.

Las pruebas cubren las fechas válidas y erróneas, los años bisiestos, la fecha opcional, la ausencia de mensajes, severidades desconocidas, el archivo vacío, el filtrado de líneas en blanco, errores de configuración y los resultados completos de ambos archivos de ejemplo.

## 8. Reflexión técnica

Se incluye el documento `documentacion/REFLEXION_TECNICA_BORRADOR.pdf` y su versión editable `.md`. Es un **borrador**, no una declaración automática sobre el trabajo realizado personalmente por el estudiante. Se deben confirmar las decisiones, reproducir el ejemplo de mejora técnica y completar los campos señalados antes de presentar la reflexión como propia.

## 9. Cómo subir a GitHub

En la terminal, dentro de la carpeta del proyecto:

```powershell
git init
git add .
git commit -m "feat: crear analizador de logs con pruebas y documentacion"
git branch -M main
```

Cree un repositorio **vacío** en GitHub y conecte la dirección que GitHub le proporcione:

```powershell
git remote add origin https://github.com/USUARIO/NOMBRE-REPOSITORIO.git
git push -u origin main
```

Reemplace `USUARIO` y `NOMBRE-REPOSITORIO` por los datos reales. Si el repositorio ya existe, revise su configuración antes de ejecutar `git init` y `git remote add`.

---

**Alcance:** herramienta académica de línea de comandos para archivos de texto UTF-8. No envía archivos a internet y no requiere cuentas ni servicios externos para ejecutar el análisis.
