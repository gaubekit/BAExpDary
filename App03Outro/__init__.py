from otree.api import *


doc = """
    This App collects data for Begin-End Comparison.
    The End-data for MFI, VAS, ZFE, artefactfree 20seconds EEG was already collected in App02 - Round 3.
    In this app data collection for original CPT, SART 2min, SART 5min is collected (similar to App01).
    Further, the eyes-open/eyes-closed calibration is repeated for validation reasons.
    Additionally demographics (age, gender) and "playing video games" will be collected.
"""


class C(BaseConstants):
    NAME_IN_URL = 'App03Outro'
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


class ResultsWaitPage(WaitPage):
    pass


class Results(Page):
    pass


page_sequence = [MyPage, ResultsWaitPage, Results]
