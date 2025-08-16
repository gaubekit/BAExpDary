from otree.api import *


doc = """
    This App is ment to get Calibrate EEG, Get Baseline Data For MFI, ZFE, VAS, and  EEG.
    Further, thus App checkes whether our SART in a 2min Evaluation is a valid representation of Sustained Attention:
        - Playing an original CPT Task for 5min # Todo: not implemented yet
        - Playing Darys SART Task for 5min
        - Playing Darys SART Task for 2 min
        
    Experiment Flow:
        - EEG Calibration with Eyes Open and Eyes closed # TODO: I have to ask michael, fabio or lukas for duration
        - MFI, ZFE, VAS as in App02
        - original CPT 5min
        - SART Dary 5min
        - SART Dary 2min
        - Eyes open as in App02
"""


class C(BaseConstants):
    NAME_IN_URL = 'App01Intro'
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
