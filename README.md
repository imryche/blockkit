![Screenshot](https://github.com/imryche/blockkit/raw/master/images/logo.png)

![Build status](https://github.com/imryche/blockkit/actions/workflows/python-app.yml/badge.svg)
[![PyPI version](https://badge.fury.io/py/blockkit.svg)](https://badge.fury.io/py/blockkit)
[![Downloads](https://static.pepy.tech/badge/blockkit)](https://pepy.tech/project/blockkit)

---

# BlockKit for Python

Build beautiful Slack UIs fast. Fluent API with type hints, validation, and zero
dependencies.

```shell
pip install blockkit
```

## Here's the thing

Building Slack apps shouldn't feel like writing JSON by hand. It's tedious. It's
error prone. And honestly? It's a waste of your time.

You know what you want to build. Your editor should help you build it. That's
what BlockKit for Python does.

### Before

This is what you're probably doing now:

```python
# Building a simple approval message. What could go wrong?
message = {
    "blocks": [{
        "type": "section",
        "text": {
            "type": "mrkdwn",  # or was it "markdown"?
            "text": "Please approve Alice's expense report"
        },
        "accessory": {
            "type": "button",
            "text": {
                "type": "plain_text",  # wait, why can't buttons use mrkdwn?
                "text": "Approve"      # hope this is under 75 chars
            },
            "action_id": "approve_button",  # better hope this is unique
            "style": "green"  # WRONG: it's "primary", not "green" 🤦
        }
    }],
    "thread_ts": 1234567890  # WRONG: should be a string, not a number
}

# Looks right? Nope. Two bugs Slack will reject at runtime.
# Good luck finding them in a large app.
```

Nest some JSON. Guess field names. Cross your fingers. Test it. Get and error.
Try again. Sound familiar?

### After

Here's the same thing:

```python
from blockkit import Message, Section, Button

message = (
    Message()
    .add_block(
        Section("Please approve Alice's expense report")
        .accessory(
            Button("Approve")
            .action_id("approve_button")
            .style("primary")  # ✅ IDE autocomplete shows valid options
        )
    )
    .thread_ts("1234567890")  # ✅ Type hints ensure it's a string
    .build()
)

# BlockKit caught those bugs before you even saved the file.
```

Done. No guessing. No runtime surprises. Your IDE helped you write it.

### The difference

The library knows Slack's rules, so you don't have to memorize them. Your editor
autocompletes everything. Validation happens immediately.

When something's wrong, you'll know right away - not after deploying.

## Real example

Let's build something real. An approval flow:

```python
from blockkit import Modal, Section, Input, PlainTextInput, RadioButtons, Option

modal = (
    Modal()
    .title("Expense Approval")
    .add_block(Section("*New expense request from Alice*"))
    .add_block(
        Input("Amount").element(
            PlainTextInput().initial_value("$42.00").action_id("amount")
        )
    )
    .add_block(
        Input("Decision").element(
            RadioButtons()
            .add_option(Option("Approve ✅", "approve"))
            .add_option(Option("Reject ❌", "reject"))
            .action_id("decision")
        )
    )
    .submit("Submit")
    .build()
)
```

That's it. Clear, readable, and it works the first time.

## Why we built this

We got tired of:

- Reading Slack's docs for the 100th time
- Building UIs that are impossible to refactor
- Shipping "perfect" JSON that Slack rejects for mysterious reasons

So we fixed it. One library. No dependencies. Just better.

## Want more?

Check out [blockkit.botsignals.co](https://blockkit.botsignals.co) for the full
docs. Or don't. The code is pretty self-explanatory.

---

Made by Botsignals
