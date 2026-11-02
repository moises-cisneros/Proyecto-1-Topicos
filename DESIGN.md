# Especificación de Diseño y Sistema de Componentes (DESIGN.md)

## 1. Propósito y Usuarios Objetivo

"Buzón Seguro SMS" (SMS Sentinel) es una plataforma de ciberseguridad diseñada para que usuarios comunes y analistas verifiquen la autenticidad de mensajes de texto en español, identifiquen vectores de estafa bancaria y comprendan la trazabilidad lingüística que realiza el pipeline de Procesamiento de Lenguaje Natural (NLP) y Machine Learning.

---

## 2. Directivas de Estilo

Por definición arquitectónica y de rendimiento visual:

* **PROHIBICIÓN TOTAL DE DEGRADADOS:** Todos los fondos, bordes y superficies deben ser colores planos y sólidos (`solid colors`). No se permite el uso de `bg-gradient-*`, reflejos o difuminados.
* **PROHIBICIÓN TOTAL DE ANIMACIONES:** La interfaz debe ser estática y determinista. No se permiten transiciones temporales (`transition-*`, `duration-*`), efectos de pulso (`animate-pulse`), spinners giratorios (`animate-spin`) ni barras de progreso con interpolación animada. Los cambios de estado (hover, selección, carga) son instantáneos.
* **SOPORTE DUAL (MODO OSCURO Y MODO CLARO):** La aplicación soporta ambos modos garantizando contraste estricto (WCAG 2.1 AA) a partir de la paleta corporativa oficial.

---

## 3. Paleta de Colores Oficial y Tokens de Diseño

La paleta canónica y definitiva del sistema está definida en Coolors:

