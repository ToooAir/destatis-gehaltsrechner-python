#!/usr/bin/env python3
"""
Destatis Gehaltsvergleich - 德國薪資估算工具 (Python 版)
係數來源: coefficients.json (從 service.destatis.de/DE/gehaltsvergleich app.js 提取)
"""

import math
import json
from pathlib import Path


def load_models(json_path: str = None) -> dict:
    """載入係數 JSON 檔，並自動補充 frauen 模型（gesamt - GPG）"""
    if json_path is None:
        json_path = Path(__file__).parent / "coefficients.json"
    with open(json_path, "r", encoding="utf-8") as f:
        models = json.load(f)
    # frauen = gesamt 但 GPG 套用（gesamt 本身不主動套用 GPG，需外部判斷）
    if "frauen" not in models:
        models["frauen"] = dict(models["gesamt"])
    return models


def _berf_erfahrung_koef(modell: dict, ef59u3_key: str, berufsjahre: float) -> float:
    """
    年資效果（含週工時群組基準修正）
    對應 JS 的 xn(e, n) 函式
    """
    i = modell.get("BE", 0)
    r = modell.get("BE_quad", 0)
    referenz = {
        "EF59U3_11": 10.25,
        "EF59U3_12": 13.25,
        "EF59U3_13": 13.25,
        "EF59U3_14": 13.75,
        "EF59U3_15": 16.25,
        "EF59U3_16": 19.25,
    }
    t = referenz.get(ef59u3_key, 13.25)
    a = berufsjahre - t - 6
    s = a * i + a * a * r
    return max(0.0, s)


def _ausbildung_koef(modell: dict, ausbildungsjahre: float) -> float:
    """
    教育年數效果（含截斷點修正）
    對應 JS 的 Tn(e) 函式
    """
    n = modell.get("EF40_1", 0)
    i = modell.get("EF40_Quad", 0)
    return ausbildungsjahre * n + ausbildungsjahre ** 2 * i


def _lead_anfn_koef(modell: dict, kldb_code: str) -> float:
    """
    職位層級係數（管理職 + 技能層級）
    對應 JS 的 Bn(e) 函式

    KldB 代碼規則：
      最後一碼 = 技能層級 (1=Helfer, 2=Fachkraft, 3=Spezialist, 4=Experte)
      倒數第二碼 = 9 表示管理職 (Führungskraft)
    """
    lead1 = modell.get("Lead1", 0)
    lead0 = modell.get("Lead0", 0)
    anfn_map = {
        "1": modell.get("AnfN1", 0),
        "2": modell.get("AnfN2", 0),
        "3": modell.get("AnfN3", 0),
        "4": modell.get("AnfN4", 0),
    }
    last = kldb_code[-1] if kldb_code else ""
    second_last = kldb_code[-2:-1] if len(kldb_code) >= 2 else ""
    u = lead1 if second_last == "9" else lead0
    l = anfn_map.get(last, 0)
    return u + l


