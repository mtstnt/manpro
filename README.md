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
1. Kelebihan client/driver
2. Banned list (penumpang - driver pair yang ada kondisi banned, sehingga tidak boleh dipasangkan)
Tambah ConstraintList utk Xij == 0

### Contributors
1. [Matthew Sutanto](https://github.com/mtstnt)
2. [Felicia Tania](https://github.com/feliciatania)
3. [Krisna Bei](https://github.com/krisnabei28)
4. Michael Alverian
5. Andy
6. Marselus Richard