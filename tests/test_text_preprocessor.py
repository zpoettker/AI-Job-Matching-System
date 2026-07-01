from text_preprocessor import TextPreprocessor

preprocessor = TextPreprocessor()


def test_clean_strips_html():
    # HTML tags should be removed from the text
    result = preprocessor.clean("<b>Testing</b> <p>Processing</p>")
    assert "<b>" not in result # Assert stops test if false
    assert "testing" in result
    assert "<p>" not in result
    assert "processing" in result
