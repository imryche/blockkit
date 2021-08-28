import pytest
from blockkit import *
from blockkit.generators import generate

cases = []

section_plain_text_case = (
    {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "plain_text",
                    "text": "This is a plain text section block.",
                    "emoji": True,
                },
            }
        ]
    },
    'Message(blocks=[Section(text=PlainText(text="This is a plain text section block.", emoji=True))])',  # noqa
)
cases.append(section_plain_text_case)

section_markdown_text_case = (
    {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        "This is a mrkdwn section block :ghost: *this is bold*, "
                        "and ~this is crossed out~, "
                        "and <https://google.com|this is a link>"
                    ),
                },
            }
        ]
    },
    'Message(blocks=[Section(text=MarkdownText(text="This is a mrkdwn section block :ghost: *this is bold*, and ~this is crossed out~, and <https://google.com|this is a link>"))])',  # noqa
)
cases.append(section_markdown_text_case)

section_text_fields_case = (
    {
        "blocks": [
            {
                "type": "section",
                "fields": [
                    {
                        "type": "plain_text",
                        "text": "*this is plain_text text*",
                        "emoji": True,
                    }
                ],
            }
        ]
    },
    'Message(blocks=[Section(fields=[PlainText(text="*this is plain_text text*", emoji=True)])])',  # noqa
)
cases.append(section_text_fields_case)

section_static_select_case = (
    {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Pick an item from the dropdown list",
                },
                "accessory": {
                    "type": "static_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select an item",
                        "emoji": True,
                    },
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "*this is plain_text text*",
                                "emoji": True,
                            },
                            "value": "value-0",
                        }
                    ],
                    "action_id": "static_select-action",
                },
            }
        ]
    },
    'Message(blocks=[Section(text=MarkdownText(text="Pick an item from the dropdown list"), accessory=StaticSelect(placeholder=PlainText(text="Select an item", emoji=True), options=[Option(text=PlainText(text="*this is plain_text text*", emoji=True), value="value-0")], action_id="static_select-action"))])',  # noqa
)
cases.append(section_static_select_case)

section_static_select_option_groups_case = (
    {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Available options",
                },
                "accessory": {
                    "type": "static_select",
                    "placeholder": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "Manage",
                    },
                    "action_id": "static_select-action",
                    "option_groups": [
                        {
                            "label": {"type": "plain_text", "text": "Group 1"},
                            "options": [
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "*this is plain_text text*",
                                    },
                                    "value": "value-0",
                                }
                            ],
                        },
                        {
                            "label": {"type": "plain_text", "text": "Group 2"},
                            "options": [
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "*this is plain_text text*",
                                    },
                                    "value": "value-3",
                                }
                            ],
                        },
                    ],
                },
            }
        ]
    },
    'Message(blocks=[Section(text=MarkdownText(text="Available options"), accessory=StaticSelect(placeholder=PlainText(emoji=True, text="Manage"), action_id="static_select-action", option_groups=[OptionGroup(label=PlainText(text="Group 1"), options=[Option(text=PlainText(text="*this is plain_text text*"), value="value-0")]), OptionGroup(label=PlainText(text="Group 2"), options=[Option(text=PlainText(text="*this is plain_text text*"), value="value-3")])]))])',  # noqa
)
cases.append(section_static_select_option_groups_case)

section_users_select_case = (
    {
        "blocks": [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "Test block with users select"},
                "accessory": {
                    "type": "users_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select a user",
                        "emoji": True,
                    },
                    "action_id": "users_select-action",
                },
            }
        ]
    },
    'Message(blocks=[Section(text=MarkdownText(text="Test block with users select"), accessory=UsersSelect(placeholder=PlainText(text="Select a user", emoji=True), action_id="users_select-action"))])',  # noqa
)
cases.append(section_users_select_case)

section_channels_select_case = (
    {
        "blocks": [
            {
                "type": "section",
                "block_id": "section678",
                "text": {
                    "type": "mrkdwn",
                    "text": "Pick a channel from the dropdown list",
                },
                "accessory": {
                    "action_id": "text1234",
                    "type": "channels_select",
                    "placeholder": {"type": "plain_text", "text": "Select an item"},
                },
            }
        ]
    },
    'Message(blocks=[Section(block_id="section678", text=MarkdownText(text="Pick a channel from the dropdown list"), accessory=ChannelsSelect(action_id="text1234", placeholder=PlainText(text="Select an item")))])',  # noqa
)
cases.append(section_channels_select_case)

