from blockkit import Section, Text, Image


section = Section(
    Text('This is title'),
    fields=[
        Text('This is first field'),
        Text('This is second field'),
    ],
    accessory=Image('http://placekitten.com/200/200', 'Kittens'),
    block_id='kittens block'
)
section.builder_url()
