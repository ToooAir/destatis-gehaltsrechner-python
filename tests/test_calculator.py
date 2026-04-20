import pytest
from salary_calculator import load_models, schaetze_monatsgehalt

@pytest.fixture(scope="module")
def models():
    return load_models()

def test_schaetze_monatsgehalt_basic(models):
    result = schaetze_monatsgehalt(
        berufsjahre=10,
        ausbildungsjahre=19,
        ef59u3_key="EF59U3_15",
        unternehmen_key="UNGr_UN6",
        bundesland_key="EF13_102",
        kldb_code="434",
        vollzeit=True,
        geschlecht="maenner",
        befristet=False,
        models=models,
    )
    assert result["modell"] == "maenner"
    assert "median_monatsgehalt_brutto" in result
    assert result["median_monatsgehalt_brutto"] > 0
    assert result["beitrage"]["Berufsgruppe (KldB)"] != 0

def test_gender_pay_gap(models):
    res_maenner = schaetze_monatsgehalt(
        berufsjahre=5, ausbildungsjahre=16, ef59u3_key="EF59U3_15",
        unternehmen_key="UNGr_UN3", bundesland_key="EF13_111", kldb_code="43414",
        geschlecht="maenner", models=models
    )
    res_frauen = schaetze_monatsgehalt(
        berufsjahre=5, ausbildungsjahre=16, ef59u3_key="EF59U3_15",
        unternehmen_key="UNGr_UN3", bundesland_key="EF13_111", kldb_code="43414",
        geschlecht="frauen", models=models
    )
    assert res_maenner["median_monatsgehalt_brutto"] != res_frauen["median_monatsgehalt_brutto"]
    assert "GPG" in res_frauen["beitrage"]
