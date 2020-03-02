import pytest

from blockkit import Confirm, PlainText, MarkdownText, Text
from blockkit.fields import (
    ArrayField,
    BooleanField,
    ObjectField,
    StringField,
    TextField,
    UrlField,
    DateField,
    IntegerField,
    ValidationError,
)


def test_string_field_validates_input():
    assert StringField().validate("input") == "input"


def test_string_field_with_incorrect_type_raises_exception():
    with pytest.raises(ValidationError):
        StringField().validate(5)


def test_string_field_with_exeeding_length_raises_exception():
    with pytest.raises(ValidationError):
        StringField(max_length=5).validate("foobar")


def test_string_field_with_incorrect_option_raises_exception():
    with pytest.raises(ValidationError):
        StringField(options=["foo", "bar"]).validate("bad_option")


def test_integer_field_validates_input():
    assert IntegerField().validate(1)


def test_integer_field_with_incorrect_input_raises_exception():
    with pytest.raises(ValidationError):
        IntegerField().validate("one")


def test_integer_field_with_exceeding_value_raises_exception():
    with pytest.raises(ValidationError):
        IntegerField(max_value=10).validate(11)


def test_boolean_field_validates_input():
    assert BooleanField().validate(True) is True


def test_boolean_field_with_incorrect_input_raises_exception():
    with pytest.raises(ValidationError):
        BooleanField().validate("true")


def test_text_field_validates_input(values):
    text = PlainText(values.text)
    assert TextField().validate(text) == text


@pytest.mark.parametrize("plain", (True, False))
def test_text_field_validates_str_input(plain, values):
    text = "Hey there!"
    assert TextField(plain=plain).validate(text) == PlainText(text, emoji=True)


def test_text_field_with_exeeding_length_raises_exception():
    with pytest.raises(ValidationError):
        TextField(max_length=5).validate(PlainText("foobar"))


def test_plain_text_field_with_incorrect_type_raises_exception(values):
    with pytest.raises(ValidationError):
        TextField(plain=True).validate(MarkdownText(values.text))


def test_array_field_validates_input(values):
    texts = [PlainText(values.text) for _ in range(3)]
    assert ArrayField(PlainText).validate(texts)


def test_array_field_validatates_strings(values):
    texts = [values.text]
    assert ArrayField(Text).validate(texts) == [PlainText(values.text, emoji=True)]


def test_array_field_with_incorrect_input_raises_exception():
    class FakeImage:
        pass

    images = [FakeImage() for _ in range(3)]

    with pytest.raises(ValidationError):
        ArrayField(PlainText).validate(images)


def test_array_field_with_exeeding_items_raises_exception(plain_text):
    with pytest.raises(ValidationError):
        ArrayField(PlainText, max_items=5).validate([plain_text for _ in range(10)])


def test_array_field_with_lacking_items_raises_exception(plain_text):
    with pytest.raises(ValidationError):
        ArrayField(PlainText, min_items=2).validate([plain_text])


def test_url_field_validates_input(values):
    assert UrlField().validate(values.url)


def test_url_field_with_exeeding_length_raises_exception():
    with pytest.raises(ValidationError):
        UrlField(max_length=5).validate("http://example.com")


def test_url_field_with_incorrect_input_raises_exception():
    with pytest.raises(ValidationError):
        UrlField().validate("thisisnoturl")


def test_object_field_validates_input(short_text):
    assert ObjectField(Confirm, PlainText).validate(
        Confirm(short_text, short_text, short_text, short_text)
    )


def test_object_field_with_incorrect_input_raises_exception(markdown_text):
    with pytest.raises(ValidationError):
        ObjectField(Confirm).validate(markdown_text)


def test_date_field_validates_input(values):
    assert DateField().validate(values.date)


def test_date_field_with_incorrect_input_raises_exception():
    with pytest.raises(ValidationError):
        DateField().validate("2019-12-43")
