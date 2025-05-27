# BlockKit for Python

You know what you want to build. A simple approval button. A form that collects
feedback. A nice home tab.

But then you open docs and see this:

```json
{
  "type": "section",
  "text": {
    "type": "mrkdwn",
    "text": "..."
  }
}
```

Three levels deep just to show text. And that's the easy part.

BlockKit fixes this. Write Python. Get perfect JSON. Ship faster.

## What is this?

BlockKit is a Python library that makes building Slack UIs actually enjoyable.
Type hints tell you what's possible. Method chaining lets you build naturally.
Validation catches mistakes before Slack does. Zero dependencies means it won't
break your project.

## Install it

```bash
pip install blockkit
```

## See the difference

Here's how most people build Slack messages:

```json
{
  "blocks": [
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "Hello from BlockKit!"
      },
      "accessory": {
        "type": "button",
        "text": {
          "type": "plain_text",
          "text": "Click me"
        },
        "action_id": "button_1"
      }
    }
  ]
}
```

Here's how you do it with BlockKit:

```python
from blockkit import Message, Section, Button

message = (
    Message()
    .add_block(
        Section("Hello from BlockKit!")
        .accessory(Button("Click me").action_id("button_1"))
    )
    .build()
)
```

Same result. Half the code. No guessing.

## The basics

### Everything chains

Start with what you want. Add what you need. Build when you're done.

```python
button = (
    Button("Save")
    .action_id("save_button")
    .style(Button.PRIMARY)
    .build()
)
```

### It knows what you mean

Write text. We'll figure out if it needs markdown.

```python
# Just text? We use plain_text
Section("Hello world")

# See markdown? We switch to mrkdwn
Section("Hello *world*")
```

You focus on the content. We handle the details.

### Mistakes get caught early

Forget a required field? We'll tell you before Slack does.

```python
# This fails immediately - confirms need a deny button

Button("Delete").confirm(
    Confirm()
    .title("Are you sure?")
    .text("This cannot be undone")
    .confirm("Yes, delete it")
    # Missing: .deny("Cancel")
).build()
```

Better to know now than later.

### Rules are built in

Slack has rules. Lots of them. Button text can't be too long. Sections can't
have too many fields. We enforce all of them.

```python
# This raises an error - button text has a 75 character limit
Button("This is way too long " * 10)
```

The library helps you follow the rules. You ship working code.
