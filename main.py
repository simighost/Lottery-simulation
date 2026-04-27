import logging
import time
from collections import OrderedDict

import numpy as np
import structlog

logging.basicConfig(level=logging.INFO, format="%(message)s")
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.ExceptionPrettyPrinter(),
        structlog.processors.TimeStamper('%H:%M'),
        structlog.dev.ConsoleRenderer(pad_event=30),
    ],
    context_class=OrderedDict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

log = structlog.get_logger()

GENERATED_TICKETS = 10_000_000
MIN_NUMBER = 1
MAX_NUMBER = 49
NUMBERS_PER_TICKET = 6
WINNING_NUMBERS = [1, 2, 3, 4, 5, 6]
TICKET_COST = 7
PRIZE_PERCENTAGE = 80


def generate_tickets(count: int, min_num: int, max_num: int, pick: int) -> np.ndarray:
    pool_size = max_num - min_num + 1
    batch_size = 100_000
    rng = np.random.default_rng()
    chunks = []

    for start in range(0, count, batch_size):
        size = min(batch_size, count - start)
        rand_vals = rng.random((size, pool_size))
        indices = np.argpartition(rand_vals, pick, axis=1)[:, :pick] + min_num
        chunks.append(indices.astype(np.int8))
        if (start + size) % 1_000_000 == 0:
            log.info(f"Generated {start + size:,} / {count:,} tickets")

    return np.vstack(chunks)


def calculate_finances(count: int, ticket_cost: int, prize_pct: int) -> dict:
    prize_per_ticket = ticket_cost * prize_pct / 100
    income = count * ticket_cost
    prize_pool = count * prize_per_ticket
    profit = income - prize_pool
    return {"income": income, "prize_pool": prize_pool, "profit": profit}


def get_prizes(prize_pool: float) -> dict:
    return {
        "total": prize_pool,
        3: prize_pool * 0.05,
        4: prize_pool * 0.10,
        5: prize_pool * 0.25,
        6: prize_pool * 0.60,
    }


def check_tickets(tickets: np.ndarray, winning_numbers: list[int]) -> np.ndarray:
    return np.sum(np.isin(tickets, winning_numbers), axis=1)


def get_winners(matches: np.ndarray, prizes: dict) -> tuple[dict, dict, float, float]:
    winner_stats = {k: int(np.sum(matches == k)) for k in (3, 4, 5, 6)}

    winnings = {
        k: prizes[k] / winner_stats[k] if winner_stats[k] else 0
        for k in (3, 4, 5, 6)
    }

    report = sum(prizes[k] for k in (3, 4, 5, 6) if winner_stats[k] == 0)
    total_winnings = sum(prizes[k] for k in (3, 4, 5, 6) if winner_stats[k] > 0)

    return winner_stats, winnings, report, total_winnings


start_time = time.time()

tickets = generate_tickets(GENERATED_TICKETS, MIN_NUMBER, MAX_NUMBER, NUMBERS_PER_TICKET)
log.info(f"Generated {GENERATED_TICKETS:,} tickets in {time.time() - start_time:.2f}s")

finances = calculate_finances(GENERATED_TICKETS, TICKET_COST, PRIZE_PERCENTAGE)
prizes = get_prizes(finances["prize_pool"])

log.info(f"Total prize pool: {prizes['total']:,.2f}")
log.info(f"Prize for 3 numbers: {prizes[3]:,.2f}")
log.info(f"Prize for 4 numbers: {prizes[4]:,.2f}")
log.info(f"Prize for 5 numbers: {prizes[5]:,.2f}")
log.info(f"Prize for 6 numbers: {prizes[6]:,.2f}")

matches = check_tickets(tickets, WINNING_NUMBERS)
stats, winnings, report, total_winnings = get_winners(matches, prizes)

log.info(f"Winning tickets with 3 numbers: {stats[3]:,} - Prize per winner: {winnings[3]:,.2f}")
log.info(f"Winning tickets with 4 numbers: {stats[4]:,} - Prize per winner: {winnings[4]:,.2f}")
log.info(f"Winning tickets with 5 numbers: {stats[5]:,} - Prize per winner: {winnings[5]:,.2f}")
log.info(f"Winning tickets with 6 numbers: {stats[6]:,} - Prize per winner: {winnings[6]:,.2f}")

log.info(f"Total reported (no winners): {report:,.2f}")
log.info(f"Total winnings paid: {total_winnings:,.2f}")

log.info(f"Total income: {finances['income']:,}")
log.info(f"Total prize pool: {finances['prize_pool']:,.2f}")
log.info(f"Total profit: {finances['profit']:,.2f}")

log.info(f"Total time: {time.time() - start_time:.2f}s")
