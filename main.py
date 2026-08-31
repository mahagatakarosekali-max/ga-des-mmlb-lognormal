import pandas as pd
import numpy as np


file_path = "input_data_tiacci_gunther35_4m_filled.xlsx"
selected_instance = "Gunther_35_4m"
output_file = "data_gunther35_4m_prepared.xlsx"


def read_excel_data(file_path):
    data = {
        "summary": pd.read_excel(file_path, sheet_name="all_instance_summary"),
        "process_time": pd.read_excel(file_path, sheet_name="process_time_all"),
        "precedence": pd.read_excel(file_path, sheet_name="task_precedence_all"),
        "model_product": pd.read_excel(file_path, sheet_name="model_product_all"),
        "assumptions": pd.read_excel(file_path, sheet_name="assumptions_notes")
    }

    return data


def filter_instance_data(data, selected_instance):
    summary_selected = data["summary"][
        data["summary"]["instance_id"] == selected_instance
    ].copy()

    process_time_selected = data["process_time"][
        data["process_time"]["instance_id"] == selected_instance
    ].copy()

    precedence_selected = data["precedence"][
        data["precedence"]["instance_id"] == selected_instance
    ].copy()

    model_product_selected = data["model_product"][
        data["model_product"]["instance_id"] == selected_instance
    ].copy()

    return {
        "summary": summary_selected,
        "process_time": process_time_selected,
        "precedence": precedence_selected,
        "model_product": model_product_selected
    }


def calculate_distribution_parameters(process_time_df):
    df = process_time_df.copy()

    df["mean_time"] = pd.to_numeric(df["mean_time"], errors="coerce").fillna(0)
    df["cv"] = pd.to_numeric(df["cv"], errors="coerce").fillna(0)

    df["std_dev"] = df["cv"] * df["mean_time"]

    df["sigma_ln_2"] = 0.0
    df["mu_ln"] = 0.0

    mask_positive = df["mean_time"] > 0

    df.loc[mask_positive, "sigma_ln_2"] = np.log(
        1 + (
            df.loc[mask_positive, "std_dev"] ** 2
            / df.loc[mask_positive, "mean_time"] ** 2
        )
    )

    df.loc[mask_positive, "mu_ln"] = (
        np.log(df.loc[mask_positive, "mean_time"])
        - 0.5 * df.loc[mask_positive, "sigma_ln_2"]
    )

    return df


def prepare_task_list(process_time_df):
    task_list = (
        process_time_df[["task_id"]]
        .drop_duplicates()
        .sort_values("task_id")
        .reset_index(drop=True)
    )

    return task_list


def prepare_model_list(model_product_df):
    model_list = (
        model_product_df[["model_id", "model_name", "sequence_count", "demand_proportion"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )

    return model_list


def prepare_mps_sequence(model_product_df):
    mps_text = model_product_df["mps_sequence"].dropna().iloc[0]
    mps_sequence = [model.strip() for model in str(mps_text).split(",")]

    mps_df = pd.DataFrame({
        "sequence_position": range(1, len(mps_sequence) + 1),
        "model_id": mps_sequence
    })

    return mps_df


def save_prepared_data(filtered_data, output_file):
    process_time_prepared = calculate_distribution_parameters(
        filtered_data["process_time"]
    )

    task_list = prepare_task_list(process_time_prepared)
    model_list = prepare_model_list(filtered_data["model_product"])
    mps_sequence = prepare_mps_sequence(filtered_data["model_product"])

    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        filtered_data["summary"].to_excel(writer, sheet_name="summary", index=False)
        process_time_prepared.to_excel(writer, sheet_name="process_time", index=False)
        filtered_data["precedence"].to_excel(writer, sheet_name="precedence", index=False)
        filtered_data["model_product"].to_excel(writer, sheet_name="model_product", index=False)
        task_list.to_excel(writer, sheet_name="task_list", index=False)
        model_list.to_excel(writer, sheet_name="model_list", index=False)
        mps_sequence.to_excel(writer, sheet_name="mps_sequence", index=False)

    print("Data Gunther_35_4m berhasil disiapkan.")
    print(f"File hasil persiapan data: {output_file}")

    print("\nRingkasan data:")
    print(f"Jumlah task              : {task_list.shape[0]}")
    print(f"Jumlah model produk      : {model_list.shape[0]}")
    print(f"Panjang minimum part set : {mps_sequence.shape[0]}")

    precedence_without_dash = filtered_data["precedence"][
        filtered_data["precedence"]["predecessor"].astype(str) != "-"
    ]

    print(f"Jumlah hubungan precedence: {precedence_without_dash.shape[0]}")


if __name__ == "__main__":
    data = read_excel_data(file_path)

    filtered_data = filter_instance_data(
        data=data,
        selected_instance=selected_instance
    )

    save_prepared_data(
        filtered_data=filtered_data,
        output_file=output_file
    )