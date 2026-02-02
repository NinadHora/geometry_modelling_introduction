#!/usr/bin/env python3
"""
============================================================================
TAREFA 1 – Representações Celulares Uniformes e Adaptativas
============================================================================
Disciplina: Modelagem Geométrica – IMPA 2026
Professor: Luiz Henrique de Figueiredo

Conceitos-chave do curso aplicados aqui:
  - Representação implícita de regiões: f(x,y) ≤ 0 define interior,
    f(x,y) = 0 define a fronteira (curva de nível zero).
  - Enumeração espacial uniforme: grade regular, classifica cada célula.
  - Enumeração espacial adaptativa (Quadtree): refina apenas células
    que intersectam a fronteira (classificação mista).
  - Classificação de caixas via Teorema do Valor Intermediário (Bolzano):
    se f assume sinais opostos nos cantos, a fronteira cruza a célula.
============================================================================
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from enum import Enum
import os

# Salva tudo na mesma pasta do script
OUTDIR = os.path.dirname(os.path.abspath(__file__)) or "."


# =========================================================================
# 1. CLASSIFICAÇÃO DE CÉLULAS
# =========================================================================

class Tipo(Enum):
    DENTRO   = "dentro"
    FORA     = "fora"
    FRONTEIRA = "fronteira"


def classificar_celula(f, x0, y0, largura, altura):
    """
    Classifica célula via Teorema do Valor Intermediário (Bolzano, 1817):
    se f assume sinais opostos nos cantos, a fronteira cruza a célula.
    """
    cantos = [(x0, y0), (x0 + largura, y0),
              (x0, y0 + altura), (x0 + largura, y0 + altura)]
    valores = [f(cx, cy) for cx, cy in cantos]
    
    if all(v <= 0 for v in valores):
        return Tipo.DENTRO
    elif all(v > 0 for v in valores):
        return Tipo.FORA
    else:
        return Tipo.FRONTEIRA


# =========================================================================
# 2. ENUMERAÇÃO ESPACIAL UNIFORME
# =========================================================================

def enumeracao_uniforme(f, xmin, ymin, xmax, ymax, nx, ny):
    dx = (xmax - xmin) / nx
    dy = (ymax - ymin) / ny
    celulas = []
    for i in range(nx):
        for j in range(ny):
            x0 = xmin + i * dx
            y0 = ymin + j * dy
            celulas.append((x0, y0, dx, dy, classificar_celula(f, x0, y0, dx, dy)))
    return celulas


# =========================================================================
# 3. ENUMERAÇÃO ESPACIAL ADAPTATIVA (QUADTREE)
# =========================================================================

class NoQuadtree:
    """
    Nó de uma Quadtree (Finkel–Bentley, 1974).
    Refinamento adaptativo (Suffern, 1990):
      - Célula homogênea → folha
      - Célula de fronteira → subdivide em 4
    """
    def __init__(self, x0, y0, largura, altura, profundidade=0):
        self.x0 = x0
        self.y0 = y0
        self.largura = largura
        self.altura = altura
        self.profundidade = profundidade
        self.tipo = None
        self.filhos = None
    
    def subdividir(self, f, prof_max, prof_min=0):
        self.tipo = classificar_celula(f, self.x0, self.y0,
                                        self.largura, self.altura)
        if self.profundidade >= prof_max:
            return
        if self.tipo != Tipo.FRONTEIRA and self.profundidade >= prof_min:
            return
        
        meia_l = self.largura / 2
        meia_a = self.altura / 2
        p = self.profundidade + 1
        self.filhos = [
            NoQuadtree(self.x0, self.y0, meia_l, meia_a, p),
            NoQuadtree(self.x0 + meia_l, self.y0, meia_l, meia_a, p),
            NoQuadtree(self.x0, self.y0 + meia_a, meia_l, meia_a, p),
            NoQuadtree(self.x0 + meia_l, self.y0 + meia_a, meia_l, meia_a, p),
        ]
        for filho in self.filhos:
            filho.subdividir(f, prof_max, prof_min)
    
    def coletar_folhas(self):
        if self.filhos is None:
            return [(self.x0, self.y0, self.largura, self.altura, self.tipo)]
        folhas = []
        for filho in self.filhos:
            folhas.extend(filho.coletar_folhas())
        return folhas


def enumeracao_adaptativa(f, xmin, ymin, xmax, ymax, prof_max=7, prof_min=2):
    raiz = NoQuadtree(xmin, ymin, xmax - xmin, ymax - ymin)
    raiz.subdividir(f, prof_max, prof_min)
    return raiz.coletar_folhas()


# =========================================================================
# 4. FUNÇÕES IMPLÍCITAS
# =========================================================================

def disco(cx, cy, r):
    """f(x,y) = (x-cx)² + (y-cy)² - r²   →  f ≤ 0 = dentro do disco"""
    return lambda x, y: (x - cx)**2 + (y - cy)**2 - r**2


def parabola(c):
    """f(x,y) = x² + c - y   →  f ≤ 0 = região y ≥ x² + c"""
    return lambda x, y: x**2 + c - y


# =========================================================================
# 5. VISUALIZAÇÃO
# =========================================================================

CORES = {
    Tipo.DENTRO:    '#FF6B6B',
    Tipo.FORA:      '#74B9FF',
    Tipo.FRONTEIRA: '#FFEAA7',
}
CORES_BORDA = {
    Tipo.DENTRO:    '#E55039',
    Tipo.FORA:      '#3498DB',
    Tipo.FRONTEIRA: '#F39C12',
}


def desenhar_celulas(ax, celulas, titulo, xmin, ymin, xmax, ymax,
                     f_fronteira=None):
    contagem = {Tipo.DENTRO: 0, Tipo.FORA: 0, Tipo.FRONTEIRA: 0}
    for (x0, y0, w, h, tipo) in celulas:
        contagem[tipo] += 1
        ax.add_patch(patches.Rectangle(
            (x0, y0), w, h, linewidth=0.3,
            edgecolor=CORES_BORDA[tipo], facecolor=CORES[tipo], alpha=0.8))
    
    if f_fronteira is not None:
        xx = np.linspace(xmin, xmax, 400)
        yy = np.linspace(ymin, ymax, 400)
        X, Y = np.meshgrid(xx, yy)
        Z = np.vectorize(f_fronteira)(X, Y)
        ax.contour(X, Y, Z, levels=[0], colors='black', linewidths=1.5)
    
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_aspect('equal')
    total = sum(contagem.values())
    ax.set_title(f"{titulo}\nTotal: {total} | Dentro: {contagem[Tipo.DENTRO]} | "
                 f"Fora: {contagem[Tipo.FORA]} | Fronteira: {contagem[Tipo.FRONTEIRA]}",
                 fontsize=10, fontweight='bold')
    ax.tick_params(labelsize=7)


def gerar_visualizacao(f, nome, xmin, ymin, xmax, ymax,
                       nx=32, ny=32, prof_max=7, prof_min=2,
                       arquivo_saida=None):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle(f"Representações Celulares — {nome}",
                 fontsize=14, fontweight='bold', y=0.98)
    
    celulas_uni = enumeracao_uniforme(f, xmin, ymin, xmax, ymax, nx, ny)
    desenhar_celulas(ax1, celulas_uni, f"Uniforme ({nx}×{ny})",
                     xmin, ymin, xmax, ymax, f)
    
    celulas_adapt = enumeracao_adaptativa(f, xmin, ymin, xmax, ymax,
                                          prof_max, prof_min)
    desenhar_celulas(ax2, celulas_adapt,
                     f"Adaptativa (Quadtree, prof. máx={prof_max})",
                     xmin, ymin, xmax, ymax, f)
    plt.tight_layout()
    if arquivo_saida:
        plt.savefig(arquivo_saida, dpi=200, bbox_inches='tight')
        print(f"  → Salvo: {arquivo_saida}")
    plt.close()


# =========================================================================
# 6. EXECUÇÃO PRINCIPAL
# =========================================================================

def main():
    print("=" * 60)
    print("  TAREFA 1 — Representações Celulares")
    print("  Modelagem Geométrica — IMPA 2026")
    print("=" * 60)
    
    # PARTE A: Disco
    print("\n▸ Parte A: Disco")
    configs = [
        {"cx": 0.3, "cy": 0.4, "r": 0.21, "label": "Disco (enunciado)"},
        {"cx": 0.5, "cy": 0.5, "r": 0.35, "label": "Disco centrado grande"},
        {"cx": 0.15, "cy": 0.15, "r": 0.12, "label": "Disco no canto"},
    ]
    for i, cfg in enumerate(configs):
        f = disco(cfg["cx"], cfg["cy"], cfg["r"])
        nome = f"{cfg['label']} — c=({cfg['cx']},{cfg['cy']}), r={cfg['r']}"
        gerar_visualizacao(f, nome, 0, 0, 1, 1,
                           arquivo_saida=os.path.join(OUTDIR, f"disco_{i+1}.png"))
    
    # PARTE B: Parábola
    print("\n▸ Parte B: Região y ≥ x² + c")
    for c in [0, -1, 1, 0.5]:
        f = parabola(c)
        gerar_visualizacao(f, f"Região y ≥ x² + {c}", -2, -2, 2, 2,
                           arquivo_saida=os.path.join(OUTDIR, f"parabola_c{c}.png"))
    
    # BÔNUS: Evolução do refinamento
    print("\n▸ Bônus: Evolução do refinamento")
    f_disco = disco(0.3, 0.4, 0.21)
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle("Evolução do Refinamento Adaptativo — Disco (0.3, 0.4, r=0.21)",
                 fontsize=14, fontweight='bold')
    for idx, prof in enumerate([1, 2, 3, 4, 5, 7]):
        ax = axes[idx // 3][idx % 3]
        celulas = enumeracao_adaptativa(f_disco, 0, 0, 1, 1,
                                         prof_max=prof, prof_min=min(prof, 2))
        desenhar_celulas(ax, celulas, f"Profundidade máxima = {prof}",
                         0, 0, 1, 1, f_disco)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTDIR, "refinamento_disco.png"), dpi=200, bbox_inches='tight')
    print(f"  → Salvo: refinamento_disco.png")
    plt.close()
    
    print("\n✓ Tarefa 1 concluída!")


if __name__ == "__main__":
    main()
