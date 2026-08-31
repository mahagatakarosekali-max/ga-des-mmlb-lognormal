import pandas as pd


output_file = "hasil_simulasi_ga_des_normal_lognormal.xlsx"


def read_selected_solution(output_file):
    task_allocation = pd.read_excel(
        output_file,
        sheet_name="lognormal_task_allocation"
    )

    buffer_allocation = pd.read_excel(
        output_file,
        sheet_name="lognormal_buffer"
    )

    model_sequence = pd.read_excel(
        output_file,
        sheet_name="lognormal_sequence"
    )

    return task_allocation, buffer_allocation, model_sequence


def show_selected_solution(task_allocation, buffer_allocation, model_sequence):
    print("=" * 70)
    print("SOLUSI TERPILIH MODEL LOGNORMAL")
    print("=" * 70)

    print("\n1. Alokasi task terpilih:")
    print(task_allocation.to_string(index=False))

    print("\n2. Kapasitas buffer terpilih:")
    print(buffer_allocation.to_string(index=False))

    print("\n3. Urutan model produk terpilih:")
    print(model_sequence.to_string(index=False))


if __name__ == "__main__":
    task_allocation, buffer_allocation, model_sequence = read_selected_solution(
        output_file=output_file
    )

    show_selected_solution(
        task_allocation=task_allocation,
        buffer_allocation=buffer_allocation,
        model_sequence=model_sequence
    )