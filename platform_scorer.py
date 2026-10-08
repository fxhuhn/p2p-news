"""
P2P Platform Audit Scorer - Deterministische Scoring-Engine

Berechnet den Netto-Score auf Basis des 4-Säulen- und Malus-Regelwerks:
- Säule 1: Regulierung & Custody (0 - 25 Pkt)
- Säule 2: Solvenz & Governance (0 - 25 Pkt)
- Säule 3: Asset-Qualität & Workout (0 - 25 Pkt)
- Säule 4: Liquidität & Fristenkongruenz (0 - 25 Pkt)
- Rohscore: Max. 100 Punkte
- Malus-Abschläge: Monokultur, Fristen-Mismatch, Related-Party, Distressed
- Netto-Score: max(0, Rohscore - Mali)
- Risikoklassen-Zuordnung & Depot-Limits
- Flags für Vorsichtsprinzip (has_conflict, data_gaps)
- Plausibilitätsprüfung (Triangulierung) gegen P2P Empire & Lars Wrobbel
"""

from typing import Any, Dict, List

from scoring_models import (
    RISK_CLASS_LIMITS,
    RISK_CLASS_RECOMMENDATIONS,
    AuditFlags,
    BenchmarkMetrics,
    MalusItem,
    ModifierEvaluation,
    PillarFactExtract,
    determine_risk_class,
)


