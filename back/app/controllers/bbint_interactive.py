""""Branch and Bound para Programação Linear Inteira Interativa"""
import json

import numpy as np
import pulp
from flask import Blueprint, jsonify, request

bbint_interactive = Blueprint("bbint_interactive", __name__)

def generate_problem_description(input_data, variable_type="binary"):
    """Generate a description of the problem based on the input data."""
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
        variable_constraints = " and ".join([
            f'x{i+1} >= 0 and x{i+1} ∈ Z' for i in range(num_vars)
        ])
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
    """Solve the linear relaxation of the problem using PuLP."""
    prob = pulp.LpProblem("Relaxation", pulp.LpMinimize)

    num_vars = len(c)
    x = [
        pulp.LpVariable(
            f'x{i+1}',
            lowBound=bounds[i][0],
            upBound=bounds[i][1],
            cat='Continuous'
        ) for i in range(num_vars)
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

def interactive_branch_and_bound(input_data, partial_tree=None, chosen_variable=None):
    """Interactive Branch and Bound for Integer Linear Programming."""
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

    problem_description = generate_problem_description(input_data, variable_type)

    def solve_node(bounds, depth=0, node_id=0, fixed_var=None):
        solution, value = solve_relaxation_pulp(c, a, b, bounds)
        node = {
            "id": node_id,
            "depth": depth,
            "bounds": bounds,
            "solution": [
                round(var, 2) if var else 0
                for var in solution
            ] if solution is not None else None,
            "objective_value": round(
                -value if maximize and value is not None else value, 2
            ) if value is not None else None,
            "fixed_variable": fixed_var,
            "branches": [],
            "podado": False
        }

        if solution is None:
            node["podado"] = True
            node["solution"] = "Unviable Solution"
            return node

        fractional_vars = [
            i for i, val in enumerate(solution) if not np.isclose((val if val else 0) % 1, 0)
        ]

        if not fractional_vars:
            # Solução inteira encontrada
            return node
        elif len(fractional_vars) == 1:
            # Apenas uma variável fracionária, ramificar automaticamente
            fractional_index = fractional_vars[0]
            fractional_value = solution[fractional_index]

            lower_bound = bounds[:]
            upper_bound = bounds[:]

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

            node["branches"].append(
                solve_node(
                    lower_bound,
                    depth + 1,
                    node_id * 2 + 1,
                    f'x{fractional_index + 1} = 0'
                        if variable_type == "binary"
                        else f'x{fractional_index + 1} <= {np.floor(fractional_value)}'
                )
            )
            node["branches"].append(
                solve_node(
                    upper_bound,
                    depth + 1,
                    node_id * 2 + 2,
                    f'x{fractional_index + 1} = 1'
                        if variable_type == "binary"
                        else f'x{fractional_index + 1} >= {np.ceil(fractional_value)}'
                )
            )
        else:
            # Múltiplas variáveis fracionárias
            node["fractional_variables"] = fractional_vars

        return node

    if partial_tree is None:
        tree = solve_node(bounds)
    else:
        tree = partial_tree
        if chosen_variable is None:
            return {
                "description": problem_description,
                "status": "Error",
                "message": "No chosen variable provided",
                "tree": tree
            }

        # Converter chosen_variable para índice
        if isinstance(chosen_variable, str):
            fractional_index = int(chosen_variable.replace('x', '')) - 1
        elif isinstance(chosen_variable, int):
            fractional_index = chosen_variable
        else:
            return {
                "description": problem_description,
                "status": "Error", 
                "message": "Invalid chosen variable format", 
                "tree": tree
            }

        fractional_value = tree["solution"][fractional_index]

        lower_bound = tree["bounds"][:]
        upper_bound = tree["bounds"][:]

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

        tree["branches"] = [
            solve_node(
                lower_bound,
                tree["depth"] + 1,
                tree["id"] * 2 + 1,
                f'x{fractional_index + 1} = 0'
                    if variable_type == "binary"
                    else f'x{fractional_index + 1} <= {np.floor(fractional_value)}'),
            solve_node(
                upper_bound,
                tree["depth"] + 1,
                tree["id"] * 2 + 2,
                f'x{fractional_index + 1} = 1'
                    if variable_type == "binary"
                    else f'x{fractional_index + 1} >= {np.ceil(fractional_value)}'
            )
        ]

    # Encontrar a melhor solução
    best_solution = None
    best_value = float('inf') if not maximize else float('-inf')

    def find_best_solution(node):
        nonlocal best_solution, best_value
        if node["solution"] is not None \
            and isinstance(node["solution"], list) \
                and all(np.isclose(np.array(node["solution"]) % 1, 0)):
            if (not maximize and node["objective_value"] < best_value) \
                or (maximize and node["objective_value"] > best_value):
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
            "objective_value": best_value, 
            "tree": tree
        }
    elif "fractional_variables" in tree:
        return {
            "description": problem_description,
            "status": "Fractional solution",
            "fractional_variables": [f"x{i+1}" for i in tree["fractional_variables"]],
            "tree": tree
        }
    else:
        return {
            "description": problem_description, 
            "status": "Branched", 
            "tree": tree
        }

@bbint_interactive.route('/interactive_branch_and_bound', methods=['POST'])
def interactive_branch_and_bound_endpoint():
    """Branch and Bound para Programação Linear Inteira Interativa."""
    input_data = request.json
    partial_tree = input_data.get('partial_tree')
    chosen_variable = input_data.get('chosen_variable')
    if chosen_variable is not None:
        # Converte 'x1' para 0, 'x2' para 1, etc.
        chosen_variable = int(chosen_variable.replace('x', '')) - 1

    # Remove partial_tree e chosen_variable do input_data antes de convertê-lo para JSON
    input_data_copy = input_data.copy()
    input_data_copy.pop('partial_tree', None)
    input_data_copy.pop('chosen_variable', None)

    result = interactive_branch_and_bound(
        json.dumps(input_data_copy),
        partial_tree,
        chosen_variable
    )
    return jsonify(result)
