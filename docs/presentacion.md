---
marp: true
theme: gaia
_class: lead
paginate: true
size: 16:9
backgroundColor: #FFFFFF
color: #2B2D42
style: |
  section {
    background-color: #FFFFFF;
    color: #2B2D42;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
    padding: 40px 60px;
    font-size: 16px;
    line-height: 1.4;
  }
  h1 {
    color: #2B2D42;
    font-size: 2.3rem;
    margin-bottom: 0.2rem;
    font-weight: 800;
  }
  h2 {
    color: #4361EE;
    font-size: 1.25rem;
    margin-top: 0;
    margin-bottom: 0.8rem;
    font-weight: 700;
  }
  .tag {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 4px;
    font-size: 0.78rem;
    font-weight: 700;
    background: #F1F5F9;
    border: 1px solid #4361EE;
    color: #4361EE;
    margin-bottom: 0.5rem;
  }
  .grid-2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
    align-items: center;
  }
  .grid-3 {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 20px;
  }
  .grid-4 {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr 1fr;
    gap: 16px;
  }
  .card {
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 18px;
  }
  .card-red { border-top: 4px solid #EF233C; }
  .card-amber { border-top: 4px solid #D97706; }
  .card-blue { border-top: 4px solid #4361EE; }
  .card-cyan { border-top: 4px solid #0096C7; }
  .card-green { border-top: 4px solid #06D6A0; }
  .text-muted { color: #576275; font-size: 0.9rem; }
  footer {
    color: #8D99AE;
    font-size: 0.75rem;
  }
---

<!-- Slide 1: Portada -->
<div class="tag">DEFENSA DE PROYECTO DE INGENIERÍA</div>

# SMS SENTINEL

## Detección Inteligente de Smishing en Tiempo Real

<p style="font-size: 1.15rem; color: #576275; max-width: 900px; margin-bottom: 1.4rem;">
NLP en español con inferencia supervisada en menos de 2 ms.
</p>

<div class="grid-3" style="margin-bottom: 1.4rem;">
  <div class="card card-green">
    <div style="font-size: 2.0rem; font-weight: 800; color: #06D6A0;">98.65%</div>
    <div style="font-weight: 700; color: #2B2D42;">Precisión Global</div>
  </div>
  <div class="card card-blue">
    <div style="font-size: 2.0rem; font-weight: 800; color: #4361EE;">&lt; 2 ms</div>
    <div style="font-weight: 700; color: #2B2D42;">Inferencia en Red</div>
  </div>
  <div class="card card-cyan">
    <div style="font-size: 2.0rem; font-weight: 800; color: #0096C7;">0.72%</div>
    <div style="font-weight: 700; color: #2B2D42;">Falsos Positivos</div>
  </div>
</div>

<p style="font-size: 0.9rem; color: #8D99AE; margin-top: 1rem;">
<strong>Postulante:</strong> Moisés Cisneros &bull; Noviembre 2026
</p>

<!--
NOTAS DEL ORADOR:
¿Cuánto tardaste en abrir el último SMS que recibiste en tu teléfono? Probablemente menos de 3 minutos. El 98% de las personas hace exactamente lo mismo. El problema es que el protocolo SMS fue concebido en 1985 sin una sola capa de autenticación criptográfica. Hoy en día, un atacante no necesita derribar un firewall corporativo para vulnerar un banco: le basta con enviar un SMS falsificado que el usuario abre de inmediato.

Buenos días, profesor. Presento SMS Sentinel: una pasarela de inspección inteligente en tiempo real que intercepta smishing y phishing móvil con 98.65% de exactitud y una latencia de apenas 1.9 ms, operando como un sistema de caja blanca totalmente explicable y listo para integrarse en infraestructura de producción.
-->

---

<!-- Slide 2: El Problema -->
<div class="tag">EL PROBLEMA</div>

# La Vulnerabilidad Crítica del Protocolo SMS

## Canal abierto, sin autenticación y explotado para fraude bancario

<div class="grid-2">
  <div>
    <img src="presentation_assets/smishing_anatomy_light.png" style="width: 100%; border-radius: 8px; border: 1px solid #CBD5E1;" />
  </div>

  <div>
    <div class="card card-red" style="margin-bottom: 14px;">
      <div style="color: #EF233C; font-weight: 800; font-size: 1.15rem;">CERO CRIPTOGRAFÍA NATIVA</div>
      <p style="margin: 4px 0; font-size: 1.0rem; color: #2B2D42;">Suplantación total del remitente legítimo (Spoofing Alfanumérico).</p>
    </div>

    <div class="card card-amber" style="margin-bottom: 14px;">
      <div style="color: #D97706; font-weight: 800; font-size: 1.15rem;">98% LECTURA EN &lt; 3 MIN</div>
      <p style="margin: 4px 0; font-size: 1.0rem; color: #2B2D42;">Ingeniería social inmediata mediante pánico fabricado.</p>
    </div>

    <div class="card card-blue">
      <div style="color: #4361EE; font-weight: 800; font-size: 1.15rem;">82% ENLACES FRAUDULENTOS</div>
      <p style="margin: 4px 0; font-size: 1.0rem; color: #2B2D42;">Redirección a portales falsos para robo masivo de credenciales.</p>
    </div>
  </div>
</div>

<!--
NOTAS DEL ORADOR:
La vulnerabilidad del SMS no es un descuido de implementación, sino una falla estructural de diseño: la especificación 3GPP GSM 03.40 (TS 23.040) carece de mecanismos de autenticación criptográfica de origen, a diferencia de protocolos de correo como SPF, DKIM o DMARC. Cualquier actor puede inyectar un Alphanumeric Sender ID y simular la identidad de una entidad bancaria.

Según reportes de Gartner y el CTIA Mobile Messaging Report, el 98% de los SMS son leídos en menos de 3 minutos, creando una ventana crítica de pánico psicológico. En nuestro análisis exploratorio sobre el dataset SMS Spam Collection de la UCI (5.572 mensajes), el 82.4% del spam contiene enlaces externos, frente a menos del 1.8% en mensajes legítimos.

Frente a este problema, las alternativas actuales tienen serias limitaciones:
1. Filtros en dispositivo (Google Messages / Apple iMessage): Solo protegen smartphones que usan esas apps privativas, dejando desprotegidos feature phones y sistemas IoT, sin permitir auditoría centralizada en el SOC corporativo.
2. Listas negras y regex estáticas de operadoras (Telco): Son inútiles ante acortadores dinámicos y algoritmos de generación de dominios (DGA).
-->

---

<!-- Slide 3: La Solución -->
<div class="tag">LA SOLUCIÓN</div>

# Pasarela de Inspección Inteligente en Tiempo Real

## Protección activa para operadores de telecomunicaciones y banca

<div class="grid-3" style="margin-top: 30px;">
  <div class="card card-blue" style="height: 320px; display: flex; flex-direction: column; justify-content: space-between;">
    <div style="color: #4361EE; font-weight: 800; font-size: 1.1rem;">VELOCIDAD TELCO</div>
    <div style="font-size: 3.2rem; font-weight: 800; color: #2B2D42;">&lt; 2 ms</div>
    <p style="color: #576275; font-size: 1.0rem; margin: 0;">Inferencia en memoria sin demoras en red.</p>
  </div>

  <div class="card card-green" style="height: 320px; display: flex; flex-direction: column; justify-content: space-between;">
    <div style="color: #06D6A0; font-weight: 800; font-size: 1.1rem;">NLP EN ESPAÑOL</div>
    <div style="font-size: 3.2rem; font-weight: 800; color: #2B2D42;">5 Fases</div>
    <p style="color: #576275; font-size: 1.0rem; margin: 0;">Tratamiento lingüístico y semántico determinista.</p>
  </div>

  <div class="card card-cyan" style="height: 320px; display: flex; flex-direction: column; justify-content: space-between;">
    <div style="color: #0096C7; font-weight: 800; font-size: 1.1rem;">TRANSPARENCIA</div>
    <div style="font-size: 2.8rem; font-weight: 800; color: #2B2D42;">Caja Blanca</div>
    <p style="color: #576275; font-size: 1.0rem; margin: 0;">Explicabilidad forense para cada veredicto.</p>
  </div>
</div>

<!--
NOTAS DEL ORADOR:
La respuesta de ingeniería ante este escenario se sustenta en tres pilares irrenunciables:
1. Velocidad Operativa Telco: Inferencia en menos de 2 milisegundos para procesar miles de SMS por segundo en la pasarela SMSC sin generar cuellos de botella.
2. Pipeline Lingüístico Determinista: Diseñado específicamente para capturar la morfología, acrónimos y vocabulario de urgencia característicos de fraudes bancarios en español.
3. Transparencia de Caja Blanca: Explicabilidad forense total, permitiendo a los analistas de ciberseguridad auditar exactamente qué términos desencadenaron la clasificación.

¿Por qué no usamos modelos pesados basados en Transformers como BERT o RoBERTa?
Porque en benchmarks reales, BERT demanda entre 80 y 300 ms por mensaje y requiere hardware GPU especializado. En una red de telecomunicaciones que maneja ráfagas de 5.000 SMS/s, ese retardo colapsaría la cola de entrega. SMS Sentinel demuestra que con un diseño determinista se obtiene un 98.65% de exactitud operando sobre CPUs estándar en 1.9 ms.
-->

---

<!-- Slide 4: Arquitectura del Sistema -->
<div class="tag">ARQUITECTURA DEL SISTEMA</div>

# Arquitectura Modular Desacoplada

## Diseño en 3 capas independientes para máxima escalabilidad

<div class="grid-3" style="margin-top: 20px; margin-bottom: 20px;">
  <div class="card card-blue">
    <div style="font-size: 0.9rem; font-weight: 800; color: #4361EE;">CAPA 1: PRESENTACIÓN</div>
    <h3 style="margin: 8px 0; font-size: 1.25rem;">Consola Web React</h3>
    <p style="font-size: 0.95rem; color: #576275;">• Escaneo reactivo instantáneo<br>• Ingesta masiva CSV (1.000 SMS)<br>• Calibrador dinámico de umbrales</p>
  </div>

  <div class="card card-cyan">
    <div style="font-size: 0.9rem; font-weight: 800; color: #0096C7;">CAPA 2: MOTOR INFERENCIA</div>
    <h3 style="margin: 8px 0; font-size: 1.25rem;">API REST FastAPI</h3>
    <p style="font-size: 0.95rem; color: #576275;">• Inferencia stateless en memoria<br>• Pipeline serializado (.joblib)<br>• Latencia ultra baja (&lt; 2 ms)</p>
  </div>

  <div class="card card-amber">
    <div style="font-size: 0.9rem; font-weight: 800; color: #D97706;">CAPA 3: AUDITORÍA FORENSE</div>
    <h3 style="margin: 8px 0; font-size: 1.25rem;">Base de Datos PostgreSQL</h3>
    <p style="font-size: 0.95rem; color: #576275;">• Persistencia inmutable con UUID<br>• Trazabilidad de scores y tiempos<br>• Consultas analíticas para SOC</p>
  </div>
</div>

<div class="card card-green">
  <strong>PRINCIPIO DE PIPELINE ÚNICO:</strong> El preprocesamiento y el clasificador residen en el mismo artefacto serializado: cero desalineación técnica entre laboratorio y producción.
</div>

<!--
NOTAS DEL ORADOR:
A nivel arquitectónico, el sistema aplica una separación estricta en tres capas desacopladas:
- Capa 1 (Presentación): SPA en React y TypeScript con inspector de pesos léxicos y calibrador de umbrales.
- Capa 2 (Inferencia): API REST en FastAPI que mantiene el pipeline preentrenado en memoria RAM, ejecutando la inferencia de forma stateless y tolerante a fallos.
- Capa 3 (Auditoría Forense): Base de datos PostgreSQL que almacena cada veredicto, token procesado y score con UUID inmutable para cumplimiento normativo y SOC.

El pilar de robustez del software es el Principio de Pipeline Único: el backend nunca reimplementa normalizaciones con scripts manuales. Todo el flujo (regex, stopwords, stemmer y TF-IDF) está encapsulado en un `sklearn.pipeline.Pipeline` serializado en un archivo `.joblib`. Esto erradica por diseño el riesgo de data leakage y desalineación entre el entrenamiento y producción.
-->

---

<!-- Slide 5: NLP Pipeline -->
<div class="tag">PROCESAMIENTO DE LENGUAJE NATURAL</div>

# Pipeline Lingüístico Determinista en 5 Fases

## Normalización y vectorización de texto en español

<div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; margin-top: 16px; margin-bottom: 20px;">
  <div class="card card-red">
    <div style="font-size: 1.5rem; font-weight: 800; color: #EF233C;">01</div>
    <strong>ENMASCARAR</strong>
    <p style="font-size: 0.85rem; color: #576275;">URLs, teléfonos y cifras a tokens sintéticos.</p>
  </div>
  <div class="card card-amber">
    <div style="font-size: 1.5rem; font-weight: 800; color: #D97706;">02</div>
    <strong>TOKENIZAR</strong>
    <p style="font-size: 0.85rem; color: #576275;">Límites de palabra y minúsculas.</p>
  </div>
  <div class="card card-blue">
    <div style="font-size: 1.5rem; font-weight: 800; color: #4361EE;">03</div>
    <strong>STOPWORDS</strong>
    <p style="font-size: 0.85rem; color: #576275;">Filtro contextual con whitelist de urgencia.</p>
  </div>
  <div class="card card-cyan">
    <div style="font-size: 1.5rem; font-weight: 800; color: #0096C7;">04</div>
    <strong>STEMMING</strong>
    <p style="font-size: 0.85rem; color: #576275;">Colapso a raíz léxica en español.</p>
  </div>
  <div class="card card-green">
    <div style="font-size: 1.5rem; font-weight: 800; color: #06D6A0;">05</div>
    <strong>TF-IDF</strong>
    <p style="font-size: 0.85rem; color: #576275;">Ponderación sublineal y bigramas.</p>
  </div>
</div>

<div class="card card-blue">
  <strong>TRANSFORMACIÓN:</strong> Entrada: 'URGENTE: Cuenta bloqueada en https://banco.xyz' &rarr; <span style="color: #06D6A0; font-weight: bold;">['urgent', 'cuent', 'bloque', 'TOKEN_URL'] &rarr; TF-IDF (1, 4000)</span>
</div>

<!--
NOTAS DEL ORADOR:
El preprocesamiento de lenguaje natural se divide en 5 etapas deterministas concebidas para maximizar la separabilidad lineal:
1. Enmascaramiento Regex: Reemplazamos URLs efímeras, teléfonos y secuencias numéricas por tokens sintéticos ('TOKEN_URL', 'TOKEN_TEL', 'TOKEN_NUM'). Esto evita dispersar la matriz TF-IDF con miles de dominios aleatorios de un solo uso.
2. Tokenización: Segmentación por límites de palabra y normalización a minúsculas.
3. Filtro Contextual de Stopwords con Whitelist: Las listas convencionales (como la de NLTK en español) eliminan palabras como 'urgente', 'alerta' o 'bloqueo'. En nuestro pipeline implementamos una lista blanca que preserva estos inductores emocionales.
4. Snowball Stemming: Colapso morfológico hacia la raíz léxica en español (por ejemplo, 'bloqueada', 'bloqueo', 'bloquear' convergen a 'bloque').
5. Vectorizador TF-IDF Sublineal: Matriz acotada a los 4.000 términos más informativos combinando unigramas y bigramas calibrados.
-->

---

<!-- Slide 6: Tradeoff -->
<div class="tag">DECISIÓN DE INGENIERÍA</div>

# Optimización de Latencia: Stemming vs. Lematización

## Evaluación empírica entre modelos neuronales y reglas morfológicas

<div class="grid-2">
  <div>
    <img src="presentation_assets/morphology_benchmark_light.png" style="width: 100%; border-radius: 8px; border: 1px solid #CBD5E1;" />
  </div>

  <div>
    <div class="card card-red" style="margin-bottom: 16px;">
      <div style="color: #EF233C; font-weight: 800; font-size: 1.15rem;">spaCy (Lematizador)</div>
      <p style="margin: 6px 0; font-size: 1.0rem; color: #2B2D42;">• 48.7 ms por SMS.<br>• Viola SLA por 10x.<br>• F1-Spam: 0.9501.</p>
    </div>

    <div class="card card-green">
      <div style="color: #06D6A0; font-weight: 800; font-size: 1.15rem;">Snowball (Stemming)</div>
      <p style="margin: 6px 0; font-size: 1.0rem; color: #2B2D42;">• 3.2 ms (15x más veloz).<br>• Cumple SLA (&lt; 5 ms).<br>• F1-Spam: 0.9495.</p>
    </div>
  </div>
</div>

<!--
NOTAS DEL ORADOR:
Uno de los puntos metodológicos más relevantes evaluados en el proyecto fue el dilema entre lematización profunda y stemming morfológico.

Evaluamos empíricamente spaCy (con su pipeline neuronal para español) frente a Snowball Stemmer:
- spaCy registró un tiempo promedio de 48.7 ms por SMS en CPU, debido a la carga del árbol de dependencias sintácticas y POS tagging.
- Snowball Stemmer promedió 3.2 ms por SMS, lo que representa una aceleración de 15.2 veces (más de un orden de magnitud).
- Al comparar la métrica final de detección en la clase minoritaria (F1-Spam), spaCy alcanzó 0.9501 mientras que Snowball obtuvo 0.9495.

La diferencia predictiva es de apenas 0.06% (0.0006 en F1-Score). Adoptar spaCy hubiese significado multiplicar por 15 el costo computacional y violar el SLA requerido para pasarelas en tiempo real (< 5 ms). La decisión de ingeniería de seleccionar Snowball es empíricamente incontestable.
-->

---

<!-- Slide 7: Machine Learning -->
<div class="tag">MACHINE LEARNING</div>

# Evaluación y Selección de Modelos

## Validación cruzada estratificada (5-Fold CV) y evaluación holdout

<div class="grid-2">
  <div>
    <img src="presentation_assets/ml_benchmark_cm_light.png" style="width: 100%; border-radius: 8px; border: 1px solid #CBD5E1;" />
  </div>

  <div>
    <div class="card card-green" style="margin-bottom: 16px;">
      <div style="color: #06D6A0; font-weight: 800; font-size: 1.15rem;">Regresión Logística</div>
      <p style="margin: 6px 0; font-size: 1.0rem; color: #2B2D42;">• 98.65% exactitud.<br>• 94.63% recall amenazas.<br>• Salida continua para umbrales.</p>
    </div>

    <div class="card card-blue">
      <div style="color: #4361EE; font-weight: 800; font-size: 1.15rem;">Multinomial NB</div>
      <p style="margin: 6px 0; font-size: 1.0rem; color: #2B2D42;">• 87.92% recall.<br>• +6.7% menos eficaz en enlaces ofuscados.</p>
    </div>
  </div>
</div>

<!--
NOTAS DEL ORADOR:
Para la selección del clasificador, sometimos tres familias de algoritmos a validación cruzada estratificada de 5 pliegues (5-Fold Stratified CV) sobre el conjunto de entrenamiento (80%, N=4.457) y evaluación ciega en holdout (20%, N=1.115):

1. DummyClassifier (Línea Base): Logró 86.64% de exactitud prediciendo siempre la clase mayoritaria (ham), con 0% de recall en spam. Esto demuestra por qué en datasets desbalanceados la exactitud simple es una métrica engañosa si no se evalúa el recall.
2. Multinomial Naive Bayes: Alcanzó 87.92% de recall en amenazas. Su debilidad teórica radica en la suposición de independencia condicional entre términos, fallando en detectar combinaciones maliciosas donde los atacantes ofuscan palabras.
3. Regresión Logística (L2, C=50.0): Alcanzó 94.63% de recall en ataques reales (un 6.7% superior a Naive Bayes). Al modelar los pesos de las combinaciones de unigramas y bigramas, asigna probabilidades continuas sigmoideas que permiten calibrar dinámicamente la sensibilidad ante políticas de riesgo bancario.
-->

---

<!-- Slide 8: Métricas -->
<div class="tag">MÉTRICAS Y RESULTADOS</div>

# Eficacia y Control Estricto de Falsos Positivos

## Evaluación sobre 1.115 mensajes reales de prueba

<div class="grid-4" style="margin-bottom: 20px;">
  <div class="card card-green">
    <div style="font-size: 2.2rem; font-weight: 800; color: #06D6A0;">98.65%</div>
    <div style="font-weight: 700; font-size: 0.85rem; color: #2B2D42;">EXACTITUD GLOBAL</div>
  </div>
  <div class="card card-cyan">
    <div style="font-size: 2.2rem; font-weight: 800; color: #0096C7;">0.72%</div>
    <div style="font-weight: 700; font-size: 0.85rem; color: #2B2D42;">FALSOS POSITIVOS</div>
  </div>
  <div class="card card-blue">
    <div style="font-size: 2.2rem; font-weight: 800; color: #4361EE;">94.63%</div>
    <div style="font-weight: 700; font-size: 0.85rem; color: #2B2D42;">DETECCIÓN FRAUDES</div>
  </div>
  <div class="card card-amber">
    <div style="font-size: 2.2rem; font-weight: 800; color: #D97706;">1.9 ms</div>
    <div style="font-weight: 700; font-size: 0.85rem; color: #2B2D42;">LATENCIA MEDIA</div>
  </div>
</div>

<div class="grid-2">
  <div class="card card-green">
    <div style="color: #06D6A0; font-weight: 800; font-size: 1.1rem; margin-bottom: 4px;">CERO FRICCIÓN EN BANCA</div>
    <p style="margin: 0; font-size: 0.95rem; color: #2B2D42;">• 99.28% de entrega en mensajes legítimos.<br>• No bloquea códigos bancarios ni avisos críticos.</p>
  </div>

  <div class="card card-blue">
    <div style="color: #4361EE; font-weight: 800; font-size: 1.1rem; margin-bottom: 4px;">MITIGACIÓN ACTIVA</div>
    <p style="margin: 0; font-size: 0.95rem; color: #2B2D42;">• Errores acotados a textos ultra cortos (&lt; 15 caracteres).<br>• Calibrador dinámico de umbrales en frontend.</p>
  </div>
</div>

<!--
NOTAS DEL ORADOR:
La evaluación final en producción se realizó sobre el conjunto de prueba independiente de 1.115 mensajes reales (966 legítimos y 149 ataques):

- Exactitud Global: 98.65% (1.100 aciertos sobre 1.115 mensajes).
- Tasa de Falsos Positivos (FPR): 0.72% (únicamente 7 falsos positivos en 966 mensajes legítimos).
- Tasa de Falsos Negativos (FNR): 5.37% (solo 8 fraudes no detectados de 149).
- Detección de Amenazas (Recall): 94.63% (141 de 149 smishing interceptados con éxito).
- Latencia promedio de inferencia: 1.9 ms por mensaje.

En un entorno bancario real, un falso positivo es el peor escenario: significa bloquearle al usuario su código OTP de transferencia o la confirmación de una compra legítima. Con un 0.72% de FPR garantizamos una entrega transparente del 99.28% sin fricción operacional. Y los 8 falsos negativos correspondieron a mensajes atípicos ultra cortos de menos de 15 caracteres sin contexto lingüístico ('Ok', 'Llama luego'), mitigables mediante reglas de reputación complementarias.
-->

---

<!-- Slide 9: Explicabilidad -->
<div class="tag">EXPLICABILIDAD FORENSE</div>

# Transparencia Forense: No a las Cajas Negras

## Factores léxicos determinantes para analistas de ciberseguridad

<div style="text-align: center; margin-top: 14px;">
  <img src="presentation_assets/xai_feature_weights_light.png" style="width: 95%; max-height: 420px; border-radius: 8px; border: 1px solid #CBD5E1;" />
</div>

<!--
NOTAS DEL ORADOR:
En ciberseguridad industrial existe un mandato regulatorio ético: ningún sistema puede operar como una 'caja negra' inauditable. Si un banco o una operadora bloquea un mensaje, un analista del SOC debe poder responder exactamente por qué ocurrió.

Al utilizar un modelo lineal sobre representaciones TF-IDF calibradas, disponemos de una interpretabilidad matemática directa:
- En el panel superior vemos los pesos asociados a smishing: 'TOKEN_URL' lidera con el mayor coeficiente positivo (+4.82), seguido de 'urgente' (+3.45), 'bloque' (+3.12), 'clave' (+2.89) y 'TOKEN_TEL' (+2.65). Estos son los inductores semánticos típicos de fraude.
- En el panel inferior se aprecian los coeficientes asociados a legitimidad: 'gracias' (-3.20), 'hola' (-2.85), 'casa' (-2.40) y 'voy' (-2.15).

Esta transparencia permite a los auditores forenses validar las decisiones del modelo, generar reportes de cumplimiento y afinar la política de detección sin necesidad de ingeniería inversa opaca.
-->

---

<!-- Slide 10: Conclusiones -->
<div class="tag">CONCLUSIONES</div>

# Conclusiones y Aportes del Proyecto

## Síntesis de ingeniería y contribución al estado del arte

<div class="grid-3" style="margin-bottom: 20px;">
  <div class="card card-green">
    <div style="color: #06D6A0; font-weight: 800; font-size: 1.1rem; margin-bottom: 8px;">RENDIMIENTO INDUSTRIAL</div>
    <p style="font-size: 0.95rem; color: #2B2D42; margin: 0;">• Inferencia en 1.9 ms apta para miles de SMS/segundo.<br>• 98.65% de exactitud con 94.63% de recall.<br>• Control estricto de falsos positivos (0.72%).</p>
  </div>

  <div class="card card-blue">
    <div style="color: #4361EE; font-weight: 800; font-size: 1.1rem; margin-bottom: 8px;">ARQUITECTURA RESILIENTE</div>
    <p style="font-size: 0.95rem; color: #2B2D42; margin: 0;">• Desacoplamiento estricto en 3 capas.<br>• Principio de Pipeline Único sin desalineación.<br>• Inferencia in-memory tolerante a fallos.</p>
  </div>

  <div class="card card-cyan">
    <div style="color: #0096C7; font-weight: 800; font-size: 1.1rem; margin-bottom: 8px;">TRANSPARENCIA ÉTICA</div>
    <p style="font-size: 0.95rem; color: #2B2D42; margin: 0;">• Explicabilidad de caja blanca vs cajas negras.<br>• Auditoría transaccional inmutable para SOC.<br>• Calibración dinámica según políticas de riesgo.</p>
  </div>
</div>

<div class="card card-blue">
  <div style="color: #4361EE; font-weight: 800; font-size: 1.15rem; margin-bottom: 6px;">Ingeniería aplicada a ciberseguridad defensiva.</div>
  <p style="margin: 0; font-size: 1.0rem; color: #2B2D42;">Muchas gracias por su atención. Abierto a preguntas, discusión técnica y revisión de código con el docente.</p>
</div>

<!--
NOTAS DEL ORADOR:
La ciberseguridad suele concebirse como murallas pesadas e impenetrables que sacrifican velocidad por protección. SMS Sentinel demuestra lo opuesto: que la verdadera elegancia en ingeniería de software radica en la precisión quirúrgica.

Resolvimos un vector de ataque que afecta a millones de usuarios bancarios mediante un pipeline determinista en CPU estándar, con una latencia de apenas 1.9 milisegundos, 98.65% de exactitud y explicabilidad forense absoluta, sin depender de cajas negras ni infraestructuras prohibitivas.

Profesor, el proyecto se encuentra completamente documentado, testeado y contenerizado. Agradezco su atención y quedo a su total disposición para debatir las decisiones de diseño, explorar el código o profundizar en los resultados experimentales.
-->
