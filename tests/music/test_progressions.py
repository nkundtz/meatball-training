"""Tests for chord progression generation."""

import pytest
from meatball.music.progressions import generate_two_five_one, generate_diatonic_cycle

def test_two_five_one():
    """Test II-V-I progression generation."""
    # Test in C major
    progression = generate_two_five_one('C')
    assert len(progression) == 4
    assert progression[0] == 'Dm7'  # II chord
    assert progression[1] == 'G7'   # V chord
    assert progression[2] == 'Cmaj7' # I chord
    assert progression[3] == 'Cmaj7' # I chord repeated
    
    # Test in F major
    progression = generate_two_five_one('F')
    assert len(progression) == 4
    assert progression[0] == 'Gm7'  # II chord
    assert progression[1] == 'C7'   # V chord
    assert progression[2] == 'Fmaj7' # I chord
    assert progression[3] == 'Fmaj7' # I chord repeated

def test_diatonic_cycle():
    """Test diatonic cycle progression generation."""
    # Test in C major
    progression = generate_diatonic_cycle('C')
    assert len(progression) == 8
    assert progression[0] == 'Cmaj7'  # I chord
    assert progression[1] == 'Fmaj7'  # IV chord
    assert progression[2] == 'Em7'    # III chord
    assert progression[3] == 'Am7'    # VI chord
    assert progression[4] == 'Dm7'    # II chord
    assert progression[5] == 'G7'     # V chord
    assert progression[6] == 'Cmaj7'  # I chord
    assert progression[7] == 'Cmaj7'  # I chord repeated
