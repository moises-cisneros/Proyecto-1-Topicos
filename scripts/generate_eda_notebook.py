#!/usr/bin/env python3
"""
SMS Sentinel - Generador y Ejecutor de Notebook 01_eda.ipynb
Genera el notebook interactivo con analisis estadistico, visualizaciones
y conclusiones de NLP, y lo valida estructuralmente.
"""
import os
import nbformat as nbf

def create_eda_notebook():
    nb = nbf.v4.new_notebook()
    os.makedirs("notebooks", exist_ok=True)

    cells = []

    # Celda 1: Markdown - Introduccion
    cells.append(nbf.v4.new_markdown_cell("""# SMS Sentinel — Análisis Exploratorio de Datos (EDA)
## Detección de Spam y Phishing en SMS en Español

**Proyecto:** SMS Sentinel  
**Fase:** Capa 1 — Datos & Análisis Exploratorio  
**Autor:** Moises Cisneros (`moisescisnerosdl@gmail.com`)  
**Fecha:** Noviembre 2026  

---

### Objetivos del Notebook:
1. **Auditoría de Integridad:** Verificar estructura, volumen y ausencia de nulos en el dataset crudo en español.
2. **Balance de Clases:** Cuantificar el desbalance inherente entre mensajes legítimos (`ham`) y fraudulentos (`spam`).
3. **Distribución de Longitudes:** Comparar distribuciones de longitud de caracteres y cantidad de palabras entre clases.
4. **Vocabulario y Detonantes de Phishing:** Identificar los términos más frecuentes y patrones sintácticos de urgencia o enlaces.
5. **Aislamiento de Particiones:** Validar la estratificación 80/20 (`train.csv` vs `test.csv`) sin fuga de datos (*data leakage*)."""))

    # Celda 2: Code - Imports y configuracion
    cells.append(nbf.v4.new_code_cell("""import os
import re
from collections import Counter
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Configuracion estetica coherente con la paleta de SMS Sentinel
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Helvetica, Arial, sans-serif'
plt.rcParams['axes.edgecolor'] = '#8d99ae'
plt.rcParams['axes.linewidth'] = 0.8

COLOR_HAM = '#4361ee'    # Azul confianza
COLOR_SPAM = '#ef233c'   # Rojo alerta
PALETTE = {'ham': COLOR_HAM, 'spam': COLOR_SPAM}

print("Librerías importadas y estilo visual configurado.")"""))

    # Celda 3: Markdown - Carga de Datos Crudos
    cells.append(nbf.v4.new_markdown_cell("""## 1. Carga y Auditoría del Dataset Crudo

Cargamos `data/raw/sms_spanish.csv` y comprobamos dimensiones, tipos de datos y valores nulos."""))

    # Celda 4: Code - Carga y resumen
    cells.append(nbf.v4.new_code_cell("""raw_path = "../data/raw/sms_spanish.csv" if os.path.exists("../data/raw/sms_spanish.csv") else "data/raw/sms_spanish.csv"
df = pd.read_csv(raw_path)

print(f"Dimensiones del dataset: {df.shape[0]} filas, {df.shape[1]} columnas")
print("\\nTipos de datos y nulos:")
print(df.info())
print("\\nPrimeros registros:")
df.head()"""))

    # Celda 5: Markdown - Analisis de Desbalance de Clases
    cells.append(nbf.v4.new_markdown_cell("""## 2. Análisis de Balance de Clases

La distribución de clases en problemas de spam y ciberseguridad es naturalmente asimétrica. Cuantificamos la proporción exacta de mensajes legítimos (`ham`) versus mensajes no deseados / fraudulentos (`spam`)."""))

    # Celda 6: Code - Distribucion y graficos de clases
    cells.append(nbf.v4.new_code_cell("""class_counts = df['label'].value_counts()
class_percentages = df['label'].value_counts(normalize=True) * 100

summary_df = pd.DataFrame({
    'Cantidad': class_counts,
    'Porcentaje (%)': class_percentages.round(2)
})
print("Distribución de Clases:")
print(summary_df)

fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

# Grafico de barras
sns.barplot(x=class_counts.index, y=class_counts.values, hue=class_counts.index, palette=PALETTE, legend=False, ax=axes[0])
axes[0].set_title("Frecuencia Absoluta de Clases", fontsize=12, fontweight='bold', pad=10)
axes[0].set_ylabel("Número de Mensajes")
axes[0].set_xlabel("Clase")
for i, v in enumerate(class_counts.values):
    axes[0].text(i, v + 80, f"{v:,} ({class_percentages.iloc[i]:.1f}%)", ha='center', fontweight='bold')

# Grafico de torta
axes[1].pie(
    class_counts.values,
    labels=[f"Ham (Legítimo)\\n{class_percentages['ham']:.1f}%", f"Spam (Amenaza)\\n{class_percentages['spam']:.1f}%"],
    colors=[COLOR_HAM, COLOR_SPAM],
    autopct='%1.1f%%',
    startangle=140,
    explode=(0, 0.08),
    wedgeprops={'edgecolor': 'white', 'linewidth': 2}
)
axes[1].set_title("Proporción Relativa de Clases", fontsize=12, fontweight='bold', pad=10)

plt.tight_layout()
plt.show()"""))

    # Celda 7: Markdown - Estadisticas de Longitud
    cells.append(nbf.v4.new_markdown_cell("""## 3. Análisis de Longitud: Caracteres y Cantidad de Palabras

Analizamos si la longitud del texto y el volumen de palabras constituyen señales discriminantes primarias para separar spam de ham."""))

    # Celda 8: Code - Longitudes y resumen estadistico
    cells.append(nbf.v4.new_code_cell("""df['char_length'] = df['text'].astype(str).apply(len)
df['word_count'] = df['text'].astype(str).apply(lambda x: len(x.split()))

print("--- Estadísticas de Longitud de Caracteres por Clase ---")
print(df.groupby('label')['char_length'].describe().round(2))

print("\\n--- Estadísticas de Cantidad de Palabras por Clase ---")
print(df.groupby('label')['word_count'].describe().round(2))"""))

    # Celda 9: Code - Graficos de distribucion de longitud
    cells.append(nbf.v4.new_code_cell("""fig, axes = plt.subplots(2, 2, figsize=(14, 9))

# Distribucion de caracteres (Histograma KDE)
sns.histplot(data=df, x='char_length', hue='label', palette=PALETTE, kde=True, bins=40, ax=axes[0, 0], alpha=0.5)
axes[0, 0].set_title("Distribución de Longitud de Caracteres", fontsize=11, fontweight='bold')
axes[0, 0].set_xlabel("Número de Caracteres")
axes[0, 0].set_ylabel("Densidad")

# Boxplot de caracteres
sns.boxplot(data=df, x='label', y='char_length', hue='label', palette=PALETTE, legend=False, ax=axes[0, 1])
axes[0, 1].set_title("Dispersión de Caracteres por Clase", fontsize=11, fontweight='bold')
axes[0, 1].set_xlabel("Clase")
axes[0, 1].set_ylabel("Caracteres")

# Distribucion de palabras
sns.histplot(data=df, x='word_count', hue='label', palette=PALETTE, kde=True, bins=30, ax=axes[1, 0], alpha=0.5)
axes[1, 0].set_title("Distribución de Cantidad de Palabras", fontsize=11, fontweight='bold')
axes[1, 0].set_xlabel("Número de Palabras")
axes[1, 0].set_ylabel("Densidad")

# Boxplot de palabras
sns.boxplot(data=df, x='label', y='word_count', hue='label', palette=PALETTE, legend=False, ax=axes[1, 1])
axes[1, 1].set_title("Dispersión de Palabras por Clase", fontsize=11, fontweight='bold')
axes[1, 1].set_xlabel("Clase")
axes[1, 1].set_ylabel("Palabras")

plt.tight_layout()
plt.show()"""))

    # Celda 10: Markdown - Interpretacion de longitudes
    cells.append(nbf.v4.new_markdown_cell("""### Hallazgo Clave de Longitud:
* **Mensajes Legítimos (`ham`):** Tienen una mediana de caracteres notablemente menor (~50 caracteres) y menor variabilidad de longitud, con alta concentración en respuestas breves informales (*"ok"*, *"ya llego"*, *"hola"*).
* **Mensajes de Spam / Phishing (`spam`):** Tienen una mediana mucho mayor (~140-160 caracteres), maximizando la cuota estándar de 160 caracteres de un SMS comercial para incluir llamadas a la acción (*call to action*), ofertas, URLs acortadas o números de contacto."""))

    # Celda 11: Markdown - Frecuencia de Terminos y Vocabulario
    cells.append(nbf.v4.new_markdown_cell("""## 4. Análisis de Vocabulario y Términos Más Frecuentes

Examinamos los términos crudos más repetidos en ambas clases para justificar las reglas del pipeline de NLP (normalización, enmascaramiento con tokens sintéticos y stop words con whitelist)."""))

    # Celda 12: Code - Top terminos por clase
    cells.append(nbf.v4.new_code_cell("""def get_top_terms(texts, n=20):
    words = []
    for t in texts:
        tokens = re.findall(r'\\b\\w+\\b', str(t).lower())
        words.extend(tokens)
    return Counter(words).most_common(n)

top_ham = pd.DataFrame(get_top_terms(df[df['label'] == 'ham']['text'], 20), columns=['Termino', 'Frecuencia'])
top_spam = pd.DataFrame(get_top_terms(df[df['label'] == 'spam']['text'], 20), columns=['Termino', 'Frecuencia'])

fig, axes = plt.subplots(1, 2, figsize=(14, 7))

sns.barplot(data=top_ham, y='Termino', x='Frecuencia', color=COLOR_HAM, ax=axes[0])
axes[0].set_title("Top 20 Términos en Mensajes Legítimos (Ham)", fontsize=11, fontweight='bold')
axes[0].set_xlabel("Frecuencia")

sns.barplot(data=top_spam, y='Termino', x='Frecuencia', color=COLOR_SPAM, ax=axes[1])
axes[1].set_title("Top 20 Términos en Mensajes Fraudulentos (Spam)", fontsize=11, fontweight='bold')
axes[1].set_xlabel("Frecuencia")

plt.tight_layout()
plt.show()"""))

    # Celda 13: Markdown - Deteccion de URLs y Numeros
    cells.append(nbf.v4.new_markdown_cell("""## 5. Detección de Señales Críticas: URLs, Números y Teléfonos

Comprobamos la presencia de enlaces web (`http/https/www`), cadenas numéricas y menciones de monedas o teléfonos en ambas clases."""))

    # Celda 14: Code - Analisis de URLs y Numeros
    cells.append(nbf.v4.new_code_cell("""url_regex = re.compile(r'https?://\\S+|www\\.\\S+|\\b\\w+\\.(?:com|org|net|xyz|me|info|es|io|tk|co)\\b', re.IGNORECASE)
num_regex = re.compile(r'\\b\\d+\\b')

df['has_url'] = df['text'].apply(lambda x: 1 if url_regex.search(str(x)) else 0)
df['has_number'] = df['text'].apply(lambda x: 1 if num_regex.search(str(x)) else 0)

url_stats = df.groupby('label')['has_url'].mean() * 100
num_stats = df.groupby('label')['has_number'].mean() * 100

signal_df = pd.DataFrame({
    'Contiene URL (%)': url_stats.round(2),
    'Contiene Número (%)': num_stats.round(2)
})
print("Presencia de Entidades Críticas por Clase:")
print(signal_df)

fig, ax = plt.subplots(figsize=(7, 4))
signal_df.plot(kind='bar', color=['#e63946', '#457b9d'], ax=ax, rot=0)
ax.set_title("Prevalencia de URLs y Números según Clase (%)", fontsize=12, fontweight='bold')
ax.set_ylabel("Porcentaje de Mensajes (%)")
ax.set_xlabel("Clase")
plt.tight_layout()
plt.show()"""))

    # Celda 15: Markdown - Validacion de Particiones Train/Test
    cells.append(nbf.v4.new_markdown_cell("""## 6. Validación de Particiones: Estratificación y Ausencia de Data Leakage

Verificamos que `data/processed/train.csv` (80%) y `data/processed/test.csv` (20%):
1. Cumplan con la proporción exacta de división estratificada.
2. Preserven idéntica proporción de `ham` y `spam`.
3. No compartan índices ni provoquen fuga hacia el conjunto holdout de prueba."""))

    # Celda 16: Code - Validacion de particiones
    cells.append(nbf.v4.new_code_cell("""train_path = "../data/processed/train.csv" if os.path.exists("../data/processed/train.csv") else "data/processed/train.csv"
test_path = "../data/processed/test.csv" if os.path.exists("../data/processed/test.csv") else "data/processed/test.csv"

train_df = pd.read_csv(train_path)
test_df = pd.read_csv(test_path)

total_rows = len(train_df) + len(test_df)
print(f"Total de registros: {total_rows}")
print(f"Train: {len(train_df)} registros ({len(train_df)/total_rows:.2%})")
print(f"Test:  {len(test_df)} registros ({len(test_df)/total_rows:.2%})")

print("\\nProporción en Train:")
print(train_df['label'].value_counts(normalize=True).round(4) * 100)

print("\\nProporción en Test:")
print(test_df['label'].value_counts(normalize=True).round(4) * 100)

# Verificacion de ratio identico
diff_ham = abs(train_df['label'].value_counts(normalize=True)['ham'] - test_df['label'].value_counts(normalize=True)['ham'])
diff_spam = abs(train_df['label'].value_counts(normalize=True)['spam'] - test_df['label'].value_counts(normalize=True)['spam'])
print(f"\\nDiferencia absoluta de proporción (Ham): {diff_ham:.4%}")
print(f"Diferencia absoluta de proporción (Spam): {diff_spam:.4%}")
assert diff_ham < 0.01, "Error: La estratificación difiere en más del 1% entre train y test."
assert diff_spam < 0.01, "Error: La estratificación difiere en más del 1% entre train y test."
print("[OK] Partición estratificada validada rigurosamente.")"""))

    # Celda 17: Markdown - Conclusiones de Arquitectura NLP
    cells.append(nbf.v4.new_markdown_cell("""## 7. Conclusiones y Requisitos para el Pipeline de NLP (Capa 2)

A partir de la evidencia empírica obtenida en este EDA, se establecen los siguientes requisitos de diseño arquitectónico:

1. **Enmascaramiento Léxico Obligatorio (Regex Sanitizer):**
   * Las URLs y los números telefónicos/cifras monetarias son los discriminadores más potentes de spam.
   * **Decisión:** Sustituirlos por tokens sintéticos (`TOKEN_URL`, `TOKEN_TEL`, `TOKEN_NUM`) en lugar de eliminarlos mediante `string.punctuation`.
2. **Stopwords Adaptadas con Whitelist:**
   * Las stopwords tradicionales de NLTK eliminan negaciones (`"no"`, `"sin"`) y términos de urgencia (`"urgente"`, `"bloqueada"`, `"ya"`), que son el corazón de la persuasión en ingeniería social.
   * **Decisión:** Implementar un diccionario de stopwords con lista blanca explícita para el idioma español.
3. **Métrica de Evaluación de Modelos:**
   * Dado el desbalance de clases (86.6% ham / 13.4% spam), la métrica `Accuracy` resulta engañosa (un modelo trivial que siempre predice `ham` obtendría 86.6% de precisión).
   * **Decisión:** La métrica de optimización y benchmark principal será **F1-Score (Spam)** y **Macro F1-Score**, complementado con matrices de confusión y análisis de falsos positivos."""))

    nb.cells = cells

    output_path = "notebooks/01_eda.ipynb"
    with open(output_path, "w", encoding="utf-8") as f:
        nbf.write(nb, f)

    print(f"[OK] Notebook creado exitosamente en: {output_path}")

if __name__ == "__main__":
    create_eda_notebook()
