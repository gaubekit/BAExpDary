from otree.api import *
import random, statistics, json


doc = """
    This App collects data for Begin (App01) - End (App03) Comparison.
    The End-data for MFI, VAS, ZFE, artefactfree 20seconds EEG was already collected in App02 - Round 3.
    
    In this app data collection for original CPT, SART 2min, SART 5min is collected (similar to App01) is repated.
        - original CPT 5min
        - SART Dary 5min
        - SART Dary 2min
    Further, the eyes-open/eyes-closed calibration is repeated for validation reasons.
    Additionally demographics (age, gender) and "playing video games" will be collected.
        - Demographics
    Finally, the eyes open/closed calibartion is repeated (data validity)
        - Eyes Open
        - Eyes Closed
    
"""


class C(BaseConstants):
    NAME_IN_URL = 'App03Outro'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    # --- Duration for Eyes Open/Closed --- #
    EEG_EYES_OPEN_END = 60  # * 1.5
    EEG_EYES_CLOSED_END = 60  # * 3

    # --- Parameter for CCPT-III ---#
    N_TRIALS = 30  # Demo: 30 Trials (original ~360)
    NO_GO_LETTER = 'X'
    NO_GO_RATE = 0.10
    LETTERS = [chr(i) for i in range(65, 91)]
    STIM_DURATION_MS = 400  # Demo 400 seconds, (original 250)
    ISI_RANGE_MS = (1500, 2500)
    RESPONSE_KEY = ' '
    # TODO Kübra: check these parameters


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    # ----- Assessment Tasks----- #
    # var for CCPT-III
    ccpt_results_json = models.LongStringField()
    ccpt_hits = models.IntegerField()
    ccpt_omissions = models.IntegerField()
    ccpt_commissions = models.IntegerField()
    ccpt_mean_rt_ms = models.IntegerField()
    ccpt_sd_rt_ms = models.IntegerField()

    # var for SART 5min
    sart5_timings = models.LongStringField(blank=True, null=True)

    # var for SART 2min
    sart2_timings = models.LongStringField(blank=True, null=True)

    # ----- Questionnaire ----- #
    age = models.IntegerField(
        label='How old are you? <br/>(Please enter a valid age between 18 and 65.)',
        min=18,
        max=66,
        error_messages={
            'min_value': 'Please enter an age of at least 18.',
            'max_value': 'Please enter an age of 65 or less.',
            'invalid': 'Please enter a valid age between 18 and 65.',
        }
    )

    gender = models.IntegerField(
        label='<br>How do you identify?',
        choices=[[1, 'Male'], [2, 'Female'], [3, 'Other']],
        blank=False
    )
    other_gender_specify = models.StringField(blank=True, label="")

    vision_problems = models.IntegerField(
        label="<br>Do you have any problems with vision (e.g., recognizing colors)?",
        choices=[[1, 'No'], [2, 'Yes']],
        blank=False
    )
    yes_vision_specify = models.StringField(blank=True, label="")

    motor_problems = models.IntegerField(
        label="<br>Do you have any motor problems with your dominant hand?",
        choices=[[1, 'No'], [2, 'Yes']],
        blank=False
    )
    yes_motor_specify = models.StringField(blank=True, label="")

    gaming_frequency = models.IntegerField(
        label="<br>How regularly do you play computer/video games?",
        choices=[
            [1, "Never"],
            [2, "Rarely (a few times per year)"],
            [3, "Occasionally (once per month)"],
            [4, "Sometimes (a few times per month)"],
            [5, "Often (a few times per week)"],
            [6, "Very often (daily)"],
            [7, "Gaming Pro (multiple hours daily)"]
        ],
        blank=False
    )

    # ----- EEG Timestamps ----- #
    eeg_timestamp_eo_outro_start, eeg_timestamp_eo_outro_stop = models.StringField(), models.StringField()
    eeg_timestamp_ec_outro_start, eeg_timestamp_ec_outro_stop = models.StringField(), models.StringField()
    eeg_timestamp_ccpt_start, eeg_timestamp_ccpt_stop = models.StringField(), models.StringField()


# HELP FUNCTION
def make_trial_sequence():
    """
    Generate a randomized sequence of trials for the Conners Continuous Performance Task (CPT).

    - Calculates the number of Go and No-Go trials based on the total number of trials and the
      specified No-Go rate.
    - Assigns letters to Go trials randomly, ensuring the No-Go letter is excluded.
    - Shuffles all trials to randomize their order.
    - Assigns a random inter-stimulus interval (ISI) within the specified range to each trial.

    Returns:
        list of dict: A list of trial dictionaries, each containing:
            - 'letter' (str): The letter to be displayed.
            - 'is_no_go' (bool): Whether the trial is a No-Go trial.
            - 'isi_ms' (int): The inter-stimulus interval in milliseconds.
    """

    n_no_go = int(C.N_TRIALS * C.NO_GO_RATE)
    n_go = C.N_TRIALS - n_no_go
    go_letters = [l for l in C.LETTERS if l != C.NO_GO_LETTER]

    trials = []
    trials += [{'letter': C.NO_GO_LETTER, 'is_no_go': True} for _ in range(n_no_go)]
    trials += [{'letter': random.choice(go_letters), 'is_no_go': False} for _ in range(n_go)]
    random.shuffle(trials)

    for t in trials:
        t['isi_ms'] = random.randint(*C.ISI_RANGE_MS)
    return trials


