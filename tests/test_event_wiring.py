"""Production event commits with explicit rollback snapshots, plus source wiring.

Rollback and barssince inputs are injected assumptions; these tests do not
emulate TradingView's execution engine. The source assertions cover connections
that cannot be established by testing a scalar helper in isolation.
"""

from types import SimpleNamespace
import unittest

from pine_scalar import NA, ScalarSource, statements


class EventWiringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pine = ScalarSource()

    def test_retracted_intrabar_marker_commits_cooldown_and_window_event(self):
        start = self.pine.source.index("spyBarBuyPlotState := math.max(")
        end = self.pine.source.index("// Aggregate resonance", start)
        body = statements(self.pine.source[start:end])
        env = {"bar_index": 100}
        for market in ("spy", "qqq", "iwm"):
            for side in ("Buy", "Sell"):
                env[f"{market}Bar{side}PlotState"] = 0
            for kind in ("Bot", "Top", "StrongBot", "StrongTop", "Elevated", "BullishDiv", "BearishDiv"):
                env[f"{market}{kind}Plot"] = False
            for kind in ("BullishDiv", "BearishDiv"):
                env[f"{market}{kind}PlotBar"] = False
        env.update(spyBotPlot=True, spyBullishDivPlot=True, spyLastBot=NA, spyLastBullDiv=NA)
        self.pine.run(body, env)
        self.assertEqual(env["spyBarBuyPlotState"], 1)

        # Simulate the next tick restoring ordinary var state to its prior-bar
        # snapshot while varip event latches remain. The raw condition has faded.
        env.update(spyBotPlot=False, spyBullishDivPlot=False, spyLastBot=NA, spyLastBullDiv=NA)
        self.pine.run(body, env)
        self.assertEqual(env["spyLastBot"], 100)
        self.assertEqual(env["spyLastBullDiv"], 100)
        self.assertTrue(env["spyBotEvent"])
        self.assertFalse(self.pine.call("f_applyCooldown", True, 10, env["spyLastBot"], env={"bar_index": 101}))

        # Bar 102 adds QQQ; injected barssince age reflects the accepted SPY
        # event at bar 100, even though its close-time raw condition was false.
        spy_recent = self.pine.call("f_recent", False, 3, env={"ta": SimpleNamespace(barssince=lambda _: 2)})
        qqq_recent = self.pine.call("f_recent", True, 3, env={"ta": SimpleNamespace(barssince=lambda _: 0)})
        resonance = self.pine.call("f_resonanceStrength", False, True, False, spy_recent, qqq_recent, False, env={"minAgree": 2})
        self.assertEqual(resonance[0], 2)
        self.assertFalse(self.pine.call("f_recent", False, 3, env={"ta": SimpleNamespace(barssince=lambda _: 4)}))
        self.assertFalse(self.pine.call("f_recent", False, 0))

    def test_accepted_weak_marker_allows_one_strong_upgrade_after_raw_fades(self):
        for market in ("spy", "qqq", "iwm"):
            for side, accepted, strong_level in (("Bot", 1, 2), ("Top", 2, 3)):
                latch = "Buy" if side == "Bot" else "Sell"
                env = {
                    f"{market}Strong{side}": True,
                    f"{market}Last{side}Level": accepted,
                    f"{market}Strong{side}Prev": False,
                    f"{market}{side}RawPrev": False,
                    f"{market}Bar{latch}PlotState": [0, accepted],
                }
                self.assertTrue(self.pine.assignment(f"{market}Strong{side}Upgrade", env))
                env[f"{market}Last{side}Level"] = strong_level
                self.assertFalse(self.pine.assignment(f"{market}Strong{side}Upgrade", env))

    def test_resonance_and_cooldown_consume_accepted_events_for_every_market(self):
        source = self.pine.source
        for market in ("spy", "qqq", "iwm"):
            for side in ("Bot", "Top"):
                self.assertIn(f"{market}{side}Recent = f_recent({market}{side}Event, confirmBars)", source)
                self.assertIn(f"if {market}{side}Event\n    {market}Last{side} := bar_index", source)
            self.assertIn(f"varip int {market}BarBuyPlotState", source)
            self.assertIn(f"varip int {market}BarSellPlotState", source)

    def test_each_market_supplies_its_own_adaptive_inputs_and_cooldown(self):
        for market in ("spy", "qqq", "iwm"):
            self.assertIn(f"f_marketAdaptive({market}RSI, {market}LongVol)", self.pine.source)
            self.assertIn(f"f_applyCooldown({market}BotRaw, {market}CooldownBars, {market}LastBot)", self.pine.source)
            self.assertIn(f"f_applyCooldown({market}BullishDivRaw, {market}DivCooldownBars, {market}LastBullDiv)", self.pine.source)
        self.assertNotIn("driverRSI", self.pine.source)

    def test_long_history_is_confirmed_daily_and_distinct_in_all_modes(self):
        self.assertEqual([self.pine.assignment("vol_history_days", {"volHistoryMode": mode}) for mode in ("6 Months", "1 Year", "2 Years")], [126, 252, 504])
        _, body = self.pine.functions["f_dailyMarketStats"]
        code = "\n".join(line for _, line in body)
        self.assertIn("ta.stdev(dailyRsi, _historyDays)", code)
        self.assertIn('request.security(_sym, "D", [dailyHigh[1], dailyLongVol[1], dailySamples[1]]', code)
        self.assertNotIn("bars_per_day", self.pine.source)

    def test_dashboard_risk_direction_controls_score_quality_and_count(self):
        for risk in (False, True):
            env = dict(panelSellActive=risk, displaySellScore=-6, displayScore=-3,
                       displayNegFactor=4, displayPosFactor=0)
            self.assertEqual(self.pine.assignment("displayPanelScore", env), -6 if risk else -3)
            # Quality and count should stay consistent for the selected side.
            env["displayPanelFactorCount"] = self.pine.assignment("displayPanelFactorCount", env)
            self.assertEqual(env["displayPanelFactorCount"], 4 if risk else 0)
            self.assertEqual(self.pine.assignment("displayPanelQuality", env), "A" if risk else "C")

    def test_agg_requires_all_market_data_before_plotting_resonance(self):
        for missing in (None, "spy", "qqq", "iwm"):
            env = dict(spyDataReady=True, qqqDataReady=True, iwmDataReady=True,
                       agreeBot=3, agreeTop=3, minAgree=2)
            if missing:
                env[f"{missing}DataReady"] = False
            env["aggDataReady"] = self.pine.assignment("aggDataReady", env)
            self.assertEqual(self.pine.assignment("aggBottom", env), missing is None)
            self.assertEqual(self.pine.assignment("aggTop", env), missing is None)

    def test_supported_timeframes_reject_ticks_and_multiday_bars(self):
        for seconds, minutes, daily, multiplier, expected in (
            (True, False, False, 30, True), (False, True, False, 5, True),
            (False, True, False, 240, True), (False, False, True, 1, True),
            (False, False, True, 2, False), (False, False, False, 1, False),
        ):
            env = {"timeframe": SimpleNamespace(isseconds=seconds, isminutes=minutes, isdaily=daily, multiplier=multiplier)}
            self.assertEqual(self.pine.assignment("supportedTimeframe", env), expected)

    def test_warmup_uses_requested_adaptation_even_while_effective_mode_is_fixed(self):
        for selected in ("spy", "qqq", "iwm"):
            env = dict(showSpy=selected == "spy", showQqq=selected == "qqq", showIwm=selected == "iwm")
            for market in ("spy", "qqq", "iwm"):
                env.update({f"{market}AdaptiveRequested": True, f"{market}AdaptiveReady": False, f"{market}UseAdaptive": False})
            self.assertTrue(self.pine.assignment("displayAdaptiveFallback", env))
            env[f"{selected}AdaptiveReady"] = True
            self.assertFalse(self.pine.assignment("displayAdaptiveFallback", env))

    def test_data_gap_preserves_panel_and_zone_until_real_hold(self):
        start = self.pine.source.index("var int signalZoneState =")
        end = self.pine.source.index("panelStrongBotSignal =", start)
        body = statements(self.pine.source[start:end])
        for zone, panel in ((1, 2), (-1, -3)):
            env = dict(signalZoneState=zone, panelSignalState=panel,
                       displayEventSide=0, displayDataReady=False,
                       displayScore=0, displaySellScore=0,
                       adjBotThreshold=4, adjTopThreshold=-4)
            env["isHoldZone"] = self.pine.assignment("isHoldZone", env)
            self.assertFalse(env["isHoldZone"])
            self.pine.run(body, env)
            self.assertEqual((env["signalZoneState"], env["panelSignalState"]), (zone, panel))
            env["displayDataReady"] = True
            env["isHoldZone"] = self.pine.assignment("isHoldZone", env)
            self.assertTrue(env["isHoldZone"])
            self.pine.run(body, env)
            self.assertEqual((env["signalZoneState"], env["panelSignalState"]), (0, 0))
        # The saved zone is hidden during a gap, not erased by a zero factor.
        self.assertIn("bgcolor(showSignalZone and displayDataReady and signalZoneState == 1", self.pine.source)
        self.assertIn("bgcolor(showSignalZone and displayDataReady and signalZoneState == -1", self.pine.source)

    def test_fixed_thresholds_do_not_show_irrelevant_adaptive_warmup(self):
        env = dict(thresholdMode="Fixed", lookbackMode="Auto",
                   displayLongVolReady=False, displayAdaptiveFallback=True)
        self.assertFalse(self.pine.assignment("displayWarmingUp", env))
        env["thresholdMode"] = "Auto"
        self.assertTrue(self.pine.assignment("displayWarmingUp", env))

    def test_missing_data_displays_wait_and_unknown_trend(self):
        for uptrend in (False, True):
            env = dict(displayDataReady=False, displayUptrend=uptrend)
            self.assertEqual(self.pine.assignment("signalText", env), "WAIT DATA / 等待数据")
            self.assertEqual(self.pine.assignment("trendText", env), "—")
            self.assertEqual(self.pine.assignment("scoreWithTrend", env), "")
            self.assertEqual(self.pine.assignment("scoreStr", env), "")
