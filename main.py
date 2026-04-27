import random
import logging
import time

import numpy as np
import structlog
from collections import OrderedDict


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


class Lottery:
    __instances = []
    __instances_started = 0
    __min_limit = 1
    __max_limit = 100
    __generated_number = 10
    __default_name = "list"
    __winning_numbers = []
    __ticket_cost = 7
    __prize_percentage = 80
    __income = 0
    __prize_pool = 0
    __profit = 0

    def __init__(self, name=None, min_limit=None, max_limit=None, generated_number=None):
        self.min_limit = min_limit if min_limit else Lottery.__min_limit
        self.max_limit = max_limit if max_limit else Lottery.__max_limit
        self.generated_number = generated_number if generated_number else Lottery.__generated_number
        self.name = name if name else Lottery.__default_name

        self.initialize()

        # log.info(f"Instance {Lottery.__instances_started} started")
        # def generate_numbers(min_limit, max_limit, generated_number):
        self.numbers = self.generate_numbers(self.min_limit, self.max_limit, self.generated_number)

        self.checked = False
        self.winning_numbers = []

    def check_ticket(self):
        if self.checked:
            return

        self.winning_numbers = set(self.numbers).intersection(Lottery.__winning_numbers)
        self.checked = True

    def initialize(self):
        Lottery.__instances.append(self)
        Lottery.__instances_started += 1
        Lottery.__income += Lottery.__ticket_cost

        prize_money = Lottery.__ticket_cost * Lottery.__prize_percentage / 100

        Lottery.__prize_pool += prize_money
        Lottery.__profit += Lottery.__ticket_cost - prize_money

    @classmethod
    def set_winning_numbers(cls, custom_numbers):
        cls.__winning_numbers = custom_numbers

    @classmethod
    def generate_winning_numbers(cls, min_limit, max_limit, generated_number):
        cls.__winning_numbers = cls.generate_numbers(min_limit, max_limit, generated_number)

    @classmethod
    def check_tickets(cls):
        batch_size = 10000
        idx = 0
        for instance in cls.__instances:
            idx += 1
            if idx % batch_size == 0:
                log.info(f"Checking tickets {idx} / {len(cls.__instances)}")
            instance.check_ticket()

    @classmethod
    def get_prizes(cls) -> dict[str, float]:
        return {
            "total_price": cls.__prize_pool,
            3: cls.__prize_pool * 0.05,
            4: cls.__prize_pool * 0.10,
            5: cls.__prize_pool * 0.25,
            6: cls.__prize_pool * 0.60,
        }

    @classmethod
    def get_winners(cls) -> tuple[dict[int, int], dict[int, int], int, int]:
        prizes = cls.get_prizes()

        winner_stats = {
            3: 0,
            4: 0,
            5: 0,
            6: 0,
        }

        for instance in cls.__instances:
            winning_numbers_length = len(instance.winning_numbers)

            if winning_numbers_length > 2:
                # log.info(f"Instance {instance.name} has {len(instance.winning_numbers)} winning numbers {instance.winning_numbers}")
                winner_stats[winning_numbers_length] += 1

        winnings = {
            3: prizes[3] / winner_stats[3] if winner_stats[3] else 0,
            4: prizes[4] / winner_stats[4] if winner_stats[4] else 0,
            5: prizes[5] / winner_stats[5] if winner_stats[5] else 0,
            6: prizes[6] / winner_stats[6] if winner_stats[6] else 0,
        }

        report = 0
        total_winnings = 0

        if winner_stats[3] == 0:
            report += prizes[3]
        else:
            total_winnings += prizes[3]

        if winner_stats[4] == 0:
            report += prizes[4]
        else:
            total_winnings += prizes[4]

        if winner_stats[5] == 0:
            report += prizes[5]
        else:
            total_winnings += prizes[5]

        if winner_stats[6] == 0:
            report += prizes[6]
        else:
            total_winnings += prizes[6]

        return winner_stats, winnings, report, total_winnings

    @staticmethod
    def generate_numbers(min_limit: int, max_limit: int, generated_number) -> list[int]:
        return np.random.choice(
            range(1, 49),
            6,
            replace=False
        ).tolist()

        # return random.sample(range(min_limit, max_limit + 1), generated_number)

generated_tickets = 1000000
default_min_limit = 1
default_max_limit = 49
default_generated_number = 6
default_start_name = "ticket_number"
winning_numbers = [1, 2, 3, 4, 5, 6]

start_time = time.time()
batch_size = 10000
idx = 0

for _ in range(generated_tickets):
    idx += 1
    Lottery(name=default_start_name, min_limit=default_min_limit, max_limit=default_max_limit, generated_number=default_generated_number)
    if idx % batch_size == 0:
        log.info(f"Checking tickets {idx} / {generated_tickets}")
log.info(f"Total time taken for generate_tickets: {time.time() - start_time}")

Lottery.set_winning_numbers(winning_numbers)
# Lottery.generate_winning_numbers(default_min_limit, default_max_limit, default_generated_number)

get_prizes = Lottery.get_prizes()

log.info(f"Total prize pool: {get_prizes['total_price']}")
log.info(f"Prize for 3 numbers: {get_prizes[3]}")
log.info(f"Prize for 4 numbers: {get_prizes[4]}")
log.info(f"Prize for 5 numbers: {get_prizes[5]}")
log.info(f"Prize for 6 numbers: {get_prizes[6]}")

Lottery.check_tickets()

stats, winnings, report, total_winnings = Lottery.get_winners()

log.info(f"Winning tickets with 3 numbers: {stats[3]} - Prize: {winnings[3]}")
log.info(f"Winning tickets with 4 numbers: {stats[4]} - Prize: {winnings[4]}")
log.info(f"Winning tickets with 5 numbers: {stats[5]} - Prize: {winnings[5]}")
log.info(f"Winning tickets with 6 numbers: {stats[6]} - Prize: {winnings[6]}")

log.info(f"Total report: {report}")
log.info(f"Total winnings: {total_winnings}")

log.info(f"Total income: {Lottery._Lottery__income}")
log.info(f"Total prize pool: {Lottery._Lottery__prize_pool}")
log.info(f"Total profit pool: {Lottery._Lottery__profit}")

log.info(f"Total time: {time.time() - start_time}")
