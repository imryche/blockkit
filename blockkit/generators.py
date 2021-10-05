from black import FileMode, format_str

from blockkit.components import Component
from blockkit.elements import Image, Option, OptionGroup
from blockkit.objects import Confirm, DispatchActionConfig, Filter
from blockkit.surfaces import Message


class CodeGenerationError(Exception):
    pass


def get_subclasses(cls):
    all_subclasses = []
    for subclass in cls.__subclasses__():
        all_subclasses.append(subclass)
        all_subclasses.extend(get_subclasses(subclass))
    return all_subclasses


components = {
    c.schema()["properties"].get("type", {}).get("default"): c
    for c in get_subclasses(Component)
}
del components[None]


def generate(payload):
    classes = set()
    code = _generate(payload, classes)
    classes = sorted(list(classes))
    imports = "from blockkit import " + ", ".join(classes)
    eval_components(code)
    code = f"{imports}; payload = {code}.build()"
    return code


def generate_pretty(payload):
    return format_str(generate(payload), mode=FileMode())


def _generate(payload, classes, component=None):
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
            kwarg = f"{name}=" + _generate(value, classes, subcomponent)
        elif type(value) == list:
            if name == "options":
                items = [_generate(v, classes, Option) for v in value]
            elif name == "option_groups":
                items = [_generate(v, classes, OptionGroup) for v in value]
            elif name in ("include", "trigger_actions_on"):
                items = [f'"{v}"' for v in value]
            elif name == "elements":
                items = [
                    _generate(v, classes, Image)
                    if v.get("type") == "image"
                    else _generate(v, classes)
                    for v in value
                ]
            else:
                items = [_generate(v, classes) for v in value]

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

    classes.add(class_name)

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
