"""Music theory utilities for chord and scale generation."""

from typing import List, Tuple, Dict

# Constants
NOTE_PAIRS = [
    ('A', 'A'),
    ('Bb', 'A#'),
    ('B', 'B'),
    ('C', 'C'),
    ('Db', 'C#'),
    ('D', 'D'),
    ('Eb', 'D#'),
    ('E', 'E'),
    ('F', 'F'),
    ('Gb', 'F#'),
    ('G', 'G'),
    ('Ab', 'G#')
]

NOTES = [pair[0] for pair in NOTE_PAIRS]  # Flat-based notes
NOTES_SHARP = [pair[1] for pair in NOTE_PAIRS]  # Sharp-based notes
SHARP_ROOTS = {'B', 'E', 'A', 'D', 'G'}  # Root notes that should use sharp-based scales

CHORD_TYPES = {
    'Major': '',  # C
    'Minor': 'm',  # Cm
    'Major 7': 'maj7',  # Cmaj7
    'Minor 7': 'm7',  # Cm7
    'Dominant 7': '7',  # C7
    'Minor 7 flat 5': 'm7b5',  # Cm7b5
    'Diminished': 'dim',  # Cdim
    'Augmented': 'aug',  # Caug
    'Sus4': 'sus4',  # Csus4
    'Sus2': 'sus2'  # Csus2
}

def get_scale_degrees(root_note: str) -> List[str]:
    """Get the scale degrees for a major scale starting from the given root note.
    
    Args:
        root_note: The root note of the scale
        
    Returns:
        List of notes in the major scale
    """
    # Choose between sharp and flat notes based on the root
    notes = NOTES_SHARP if root_note in SHARP_ROOTS else NOTES
    
    # Major scale intervals in semitones from the root
    intervals = [0, 2, 4, 5, 7, 9, 11]
    note_index = notes.index(root_note)
    scale_notes = []
    
    for interval in intervals:
        scale_index = (note_index + interval) % len(notes)
        scale_notes.append(notes[scale_index])
    
    return scale_notes

def get_note_display(note: str) -> str:
    """Get the display version of a note (showing both representations if applicable).
    
    Args:
        note: The note to get display version for
        
    Returns:
        Display version of the note (e.g., "F#/Gb")
    """
    # Try to find the note in both lists
    try:
        idx = NOTES.index(note)
    except ValueError:
        try:
            idx = NOTES_SHARP.index(note)
        except ValueError:
            return note  # If not found in either list, return as is
    
    flat_note = NOTES[idx]
    sharp_note = NOTES_SHARP[idx]
    if flat_note != sharp_note:
        return f"{sharp_note}/{flat_note}"
    return note
