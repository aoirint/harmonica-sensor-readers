import os
import sqlite3
from datetime import datetime as dt
from datetime import timedelta
import dateutil.parser as dtparser
from pytz import timezone

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker

from pathlib import Path
import logging
logger = logging.getLogger(__name__)


def _getData(cur, start, end):
    rows = []
    for row in cur.execute('SELECT * FROM sensor'):
        tsString = row[6]
        ts = dtparser.parse(tsString)
        if start <= ts and ts < end:
            rows.append(row + (ts, ))
    return rows

def _draw(cur, date, fp):
    start = date ; end = date + timedelta(days=1)
    x = [] ; y = []
    for row in _getData(cur, start, end):
        ts = row[7] ; val = row[5]
        if val is None:
            continue

        ts_n = ts.replace(tzinfo=None)

        # #define VOLT 5.0
        # #define V_OFFSET 0.6
        # #define DEGREE_PER_VOLT 0.01
        #
        # float v0 = (float)temperatureRaw / 1023 * VOLT;
        # float temperature = (v0 - V_OFFSET) / DEGREE_PER_VOLT;
        #val = ((raw/1023*5.0)-0.6)/0.01
        #val -= 1.5 # hand-fix

        x.append(ts_n) ; y.append(val)

    start_n = start.replace(tzinfo=None)
    end_n = end.replace(tzinfo=None)
    date_string = start_n.date().isoformat()

    plt.clf()
    fig, ax = plt.subplots()
    ax.set_xlim(start_n, end_n)
    ax.set_ylim(0, 40)
    ax.plot(x, y)
#    ax.plot([ start, end ], [ 10 * 10**9, ] * 2)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, pos: '%.2f C' % (y, )))
    fig.suptitle(f'MHZ19 Temperature {date_string}')
    fig.savefig(fp)

    plt.close()


def draw_days(
    cur,
    output_dir: Path,
    tz: str,
    days: int = 1,
):
    now = dt.now(timezone(tz))
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)

    output_dir.mkdir(parents=True, exist_ok=True)

    for dd in range(days):
        date = today - timedelta(days=dd)
        date_string = date.replace(tzinfo=None).date().isoformat()
        logger.info(f'MHZ19 Temperature {date_string}')

        path = output_dir / f'{date_string}.png'
        _draw(cur, date, path)
