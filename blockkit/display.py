from json import dumps
from urllib.parse import quote


def create_block_kit_builder_url(block_kit_like_object):
    """
    Takes block_kit_like_object like element, component, surfaces, and objects
    block_kit_like_object can be built (build()) or unbuilt, see example
    """
    block_kit_builder_url = "https://app.slack.com/block-kit-builder/#"
    try:
        block_dump = dumps(block_kit_like_object.build())
    except AttributeError as attribute_error:
        if str(attribute_error) == "'dict' object has no attribute 'build'":
            block_dump = dumps(block_kit_like_object)
        else:
            raise AttributeError
    except Exception as e:
        raise e from None
    final_url = block_kit_builder_url + block_dump
    final_url_safe = quote(final_url, safe="/:?=&#")
    msg = "Block kit builder example/validation:  \n\t" + final_url_safe
    print(msg)
