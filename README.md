# blockkit

[![Build Status](https://travis-ci.com/imryche/blockkit.svg?branch=master)](https://travis-ci.com/imryche/blockkit)
[![PyPI version](https://badge.fury.io/py/blockkit.svg)](https://badge.fury.io/py/blockkit)
[![Downloads](https://pepy.tech/badge/blockkit)](https://pepy.tech/project/blockkit)

Blockkit is a Python library for building UI interfaces for Slack apps. It allows you to compose the interface from Python classes, so you type less, and your code becomes more maintainable.

Blockkit performs validation at runtime and provides user-friendly errors when data is invalid.

## Installation

```bash
pip install blockkit
```

## Usage

Start with one of the `Home`, `Modal`, or `Message` surface classes and follow the structure as you would follow it in JSON.

The library supports all types of [surfaces](https://api.slack.com/surfaces), [blocks](https://api.slack.com/block-kit), [block elements](https://api.slack.com/block-kit), and [composition objects](https://api.slack.com/block-kit) Slack provides.

Once UI is ready, call the `build()` method to render components to dictionary:

```python
from blockkit import Message, Section, Actions, MarkdownText, Button


message = Message(
    blocks=[
        Section(MarkdownText("You have a new request")),
        Section(
            fields=[
                MarkdownText("*Type:*\nComputer (laptop)"),
                MarkdownText("*When:*\nSubmitted Aut 10"),
                MarkdownText("*Last Update:*\nMar 10, 2015 (3 years, 5 months)"),
                MarkdownText("*Reason:*\nAll vowel keys aren't working."),
                MarkdownText("*Specs:*\nCheetah Pro 15 - Fast, really fast"),
            ],
        ),
        Actions(
            [
                Button("Approve", style=Button.primary, action_id="approve"),
                Button("Decline", style=Button.danger, action_id="decline"),
                Button("Discuss", action_id="discuss"),
            ]
        ),
    ]
)

message = message.build()
```

## Viewing Blocks in Block UI Builder
Visualize in the [Slack's Block Kit Builder](https://app.slack.com/block-kit-builder/#):
```python
message = Message(
    blocks=[Section(text="Hello, world!")]
)

create_block_kit_builder_url(message)
"""
outputs:
Block kit builder example/validation:  
	https://app.slack.com/block-kit-builder/#%7B%22blocks%22:%20%5B%7B%22type%22:%20%22section%22%2C%20%22text%22:%20%7B%22text%22:%20%22HELLLOOOO%20WORLD%21%22%2C%20%22type%22:%20%22plain_text%22%2C%20%22emoji%22:%20true%7D%7D%5D%7D
"""
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
