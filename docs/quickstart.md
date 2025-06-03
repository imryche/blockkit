# Quickstart

Skip the theory. Let's build something real and see it work in Slack.

Here's a complete Slack message. Built in BlockKit. Sent to a channel. Done in 5
minutes.

## Install it

```bash
pip install blockkit
```

## Build a message

```python
from blockkit import Message, Section, Actions, Button

message = (
    Message()
    .add_block(Section("Your deployment to production is complete."))
    .add_block(
        Actions().add_element(Button("View Logs").action_id("view_logs"))
    )
    .build()
)
```

That's it. Real Slack BlockKit JSON. Ready to send.

## Send it

```python
from slack_sdk.web import WebClient

client = WebClient("your-token")

client.chat_postMessage(channel="#deployments", **message)
```

## It works

Your message appears in Slack. The buttons work. No JSON debugging. No "invalid
block" errors. No wondering if you got the structure right.

## Make it yours

Change the message:

```python
Section("🚀 Version 2.1.4 deployed successfully to production.")
```

Add more actions:

```python
Actions()
.add_element(Button("View Logs").action_id("view_logs"))
.add_element(Button("Monitor").action_id("monitor"))
.add_element(Button("Rollback").action_id("rollback").style(Button.DANGER))
```

Add a confirmation to that rollback button:

```python
Button("Rollback").action_id("rollback").style(Button.DANGER).confirm(
    Confirm()
    .title("Rollback to previous version?")
    .text("This will revert all changes from the current deployment")
    .confirm("Yes, rollback")
    .deny("Cancel")
)
```

## What just happened

You built a Slack message without touching JSON. The library:

- Figured out text formatting automatically
- Guided you with autocompletion in your editor
- Validated everything against Slack's rules before you sent it
- Made sure required fields weren't missing

## What's next

That's a real Slack message. Built in Python. Sent to your channel. Working
buttons included.

Ready to build something bigger? Explore all the building blocks you can use.
