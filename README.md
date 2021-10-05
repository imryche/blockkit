![Screenshot](https://github.com/imryche/blockkit/raw/master/images/logo.png)

![Build status](https://github.com/imryche/blockkit/actions/workflows/python-app.yml/badge.svg)
[![PyPI version](https://badge.fury.io/py/blockkit.svg)](https://badge.fury.io/py/blockkit)
[![Downloads](https://pepy.tech/badge/blockkit)](https://pepy.tech/project/blockkit)

---

Blockkit is a Python library for building UI interfaces for Slack apps. It allows you to compose the interface from Python classes, so you type less, and your code becomes more maintainable.

Blockkit performs validation at runtime and provides user-friendly errors when data is invalid.

## Generate

You don't even need to write code yourself. Go to [blockkit-generator.com](https://blockkit-generator.com) paste your JSON payload from [Block Kit Builder](https://api.slack.com/tools/block-kit-builder) and get corresponding Python code!

![Screenshot](https://github.com/imryche/blockkit/raw/master/images/generator.png)

## Installation

```bash
pip install blockkit
```

## Usage

Start with one of the `Home`, `Modal`, or `Message` surface classes and follow the structure as you would follow it in JSON.

The library supports all types of [surfaces](https://api.slack.com/surfaces), [blocks](https://api.slack.com/block-kit), [block elements](https://api.slack.com/block-kit), and [composition objects](https://api.slack.com/block-kit) Slack provides.

Once UI is ready, call the `build()` method to render components to dictionary:

```python
from blockkit import Section, MarkdownText

Section(text=MarkdownText(text="hello world")).build()

{"type": "section", "text": {"text": "hello world", "type": "mrkdwn"}}
```

Here's the list of types of components and corresponding classes:

### Surfaces

| Type  | Class   |
| ----- | ------- |
| home  | Home    |
| modal | Modal   |
|       | Message |

### Blocks

| Type    | Class      |
| ------- | ---------- |
| actions | Actions    |
| context | Context    |
| divider | Divider    |
| header  | Header     |
| image   | ImageBlock |
| input   | Input      |
| section | Section    |

### Block elements

| Type                       | Class                    |
| -------------------------- | ------------------------ |
| button                     | Button                   |
| checkboxes                 | Checkboxes               |
| datepicker                 | DatePicker               |
| type                       | Image                    |
| multi_static_select        | MultiStaticSelect        |
| multi_users_select         | MultiUsersSelect         |
| multi_channels_select      | MultiChannelsSelect      |
| multi_conversations_select | MultiConversationsSelect |
| multi_external_select      | MultiExternalSelect      |
| overflow                   | Overflow                 |
| plain_text_input           | PlainTextInput           |
| radio_buttons              | RadioButtons             |
| static_select              | StaticSelect             |
| users_select               | UsersSelect              |
| channels_select            | ChannelsSelect           |
| conversations_select       | ConversationsSelect      |
| external_select            | ExternalSelect           |
| timepicker                 | Timepicker               |

### Composition objects

| Type       | Class                |
| ---------- | -------------------- |
| plain_text | PlainText            |
| mrkdwn     | MarkdownText         |
|            | Confirm              |
|            | Option               |
|            | OptionGroup          |
|            | Filter               |
|            | DispatchActionConfig |

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)
