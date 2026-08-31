import pandas as pd
import matplotlib.pyplot as plt


output_file = "hasil_simulasi_ga_des_normal_lognormal.xlsx"


def read_result_data(output_file):
    comparison = pd.read_excel(output_file, sheet_name="comparison")
    history_normal = pd.read_excel(output_file, sheet_name="history_normal")
    history_lognormal = pd.read_excel(output_file, sheet_name="history_lognormal")

    return comparison, history_normal, history_lognormal


def create_normal_convergence_chart(history_normal):
    plt.figure(figsize=(8, 5))
    plt.plot(
        history_normal["generation"],
        history_normal["best_fitness"],
        marker="o"
    )

    plt.title("Grafik Konvergensi Genetic Algorithm Model Normal")
    plt.xlabel("Generasi")
    plt.ylabel("Nilai Fitness (Fq) Terbaik")
    plt.grid(True)
    plt.tight_layout()

    plt.savefig("grafik_konvergensi_normal.png", dpi=300)
    plt.close()


def create_lognormal_convergence_chart(history_lognormal):
    plt.figure(figsize=(8, 5))
    plt.plot(
        history_lognormal["generation"],
        history_lognormal["best_fitness"],
        marker="o"
    )

    plt.title("Grafik Konvergensi Genetic Algorithm Model Lognormal")
    plt.xlabel("Generasi")
    plt.ylabel("Nilai Fitness (Fq) Terbaik")
    plt.grid(True)
    plt.tight_layout()

    plt.savefig("grafik_konvergensi_lognormal.png", dpi=300)
    plt.close()


def create_combined_convergence_chart(history_normal, history_lognormal):
    plt.figure(figsize=(8, 5))

    plt.plot(
        history_normal["generation"],
        history_normal["best_fitness"],
        marker="o",
        label="Normal"
    )

    plt.plot(
        history_lognormal["generation"],
        history_lognormal["best_fitness"],
        marker="o",
        label="Lognormal"
    )

    plt.title("Perbandingan Konvergensi Genetic Algorithm")
    plt.xlabel("Generasi")
    plt.ylabel("Nilai Fitness (Fq) Terbaik")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plt.savefig("grafik_perbandingan_konvergensi.png", dpi=300)
    plt.close()


def create_performance_comparison_chart(comparison):
    indicators = [
        "fitness_Fq",
        "effective_cycle_time",
        "line_efficiency",
        "blocking",
        "starvation"
    ]

    comparison_plot = comparison.set_index("scenario")[indicators].T

    plt.figure(figsize=(9, 5))
    comparison_plot.plot(kind="bar")

    plt.title("Perbandingan Performansi Model Normal dan Lognormal")
    plt.xlabel("Indikator Performansi")
    plt.ylabel("Nilai")
    plt.xticks(rotation=30, ha="right")
    plt.grid(axis="y")
    plt.tight_layout()

    plt.savefig("grafik_perbandingan_performansi.png", dpi=300)
    plt.close()


if __name__ == "__main__":
    comparison, history_normal, history_lognormal = read_result_data(output_file)

    create_normal_convergence_chart(history_normal)
    create_lognormal_convergence_chart(history_lognormal)
    create_combined_convergence_chart(history_normal, history_lognormal)
    create_performance_comparison_chart(comparison)

    print("Grafik BAB V berhasil dibuat:")
    print("- grafik_konvergensi_normal.png")
    print("- grafik_konvergensi_lognormal.png")
    print("- grafik_perbandingan_konvergensi.png")
    print("- grafik_perbandingan_performansi.png")