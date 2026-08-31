# GA-DES Mixed-Model Line Balancing Lognormal

Repositori ini berisi kode program, data input, dan hasil uji komputasi untuk penelitian tugas akhir berjudul:

**Pengembangan Model Mixed-Model Line Balancing dengan Waktu Proses Berdistribusi Lognormal Menggunakan Genetic Algorithm dan Discrete Event Simulation**

## Deskripsi

Program ini digunakan untuk menyelesaikan permasalahan mixed-model line balancing dengan waktu proses stokastik. Metode yang digunakan adalah integrasi Genetic Algorithm dan Discrete Event Simulation.

Penelitian ini membandingkan dua skenario distribusi waktu proses, yaitu distribusi normal dan distribusi lognormal.

## Data

Data yang digunakan adalah data Gunther_35_4m yang diolah dari Tiacci (2024). Data terdiri dari 35 task dan 4 model produk.

## Isi Repositori

Repositori ini memuat:

1. Kode program GA-DES
2. Data input program
3. Hasil uji komputasi model normal
4. Hasil uji komputasi model lognormal
5. Hasil analisis statistik
6. Grafik konvergensi
7. Grafik perbandingan performansi
8. Solusi terpilih model lognormal

## Output Program

Output utama program meliputi:

1. Fitness
2. Effective cycle time
3. Line efficiency
4. Blocking
5. Starvation
6. Alokasi task
7. Kapasitas buffer
8. Urutan model produk

## Cara Menjalankan Program

Program dijalankan menggunakan Python dengan library pandas, numpy, openpyxl, dan matplotlib.

File utama untuk menjalankan uji komputasi adalah:

`test_ga.py`

File untuk membuat grafik BAB V adalah:

`buat_grafik_bab5.py`

File untuk membuat analisis statistik BAB V adalah:

`analisis_statistik_bab5.py`

## Sumber Data

Data penelitian diolah dari:

Tiacci, L. (2024). Combining balancing, sequencing and buffer allocation decisions to improve the efficiency of mixed-model asynchronous assembly lines. Computers & Industrial Engineering, 194, 110357.
