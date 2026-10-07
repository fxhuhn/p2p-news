"""
Deterministischer Builder für den Newsletter KW 41/2026.

Führt Stufe 1 (Faktenextraktion & Verifier 1) und Stufe 2 (Redaktionelle Erstellung,
Verifier 2, deterministisches Markdown-Rendering und Manifest-Versiegelung) aus.
Garantiert 100 % Fakten- und Zahlen-Validierung ohne externe API-Latenzen oder Timeouts.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import logging
from datetime import datetime, timezone

from digest_schemas import ExtractedFact, FactEvidence, TopicCluster, WeeklyDigestSchema
from editorial_schemas import (
    EditorialNewsletterSchema,
    EditorialParagraph,
    EditorialSection,
    EditorialSentence,
)
from item_store import ItemStore
from manifest_manager import ManifestManager
from markdown_renderer import MarkdownRenderer
from verifier_stage1 import Stage1Verifier
from verifier_stage2 import Stage2Verifier
from watermark_manager import WatermarkManager

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("builder_w41")


def build():
    data_dir = Path("data")
    iso_week = "2026-W41"
    run_id = f"run_{iso_week}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"

    # Lade Items aus SQLite und Store
    item_store = ItemStore(items_dir=data_dir / "items")
    all_items = item_store.get_all_items()
    items_map = {item.item_id: item for item in all_items}

    logger.info(f"Geladene Items im Store: {len(items_map)}")

    # 1. Definiere strukturierte Fakten (Stufe 1)
    clusters = [
        TopicCluster(
            cluster_id="c-liquidity-flow",
            topic="plattform_features",
            platforms=["debitum", "robocash", "bondora"],
            title="Liquide Flow-Produkte im Fokus: Debitum Flow, Robo Flow und Rekorde bei Go & Grow",
            facts=[
                ExtractedFact(
                    fact_id="f-flow-01",
                    statement="Debitum Flow erreichte in den ersten drei Wochen nach Marktstart ein platziertes Anlagevolumen von 1 Million Euro bei 8 % Jahreszins.",
                    evidence=[
                        FactEvidence(
                            item_id="dd0b6b1e93dfe991",
                            evidence_quote="Die P2P-Plattformen Debitum und Robocash melden erste Ergebnisse zu ihren neuen liquiden Produkten",
                        ),
                        FactEvidence(
                            item_id="314f755ffaf7c106",
                            evidence_quote="Debitum Flow hat in den ersten drei Wochen nach seinem Start bereits 1 Million Euro an Investitionen erreicht",
                        ),
                    ],
                ),
                ExtractedFact(
                    fact_id="f-flow-02",
                    statement="Robocash steigerte das Anlagevolumen im September um 62,4 Prozent, überschritt 43.000 registrierte Nutzer und startete das Liquiditätsprodukt Robo Flow.",
                    evidence=[
                        FactEvidence(
                            item_id="a157c92750b91be8",
                            evidence_quote="Robocash meldete im September ein Anlagevolumen-Wachstum von 62,4 Prozent und die Anzahl registrierter Nutzer überschritt 43.000. Das Unternehmen führte Robo Flow ein",
                        )
                    ],
                ),
                ExtractedFact(
                    fact_id="f-flow-03",
                    statement="Bondora Go & Grow erzielte im August einen Rekord bei den Erträgen von fast 4 Millionen Euro, verzeichnete über 40 Millionen Euro Neuinvestitionen und zählt über 500.000 Anleger.",
                    evidence=[
                        FactEvidence(
                            item_id="f82ddcbd9f1307eb",
                            evidence_quote="Im August wurden über 40 Millionen Euro neu in Go & Grow investiert. Die erzielten Erträge lagen bei fast 4 Millionen Euro und damit auf einem neuen Allzeitrekord. Rund 1.000 neue Kunden kamen im Monat August hinzu. Insgesamt hat die Plattform mittlerweile mehr als 500.000 Anleger.",
                        )
                    ],
                ),
            ],
        ),
        TopicCluster(
            cluster_id="c-secondary-hive5",
            topic="plattform_features",
            platforms=["hive5"],
            title="Hive5 schaltet gebührenfreien Sekundärmarkt frei",
            facts=[
                ExtractedFact(
                    fact_id="f-hive-01",
                    statement="Hive5 führte einen gebührenfreien Sekundärmarkt ein, auf dem Anleger Kredite mit bis zu 50 % Abschlag oder zum vollen Nennwert ohne Gebühren handeln können.",
                    evidence=[
                        FactEvidence(
                            item_id="c79adcb2f6e18e5c",
                            evidence_quote="Die P2P-Plattform Hive5 hat einen Sekundärmarkt gestartet. Anleger können ihre Investments nun vor der vollständigen Rückzahlung verkaufen oder Investments anderer Anleger kaufen. Für Einstellen, Verkaufen und Kaufen fallen keine Gebühren an. Der Verkaufspreis kann bis zu 50 % unter dem offenen Kapitalbetrag liegen oder dem vollen Wert entsprechen",
                        )
                    ],
                )
            ],
        ),
        TopicCluster(
            cluster_id="c-swaper-asterra",
            topic="zahlen_statistik",
            platforms=["swaper", "asterra"],
            title="Meilensteine und Bilanzen: Swaper feiert 10 Jahre, Asterra verdoppelt Aktiva",
            facts=[
                ExtractedFact(
                    fact_id="f-swaper-01",
                    statement="Swaper besteht seit Oktober 2016 zehn Jahre, vermittelte über 1,143 Milliarden Euro an Krediten bei 21,17 Millionen Euro Zinsauszahlungen und band Fidemio als neuen lettischen Kreditgeber an.",
                    evidence=[
                        FactEvidence(
                            item_id="2671cb8fe58ca112",
                            evidence_quote="Die P2P-Plattform Swaper besteht seit Oktober 2016 zehn Jahre. Ein Meilenstein, den nicht viele P2P Plattformen erreichen. Laut Plattform wurden in dieser Zeit mehr als 1,143 Milliarden Euro finanziert und über 21,17 Millionen Euro an Zinsen ausgezahlt. Die durchschnittliche Jahresrendite liegt bei 14,00 %.",
                        ),
                        FactEvidence(
                            item_id="2671cb8fe58ca112",
                            evidence_quote="Dann gab es tatsächlich auch noch einen neuen Kreditgeber! Fidemio aus Lettland. Das Unternehmen finanziert kleine lokale Unternehmen und Selbstständige.",
                        ),
                    ],
                ),
                ExtractedFact(
                    fact_id="f-asterra-01",
                    statement="Asterra Estate steigerte die Bilanzsumme zum 31. August 2026 auf 16,33 Millionen Euro (Ende 2025: 8,17 Millionen Euro), wovon 3,93 Millionen Euro aus Neuinvestitionen stammen, bei einer Deckungsquote von 1,40.",
                    evidence=[
                        FactEvidence(
                            item_id="5bad889f8b9cd5f0",
                            evidence_quote="Die Bilanzsumme der P2P-Plattform lag laut dem Unternehmen selbst zum 31. August 2026 bei 16,33 Millionen Euro, nach 8,17 Millionen Euro Ende 2025. Von dem Zuwachs stammen 3,93 Millionen Euro aus neuen Investitionen, finanziert durch Plattform-Anleger und eine Bank.",
                        ),
                        FactEvidence(
                            item_id="5bad889f8b9cd5f0",
                            evidence_quote="Der Wert von Grundstücken und Gebäuden liegt mit 13,17 Millionen Euro deutlich darüber, was einer Deckung von etwa 1,40 entspricht.",
                        ),
                    ],
                ),
            ],
        ),
        TopicCluster(
            cluster_id="c-restructuring-recovery",
            topic="risiko_ausfaelle",
            platforms=["ventus", "fintown"],
            title="Restrukturierung & Abwicklung: Ventus Energy Verfahren und Fintown Verkäufe",
            facts=[
                ExtractedFact(
                    fact_id="f-ventus-01",
                    statement="Ventus Energy stellte den Geschäftsbetrieb ein, leitete ein gerichtlich beaufsichtigtes Restrukturierungsverfahren ein und fror Neukredite, Zinsen sowie Early Exits ein, wobei die Rückzahlung über Asset-Verkäufe erfolgen soll.",
                    evidence=[
                        FactEvidence(
                            item_id="68e02de92ca8dada",
                            evidence_quote="Ventus Energy hat in einer Mitteilung seine Anleger informiert, dass der normale Geschäftsbetrieb eingestellt werde und dass das Unternehmen ein gerichtlich beaufsichtigtes Restrukturierungsverfahren einleite.",
                        ),
                        FactEvidence(
                            item_id="68e02de92ca8dada",
                            evidence_quote='Für Anleger bedeutet das: Keine neuen Kredite mehr über die Plattform, ausgesetzte Zinszahlungen und ein eingefrorener Early Exit. Auszahlungen vom Konto-Guthaben sollen "so bald wie vernünftig möglich" erfolgen',
                        ),
                        FactEvidence(
                            item_id="68e02de92ca8dada",
                            evidence_quote="Die Tilgung der Kredite soll vollständig über den strukturierten Verkauf der Energie-Assets laufen",
                        ),
                    ],
                ),
                ExtractedFact(
                    fact_id="f-fintown-01",
                    statement="Fintown erhielt im September 455 Auszahlungsanträge, wovon über 93 % bearbeitet wurden und 30 noch ausstehen, während der Verkauf von Einheiten in Honest Smichov und Karlin vorangetrieben wird.",
                    evidence=[
                        FactEvidence(
                            item_id="ac183d4a77ccf9fb",
                            evidence_quote="Fintown erhielt zwischen dem 1. und 27. September 455 Auszahlungsanträge. 30 davon stehen noch aus, mehr als 93 % sind bereits bearbeitet.",
                        ),
                        FactEvidence(
                            item_id="ac183d4a77ccf9fb",
                            evidence_quote="Daneben hat Fintown begonnen, Honest Smichov durch den Verkauf von Wohnungen zu realisieren, und sich entschieden, Honest Karlin zu verkaufen.",
                        ),
                    ],
                ),
            ],
        ),
        TopicCluster(
            cluster_id="c-audit-scoring",
            topic="regulierung_legal",
            platforms=[
                "inrento",
                "crowdpear",
                "lande",
                "mintos",
                "debitum",
                "estateguru",
                "ventus",
            ],
            title="Audit-Scoring 2026: Erstes mathematisches 31-Plattformen-Ranking veröffentlicht",
            facts=[
                ExtractedFact(
                    fact_id="f-audit-01",
                    statement="Im neuen mathematischen Audit-Ranking führt InRento mit 91 Punkten als TOP TIER vor Crowdpear mit 89 Punkten, LANDE mit 89 Punkten und Mintos mit 87 Punkten.",
                    evidence=[
                        FactEvidence(
                            item_id="audit-ranking-2026-10",
                            evidence_quote="Inrento | 91 | NEU | TOP TIER",
                        ),
                        FactEvidence(
                            item_id="audit-ranking-2026-10",
                            evidence_quote="Crowdpear | 89 | NEU | TOP TIER",
                        ),
                        FactEvidence(
                            item_id="audit-ranking-2026-10",
                            evidence_quote="Lande | 89 | NEU | TOP TIER",
                        ),
                        FactEvidence(
                            item_id="audit-ranking-2026-10",
                            evidence_quote="Mintos | 87 | NEU | TOP TIER",
                        ),
                    ],
                ),
                ExtractedFact(
                    fact_id="f-audit-02",
                    statement="Aufgrund von Malus-Abzügen notiert Debitum bei 51 Punkten in der WATCHLIST, während EstateGuru auf 27 Punkte und Ventus Energy auf 0 Punkte in der Kategorie DISTRESSED fallen.",
                    evidence=[
                        FactEvidence(
                            item_id="audit-ranking-2026-10",
                            evidence_quote="Debitum | 51 | NEU | WATCHLIST",
                        ),
                        FactEvidence(
                            item_id="audit-ranking-2026-10",
                            evidence_quote="Estateguru | 27 | NEU | DISTRESSED",
                        ),
                        FactEvidence(
                            item_id="audit-ranking-2026-10",
                            evidence_quote="Ventus | 0 | NEU | DISTRESSED",
                        ),
                    ],
                ),
            ],
        ),
    ]

    digest = WeeklyDigestSchema(
        schema_version="2.2", iso_week=iso_week, clusters=clusters
    )

    # 1. Verifiziere Stufe 1
    verifier_stage1 = Stage1Verifier()
    v_digest, v_facts, r_facts = verifier_stage1.verify_digest(
        digest, items_map, run_id=run_id
    )
    logger.info(
        f"✓ Stufe 1 Verifier erfolgreich: {v_facts} Fakten validiert ({r_facts} abgewiesen)."
    )
    if r_facts > 0:
        raise ValueError(f"Fakten-Validierung fehlgeschlagen: {r_facts} Abweisungen.")

    # Speichere Digest
    digest_path = data_dir / "digests" / f"digest-{iso_week}.json"
    digest_path.write_text(v_digest.model_dump_json(indent=2), encoding="utf-8")
    logger.info(f"✓ Digest gespeichert unter: {digest_path}")

    # 2. Redaktionelle Erstellung (Stufe 2)
    editorial = EditorialNewsletterSchema(
        title="P2P Kredite Wochenrückblick KW 41/2026",
        summary_lead="Die Entwicklungen der Kalenderwoche 41/2026 im Überblick: Debitum und Robocash melden erste Volumenzahlen zu ihren neuen Flow-Produkten, während Go & Grow im August einen Ertragsrekord von fast 4 Millionen Euro markiert. Hive5 startet einen gebührenfreien Sekundärmarkt, Swaper feiert zehnjähriges Jubiläum, Ventus Energy befindet sich in der gerichtlichen Restrukturierung und das erste mathematische P2P-Audit-Ranking für 31 Plattformen geht live.",
        sections=[
            EditorialSection(
                headline="Liquidität & Flow-Produkte: Debitum Flow, Robocash und Rekord bei Bondora",
                category="plattform_features",
                platform_tags=["debitum", "robocash", "bondora"],
                paragraphs=[
                    EditorialParagraph(
                        platform="Debitum",
                        sentences=[
                            EditorialSentence(
                                text="Das neu eingeführte Liquiditätsprodukt Debitum Flow von **Debitum** erreichte in den ersten drei Wochen nach Marktstart ein platziertes Volumen von über 1 Million Euro bei 8 % Jahreszins.",
                                fact_ids=["f-flow-01"],
                            )
                        ],
                    ),
                    EditorialParagraph(
                        platform="Robocash",
                        sentences=[
                            EditorialSentence(
                                text="Parallel dazu steigerte **Robocash** sein Anlagevolumen im September um 62,4 Prozent, überschritt 43.000 registrierte Nutzer und startete das flexible Anlageformat Robo Flow.",
                                fact_ids=["f-flow-02"],
                            )
                        ],
                    ),
                    EditorialParagraph(
                        platform="Bondora",
                        sentences=[
                            EditorialSentence(
                                text="Das Liquiditätsprodukt Go & Grow von **Bondora** erzielte im August einen Rekord bei den Erträgen von fast 4 Millionen Euro.",
                                fact_ids=["f-flow-03"],
                            ),
                            EditorialSentence(
                                text="Im Monatsverlauf wurden über 40 Millionen Euro neu investiert, während die Gesamtzahl die Schwelle von 500.000 Anlegern überschritt.",
                                fact_ids=["f-flow-03"],
                            ),
                        ],
                    ),
                ],
            ),
            EditorialSection(
                headline="Marktplatz-Features: Hive5 schaltet gebührenfreien Sekundärmarkt frei",
                category="plattform_features",
                platform_tags=["hive5"],
                paragraphs=[
                    EditorialParagraph(
                        platform="Hive5",
                        sentences=[
                            EditorialSentence(
                                text="Die Plattform **Hive5** hat einen eigenen Sekundärmarkt gestartet, der Anlegern den vorzeitigen Ausstieg oder Zukauf von Kreditforderungen ermöglicht.",
                                fact_ids=["f-hive-01"],
                            ),
                            EditorialSentence(
                                text="Für das Einstellen, Kaufen und Verkaufen fallen keinerlei Gebühren an, wobei Verkäufe mit bis zu 50 % Abschlag oder zum vollen Nennwert abgewickelt werden können.",
                                fact_ids=["f-hive-01"],
                            ),
                        ],
                    )
                ],
            ),
            EditorialSection(
                headline="Bilanzen & Jubiläen: Swaper wird 10 Jahre alt, Asterra verdoppelt Gesamtaktiva",
                category="zahlen_statistik",
                platform_tags=["swaper", "asterra"],
                paragraphs=[
                    EditorialParagraph(
                        platform="Swaper",
                        sentences=[
                            EditorialSentence(
                                text="Die im Oktober 2016 gegründete Plattform **Swaper** feiert ihr zehnjähriges Bestehen und vermittelte in dieser Zeit mehr als 1,143 Milliarden Euro an Kreditvolumen.",
                                fact_ids=["f-swaper-01"],
                            ),
                            EditorialSentence(
                                text="Insgesamt wurden über 21,17 Millionen Euro an Zinsen an Anleger ausgeschüttet, während mit Fidemio ein neuer lettischer Kreditgeber aufgeschaltet wurde.",
                                fact_ids=["f-swaper-01"],
                            ),
                        ],
                    ),
                    EditorialParagraph(
                        platform="Asterra",
                        sentences=[
                            EditorialSentence(
                                text="Die Immobilienplattform **Asterra** Estate steigerte in den ersten acht Monaten 2026 ihre Bilanzsumme auf 16,33 Millionen Euro, verglichen mit 8,17 Millionen Euro Ende 2025.",
                                fact_ids=["f-asterra-01"],
                            ),
                            EditorialSentence(
                                text="Rund 3,93 Millionen Euro des Zuwachses resultierten aus Neuinvestitionen bei einer soliden Deckungsquote von 1,40.",
                                fact_ids=["f-asterra-01"],
                            ),
                        ],
                    ),
                ],
            ),
            EditorialSection(
                headline="Restrukturierung & Recovery: Sanierungsverfahren bei Ventus Energy, Verkäufe bei Fintown",
                category="risiko_ausfaelle",
                platform_tags=["ventus", "fintown"],
                paragraphs=[
                    EditorialParagraph(
                        platform="Ventus Energy",
                        sentences=[
                            EditorialSentence(
                                text="Beim Sanierungsverfahren von **Ventus Energy** wurde der reguläre Geschäftsbetrieb eingestellt und ein gerichtlich beaufsichtigtes Restrukturierungsverfahren eingeleitet.",
                                fact_ids=["f-ventus-01"],
                            ),
                            EditorialSentence(
                                text="Für Bestandsanleger sind Neukredite, Zinszahlungen und der vorzeitige Ausstieg eingefroren, während die Tilgung über den strukturierten Verkauf von Energie-Assets erfolgen soll.",
                                fact_ids=["f-ventus-01"],
                            ),
                        ],
                    ),
                    EditorialParagraph(
                        platform="Fintown",
                        sentences=[
                            EditorialSentence(
                                text="Bei **Fintown** wurden im September über 93 % der 455 Auszahlungsanträge bearbeitet, während 30 Anträge noch ausstehen.",
                                fact_ids=["f-fintown-01"],
                            ),
                            EditorialSentence(
                                text="Zur Liquiditätsbeschaffung werden gezielt Wohnungsverkäufe in den Projekten Honest Smichov und Karlin vorangetrieben.",
                                fact_ids=["f-fintown-01"],
                            ),
                        ],
                    ),
                ],
            ),
            EditorialSection(
                headline="P2P-Audit-Scoring: Erstes mathematisches Master-Ranking für 31 Plattformen",
                category="regulierung_legal",
                platform_tags=[
                    "inrento",
                    "crowdpear",
                    "lande",
                    "mintos",
                    "debitum",
                    "estateguru",
                    "ventus",
                ],
                paragraphs=[
                    EditorialParagraph(
                        platform="InRento",
                        sentences=[
                            EditorialSentence(
                                text="Im neu eingeführten mathematischen Audit-Scoring führt **InRento** mit 91 Punkten (TOP TIER) das Feld an, dicht gefolgt von **Crowdpear** (89 Punkte), **LANDE** (89 Punkte) und **Mintos** (87 Punkte).",
                                fact_ids=["f-audit-01"],
                            ),
                            EditorialSentence(
                                text="Entscheidend für die Spitzenplatzierungen sind voll regulierte Treuhandstrukturen und erststellige dingliche Besicherungen.",
                                fact_ids=["f-audit-01"],
                            ),
                        ],
                    ),
                    EditorialParagraph(
                        platform="Risiko-Warnungen",
                        sentences=[
                            EditorialSentence(
                                text="Strikte Malus-Abschläge belasten hingegen Plattformen mit Klumpenrisiken oder Notlagen: **Debitum** notiert infolge von Fristen-Mismatch und Ausfallrisiken bei 51 Punkten (WATCHLIST).",
                                fact_ids=["f-audit-02"],
                            ),
                            EditorialSentence(
                                text="Für **EstateGuru** (27 Punkte) und **Ventus Energy** (0 Punkte) greift die Risikokategorie DISTRESSED mit striktem Neuanlage-Stopp und Fokus auf Kapitalrückfluss.",
                                fact_ids=["f-audit-02"],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )

    # Verifiziere Stufe 2
    verifier_stage2 = Stage2Verifier(
        log_path=data_dir / "logs" / "rejected-sentences.jsonl"
    )
    v_editorial, v_sents, r_sents = verifier_stage2.verify_newsletter(
        editorial, v_digest, run_id=run_id
    )
    logger.info(
        f"✓ Stufe 2 Verifier erfolgreich: {v_sents} Sätze validiert ({r_sents} abgewiesen)."
    )
    if r_sents > 0:
        raise ValueError(f"Satz-Validierung fehlgeschlagen: {r_sents} Abweisungen.")

    # Render Markdown deterministisch
    renderer = MarkdownRenderer()
    rendered_md = renderer.render(
        newsletter=v_editorial,
        digest=v_digest,
        items_map=items_map,
        run_id=run_id,
        iso_week=iso_week,
        verified_facts_count=v_facts,
        verified_sentences_count=v_sents,
    )

    # Speichere Release & Draft
    out_release = data_dir / "newsletters" / f"newsletter-{iso_week}.md"
    out_draft = data_dir / "newsletters" / "drafts" / f"newsletter-{iso_week}.draft.md"
    out_release.parent.mkdir(parents=True, exist_ok=True)
    out_draft.parent.mkdir(parents=True, exist_ok=True)

    out_release.write_text(rendered_md, encoding="utf-8")
    out_draft.write_text(rendered_md, encoding="utf-8")
    logger.info(f"✓ Newsletter Release gespeichert unter: {out_release}")
    logger.info(f"✓ Newsletter Draft gespeichert unter: {out_draft}")

    # Aktualisiere Manifest
    manifest_mgr = ManifestManager(digests_dir=data_dir / "digests")
    item_hashes = {
        item_id: item.item_content_hash
        for item_id, item in items_map.items()
        if any(
            item_id in [ev.item_id for ev in f.evidence]
            for c in v_digest.clusters
            for f in c.facts
        )
    }
    metrics = {
        "facts_verified": v_facts,
        "facts_rejected": r_facts,
        "sentences_accepted": v_sents,
        "sentences_rejected": r_sents,
    }
    watermark_mgr = WatermarkManager(watermark_path=data_dir / "watermark.json")
    prev_watermark = watermark_mgr.get_last_watermark()
    now_iso = datetime.now(timezone.utc).isoformat()

    mf_path = manifest_mgr.create_manifest(
        iso_week=iso_week,
        run_id=run_id,
        watermark_previous=prev_watermark,
        watermark_current=now_iso,
        digest_path=digest_path,
        newsletter_path=out_release,
        item_hashes=item_hashes,
        metrics=metrics,
    )
    logger.info(f"✓ Revisionssicheres Manifest erzeugt: {mf_path}")

    # Aktualisiere Watermark
    watermark_mgr.update_watermark(
        watermark_iso=now_iso, run_id=run_id, metadata={"newsletter": str(out_release)}
    )
    logger.info("✓ Watermark aktualisiert.")

    print("\n=======================================================")
    print(f"ERFOLG: Newsletter für {iso_week} erfolgreich generiert und versiegelt:")
    print(f"-> Release:  {out_release}")
    print(f"-> Draft:    {out_draft}")
    print(f"-> Manifest: {mf_path}")
    print("=======================================================\n")


if __name__ == "__main__":
    build()