section_conversations_select = (
    {
        "blocks": [
            {
                "type": "section",
                "block_id": "section678",
                "text": {
                    "type": "mrkdwn",
                    "text": "Pick a conversation from the dropdown list",
                },
                "accessory": {
                    "action_id": "text1234",
                    "type": "conversations_select",
                    "placeholder": {"type": "plain_text", "text": "Select an item"},
                },
            }
        ]
    },
    'Message(blocks=[Section(block_id="section678", text=MarkdownText(text="Pick a conversation from the dropdown list"), accessory=ConversationsSelect(action_id="text1234", placeholder=PlainText(text="Select an item")))])',  # noqa
)
cases.append(section_conversations_select)

section_external_select_case = (
    {
        "blocks": [
            {
                "type": "section",
                "block_id": "section678",
                "text": {
                    "type": "mrkdwn",
                    "text": "Pick an item from the dropdown list",
                },
                "accessory": {
                    "action_id": "text1234",
                    "type": "external_select",
                    "placeholder": {"type": "plain_text", "text": "Select an item"},
                    "min_query_length": 3,
                },
            }
        ]
    },
    'Message(blocks=[Section(block_id="section678", text=MarkdownText(text="Pick an item from the dropdown list"), accessory=ExternalSelect(action_id="text1234", placeholder=PlainText(text="Select an item"), min_query_length=3))])',  # noqa
)
cases.append(section_external_select_case)

section_multi_static_select = (
    {
        "blocks": [
            {
                "type": "section",
                "block_id": "section678",
                "text": {"type": "mrkdwn", "text": "Pick items from the list"},
                "accessory": {
                    "action_id": "text1234",
                    "type": "multi_static_select",
                    "placeholder": {"type": "plain_text", "text": "Select items"},
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "*this is plain_text text*",
                            },
                            "value": "value-0",
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "*this is plain_text text*",
                            },
                            "value": "value-1",
                        },
                    ],
                },
            }
        ]
    },
    'Message(blocks=[Section(block_id="section678", text=MarkdownText(text="Pick items from the list"), accessory=MultiStaticSelect(action_id="text1234", placeholder=PlainText(text="Select items"), options=[Option(text=PlainText(text="*this is plain_text text*"), value="value-0"), Option(text=PlainText(text="*this is plain_text text*"), value="value-1")]))])',  # noqa
)
cases.append(section_multi_static_select)

section_multi_users_select_case = (
    {
        "blocks": [
            {
                "type": "section",
                "block_id": "section678",
                "text": {"type": "mrkdwn", "text": "Pick users from the list"},
                "accessory": {
                    "action_id": "text1234",
                    "type": "multi_users_select",
                    "placeholder": {"type": "plain_text", "text": "Select users"},
                },
            }
        ]
    },
    'Message(blocks=[Section(block_id="section678", text=MarkdownText(text="Pick users from the list"), accessory=MultiUsersSelect(action_id="text1234", placeholder=PlainText(text="Select users")))])',  # noqa
)
cases.append(section_multi_users_select_case)

section_multi_channels_select_case = (
    {
        "blocks": [
            {
                "type": "section",
                "block_id": "section678",
                "text": {"type": "mrkdwn", "text": "Pick channels from the list"},
                "accessory": {
                    "action_id": "text1234",
                    "type": "multi_channels_select",
                    "placeholder": {"type": "plain_text", "text": "Select channels"},
                },
            }
        ]
    },
    'Message(blocks=[Section(block_id="section678", text=MarkdownText(text="Pick channels from the list"), accessory=MultiChannelsSelect(action_id="text1234", placeholder=PlainText(text="Select channels")))])',  # noqa
)
cases.append(section_multi_channels_select_case)

