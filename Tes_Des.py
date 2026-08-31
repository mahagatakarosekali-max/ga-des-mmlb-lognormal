import pandas as pd
import numpy as np
import random
import re


prepared_file = "data_gunther35_4m_prepared.xlsx"

number_of_work_centres = 5
maximum_buffer_capacity = 5
simulation_loads = 1000


def read_prepared_data(prepared_file):
    data = {
        "process_time": pd.read_excel(prepared_file, sheet_name="process_time"),
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


def create_process_time_lookup(process_time_df):
    lookup = {}

    for _, row in process_time_df.iterrows():
        key = (
            row["task_id"],
            row["model_id"]
        )

        lookup[key] = {
            "mean_time": row["mean_time"],
            "std_dev": row["std_dev"],
            "sigma_ln_2": row["sigma_ln_2"],
            "mu_ln": row["mu_ln"]
        }

    return lookup


def generate_process_time(parameter, distribution_type):
    mean_time = parameter["mean_time"]

    if mean_time == 0:
        return 0

    if distribution_type == "normal":
        std_dev = parameter["std_dev"]

        process_time = np.random.normal(
            loc=mean_time,
            scale=std_dev
        )

        process_time = max(0, process_time)

    elif distribution_type == "lognormal":
        mu_ln = parameter["mu_ln"]
        sigma_ln = np.sqrt(parameter["sigma_ln_2"])

        process_time = np.random.lognormal(
            mean=mu_ln,
            sigma=sigma_ln
        )

    else:
        raise ValueError("distribution_type harus 'normal' atau 'lognormal'.")

    return process_time


def calculate_work_centre_process_time(
    individual,
    process_time_lookup,
    model_id,
    distribution_type
):
    work_centre_time = {
        work_centre: 0
        for work_centre in range(1, number_of_work_centres + 1)
    }

    for task_id, work_centre in individual["task_allocation"].items():
        key = (
            task_id,
            model_id
        )

        if key not in process_time_lookup:
            continue

        parameter = process_time_lookup[key]

        task_process_time = generate_process_time(
            parameter=parameter,
            distribution_type=distribution_type
        )

        work_centre_time[work_centre] += task_process_time

    return work_centre_time


def create_load_sequence(model_sequence, simulation_loads):
    load_sequence = []

    while len(load_sequence) < simulation_loads:
        for model_id in model_sequence:
            load_sequence.append(model_id)

            if len(load_sequence) >= simulation_loads:
                break

    return load_sequence


def run_des_simulation(
    individual,
    process_time_df,
    distribution_type,
    simulation_loads
):
    process_time_lookup = create_process_time_lookup(process_time_df)

    load_sequence = create_load_sequence(
        model_sequence=individual["model_sequence"],
        simulation_loads=simulation_loads
    )

    start_time = np.zeros(
        (number_of_work_centres, simulation_loads)
    )

    completion_time = np.zeros(
        (number_of_work_centres, simulation_loads)
    )

    departure_time = np.zeros(
        (number_of_work_centres, simulation_loads)
    )

    busy_time = np.zeros(number_of_work_centres)
    blocking_time = np.zeros(number_of_work_centres)
    starvation_time = np.zeros(number_of_work_centres)

    for load_index, model_id in enumerate(load_sequence):
        work_centre_process_time = calculate_work_centre_process_time(
            individual=individual,
            process_time_lookup=process_time_lookup,
            model_id=model_id,
            distribution_type=distribution_type
        )

        for work_centre_index in range(number_of_work_centres):
            work_centre_number = work_centre_index + 1

            if work_centre_index == 0:
                arrival_time = 0
            else:
                arrival_time = departure_time[
                    work_centre_index - 1,
                    load_index
                ]

            if load_index == 0:
                previous_departure_same_wc = 0
            else:
                previous_departure_same_wc = departure_time[
                    work_centre_index,
                    load_index - 1
                ]

            start_time[work_centre_index, load_index] = max(
                arrival_time,
                previous_departure_same_wc
            )

            starvation = max(
                0,
                arrival_time - previous_departure_same_wc
            )

            starvation_time[work_centre_index] += starvation

            processing_time = work_centre_process_time[work_centre_number]

            completion_time[work_centre_index, load_index] = (
                start_time[work_centre_index, load_index]
                + processing_time
            )

            busy_time[work_centre_index] += processing_time

            if work_centre_index == number_of_work_centres - 1:
                departure_time[work_centre_index, load_index] = (
                    completion_time[work_centre_index, load_index]
                )
            else:
                buffer_name = f"B{work_centre_number}"
                buffer_capacity = individual["buffer_allocation"][buffer_name]

                blocking_reference_index = (
                    load_index
                    - buffer_capacity
                    - 1
                )

                if blocking_reference_index >= 0:
                    next_work_centre_departure = departure_time[
                        work_centre_index + 1,
                        blocking_reference_index
                    ]

                    departure_time[work_centre_index, load_index] = max(
                        completion_time[work_centre_index, load_index],
                        next_work_centre_departure
                    )
                else:
                    departure_time[work_centre_index, load_index] = (
                        completion_time[work_centre_index, load_index]
                    )

            blocking = (
                departure_time[work_centre_index, load_index]
                - completion_time[work_centre_index, load_index]
            )

            blocking_time[work_centre_index] += blocking

    simulation_time = departure_time[
        number_of_work_centres - 1,
        simulation_loads - 1
    ]

    total_busy_time = busy_time.sum()
    total_blocking_time = blocking_time.sum()
    total_starvation_time = starvation_time.sum()

    effective_cycle_time = simulation_time / simulation_loads

    line_efficiency = (
        total_busy_time
        / (number_of_work_centres * simulation_time)
    ) * 100

    blocking_percentage = (
        total_blocking_time
        / (number_of_work_centres * simulation_time)
    ) * 100

    starvation_percentage = (
        total_starvation_time
        / (number_of_work_centres * simulation_time)
    ) * 100

    performance = {
        "distribution": distribution_type,
        "simulation_time": simulation_time,
        "effective_cycle_time": effective_cycle_time,
        "line_efficiency": line_efficiency,
        "blocking": blocking_percentage,
        "starvation": starvation_percentage
    }

    return performance


def calculate_fitness(performance, penalty=0):
    effective_cycle_time = performance["effective_cycle_time"]
    line_efficiency = performance["line_efficiency"]
    blocking = performance["blocking"]
    starvation = performance["starvation"]

    fitness_value = (
        effective_cycle_time
        + blocking
        + starvation
        - line_efficiency
        + penalty
    )

    return fitness_value


def show_result(performance, fitness_value):
    print("=" * 70)
    print(f"HASIL EVALUASI DES - {performance['distribution'].upper()}")
    print("=" * 70)

    print(f"Simulation time       : {performance['simulation_time']:.4f}")
    print(f"Effective cycle time  : {performance['effective_cycle_time']:.4f}")
    print(f"Line efficiency (%)   : {performance['line_efficiency']:.4f}")
    print(f"Blocking (%)          : {performance['blocking']:.4f}")
    print(f"Starvation (%)        : {performance['starvation']:.4f}")
    print(f"Fitness Fq            : {fitness_value:.4f}")


if __name__ == "__main__":
    data = read_prepared_data(prepared_file)

    individual = create_individual(data)

    normal_performance = run_des_simulation(
        individual=individual,
        process_time_df=data["process_time"],
        distribution_type="normal",
        simulation_loads=simulation_loads
    )

    normal_fitness = calculate_fitness(
        performance=normal_performance,
        penalty=0
    )

    lognormal_performance = run_des_simulation(
        individual=individual,
        process_time_df=data["process_time"],
        distribution_type="lognormal",
        simulation_loads=simulation_loads
    )

    lognormal_fitness = calculate_fitness(
        performance=lognormal_performance,
        penalty=0
    )

    show_result(
        performance=normal_performance,
        fitness_value=normal_fitness
    )

    print("\n")

    show_result(
        performance=lognormal_performance,
        fitness_value=lognormal_fitness
    )