"""Functions for generating chord progressions."""

from typing import List, Tuple
from .theory import get_scale_degrees, CHORD_TYPES

def generate_two_five_one(root_note: str) -> List[str]:
    """Generate a II-V-I progression in the key of the given root note.
    
    Args:
        root_note: The root note of the key
        
    Returns:
        List of chord symbols (e.g., ["Dm7", "G7", "Cmaj7", "Cmaj7"])
    """
    scale = get_scale_degrees(root_note)
    
    # II chord (minor 7)
    ii_chord = f"{scale[1]}{CHORD_TYPES['Minor 7']}"
    
    # V chord (dominant 7)
    v_chord = f"{scale[4]}{CHORD_TYPES['Dominant 7']}"
    
    # I chord (major 7) repeated for two bars
    i_chord = f"{scale[0]}{CHORD_TYPES['Major 7']}"
    
    return [ii_chord, v_chord, i_chord, i_chord]

def generate_diatonic_cycle(root_note: str) -> List[str]:
    """Generate a I-IV-III-VI-II-V-I progression in the key of the given root note.
    
    Args:
        root_note: The root note of the key
        
    Returns:
        List of chord symbols
    """
    scale = get_scale_degrees(root_note)
    
    progression = []
    
    # I chord (major 7)
    progression.append(f"{scale[0]}{CHORD_TYPES['Major 7']}")
    
    # IV chord (major 7)
    progression.append(f"{scale[3]}{CHORD_TYPES['Major 7']}")
    
    # III chord (minor 7)
    progression.append(f"{scale[2]}{CHORD_TYPES['Minor 7']}")
    
    # VI chord (minor 7)
    progression.append(f"{scale[5]}{CHORD_TYPES['Minor 7']}")
    
    # II chord (minor 7)
    progression.append(f"{scale[1]}{CHORD_TYPES['Minor 7']}")
    
    # V chord (dominant 7)
    progression.append(f"{scale[4]}{CHORD_TYPES['Dominant 7']}")
    
    # I chord (major 7)
    progression.append(f"{scale[0]}{CHORD_TYPES['Major 7']}")
    progression.append(f"{scale[0]}{CHORD_TYPES['Major 7']}")
    
    return progression
