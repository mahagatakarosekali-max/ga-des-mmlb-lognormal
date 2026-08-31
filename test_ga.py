import copy
import random
import pandas as pd

from Tes_Des import (
    read_prepared_data,
    create_individual,
    run_des_simulation,
    calculate_fitness,
    prepared_file,
    simulation_loads
)

from test_feasibility import check_individual_feasibility


population_size = 40
number_of_generations = 100
crossover_rate = 0.8
mutation_rate = 0.2
output_file = "hasil_simulasi_ga_des_normal_lognormal.xlsx"


def create_feasible_individual(data, maximum_attempts=1000):
    attempts = 0

    while attempts < maximum_attempts:
        attempts += 1

        individual = create_individual(data)

        # Membuat variasi urutan model produk
        random.shuffle(individual["model_sequence"])

        is_feasible, violations = check_individual_feasibility(
            individual=individual,
            precedence_df=data["precedence"]
        )

        if is_feasible:
            return individual

    raise RuntimeError("Gagal membentuk individu layak.")


def initialize_population(data, population_size):
    population = []

    while len(population) < population_size:
        individual = create_feasible_individual(data)
        population.append(individual)

    return population


def evaluate_individual(individual, data, distribution_type):
    performance = run_des_simulation(
        individual=individual,
        process_time_df=data["process_time"],
        distribution_type=distribution_type,
        simulation_loads=simulation_loads
    )

    fitness_value = calculate_fitness(
        performance=performance,
        penalty=0
    )

    individual["fitness"] = fitness_value
    individual["performance"] = performance

    return individual


def evaluate_population(population, data, distribution_type):
    evaluated_population = []

    for individual in population:
        evaluated_individual = evaluate_individual(
            individual=individual,
            data=data,
            distribution_type=distribution_type
        )

        evaluated_population.append(evaluated_individual)

    evaluated_population = sorted(
        evaluated_population,
        key=lambda x: x["fitness"]
    )

    return evaluated_population


def select_parent(population):
    tournament_size = 3

    candidates = random.sample(
        population,
        k=min(tournament_size, len(population))
    )

    candidates = sorted(
        candidates,
        key=lambda x: x["fitness"]
    )

    parent = copy.deepcopy(candidates[0])

    return parent


def crossover(parent_1, parent_2, data):
    child = copy.deepcopy(parent_1)

    if random.random() < crossover_rate:
        for task_id in child["task_allocation"].keys():
            if random.random() < 0.5:
                child["task_allocation"][task_id] = parent_2["task_allocation"][task_id]

        for buffer_name in child["buffer_allocation"].keys():
            if random.random() < 0.5:
                child["buffer_allocation"][buffer_name] = parent_2["buffer_allocation"][buffer_name]

        if random.random() < 0.5:
            child["model_sequence"] = parent_2["model_sequence"].copy()

    child["fitness"] = None

    if "performance" in child:
        del child["performance"]

    is_feasible, violations = check_individual_feasibility(
        individual=child,
        precedence_df=data["precedence"]
    )

    if not is_feasible:
        child = create_feasible_individual(data)

    return child


def mutation(individual, data):
    child = copy.deepcopy(individual)

    if random.random() < mutation_rate:
        task_list = list(child["task_allocation"].keys())
        selected_task = random.choice(task_list)

        maximum_work_centre = max(child["task_allocation"].values())

        child["task_allocation"][selected_task] = random.randint(
            1,
            maximum_work_centre
        )

    if random.random() < mutation_rate:
        buffer_list = list(child["buffer_allocation"].keys())
        selected_buffer = random.choice(buffer_list)

        child["buffer_allocation"][selected_buffer] = random.randint(
            1,
            5
        )

    if random.random() < mutation_rate:
        sequence = child["model_sequence"]

        if len(sequence) > 1:
            position_1, position_2 = random.sample(
                range(len(sequence)),
                2
            )

            sequence[position_1], sequence[position_2] = (
                sequence[position_2],
                sequence[position_1]
            )

            child["model_sequence"] = sequence

    child["fitness"] = None

    if "performance" in child:
        del child["performance"]

    is_feasible, violations = check_individual_feasibility(
        individual=child,
        precedence_df=data["precedence"]
    )

    if not is_feasible:
        return individual

    return child


