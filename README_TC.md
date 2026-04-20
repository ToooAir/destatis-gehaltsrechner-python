# README — Destatis Gehaltsvergleich Python 薪資估算工具

[👉 English Version (英文版說明)](README.md)

> **⚠️ 免責聲明 (Disclaimer)**  
> 本專案為非官方工具。所使用之模型係數與計算邏輯均提取自德國聯邦統計局 (Destatis) 公開之薪資比較器前端網頁 (`app.js`)，並非透過官方 API 或官方授權套件取得。估算結果僅供參考，實際薪資會受市場波動、個人談判能力及其他未涵蓋之變數影響。本專案不對計算結果的準確性或適用性承擔任何法律責任。

***

## 目錄

1. [專案說明](#1-%E5%B0%88%E6%A1%88%E8%AA%AA%E6%98%8E)
2. [快速開始](#2-%E5%BF%AB%E9%80%9F%E9%96%8B%E5%A7%8B)
3. [參數完整說明](#3-%E5%8F%83%E6%95%B8%E5%AE%8C%E6%95%B4%E8%AA%AA%E6%98%8E)
    - [berufsjahre — 工作年資](#31-berufsjahre--%E5%B7%A5%E4%BD%9C%E5%B9%B4%E8%B3%87)
    - [ausbildungsjahre — 教育年數](#32-ausbildungsjahre--%E6%95%99%E8%82%B2%E5%B9%B4%E6%95%B8)
    - [ef59u3_key — 週工時群組](#33-ef59u3_key--%E9%80%B1%E5%B7%A5%E6%99%82%E7%BE%A4%E7%B5%84)
    - [unternehmen_key — 企業規模](#34-unternehmen_key--%E4%BC%81%E6%A5%AD%E8%A6%8F%E6%A8%A1)
    - [bundesland_key — 聯邦州](#35-bundesland_key--%E8%81%AF%E9%82%A6%E5%B7%9E)
    - [kldb_code — 職業代碼](#36-kldb_code--%E8%81%B7%E6%A5%AD%E4%BB%A3%E7%A2%BC-kldb-2010)
    - [vollzeit — 全職/兼職](#37-vollzeit--%E5%85%A8%E8%81%B7%E5%85%BC%E8%81%B7)
    - [geschlecht — 模型選擇](#38-geschlecht--%E6%A8%A1%E5%9E%8B%E9%81%B8%E6%93%87)
    - [befristet — 合約類型](#39-befristet--%E5%90%88%E7%B4%84%E9%A1%9E%E5%9E%8B)
4. [KldB 完整職業代碼表](#4-kldb-%E5%AE%8C%E6%95%B4%E8%81%B7%E6%A5%AD%E4%BB%A3%E7%A2%BC%E8%A1%A8)
5. [模型原理](#5-%E6%A8%A1%E5%9E%8B%E5%8E%9F%E7%90%86)
6. [使用範例](#6-%E4%BD%BF%E7%94%A8%E7%AF%84%E4%BE%8B)
7. [注意事項](#7-%E6%B3%A8%E6%84%8F%E4%BA%8B%E9%A0%85)

***

## 1. 專案說明

本工具依據德國聯邦統計局（[Statistisches Bundesamt / Destatis](https://service.destatis.de/DE/gehaltsvergleich/)）公開的「**Gehaltsvergleich**（薪資比較器）」，將其前端 `app.js` 中的**對數線性迴歸模型（OLS log-linear regression）**轉譯為 Python，用於估算德國**稅前月薪中位數（Bruttogehalt Median）**。

```
檔案結構：
destatis-gehaltsrechner-python/
├── salary_calculator/
│   ├── coefficients.json     ← 全部迴歸係數（從 app.js 提取）
│   └── __init__.py           ← 主計算程式
├── README.md                 ← 英文說明文件
└── README_TC.md              ← 本說明文件
```


***

## 2. 快速開始

```python
from salary_calculator import load_models, schaetze_monatsgehalt, formatiere_ergebnis

MODELS = load_models("coefficients.json")

result = schaetze_monatsgehalt(
    berufsjahre=5,
    ausbildungsjahre=19,
    ef59u3_key="EF59U3_15",
    unternehmen_key="EF13_101",
    bundesland_key="EF13_101",
    kldb_code="434",
    vollzeit=True,
    geschlecht="maenner",
    befristet=False,
    models=MODELS,
)
print(formatiere_ergebnis(result))
```


***

## 3. 參數完整說明


***

### 3.1 `berufsjahre` — 工作年資

**類型：** `float`
**範圍：** `0` ～ `51`（年）
**說明：** 在同領域或同職業的**總工作年數**，非人生年齡。

```python
berufsjahre = 5    # 5年工作經驗
berufsjahre = 0    # 剛入職/應屆
berufsjahre = 20   # 資深職員
```

> **注意：** 薪資效益並非線性成長，模型使用二次函式（含 `BE_quad` 負係數），反映年資越高、邊際加薪效益越低的現實。

***

### 3.2 `ausbildungsjahre` — 教育年數

**類型：** `float`
**說明：** 從小學到最高學歷結束的**正規教育總年數**。


| 學歷程度 | 年數 | 說明 |
| :-- | :-- | :-- |
| 無正式學歷 | 9 | 僅義務教育（Hauptschule） |
| Hauptschulabschluss + 職訓 | 12 | 初中畢業 + Ausbildung |
| Mittlere Reife + 職訓 | 13 | 中學畢業 + Ausbildung |
| Abitur（高中畢業） | 13 | 不含大學 |
| Abitur + Ausbildung（雙軌） | 15 | 高中 + 職業訓練 |
| Bachelor（學士，3年） | 16 | 13年學校 + 3年大學 |
| Bachelor（學士，4年） | 17 | 13年學校 + 4年大學 |
| Master / Diplom（碩士） | 18–19 | 13年學校 + 5–6年大學 |
| Staatsexamen（法律/醫學） | 19–20 | 含實習年 |
| Promotion（博士） | 21–23 | 含博士年限 |

```python
ausbildungsjahre = 19   # 碩士學歷
ausbildungsjahre = 17   # 學士學歷
ausbildungsjahre = 13   # 職業訓練（Ausbildung）
```


***

### 3.3 `ef59u3_key` — 週工時群組

**類型：** `str`
**說明：** 選擇最接近你**每週實際工作時數**的區間。


| 參數值 | 每週工時 | 典型場景 | 薪資影響（vs 21–32h） |
| :-- | :-- | :-- | :-- |
| `"EF59U3_11"` | ≤ 20 小時 | 少量兼職 | −5.7% |
| `"EF59U3_12"` | 21–32 小時 | 一般兼職（**參照組**） | ± 0% |
| `"EF59U3_13"` | 33–36 小時 | 縮短全職（Teilzeit） | +10.1% |
| `"EF59U3_14"` | 37–39 小時 | TVöD 公務員標準 | +11.5% |
| `"EF59U3_15"` | 40 小時 | 一般私部門全職 | +21.6% |
| `"EF59U3_16"` | ≥ 41 小時 | 超時工作 | +30.2% |

```python
ef59u3_key = "EF59U3_15"   # 一般全職，每週40小時
ef59u3_key = "EF59U3_14"   # 公務員/TVöD，每週38.5小時
```

> **重要：** 此參數同時影響年資效益的計算基準。週工時越長，年資帶來的薪資成長略有不同。

***

### 3.4 `unternehmen_key` — 企業規模

**類型：** `str`
**說明：** 依公司**全體員工總人數**選擇，規模越大薪資通常越高。


| 參數值 | 員工人數 | 薪資係數 | 對比大企業 |
| :-- | :-- | :-- | :-- |
| `"UNGr_UN1"` | 1–9 人 | −0.176 | 約少 **16%** |
| `"UNGr_UN2"` | 10–49 人 | −0.108 | 約少 **10%** |
| `"UNGr_UN3"` | 50–249 人 | −0.070 | 約少 **7%** |
| `"UNGr_UN4"` | 250–499 人 | −0.042 | 約少 **4%** |
| `"UNGr_UN5"` | 500–999 人 | −0.026 | 約少 **3%** |
| `"UNGr_UN6"` | ≥ 1000 人 | 0（**參照組**） | 基準 |

```python
unternehmen_key = "UNGr_UN6"   # 大型企業（如 SAP、Deutsche Bahn）
unternehmen_key = "UNGr_UN3"   # 中型企業（50–249人）
unternehmen_key = "UNGr_UN2"   # 小型公司（10–49人）
```


***

### 3.5 `bundesland_key` — 聯邦州

**類型：** `str`
**說明：** 你工作地點所在的德國聯邦州。參照組為 **NRW（`EF13_105`）**，係數為 0。


| 參數值 | 聯邦州 | 係數 | 地區 |
| :-- | :-- | :-- | :-- |
| `"EF13_101"` | Schleswig-Holstein | −0.015 | 北部 |
| `"EF13_102"` | Hamburg | +0.031 | 北部 |
| `"EF13_103"` | Niedersachsen | −0.001 | 北部 |
| `"EF13_104"` | Bremen | −0.003 | 北部 |
| `"EF13_105"` | Nordrhein-Westfalen | 0（**參照組**） | 西部 |
| `"EF13_106"` | Hessen | +0.029 | 西部 |
| `"EF13_107"` | Rheinland-Pfalz | −0.003 | 西部 |
| `"EF13_108"` | Baden-Württemberg | +0.052 | 南部 ⬆ |
| `"EF13_109"` | Bayern | +0.034 | 南部 ⬆ |
| `"EF13_110"` | Saarland | −0.002 | 西南 |
| `"EF13_111"` | Berlin | −0.011 | 東部/首都 |
| `"EF13_112"` | Brandenburg | −0.084 | 東部 |
| `"EF13_113"` | Mecklenburg-Vorpommern | −0.094 | 東部 |
| `"EF13_114"` | Sachsen | −0.114 | 東部 ⬇ |
| `"EF13_115"` | Sachsen-Anhalt | −0.103 | 東部 ⬇ |
| `"EF13_116"` | Thüringen | −0.103 | 東部 ⬇ |

```python
bundesland_key = "EF13_101"   # Schleswig-Holstein（你的所在地）
bundesland_key = "EF13_102"   # Hamburg（鄰近大城市）
bundesland_key = "EF13_108"   # Baden-Württemberg（薪資最高州）
```

> 東西德薪資差距明顯：東部各州普遍低 **8–11%**，西南部（BW/Bayern）高 **3–5%**。

***

### 3.6 `kldb_code` — 職業代碼（KldB 2010）

**類型：** `str`（3位數字符串）
**說明：** 使用德國**職業分類 KldB 2010** 的三位數代碼，是影響薪資最大的單一參數。

#### 代碼結構

```
代碼格式：  X  Y  Z
            │  │  └── 最後一碼：技能層級（Anforderungsniveau）
            │  └───── 中間一碼：職業群組（Berufsgruppe）
            └──────── 第一碼：職業大類（Berufshauptgruppe）
```


#### 最後一碼 Z — 技能層級（最重要！）

| 末碼 | 技能層級 | 對應學歷 | 說明 |
| :-- | :-- | :-- | :-- |
| `1` | Helfer / Anlernkräfte | 無特殊學歷 | 輔助工、學習中 |
| `2` | Fachkräfte | 職業訓練（Ausbildung） | 合格技術工 |
| `3` | Spezialist/innen | Meister / Techniker / FH | 進階技術/管理 |
| `4` | Expert/innen | 大學學士以上 | 工程師、學術職位 |

> **倒數第二碼為 `9`** 時，表示**管理職（Führungskraft）**，模型會額外加上 `Lead1` 係數（約 +8–9%）。例：`439` = IT 管理主管。

***

## 4. KldB 完整職業代碼表

代碼由 **前兩碼（大類）+ 末碼（技能層級）** 組成。查詢自己的職業代碼，可至官網搜尋：[klassifikationsserver.de](https://www.klassifikationsserver.de/klassService/thyme/variant/kldb2010)

### 大類 01–12：農業、林業、園藝

| 代碼前綴 | 職業群組 |
| :-- | :-- |
| `011x` | 農業、畜牧（Landwirtschaft, Tierzucht） |
| `012x` | 馬術、動物護理（Pferdewirtschaft, Tierpflege） |
| `013x` | 狩獵（Jagd） |
| `014x` | 林業（Forstwirtschaft） |
| `111x` | 園藝綜合（Gartenbau allgemein） |
| `112x` | 庭園景觀（Garten-, Landschaftsbau） |
| `113x` | 花卉（Zierpflanzenbau） |
| `114x` | 蔬果（Gemüse-, Obstanbau） |
| `115x` | 葡萄酒（Weinbau） |
| `116x` | 啤酒花種植（Hopfenbau） |
| `121x` | 農業加工（Landw. Produkte be- und Verarbeitung） |
| `122x` | 漁業（Fischerei） |

### 大類 21–29：礦業、化學、金屬、機械、電子

| 代碼前綴 | 職業群組 |
| :-- | :-- |
| `211x` | 礦業採礦（Bergbau, Mineralgewinnung） |
| `212x` | 石油/天然氣（Erdöl-, Erdgasgewinnung） |
| `213x` | 鑽探技術（Bohr- und Gewinnungstechnik） |
| `221x` | 玻璃製造（Glaserzeugung） |
| `222x` | 陶瓷製造（Keramik） |
| `223x` | Steine und Erden |
| `231x` | 化學品生產（Chemie allgemein） |
| `232x` | 合成材料（Kunststoff） |
| `233x` | 橡膠（Kautschuk） |
| `234x` | 製藥（Pharmazie） |
| `241x` | 金屬冶煉（Metallerzeugung） |
| `242x` | 金屬加工（Metallbearbeitung） |
| `243x` | 鋼鐵（Stahl） |
| `244x` | 有色金屬（Nichteisenmetall） |
| `245x` | 鑄造（Gießerei） |
| `251x` | 機械元件加工（Maschinenbauteile） |
| `252x` | 工具製造（Werkzeugbau） |
| `261x` | 精密機械（Feinmechanik） |
| `262x` | 光學（Optik） |
| `263x` | 醫療設備（Medizintechnik） |
| `271x` | 電機設備（Elektrische Betriebstechnik） |
| `272x` | 電子元件（Elektronik） |
| `273x` | 機電整合（Mechatronik） |
| `281x` | 紡織（Textil） |
| `282x` | 皮革（Leder） |
| `283x` | 鞋業（Schuh） |
| `291x` | 食品加工（Lebensmittelherstellung） |
| `292x` | 飲料（Getränke） |
| `293x` | 菸草（Tabak） |

### 大類 31–34：建築與技術設施

| 代碼前綴 | 職業群組 |
| :-- | :-- |
| `311x` | 主體結構（Hochbau） |
| `312x` | 土木工程（Tiefbau） |
| `321x` | 木工/木結構（Zimmerei, Holzbau） |
| `322x` | 室內建築（Innenausbau） |
| `331x` | 建築機械（Baumaschinentechnik） |
| `332x` | 建材鋪設（Bodenverlegung） |
| `333x` | 建築測量（Bauplanung, Vermessung） |
| `341x` | 建物設施技術（Gebäudetechnik allgemein） |
| `342x` | 電氣設施（Elektrotechnik Gebäude） |
| `343x` | 水電暖氣（Sanitär-, Heizungs-, Klimatechnik） |

### 大類 41–43：資訊科技、自然科學（IT 工作者必看）

| 代碼前綴 | 職業群組 |
| :-- | :-- |
| `411x` | 數學、統計（Mathematik, Statistik） |
| `412x` | 生物科學（Biologie, Biochemie） |
| `413x` | 化學、製藥科學（Chemie, Pharmazie） |
| `414x` | 物理、材料科學（Physik, Werkstoff） |
| `421x` | 地球科學（Geowissenschaften） |
| `422x` | 環境保護（Umweltschutz） |
| `423x` | 氣象（Meteorologie） |
| `431x` | **IT 基礎（Informatik allgemein）** |
| `432x` | **IT 系統整合（Systemadministration）** |
| `433x` | **IT 協調、品保、測試（IT-Koordination, QS）** |
| `434x` | **軟體開發（Softwareentwicklung）** |

#### IT 職業代碼詳細對應（大類 43）

| 完整代碼 | 職稱範例 |
| :-- | :-- |
| `43102` | Fachinformatikerin - Systemintegration |
| `43103` | EDV-Technikerin, Informatiktechnikerin |
| `43104` | **Data Scientist**, Informatikingenieurin |
| `43112` | Informatikkaufmann-frau |
| `43113` | Wirtschaftsinformatikerin (Fachschule) |
| `43114` | **Wirtschaftsinformatikerin (Hochschule)** |
| `43122` | SPS-Fachkraft, Technischer Systeminformatikerin |
| `43123` | IT-Technikerin, Systemintegratorin |
| `43124` | Ingenieurinformatikerin |
| `43153` | **Web-Entwicklerin**, IT-Spezialistin digitale Wirtschaft |
| `43154` | Medieninformatikerin (Hochschule) |
| `43194` | Leiterin - Informatik, Informationsmanagerin |
| `43214` | **Systemarchitektin**, IT-Architektin |
| `43223` | Helpdesk-Administratorin, IT-Kundenbetreuerin |
| `43224` | **IT-Consultant**, ERP-Beraterin, Softwareberaterin |
| `43313` | Netzwerktechnikerin, PC- und Netzwerkfachkraft |
| `43314` | **Netzwerkplanerin**, Netzwerkkoordinatorin |
| `43323` | **IT-Projektkoordinatorin**, IT-Testerin, IT-Qualitätssicherungskoordinatorin |
| `43343` | **IT-Systemadministratorin**, Systemadministratorin |
| `43353` | **Datenbankadministratorin**, Datenbankentwicklerin |
| `43363` | Webadministratorin, Web-Masterin |
| `43383` | **IT-Sicherheitstechnikerin**, Security Technician |
| `43384` | IT-Sicherheitskoordinatorin |
| `43394` | **IT-Leiterin**, IT-Managerin, IT-Projektleiterin |
| `43412` | Fachinformatikerin - Anwendungsentwicklung |
| `43413` | **Softwaretechnikerin**, Anwendungsentwicklerin |
| `43414` | **Softwareentwicklerin**, Software-Ingenieurin |
| `43423` | **Programmiererin**, Anwendungsprogrammiererin |
| `43494` | **Leiterin - Softwareentwicklung**, Software-Projektleiterin |

> **快速選碼原則：** 前兩碼決定領域，末碼決定你的層級（2=有訓練, 3=有進階資格, 4=大學學歷）。例如後端工程師+學士 = `43414`；後端工程師+碩士 = `43414`（同碼，學歷透過 `ausbildungsjahre` 反映）。

### 大類 51–54：交通、物流

| 代碼前綴 | 職業群組 |
| :-- | :-- |
| `511x` | 交通基礎設施（Fahrzeug-, Luft-, Schiffsinspektion） |
| `512x` | 貨物裝卸（Güterabfertigung） |
| `513x` | 倉儲物流（Lagerwirtschaft） |
| `514x` | 交通服務（Fahrkartenservice） |
| `515x` | 交通管制（Verkehrsleitung） |
| `516x` | 航空、海運管理（Luftverkehr, Seeverkehr） |
| `521x` | 計程車/轎車駕駛（Pkw-Fahrer） |
| `522x` | 貨車駕駛（Lkw-Fahrer） |
| `523x` | 公車/電車駕駛（Bus-, Straßenbahnfahrer） |
| `524x` | 火車駕駛（Lokführer） |
| `531x` | 快遞物流（Kurier, Post） |
| `532x` | 海港物流（Hafenlogistik） |

### 大類 61–63：商業、零售、旅遊

| 代碼前綴 | 職業群組 |
| :-- | :-- |
| `611x` | 批發採購（Großhandel） |
| `612x` | 零售銷售（Einzelhandel） |
| `613x` | 業務開發（Technischer Verkauf） |
| `621x` | 食品零售（Lebensmittelverkauf） |
| `622x` | 藥妝/美容（Drogerie, Kosmetik） |
| `623x` | 服裝零售（Textil） |
| `624x` | 電器零售（Elektrofachhandel） |
| `625x` | 建材/家具（Bau-, Möbelhandel） |
| `631x` | 旅遊業（Tourismus） |
| `632x` | 餐飲旅宿（Gastronomie, Hotel） |
| `633x` | 活動管理（Veranstaltungsmanagement） |

### 大類 71–73：企業管理、行銷、媒體

| 代碼前綴 | 職業群組 |
| :-- | :-- |
| `711x` | 企業管理（Unternehmensführung, Geschäftsführung） |
| `712x` | 公共行政（Öffentliche Verwaltung） |
| `713x` | 組織管理（Organisation, Planung） |
| `714x` | 人事（Personalwesen） |
| `715x` | 財務控管（Rechnungswesen, Controlling） |
| `721x` | 行銷/公關（Marketing, PR） |
| `722x` | 廣告媒體購買（Werbung, Mediaplanung） |
| `723x` | 廣告設計（Werbegestaltung） |
| `731x` | 出版（Verlagswesen） |
| `732x` | 新聞記者（Journalismus） |
| `733x` | 攝影/影像（Fotografie, Film） |

### 大類 81–84：醫療、社工、教育

| 代碼前綴 | 職業群組 |
| :-- | :-- |
| `811x` | 醫師、醫學（Medizin allgemein） |
| `812x` | 藥師（Apotheke, Pharmazie） |
| `813x` | 護理（Krankenpflege, Altenpflege） |
| `814x` | **醫療/護理管理** (Gesundheitsmanagement) |
| `815x` | 物理治療（Physiotherapie） |
| `816x` | 牙科（Zahnmedizin） |
| `817x` | 獸醫（Veterinärwesen） |
| `818x` | 醫療技術（Medizintechnik） |
| `821x` | 兒童照護（Kindertagesbetreuung） |
| `822x` | 社會工作（Soziale Arbeit） |
| `823x` | 老人照護（Altenpflege） |
| `824x` | 身心障礙輔助（Heilerziehung） |
| `825x` | 心理輔導（Psychologischer Dienst） |
| `831x` | 幼稚園教師（Erzieher/in） |
| `832x` | 學校老師（Lehramt Berufsschule） |
| `833x` | 高等教育（Hochschullehre） |
| `841x` | 人文科學（Geisteswissenschaften） |
| `842x` | 社會科學（Sozialwissenschaften） |
| `843x` | 宗教/神學（Theologie） |
| `844x` | 歷史（Geschichte） |
| `845x` | 哲學（Philosophie） |

### 大類 91–94：法律、財務、文書、藝術

| 代碼前綴 | 職業群組 |
| :-- | :-- |
| `911x` | 法官（Richter） |
| `912x` | 律師（Rechtsanwalt） |
| `913x` | 公證/法律文書（Notar, Rechtssekretariat） |
| `914x` | 合規/法律顧問（Compliance, Jurist） |
| `921x` | 銀行（Banken, Kreditwesen） |
| `922x` | 保險（Versicherungswesen） |
| `923x` | 投資/股票（Geldanlagen, Börse） |
| `924x` | 會計（Buchhaltung, Steuerberatung） |
| `931x` | 土地/房地產（Immobilien） |
| `932x` | 文書/行政助理（Bürokraft） |
| `933x` | 翻譯（Übersetzung） |
| `934x` | 速記/文秘（Schreibkraft） |
| `941x` | 音樂（Musik） |
| `942x` | 表演藝術（Theater, Film） |
| `943x` | 設計（Design） |
| `944x` | 攝影/媒體製作（Medienproduktion） |
| `945x` | 舞台技術（Veranstaltungstechnik） |


***

### 3.7 `vollzeit` — 全職/兼職

**類型：** `bool`
**說明：** 雇用性質是否為全職。


| 值 | 說明 | 薪資影響 |
| :-- | :-- | :-- |
| `True` | 全職（Vollzeit）— 參照組 | ± 0% |
| `False` | 兼職（Teilzeit） | 約 −5.2% |

```python
vollzeit = True    # 全職工作
vollzeit = False   # 兼職工作（配合 EF59U3_11 或 EF59U3_12 使用）
```


***

### 3.8 `geschlecht` — 模型選擇

**類型：** `str`
**說明：** 選擇使用哪套迴歸模型，並非直接等於「填入性別」。三套模型的係數略有差異。


| 值 | 模型 | Intercept | 說明 |
| :-- | :-- | :-- | :-- |
| `"gesamt"` | 全體平均 | 7.7281 | 男女混合資料，含 GPG 修正欄位（但不主動套用） |
| `"maenner"` | 男性 | 7.8486 | 男性專屬迴歸結果，截距較高 |
| `"frauen"` | 女性 | 7.7281 | 與 gesamt 相同係數，但在計算時額外套用 GPG（−8%） |

```python
geschlecht = "maenner"   # 男性薪資估算
geschlecht = "frauen"    # 女性薪資估算（會套用 −8% GPG）
geschlecht = "gesamt"    # 全體平均（中性估算）
```

> **GPG（Gender Pay Gap）係數：** `gesamt` 模型中為 −0.0805，`maenner` 模型中為 −0.0848。女性模型在計算時將此係數加入線性預測值，反映德國男女薪資差距現實。

***

### 3.9 `befristet` — 合約類型

**類型：** `bool`
**說明：** 是否為**期限合約（Befristeter Arbeitsvertrag）**。


| 值 | 說明 | 薪資影響 |
| :-- | :-- | :-- |
| `False` | 無限期合約（Unbefristet）— 參照組 | ± 0% |
| `True` | 臨時/有期限合約（Befristet） | 約 −7.5% |

```python
befristet = False   # 正式無限期合約
befristet = True    # 試用期/臨時工/固定期限合約
```


***

## 5. 模型原理

本工具使用**對數線性迴歸（OLS log-linear regression）**：

$\ln(\text{月薪}) = \text{Intercept} + \beta_{\text{BE}} \cdot f(\text{年資}) + \beta_{\text{EF40}} \cdot g(\text{學歷}) + \sum_i \beta_i \cdot \mathbf{1}[\text{類別}_i]$

$\text{月薪（中位數）} = e^{\hat{y}}$

係數均來自 Destatis 官方 `app.js` 內的 OLS 估計結果，以德國薪資結構調查（Verdienststrukturerhebung）為資料基礎。輸出為**稅前月薪中位數（Bruttogehalt Median）**，非平均值。

***

## 6. 使用範例

```python
MODELS = load_models("coefficients.json")

# Backend 工程師，Hamburg，碩士，10年，大企業，全職，無限期
result = schaetze_monatsgehalt(
    berufsjahre=10,
    ausbildungsjahre=19,        # 碩士
    ef59u3_key="EF59U3_15",     # 40小時/週
    unternehmen_key="UNGr_UN6", # ≥1000人
    bundesland_key="EF13_102",  # Hamburg
    kldb_code="43414",          # Softwareentwicklerin
    vollzeit=True,
    geschlecht="maenner",
    befristet=False,
    models=MODELS,
)

# IT 管理主管，Bayern，碩士，15年，大企業（管理職用倒數第二碼9）
result2 = schaetze_monatsgehalt(
    berufsjahre=15,
    ausbildungsjahre=19,
    ef59u3_key="EF59U3_16",     # >40小時/週
    unternehmen_key="UNGr_UN6",
    bundesland_key="EF13_109",  # Bayern
    kldb_code="43394",          # IT-Leiterin（末碼=4, 倒數第二碼=9=管理職）
    vollzeit=True,
    geschlecht="maenner",
    befristet=False,
    models=MODELS,
)
```


***

## 7. 注意事項

- 輸出為**稅前（Brutto）** 月薪，實際稅後（Netto）需另依稅率、Steuerklasse、Sozialversicherung 試算
- 結果為**中位數估算**，非保證薪資
- 模型資料基準年為 Destatis 原始發布年份（約 2018–2020 年薪資結構調查），未含近年通膨調整
- 如職業代碼不確定，可至 [Klassifikationsserver](https://www.klassifikationsserver.de/klassService/thyme/variant/kldb2010) 搜尋職稱

