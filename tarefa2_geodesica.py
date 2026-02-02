#!/usr/bin/env python3
"""
============================================================================
TAREFA 2 – Esfera Geodésica via Subdivisão de Faces Triangulares
============================================================================
Disciplina: Modelagem Geométrica – IMPA 2026
Professor: Luiz Henrique de Figueiredo

Conceitos-chave:
  - Representação por fronteira (B-rep): malha de triângulos.
  - Subdivisão de triângulos: cada triângulo → 4 subtriângulos.
  - Projeção na esfera unitária: normalização dos vértices.
  - Tabela hash para unificação de vértices (evita duplicatas).
  - Formato OBJ: representação padrão de modelos 3D.
============================================================================
"""

import numpy as np
import math
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import os

# Salva tudo na mesma pasta do script
OUTDIR = os.path.dirname(os.path.abspath(__file__)) or "."


# =========================================================================
# 1. SÓLIDOS PLATÔNICOS
# =========================================================================

def tetraedro():
    a = 1.0 / 3.0
    b = math.sqrt(8.0 / 9.0)
    c = math.sqrt(2.0 / 9.0)
    d = math.sqrt(2.0 / 3.0)
    vertices = [np.array([0, 0, 1]), np.array([c, d, -a]),
                np.array([c, -d, -a]), np.array([-b, 0, -a])]
    vertices = [v / np.linalg.norm(v) for v in vertices]
    faces = [(0, 1, 2), (0, 2, 3), (0, 3, 1), (1, 3, 2)]
    return vertices, faces


def octaedro():
    vertices = [np.array([1,0,0]), np.array([-1,0,0]), np.array([0,1,0]),
                np.array([0,-1,0]), np.array([0,0,1]), np.array([0,0,-1])]
    faces = [(4,0,2),(4,2,1),(4,1,3),(4,3,0),(5,2,0),(5,1,2),(5,3,1),(5,0,3)]
    return vertices, faces


def icosaedro():
    """Dados do enunciado, normalizados para esfera unitária."""
    vr = [np.array([0,0.30901699437495,-0.5]), np.array([0.30901699437495,0.5,0]),
          np.array([-0.30901699437495,0.5,0]), np.array([0,0.30901699437495,0.5]),
          np.array([0,-0.30901699437495,0.5]), np.array([-0.5,0,0.30901699437495]),
          np.array([0.5,0,0.30901699437495]), np.array([0,-0.30901699437495,-0.5]),
          np.array([0.5,0,-0.30901699437495]), np.array([-0.5,0,-0.30901699437495]),
          np.array([0.30901699437495,-0.5,0]), np.array([-0.30901699437495,-0.5,0])]
    vertices = [v / np.linalg.norm(v) for v in vr]
    faces = [(0,2,1),(3,1,2),(3,5,4),(3,4,6),(0,8,7),(0,7,9),(4,11,10),(7,10,11),
             (2,9,5),(11,5,9),(1,6,8),(10,8,6),(3,2,5),(3,6,1),(0,9,2),(0,1,8),
             (7,11,9),(7,8,10),(4,5,11),(4,10,6)]
    return vertices, faces


# =========================================================================
# 2. TABELA HASH PARA UNIFICAÇÃO DE VÉRTICES
# =========================================================================

class TabelaVertices:
    """
    Tabela hash: coordenadas arredondadas como chave.
    Garante que arestas compartilhadas geram o MESMO vértice.
    """
    def __init__(self, precisao=8):
        self.precisao = precisao
        self.hash_para_indice = {}
        self.vertices = []
    
    def _chave(self, v):
        return (round(v[0], self.precisao),
                round(v[1], self.precisao),
                round(v[2], self.precisao))
    
    def adicionar(self, v):
        chave = self._chave(v)
        if chave in self.hash_para_indice:
            return self.hash_para_indice[chave]
        indice = len(self.vertices)
        self.vertices.append(np.array(v))
        self.hash_para_indice[chave] = indice
        return indice
    
    def carregar_iniciais(self, vertices_iniciais):
        return [self.adicionar(v) for v in vertices_iniciais]


# =========================================================================
# 3. SUBDIVISÃO + PROJEÇÃO NA ESFERA
# =========================================================================

def subdividir_e_projetar(tabela, faces, n_niveis=1):
    """
    Cada triângulo ABC → 4 subtriângulos (ADF, DBE, FEC, DEF)
    onde D, E, F são pontos médios projetados na esfera.
    """
    faces_atuais = list(faces)
    for nivel in range(n_niveis):
        novas_faces = []
        for (i_a, i_b, i_c) in faces_atuais:
            A = tabela.vertices[i_a]
            B = tabela.vertices[i_b]
            C = tabela.vertices[i_c]
            
            D = (A + B) / 2.0; D = D / np.linalg.norm(D)
            E = (B + C) / 2.0; E = E / np.linalg.norm(E)
            F = (A + C) / 2.0; F = F / np.linalg.norm(F)
            
            i_d = tabela.adicionar(D)
            i_e = tabela.adicionar(E)
            i_f = tabela.adicionar(F)
            
            novas_faces.extend([
                (i_a, i_d, i_f), (i_d, i_b, i_e),
                (i_f, i_e, i_c), (i_d, i_e, i_f)
            ])
        faces_atuais = novas_faces
        print(f"    Nível {nivel + 1}: {len(tabela.vertices)} vértices, "
              f"{len(faces_atuais)} faces")
    return faces_atuais


# =========================================================================
# 4. EXPORTAÇÃO OBJ
# =========================================================================

