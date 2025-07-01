---
toc_depth: 2
---

## v2.0.4 (Jul 1, 2025)

#### Fixed

- Fix the validation logic of the `Section` component's fields
  [#119](https://github.com/imryche/blockkit/pull/119).

## v2.0.3 (June 21, 2025)

#### Fixed

- Improve markdown detection in `is_md`.

## v2.0.2 (June 13, 2025)

#### Fixed

- Now `DatetimePicker.initial_date_time` accepts integers or datetime objects.

## v2.0.1 (June 10, 2025)

#### Fixed

- Added `py.typed` for the type checking support.

## v2.0.0 (June 4, 2025)

We're excited to announce BlockKit v2.0.0 - a complete ground-up rewrite that
makes building Slack UIs faster, more intuitive, and more enjoyable than ever
before.

### What's new

#### Zero dependencies

BlockKit v2.0.0 has **zero runtime dependencies**. We've removed the Pydantic
and built a custom validation system that's more focused on Block Kit's specific
needs.

#### Method chaining

Every component now supports full method chaining for a more natural building
experience:

```python
# v1.9.2
button = Button(
    text=PlainText(text="Click me"),
    action_id="button_action",
    style="primary"
)

# v2.0.0 - Much cleaner!
button = (
    Button()
    .text("Click me")
    .action_id("button_action")
    .style(Button.PRIMARY)
)
```

#### Automatic text type detection

No more guessing whether to use `plain_text` or `mrkdwn`. BlockKit now
automatically detects markdown formatting:

```python
# Automatically uses plain_text
Section("Hello world")

# Automatically detects markdown and uses mrkdwn
Section("Hello *world*")
```

#### Intelligent string conversion

Pass strings anywhere - BlockKit automatically converts them to the appropriate
Text objects:

```python
# All of these work seamlessly
Modal().title("My Modal")
Button().text("Click me")
Section("*Bold text*")
```

#### Complete coverage

The library now supports all blocks, elements and composition objects that are
currently available in Block Kit.

#### Better error messages

```python
# Clear, actionable validation errors
FieldValidationError: Field 'text': Length must be between 1 and 75 (got 82)
ComponentValidationError: Component 'Button': Only plain_text is allowed
```

#### Type safety and editor autocompletion

Full type hints throughout the codebase for better IDE support and fewer runtime
errors.

#### Consistent patterns

Every component follows the same patterns - if you know how to use one, you know
how to use them all.
