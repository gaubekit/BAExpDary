from otree.api import *
import json

doc = """
    - 3 Rounds of Assessment Block +  Mental Fatigue Block
    - Mental Fatigue block is not displayed in Round Number 2
    
    Assessment Block:
        Tasks:
        ======
            - Dary Aim Trainer
            - Reaction Time Keyboard
            - Reaction Time Mouse
            - SART Keyboard
            - SART Mouse
            - Choice Reaction Time Keyboard
            -  Choice Reaction Time Mouse
        
        Questionnaires:
        ==============
            - MFI Subscale Mental Fatigue
            - ZFE Subscale General Fatigue
            - Visual Analogous Scales
                - Motivation  # Note: Motivation + Sleepiness + Mood = Readiness
                - Sleepiness
                - Mood
                - Frustration
                - Workload
                - Mental Fatigue
            - Eyes open Calibration
            
    Mental Fatigue Block
        - MATB-II Level X
        - VAS + Eyes Open # Note: Repetition of Code
        - MATB-II Level X
        - VAS + Eyes Open
        - MATB-II Level X
"""


class C(BaseConstants):
    NAME_IN_URL = 'App02Main'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 3
    MATB_LEVELS = [
        [2, 1, 3],  # Level sequence in first iteration
        [3, 1, 2]  # Level sequence in second iteration
    ]  # Note: not used, hardcoded in js
    EEG_EYES_OPEN_INBETWEEN = 20  # central configuration for eyes open calibration


class Subsession(BaseSubsession):
    pass



class Group(BaseGroup):
    pass


class Player(BasePlayer):
    """
    This class defines the player var
    Each var defined here is automatically stored int PostgreSQL,
    as long the respective form_fields are included in the page
    """
    # ----- Assessment Tasks----- #
    # TODO: Assessment Task Metrics go here
    timings_json = models.LongStringField(blank=True, null=True)
    aim_timings = models.LongStringField(blank=True, null=True)
    sart_timings = models.LongStringField(blank=True, null=True)
    sart_mt_timings = models.LongStringField(blank=True, null=True)
    rt_timings = models.LongStringField(blank=True, null=True)
    rt_mt_timings = models.LongStringField(blank=True, null=True)
    crt_timings = models.LongStringField(blank=True, null=True)
    crt_mt_timings = models.LongStringField(blank=True, null=True)

    # ----- Assessment Questionnaires ----- #
    # var for Multidimensional Fatigue Inventory (MFI)
    # Note: extended scales;
    ## When I am doing something, I can keep my thoughts on it.
    mfi_mental_1 = models.IntegerField(widget=widgets.RadioSelect, choices=list(range(-10, 11)))
    ## I can concentrate well.
    mfi_mental_2 = models.IntegerField(widget=widgets.RadioSelect, choices=list(range(-10, 11)))
    ## It takes a lot of effort to concentrate on things.
    mfi_mental_3 = models.IntegerField(widget=widgets.RadioSelect, choices=list(range(-10, 11)))
    ## My thoughts easily wander.
    mfi_mental_4 = models.IntegerField(widget=widgets.RadioSelect, choices=list(range(-10, 11)))

    # var for Zoom Fatigue & Exhaustion Questionnaire
    # Note: extended scales; replaced "after this video conference" with "right now"
    ## How much do you dread having to do things righ now?
    zfe_general_1 = models.IntegerField(widget=widgets.RadioSelect, choices=list(range(-10, 11)))
    ## How much do you feel like doing nothing righ now?
    zfe_general_2 = models.IntegerField(widget=widgets.RadioSelect, choices=list(range(-10, 11)))
    ## How much do you feel too tired to do other things righ now?
    zfe_general_3 = models.IntegerField(widget=widgets.RadioSelect, choices=list(range(-10, 11)))

    # var for Visual Analogous Scales
    mental_fatigue = models.IntegerField(min=0, max=100)
    motivation = models.IntegerField(min=0, max=101)
    mental_workload = models.IntegerField(min=0, max=100)
    frustration = models.IntegerField(min=0, max=100)
    sleepiness = models.IntegerField(min=0, max=100)
    mood = models.IntegerField(min=0, max=100)

    # var for Timestamp EEG
    eeg_timestamp_eyes_open_start, eeg_timestamp_eyes_open_stop = models.StringField(), models.StringField()

    # ----- MATB PERFORMANCE ----- #
    # var for first block
    sysmon_score_a = models.IntegerField(min=0, max=100)
    tracking_score_a = models.IntegerField(min=0, max=100)
    comm_score_a = models.IntegerField(min=0, max=100)
    resman_score_a = models.IntegerField(min=0, max=100)

    # var for second block
    sysmon_score_b = models.IntegerField(min=0, max=100)
    tracking_score_b = models.IntegerField(min=0, max=100)
    comm_score_b = models.IntegerField(min=0, max=100)
    resman_score_b = models.IntegerField(min=0, max=100)

    # var for third block
    sysmon_score_c = models.IntegerField(min=0, max=100)
    tracking_score_c = models.IntegerField(min=0, max=100)
    comm_score_c = models.IntegerField(min=0, max=100)
    resman_score_c = models.IntegerField(min=0, max=100)

    # ----- Short Assessment ----- #
    # var for first block
    mental_fatigue_a = models.IntegerField(min=0, max=100)
    motivation_a = models.IntegerField(min=0, max=101)
    mental_workload_a = models.IntegerField(min=0, max=100)
    frustration_a = models.IntegerField(min=0, max=100)
    eeg_timestamp_eyes_open_a_start, eeg_timestamp_eyes_open_a_stop = models.StringField(), models.StringField()

    # var for second block
    mental_fatigue_b = models.IntegerField(min=0, max=100)
    motivation_b = models.IntegerField(min=0, max=101)
    mental_workload_b = models.IntegerField(min=0, max=100)
    frustration_b = models.IntegerField(min=0, max=100)
    eeg_timestamp_eyes_open_b_start, eeg_timestamp_eyes_open_b_stop = models.StringField(), models.StringField()

    # var for third block
    mental_fatigue_c = models.IntegerField(min=0, max=100)
    motivation_c = models.IntegerField(min=0, max=101)
    mental_workload_c = models.IntegerField(min=0, max=100)
    frustration_c = models.IntegerField(min=0, max=100)
    eeg_timestamp_eyes_open_c_start, eeg_timestamp_eyes_open_c_stop = models.StringField(), models.StringField()


