from enum import Enum
from typing import List

class alternative:
    def __init__(self, identifier='', content=''):
        self.identifier = identifier
        self.content = content

class interaction_type(Enum):
    Choice = 0
    TextEntry = 1
    GapMatch = 2
    InlineChoice = 3
    ExtendedText = 4
    HotText = 5
    Info = 6
    SelectPoint = 7
    GraphicAssociate = 8
    GraphicGapMatch = 9
    Slider = 10
    MatchInteraction = 11
    Order = 12
    Combined = 13
    NotDetermined = 14


class item_base:
    identifier = str
    interaction_type = interaction_type
    body = str
    correct_response = str

    def __init__(self, identifier='', interaction_type=interaction_type.NotDetermined,
                 body='', correct_response=''):
        self.identifier = identifier
        self.body = body
        self.correct_response = correct_response
        self.interaction_type = interaction_type

    def to_dict(self):
        return {
            'identifier': self.identifier,
            'body': self.body,
            'interaction_type': 'MC',
            'correct_response': self.correct_response
        }


class multiple_choice_item(item_base):
    alternatives = List[alternative]

    def __init__(self, identifier='', interaction_type=interaction_type.NotDetermined,
                 body='', correct_response='',  alternatives=[]):
        item_base.__init__(self, identifier, interaction_type, body, correct_response)
        self.alternatives = alternatives

    def to_dict(self):
        alternatives = {(chr(idx + 65)): alt.content for idx,
                        alt in enumerate(self.alternatives)}
        # find the index of the correct answer which matches the identifier of the self.alternatives
        correct_response = ''
        if self.correct_response != '':
            correct_response = (chr([k for k, v in enumerate(self.alternatives) if v.identifier == self.correct_response][0] + 65))
        
        return {**item_base.to_dict(self), **alternatives, 'correct_response': correct_response}