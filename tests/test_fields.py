import pytest

from blockkit import Confirm, Text
from blockkit.fields import (
    ArrayField,
    BooleanField,
    ConfirmField,
    StringField,
    TextField,
    UrlField,
    DateField,
)
from blockkit.validators import ValidationError


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


def test_boolean_field_validates_input():
    assert BooleanField().validate(True) is True


def test_boolean_field_with_incorrect_input_raises_exception():
    with pytest.raises(ValidationError):
        BooleanField().validate("true")


def test_text_field_validates_input(values):
    text = Text(values.text)
    assert TextField().validate(text) == text


def test_text_field_with_incorrect_input_raises_exception():
    with pytest.raises(ValidationError):
        TextField().validate("text")


def test_text_field_with_exeeding_length_raises_exception():
    with pytest.raises(ValidationError):
        TextField(max_length=5).validate(Text("foobar"))


def test_plain_text_field_with_incorrect_type_raises_exception(values):
    with pytest.raises(ValidationError):
        TextField(plain=True).validate(Text(values.text, type=Text.markdown))


def test_array_field_validates_input(values):
    texts = [Text(values.text) for _ in range(3)]
    assert ArrayField().validate(texts)


def test_array_field_with_incorrect_input_raises_exception():
    class FakeImage:
        pass

    images = [FakeImage() for _ in range(3)]

    with pytest.raises(ValidationError):
        ArrayField([Text]).validate(images)


def test_array_field_with_exeeding_items_raises_exception(plain_text):
    with pytest.raises(ValidationError):
        ArrayField([Text], max_items=5).validate([plain_text for _ in range(10)])


def test_url_field_validates_input(values):
    assert UrlField().validate(values.url)


def test_url_field_with_exeeding_length_raises_exception():
    with pytest.raises(ValidationError):
        UrlField(max_length=5).validate("http://example.com")


def test_url_field_with_incorrect_input_raises_exception():
    with pytest.raises(ValidationError):
        UrlField().validate("thisisnoturl")


def test_confirm_field_validates_input(short_text):
    assert ConfirmField().validate(
        Confirm(short_text, short_text, short_text, short_text)
    )


def test_confirm_field_with_incorrect_input_raises_exception(basic_text):
    with pytest.raises(ValidationError):
        ConfirmField().validate(basic_text)


def test_date_field_validates_input(values):
    assert DateField().validate(values.date)


def test_date_field_with_incorrect_input_raises_exception():
    with pytest.raises(ValidationError):
        DateField().validate('2019-12-43')
