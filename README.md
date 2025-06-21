<p align="center">
  <picture>
    <img alt="blockkit-logo" src="https://github.com/imryche/blockkit/raw/master/docs/img/blockkit.svg">
  </picture>
</p>

![Build status](https://github.com/imryche/blockkit/actions/workflows/ci.yml/badge.svg)
[![PyPI version](https://badge.fury.io/py/blockkit.svg)](https://badge.fury.io/py/blockkit)
[![Downloads](https://static.pepy.tech/badge/blockkit)](https://pepy.tech/project/blockkit)

---

**Documentation**:
<a href="https://blockkit.botsignals.co" target="_blank">https://blockkit.botsignals.co</a>

**Source Code**:
<a href="https://github.com/imryche/blockkit" target="_blank">https://github.com/imryche/blockkit</a>

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
            "type": "mrkdwn",  # 🤔 or was it "markdown"?
            "text": "Please approve *Alice's* expense report for $42"
        },
        "accessory": {
            "type": "button",
            "text": {
                "type": "plain_text",  # 😕 wait, why can't buttons use mrkdwn?
                "text": "Approve"      # 🤞 hope this isn't too long
            },
            "action_id": "approve_button",
            "style": "green",  # ❌ is it "green"? "success"? "primary"?
            "confirm": {       # 🤔 what's the structure again?
                "title": {
                    "type": "plain_text",
                    "text": "Are you sure?"
                },
                "text": {
                    "type": "plain_text",
                    "text": "This action cannot be undone"
                },
                "confirm": {
                    "type": "plain_text",
                    "text": "Yes, approve"
                }
                # ❌ forgot the required "deny" field
            }
        }
    }],
    "thread_ts": 1234567890  # ❌ wait, should this be a string?
}

# Three bugs. Deeply nested JSON. Good luck debugging this.
```

Nest some JSON. Guess field names. Cross your fingers. Test it. Get an error.
Try again. Sound familiar?

### After

Here's the same thing:

```python
from blockkit import Message, Section, Button, Confirm

message = (
    Message()
    .add_block(
        Section("Please approve *Alice's* expense report for $42")  # ✅ Markdown detected automatically
        .accessory(
            Button("Approve")
            .action_id("approve_button")
            .style(Button.PRIMARY)  # ✅ Class constants prevent typos
            .confirm(
                Confirm()
                .title("Are you sure?")
                .text("This action cannot be undone")
                .confirm("Yes, approve")
                .deny("Cancel")  # ✅ Can't forget required fields
            )
        )
    )
    .thread_ts(1234567890)  # ✅ Converts types automatically
    .build()  # ✅ Validates everything: types, lengths, required fields
)

# Clean. Readable. BlockKit catches errors before you event send it to Slack.
```

Done. No guessing. No runtime surprises. Your editor helped you write it.

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
