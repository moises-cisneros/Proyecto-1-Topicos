"""
SMS Sentinel - Active Visual Assets Generator
Generates only the active diagrams and charts used in the presentations (Light and Dark versions).
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

OUTPUT_DIR = os.path.join("docs", "presentation_assets")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Palettes
PALETTE_LIGHT = {
    "bg": "#FFFFFF",
    "surface": "#F8FAFC",
    "border": "#E2E8F0",
    "border_dark": "#CBD5E1",
    "text": "#2B2D42",
    "text_muted": "#576275",
    "accent_blue": "#4361EE",
    "accent_red": "#EF233C",
    "accent_green": "#06D6A0",
    "accent_amber": "#D97706",
}

PALETTE_DARK = {
    "bg": "#131524",
    "surface": "#1E2238",
    "border": "#384064",
    "border_dark": "#4361EE",
    "text": "#EDF2F4",
    "text_muted": "#8D99AE",
    "accent_blue": "#4361EE",
    "accent_red": "#EF233C",
    "accent_green": "#06D6A0",
    "accent_amber": "#FFB703",
}

plt.rcParams['font.family'] = ['Segoe UI', 'DejaVu Sans', 'Arial']


def generate_smishing_anatomy(is_dark=False):
    p = PALETTE_DARK if is_dark else PALETTE_LIGHT
    suffix = "" if is_dark else "_light"

    fig, ax = plt.subplots(figsize=(7.2, 5.0), dpi=200)
    fig.patch.set_facecolor(p["bg"])
    ax.set_facecolor(p["bg"])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    phone = patches.FancyBboxPatch(
        (18, 5), 64, 90,
        boxstyle="round,pad=1.5,rounding_size=4",
        facecolor=p["surface"],
        edgecolor=p["border_dark"],
        linewidth=2
    )
    ax.add_patch(phone)

    notch = patches.FancyBboxPatch(
        (42, 91), 16, 2.0,
        boxstyle="round,pad=0.3,rounding_size=1",
        facecolor="#CBD5E1" if not is_dark else "#384064",
        edgecolor="none"
    )
    ax.add_patch(notch)

    contact_card = patches.FancyBboxPatch(
        (23, 79), 54, 9,
        boxstyle="round,pad=0.6,rounding_size=2",
        facecolor=p["bg"] if not is_dark else p["surface"],
        edgecolor=p["accent_red"],
        linewidth=1.2
    )
    ax.add_patch(contact_card)
    ax.text(26, 84, "BANCO_ALERTA", fontsize=11, fontweight='bold', color=p["accent_red"])
    ax.text(26, 80.5, "Remitente Alfanumérico • Sin Autenticación Criptográfica (Spoofing)", fontsize=6.8, color=p["text_muted"])

    bubble = patches.FancyBboxPatch(
        (23, 44), 54, 31,
        boxstyle="round,pad=1.0,rounding_size=2.5",
        facecolor=p["bg"] if not is_dark else "#252A45",
        edgecolor=p["border"],
        linewidth=1.2
    )
    ax.add_patch(bubble)

    lines = [
        ("ALERTA BANCO: ", True, p["accent_red"]),
        ("Su cuenta ha sido bloqueada por", False, p["text"]),
        ("seguridad. Ingrese de inmediato a:", False, p["text"]),
        ("https://banco-login-verif.xyz/seguro", True, p["accent_blue"]),
        ("para verificar su identidad y evitar multas.", False, p["text"])
    ]
    y_pos = 70
    for text, bold, col in lines:
        ax.text(26, y_pos, text, fontsize=8.5, fontweight='bold' if bold else 'normal', color=col)
        y_pos -= 5.0

    ax.annotate(
        "Inductor de Urgencia\n(Whitelist Preservada)",
        xy=(56, 68), xytext=(80, 78),
        arrowprops=dict(facecolor=p["accent_amber"], edgecolor=p["accent_amber"], arrowstyle="->", lw=1.5),
        fontsize=7.8, fontweight='bold', color=p["accent_amber"],
        bbox=dict(boxstyle="round,pad=0.4", fc=p["surface"], ec=p["accent_amber"], lw=1)
    )

    ax.annotate(
        "Enlace Fraudulento\n(Tokenizado: TOKEN_URL)",
        xy=(58, 54), xytext=(80, 50),
        arrowprops=dict(facecolor=p["accent_blue"], edgecolor=p["accent_blue"], arrowstyle="->", lw=1.5),
        fontsize=7.8, fontweight='bold', color=p["accent_blue"],
        bbox=dict(boxstyle="round,pad=0.4", fc=p["surface"], ec=p["accent_blue"], lw=1)
    )

    banner = patches.FancyBboxPatch(
        (23, 14), 54, 25,
        boxstyle="round,pad=1.0,rounding_size=2.5",
        facecolor="#FEF2F2" if not is_dark else "#2A1017",
        edgecolor=p["accent_red"],
        linewidth=1.8
    )
    ax.add_patch(banner)

    ax.text(50, 32, "VEREDICTO EN TIEMPO REAL", ha='center', fontsize=9.0, fontweight='bold', color=p["accent_red"])
    ax.text(50, 25, "AMENAZA: SMISHING BANCARIO", ha='center', fontsize=11.5, fontweight='bold', color=p["text"])
    ax.text(50, 19, "Probabilidad: 99.8%  |  Latencia: 1.8 ms", ha='center', fontsize=8.5, color=p["text_muted"])
    ax.text(50, 15, "Acción: Bloqueo Inmediato y Reporte Forense", ha='center', fontsize=7.5, fontweight='bold', color=p["accent_red"])

    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, f"smishing_anatomy{suffix}.png")
    fig.savefig(output_path, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
    plt.close(fig)


def generate_morphology_benchmark(is_dark=False):
    p = PALETTE_DARK if is_dark else PALETTE_LIGHT
    suffix = "" if is_dark else "_light"

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 4.4), dpi=200)
    fig.patch.set_facecolor(p["bg"])

    ax1.set_facecolor(p["surface"])
    models = ['spaCy (Neuronal)\nLematizador', 'Snowball Stemmer\n(Seleccionado)']
    latencies = [48.7, 3.2]
    colors = [p["accent_red"], p["accent_green"]]

    bars1 = ax1.bar(models, latencies, color=colors, width=0.48, edgecolor=p["border"])
    ax1.set_title("Latencia de Inferencia por Mensaje (ms)", fontsize=11, fontweight='bold', pad=12, color=p["text"])
    ax1.set_ylabel("Milisegundos (ms)", fontsize=9.5, color=p["text"])
    ax1.set_ylim(0, 58)
    ax1.tick_params(colors=p["text_muted"])

    ax1.axhline(5.0, color=p["accent_amber"], linestyle='--', linewidth=2, label="Umbral Máximo SLA (< 5 ms)")
    ax1.legend(loc='upper right', facecolor=p["bg"], edgecolor=p["border"], fontsize=8.5, labelcolor=p["text"])

    for bar, val in zip(bars1, latencies):
        y = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width() / 2, y + 1.8, f"{val:.1f} ms", ha='center', fontsize=11, fontweight='bold', color=p["text"])

    ax1.text(1, 10, "15x MÁS RÁPIDO\nCumple SLA holgadamente", ha='center', fontsize=9.0, fontweight='bold', color=p["accent_green"],
             bbox=dict(boxstyle="round,pad=0.4", fc=p["surface"], ec=p["accent_green"]))
    ax1.text(0, 30, "INVIABLE EN RED\nSupera el SLA en casi 10x", ha='center', fontsize=9.0, fontweight='bold', color=p["accent_red"],
             bbox=dict(boxstyle="round,pad=0.4", fc=p["surface"], ec=p["accent_red"]))

    ax2.set_facecolor(p["surface"])
    f1_scores = [95.01, 94.95]
    bars2 = ax2.bar(models, f1_scores, color=[p["accent_blue"], p["accent_green"]], width=0.48, edgecolor=p["border"])
    ax2.set_title("Eficacia Predictiva (F1-Score en Spam %)", fontsize=11, fontweight='bold', pad=12, color=p["text"])
    ax2.set_ylabel("F1-Score (%)", fontsize=9.5, color=p["text"])
    ax2.set_ylim(90, 97)
    ax2.tick_params(colors=p["text_muted"])

    for bar, val in zip(bars2, f1_scores):
        y = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width() / 2, y + 0.3, f"{val:.2f}%", ha='center', fontsize=11, fontweight='bold', color=p["text"])

    ax2.text(0.5, 92.5, "Equivalencia Estadística\nDelta F1 = 0.06% (Despreciable)", ha='center', fontsize=9.5, fontweight='bold', color=p["text"],
             bbox=dict(boxstyle="round,pad=0.5", fc=p["surface"], ec=p["accent_blue"], lw=1.2))

    for ax in (ax1, ax2):
        ax.grid(axis='y', color=p["border"], linestyle=':', alpha=0.8)
        for spine in ax.spines.values():
            spine.set_color(p["border"])

    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, f"morphology_benchmark{suffix}.png")
    fig.savefig(output_path, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
    plt.close(fig)


def generate_ml_benchmark_cm(is_dark=False):
    p = PALETTE_DARK if is_dark else PALETTE_LIGHT
    suffix = "" if is_dark else "_light"

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 4.4), dpi=200)
    fig.patch.set_facecolor(p["bg"])

    ax1.set_facecolor(p["surface"])
    models = ['Baseline\n(Dummy)', 'Multinomial\nNaive Bayes', 'Regresión\nLogística (Ganador)']
    accuracy = [86.64, 98.21, 98.65]
    f1_spam = [0.0, 92.91, 94.95]

    x = np.arange(len(models))
    width = 0.32

    rects1 = ax1.bar(x - width/2, accuracy, width, label='Exactitud Global', color=p["accent_blue"], edgecolor=p["border"])
    rects2 = ax1.bar(x + width/2, f1_spam, width, label='F1-Score en Amenazas', color=p["accent_green"], edgecolor=p["border"])

    ax1.set_title("Comparación de Clasificadores (Holdout N=1.115)", fontsize=11, fontweight='bold', pad=12, color=p["text"])
    ax1.set_xticks(x)
    ax1.set_xticklabels(models, fontsize=8.5, color=p["text"])
    ax1.set_ylim(0, 115)
    ax1.tick_params(colors=p["text_muted"])
    ax1.legend(loc='upper left', facecolor=p["bg"], edgecolor=p["border"], fontsize=8.5, labelcolor=p["text"])
    ax1.grid(axis='y', color=p["border"], linestyle=':', alpha=0.8)

    for rect in rects1:
        h = rect.get_height()
        ax1.text(rect.get_x() + rect.get_width()/2, h + 1.5, f"{h:.1f}%", ha='center', fontsize=8, fontweight='bold', color=p["text"])
    for rect in rects2:
        h = rect.get_height()
        ax1.text(rect.get_x() + rect.get_width()/2, h + 1.5, f"{h:.1f}%", ha='center', fontsize=8, fontweight='bold', color=p["accent_green"])

    ax2.set_facecolor(p["surface"])
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    ax2.axis('off')
    ax2.set_title("Matriz de Confusión en Producción (N = 1.115)", fontsize=11, fontweight='bold', pad=12, color=p["text"])

    tn_box = patches.FancyBboxPatch((1, 5.2), 3.8, 3.8, boxstyle="round,pad=0.3", fc="#1C2E28" if is_dark else "#ECFDF5", ec=p["accent_green"], lw=2)
    ax2.add_patch(tn_box)
    ax2.text(2.9, 7.8, "TN = 959", ha='center', fontsize=13, fontweight='bold', color=p["accent_green"])
    ax2.text(2.9, 6.7, "Mensajes Legítimos", ha='center', fontsize=8.5, color=p["text"])
    ax2.text(2.9, 5.8, "99.28% Entregados", ha='center', fontsize=7.5, color=p["text_muted"])

    fp_box = patches.FancyBboxPatch((5.2, 5.2), 3.8, 3.8, boxstyle="round,pad=0.3", fc="#2A1A10" if is_dark else "#FFFBEB", ec=p["accent_amber"], lw=1.5)
    ax2.add_patch(fp_box)
    ax2.text(7.1, 7.8, "FP = 7", ha='center', fontsize=13, fontweight='bold', color=p["accent_amber"])
    ax2.text(7.1, 6.7, "Falsos Positivos", ha='center', fontsize=8.5, color=p["text"])
    ax2.text(7.1, 5.8, "FPR = 0.72% (< 1% SLA)", ha='center', fontsize=7.5, color=p["accent_green"])

    fn_box = patches.FancyBboxPatch((1, 1), 3.8, 3.8, boxstyle="round,pad=0.3", fc="#3A1017" if is_dark else "#FEF2F2", ec=p["accent_red"], lw=1.5)
    ax2.add_patch(fn_box)
    ax2.text(2.9, 3.6, "FN = 8", ha='center', fontsize=13, fontweight='bold', color=p["accent_red"])
    ax2.text(2.9, 2.5, "Falsos Negativos", ha='center', fontsize=8.5, color=p["text"])
    ax2.text(2.9, 1.6, "FNR = 5.37%", ha='center', fontsize=7.5, color=p["text_muted"])

    tp_box = patches.FancyBboxPatch((5.2, 1), 3.8, 3.8, boxstyle="round,pad=0.3", fc="#1A2544" if is_dark else "#EFF6FF", ec=p["accent_blue"], lw=2)
    ax2.add_patch(tp_box)
    ax2.text(7.1, 3.6, "TP = 141", ha='center', fontsize=13, fontweight='bold', color=p["accent_blue"])
    ax2.text(7.1, 2.5, "Amenazas Bloqueadas", ha='center', fontsize=8.5, color=p["text"])
    ax2.text(7.1, 1.6, "Recall = 94.63%", ha='center', fontsize=7.5, color=p["accent_blue"])

    for ax in (ax1, ax2):
        for spine in ax.spines.values():
            spine.set_color(p["border"])

    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, f"ml_benchmark_cm{suffix}.png")
    fig.savefig(output_path, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
    plt.close(fig)


def generate_xai_feature_weights(is_dark=False):
    p = PALETTE_DARK if is_dark else PALETTE_LIGHT
    suffix = "" if is_dark else "_light"

    fig, ax = plt.subplots(figsize=(11.5, 4.4), dpi=200)
    fig.patch.set_facecolor(p["bg"])
    ax.set_facecolor(p["surface"])

    features = [
        ("TOKEN_URL", 4.82, p["accent_red"]),
        ("urgente", 3.45, p["accent_red"]),
        ("bloque", 3.12, p["accent_red"]),
        ("clave", 2.89, p["accent_red"]),
        ("TOKEN_TEL", 2.65, p["accent_red"]),
        ("verif", 2.41, p["accent_red"]),
        ("banc", 2.22, p["accent_red"]),
        ("gracias", -3.20, p["accent_green"]),
        ("hola", -2.85, p["accent_green"]),
        ("casa", -2.40, p["accent_green"]),
        ("voy", -2.15, p["accent_green"]),
        ("bien", -1.90, p["accent_green"]),
        ("manana", -1.75, p["accent_green"])
    ]

    names = [f[0] for f in features]
    weights = [f[1] for f in features]
    colors = [f[2] for f in features]

    y_pos = np.arange(len(names))
    ax.barh(y_pos, weights, color=colors, height=0.62, edgecolor=p["border"], linewidth=1)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(names, fontsize=8.5, fontweight='bold', color=p["text"])
    ax.tick_params(colors=p["text_muted"])
    ax.set_xlabel("Ponderación del Modelo (Positivo = Alerta de Phishing | Negativo = Mensaje Benigno)", fontsize=9, labelpad=8, color=p["text"])
    ax.set_title("Explicabilidad: Palabras y Entidades Clave en la Decisión", fontsize=11, fontweight='bold', pad=12, color=p["text"])

    ax.axvline(0, color=p["text_muted"], lw=1.2)
    ax.grid(axis='x', color=p["border"], linestyle=':', alpha=0.8)

    ax.text(2.2, 10, "INDICADORES DE PHISHING", color=p["accent_red"], fontweight='bold', fontsize=9,
            bbox=dict(boxstyle="round,pad=0.4", fc=p["surface"], ec=p["accent_red"]))
    ax.text(-2.8, 2, "INDICADORES BENIGNOS", color=p["accent_green"], fontweight='bold', fontsize=9,
            bbox=dict(boxstyle="round,pad=0.4", fc=p["surface"], ec=p["accent_green"]))

    for spine in ax.spines.values():
        spine.set_color(p["border"])

    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, f"xai_feature_weights{suffix}.png")
    fig.savefig(output_path, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
    plt.close(fig)


def main():
    print("[*] Generando únicamente activos visuales activos (Light y Dark)...")
    for is_dark in [False, True]:
        generate_smishing_anatomy(is_dark)
        generate_morphology_benchmark(is_dark)
        generate_ml_benchmark_cm(is_dark)
        generate_xai_feature_weights(is_dark)
    print("[+] 8 activos visuales limpios generados exitosamente.")


if __name__ == "__main__":
    main()