# PAGES
# ----------------- Assessment Block - Tasks ----------------- #
# all tasks are played for 2 minutes
def add_timings(player, idx, updates: dict, field: str = 'timings_json'):
    """
    Append/merge per-trial timing data into a JSON-backed dictionary on the Player.

    - Expects a JSON field on `player` (default: 'timings_json') that stores a dict of trial entries,
      keyed by the trial index (string).
    - Safely reads the existing JSON using `player.field_maybe_none(field)`:
        - Parses JSON to a dict if present.
        - Falls back to an empty dict on null/invalid/non-dict content.
    - Ensures the entry for the given trial key exists and is a dict, then merges `updates`:
        - Skips keys whose values are `None` (does not overwrite existing values with nulls).
        - Writes the merged entry back under the trial key.
    - Note: This helper updates the in-memory `store`; persisting back to the model
      (e.g., `setattr(player, field, json.dumps(store))`) must be done by the caller
      or elsewhere in the calling flow.
    """
    key = str(idx)

    # safe read for nullable fields
    raw = player.field_maybe_none(field)
    try:
        store = json.loads(raw) if raw else {}
        if not isinstance(store, dict):
            store = {}
    except Exception:
        store = {}

    # merge (skip None values)
    entry = store.get(key)
    if not isinstance(entry, dict):
        entry = {}
    entry.update({k: v for k, v in updates.items() if v is not None})
    store[key] = entry

    # assign back 
    setattr(player, field, json.dumps(store))


class Aim(Page):  # better name?
    @staticmethod
    def live_method(player: Player, data):
        idx = data.get('trial_index')
        if idx is None:
            return
        add_timings(player, idx, {
            'reaction_time': data.get('leave_time'),
            'response_time': data.get('response_time'),
        }, field='aim_timings')