section_multi_conversations_select = (
    {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Test block with multi conversations select",
                },
                "accessory": {
                    "type": "multi_conversations_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select conversations",
                        "emoji": True,
                    },
                    "action_id": "multi_conversations_select-action",
                },
            }
        ]
    },
    'Message(blocks=[Section(text=MarkdownText(text="Test block with multi conversations select"), accessory=MultiConversationsSelect(placeholder=PlainText(text="Select conversations", emoji=True), action_id="multi_conversations_select-action"))])',  # noqa
)
cases.append(section_multi_conversations_select)

section_multi_external_select_case = (
    {
        "blocks": [
            {
                "type": "section",
                "block_id": "section678",
                "text": {"type": "mrkdwn", "text": "Pick items from the list"},
                "accessory": {
                    "action_id": "text1234",
                    "type": "multi_external_select",
                    "placeholder": {"type": "plain_text", "text": "Select items"},
                    "min_query_length": 3,
                },
            }
        ]
    },
    'Message(blocks=[Section(block_id="section678", text=MarkdownText(text="Pick items from the list"), accessory=MultiExternalSelect(action_id="text1234", placeholder=PlainText(text="Select items"), min_query_length=3))])',  # noqa
)
cases.append(section_external_select_case)

section_button_case = (
    {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "This is a section block with a button.",
                },
                "accessory": {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Click Me", "emoji": True},
                    "value": "click_me_123",
                    "action_id": "button-action",
                },
            }
        ]
    },
    'Message(blocks=[Section(text=MarkdownText(text="This is a section block with a button."), accessory=Button(text=PlainText(text="Click Me", emoji=True), value="click_me_123", action_id="button-action"))])',  # noqa
)
cases.append(section_button_case)

section_button_confirm_case = (
    {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "This is a section block with a button.",
                },
                "accessory": {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Click Me", "emoji": True},
                    "value": "click_me_123",
                    "action_id": "button-action",
                    "confirm": {
                        "title": {"type": "plain_text", "text": "Are you sure?"},
                        "text": {
                            "type": "mrkdwn",
                            "text": "Wouldn't you prefer a good game of _chess_?",
                        },
                        "confirm": {"type": "plain_text", "text": "Do it"},
                        "deny": {
                            "type": "plain_text",
                            "text": "Stop, I've changed my mind!",
                        },
                    },
                },
            }
        ]
    },
    'Message(blocks=[Section(text=MarkdownText(text="This is a section block with a button."), accessory=Button(text=PlainText(text="Click Me", emoji=True), value="click_me_123", action_id="button-action", confirm=Confirm(title=PlainText(text="Are you sure?"), text=MarkdownText(text="Wouldn\'t you prefer a good game of _chess_?"), confirm=PlainText(text="Do it"), deny=PlainText(text="Stop, I\'ve changed my mind!"))))])',  # noqa
)
cases.append(section_button_confirm_case)

section_link_button_case = (
    {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "This is a section block with a button.",
                },
                "accessory": {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Click Me", "emoji": True},
                    "value": "click_me_123",
                    "url": "https://google.com",
                    "action_id": "button-action",
                },
            }
        ]
    },
    'Message(blocks=[Section(text=MarkdownText(text="This is a section block with a button."), accessory=Button(text=PlainText(text="Click Me", emoji=True), value="click_me_123", url="https://google.com", action_id="button-action"))])',  # noqa
)
cases.append(section_link_button_case)

section_image_case = (
    {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "This is a section block with a button.",
                },
                "accessory": {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Click Me", "emoji": True},
                    "value": "click_me_123",
                    "url": "https://google.com",
                    "action_id": "button-action",
                },
            }
        ]
    },
    'Message(blocks=[Section(text=MarkdownText(text="This is a section block with a button."), accessory=Button(text=PlainText(text="Click Me", emoji=True), value="click_me_123", url="https://google.com", action_id="button-action"))])',  # noqa
)
cases.append(section_link_button_case)

section_image_case = (
    {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "This is a section block with an accessory image.",
                },
                "accessory": {
                    "type": "image",
                    "image_url": (
                        "https://pbs.twimg.com/profile_images/"
                        "625633822235693056/lNGUneLX_400x400.jpg"
                    ),
                    "alt_text": "cute cat",
                },
            }
        ]
    },
    'Message(blocks=[Section(text=MarkdownText(text="This is a section block with an accessory image."), accessory=Image(image_url="https://pbs.twimg.com/profile_images/625633822235693056/lNGUneLX_400x400.jpg", alt_text="cute cat"))])',  # noqa
)
cases.append(section_image_case)

