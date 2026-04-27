# Lottery Simulation

A Python lottery simulation that generates random lottery tickets, compares them against winning numbers, and calculates prize distribution, total income, prize pool, and profit.

## What it does

This project simulates a lottery system where:

- Each ticket costs `7`
- `80%` of ticket revenue goes into the prize pool
- `20%` is kept as profit
- Tickets contain 6 unique numbers
- Winning numbers are compared against every generated ticket
- Prizes are distributed based on matching 3, 4, 5, or 6 numbers

## Prize distribution

The prize pool is split as follows:

| Matches | Prize Pool Share |
|---|---:|
| 3 numbers | 5% |
| 4 numbers | 10% |
| 5 numbers | 25% |
| 6 numbers | 60% |

If there are no winners in a category, that amount is reported separately.

## Project structure

```text
.
├── main.py
└── README.md
