import concurrent.futures
import multiprocessing
from rqalpha import run


tasks = []
for short_period in range(3, 10, 2):
    for long_period in range(30, 90, 5):
        config = {
            "extra": {
                "context_vars": {
                    "SHORTPERIOD": short_period,
                    "LONGPERIOD": long_period,
                },
                "log_level": "error",
            },
            "base": {
                "matching_type": "current_bar",
                "start_date": "2015-01-01",
                "end_date": "2016-01-01",
                "benchmark": "000001.XSHE",
                "frequency": "1d",

        "accounts": {
            "stock": 100000
        }
            },
            "mod": {
                "sys_progress": {
                    "enabled": True,
                    "show": True,
                },
                "sys_analyser": {
                    "enabled": True,
                    "output_file": "results/out-{short_period}-{long_period}.pkl".format(
                        short_period=short_period,
                        long_period=long_period,
                    )
                },
            },
        }

        tasks.append(config)


def run_bt(config,short_period,long_period):
    import talib

    def init(context):
        context.s1 = '000001.XSHE'

        context.SHORTPERIOD = short_period
        context.LONGPERIOD = long_period

        print('init', short_period, long_period)

    def handle_bar(context, bar_dict):
        prices = history_bars(context.s1, context.LONGPERIOD + 1, '1d', 'close')

        short_avg = talib.SMA(prices, context.SHORTPERIOD)
        long_avg = talib.SMA(prices, context.LONGPERIOD)

        cur_position = context.portfolio.positions[context.s1].quantity
        shares = context.portfolio.cash / bar_dict[context.s1].close

        if short_avg[-1] - long_avg[-1] < 0 and short_avg[-2] - long_avg[-2] > 0 and cur_position > 0:
            order_target_value(context.s1, 0)

        if short_avg[-1] - long_avg[-1] > 0 and short_avg[-2] - long_avg[-2] < 0:
            order_shares(context.s1, shares)


with concurrent.futures.ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
    for task in tasks:
        executor.submit(run_bt, task)