import logging
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import dateutil.parser as dtparser
import matplotlib
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from pytz import timezone

matplotlib.use("Agg")
logger = logging.getLogger(__name__)


def _getData(cur: sqlite3.Cursor, start: datetime, end: datetime) -> list[Any]:
    rows = []
    for row in cur.execute("SELECT * FROM sensor"):
        tsString = row[6]
        ts = dtparser.parse(tsString)
        if start <= ts and ts < end:
            rows.append(row + (ts,))
    return rows


def _draw(cur: sqlite3.Cursor, date: datetime, fp: Path) -> None:
    start = date
    end = date + timedelta(days=1)
    x = []
    y = []
    for row in _getData(cur, start, end):
        ts = row[7]
        val = row[5]
        if val is None:
            continue

        ts_n = ts.replace(tzinfo=None)

        # #define VOLT 5.0
        # #define V_OFFSET 0.6
        # #define DEGREE_PER_VOLT 0.01
        #
        # float v0 = (float)temperatureRaw / 1023 * VOLT;
        # float temperature = (v0 - V_OFFSET) / DEGREE_PER_VOLT;
        # val = ((raw/1023*5.0)-0.6)/0.01
        # val -= 1.5 # hand-fix

        x.append(ts_n)
        y.append(val)

    start_n = start.replace(tzinfo=None)
    end_n = end.replace(tzinfo=None)
    date_string = start_n.date().isoformat()

    plt.clf()
    fig, ax = plt.subplots()
    ax.set_xlim(start_n, end_n)
    ax.set_ylim(0, 40)
    ax.plot(x, y)
    #    ax.plot([ start, end ], [ 10 * 10**9, ] * 2)
    date_formatter = mdates.DateFormatter(fmt="%H:%M")  # type: ignore[no-untyped-call]
    ax.xaxis.set_major_formatter(date_formatter)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, pos: "%.2f C" % (y,)))
    fig.suptitle(f"MHZ19 Temperature {date_string}")
    fig.savefig(fp)

    plt.close()


def draw_days(
    cur: sqlite3.Cursor,
    output_dir: Path,
    tz: str,
    days: int = 1,
) -> None:
    now = datetime.now(timezone(tz))
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)

    output_dir.mkdir(parents=True, exist_ok=True)

    for dd in range(days):
        date = today - timedelta(days=dd)
        date_string = date.replace(tzinfo=None).date().isoformat()
        logger.info(f"MHZ19 Temperature {date_string}")

        path = output_dir / f"{date_string}.png"
        _draw(cur, date, path)