section_overflow_case = (
    {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "This is a section block with an overflow menu.",
                },
                "accessory": {
                    "type": "overflow",
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "*this is plain_text text*",
                                "emoji": True,
                            },
                            "value": "value-0",
                        }
                    ],
                    "action_id": "overflow-action",
                },
            }
        ]
    },
    'Message(blocks=[Section(text=MarkdownText(text="This is a section block with an overflow menu."), accessory=Overflow(options=[Option(text=PlainText(text="*this is plain_text text*", emoji=True), value="value-0")], action_id="overflow-action"))])',  # noqa
)
cases.append(section_overflow_case)

section_datepicker_case = (
    {
        "blocks": [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "Pick a date for the deadline."},
                "accessory": {
                    "type": "datepicker",
                    "initial_date": "1990-04-28",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select a date",
                        "emoji": True,
                    },
                    "action_id": "datepicker-action",
                },
            }
        ]
    },
    'Message(blocks=[Section(text=MarkdownText(text="Pick a date for the deadline."), accessory=DatePicker(initial_date="1990-04-28", placeholder=PlainText(text="Select a date", emoji=True), action_id="datepicker-action"))])',  # noqa
)
cases.append(section_datepicker_case)

section_checkboxes_case = (
    {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "This is a section block with checkboxes.",
                },
                "accessory": {
                    "type": "checkboxes",
                    "options": [
                        {
                            "text": {"type": "mrkdwn", "text": "*this is mrkdwn text*"},
                            "description": {
                                "type": "mrkdwn",
                                "text": "*this is mrkdwn text*",
                            },
                            "value": "value-0",
                        }
                    ],
                    "action_id": "checkboxes-action",
                },
            }
        ]
    },
    'Message(blocks=[Section(text=MarkdownText(text="This is a section block with checkboxes."), accessory=Checkboxes(options=[Option(text=MarkdownText(text="*this is mrkdwn text*"), description=MarkdownText(text="*this is mrkdwn text*"), value="value-0")], action_id="checkboxes-action"))])',  # noqa
)
cases.append(section_checkboxes_case)

section_radio_buttons_case = (
    {
        "blocks": [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "Section block with radio buttons"},
                "accessory": {
                    "type": "radio_buttons",
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "*this is plain_text text*",
                                "emoji": True,
                            },
                            "value": "value-0",
                        }
                    ],
                    "action_id": "radio_buttons-action",
                },
            }
        ]
    },
    'Message(blocks=[Section(text=MarkdownText(text="Section block with radio buttons"), accessory=RadioButtons(options=[Option(text=PlainText(text="*this is plain_text text*", emoji=True), value="value-0")], action_id="radio_buttons-action"))])',  # noqa
)
cases.append(section_radio_buttons_case)

actions_all_selects_case = (
    {
        "blocks": [
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "conversations_select",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Select a conversation",
                            "emoji": True,
                        },
                        "action_id": "actionId-0",
                    },
                    {
                        "type": "channels_select",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Select a channel",
                            "emoji": True,
                        },
                        "action_id": "actionId-1",
                    },
                    {
                        "type": "users_select",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Select a user",
                            "emoji": True,
                        },
                        "action_id": "actionId-2",
                    },
                    {
                        "type": "static_select",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Select an item",
                            "emoji": True,
                        },
                        "options": [
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "*this is plain_text text*",
                                    "emoji": True,
                                },
                                "value": "value-0",
                            }
                        ],
                        "action_id": "actionId-3",
                    },
                ],
            }
        ]
    },
    'Message(blocks=[Actions(elements=[ConversationsSelect(placeholder=PlainText(text="Select a conversation", emoji=True), action_id="actionId-0"), ChannelsSelect(placeholder=PlainText(text="Select a channel", emoji=True), action_id="actionId-1"), UsersSelect(placeholder=PlainText(text="Select a user", emoji=True), action_id="actionId-2"), StaticSelect(placeholder=PlainText(text="Select an item", emoji=True), options=[Option(text=PlainText(text="*this is plain_text text*", emoji=True), value="value-0")], action_id="actionId-3")])])',  # noqa
)
cases.append(actions_all_selects_case)

