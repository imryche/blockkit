from typing import Dict, List, Optional, Set, Type, TypeVar, cast

from black import FileMode, format_str

from blockkit.components import Component
from blockkit.elements import Image, MarkdownOption, OptionGroup, PlainOption
from blockkit.objects import (
    Confirm,
    DispatchActionConfig,
    Filter,
    MarkdownText,
    PlainText,
)
from blockkit.surfaces import Message

T = TypeVar("T")


class CodeGenerationError(Exception):
    pass


def get_subclasses(cls: Type[T]) -> List[Type[T]]:
    all_subclasses = []
    for subclass in cls.__subclasses__():
        all_subclasses.append(subclass)
        all_subclasses.extend(get_subclasses(subclass))
    return all_subclasses


components: Dict[str, Type[Component]] = {
    c.schema()["properties"].get("type", {}).get("default"): c
    for c in get_subclasses(Component)
}
del components[None]


def generate(payload: Dict, compact: bool = False) -> str:
    classes: Set[str] = set()
    code = _generate(payload, classes, compact=compact)
    imports = "from blockkit import " + ", ".join(sorted(classes))
    eval_components(code)
    code = f"{imports}; payload = {code}.build()"
    return code


def generate_pretty(payload: Dict, compact: bool = False) -> str:
    return format_str(generate(payload, compact=compact), mode=FileMode()).rstrip()


def _generate(
    payload: Dict,
    classes: Set[str],
    component: Optional[Type[Component]] = None,
    compact: bool = False,
) -> str:
    text, emoji, verbatim = None, None, None
    kwargs = []

    for name, value in payload.items():
        if name == "type":
            continue

        emoji = value if name == "emoji" else None
        verbatim = value if name == "verbatim" else None

        if type(value) == str:
            if name == "text":
                value = (
                    value.replace("\n", "\\n").replace("\t", "\\t").replace('"', '\\"')
                )
                text = value
            quote = "'" if '"' in value else '"'
            kwarg = f"{name}={quote}{value}{quote}"

        elif type(value) == dict:
            subcomponent: Optional[Type[Component]] = None
            if name == "filter":
                subcomponent = Filter
            elif name == "dispatch_action_config":
                subcomponent = DispatchActionConfig
            elif name == "initial_option":
                subcomponent = (
                    PlainOption
                    if value["text"]["type"] == "plain_text"
                    else MarkdownOption
                )
            elif name == "confirm" and "confirm" in value:
                subcomponent = Confirm
            elif name == "accessory" and value.get("type") == "image":
                subcomponent = Image
            kwarg = f"{name}=" + _generate(
                value, classes, subcomponent, compact=compact
            )

        elif type(value) == list:
            if name in ["options", "initial_options"]:
                items = []
                for v in value:
                    subcomponent = (
                        PlainOption
                        if v["text"]["type"] == "plain_text"
                        else MarkdownOption
                    )
                    items.append(_generate(v, classes, subcomponent, compact))
            elif name == "option_groups":
                items = [
                    _generate(v, classes, OptionGroup, compact=compact) for v in value
                ]
            elif name in ("include", "trigger_actions_on"):
                items = [f'"{v}"' for v in value]
            elif name == "elements":
                items = [
                    _generate(v, classes, Image, compact)
                    if v.get("type") == "image"
                    else _generate(v, classes, compact=compact)
                    for v in value
                ]
            else:
                items = [_generate(v, classes, compact=compact) for v in value]

            joined_items = ", ".join(items)
            kwarg = f"{name}=[{joined_items}]"

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

    if compact:
        if (
            component is PlainText
            and emoji is not False
            or component is MarkdownText
            and verbatim is not True
        ):
            return f'"{text}"'

    class_name = component.__name__
    joined_kwargs = ", ".join(kwargs)

    classes.add(class_name)

    return f"{class_name}({joined_kwargs})"


allowed_names: Dict[str, Type[Component]] = {c.__name__: c for c in components.values()}
allowed_names.update(
    {
        c.__name__: cast(Type[Component], c)
        for c in [
            Message,
            Filter,
            DispatchActionConfig,
            Confirm,
            Image,
            PlainOption,
            MarkdownOption,
            OptionGroup,
        ]
    }
)


def eval_components(code: str) -> Dict:
    compiled_code = compile(code, "<string>", "eval")
    for name in compiled_code.co_names:
        if name not in allowed_names:
            raise NameError(f"Use of {name} not allowed")
    return eval(code, {"__builtins__": {}}, allowed_names)
