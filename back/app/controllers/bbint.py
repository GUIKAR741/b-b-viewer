""""Branch and Bound para Programação Linear Inteira"""
import json

import numpy as np
import pulp
from flask import Blueprint, jsonify, request

bbint = Blueprint("bbint", __name__)

def generate_problem_description(input_data, variable_type="binary"):
    """Gerar a descrição textual do problema."""
    data = json.loads(input_data)
    num_vars = len(data["objective_coeffs"])
    objective_terms = " + ".join(
        [f'{coef}x{i+1}' for i, coef in enumerate(data["objective_coeffs"])]
    )

    # Criar as restrições
    constraints = []
    for row, rhs, op in zip(
            data["constraints_coeffs"],
            data["constraints_rhs"],
            data["constraints_ops"]
        ):
        terms = " + ".join([f'{coef}x{j+1}' for j, coef in enumerate(row)])
        constraints.append(f'{terms} {op} {rhs}')

    # Descrição das variáveis
    if variable_type == "binary":
        variable_constraints = " and ".join([f'x{i+1} ∈ {{0, 1}}' for i in range(num_vars)])
    elif variable_type == "integer":
        variable_constraints = " and ".join([f'x{i+1} ∈ Z' for i in range(num_vars)])
    elif variable_type == "non_negative_integer":
        variable_constraints = " and ".join(
            [f'x{i+1} >= 0 and x{i+1} ∈ Z' for i in range(num_vars)]
        )
    else:
        raise ValueError(
            "Unsupported variable type."
            " Choose between 'binary', 'integer', or 'non_negative_integer'."
        )

    # Montar a descrição como um vetor de linhas
    description_lines = [
        "Integer Linear Programming Problem:",
        "",
        f"Objective: {'Minimize' if not data['maximize'] else 'Maximize'} {objective_terms}",
        "",
        "Subject to restrictions:"
    ]
    description_lines.extend(constraints)
    description_lines.append(f"With {variable_constraints}")

    return description_lines

def solve_relaxation_pulp(c, a, b, bounds):
    """Resolver a relaxação linear do problema."""
    prob = pulp.LpProblem("Relaxation", pulp.LpMinimize)

    num_vars = len(c)
    x = [
        pulp.LpVariable(f'x{i+1}', lowBound=bounds[i][0], upBound=bounds[i][1], cat='Continuous')
        for i in range(num_vars)
    ]

    prob += pulp.lpSum([c[i] * x[i] for i in range(num_vars)])

    for i in range(len(a)):
        prob += (pulp.lpSum([a[i][j] * x[j] for j in range(num_vars)]) <= b[i])

    prob.solve()

    if pulp.LpStatus[prob.status] == "Optimal":
        solution = [pulp.value(x[i]) for i in range(num_vars)]
        value = pulp.value(prob.objective)
        return solution, value
    else:
        return None, None

def branch_and_bound(input_data):
    """Branch and Bound para Programação Linear Inteira."""
    data = json.loads(input_data)
    c = np.array(data["objective_coeffs"])
    maximize = data["maximize"]
    a = np.array(data["constraints_coeffs"])
    b = np.array(data["constraints_rhs"])
    bounds = None

    variable_type = data.get("variable_type", "binary")
    if variable_type == "binary":
        bounds = [(0, 1) for _ in c]
    elif variable_type == "integer":
        bounds = [(None, None) for _ in c]
    elif variable_type == "non_negative_integer":
        bounds = [(0, None) for _ in c]

    if maximize:
        c = -c

    # Gerar a descrição textual do problema
    problem_description = generate_problem_description(input_data, variable_type)

    def build_tree(c, a, b, bounds, depth=0, node_id=0,
                   best_value=float('-inf') if maximize else float('inf'), fixed_var=None
        ):
        solution, value = solve_relaxation_pulp(c, a, b, bounds)
        node = {
            "id": node_id,
            "depth": depth,
            "bounds": bounds,
            "solution": [
                round(var, 2) if var else 0 for var in solution
            ] if solution is not None else None,
            "objective_value": round(
                -value if maximize and value is not None else value, 2
            ) if value is not None else None,
            "fixed_variable": fixed_var,  # Mostrar a variável de ramificação
            "branches": [],
            "podado": False
        }

        if solution is None:
            node["podado"] = True
            node["solution"] = "Solução Inviável"  # Adicionar a solução inviável como outro campo
            return node

        if maximize:
            if value <= best_value:
                node["podado"] = True
                return node
        else:
            if value >= best_value:
                node["podado"] = True
                return node

        if all(np.isclose(np.array(solution) % 1, 0)):
            return node  # Não altera o fixed_variable; mantém a restrição do nó pai

        # Identificando o índice da variável fracionária
        fractional_index = np.argmax(np.abs(np.array(solution) % 1))
        fractional_value = solution[fractional_index]

        lower_bound = bounds[:]
        upper_bound = bounds[:]

        # Alterar os limites com base na variável fracionária
        if variable_type == "binary":
            lower_bound[fractional_index] = (0, 0)
            upper_bound[fractional_index] = (1, 1)
        else:
            lower_bound[fractional_index] = (
                lower_bound[fractional_index][0],
                np.floor(fractional_value)
            )
            upper_bound[fractional_index] = (
                np.ceil(fractional_value),
                upper_bound[fractional_index][1]
            )

        # Ramificar para os nós filhos
        node["branches"].append(
            build_tree(
                c, a, b, lower_bound, depth + 1,
                node_id=node_id * 2 + 1, best_value=best_value,
                fixed_var=f'x{fractional_index + 1} = 0'
                            if variable_type == "binary"
                            else f'x{fractional_index + 1} <= {np.floor(fractional_value)}'
            )
        )
        node["branches"].append(
            build_tree(
                c, a, b, upper_bound, depth + 1,
                node_id=node_id * 2 + 2, best_value=best_value,
                fixed_var=f'x{fractional_index + 1} = 1'
                            if variable_type == "binary"
                            else f'x{fractional_index + 1} >= {np.ceil(fractional_value)}'
            )
        )

        return node

    tree = build_tree(c, a, b, bounds, node_id=0)

    best_solution = None
    best_value = float('inf') if not maximize else float('-inf')

    def find_best_solution(node):
        nonlocal best_solution, best_value
        if node["solution"] is not None \
            and isinstance(node["solution"], list)\
                and all(np.isclose(np.array(node["solution"]) % 1, 0)):
            if node["objective_value"] < best_value \
                if not maximize \
                else node["objective_value"] > best_value:
                best_solution = node["solution"]
                best_value = node["objective_value"]
        for branch in node["branches"]:
            find_best_solution(branch)

    find_best_solution(tree)

    if best_solution is not None:
        return {
            "description": problem_description,
            "status": "Optimal",
            "solution": best_solution,
            "objective_value": best_value, "tree": tree}
    else:
        return {
            "description": problem_description,
            "status":
            "No feasible solution",
            "tree": tree
        }

@bbint.route('/branch_and_bound', methods=['POST'])
def branch_and_bound_endpoint():
    """Branch and Bound para Programação Linear Inteira."""
    input_data = request.json
    result = branch_and_bound(json.dumps(input_data))
    return jsonify(result)
