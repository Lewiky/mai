import pretty_midi
import IPython.display
import math
import matplotlib.pyplot as plt


def make_music_heterophonic(pitches=60, durs=0.25, pgm=1, is_drum=False, format='inbrowser', sr=16000):
    """Turn a list of a list of numbers into music."""

    # check and convert to list if needed
    pitches = pitches if isinstance(pitches, list) else [pitches]
    durs = durs if isinstance(durs, list) else [durs]
    pgm = pgm if isinstance(pgm, list) else [pgm]
    is_drum = is_drum if isinstance(is_drum, list) else [is_drum]

    # extend short lists if size mismatch (in number of voices)
    num_voices = max(len(pitches), len(durs), len(pgm), len(is_drum))
    pitches += [pitches[-1]] * (num_voices - len(pitches))
    durs += [durs[-1]] * (num_voices - len(durs))
    pgm += [pgm[-1]] * (num_voices - len(pgm))
    is_drum += [is_drum[-1]] * (num_voices - len(is_drum))

    # make music for each and collect into list of instruments
    ins = [make_music(pitches=p, durs=d, pgm=i, is_drum=x, format='MIDI').instruments[0]
           for p,d,i,x in zip(pitches, durs, pgm, is_drum)]

    # create a PrettyMIDI score
    score = pretty_midi.PrettyMIDI()

    # add all instruments
    score.instruments.extend(ins)

    # which format to render
    if format=='MIDI':
        return score
    elif format=='audio':
        return score.fluidsynth(fs=16000)
    elif format=='inbrowser':
        return IPython.display.Audio(score.fluidsynth(fs=sr), rate=sr)
    elif format=='autoplay':
        return IPython.display.Audio(score.fluidsynth(fs=sr), rate=sr, autoplay=True)
    else:
        raise ValueError("So sorry but your `format` argument did not match one of the available options")

def test_make_music_heterophonic():
    v1 = [60 + 2 * x for x in range(8)]
    v2 = [x + 4 for x in v1]
    v3 = [x - 4 for x in v1]
    return make_music_heterophonic(pitches=[v1, v2, v3], durs=0.25, pgm=[1,13,24], format='MIDI')


def make_music(pitches=60, durs=0.333, pgm=1, is_drum=False, format='inbrowser', sr=16000, resolution=220):
    """Turn lists of numbers into music.

    Converts pitch and duration values into MIDI and/or audio playback. Uses
    `pretty_midi` for MIDI representation handling, fluidsynth for resynthesis,
    and `IPython.display.Audio` for browser playback.

    Parameters
    ----------
    pitches : list or scalar
        List of pitches, or scalar if constant pitch. Floating point values are
        interpreted as microtonal pitch deviations.
    durs: list or scalar
        List of durations, or scalar if constant duration.
    pgm: number
        MIDI program number, in range ``[0, 127]``.
    is_drum : bool
        If True use percussion channel 10.
    format : string
        Which format to render sound to?
        - `'MIDI'` returns MIDI as a `pretty_midi` object
        - `'audio'` returns waveforms as a `numpy` nd.array
        - `'inbrowser'` returns `IPython.display.Audio` widget
        - `'autoplay'` returns `IPython.display.Audio` widget and plays it

    Returns
    -------
    synthesized: depends on the value of `format`.

    Notes
    -----
    If len(pitches) and len(durs) do not match, the smaller list is extended to
    match the length of the longer list by repeating the last value.
    """

    # check and convert to list if needed
    pitches = pitches if isinstance(pitches, list) else [pitches]
    durs = durs if isinstance(durs, list) else [durs]

    # extend short lists if size mismatch
    max_length = max(len(pitches), len(durs))
    pitches += [pitches[-1]] * (max_length - len(pitches))
    durs += [durs[-1]] * (max_length - len(durs))

    # create a PrettyMIDI score
    score = pretty_midi.PrettyMIDI(resolution=resolution)

    # create a list of instruments one for each voice (for polypohonic pitch bend)
    num_voices = max([len(p) if isinstance(p, list) else 1 for p in pitches])
    ins = [pretty_midi.Instrument(program=max(pgm-1, 0), is_drum=is_drum) for i in range(num_voices)]

    # iterate through music
    now_time = 0
    for pitch, dur in zip(pitches, durs):

        # rest if pitch is None
        if pitch is not None:

            # convert to list if needed
            pitch = pitch if isinstance(pitch, list) else [pitch]

            # loop through each voice of the list
            for voice_index, pitch_val in enumerate(pitch):

                # split into 12tet and microtones
                micros, twlvtet = math.modf(pitch_val)

                # create a new note
                note = pretty_midi.Note(velocity=100, pitch=int(twlvtet), start=now_time, end=now_time+dur)

                # and add it to the instrument
                ins[voice_index].notes.append(note)

                # if microtonal
                if micros != 0:

                    # create a new pitch bend
                    # note: 4096 is a semitone in standard MIDI +/-2 pitchbend range
                    micropitch = pretty_midi.PitchBend(pitch=int(round(micros*4096)), time=now_time)

                    # and add it to the instrument
                    ins[voice_index].pitch_bends.append(micropitch)

        # advance time
        now_time += dur

    # add instrument to the score
    score.instruments.extend(ins)

    # which format to render
    if format=='MIDI':
        return score
    elif format=='audio':
        return score.fluidsynth(fs=16000)
    elif format=='inbrowser':
        return IPython.display.Audio(score.fluidsynth(fs=sr), rate=sr)
    elif format=='autoplay':
        return IPython.display.Audio(score.fluidsynth(fs=sr), rate=sr, autoplay=True)
    else:
        raise ValueError("So sorry but your `format` argument did not match one of the available options")

def n_max(a):
    '''Return the max of a list that contains None`'''
    return max(filter(lambda x: x is not None, a))

def n_min(a):
    '''Return the min of a list that contains None'''
    return min(filter(lambda x: x is not None, a))

def make_music_plot(pitches=60, durs=0.333, pgm=1, is_drum=False, format='autoplay', sr=16000, figsize=(9,3), cmap='jet', show=True):
    """Plot lists of numbers as music (same API as `make_music`)"""

    # check and convert to list if needed
    pitches = pitches if isinstance(pitches, list) else [pitches]
    durs = durs if isinstance(durs, list) else [durs]

    # extend short lists if size mismatch
    max_length = max(len(pitches), len(durs))
    pitches += [pitches[-1]] * (max_length - len(pitches))
    durs += [durs[-1]] * (max_length - len(durs))

    # plot
    plt.figure(figsize=figsize)
    cm = plt.cm.get_cmap(name=cmap)
    curr_time = 0
    for pitch,dur in zip(pitches, durs):
        if pitch is not None:
            pitch_normed = float(pitch - n_min(pitches)) / (n_max(pitches) - n_min(pitches)) if (n_max(pitches) - n_min(pitches)) != 0 else 1
            plt.scatter([curr_time], [pitch], marker='|', c='white', s=25, zorder=3)
            plt.plot([curr_time, curr_time + dur], [pitch, pitch], lw=5, solid_capstyle='butt', c=cm(pitch_normed), alpha=0.75)
        curr_time += dur

    if show:
        plt.show()
