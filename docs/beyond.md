# Beyond basics

You've built your first message. Now what?

Let's build bigger. Start simple. Add complexity only when you need it. The
library grows with your needs.

## Start with messages

Every Slack UI starts here. A message in a channel. Nothing fancy.

```python
from blockkit import Message, Section

message = Message().add_block(Section("New support ticket #1247")).build()
```

One line of information. That's often enough.

## Add some context

Users need details. Who reported this? When? How urgent?

```python
from blockkit import Context, Message, Section, Text

message = (
    Message()
    .add_block(Section("New support ticket #1247"))
    .add_block(
        Context().add_element(
            Text("Reported by Alice • High priority • 2 minutes ago")
        )
    )
    .build()
)
```

Now they know what, who, and when.

## Make it actionable

Information is good. But let's add actions to it.

```python
from blockkit import Actions, Button, Context, Message, Section, Text

message = (
    Message()
    .add_block(Section("New support ticket #1247"))
    .add_block(
        Context().add_element(
            Text("Reported by Alice • High priority • 2 minutes ago")
        )
    )
    .add_block(
        Actions()
        .add_element(Button("Assign to me").action_id("assign"))
        .add_element(Button("View Details").action_id("details"))
    )
    .build()
)
```

Now they can do something about it.

## When things can go wrong

Some actions are final. Help them think twice.

```python
from blockkit import Actions, Button, Confirm, Context, Message, Section, Text

message = (
    Message()
    .add_block(Section("New support ticket #1247"))
    .add_block(
        Context().add_element(
            Text("Reported by Alice • High priority • 2 minutes ago")
        )
    )
    .add_block(
        Actions()
        .add_element(Button("Assign to me").action_id("assign"))
        .add_element(Button("View Details").action_id("details"))
        .add_element(
            Button("Close Ticket")
            .action_id("close")
            .style(Button.DANGER)
            .confirm(
                Confirm()
                .title("Close this ticket?")
                .text(
                    "The customer will be notified that their issue is resolved"
                )
                .confirm("Yes, close it")
                .deny("Keep it open")
            )
        )
    )
    .build()
)
```

The library makes confirmations simple.

## Collect information with modals

Messages are great for showing information. Modals are better for collecting it.

Start simple:

```python
from blockkit import Input, Modal, PlainTextInput

modal = (
    Modal()
    .title("Create Support Ticket")
    .add_block(
        Input("Describe the issue").element(
            PlainTextInput().action_id("description")
        )
    )
    .submit("Create Ticket")
    .build()
)
```

One question. One input. One submit button.

## Add structure to your forms

Real forms need multiple fields. Different types of input.

```python
from blockkit import Checkboxes, Input, Modal, Option, PlainTextInput, StaticSelect

modal = (
    Modal()
    .title("Create Support Ticket")
    .add_block(
        Input("Describe the issue").element(
            PlainTextInput().multiline().action_id("description")
        )
    )
    .add_block(
        Input("Priority").element(
            StaticSelect()
            .add_option(Option("Low", "low"))
            .add_option(Option("Medium", "medium"))
            .add_option(Option("High", "high"))
            .action_id("priority")
        )
    )
    .add_block(
        Input("Category").element(
            Checkboxes()
            .add_option(Option("Bug Report", "bug"))
            .add_option(Option("Feature Request", "feature"))
            .add_option(Option("Account Issue", "account"))
            .action_id("category")
        )
    )
    .submit("Create Ticket")
    .build()
)
```

Now you have a proper form with multiple input types working together.

## Build rich app homes

App homes are different from messages and modals. They're persistent spaces that
people can always always return to.

Start with the essentials:

```python
from blockkit import Divider, Header, Home

home = (
    Home()
    .add_block(Header("Support Dashboard"))
    .add_block(Section("Your team's tickets:"))
    .add_block(Divider())
    .build()
)
```

Header. Introduction. Visual separation.

## Add dynamic content

App homes should feel alive. Show current information.

```python
from blockkit import Button, Context, Divider, Header, Home, Section, Text

home = (
    Home()
    .add_block(Header("Support Dashboard"))
    .add_block(Section("Your team's tickets:"))
    .add_block(Divider())
    .add_block(
        Section("*12 open tickets*").accessory(
            Button("View All").action_id("view_all")
        )
    )
    .add_block(
        Section("*3 high priority*").accessory(
            Button("Review Now").action_id("high_priority")
        )
    )
    .add_block(Section("*Average response time: 2.4 hours*"))
    .add_block(Divider())
    .add_block(Context().add_element(Text("Last updated 5 minutes ago")))
    .build()
)
```

Now people can see what's happening, take action on what matters, and know when
the information was last updated.

## The pattern

Notice what happened? We started simple and added complexity:

1. **Ticket notification → Notification with context → Notification with
   actions**
2. **Simple ticket form → Complex form with multiple inputs**
3. **Basic dashboard → Live support metrics**

Each step added more complexity, but the library guided you through it with the
same consistent patterns.

## Why this works

The library doesn't fight you. It helps you:

- **Start small** - One section, one button, one field
- **Add incrementally** - New blocks, more elements, richer interations
- **Stay consistent** - Same patterns, same methods, same validation

You write Python. We handle JSON. Slack handles the rest.

## What's next

You know how to build. Now go build your own Slack UIs. The library will guide
you through the complexity. Good luck!
