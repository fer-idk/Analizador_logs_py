# Reflexión técnica: IA como herramienta, no como autor

**Actividad:** Desarrollo guiado y validado de un script en Python  
**Estudiante:** [Escribir nombre]  
**Fecha:** [Completar]  
**Estado:** Borrador orientativo que debe verificarse y personalizarse antes de su entrega.

## 1. Apoyo recibido de la inteligencia artificial

El proyecto se elaboró con asistencia de IA para estructurar el código en funciones, proponer una forma de detectar el encabezado de severidad y separar la validación de cada línea del resumen global. También se empleó como apoyo para escribir pruebas automatizadas, documentar los parámetros de consola y preparar el archivo README. Estas propuestas no sustituyen la responsabilidad de revisar el código y comprobar sus resultados.

Las funciones principales son `cargar_reglas()`, `validar_fecha()`, `analizar_linea()`, `analizar_archivo()` y `generar_resumen()`. Su separación permite identificar con claridad dónde ocurre cada comprobación y comprobarlas de forma independiente mediante pruebas.

## 2. Decisiones de validación que debe asumir el estudiante

El archivo `config/reglas.json` contiene dos decisiones explícitas: si una fecha es obligatoria y si las líneas vacías cuentan como eventos incorrectos. En la configuración preparada para pruebas, ambas opciones están activadas. La fecha se acepta únicamente con formato `AAAA-MM-DD` y si existe realmente en el calendario; el mensaje es obligatorio; únicamente se reconocen las severidades INFO, WARNING y ERROR.

**Antes de entregar, completar con una justificación propia y verificada:**

- ¿Por qué mantener o modificar la regla `fecha_obligatoria`? **[Escribir decisión y motivo]**.
- ¿Por qué contar o ignorar líneas vacías? **[Escribir decisión y motivo]**.
- ¿Qué caso borde revisó personalmente y cómo comprobó su comportamiento? **[Completar]**.

## 3. Ejemplo concreto de una propuesta técnica incompleta y su corrección

**Ejemplo reproducible para revisión:** una validación que utilice únicamente la expresión regular `^\d{4}-\d{2}-\d{2}$` verifica la estructura visual de una fecha, pero aceptaría `2025-02-30`, que no existe en el calendario. Para resolver esa limitación, el script combina la expresión regular con `datetime.strptime()`. El caso queda reflejado en `test_fecha_inexistente` y en `pruebas/log_con_errores.txt`; la ejecución registrada muestra la fecha como inválida.

**Importante:** este apartado demuestra una mejora técnica real del código, pero no prueba por sí solo que una IA haya sugerido primero esa expresión ni que el estudiante la haya corregido personalmente. Para cumplir con rigor el requisito de la actividad, **[sustituir o completar con una sugerencia real de IA que usted recibió, cómo detectó el problema y la modificación que hizo]**. Conserve, si está disponible, el prompt o la evidencia del cambio.

## 4. Pruebas y resultados

El archivo `log_bien_formado.txt` contiene seis eventos: se esperaban seis válidos y cero mal formados, y se obtuvieron exactamente esos valores. El archivo `log_con_errores.txt` contiene diez líneas con inconsistencias diversas: se esperaban tres eventos válidos y siete incorrectos, y se obtuvo el mismo resultado. Además, la suite de `unittest` ejecutó **14 pruebas y todas finalizaron correctamente**. Los reportes reales se encuentran en `evidencias/`.

El análisis de los resultados muestra por qué conviene probar no solo entradas ideales, sino también líneas incompletas, fechas imposibles y niveles desconocidos. El programa no se detiene al encontrar una línea defectuosa; la registra y continúa el análisis.

## 5. Aprendizaje sobre el uso responsable de la IA

Este ejercicio permite distinguir entre generar una propuesta de código y demostrar que funciona bajo reglas conocidas. Una sugerencia que parece correcta puede omitir situaciones importantes, como la diferencia entre el formato de una fecha y su validez real. Por eso, los criterios de aceptación deben poder explicarse, modificarse y verificarse mediante pruebas con resultados esperados definidos de antemano.

**Conclusión personal que debe añadir el estudiante:** **[Escribir qué revisó, qué aprendió y qué haría distinto la próxima vez al utilizar IA para programar]**.

---

*Documento preparado como base editable. No presentar los campos pendientes como experiencias realizadas.*