actions_filtered_conversations_select_case = (
    {
        "blocks": [
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "conversations_select",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Select private conversation",
                            "emoji": True,
                        },
                        "filter": {"include": ["private"]},
                        "action_id": "actionId-0",
                    }
                ],
            }
        ]
    },
    'Message(blocks=[Actions(elements=[ConversationsSelect(placeholder=PlainText(text="Select private conversation", emoji=True), filter=Filter(include=["private"]), action_id="actionId-0")])])',  # noqa
)
cases.append(actions_filtered_conversations_select_case)

actions_selects_with_initial_options = (
    {
        "blocks": [
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "conversations_select",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Select a conversation",
                            "emoji": True,
                        },
                        "initial_conversation": "G12345678",
                        "action_id": "actionId-0",
                    },
                    {
                        "type": "users_select",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Select a user",
                            "emoji": True,
                        },
                        "initial_user": "U12345678",
                        "action_id": "actionId-1",
                    },
                    {
                        "type": "channels_select",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Select a channel",
                            "emoji": True,
                        },
                        "initial_channel": "C12345678",
                        "action_id": "actionId-2",
                    },
                ],
            }
        ]
    },
    'Message(blocks=[Actions(elements=[ConversationsSelect(placeholder=PlainText(text="Select a conversation", emoji=True), initial_conversation="G12345678", action_id="actionId-0"), UsersSelect(placeholder=PlainText(text="Select a user", emoji=True), initial_user="U12345678", action_id="actionId-1"), ChannelsSelect(placeholder=PlainText(text="Select a channel", emoji=True), initial_channel="C12345678", action_id="actionId-2")])])',  # noqa
)
cases.append(actions_selects_with_initial_options)

divider_case = ({"blocks": [{"type": "divider"}]}, "Message(blocks=[Divider()])")
cases.append(divider_case)

image_title_case = (
    {
        "blocks": [
            {
                "type": "image",
                "title": {"type": "plain_text", "text": "I Need a Marg", "emoji": True},
                "image_url": (
                    "https://assets3.thrillist.com/v1/image/"
                    "1682388/size/tl-horizontal_main.jpg"
                ),
                "alt_text": "marg",
            }
        ]
    },
    'Message(blocks=[ImageBlock(title=PlainText(text="I Need a Marg", emoji=True), image_url="https://assets3.thrillist.com/v1/image/1682388/size/tl-horizontal_main.jpg", alt_text="marg")])',  # noqa
)
cases.append(image_title_case)

image_no_title_case = (
    {
        "blocks": [
            {
                "type": "image",
                "image_url": (
                    "https://i1.wp.com/thetempest.co/wp-content/uploads/2017/08/"
                    "The-wise-words-of-Michael-Scott-Imgur-2.jpg?w=1024&ssl=1"
                ),
                "alt_text": "inspiration",
            }
        ]
    },
    'Message(blocks=[ImageBlock(image_url="https://i1.wp.com/thetempest.co/wp-content/uploads/2017/08/The-wise-words-of-Michael-Scott-Imgur-2.jpg?w=1024&ssl=1", alt_text="inspiration")])',  # noqa
)
cases.append(image_no_title_case)


context_plain_text_case = (
    {
        "blocks": [
            {
                "type": "context",
                "elements": [
                    {
                        "type": "plain_text",
                        "text": "Author: K A Applegate",
                        "emoji": True,
                    }
                ],
            }
        ]
    },
    'Message(blocks=[Context(elements=[PlainText(text="Author: K A Applegate", emoji=True)])])',  # noqa
)
cases.append(context_plain_text_case)

context_mrkdwn_case = (
    {
        "blocks": [
            {
                "type": "context",
                "elements": [
                    {
                        "type": "image",
                        "image_url": (
                            "https://pbs.twimg.com/profile_images/"
                            "625633822235693056/lNGUneLX_400x400.jpg"
                        ),
                        "alt_text": "cute cat",
                    },
                    {"type": "mrkdwn", "text": "*Cat* has approved this message."},
                ],
            }
        ]
    },
    'Message(blocks=[Context(elements=[Image(image_url="https://pbs.twimg.com/profile_images/625633822235693056/lNGUneLX_400x400.jpg", alt_text="cute cat"), MarkdownText(text="*Cat* has approved this message.")])])',  # noqa
)
cases.append(context_mrkdwn_case)