class ReactionTimeKeyboard(Page):
    @staticmethod
    def live_method(player: Player, data):
        idx = data.get('trial_index')
        if idx is None:
            return
        add_timings(player, idx, {
            'reaction_time': data.get('reaction_time'),
        }, field='rt_timings')


class ReactionTimeMouse(Page):
    @staticmethod
    def live_method(player: Player, data):
        idx = data.get('trial_index')
        if idx is None:
            return
        add_timings(player, idx, {
            'movement_time': data.get('response_time'),
            'reaction_time': data.get('leave_time'),
        }, field='rt_mt_timings')


class SustainedAttentionKeyboard(Page):
    @staticmethod
    def live_method(player: Player, data):
        idx = data.get('trial_index')
        if idx is None:
            return
        add_timings(player, idx, {
            'reaction_time': data.get('reaction_time'),
            'is_correct': data.get('is_correct'),
            'trial_type': data.get('trial_type'),
        }, field='sart_timings')


class SustainedAttentionMouse(Page):
    @staticmethod
    def live_method(player: Player, data):
        idx = data.get('trial_index')
        if idx is None:
            return
        add_timings(player, idx, {
            'trial_type': data.get('trial_type'),        # "go" | "nogo"
            'is_correct': data.get('is_correct'),
            'reaction_time': data.get('reaction_time'),  # equals leave_time on correct Go
            'movement_time': data.get('movement_time'),  # click after release
            'leave_time': data.get('leave_time'),  
            'error_type': data.get('error_type'),        # commission | omission | no_click | no_release | null
      }, field='sart_mt_timings')


class ChoiceReactionTimeKeyboard(Page):
    @staticmethod
    def live_method(player: Player, data):
        idx = data.get('trial_index')
        if idx is None:
            return
        add_timings(player, idx, {
            'reaction_time': data.get('reaction_time'),
            'movement_time': data.get('movement_time'),
            'is_correct': data.get('is_correct'),
            'clicked_index': data.get('clicked_index'),
        }, field='crt_timings')


class ChoiceReactionTimeMouse(Page):
    @staticmethod
    def live_method(player: Player, data):
        idx = data.get('trial_index')
        if idx is None:
            return
        add_timings(player, idx, {
            'reaction_time': data.get('reaction_time'),
            'movement_time': data.get('movement_time'),
            'is_correct': data.get('is_correct'),
            'clicked_index': data.get('clicked_index'),
        }, field='crt_mt_timings')


# ----------------- Assessment Block - Questionnaires ----------------- #

class MentalFatigueQuestionnaires(Page):
    """
    Questionnaires for Mental Fatigue
    - ZFE Subscale General
    - MFI Subscale Mental
    """
    form_model = 'player'
    form_fields = ['mfi_mental_1', 'mfi_mental_2', 'mfi_mental_3', 'mfi_mental_4',
                   'zfe_general_1', 'zfe_general_2', 'zfe_general_3']


class VisualAnalogousScales(Page):
    """
    Visual-Analogous-Scales (VAS) for mood, sleepiness, motivation, workload, frustration, fatigue.
    Quick and Dirty Solution - Instructions not validated.
    In general, mental readiness is measured with mood, sleepiness and motivation
    """
    form_model = 'player'
    form_fields = ['mental_fatigue', 'motivation', 'sleepiness', 'mood', 'mental_workload', 'frustration']


class EyesOpenCalibration(Page):
    """
    This page display a cross, after clicking a button. Focusing on this cross without
    any movement allows for 20 seconds of artefact-free EEG Date.
    Therefore, the client-timestamp is saved to match it with the EEG timestamps
    """
    form_model = 'player'
    form_fields = ['eeg_timestamp_eyes_open_start', 'eeg_timestamp_eyes_open_stop']


# ----------------- Mental Fatigue Block  ----------------- #
# only displayed in round 1 and 2

