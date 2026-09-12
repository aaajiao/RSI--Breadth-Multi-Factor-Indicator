"""Tick sequences execute the production scalar alert block with injected inputs.

We inject bar/session flags and already-visible marker levels. This checks
deduplication and publication state, not how TradingView generates those inputs,
delivers notifications, rolls back a realtime bar, or rebuilds history.
"""

from datetime import date
from types import SimpleNamespace
import unittest

from pine_scalar import ScalarSource, statements


class BooleanSeries:
    """Injected current/prior-bar values; this is not a Pine series engine."""

    def __init__(self, current, previous):
        self.values = (bool(current), bool(previous))

    def __bool__(self):
        return self.values[0]

    def __getitem__(self, bars_ago):
        return self.values[bars_ago]


class AlertSequence:
    def __init__(self, *, intraday=True, live=True, path="SPY", min_level=1):
        self.pine = ScalarSource()
        start = self.pine.source.index("varip int buy_alert_level_sent =")
        self.body = statements(self.pine.source[start:])
        self.published = []
        self.last_bar = None
        self.previous_active = (False, False)
        self.current_active = (False, False)
        self.previous_ready = False
        self.current_ready = False

        def publish(message, frequency):
            side = "buy" if self.env["should_alert_buy"] else "risk"
            level = self.env["current_buy_level" if side == "buy" else "current_sell_level"]
            self.published.append((self.env["bar_index"], side, level))

        publish.freq_all = "all"
        self.env = dict(
            intradayMode=intraday, useLiveData=live, enable_smart_alert=True,
            min_alert_level=min_level, displayDataReady=True,
            showSpy=path == "SPY", showQqq=path == "QQQ", showIwm=path == "IWM", showAgg=path == "AGG",
            alertTickerLabel=path, displayUptrend=False, displayDrawdown=6,
            displayScore=4, displaySellScore=-4, displayBuyQuality="A", displaySellQuality="A",
            alert=publish, str=SimpleNamespace(format=lambda *args: "message"),
            year=lambda stamp: stamp.year, month=lambda stamp: stamp.month, dayofmonth=lambda stamp: stamp.day,
        )

    def tick(self, bar, *, buy=0, risk=0, day=12, realtime=True, regular=True, ready=True, active=None):
        new = bar != self.last_bar
        if new:
            self.previous_active = self.current_active
            self.previous_ready = self.current_ready
        self.current_active = active if active is not None else (buy > 0, risk > 0)
        self.current_ready = ready
        self.last_bar = bar
        self.env.update(
            bar_index=bar, barstate=SimpleNamespace(isnew=new, isrealtime=realtime),
            session=SimpleNamespace(ismarket=regular), time=date(2026, 9, day),
            displayDataReady=BooleanSeries(ready, self.previous_ready),
            alertBuySideActive=[self.current_active[0], self.previous_active[0]],
            alertSellSideActive=[self.current_active[1], self.previous_active[1]],
            autoBotTrig=buy > 0, autoStrongBotTrig=buy >= 4,
            autoBotResonanceTrig=buy in (3, 5), autoBullishDivTrig=buy == 2,
            autoTopTrig=risk > 0, autoStrongTopTrig=risk >= 4,
            autoTopResonanceTrig=risk in (3, 5), autoBearishDivTrig=risk == 2,
            autoElevatedTrig=False,
            displayBuyEventLevel=buy, displaySellEventLevel=risk,
            displayEventSide=1 if buy >= risk and buy else -1 if risk else 0,
        )
        self.pine.run(self.body, self.env)
        return self.published[:]