def schaetze_monatsgehalt(
    berufsjahre: float,
    ausbildungsjahre: float,
    ef59u3_key: str,
    unternehmen_key: str,
    bundesland_key: str,
    kldb_code: str,
    vollzeit: bool = True,
    geschlecht: str = "gesamt",
    befristet: bool = False,
    models: dict = None,
) -> dict:
    """
    估算德國月薪（稅前 Bruttogehalt 中位數）

    參數說明：
      berufsjahre      工作年資（年）
      ausbildungsjahre 學歷教育年數（例：大學=17, 碩士=19）
      ef59u3_key       週工時群組（EF59U3_11~16）
      unternehmen_key  企業規模（UNGr_UN1~6）
      bundesland_key   聯邦州（EF13_101~116）
      kldb_code        KldB 2010 職業代碼（3位數，例 "423"）
      vollzeit         True=全職 / False=兼職
      geschlecht       模型選擇："gesamt" / "maenner" / "frauen"
      befristet        True=臨時合約 / False=無限期合約
      models           預載的係數字典（None 時自動從 coefficients.json 讀取）
    """
    if models is None:
        models = load_models()

    modell = models.get(geschlecht, models["gesamt"])
    linear = 0.0
    beitrage = {}

    # 1. 截距
    v = modell.get("Intercept", 0)
    linear += v; beitrage["Intercept"] = v

    # 2. 年資（含工時基準修正）
    v = _berf_erfahrung_koef(modell, ef59u3_key, berufsjahre)
    linear += v; beitrage["Berufserfahrung"] = v

    # 3. 教育年數
    v = _ausbildung_koef(modell, ausbildungsjahre)
    linear += v; beitrage["Ausbildungsjahre"] = v

    # 4. 週工時群組
    v = modell.get(ef59u3_key, 0.0)
    linear += v; beitrage["Arbeitszeit"] = v

    # 5. 企業規模
    v = modell.get(unternehmen_key, 0.0)
    linear += v; beitrage["Unternehmensgröße"] = v

    # 6. 聯邦州
    v = modell.get(bundesland_key, 0.0)
    linear += v; beitrage["Bundesland"] = v

    # 7. 職業代碼（KldB）
    berufs_koef = 0.0
    for length in [3, 2]:
        candidate = kldb_code[:length]
        if candidate in modell:
            berufs_koef = modell[candidate]
            break
    linear += berufs_koef; beitrage["Berufsgruppe (KldB)"] = berufs_koef

    # 8. 職位層級（Lead + AnfN）
    v = _lead_anfn_koef(modell, kldb_code)
    linear += v; beitrage["Führung/Niveau"] = v

    # 9. 雇用形式
    v = modell.get("EF58_1D1" if vollzeit else "EF58_1D0", 0.0)
    linear += v; beitrage["Beschäftigungsart"] = v

    # 10. 臨時合約
    v = modell.get("EF17BefrD1" if befristet else "EF17BefrD0", 0.0)
    linear += v; beitrage["Befristung"] = v

    # 11. 性別工資差距（frauen 模型專用）
    gpg = 0.0
    if geschlecht == "frauen":
        gpg = modell.get("GPG", 0.0)
        linear += gpg
    beitrage["GPG"] = gpg

    return {
        "linear_predictor": round(linear, 6),
        "median_monatsgehalt_brutto": round(math.exp(linear), 2),
        "beitrage": {k: round(v, 6) for k, v in beitrage.items()},
        "modell": geschlecht,
    }


def formatiere_ergebnis(ergebnis: dict) -> str:
    gehalt = ergebnis["median_monatsgehalt_brutto"]
    lines = [
        "=" * 52,
        f"  Modell: {ergebnis['modell']}",
        f"  Geschätztes Monatsgehalt (Median, Brutto)",
        "=" * 52,
        f"  → {gehalt:>10,.0f} €/Monat",
        f"  → {gehalt * 12:>10,.0f} €/Jahr",
        "",
        "  Beiträge:",
        "  " + "-" * 48,
    ]
    for k, v in ergebnis["beitrage"].items():
        if v != 0:
            lines.append(f"  {k:<30} {v:+.4f}")
    lines += [
        "  " + "-" * 48,
        f"  {'Summe (ln)':<30} {ergebnis['linear_predictor']:+.4f}",
        f"  {'exp(Summe)':<30} = {gehalt:,.0f} €",
        "=" * 52,
    ]
    return "\n".join(lines)


# ─── 使用範例 ──────────────────────────────────────────────
if __name__ == "__main__":
    MODELS = load_models()  # 只載入一次，可傳入多次呼叫

    print("\n【範例】Backend 工程師, Hamburg, 碩士, 10年, ≥1000人公司")
    result = schaetze_monatsgehalt(
        berufsjahre=10,
        ausbildungsjahre=19,        # 碩士
        ef59u3_key="EF59U3_15",     # 40小時/週
        unternehmen_key="UNGr_UN6", # ≥1000人
        bundesland_key="EF13_102",  # Hamburg
        kldb_code="434",            # IT 專案管理 Experte
        vollzeit=True,
        geschlecht="maenner",
        befristet=False,
        models=MODELS,
    )
    print(formatiere_ergebnis(result))