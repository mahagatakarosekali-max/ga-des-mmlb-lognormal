import pandas as pd


output_file = "hasil_simulasi_ga_des_normal_lognormal.xlsx"


def read_history_data(output_file):
    history_normal = pd.read_excel(
        output_file,
        sheet_name="history_normal"
    )

    history_lognormal = pd.read_excel(
        output_file,
        sheet_name="history_lognormal"
    )

    return history_normal, history_lognormal


def calculate_statistics(history_df, scenario_name):
    fitness = history_df["best_fitness"]

    first_fitness = fitness.iloc[0]
    final_fitness = fitness.iloc[-1]
    improvement = first_fitness - final_fitness
    improvement_percentage = (improvement / first_fitness) * 100

    statistics = {
        "scenario": scenario_name,
        "minimum_fitness": fitness.min(),
        "maximum_fitness": fitness.max(),
        "mean_fitness": fitness.mean(),
        "median_fitness": fitness.median(),
        "standard_deviation": fitness.std(),
        "first_generation_fitness": first_fitness,
        "final_generation_fitness": final_fitness,
        "fitness_improvement": improvement,
        "fitness_improvement_percentage": improvement_percentage
    }

    return statistics


def save_statistics(normal_statistics, lognormal_statistics):
    statistics_df = pd.DataFrame([
        normal_statistics,
        lognormal_statistics
    ])

    statistics_df.to_excel(
        "analisis_statistik_bab5.xlsx",
        index=False
    )

    print("Analisis statistik berhasil dibuat.")
    print("File output: analisis_statistik_bab5.xlsx")

    print("\nHasil analisis statistik:")
    print(statistics_df.to_string(index=False))


if __name__ == "__main__":
    history_normal, history_lognormal = read_history_data(output_file)

    normal_statistics = calculate_statistics(
        history_df=history_normal,
        scenario_name="normal"
    )

    lognormal_statistics = calculate_statistics(
        history_df=history_lognormal,
        scenario_name="lognormal"
    )

    save_statistics(
        normal_statistics=normal_statistics,
        lognormal_statistics=lognormal_statistics
    )