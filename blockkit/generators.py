from black import FileMode, format_str

from blockkit.blocks import (
    Actions,
    Context,
    Divider,
    Header,
    ImageBlock,
    Input,
    Section,
)
from blockkit.elements import (
    Button,
    ChannelsSelect,
    Checkboxes,
    ConversationsSelect,
    DatePicker,
    ExternalSelect,
    Image,
    MultiChannelsSelect,
    MultiConversationsSelect,
    MultiExternalSelect,
    MultiStaticSelect,
    MultiUsersSelect,
    Overflow,
    PlainTextInput,
    RadioButtons,
    StaticSelect,
    UsersSelect,
)
from blockkit.objects import (
    Confirm,
    DispatchActionConfig,
    Filter,
    MarkdownText,
    Option,
    OptionGroup,
    PlainText,
)
from blockkit.surfaces import Home, Message, Modal


class CodeGenerationError(Exception):
    pass


components = {
    "section": Section,
    "plain_text": PlainText,
    "mrkdwn": MarkdownText,
    "button": Button,
    "static_select": StaticSelect,
    "users_select": UsersSelect,
    "channels_select": ChannelsSelect,
    "conversations_select": ConversationsSelect,
    "external_select": ExternalSelect,
    "multi_static_select": MultiStaticSelect,
    "multi_users_select": MultiUsersSelect,
    "multi_channels_select": MultiChannelsSelect,
    "multi_conversations_select": MultiConversationsSelect,
    "multi_external_select": MultiExternalSelect,
    "image": ImageBlock,
    "overflow": Overflow,
    "datepicker": DatePicker,
    "checkboxes": Checkboxes,
    "radio_buttons": RadioButtons,
    "actions": Actions,
    "divider": Divider,
    "context": Context,
    "input": Input,
    "plain_text_input": PlainTextInput,
    "header": Header,
    "modal": Modal,
    "home": Home,
}


def generate(payload, component=None):
    kwargs = []
    for name, value in payload.items():
        if name == "type":
            continue

        if type(value) == str:
            if name == "text":
                value = (
                    value.replace("\n", "\\n").replace("\t", "\\t").replace('"', '\\"')
                )
            kwarg = f'{name}="{value}"'
        elif type(value) == dict:
            subcomponent = None
            if name == "filter":
                subcomponent = Filter
            elif name == "dispatch_action_config":
                subcomponent = DispatchActionConfig
            elif name == "confirm" and "confirm" in value:
                subcomponent = Confirm
            elif name == "accessory" and value.get("type") == "image":
                subcomponent = Image
            kwarg = f"{name}=" + generate(value, subcomponent)
        elif type(value) == list:
            if name == "options":
                items = [generate(v, Option) for v in value]
            elif name == "option_groups":
                items = [generate(v, OptionGroup) for v in value]
            elif name in ("include", "trigger_actions_on"):
                items = [f'"{v}"' for v in value]
            elif name == "elements":
                items = [
                    generate(v, Image) if v.get("type") == "image" else generate(v)
                    for v in value
                ]
            else:
                items = [generate(v) for v in value]

            items = ", ".join(items)
            kwarg = f"{name}=[{items}]"
        else:
            kwarg = f"{name}={value}"

        kwargs.append(kwarg)

    if not component:
        if "type" not in payload:
            component = Message
        else:
            try:
                component = components[payload["type"]]
            except KeyError:
                raise CodeGenerationError(
                    f"Can't generate component of type {payload['type']}."
                )

    class_name = component.__name__
    kwargs = ", ".join(kwargs)

    return f"{class_name}({kwargs})"


def generate_pretty(payload):
    return format_str(generate(payload), mode=FileMode())