input_dispatches_actions_case = (
    {
        "blocks": [
            {
                "dispatch_action": True,
                "type": "input",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "plain_text_input-action",
                },
                "label": {"type": "plain_text", "text": "Label", "emoji": True},
            }
        ]
    },
    'Message(blocks=[Input(dispatch_action=True, element=PlainTextInput(action_id="plain_text_input-action"), label=PlainText(text="Label", emoji=True))])',  # noqa
)
cases.append(input_dispatches_actions_case)

input_dispatches_custom_actions_case = (
    {
        "blocks": [
            {
                "dispatch_action": True,
                "type": "input",
                "element": {
                    "type": "plain_text_input",
                    "dispatch_action_config": {
                        "trigger_actions_on": ["on_character_entered"]
                    },
                    "action_id": "plain_text_input-action",
                },
                "label": {"type": "plain_text", "text": "Label", "emoji": True},
            }
        ]
    },
    'Message(blocks=[Input(dispatch_action=True, element=PlainTextInput(dispatch_action_config=DispatchActionConfig(trigger_actions_on=["on_character_entered"]), action_id="plain_text_input-action"), label=PlainText(text="Label", emoji=True))])',  # noqa
)
cases.append(input_dispatches_custom_actions_case)

input_multiline_plain_text_case = (
    {
        "blocks": [
            {
                "type": "input",
                "element": {
                    "type": "plain_text_input",
                    "multiline": True,
                    "action_id": "plain_text_input-action",
                },
                "label": {"type": "plain_text", "text": "Label", "emoji": True},
            }
        ]
    },
    'Message(blocks=[Input(element=PlainTextInput(multiline=True, action_id="plain_text_input-action"), label=PlainText(text="Label", emoji=True))])',  # noqa
)
cases.append(input_multiline_plain_text_case)

input_plain_text_case = (
    {
        "blocks": [
            {
                "type": "input",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "plain_text_input-action",
                },
                "label": {"type": "plain_text", "text": "Label", "emoji": True},
            }
        ]
    },
    'Message(blocks=[Input(element=PlainTextInput(action_id="plain_text_input-action"), label=PlainText(text="Label", emoji=True))])',  # noqa
)
cases.append(input_plain_text_case)

header_case = (
    {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "This is a header block",
                    "emoji": True,
                },
            }
        ]
    },
    'Message(blocks=[Header(text=PlainText(text="This is a header block", emoji=True))])',  # noqa
)
cases.append(header_case)

modal_case = (
    {
        "type": "modal",
        "title": {"type": "plain_text", "text": "My App", "emoji": True},
        "submit": {"type": "plain_text", "text": "Submit", "emoji": True},
        "close": {"type": "plain_text", "text": "Cancel", "emoji": True},
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "plain_text",
                    "text": "This is a plain text section block.",
                    "emoji": True,
                },
            }
        ],
    },
    'Modal(title=PlainText(text="My App", emoji=True), submit=PlainText(text="Submit", emoji=True), close=PlainText(text="Cancel", emoji=True), blocks=[Section(text=PlainText(text="This is a plain text section block.", emoji=True))])',  # noqa
)
cases.append(modal_case)

app_home_case = (
    {
        "type": "home",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "plain_text",
                    "text": "This is a plain text section block.",
                    "emoji": True,
                },
            }
        ],
    },
    'Home(blocks=[Section(text=PlainText(text="This is a plain text section block.", emoji=True))])',  # noqa,
)
cases.append(app_home_case)

escape_case = (
    {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "plain_text",
                    "text": "This is a plain\n\ttext section block.",
                    "emoji": True,
                },
            }
        ]
    },
    'Message(blocks=[Section(text=PlainText(text="This is a plain\\n\\ttext section block.", emoji=True))])',  # noqa
)
cases.append(escape_case)


@pytest.mark.parametrize(
    "payload, expected_code",
    cases,
)
def test_generate(payload, expected_code):
    code = generate(payload)
    assert code == expected_code