def compute_summary_from_results(player: Player):
    """
    Compute summary statistics from a player's trial results in the CPT task.

    - Parses the player's JSON results.
    - Counts the number of ccpt_hits (correct responses to Go trials), ccpt_omissions (missed Go trials),
      and ccpt_commissions (incorrect responses to No-Go trials).
    - Collects reaction times (RTs) for correct Go responses and computes:
        - mean reaction time (ccpt_mean_rt_ms)
        - standard deviation of reaction times (ccpt_sd_rt_ms)
    - Stores these summary statistics as attributes on the player object.

    Args:
        player (Player): The player object containing the 'ccpt_results_json' field with trial data.

    Returns:
        None: The function updates the player object in-place.
    """

    data = json.loads(player.ccpt_results_json)

    ccpt_hits, ccpt_omissions, ccpt_commissions = 0, 0, 0
    rts = []

    for tr in data:
        is_no_go = tr['is_no_go']
        responded = tr['responded']
        rt = tr.get('rt_ms', None)

        if not is_no_go:
            if responded:
                ccpt_hits += 1
                if rt is not None:
                    rts.append(rt)
            else:
                ccpt_omissions += 1
        else:
            if responded:
                ccpt_commissions += 1

    player.ccpt_hits = ccpt_hits
    player.ccpt_omissions = ccpt_omissions
    player.ccpt_commissions = ccpt_commissions
    player.ccpt_mean_rt_ms = int(statistics.mean(rts)) if rts else 0
    player.ccpt_sd_rt_ms = int(statistics.pstdev(rts)) if len(rts) > 1 else 0


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


# PAGES
# ----------------- Assessment Tasks ----------------- #
class AssessmentTaskCCPT(Page):
    """
   Conners Continuous Performance Task (CCPT).

    - Uses 'player' as the form model and stores the raw trial results in the 'ccpt_results_json' field.
    - Prepares variables for the frontend template, including:
        - RESPONSE_KEY: the key used for responses.
        - STIM_DURATION_MS: stimulus presentation duration in milliseconds.
        - TRIALS: a randomized sequence of Go and No-Go trials generated by make_trial_sequence().
    - After the page is completed, computes summary statistics from the player's responses
      (ccpt_hits, ccpt_omissions, ccpt_commissions, mean and SD of reaction times) and stores them on the player object.
    """

    form_model = 'player'
    form_fields = [
        'ccpt_results_json',
        'eeg_timestamp_ccpt_start',
        'eeg_timestamp_ccpt_stop',
    ]

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            RESPONSE_KEY=C.RESPONSE_KEY,
            STIM_DURATION_MS=C.STIM_DURATION_MS,
            TRIALS=make_trial_sequence(),
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        compute_summary_from_results(player)


class SustainedAttentionKeyboard5min(Page):
    @staticmethod
    def live_method(player: Player, data):
        idx = data.get('trial_index')
        if idx is None:
            return
        add_timings(player, idx, {
            'reaction_time': data.get('reaction_time'),
            'is_correct': data.get('is_correct'),
            'trial_type': data.get('trial_type'),
        }, field='sart5_timings')


class SustainedAttentionKeyboard2min(Page):
    @staticmethod
    def live_method(player: Player, data):
        idx = data.get('trial_index')
        if idx is None:
            return
        add_timings(player, idx, {
            'reaction_time': data.get('reaction_time'),
            'is_correct': data.get('is_correct'),
            'trial_type': data.get('trial_type'),
        }, field='sart2_timings')


# ----------------- Questionnaires ----------------- #
class QuestDemographics(Page):
    form_model = 'player'
    form_fields = [
        'age', 'gender', 'other_gender_specify',
        'vision_problems', 'yes_vision_specify',
        'motor_problems', 'yes_motor_specify',
        'gaming_frequency'
    ]


# ----------------- Calibrating EEG ----------------- #
class EyesOpenCalibrationEnd(Page):  # TODO: Define "xx" time
    """
    This page display a cross, after clicking a button. Focusing on this cross without
    any movement allows for XX seconds of artefact-free EEG Date.
    Therefore, the client-timestamp is saved to match it with the EEG timestamps
    """
    form_model = 'player'
    form_fields = ['eeg_timestamp_eo_outro_start', 'eeg_timestamp_eo_outro_stop']


class EyesClosedCalibrationEnd(Page):  # TODO: Define "xx" time
    """
    This page display an eye-symbol, after clicking a button. The eye's should be closed during this time.
    A sound will be played after xx seconds, to indicate the time is over and the eyes can be opend again
    """
    form_model = 'player'
    form_fields = ['eeg_timestamp_ec_outro_start', 'eeg_timestamp_ec_outro_stop']


page_sequence = [
    AssessmentTaskCCPT,
    SustainedAttentionKeyboard2min,
    SustainedAttentionKeyboard5min,
    QuestDemographics,
    EyesOpenCalibrationEnd,
    EyesClosedCalibrationEnd,
]
