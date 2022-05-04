# Project Order Fulfillment Priority Matching (Team 2)
Metode yang digunakan: Goal Programming

To install:
1. Install packages:
    - pyomo
    - flask
    - pandas
    - openrouteservice
    - python-dotenv
2. Copy `.env.example` as `.env`. Fill in Open Route Service API key.
3. Install CBC Solver in [here](https://www.coin-or.org/download/binary/CoinAll). COIN-OR, version 1.74.
4. Run it.
### Idea: 
1. Empty driver (Dummy ditaruh di driver csv ngikutin jumlah penumpang. 
Kasih distance calculation jadi Infinity, dan feature lainnya jadi paling jelek.
Nanti driver dummy ini akan dipasangkan dengan worst passenger, yang ga akan dpt passenger.

2. Kelebihan driver: ada driver yang tidak dapat penumpang
Sebaliknya yang pertama.

3. Tambahin analisa di hasil
Web nanti kalo mau bisa masukin chart pake chart.js atau highcharts.

4. Banned list (penumpang - driver pair yang ada kondisi banned, sehingga tidak boleh dipasangkan)
Tambah ConstraintList utk Xij == 0