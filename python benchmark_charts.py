import matplotlib.pyplot as plt
import numpy as np

# 12 workers: melhor que 8, mas ganho marginal (saturação suave)
# 8 workers: 26.80s → speedup 4.41x
# 12 workers: 22.50s → speedup 4.85x (melhor, mas ganho pequeno vs 8)
WORKERS = [1, 2, 4, 8, 12]
TIMES   = [126.60, 70.70, 40.52, 26.80, 22.50]
SPEEDUP = [TIMES[0] / t for t in TIMES]
EFFICIENCY = [s / w * 100 for s, w in zip(SPEEDUP, WORKERS)]

PALETTE = {
    "blue":    "#2a78d6",
    "green":   "#1baf7a",
    "amber":   "#eda100",
    "red":     "#e34948",
    "surface": "#f7f7f5",
    "border":  "#e1e0d9",
    "text":    "#0b0b0b",
    "muted":   "#898781",
}

WORKER_LABELS = ["Serial\n(1)", "2", "4", "8", "12"]

plt.rcParams.update({
    "font.family":       "sans-serif",
    "font.size":         12,
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "axes.grid":         True,
    "grid.color":        PALETTE["border"],
    "grid.linewidth":    0.8,
    "grid.linestyle":    "-",
    "axes.axisbelow":    True,
    "figure.facecolor":  PALETTE["surface"],
    "axes.facecolor":    PALETTE["surface"],
    "axes.edgecolor":    PALETTE["border"],
    "xtick.color":       PALETTE["muted"],
    "ytick.color":       PALETTE["muted"],
    "axes.labelcolor":   PALETTE["text"],
    "text.color":        PALETTE["text"],
})

fig, axes = plt.subplots(1, 3, figsize=(16, 5.5))
fig.suptitle(
    "Análise de Desempenho — Processamento Paralelo de Avaliações",
    fontsize=15, fontweight="normal", color=PALETTE["text"], y=1.01
)
fig.patch.set_facecolor(PALETTE["surface"])

BAR_W = 0.55
x = np.arange(len(WORKERS))

# ── Gráfico 1: Tempo de execução ─────────────────────────────────────────────
ax1 = axes[0]
bar_colors = [PALETTE["blue"]] * len(WORKERS)
min_idx = TIMES.index(min(TIMES))
bar_colors[min_idx] = PALETTE["green"]   # 12 workers = menor tempo = verde

bars = ax1.bar(x, TIMES, width=BAR_W, color=bar_colors, linewidth=0, zorder=2)

for bar, val in zip(bars, TIMES):
    ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 2,
             f"{val:.2f}s", ha="center", va="bottom",
             fontsize=10.5, color=PALETTE["text"])

ax1.set_xticks(x)
ax1.set_xticklabels(WORKER_LABELS, fontsize=11)
ax1.set_xlabel("Workers", fontsize=11)
ax1.set_ylabel("Tempo de execução (s)", fontsize=11)
ax1.set_title("Tempo de execução", fontsize=13, fontweight="normal", pad=10)
ax1.set_ylim(0, max(TIMES) * 1.22)

# ── Gráfico 2: Speedup ───────────────────────────────────────────────────────
ax2 = axes[1]
# Linha ideal calculada com base no NÚMERO REAL de workers (eixo linear),
# depois mapeada de volta para as posições x (que não são igualmente espaçadas).
# Isso garante que a linha ideal seja uma reta y = x de fato.
ideal_speedup = [float(w) for w in WORKERS]

# Para a reta ficar visualmente correta, plotamos a linha ideal usando o
# próprio valor de WORKERS no eixo X numérico (não os índices categóricos),
# mantendo os pontos reais nas posições categóricas via twin axis.
ax2b = ax2.twiny()
ax2b.plot(WORKERS, ideal_speedup, linestyle="--", color=PALETTE["muted"],
          linewidth=1.4, label="Speedup ideal", zorder=2)
ax2b.set_xlim(WORKERS[0], WORKERS[-1])
ax2b.set_xticks([])  # eixo auxiliar invisível, só serve para a reta ficar correta

ax2.plot(x, SPEEDUP, color=PALETTE["blue"], linewidth=2.2,
         marker="o", markersize=8, zorder=3, label="Speedup real")
ax2.fill_between(x, SPEEDUP, 0, alpha=0.08, color=PALETTE["blue"])

peak_idx = SPEEDUP.index(max(SPEEDUP))
ax2.annotate(f"  ×{SPEEDUP[peak_idx]:.2f}",
             xy=(x[peak_idx], SPEEDUP[peak_idx]),
             fontsize=10.5, color=PALETTE["green"], va="bottom")

ax2.set_xticks(x)
ax2.set_xticklabels(WORKER_LABELS, fontsize=11)
ax2.set_xlabel("Workers", fontsize=11)
ax2.set_ylabel("Speedup (×)", fontsize=11)
ax2.set_title("Speedup", fontsize=13, fontweight="normal", pad=10)
ax2.set_ylim(0, max(ideal_speedup) * 1.1)

# Combina as legendas dos dois eixos (principal + auxiliar) em uma só caixa
handles1, labels1 = ax2.get_legend_handles_labels()
handles2, labels2 = ax2b.get_legend_handles_labels()
ax2.legend(handles2 + handles1, labels2 + labels1, fontsize=10, frameon=False)

# ── Gráfico 3: Eficiência paralela ───────────────────────────────────────────
ax3 = axes[2]
eff_colors = []
for eff in EFFICIENCY:
    if eff >= 75:
        eff_colors.append(PALETTE["green"])
    elif eff >= 45:
        eff_colors.append(PALETTE["amber"])
    else:
        eff_colors.append(PALETTE["red"])

bars3 = ax3.bar(x, EFFICIENCY, width=BAR_W, color=eff_colors, linewidth=0, zorder=2)

for bar, val in zip(bars3, EFFICIENCY):
    ax3.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1.2,
             f"{val:.0f}%", ha="center", va="bottom",
             fontsize=10.5, color=PALETTE["text"])

ax3.axhline(100, linestyle="--", color=PALETTE["muted"],
            linewidth=1.2, label="Eficiência ideal (100%)", zorder=2)
ax3.set_xticks(x)
ax3.set_xticklabels(WORKER_LABELS, fontsize=11)
ax3.set_xlabel("Workers", fontsize=11)
ax3.set_ylabel("Eficiência (%)", fontsize=11)
ax3.set_title("Eficiência paralela", fontsize=13, fontweight="normal", pad=10)
ax3.set_ylim(0, 120)
ax3.legend(fontsize=10, frameon=False)

# ── Legenda global ────────────────────────────────────────────────────────────
legend_items = [
    (PALETTE["green"], "Melhor resultado"),
    (PALETTE["amber"], "Desempenho moderado"),
    (PALETTE["blue"],  "Demais configurações"),
]
handles = [plt.Rectangle((0, 0), 1, 1, color=c, linewidth=0) for c, _ in legend_items]
labels  = [lbl for _, lbl in legend_items]
fig.legend(handles, labels, loc="lower center", ncol=3,
           fontsize=10, frameon=False, bbox_to_anchor=(0.5, -0.07))

plt.tight_layout(pad=2.0)
plt.savefig("/mnt/user-data/outputs/benchmark_speedup.png", dpi=150, bbox_inches="tight",
            facecolor=PALETTE["surface"])
plt.show()
print("Gráfico salvo em: benchmark_speedup.png")