* **Enlace Oficial:** [Create a Palette - Coolors](https://coolors.co/2b2d42-8d99ae-edf2f4-ef233c-4361ee)
* **Valores Hexadecimales:**

```json
["#2b2d42", "#8d99ae", "#edf2f4", "#ef233c", "#4361ee"]
```

* **Mockup Oficial del Proyecto:** Disponible para inspección interactiva en [mockups/index.html](file:///c:/Users/BOL%20ALEX/Desktop/Proyectos_Program/Proyectos_Materia/Proyecto-1-Topicos/mockups/index.html).

### 3.1. Mapeo Semántico de la Paleta

| Hex | Nombre | Rol en Modo Oscuro | Rol en Modo Claro | Función en el Sistema |
| :--- | :--- | :--- | :--- | :--- |
| **`#2b2d42`** | Space Cadet | Fondo de tarjetas y paneles (`surface-card`). | Texto principal de encabezados y títulos. | Ancla visual oscura y contenedores modulares. |
| **`#8d99ae`** | Cool Gray | Bordes, separadores y texto secundario. | Bordes, divisores y texto secundario. | Estructura, delimitación y neutralidad. |
| **`#edf2f4`** | Anti-Flash White | Texto principal de lectura y títulos. | Fondo principal del lienzo (`surface-canvas`). | Alto contraste de lectura y superficies claras. |
| **`#ef233c`** | Red Pantone | Borde, texto y badge de alerta de Phishing. | Borde, texto y badge de alerta de Phishing. | Indicador primario y exclusivo de amenaza. |
| **`#4361ee`** | Tech Blue | Botón de acción principal (CTA "Analizar SMS") y nodos activos. | Botón de acción principal (CTA) y acentos interactivos. | Gatillador de análisis y navegación activa. |

### 3.2. Tokens de Superficies y Texto (Modo Oscuro vs. Modo Claro)

| Token Semántico | Modo Oscuro | Modo Claro | Uso Principal |
| :--- | :--- | :--- | :--- |
| `surface-canvas` | `#1e2030` | `#edf2f4` | Fondo general de la ventana y vistas. |
| `surface-card` | `#2b2d42` | `#ffffff` | Tarjetas, contenedores modulares y paneles. |
| `surface-subtle` | `#232537` | `#f4f7f8` | Cajas de texto (inputs/textarea), celdas alternas. |
| `border-subtle` | `rgba(141,153,174,0.3)` | `rgba(141,153,174,0.4)` | Delimitadores de tarjetas y separadores. |
| `border-prominent` | `#8d99ae` | `#8d99ae` | Bordes activos, focus rings y divisores clave. |
| `text-primary` | `#edf2f4` | `#2b2d42` | Títulos principales, valores KPI y encabezados. |
| `text-secondary` | `#8d99ae` | `#576275` | Textos secundarios, descripciones y etiquetas. |
| `text-muted` | `#6b778c` | `#8d99ae` | Metadatos y placeholders. |

### 3.3. Tokens Semánticos de Estado

* **Amenaza / Phishing:**
  * Fondo: `#3a1017` (Oscuro) / `#ffebee` (Claro)
  * Borde: `#ef233c` sólido
  * Texto: `#ef233c` sólido
* **Legítimo / Ham:**
  * Fondo: `#1c2e28` (Oscuro) / `#e8f0fe` (Claro)
  * Borde: `#8d99ae` sólido
  * Texto: `#a8dadc` (Oscuro) / `#2b2d42` (Claro)
* **Entidades NLP (`TOKEN_URL`, `TOKEN_TEL`, etc.):**
  * Entidades técnicas en cajas sólidas con borde `#8d99ae` y texto `#edf2f4`.
  * Urgencia y enlaces externos acentuados con `#4361ee` y `#ef233c`.

### 3.4. Tipografía Jerárquica

* **Familia Primaria (UI):** `Inter, system-ui, -apple-system, sans-serif` (`font-sans`).
* **Familia Técnica (Tokens, Código, TF-IDF, Métricas):** `JetBrains Mono, Fira Code, monospace` (`font-mono`).

| Nivel | Tamaño / Leading | Peso | Aplicación |
| :--- | :--- | :--- | :--- |
| **Display** | 30px / 36px | Bold (700) | Encabezado principal del Dashboard. |
| **Heading 1** | 24px / 32px | Bold (700) | Títulos de Vistas Principales. |
| **Heading 2** | 20px / 28px | Semibold (600) | Títulos de Tarjetas y Secciones. |
| **Body Base** | 16px / 24px | Normal (400) | Textos descriptivos principales. |
| **Caption / Mono** | 12px / 16px | Medium (500) | Badges, chips, pesos TF-IDF y timestamps. |

### 3.5. Espaciado y Radios de Borde

* **Escala de Espaciado Modular (Base 4px / 8px):** `space-1` (4px), `space-2` (8px), `space-3` (12px), `space-4` (16px), `space-6` (24px), `space-8` (32px).
* **Radios de Borde:** `rounded-md` (6px) para inputs y botones; `rounded-xl` (12px) para tarjetas contenedoras.

---

## 4. Catálogo de Componentes Reutilizables

* **`Button`:**
  * `Primary CTA`: `#4361ee` sólido con hover `#3751d8` y texto `#ffffff`.
  * `Secondary`: `#2b2d42` con borde `#8d99ae` y texto `#edf2f4`.
  * `Danger / Alert`: `#ef233c` con texto `#edf2f4`.
  * `Outline`: Transparente con borde `#8d99ae`.
* **`Card`:** Tarjeta modular en `#2b2d42` (Oscuro) o `#ffffff` (Claro) con borde semántico reactivo (`#ef233c` para Phishing, `#8d99ae` para Legítimo).
* **`MessageTextarea`:** Área de texto forense con contador estático de caracteres/palabras y botón principal CTA.
* **`PipelineStepper`:** 6 pestañas estáticas para la inspección paso a paso del pipeline NLP con pestaña activa en `#4361ee`.
* **`AuditTable`:** Tabla con cabecera en `#2b2d42` o `#f4f7f8` y filas alternas con botón para inspección detallada.
* **`ConfusionMatrix`:** Cuadrantes 2x2 de diagnóstico de falsos positivos y falsos negativos.
