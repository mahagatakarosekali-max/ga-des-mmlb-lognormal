import pandas as pd
import random


prepared_file = "data_gunther35_4m_prepared.xlsx"

number_of_work_centres = 5
maximum_buffer_capacity = 5


def read_prepared_data(prepared_file):
    data = {
        "task_list": pd.read_excel(prepared_file, sheet_name="task_list"),
        "precedence": pd.read_excel(prepared_file, sheet_name="precedence"),
        "model_list": pd.read_excel(prepared_file, sheet_name="model_list"),
        "mps_sequence": pd.read_excel(prepared_file, sheet_name="mps_sequence")
    }

    return data


def create_task_order(task_list):
    task_order = task_list["task_id"].tolist()

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


def show_individual(individual):
    print("=" * 70)
    print("INDIVIDU GA BERHASIL DIBENTUK")
    print("=" * 70)

    print("\n1. Task order:")
    print(individual["task_order"])

    print("\n2. Task allocation:")
    for task_id, work_centre in individual["task_allocation"].items():
        print(f"{task_id} -> WC{work_centre}")

    print("\n3. Buffer allocation:")
    for buffer_name, capacity in individual["buffer_allocation"].items():
        print(f"{buffer_name} = {capacity}")

    print("\n4. Model sequence:")
    print(individual["model_sequence"])

    print("\n5. Fitness:")
    print(individual["fitness"])


if __name__ == "__main__":
    data = read_prepared_data(prepared_file)

    individual = create_individual(data)

    show_individual(individual)