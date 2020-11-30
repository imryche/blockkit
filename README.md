# blockkit-slack

[![Build Status](https://travis-ci.com/oneor0/blockkit-slack.svg?branch=master)](https://travis-ci.com/oneor0/blockkit-slack)

A fast way to build Block Kit interfaces in Python 

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install blockkit.

```bash
pip install blockkit
```

## Usage

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
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
