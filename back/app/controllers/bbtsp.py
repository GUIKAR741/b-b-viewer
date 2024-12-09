"""Branch and Bound para o problema do Caixeiro Viajante."""
import copy
import random

from flask import Blueprint, jsonify, request
from scipy.optimize import linprog

bbtsp = Blueprint("bbtsp", __name__)

def dfs(d, inicio):
    """Função DFS para realizar caminhamento no grafo."""
    visitado = set()
    pilha = [inicio]
    ciclo = []

    while pilha:
        vertice = pilha.pop()
        if vertice not in visitado:
            ciclo.append(vertice)
            visitado.add(vertice)
            pilha.extend(d[vertice] - visitado)
    return ciclo

def formatar_caminho(caminho):
    """Função para formatar o caminho, incrementando cada cidade em 1"""
    return [int(cidade + 1) for cidade in caminho]

def criar_no(z_atual, h, c, caminho, tam_matriz, pai_id=None):
    """Função auxiliar para criar um novo nó na árvore de busca."""
    return {
        "objective_value": z_atual,
        "branches": [],
        "depth": h,
        "podado": False,
        "fixed_variable": None,
        "id": c,
        "bounds": [],
        "solution": formatar_caminho(caminho),
        "parent_id": pai_id,
        "solucao_completa": len(caminho) == tam_matriz
    }

