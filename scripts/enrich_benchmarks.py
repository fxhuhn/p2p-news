import glob
import re

import httpx
import yaml
from bs4 import BeautifulSoup


def enrich_all_benchmarks():
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}

    # 1. Scrape Rethink P2P
    print("Scrape re:think P2P...")
    rethink_map = {}
    try:
        r = httpx.get(
            "https://rethink-p2p.de/sicherste-p2p-plattformen/",
            headers=headers,
            follow_redirects=True,
            timeout=20.0,
        )
        soup = BeautifulSoup(r.text, "html.parser")
        table = soup.find("table", class_="ss-table")
        if table:
            for tr in table.find_all("tr")[1:]:
                cols = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
                if len(cols) >= 9:
                    rank, name, reg, fin, tra, kred, track, rf, score = cols[:9]
                    key = name.lower().replace(" ", "").replace("-", "")
                    rethink_map[key] = {
                        "raw_name": name,
                        "rank": f"Platz {rank}",
                        "score": float(score.replace(",", ".")),
                        "red_flags": rf,
                    }
        print(f"✓ re:think P2P: {len(rethink_map)} Plattformen geladen.")
    except Exception as e:
        print(f"Fehler bei re:think P2P: {e}")

    # 2. Scrape P2P Game
    print("Scrape P2P Game...")
    game_map = {}
    try:
        r2 = httpx.get(
            "https://p2p-game.com/p2p-ratings",
            headers=headers,
            follow_redirects=True,
            timeout=20.0,
        )
        soup2 = BeautifulSoup(r2.text, "html.parser")
        panels = soup2.find_all("div", class_="sue-panel")
        for p in panels:
            text = p.get_text(" ", strip=True)
            m_score = re.search(r"(\d+)\s*/100\s+Platz\s+(\d+)\s+von\s+(\d+)", text)
            links = p.find_all("a")
            m_name = None
            for link_tag in links:
                lt = link_tag.get_text(strip=True)
                m_exp = re.search(r"Meine\s+(.*?)\s+Erfahrungen", lt, re.I)
                if m_exp:
                    m_name = m_exp.group(1).strip()
                    break
            if not m_name:
                for link_tag in links:
                    lt = link_tag.get_text(strip=True)
                    if lt and not lt.startswith("ZUM") and "+" not in lt:
                        m_name = lt
                        break
            if m_score and m_name:
                score_val = int(m_score.group(1))
                rank_val = int(m_score.group(2))
                key = m_name.lower().replace(" ", "").replace("-", "")
                game_map[key] = {
                    "raw_name": m_name,
                    "rank": f"Platz {rank_val} von 40",
                    "score": score_val,
                }
        print(f"✓ P2P Game: {len(game_map)} Plattformen geladen.")
    except Exception as e:
        print(f"Fehler bei P2P Game: {e}")

    # 3. Aktualisiere profile.yaml aller 31 Plattformen
    profiles = sorted(glob.glob("data/platforms/*/profile.yaml"))
    print(f"\nAktualisiere {len(profiles)} Profile...")
    updated_count = 0

    for p_path in profiles:
        with open(p_path, "r", encoding="utf-8") as f:
            prof = yaml.safe_load(f)

        plat = prof.get("platform")
        clean_p = plat.lower().replace(" ", "").replace("-", "")

        bench = prof.get("benchmarks", {})

        # Match rethink-p2p
        r_match = None
        for k, v in rethink_map.items():
            if (
                clean_p in k
                or k in clean_p
                or (plat == "income" and "income" in k)
                or (plat == "monefit" and "monefit" in k)
                or (plat == "insoil" and "insoil" in k)
            ):
                r_match = v
                break

        if r_match:
            bench["rethink_p2p_score"] = r_match["score"]
            bench["rethink_p2p_rank"] = r_match["rank"]
            bench["rethink_p2p_red_flags"] = r_match["red_flags"]
        else:
            bench["rethink_p2p_score"] = None
            bench["rethink_p2p_rank"] = "Nicht gelistet"
            bench["rethink_p2p_red_flags"] = None

        # Match p2p-game
        g_match = None
        for k, v in game_map.items():
            if (
                clean_p in k
                or k in clean_p
                or (plat == "income" and "income" in k)
                or (plat == "monefit" and "monefit" in k)
                or (plat == "insoil" and "heavy" in k)
            ):
                g_match = v
                break

        if g_match:
            bench["p2p_game_score"] = g_match["score"]
            bench["p2p_game_rank"] = g_match["rank"]
        else:
            bench["p2p_game_score"] = None
            bench["p2p_game_rank"] = "Nicht gelistet"

        prof["benchmarks"] = bench

        with open(p_path, "w", encoding="utf-8") as f:
            yaml.dump(prof, f, allow_unicode=True, sort_keys=False)

        updated_count += 1
        r_info = (
            f"{bench['rethink_p2p_score']}/10" if bench["rethink_p2p_score"] else "-"
        )
        g_info = f"{bench['p2p_game_score']}/100" if bench["p2p_game_score"] else "-"
        print(f"✓ {plat:<15} -> re:think: {r_info:<6} | P2P-Game: {g_info}")

    print(
        f"\nErfolgreich {updated_count} Profile mit re:think P2P und P2P-Game Daten angereichert!"
    )


if __name__ == "__main__":
    enrich_all_benchmarks()