class PlatformScorer:
    """Führt die deterministische Bewertung für ein Plattform-Profil durch."""

    def score_platform(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        platform_id = profile["platform"]
        platform_name = profile.get("platform_name", platform_id.capitalize())

        # 1. Säulen berechnen
        p1 = self._score_pillar_1(profile.get("regulation", {}))
        p2 = self._score_pillar_2(profile.get("governance_and_solvency", {}))
        p3 = self._score_pillar_3(profile.get("collateral_and_workout", {}))
        p4 = self._score_pillar_4(profile.get("liquidity_and_marketplace", {}))

        raw_score = p1.final_score + p2.final_score + p3.final_score + p4.final_score

        # 2. Malus-Abzüge berechnen
        mali = self._evaluate_malus(profile.get("malus_triggers", {}))
        malus_total = sum(m.penalty for m in mali)

        # 3. Netto-Score & Risikoklasse
        net_score = max(0, raw_score + malus_total)  # malus_total ist negativ
        risk_class = determine_risk_class(net_score)

        # 4. Flags & Datenlücken
        flags = self._evaluate_flags(profile, p1, p2, p3, p4)

        # 5. Benchmark Metrics
        benchmarks = self._extract_benchmarks(profile.get("benchmarks", {}))

        return {
            "platform": platform_id,
            "platform_name": platform_name,
            "raw_score": raw_score,
            "net_score": net_score,
            "risk_class": risk_class,
            "portfolio_limit": RISK_CLASS_LIMITS[risk_class],
            "recommendation": RISK_CLASS_RECOMMENDATIONS[risk_class],
            "pillar_1": p1,
            "pillar_2": p2,
            "pillar_3": p3,
            "pillar_4": p4,
            "malus_deductions": mali,
            "malus_total": malus_total,
            "flags": flags,
            "benchmarks": benchmarks,
        }

    # =========================================================================
    # Säule 1: Regulierung, Verwahrung & Rechtliche Trennung (0 - 25 Pkt)
    # =========================================================================
    def _score_pillar_1(self, reg: Dict[str, Any]) -> PillarFactExtract:
        reg_type = reg.get("type", "unregulated")
        has_investor_comp = reg.get("investor_compensation", False)
        custody_text = (reg.get("custody") or "").lower()
        notes = reg.get("notes", "")

        modifiers: List[ModifierEvaluation] = []

        if reg_type == "licensed_mifid":
            band_id = "Band_21_25"
            base_score = 23
            if has_investor_comp:
                modifiers.append(
                    ModifierEvaluation(
                        name="MiFID II Anlegerentschädigung (bis 20.000 €)",
                        points=2,
                        condition_met=True,
                        rationale="Gesetzliche Entschädigungseinrichtung schützt Barbestände.",
                    )
                )
            if "tier-1" in custody_text or "tier 1" in custody_text:
                pass  # Standard
            rating_label = "MiFID II / IBF lizenziert"

        elif reg_type == "licensed_ecsp":
            band_id = "Band_21_25"
            base_score = 23
            if "paysera" in custody_text or "lemonway" in custody_text:
                modifiers.append(
                    ModifierEvaluation(
                        name="Segregierte Treuhandkonten bei lizenziertem EMI",
                        points=2,
                        condition_met=True,
                        rationale="Insolvenzfeste Verwahrung bei Lemonway/Paysera.",
                    )
                )
            rating_label = "ECSP lizenziert"

        elif reg_type == "national_special" or reg_type == "national":
            band_id = "Band_14_20"
            base_score = 17
            rating_label = "National reguliert"
            if not has_investor_comp and (
                "keine mifid" in notes.lower()
                or "keine einlagensicherung" in notes.lower()
                or "sammelpool" in notes.lower()
                or "nicht segregiert" in custody_text
                or "keine mifid ii" in custody_text
            ):
                modifiers.append(
                    ModifierEvaluation(
                        name="Keine MiFID-Segregation oder Einlagensicherung bei nationalem Kreditgeber",
                        points=-3,
                        condition_met=True,
                        rationale="Kundengelder im Sammelpool / operativer Bilanz gebunden.",
                    )
                )

        elif reg_type == "unregulated_with_pipeline":
            # Beispiel Esketit: Kroatische Abtretung, aber IBF-Verfahren läuft
            band_id = "Band_6_13"
            base_score = 9
            modifiers.append(
                ModifierEvaluation(
                    name="IBF-Migrationspfad durch lizenzierte Schwester",
                    points=2,
                    condition_met=True,
                    rationale="IBF-Lizenz für SIA IBC Invest erteilt.",
                )
            )
            if "segregiert" in custody_text or "getrennt" in custody_text:
                modifiers.append(
                    ModifierEvaluation(
                        name="Externe Kontoführung bei EU-Banken",
                        points=2,
                        condition_met=True,
                        rationale="Kontenführung bei regulierten europäischen Partnerbanken.",
                    )
                )
            rating_label = "Unreguliert / Lizenzübergang"

        else:  # unregulated
            if "offshore" in custody_text or "unklar" in custody_text:
                band_id = "Band_0_5"
                base_score = 2
                rating_label = "Völlig unreguliert / Offshore"
            else:
                band_id = "Band_6_13"
                base_score = 8
                rating_label = "Unreguliert (Abtretungsverträge)"
                if (
                    "paysera" in custody_text
                    or "treuhand" in custody_text
                    or "lemonway" in custody_text
                ):
                    modifiers.append(
                        ModifierEvaluation(
                            name="Treuhänderische / EMI-Zahlungsabwicklung",
                            points=2,
                            condition_met=True,
                            rationale="Gelder bei lizenziertem E-Geld-Institut geführt.",
                        )
                    )
                if reg.get("parent_company_regulated", False) or (
                    "finantsinspektsioon" in notes.lower()
                    and "muttergesellschaft" in notes.lower()
                ):
                    modifiers.append(
                        ModifierEvaluation(
                            name="Regulierte Muttergesellschaft (Konzernaufsicht)",
                            points=2,
                            condition_met=True,
                            rationale="Muttergesellschaft verfügt über aufsichtsrechtliche Kreditgeber-Lizenz.",
                        )
                    )

        final_score = base_score + sum(m.points for m in modifiers if m.condition_met)
        final_score = max(0, min(25, final_score))

        return PillarFactExtract(
            band_id=band_id,
            base_score=base_score,
            modifiers=modifiers,
            final_score=final_score,
            rating_label=rating_label,
            evidence_text=notes
            or f"Regulierung: {reg_type}, Verwahrung: {custody_text}",
        )

    # =========================================================================
    # Säule 2: Solvenz & Governance des Garantiegebers (0 - 25 Pkt)
    # =========================================================================
    def _score_pillar_2(self, sol: Dict[str, Any]) -> PillarFactExtract:
        auditor = (sol.get("auditor") or "").lower()
        opinion = (sol.get("audit_opinion") or "").lower()
        equity_ratio = (
            sol.get("equity_ratio_pct")
            if sol.get("equity_ratio_pct") is not None
            else sol.get("equity_ratio_pct: ")
        )
        icr = sol.get("interest_coverage_ratio")
        notes = sol.get("notes", "")

        modifiers: List[ModifierEvaluation] = []

        is_top_auditor = any(
            a in auditor
            for a in ["bdo", "grant thornton", "kpmg", "pwc", "ey", "deloitte"]
        )

        if is_top_auditor and "unqualified" in opinion:
            band_id = "Band_21_25"
            base_score = 20
            if equity_ratio is not None and equity_ratio > 40.0:
                modifiers.append(
                    ModifierEvaluation(
                        name="Hervorragende Eigenkapitalquote (>40 %)",
                        points=4,
                        condition_met=True,
                        rationale=f"Eigenkapitalquote liegt bei {equity_ratio} %.",
                    )
                )
            elif equity_ratio is not None and equity_ratio > 30.0:
                modifiers.append(
                    ModifierEvaluation(
                        name="Starke Eigenkapitalquote (>30 %)",
                        points=2,
                        condition_met=True,
                        rationale=f"Eigenkapitalquote liegt bei {equity_ratio} %.",
                    )
                )
            elif equity_ratio is not None and equity_ratio > 25.0:
                modifiers.append(
                    ModifierEvaluation(
                        name="Gute Eigenkapitalquote (>25 %)",
                        points=1,
                        condition_met=True,
                        rationale=f"Eigenkapitalquote liegt bei {equity_ratio} %.",
                    )
                )
            if icr is not None and icr < 3.0:
                modifiers.append(
                    ModifierEvaluation(
                        name="Zinsdeckung unter 3.0x",
                        points=-2,
                        condition_met=True,
                        rationale=f"ICR beträgt {icr}x.",
                    )
                )
            rating_label = "Sehr gut / Testiert"

        elif "lokal" in auditor or (equity_ratio is not None and equity_ratio > 15.0):
            band_id = "Band_14_20"
            base_score = 17
            rating_label = "Solide / Lokaler Abschluss"

        elif not is_top_auditor and not auditor:
            # Vorsichtsprinzip bei fehlendem Abschluss
            band_id = "Band_0_6"
            base_score = 3
            rating_label = "Keine testierten Finanzberichte"

        else:
            band_id = "Band_7_13"
            base_score = 10
            rating_label = "Befriedigend / Governance-Schwächen"

        final_score = base_score + sum(m.points for m in modifiers if m.condition_met)
        final_score = max(0, min(25, final_score))

        return PillarFactExtract(
            band_id=band_id,
            base_score=base_score,
            modifiers=modifiers,
            final_score=final_score,
            rating_label=rating_label,
            evidence_text=notes
            or f"Auditor: {auditor}, EK-Quote: {equity_ratio}%, ICR: {icr}x",
        )

    # =========================================================================
    # Säule 3: Asset-Qualität, Besicherung & Workout (0 - 25 Pkt)
    # =========================================================================
    def _score_pillar_3(self, col: Dict[str, Any]) -> PillarFactExtract:
        asset_type = (col.get("primary_asset_type") or "").lower()
        security_type = (col.get("security_type") or "").lower()
        ltv = col.get("ltv_max_pct")
        hist_loss = col.get("historical_loss_pct", 0.0)
        npl = col.get("current_npl_pct", 0.0)
        notes = col.get("notes", "")

        modifiers: List[ModifierEvaluation] = []

        if (
            "1st-rank" in security_type
            or "hypothek" in security_type
            or "grundschuld" in security_type
        ):
            if npl is not None and npl > 30.0:
                # Akute Notlage wie bei EstateGuru
                band_id = "Band_0_7"
                base_score = 3
                rating_label = "Notleidend (NPL >30 %)"
            else:
                band_id = "Band_21_25"
                base_score = 23
                if ltv is not None and ltv <= 60.0 and hist_loss == 0.0:
                    modifiers.append(
                        ModifierEvaluation(
                            name="Konservativer LTV (<=60 %) & 0 % Verlusthistorie",
                            points=2,
                            condition_met=True,
                            rationale=f"LTV max {ltv} %, historischer Kapitalverlust 0 %.",
                        )
                    )
                rating_label = "Erststellige Realsicherheiten"

        elif (
            ("agrar" in asset_type or "kfz" in asset_type or "maschinen" in asset_type)
            and (
                "pfand" in security_type
                or "sicherungsübereignung" in security_type
                or "eigentumsvorbehalt" in security_type
                or "brief" in security_type
                or "hypothek" in security_type
            )
            or ("pfand" in security_type and "buyback" not in security_type)
        ):
            band_id = "Band_15_20"
            base_score = 17
            rating_label = "Dinglich besichert (Mobiliar)"

        elif (
            "buyback" in security_type
            or "rückkauf" in security_type
            or "konsum" in asset_type
            or "keine dingliche" in security_type
        ):
            band_id = "Band_8_14"
            base_score = 11
            if hist_loss == 0.0:
                modifiers.append(
                    ModifierEvaluation(
                        name="Krisenerprobter 100 % Buyback-Track-Record",
                        points=3,
                        condition_met=True,
                        rationale="0 % Kapitalverlust für Anleger in der Historie.",
                    )
                )
            # Puffer für etablierte Anbieter
            if npl is not None and npl < 5.0:
                modifiers.append(
                    ModifierEvaluation(
                        name="Niedrige Ausfallrate (<5 %)",
                        points=2,
                        condition_met=True,
                        rationale=f"Aktuelle Problemquote nur {npl} %.",
                    )
                )
            if (
                hist_loss == 0.0
                and notes
                and any(
                    w in notes.lower()
                    for w in [
                        "krieg",
                        "100 % rückzahlung",
                        "100% rückzahlung",
                        "krisenerprobt",
                    ]
                )
            ):
                modifiers.append(
                    ModifierEvaluation(
                        name="Vollständige Krisen-Schadensregulierung aus Konzerngewinnen",
                        points=1,
                        condition_met=True,
                        rationale="Nachgewiesene 100 % Rückabwicklung geopolitischer Krisenfälle aus Konzernmitteln.",
                    )
                )
            if (
                col.get("has_loss_buffer", False)
                or "renditeabstand" in notes.lower()
                or (
                    "diversifikation" in notes.lower()
                    and ("puffer" in notes.lower() or "reserve" in notes.lower())
                )
            ):
                modifiers.append(
                    ModifierEvaluation(
                        name="Granulare Diversifikation & Zinsabstand-Verlustpuffer",
                        points=2,
                        condition_met=True,
                        rationale="Hohe Streuung über Zehntausende Kleinkredite und Zinsmarge als interner Verlustpuffer.",
                    )
                )
            rating_label = "Unbesichert mit Buyback"

        else:
            band_id = "Band_0_7"
            base_score = 3
            rating_label = "Unbesichert ohne Rückkauf / Hochrisiko"

        final_score = base_score + sum(m.points for m in modifiers if m.condition_met)
        final_score = max(0, min(25, final_score))

        return PillarFactExtract(
            band_id=band_id,
            base_score=base_score,
            modifiers=modifiers,
            final_score=final_score,
            rating_label=rating_label,
            evidence_text=notes
            or f"Asset: {asset_type}, Besicherung: {security_type}, NPL: {npl}%",
        )

    # =========================================================================
    # Säule 4: Liquidität & Fristenkongruenz (0 - 25 Pkt)
    # =========================================================================
    def _score_pillar_4(self, liq: Dict[str, Any]) -> PillarFactExtract:
        has_secondary = liq.get("secondary_market", False)
        sm_fee = liq.get("secondary_market_fee_pct")
        waiting_days = liq.get("secondary_market_waiting_days", 0)
        duration_days = liq.get("primary_loan_duration_days_avg", 180)
        queue_days = liq.get("withdrawal_queue_days", 0)
        notes = liq.get("notes", "")

        modifiers: List[ModifierEvaluation] = []

        is_pool = (
            liq.get("is_liquidity_pool", False)
            or "pool" in notes.lower()
            or "go & grow" in notes.lower()
            or "smartsaver" in notes.lower()
        )

        if queue_days is not None and queue_days > 7:
            # Auszahlungsstopp oder blockiert
            band_id = "Band_0_5"
            base_score = 2
            rating_label = "Liquiditätsstau / Warteschlange"

        elif is_pool:
            band_id = "Band_13_19"
            base_score = 18
            rating_label = "Hohe Alltagsliquidität (Reserve-Pool)"
            if (
                "teilauszahlung" in notes.lower()
                or "partial" in notes.lower()
                or "auszahlungsdeckel" in notes.lower()
            ):
                modifiers.append(
                    ModifierEvaluation(
                        name="Vertragliches Schutzventil (gestaffelte Teilauszahlungen)",
                        points=0,
                        condition_met=True,
                        rationale="Auszahlungsdeckel schützt vor Notverkäufen bei Marktpanik.",
                    )
                )

        elif (
            has_secondary
            and duration_days <= 90
            and (waiting_days is None or waiting_days == 0)
        ):
            # Hochliquid: Payday-Kurzläufer + gebührenfreier Sofort-Sekundärmarkt (wie Esketit, PeerBerry)
            band_id = "Band_20_25"
            base_score = 22
            if duration_days > 30:
                modifiers.append(
                    ModifierEvaluation(
                        name="Mittlere Kurzläufer-Dauer (30-90 Tage)",
                        points=-2,
                        condition_met=True,
                        rationale=f"Durchschnittliche Laufzeit beträgt {duration_days} Tage.",
                    )
                )
            if sm_fee is not None and sm_fee == 0.0 and duration_days <= 30:
                modifiers.append(
                    ModifierEvaluation(
                        name="Gebührenfreier Sofort-Sekundärmarkt bei ultrakurzen Laufzeiten",
                        points=2,
                        condition_met=True,
                        rationale="Keine Zweitmarktgebühren und sofortiger Liquiditätsabruf bei Laufzeiten <=30 Tagen.",
                    )
                )
            rating_label = "Sehr liquide / Kurzläufer & Zweitmarkt"

        elif has_secondary or duration_days <= 180:
            band_id = "Band_13_19"
            base_score = 16
            if waiting_days is not None and waiting_days >= 180:
                modifiers.append(
                    ModifierEvaluation(
                        name="Sekundärmarkt-Mindesthaltedauer (6 Monate)",
                        points=-2,
                        condition_met=True,
                        rationale="Verkauf erst nach 180 Tagen Haltedauer möglich.",
                    )
                )
            if sm_fee is not None and sm_fee <= 1.0:
                modifiers.append(
                    ModifierEvaluation(
                        name="Niedrige Zweitmarktgebühr (<=1 %)",
                        points=2,
                        condition_met=True,
                        rationale=f"Zweitmarktgebühr beträgt {sm_fee} %.",
                    )
                )
            rating_label = "Gute Liquidität"

        elif not has_secondary and duration_days > 365:
            band_id = "Band_6_12"
            base_score = 9
            rating_label = "Illiquide / Langläufer ohne Zweitmarkt"

        else:
            band_id = "Band_6_12"
            base_score = 11
            rating_label = "Planbare Tilgung"

        final_score = base_score + sum(m.points for m in modifiers if m.condition_met)
        final_score = max(0, min(25, final_score))

        return PillarFactExtract(
            band_id=band_id,
            base_score=base_score,
            modifiers=modifiers,
            final_score=final_score,
            rating_label=rating_label,
            evidence_text=notes
            or f"Sekundärmarkt: {has_secondary}, Ø Laufzeit: {duration_days} Tage",
        )

    # =========================================================================
    # Das Malus-System (Punktabzüge)
    # =========================================================================
    def _evaluate_malus(self, triggers: Dict[str, Any]) -> List[MalusItem]:
        mali: List[MalusItem] = []

        # 1. Monokultur-Malus (Einzelner Anbahner > 50 %) - Gilt nur für Marktplätze, nicht für Direktkreditgeber
        is_direct_lender = triggers.get("is_direct_lender", False)
        mono_pct = triggers.get("monoculture_pct", 0.0)
        originator = triggers.get("monoculture_originator", "Hauptkreditgeber")
        if not is_direct_lender and mono_pct > 50.0:
            if mono_pct > 90.0:
                penalty = -8
            elif mono_pct >= 70.0:
                penalty = -6
            else:
                penalty = -4
            mali.append(
                MalusItem(
                    type="monoculture",
                    name="Monokultur-Malus",
                    penalty=penalty,
                    trigger_detected=True,
                    trigger_detail=f"{originator} stellt {mono_pct} % des Portfolios (>50 %)",
                    evidence_quote=f"Hohe Klumpenbildung: Über {mono_pct} % Abhängigkeit von einem Garantiekonzern.",
                )
            )

        # 2. Fristen-Mismatch-Malus
        if triggers.get("term_mismatch", False):
            detail = triggers.get(
                "term_mismatch_detail",
                "Tägliche Auszahlung mit langlaufenden Notes hinterlegt",
            )
            penalty = triggers.get("term_mismatch_penalty", -7)
            mali.append(
                MalusItem(
                    type="term_mismatch",
                    name="Fristen-Mismatch-Malus",
                    penalty=penalty,
                    trigger_detected=True,
                    trigger_detail=detail,
                    evidence_quote=detail,
                )
            )

        # 3. Related-Party- & Opazitäts-Malus
        if triggers.get("related_party_opacity", False):
            detail = triggers.get(
                "related_party_detail", "Insidergeschäfte / Schwesterfirmen-Aufschläge"
            )
            penalty = triggers.get("related_party_penalty", -10)
            mali.append(
                MalusItem(
                    type="related_party",
                    name="Related-Party- & Opazitäts-Malus",
                    penalty=penalty,
                    trigger_detected=True,
                    trigger_detail=detail,
                    evidence_quote=detail,
                )
            )

        # 4. Distressed- & Ausfall-Malus
        if triggers.get("distressed_workout", False):
            detail = triggers.get(
                "distressed_notes", "Portfolio-NPL >40 % oder gerichtliche Sanierung"
            )
            penalty = triggers.get("distressed_penalty", -20)
            mali.append(
                MalusItem(
                    type="distressed",
                    name="Distressed- & Ausfall-Malus",
                    penalty=penalty,
                    trigger_detected=True,
                    trigger_detail=detail,
                    evidence_quote=detail,
                )
            )

        # 5. Marktplatz-Anbahnerausfall- & Workout-Malus
        if triggers.get("marketplace_originator_risk", False):
            detail = triggers.get(
                "marketplace_originator_detail",
                "Wiederholte Ausfälle externer Kreditanbahner / erhebliche Pending Payments",
            )
            penalty = triggers.get("marketplace_originator_penalty", -10)
            mali.append(
                MalusItem(
                    type="marketplace_originator_risk",
                    name="Marktplatz-Anbahnerausfall-Malus",
                    penalty=penalty,
                    trigger_detected=True,
                    trigger_detail=detail,
                    evidence_quote=detail,
                )
            )

        return mali

    # =========================================================================
    # Vorsichtsprinzip & Flags
    # =========================================================================
    def _evaluate_flags(
        self,
        profile: Dict[str, Any],
        p1: PillarFactExtract,
        p2: PillarFactExtract,
        p3: PillarFactExtract,
        p4: PillarFactExtract,
    ) -> AuditFlags:
        conflict_notes: List[str] = []
        data_gaps: List[str] = []

        # Prüfe auf Treuhand-/Verwahrungs-Konflikt
        reg = profile.get("regulation", {})
        if reg.get("has_custody_conflict") or profile.get("has_conflict"):
            c_notes = profile.get("conflict_notes")
            if isinstance(c_notes, list):
                conflict_notes.extend([str(x) for x in c_notes])
            else:
                conflict_notes.append(
                    "Widersprüchliche Angaben zur treuhänderischen Verwahrung der Kundengelder."
                )

        # Prüfe auf Datenlücken (Minimalwert-Bänder)
        if p2.band_id == "Band_0_6":
            data_gaps.append(
                "Keine unabhängig testierten Finanzberichte auffindbar (Säule 2 auf Minimalwert gesetzt)."
            )
        if p3.band_id == "Band_0_7" and not profile.get(
            "collateral_and_workout", {}
        ).get("notes"):
            data_gaps.append(
                "Unzureichende Dokumentation der Besicherung oder Ausfallhistorie."
            )
        gaps = profile.get("data_gaps")
        if isinstance(gaps, list):
            data_gaps.extend([str(x) for x in gaps])

        has_conflict = len(conflict_notes) > 0

        return AuditFlags(
            has_conflict=has_conflict,
            conflict_notes=conflict_notes,
            data_gaps=data_gaps,
            sourcing_strategy=profile.get(
                "sourcing_strategy", "curated_profile_and_secondary_audits"
            ),
        )

    # =========================================================================
    # Externe Benchmarks
    # =========================================================================
    def _extract_benchmarks(self, b_data: Dict[str, Any]) -> BenchmarkMetrics:
        return BenchmarkMetrics(
            p2p_empire_safety_score=b_data.get("p2p_empire_safety_score"),
            p2p_empire_safety_band=b_data.get("p2p_empire_safety_band"),
            p2p_empire_portfolio_perf=b_data.get("p2p_empire_portfolio_perf"),
            p2p_empire_avg_return=b_data.get("p2p_empire_avg_return"),
            p2p_game_score=b_data.get("p2p_game_score"),
            p2p_game_rank=b_data.get("p2p_game_rank"),
            rethink_p2p_score=b_data.get("rethink_p2p_score"),
            rethink_p2p_rank=b_data.get("rethink_p2p_rank"),
            rethink_p2p_red_flags=b_data.get("rethink_p2p_red_flags"),
            lars_wrobbel_score=b_data.get("lars_wrobbel_score"),
            lars_wrobbel_rank=b_data.get("lars_wrobbel_rank"),
            external_review_urls=b_data.get("external_review_urls", []),
        )