def run_ga(data, distribution_type):
    population = initialize_population(
        data=data,
        population_size=population_size
    )

    history = []

    for generation in range(1, number_of_generations + 1):
        population = evaluate_population(
            population=population,
            data=data,
            distribution_type=distribution_type
        )

        best_individual = population[0]
        best_performance = best_individual["performance"]

        history.append({
            "generation": generation,
            "best_fitness": best_individual["fitness"],
            "effective_cycle_time": best_performance["effective_cycle_time"],
            "line_efficiency": best_performance["line_efficiency"],
            "blocking": best_performance["blocking"],
            "starvation": best_performance["starvation"]
        })

        print(
            f"{distribution_type.upper()} | "
            f"Generasi {generation} | "
            f"Fq terbaik = {best_individual['fitness']:.4f}"
        )

        new_population = [
            copy.deepcopy(best_individual)
        ]

        while len(new_population) < population_size:
            parent_1 = select_parent(population)
            parent_2 = select_parent(population)

            child = crossover(
                parent_1=parent_1,
                parent_2=parent_2,
                data=data
            )

            child = mutation(
                individual=child,
                data=data
            )

            new_population.append(child)

        population = new_population

    population = evaluate_population(
        population=population,
        data=data,
        distribution_type=distribution_type
    )

    best_individual = population[0]
    history_df = pd.DataFrame(history)

    return best_individual, history_df


def task_allocation_to_dataframe(individual):
    rows = []

    for task_id, work_centre in individual["task_allocation"].items():
        rows.append({
            "task_id": task_id,
            "work_centre": work_centre
        })

    return pd.DataFrame(rows)


def buffer_allocation_to_dataframe(individual):
    rows = []

    for buffer_name, capacity in individual["buffer_allocation"].items():
        rows.append({
            "buffer": buffer_name,
            "capacity": capacity
        })

    return pd.DataFrame(rows)


def model_sequence_to_dataframe(individual):
    rows = []

    for position, model_id in enumerate(individual["model_sequence"], start=1):
        rows.append({
            "sequence_position": position,
            "model_id": model_id
        })

    return pd.DataFrame(rows)


def save_ga_result(
    normal_best,
    lognormal_best,
    normal_history,
    lognormal_history,
    output_file
):
    normal_performance = normal_best["performance"]
    lognormal_performance = lognormal_best["performance"]

    comparison = pd.DataFrame([
        {
            "scenario": "normal",
            "fitness_Fq": normal_best["fitness"],
            "effective_cycle_time": normal_performance["effective_cycle_time"],
            "line_efficiency": normal_performance["line_efficiency"],
            "blocking": normal_performance["blocking"],
            "starvation": normal_performance["starvation"]
        },
        {
            "scenario": "lognormal",
            "fitness_Fq": lognormal_best["fitness"],
            "effective_cycle_time": lognormal_performance["effective_cycle_time"],
            "line_efficiency": lognormal_performance["line_efficiency"],
            "blocking": lognormal_performance["blocking"],
            "starvation": lognormal_performance["starvation"]
        }
    ])

    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        comparison.to_excel(writer, sheet_name="comparison", index=False)

        normal_history.to_excel(writer, sheet_name="history_normal", index=False)
        lognormal_history.to_excel(writer, sheet_name="history_lognormal", index=False)

        task_allocation_to_dataframe(normal_best).to_excel(
            writer,
            sheet_name="normal_task_allocation",
            index=False
        )

        buffer_allocation_to_dataframe(normal_best).to_excel(
            writer,
            sheet_name="normal_buffer",
            index=False
        )

        model_sequence_to_dataframe(normal_best).to_excel(
            writer,
            sheet_name="normal_sequence",
            index=False
        )

        task_allocation_to_dataframe(lognormal_best).to_excel(
            writer,
            sheet_name="lognormal_task_allocation",
            index=False
        )

        buffer_allocation_to_dataframe(lognormal_best).to_excel(
            writer,
            sheet_name="lognormal_buffer",
            index=False
        )

        model_sequence_to_dataframe(lognormal_best).to_excel(
            writer,
            sheet_name="lognormal_sequence",
            index=False
        )

    print("\nHasil GA sederhana berhasil disimpan.")
    print(f"File output: {output_file}")


if __name__ == "__main__":
    data = read_prepared_data(prepared_file)

    print("=" * 70)
    print("MENJALANKAN GA-DES SKENARIO NORMAL")
    print("=" * 70)

    normal_best, normal_history = run_ga(
        data=data,
        distribution_type="normal"
    )

    print("\n" + "=" * 70)
    print("MENJALANKAN GA-DES SKENARIO LOGNORMAL")
    print("=" * 70)

    lognormal_best, lognormal_history = run_ga(
        data=data,
        distribution_type="lognormal"
    )

    save_ga_result(
        normal_best=normal_best,
        lognormal_best=lognormal_best,
        normal_history=normal_history,
        lognormal_history=lognormal_history,
        output_file=output_file
    )