def exportar_obj(vertices, faces, arquivo, comentario=""):
    with open(arquivo, 'w') as f:
        f.write(f"# Esfera Geodesica\n")
        if comentario:
            f.write(f"# {comentario}\n")
        f.write(f"# Vertices: {len(vertices)}, Faces: {len(faces)}\n#\n")
        for v in vertices:
            f.write(f"v {v[0]:.10f} {v[1]:.10f} {v[2]:.10f}\n")
        f.write(f"\n")
        for (a, b, c) in faces:
            f.write(f"f {a + 1} {b + 1} {c + 1}\n")
    print(f"    → OBJ salvo: {arquivo}")


# =========================================================================
# 5. VISUALIZAÇÃO 3D
# =========================================================================

def visualizar_esfera(vertices, faces, titulo, arquivo_png=None):
    fig = plt.figure(figsize=(14, 6))
    for idx, (elev, azim) in enumerate([(25, 45), (25, 135)]):
        ax = fig.add_subplot(1, 2, idx + 1, projection='3d')
        polys = [[vertices[a], vertices[b], vertices[c]] for a, b, c in faces]
        col = Poly3DCollection(polys, alpha=0.6)
        col.set_facecolor('#3498DB')
        col.set_edgecolor('#2C3E50')
        col.set_linewidth(0.3)
        ax.add_collection3d(col)
        ax.set_xlim([-1.1, 1.1]); ax.set_ylim([-1.1, 1.1]); ax.set_zlim([-1.1, 1.1])
        ax.tick_params(labelsize=6)
        ax.view_init(elev=elev, azim=azim)
    fig.suptitle(f"{titulo}\n{len(vertices)} vértices, {len(faces)} faces",
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    if arquivo_png:
        plt.savefig(arquivo_png, dpi=200, bbox_inches='tight')
        print(f"    → PNG salvo: {arquivo_png}")
    plt.close()


def verificar_esfera(vertices, faces):
    normas = [np.linalg.norm(v) for v in vertices]
    erro_max = max(abs(n - 1.0) for n in normas)
    V = len(vertices); F = len(faces); E = F * 3 // 2
    areas = []
    for (a, b, c) in faces:
        v0, v1, v2 = np.array(vertices[a]), np.array(vertices[b]), np.array(vertices[c])
        areas.append(0.5 * np.linalg.norm(np.cross(v1 - v0, v2 - v0)))
    area_total = sum(areas)
    print(f"    ✓ Euler V-E+F: {V}-{E}+{F} = {V - E + F} (esperado: 2)")
    print(f"    ✓ Erro norma: {erro_max:.2e}")
    print(f"    ✓ Área: {area_total:.4f} (esfera: {4*math.pi:.4f}, "
          f"erro: {abs(area_total-4*math.pi)/(4*math.pi)*100:.2f}%)")
    print(f"    ✓ Razão áreas: {max(areas)/min(areas):.2f}")


# =========================================================================
# 6. EXECUÇÃO PRINCIPAL
# =========================================================================

def main():
    print("=" * 60)
    print("  TAREFA 2 — Esfera Geodésica")
    print("  Modelagem Geométrica — IMPA 2026")
    print("=" * 60)
    
    solidos = {
        "Tetraedro": (tetraedro, 5),
        "Octaedro": (octaedro, 4),
        "Icosaedro": (icosaedro, 3),
    }
    
    for nome, (gerar, n_niveis) in solidos.items():
        print(f"\n▸ {nome} ({n_niveis} níveis)")
        vertices_init, faces_init = gerar()
        print(f"  Inicial: {len(vertices_init)} v, {len(faces_init)} f")
        
        tabela = TabelaVertices()
        tabela.carregar_iniciais(vertices_init)
        faces_final = subdividir_e_projetar(tabela, faces_init, n_niveis)
        
        verificar_esfera(tabela.vertices, faces_final)
        exportar_obj(tabela.vertices, faces_final,
                     os.path.join(OUTDIR, f"esfera_{nome.lower()}.obj"),
                     f"a partir de {nome}, {n_niveis} niveis")
        visualizar_esfera(tabela.vertices, faces_final,
                         f"Esfera Geodésica — {nome} ({n_niveis} subdivisões)",
                         os.path.join(OUTDIR, f"esfera_{nome.lower()}.png"))
    
    # Comparação
    print(f"\n▸ Comparação (3 sólidos, 3 níveis)")
    fig = plt.figure(figsize=(15, 5))
    cores = ['#E74C3C', '#27AE60', '#3498DB']
    for idx, (nome, (gerar, _)) in enumerate(solidos.items()):
        vi, fi = gerar()
        tab = TabelaVertices(); tab.carregar_iniciais(vi)
        ff = subdividir_e_projetar(tab, fi, 3)
        ax = fig.add_subplot(1, 3, idx + 1, projection='3d')
        polys = [[tab.vertices[a], tab.vertices[b], tab.vertices[c]] for a, b, c in ff]
        col = Poly3DCollection(polys, alpha=0.7)
        col.set_facecolor(cores[idx]); col.set_edgecolor('#2C3E50'); col.set_linewidth(0.2)
        ax.add_collection3d(col)
        ax.set_xlim([-1.1,1.1]); ax.set_ylim([-1.1,1.1]); ax.set_zlim([-1.1,1.1])
        ax.set_title(f"{nome}\n{len(tab.vertices)} v, {len(ff)} f",
                     fontsize=11, fontweight='bold')
        ax.tick_params(labelsize=6); ax.view_init(elev=20, azim=45)
    fig.suptitle("Comparação: Esferas Geodésicas (3 níveis)",
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTDIR, "comparacao_solidos.png"), dpi=200, bbox_inches='tight')
    plt.close()
    
    print("\n✓ Tarefa 2 concluída!")


if __name__ == "__main__":
    main()