class AlertSequenceTests(unittest.TestCase):
    def test_historical_resonance_does_not_consume_live_reminder(self):
        s = AlertSequence()
        self.assertEqual(s.tick(100, buy=3, realtime=False), [])
        self.assertEqual(s.tick(101, buy=3, realtime=False), [])
        self.assertEqual(s.tick(102, buy=1), [(102, "buy", 1)])

    def test_intrabar_flicker_and_upgrade_publish_only_once_per_bar(self):
        s = AlertSequence()
        s.tick(100, buy=1)
        s.tick(100, buy=0)
        s.tick(100, buy=1)
        s.tick(100, buy=5)
        self.assertEqual(s.published, [(100, "buy", 1)])
        self.assertEqual(s.tick(101, buy=5), [(100, "buy", 1), (101, "buy", 5)])

    def test_same_session_repeats_and_downgrades_stay_muted(self):
        s = AlertSequence()
        s.tick(100, buy=3)
        for bar, level in [(101, 3), (102, 1), (103, 0), (104, 3)]:
            s.tick(bar, buy=level)
        self.assertEqual(s.published, [(100, "buy", 3)])

    def test_rth_only_new_day_rearms_without_afterhours_bar(self):
        s = AlertSequence()
        s.tick(100, buy=3, day=12)
        s.tick(101, buy=1, day=12)
        self.assertEqual(s.tick(102, buy=1, day=13), [(100, "buy", 3), (102, "buy", 1)])

    def test_afterhours_does_not_publish_or_consume_next_session(self):
        s = AlertSequence()
        self.assertEqual(s.tick(100, buy=5, regular=False), [])
        self.assertEqual(s.tick(101, buy=1, day=13), [(101, "buy", 1)])

    def test_missing_data_does_not_consume_a_reminder(self):
        s = AlertSequence()
        self.assertEqual(s.tick(100, buy=3, ready=False), [])
        self.assertEqual(s.tick(100, buy=3, ready=True), [(100, "buy", 3)])

    def test_higher_level_wins_dual_side_tick_and_tie_uses_buy(self):
        s = AlertSequence()
        self.assertEqual(s.tick(100, buy=1, risk=4), [(100, "risk", 4)])
        tie = AlertSequence()
        self.assertEqual(tie.tick(100, buy=3, risk=3), [(100, "buy", 3)])

    def test_buy_and_risk_have_independent_session_latches(self):
        s = AlertSequence()
        s.tick(100, buy=3)
        self.assertEqual(s.tick(101, risk=1), [(100, "buy", 3), (101, "risk", 1)])
        s.tick(102, buy=1)
        s.tick(103, risk=1)
        self.assertEqual(len(s.published), 2)

    def test_deduplicated_winning_side_does_not_publish_opposite_weaker_event(self):
        s = AlertSequence()
        s.tick(100, risk=5)
        self.assertEqual(s.tick(101, buy=1, risk=5), [(100, "risk", 5)])

    def test_all_display_paths_publish_the_visible_path(self):
        for path in ("SPY", "QQQ", "IWM", "AGG"):
            with self.subTest(path=path):
                s = AlertSequence(path=path)
                self.assertEqual(s.tick(100, buy=3), [(100, "buy", 3)])

    def test_daily_path_rearms_only_after_prior_bar_leaves_side(self):
        s = AlertSequence(intraday=False)
        s.tick(100, buy=3)
        s.tick(101, buy=1)
        s.tick(102, buy=0, active=(False, False))
        self.assertEqual(s.tick(103, buy=1), [(100, "buy", 3), (103, "buy", 1)])

    def test_nonlive_data_gap_does_not_rearm_same_side(self):
        for intraday in (False, True):
            for side in ("buy", "risk"):
                with self.subTest(intraday=intraday, side=side):
                    s = AlertSequence(intraday=intraday, live=False)
                    s.tick(100, **{side: 3})
                    s.tick(101, ready=False, active=(False, False))
                    s.tick(102, **{side: 3})
                    self.assertEqual(s.published, [(100, side, 3)])
                    # A confirmed, usable neutral bar really does re-arm.
                    s.tick(103, ready=True, active=(False, False))
                    self.assertEqual(s.tick(104, **{side: 1}), [(100, side, 3), (104, side, 1)])

    def test_minimum_level_does_not_consume_lower_event(self):
        s = AlertSequence(min_level=3)
        self.assertEqual(s.tick(100, buy=1), [])
        self.assertEqual(s.tick(100, buy=3), [(100, "buy", 3)])
