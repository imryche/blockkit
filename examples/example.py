from blockkit import Message, Section, Actions, MarkdownText, Button, PlainText


message = Message(
    blocks=[
        Section(
            MarkdownText("You have a new request:\n*<fakeLink.toEmployeeProfile.com|Fred Enriquez - New device request>*")
        ),
        Section(
            MarkdownText("So cool"),
            fields=[
                MarkdownText("*Type:*\nComputer (laptop)"),
                MarkdownText("*When:*\nSubmitted Aut 10"),
                MarkdownText("*Last Update:*\nMar 10, 2015 (3 years, 5 months)"),
                MarkdownText("*Reason:*\nAll vowel keys aren't working."),
                MarkdownText("*Specs:*\nCheetah Pro 15 - Fast, really fast"),
            ]
        ),
        Actions(
            [
                Button(PlainText("Approve"), style=Button.primary, action_id="click_me_123"),
                Button(PlainText("Decline"), style=Button.danger, action_id="click_me_456"),
                Button(PlainText("Discuss"), action_id="click_me_456"),
            ]
        ),
    ]
)

message = message.build()