# Função principal do Branch and Bound
def branch_and_bound(l, h=0, pai_id=None):
    """Branch and Bound para o problema do Caixeiro Viajante."""
    global pilha_matriz, pilha_arestas, resultado_otimo, z_otimo, cont, nos_por_nivel
    cont = cont + 1
    c = int(cont)
    resultado_otimo = []
    children = []

    # Definindo os limites das variáveis
    x_bounds = []
    t = (0, None)
    for i in range(len(l)):
        for j in range(len(l[0])):
            x_bounds.insert(i, t)

    # Coeficientes da função objetivo
    c_obj = []
    for i in l:
        for j in i:
            c_obj.append(j)

    # Coeficientes da matriz de restrições
    a = []
    count = 0
    # Parte 1: soma das saídas
    for i in range(len(l)):
        linha = []
        for j in range(len(l)):
            for k in range(len(l)):
                if j == count:
                    linha.append(1)
                else:
                    linha.append(0)
        count = count + 1
        a.append(linha)
    # Parte 2: soma das entradas
    count = 0
    for i in range(len(l)):
        linha = []
        for j in range(len(l)):
            for k in range(len(l)):
                if k == count:
                    linha.append(1)
                else:
                    linha.append(0)
        count = count + 1
        a.append(linha)

    # Vetor de igualdade da matriz de restrições
    b = []
    for i in range(2 * len(l)):
        b.append(1)

    # Resolvendo o problema de relaxação linear
    results = linprog(c=c_obj, A_eq=a, b_eq=b, bounds=x_bounds, method='highs-ds')

    # Verificando o resultado
    if results.status == 0:  # problema possui solução
        z_atual = results.fun

        # Monta a matriz com o resultado atual
        resultado_atual = []
        k = 0
        for i in range(len(l)):
            linha = []
            for j in range(len(l)):
                if results.x[k] == 1:
                    linha.append(1)
                else:
                    linha.append(0)
                k = k + 1
            resultado_atual.append(linha)

        # Montando a entrada para dfs
        keylist = [i for i in range(len(l))]
        d = {i: None for i in keylist}

        # Incluindo os valores das linhas
        k = 0
        for i in range(len(l)):
            linha = []
            for j in range(len(l)):
                if results.x[k] == 1:
                    linha.append(j)
                k = k + 1
            d[i] = set(linha)

        # Realiza o caminhamento em profundidade
        v = random.randrange(len(l))
        caminho = dfs(d, v)

        # Criação do nó atual
        no_atual = criar_no(z_atual, h, c, caminho, len(l), pai_id)
        if h not in nos_por_nivel:
            nos_por_nivel[h] = []
        nos_por_nivel[h].append(no_atual)

        # Verifica a conexidade do resultado
        if (len(caminho) != len(l)) and (z_atual < z_otimo):
            lista = []

            # Gera uma lista com as arestas da componente conexa visitada pelo dfs
            for i, k in enumerate(caminho):
                if i != (len(caminho) - 1):
                    elemento = (k, caminho[i + 1])
                    lista.append(elemento)
                else:
                    elemento = (k, caminho[0])
                    lista.append(elemento)

            if lista:  # Só adiciona se a lista não estiver vazia
                pilha_arestas.append(lista)

        if (len(caminho) != len(l)) and (z_atual >= z_otimo):
            no_atual["podado"] = True
            if pilha_matriz and len(pilha_matriz) > 0:
                pilha_matriz.pop()

        if len(caminho) == len(l):
            if z_atual < z_otimo:
                z_otimo = z_atual
                resultado_otimo = resultado_atual
            if pilha_matriz and len(pilha_matriz) > 0:
                pilha_matriz.pop()
    else:  # problema infeasible
        no_atual = criar_no(float('inf'), h, c, [], len(l), [], pai_id)
        no_atual["podado"] = True
        if h not in nos_por_nivel:
            nos_por_nivel[h] = []
        nos_por_nivel[h].append(no_atual)
        if pilha_matriz and len(pilha_matriz) > 0:
            pilha_matriz.pop()

    if pilha_matriz and len(pilha_matriz) > 0:
        pos_ultima_aresta = len(pilha_arestas) - 1 if pilha_arestas else -1

        if pilha_arestas and len(pilha_arestas) > 0 \
            and pos_ultima_aresta >= 0 and pilha_arestas[pos_ultima_aresta]:
            lista = pilha_arestas.pop()
            if lista:  # Verifica se a lista não está vazia
                arestas_restantes = lista.copy()
                aresta = lista.pop()
                pilha_arestas.append(lista)
                if len(pilha_matriz) >= 1:  # Garantindo que existe pelo menos um elemento
                    ultima_matriz = copy.deepcopy(pilha_matriz[-1])
                    ultima_matriz[aresta[0]][aresta[1]] = 9999
                    pilha_matriz.append(ultima_matriz)

                    # Criamos ramos paralelos para cada aresta restante
                    matriz_base = None
                    if len(pilha_matriz) >= 2:
                        matriz_base = copy.deepcopy(pilha_matriz[-2])

                    if matriz_base is not None:  # Só cria ramos paralelos se tiver matriz base
                        for aresta_alt in arestas_restantes:
                            matriz_alt = copy.deepcopy(matriz_base)
                            matriz_alt[aresta_alt[0]][aresta_alt[1]] = 9999
                            child = branch_and_bound(matriz_alt, h + 1, c)
                            if child:
                                children.append(child)

                    # Exploramos o ramo atual
                    child = branch_and_bound(ultima_matriz, h + 1, c)
                    if child:
                        children.append(child)
        else:
            # Remove pilhas vazias com segurança
            while (pilha_arestas and len(pilha_arestas) > 0 and
                   pilha_matriz and len(pilha_matriz) > 0):
                if not pilha_arestas[-1] or len(pilha_arestas[-1]) == 0:
                    pilha_matriz.pop()
                    pilha_arestas.pop()
                else:
                    break

            if (pilha_matriz and len(pilha_matriz) > 0 and
                pilha_arestas and len(pilha_arestas) > 0 and
                pilha_arestas[-1] and len(pilha_arestas[-1]) > 0):

                lista = pilha_arestas.pop()
                if lista:  # Verificação adicional de segurança
                    arestas_restantes = lista.copy()
                    aresta = lista.pop()
                    pilha_arestas.append(lista)

                    if len(pilha_matriz) >= 1:  # Garantindo que existe pelo menos um elemento
                        ultima_matriz = copy.deepcopy(pilha_matriz[-1])
                        ultima_matriz[aresta[0]][aresta[1]] = 9999
                        pilha_matriz.append(ultima_matriz)

                        # Similar ao bloco anterior, criamos ramos paralelos
                        matriz_base = None
                        if len(pilha_matriz) >= 2:
                            matriz_base = copy.deepcopy(pilha_matriz[-2])

                        if matriz_base is not None:  # Só cria ramos paralelos se tiver matriz base
                            for aresta_alt in arestas_restantes:
                                matriz_alt = copy.deepcopy(matriz_base)
                                matriz_alt[aresta_alt[0]][aresta_alt[1]] = 9999
                                child = branch_and_bound(matriz_alt, h + 1, c)
                                if child:
                                    children.append(child)

                        # Exploramos o ramo atual
                        child = branch_and_bound(ultima_matriz, h + 1, c)
                        if child:
                            children.append(child)

    no_atual["branches"] = children
    return no_atual

@bbtsp.route('/tsp/branch_and_bound', methods=['POST'])
def solve_tsp():
    """Branch and Bound para o problema do Caixeiro Viajante."""
    data = request.json
    matriz = data.get("matriz")

    global cont, pilha_matriz, pilha_arestas, resultado_otimo, z_otimo, nos_por_nivel
    cont = 0
    pilha_matriz = [matriz]
    pilha_arestas = []
    nos_por_nivel = {}
    resultado_otimo = []
    z_otimo = 99999999999

    resultado = branch_and_bound(matriz)

    return jsonify({
        "description": ["Branch and Bound for the Traveling Salesman Problem"],
        "objective_value": z_otimo,
        "solution": resultado_otimo,
        "status": "Optimal",
        "tree": resultado
    })
