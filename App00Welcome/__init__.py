from otree.api import *

# TODO: Short Welcome Page
# TODO: Intro pages for tasks

doc = """
Your app description 
"""


class C(BaseConstants):
    NAME_IN_URL = 'App00Welcome'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass


# PAGES
class MyPage(Page):
    pass

page_sequence = [
    MyPage,
]
