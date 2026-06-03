from kaloricketabulky.sdk.models.tips import Tip


def test_tip_parses() -> None:
    tip = Tip.model_validate(
        {
            "key": "analysis.tip.112",
            "title": "Ubereme cukr.",
            "text": "Jednoduché sacharidy...",
            "advice": None,
            "icon": "cake_gray_250",
            "indicator": 0,
            "order": 2,
        }
    )
    assert tip.key == "analysis.tip.112"
    assert tip.title == "Ubereme cukr."
    assert tip.advice is None
    assert tip.indicator == 0
    assert tip.order == 2
