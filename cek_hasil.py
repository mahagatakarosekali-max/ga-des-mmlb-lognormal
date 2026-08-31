import pandas as pd


output_file = "hasil_simulasi_ga_des_normal_lognormal.xlsx"


def check_output_file(output_file):
    excel_file = pd.ExcelFile(output_file)

    print("File output berhasil dibaca.")
    print("Daftar sheet output:")

    for sheet_name in excel_file.sheet_names:
        print(f"- {sheet_name}")

    print("\nIsi sheet comparison:")
    comparison = pd.read_excel(output_file, sheet_name="comparison")
    print(comparison.to_string(index=False))


if __name__ == "__main__":
    check_output_file(output_file)