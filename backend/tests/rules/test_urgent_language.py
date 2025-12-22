from analyzer.rules.urgent_language import urgent_language_rule


def test_detects_urgent_language():
    text = "Urgent hiring! Join immediately for this role."
    result = urgent_language_rule(text)

    assert result["score"] > 0
    assert "Urgent" in result["reason"]


def test_no_urgent_language():
    text = "We are hiring a software engineer with 3 years experience."
    result = urgent_language_rule(text)

    assert result["score"] == 0.0
    assert result["reason"] is None