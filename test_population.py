import pandas as pd
import random
import re


prepared_file = "data_gunther35_4m_prepared.xlsx"

number_of_work_centres = 5
maximum_buffer_capacity = 5
population_size = 10
maximum_attempts = 1000


def read_prepared_data(prepared_file):
    data = {
        "task_list": pd.read_excel(prepared_file, sheet_name="task_list"),
        "precedence": pd.read_excel(prepared_file, sheet_name="precedence"),
        "mps_sequence": pd.read_excel(prepared_file, sheet_name="mps_sequence")
    }

    return data


def get_task_number(task_id):
    number = re.findall(r"\d+", str(task_id))

    if number:
        return int(number[0])

    return 0


def create_task_order(task_list):
    task_df = task_list.copy()
    task_df["task_number"] = task_df["task_id"].apply(get_task_number)

    task_order = (
        task_df
        .sort_values("task_number")
        ["task_id"]
        .tolist()
    )

    return task_order


def create_task_allocation(task_order, number_of_work_centres):
    task_allocation = {}

    current_work_centre = 1

    for task_id in task_order:
        task_allocation[task_id] = current_work_centre

        if current_work_centre < number_of_work_centres:
            move_probability = random.random()

            if move_probability < 0.25:
                current_work_centre += 1

    return task_allocation


def create_buffer_allocation(number_of_work_centres, maximum_buffer_capacity):
    buffer_allocation = {}

    for work_centre in range(1, number_of_work_centres):
        buffer_name = f"B{work_centre}"

        buffer_allocation[buffer_name] = random.randint(
            1,
            maximum_buffer_capacity
        )

    return buffer_allocation


def create_model_sequence(mps_sequence_df):
    model_sequence = mps_sequence_df["model_id"].tolist()

    return model_sequence


def create_individual(data):
    task_order = create_task_order(data["task_list"])

    task_allocation = create_task_allocation(
        task_order=task_order,
        number_of_work_centres=number_of_work_centres
    )

    buffer_allocation = create_buffer_allocation(
        number_of_work_centres=number_of_work_centres,
        maximum_buffer_capacity=maximum_buffer_capacity
    )

    model_sequence = create_model_sequence(
        mps_sequence_df=data["mps_sequence"]
    )

    individual = {
        "task_order": task_order,
        "task_allocation": task_allocation,
        "buffer_allocation": buffer_allocation,
        "model_sequence": model_sequence,
        "fitness": None
    }

    return individual


def split_predecessor(predecessor):
    predecessor_text = str(predecessor).strip()

    if predecessor_text == "-" or predecessor_text == "" or predecessor_text.lower() == "nan":
        return []

    predecessors = re.split(r"[,;]", predecessor_text)

    predecessors = [
        pred.strip()
        for pred in predecessors
        if pred.strip() != ""
    ]

    return predecessors


def check_task_order_feasibility(individual, precedence_df):
    task_order = individual["task_order"]

    task_position = {
        task_id: position
        for position, task_id in enumerate(task_order)
    }

    violations = []

    for _, row in precedence_df.iterrows():
        task_id = row["task_id"]
        predecessor_list = split_predecessor(row["predecessor"])

        for predecessor in predecessor_list:
            if predecessor not in task_position or task_id not in task_position:
                violations.append(
                    f"Task {task_id} atau predecessor {predecessor} tidak ditemukan."
                )
                continue

            if task_position[predecessor] > task_position[task_id]:
                violations.append(
                    f"Urutan task melanggar precedence: {predecessor} muncul setelah {task_id}."
                )

    return violations


def check_task_allocation_feasibility(individual, precedence_df):
    task_allocation = individual["task_allocation"]

    violations = []

    for _, row in precedence_df.iterrows():
        task_id = row["task_id"]
        predecessor_list = split_predecessor(row["predecessor"])

        for predecessor in predecessor_list:
            if predecessor not in task_allocation or task_id not in task_allocation:
                violations.append(
                    f"Alokasi task {task_id} atau predecessor {predecessor} tidak ditemukan."
                )
                continue

            predecessor_wc = task_allocation[predecessor]
            task_wc = task_allocation[task_id]

            if predecessor_wc > task_wc:
                violations.append(
                    f"Alokasi melanggar precedence: {predecessor} di WC{predecessor_wc}, "
                    f"tetapi {task_id} di WC{task_wc}."
                )

    return violations


def check_buffer_feasibility(individual):
    buffer_allocation = individual["buffer_allocation"]

    violations = []

    for buffer_name, capacity in buffer_allocation.items():
        if capacity < 0 or capacity > maximum_buffer_capacity:
            violations.append(
                f"{buffer_name} memiliki kapasitas {capacity}, di luar batas."
            )

    return violations


def check_individual_feasibility(individual, precedence_df):
    violations = []

    violations.extend(
        check_task_order_feasibility(
            individual=individual,
            precedence_df=precedence_df
        )
    )

    violations.extend(
        check_task_allocation_feasibility(
            individual=individual,
            precedence_df=precedence_df
        )
    )

    violations.extend(
        check_buffer_feasibility(
            individual=individual
        )
    )

    is_feasible = len(violations) == 0

    return is_feasible, violations


def initialize_population(data, population_size, maximum_attempts):
    population = []
    attempts = 0

    while len(population) < population_size and attempts < maximum_attempts:
        attempts += 1

        individual = create_individual(data)

        is_feasible, violations = check_individual_feasibility(
            individual=individual,
            precedence_df=data["precedence"]
        )

        if is_feasible:
            population.append(individual)

    if len(population) < population_size:
        print("Populasi belum mencapai ukuran yang diinginkan.")
        print(f"Jumlah individu layak: {len(population)}")
        print(f"Jumlah percobaan: {attempts}")

    return population, attempts


def show_population(population, attempts):
    print("=" * 70)
    print("POPULASI AWAL GA")
    print("=" * 70)

    print(f"Jumlah individu layak terbentuk : {len(population)}")
    print(f"Jumlah percobaan pembentukan    : {attempts}")

    for index, individual in enumerate(population, start=1):
        print("\n" + "-" * 70)
        print(f"Individu {index}")

        print("Task allocation:")
        for task_id, work_centre in individual["task_allocation"].items():
            print(f"{task_id} -> WC{work_centre}")

        print("Buffer allocation:")
        for buffer_name, capacity in individual["buffer_allocation"].items():
            print(f"{buffer_name} = {capacity}")

        print("Model sequence:")
        print(individual["model_sequence"])

        print("Fitness:")
        print(individual["fitness"])


if __name__ == "__main__":
    data = read_prepared_data(prepared_file)

    population, attempts = initialize_population(
        data=data,
        population_size=population_size,
        maximum_attempts=maximum_attempts
    )

    show_population(
        population=population,
        attempts=attempts
    )