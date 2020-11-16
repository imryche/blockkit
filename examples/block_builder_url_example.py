from blockkit import Section, Message
from blockkit.display import create_block_kit_builder_url

message = Message(
    blocks=[
        Section(text="HELLLOOOO WORLD!")
        ]
)

"""
outputs:
Block kit builder example/validation:  
	https://app.slack.com/block-kit-builder/#%7B%22blocks%22:%20%5B%7B%22type%22:%20%22section%22%2C%20%22text%22:%20%7B%22text%22:%20%22HELLLOOOO%20WORLD%21%22%2C%20%22type%22:%20%22plain_text%22%2C%20%22emoji%22:%20true%7D%7D%5D%7D
"""
create_block_kit_builder_url(message)