# first block (A)
class MatbTaskA(Page):
    """
    Inducing Mental Fatigue via cockpit control task for ~5min.
        - round1 -> level 2
        - round 2 -> level 3
        - round 3 -> skipped
    """
    form_model = 'player'
    form_fields = ['sysmon_score_a', 'tracking_score_a', 'comm_score_a', 'resman_score_a']

    @staticmethod
    def is_displayed(player):
        return player.round_number < 3


class VisualAnalogousScalesShortA(Page):
    """
        Shorter Visual-Analogous-Scales (VAS) for motivation, workload, frustration, fatigue.
    """
    form_model = 'player'
    form_fields = ['mental_fatigue_a', 'motivation_a', 'mental_workload_a', 'frustration_a']

    @staticmethod
    def is_displayed(player):
        return player.round_number < 3


class EyesOpenCalibrationA(Page):
    """ 20 seconds of artefact-free EEG Date """
    form_model = 'player'
    form_fields = ['eeg_timestamp_eyes_open_a_start', 'eeg_timestamp_eyes_open_a_stop']

    @staticmethod
    def is_displayed(player):
        return player.round_number < 3


# second block (B)
class MatbTaskB(Page):
    """
    Inducing Mental Fatigue via cockpit control task for ~5min.
        - round1 -> level 1
        - round 2 -> level 1
        - round 3 -> skipped
    """
    form_model = 'player'
    form_fields = ['sysmon_score_b', 'tracking_score_b', 'comm_score_b', 'resman_score_b']

    @staticmethod
    def is_displayed(player):
        return player.round_number < 3


class VisualAnalogousScalesShortB(Page):
    """
    Shorter Visual-Analogous-Scales (VAS) for motivation, workload, frustration, fatigue.
    """
    form_model = 'player'
    form_fields = ['mental_fatigue_b', 'motivation_b', 'mental_workload_b', 'frustration_b']

    @staticmethod
    def is_displayed(player):
        return player.round_number < 3


class EyesOpenCalibrationB(Page):
    """ 20 seconds of artefact-free EEG Date """
    form_model = 'player'
    form_fields = ['eeg_timestamp_eyes_open_b_start', 'eeg_timestamp_eyes_open_b_stop']

    @staticmethod
    def is_displayed(player):
        return player.round_number < 3


# third block (C)
class MatbTaskC(Page):
    """
    Inducing Mental Fatigue via cockpit control task for ~5min.
        - round1 -> level 3
        - round 2 -> level 2
        - round 3 -> skipped
    """
    form_model = 'player'
    form_fields = ['sysmon_score_c', 'tracking_score_c', 'comm_score_c', 'resman_score_c']

    @staticmethod
    def is_displayed(player):
        return player.round_number < 3


class VisualAnalogousScalesShortC(Page):
    """
    Shorter Visual-Analogous-Scales (VAS) for motivation, workload, frustration, fatigue.
    """
    form_model = 'player'
    form_fields = ['mental_fatigue_c', 'motivation_c', 'mental_workload_c', 'frustration_c']

    @staticmethod
    def is_displayed(player):
        return player.round_number < 3


class EyesOpenCalibrationC(Page):
    """ 20 seconds of artefact-free EEG Date """
    form_model = 'player'
    form_fields = ['eeg_timestamp_eyes_open_c_start', 'eeg_timestamp_eyes_open_c_stop']

    @staticmethod
    def is_displayed(player):
        return player.round_number < 3


page_sequence = [
    # -- Assessment Block Tasks -- #
    Aim,
    ReactionTimeKeyboard,
    ReactionTimeMouse,
    SustainedAttentionKeyboard,
    SustainedAttentionMouse,
    ChoiceReactionTimeKeyboard,
    ChoiceReactionTimeMouse,

    # -- Assessment Block Questionnaires --#
    MentalFatigueQuestionnaires,
    VisualAnalogousScales,
    EyesOpenCalibration,

    # -- Mental Fatigue Block --#
    MatbTaskA,
    VisualAnalogousScalesShortA,
    EyesOpenCalibrationA,
    MatbTaskB,
    VisualAnalogousScalesShortB,
    EyesOpenCalibrationB,
    MatbTaskC,
    VisualAnalogousScalesShortC,
    EyesOpenCalibrationC,
]
