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


def generate(payload):
    code = _generate(payload)
    eval_components(code)
    return code


def generate_pretty(payload):
    return format_str(generate(payload), mode=FileMode())


def _generate(payload, component=None):
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
            kwarg = f"{name}=" + _generate(value, subcomponent)
        elif type(value) == list:
            if name == "options":
                items = [_generate(v, Option) for v in value]
            elif name == "option_groups":
                items = [_generate(v, OptionGroup) for v in value]
            elif name in ("include", "trigger_actions_on"):
                items = [f'"{v}"' for v in value]
            elif name == "elements":
                items = [
                    _generate(v, Image) if v.get("type") == "image" else _generate(v)
                    for v in value
                ]
            else:
                items = [_generate(v) for v in value]

            items = ", ".join(items)
            kwarg = f"{name}=[{items}]"
        else:
            kwarg = f"{name}={value}"

        kwargs.append(kwarg)

    if not component:
        if "blocks" in payload and "type" not in payload:
            component = Message
        else:
            type_ = payload.get("type")
            try:
                component = components[type_]
            except KeyError:
                raise CodeGenerationError(
                    f'Can\'t _generate component of type "{type_}."'
                )

    class_name = component.__name__
    kwargs = ", ".join(kwargs)

    return f"{class_name}({kwargs})"


allowed_names = {c.__name__: c for c in components.values()}
allowed_names.update(
    {
        c.__name__: c
        for c in (
            Message,
            Filter,
            DispatchActionConfig,
            Confirm,
            Image,
            Option,
            OptionGroup,
        )
    }
)


def eval_components(code):
    compiled_code = compile(code, "<string>", "eval")
    for name in compiled_code.co_names:
        if name not in allowed_names:
            raise NameError(f"Use of {name} not allowed")
    return eval(code, {"__builtins__": {}}, allowed_names)
