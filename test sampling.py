import pandas as pd
import numpy as np


prepared_file = "data_gunther35_4m_prepared.xlsx"
output_file = "cek_sampling_waktu_proses.xlsx"


def read_prepared_process_time(prepared_file):
    process_time = pd.read_excel(
        prepared_file,
        sheet_name="process_time"
    )

    return process_time


def generate_normal_time(mean_time, std_dev):
    if mean_time == 0:
        return 0

    process_time = np.random.normal(
        loc=mean_time,
        scale=std_dev
    )

    process_time = max(0, process_time)

    return process_time


def generate_lognormal_time(mean_time, mu_ln, sigma_ln_2):
    if mean_time == 0:
        return 0

    sigma_ln = np.sqrt(sigma_ln_2)

    process_time = np.random.lognormal(
        mean=mu_ln,
        sigma=sigma_ln
    )

    return process_time


def test_process_time_sampling(process_time_df):
    df = process_time_df.copy()

    normal_samples = []
    lognormal_samples = []

    for _, row in df.iterrows():
        mean_time = row["mean_time"]
        std_dev = row["std_dev"]
        sigma_ln_2 = row["sigma_ln_2"]
        mu_ln = row["mu_ln"]

        normal_time = generate_normal_time(
            mean_time=mean_time,
            std_dev=std_dev
        )

        lognormal_time = generate_lognormal_time(
            mean_time=mean_time,
            mu_ln=mu_ln,
            sigma_ln_2=sigma_ln_2
        )

        normal_samples.append(normal_time)
        lognormal_samples.append(lognormal_time)

    df["normal_sample"] = normal_samples
    df["lognormal_sample"] = lognormal_samples

    return df


def save_sampling_result(result_df, output_file):
    result_df.to_excel(
        output_file,
        index=False
    )

    print("Sampling waktu proses berhasil dibuat.")
    print(f"File hasil sampling: {output_file}")

    print("\n5 baris pertama hasil sampling:")
    print(result_df.head().to_string(index=False))

    print("\nPemeriksaan nilai minimum:")
    print(f"Minimum normal sample    : {result_df['normal_sample'].min()}")
    print(f"Minimum lognormal sample : {result_df['lognormal_sample'].min()}")


if __name__ == "__main__":
    process_time = read_prepared_process_time(prepared_file)

    sampling_result = test_process_time_sampling(
        process_time_df=process_time
    )

    save_sampling_result(
        result_df=sampling_result,
        output_file=output_file
    )