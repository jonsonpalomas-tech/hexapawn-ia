"""
Simula o treino IA vs IA do Hexapawn fora do Colab (sem interface)
e gera a curva de aprendizado usada no README.

Mesma lógica dos notebooks: cada IA guarda "caixinhas" com as jogadas
possíveis para cada estado do tabuleiro. Quando vence, reforça as
jogadas que usou; quando perde, remove a última jogada que fez.

Uso:
    python analise/simular_treino.py
"""
import random
import matplotlib.pyplot as plt

N_TREINOS = 200     # quantos treinos independentes
N_PARTIDAS = 150    # partidas por treino


def buscar_movimentos(tab, cor):
    lista = []
    direcao = 1 if cor == 'W' else -1
    inimigo = 'B' if cor == 'W' else 'W'
    for r in range(3):
        for c in range(3):
            if tab[r][c] == cor:
                nr = r + direcao
                if 0 <= nr < 3:
                    if tab[nr][c] == ' ':
                        lista.append(((r, c), (nr, c)))
                    for dc in (-1, 1):
                        nc = c + dc
                        if 0 <= nc < 3 and tab[nr][nc] == inimigo:
                            lista.append(((r, c), (nr, nc)))
    return lista


def checar_fim(tab):
    if any(tab[2][c] == 'W' for c in range(3)):
        return 'V'
    if any(tab[0][c] == 'B' for c in range(3)):
        return 'A'
    if not buscar_movimentos(tab, 'W'):
        return 'A'
    if not buscar_movimentos(tab, 'B'):
        return 'V'
    return None


def treinar(n_partidas, seed):
    random.seed(seed)
    caixinhas = {'W': {}, 'B': {}}
    vencedores = []
    for _ in range(n_partidas):
        tab = [['W'] * 3, [' '] * 3, ['B'] * 3]
        historico = {'W': [], 'B': []}
        vez = 'W'
        while True:
            fim = checar_fim(tab)
            if fim:
                break
            estado = str(tab)
            caixa = caixinhas[vez]
            if estado not in caixa:
                caixa[estado] = buscar_movimentos(tab, vez)
            if not caixa[estado]:          # caixinha vazia: desiste
                fim = 'A' if vez == 'W' else 'V'
                break
            mov = random.choice(caixa[estado])
            historico[vez].append((estado, mov))
            (r1, c1), (r2, c2) = mov
            tab[r1][c1] = ' '
            tab[r2][c2] = vez
            vez = 'B' if vez == 'W' else 'W'

        for cor, rotulo in (('W', 'V'), ('B', 'A')):
            if not historico[cor]:
                continue
            if fim == rotulo:
                for estado, mov in historico[cor]:
                    caixinhas[cor][estado].append(mov)
            else:
                estado, mov = historico[cor][-1]
                if mov in caixinhas[cor][estado]:
                    caixinhas[cor][estado].remove(mov)
        vencedores.append(fim)
    return vencedores


if __name__ == '__main__':
    resultados = [treinar(N_PARTIDAS, s) for s in range(N_TREINOS)]

    taxa_azul = [
        100 * sum(r[i] == 'A' for r in resultados) / N_TREINOS
        for i in range(N_PARTIDAS)
    ]
    ultima_derrota = sorted(
        max([i for i, v in enumerate(r) if v == 'V'], default=-1) + 1
        for r in resultados
    )
    print(f"A IA Azul para de perder, em mediana, após a partida {ultima_derrota[N_TREINOS // 2]}")
    print(f"No pior caso, após a partida {ultima_derrota[-1]}")

    plt.rcParams['font.family'] = 'DejaVu Sans'
    fig, ax = plt.subplots(figsize=(9, 4), dpi=150)
    ax.plot(range(1, N_PARTIDAS + 1), taxa_azul, color='#2B2F36', linewidth=2)
    ax.set_title(f'Vitórias da IA Azul ao longo do treino (média de {N_TREINOS} treinos)',
                 fontsize=11, loc='left', color='#1A1A1A')
    ax.set_xlabel('Partida', fontsize=9, color='#555555')
    ax.set_ylabel('Treinos em que o Azul venceu (%)', fontsize=9, color='#555555')
    ax.set_ylim(40, 102)
    ax.set_xlim(1, N_PARTIDAS)
    ax.grid(axis='y', color='#E5E5E5', linewidth=0.8)
    for lado in ('top', 'right'):
        ax.spines[lado].set_visible(False)
    for lado in ('left', 'bottom'):
        ax.spines[lado].set_color('#BBBBBB')
    ax.tick_params(colors='#555555', labelsize=8)
    plt.tight_layout()
    plt.savefig('imagens/curva_aprendizado.png')
