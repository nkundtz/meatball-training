"""Functions for generating playback sequences."""

from typing import List, Dict, Tuple
import random
from .theory import NOTES, CHORD_TYPES
from .progressions import generate_two_five_one, generate_diatonic_cycle

def generate_chord_sequence(
    num_chords: int,
    progression_type: str,
    selected_notes: List[str],
    selected_chord_types: List[str],
    seconds_per_measure: float
) -> Tuple[List[Dict], List[str]]:
    """Generate a sequence of chords and their corresponding MIDI notes.
    
    Args:
        num_chords: Number of chords to generate
        progression_type: Type of progression ("Random", "II-V-I", "Diatonic Cycle")
        selected_notes: List of root notes to choose from
        selected_chord_types: List of chord types to choose from
        seconds_per_measure: Duration of each measure in seconds
        
    Returns:
        Tuple of (MIDI sequence, display sequence)
    """
    sequence = []
    display_sequence = []
    
    if progression_type == "II-V-I":
        while len(display_sequence) < num_chords:
            root = random.choice(selected_notes)
            progression = generate_two_five_one(root)
            display_sequence.extend(progression)
            if len(display_sequence) > num_chords:
                display_sequence = display_sequence[:num_chords]
                break
    
    elif progression_type == "Diatonic Cycle":
        while len(display_sequence) < num_chords:
            root = random.choice(selected_notes)
            progression = generate_diatonic_cycle(root)
            display_sequence.extend(progression)
            if len(display_sequence) > num_chords:
                display_sequence = display_sequence[:num_chords]
                break
    
    else:
        # Generate random chords
        for _ in range(num_chords):
            note = random.choice(selected_notes)
            chord_type = random.choice(selected_chord_types)
            display_chord = f"{note}{CHORD_TYPES[chord_type]}"
            display_sequence.append(display_chord)
    
    # Convert display chords to MIDI sequence
    for i, chord in enumerate(display_sequence):
        # Extract the root note from the chord symbol
        root_note = chord[0]
        if len(chord) > 1 and chord[1] in ['b', '#']:
            root_note += chord[1]
            
        # Use octave 2 for a deep double bass sound
        midi_note = f"{root_note}2"
        sequence.append({
            'note': midi_note,
            'time': i * seconds_per_measure,
            'duration': seconds_per_measure * 0.95,
            'instrument': 'bass'
        })
    
    return sequence, display_sequence

def generate_metronome_sequence(
    num_measures: int,
    beats_per_measure: int,
    seconds_per_beat: float
) -> List[float]:
    """Generate metronome clicks for each beat.
    
    Args:
        num_measures: Number of measures
        beats_per_measure: Beats per measure (time signature)
        seconds_per_beat: Duration of each beat in seconds
        
    Returns:
        List of metronome click times
    """
    sequence = []
    total_beats = num_measures * beats_per_measure
    
    for i in range(total_beats):
        sequence.append(i * seconds_per_beat)
    
    return sequence
