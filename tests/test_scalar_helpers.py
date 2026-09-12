"""Boundary regressions against extracted production scalar helpers.

Run: python3 -m unittest discover -s tests -v
Passing does NOT establish Pine compilation or TradingView runtime behavior.
"""

from itertools import product
import unittest

from pine_scalar import NA, ScalarSource


class ScalarHelperTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pine = ScalarSource()

    def test_factor_boundaries_and_missing_volume(self):
        for value, expected in [(-1501, 3), (-1500, 2), (-500, 1), (0, 0), (500, -1), (1500, -2), (1501, -3), (NA, 0)]:
            with self.subTest(add=value):
                self.assertEqual(self.pine.call("f_addScore", value), expected)
        for up, down, expected in [(1, 0, 0), (NA, 1, 0), (1, NA, 0), (.49, 1, 2), (.5, 1, 1), (.8, 1, 0), (1.8, 1, 0), (2.5, 1, -1), (2.51, 1, -2)]:
            with self.subTest(volume=(up, down)):
                self.assertEqual(self.pine.call("f_volScore", up, down), expected)

    def test_intraday_add_replaces_daily_breadth(self):
        daily = self.pine.call("f_totalScore", 20, 20, 20, .4, 1, 2000, False, 30, 40, 75, 65)
        intraday = self.pine.call("f_totalScore", 20, 20, 20, .4, 1, 2000, True, 30, 40, 75, 65)
        self.assertEqual(daily, [8, 2, 3, 1, 2, 0])
        self.assertEqual(intraday, [1, 2, 0, 0, 2, -3])

    def test_risk_quality_counts_risk_factors_and_intraday_denominator(self):
        self.assertEqual(self.pine.call("f_signalQuality", -2, -2, -3, -2, 0, False), ["C", "A", 0, 4])
        self.assertEqual(self.pine.call("f_signalQuality", -2, 3, 1, -2, -3, True), ["C", "A", 0, 3])
        self.assertEqual(self.pine.call("f_signalQuality", 2, -2, -3, 2, 0, False), ["B", "B", 2, 2])
        self.assertEqual([self.pine.call("f_qualityGrade", count) for count in range(5)], ["C", "C", "B", "A", "A"])

    def test_raw_risk_status_survives_drawdown_bonus(self):
        self.assertEqual(self.pine.call("f_marketStatus", 2, -1, 1, -1, True), "🔴")
        self.assertEqual(self.pine.call("f_marketStatus", 2, 0, 1, -1, True), "🟢")
        self.assertEqual(self.pine.call("f_marketStatus", 0, 0, 1, -1, True), "🟡")
        self.assertNotIn(self.pine.call("f_marketStatus", 2, -1, 1, -1, False), ("🔴", "🟢", "🟡"))

    def test_alert_upgrades_require_a_visible_base_trigger(self):
        for resonance, divergence in product((False, True), repeat=2):
            self.assertEqual(self.pine.call("f_buy_level", False, False, resonance, divergence), 0)
            self.assertEqual(self.pine.call("f_sell_level", False, False, resonance, divergence, False), 0)
        self.assertEqual(self.pine.call("f_buy_level", False, True, False, False), 1)
        self.assertEqual(self.pine.call("f_buy_level", False, True, False, True), 2)
        self.assertEqual(self.pine.call("f_buy_level", False, True, True, True), 3)
        self.assertEqual(self.pine.call("f_buy_level", True, False, False, True), 4)
        self.assertEqual(self.pine.call("f_buy_level", True, False, True, True), 5)
        self.assertEqual(self.pine.call("f_sell_level", False, False, False, False, True), 1)
        self.assertEqual(self.pine.call("f_sell_level", True, False, True, True, False), 5)

    def test_panel_and_alert_event_arbitration(self):
        for buy, risk in product(range(6), repeat=2):
            expected = 0 if buy == risk == 0 else 1 if buy >= risk else -1
            with self.subTest(buy=buy, risk=risk):
                self.assertEqual(self.pine.call("f_eventSide", buy, risk), expected)

    def test_all_supported_threshold_inputs_keep_hold_gap_and_strong_order(self):
        for buy, sell, mode, intraday in product(range(25, 76, 5), range(25, 76, 5), ("Aggressive", "Standard", "Conservative"), (False, True)):
            env = dict(buyThresholdPct=buy, sellThresholdPct=sell, mode=mode,
                       intradayMode=intraday, strongOffset=25, maxBuyScore=8, maxSellScore=9)
            for name in ("botThreshold", "strongBotThreshold", "topThreshold", "strongTopThreshold", "modeAdjust", "intradayAdjust", "adjBotThreshold", "adjStrongBotThreshold", "adjTopThreshold", "adjStrongTopThreshold"):
                env[name] = self.pine.assignment(name, env)
            with self.subTest(buy=buy, sell=sell, mode=mode, intraday=intraday):
                self.assertLessEqual(env["adjTopThreshold"], -1)
                self.assertGreaterEqual(env["adjBotThreshold"], 1)
                self.assertLess(env["adjStrongTopThreshold"], env["adjTopThreshold"])
                self.assertGreater(env["adjStrongBotThreshold"], env["adjBotThreshold"])
            if buy == 50 and sell == 45 and mode == "Standard" and not intraday:
                self.assertEqual([env[name] for name in ("adjBotThreshold", "adjStrongBotThreshold", "adjTopThreshold", "adjStrongTopThreshold")], [4, 6, -4, -6])

    def test_adaptive_lookback_never_receives_na_or_zero_length(self):
        env = dict(lookbackPrecision="High", lookbackMode="Auto", lookbackCustom=252, rsiVolThreshold=8)
        for vol, available in product((NA, 0, 8, 100), (NA, 0, 1, 9, 50, 5000)):
            with self.subTest(vol=vol, available=available):
                actual = self.pine.call("f_adaptiveLookback", vol, available, env=env)
                self.assertIsInstance(actual, int)
                self.assertGreaterEqual(actual, 1)
                self.assertLessEqual(actual, 1000)
                if available == available:
                    self.assertLessEqual(actual, max(1, available))
        for mode, custom, expected in [("Fixed 252", 500, 252), ("Custom", 500, 500)]:
            self.assertEqual(self.pine.call("f_adaptiveLookback", NA, 5000, env={**env, "lookbackMode": mode, "lookbackCustom": custom}), expected)

    def test_cooldown_boundary_and_user_disable(self):
        self.assertFalse(self.pine.call("f_applyCooldown", True, 10, 100, env={"bar_index": 109}))
        self.assertTrue(self.pine.call("f_applyCooldown", True, 10, 100, env={"bar_index": 110}))
        self.assertTrue(self.pine.call("f_applyCooldown", True, 10, NA, env={"bar_index": 1}))
        self.assertEqual(self.pine.call("f_dynamicCooldown", 0, 1, 8), 0)

    def test_window_resonance_is_distinct_from_same_bar_synchrony(self):
        env = {"minAgree": 2}
        self.assertEqual(self.pine.call("f_resonanceStrength", False, True, False, True, True, False, env=env), [2.0, .5, False, 1, 2])
        self.assertEqual(self.pine.call("f_resonanceStrength", True, True, False, True, True, False, env=env), [2.5, 1.0, True, 2, 2])
        self.assertEqual(self.pine.call("f_resonanceStrength", True, True, True, True, True, True, env=env), [3.0, 1.0, True, 3, 3])
        self.assertEqual(self.pine.call("f_resonanceStrength", True, True, False, True, True, False, env={"minAgree": 3})[:3], [1.0, 0.0, False])
        self.assertEqual(self.pine.call("f_resonanceStrength", True, False, False, True, False, False, env={"minAgree": 1})[:3], [1.0, 0.0, False])

    def test_required_data_is_not_treated_as_neutral(self):
        valid = [100, 50, 99, 110, 40, 50, 1000, 1000, 0]
        self.assertTrue(self.pine.call("f_marketDataReady", *valid, False))
        self.assertTrue(self.pine.call("f_marketDataReady", *valid, True))
        for missing in range(8):
            values = valid[:]
            values[missing] = NA
            self.assertFalse(self.pine.call("f_marketDataReady", *values, False))
        # Daily breadth slots do not score intraday, and ADD does not score daily.
        self.assertTrue(self.pine.call("f_marketDataReady", *valid[:4], NA, NA, *valid[6:], True))
        self.assertTrue(self.pine.call("f_marketDataReady", *valid[:8], NA, False))
        self.assertFalse(self.pine.call("f_marketDataReady", *valid[:8], NA, True))
        self.assertFalse(self.pine.call("f_marketDataReady", *valid[:7], 0, 0, True))
