"""Tests for sequence generation."""

import pytest
from meatball.music.sequence import generate_chord_sequence, generate_metronome_sequence

def test_random_chord_sequence():
    """Test random chord sequence generation."""
    num_chords = 8
    progression_type = "Random"
    selected_notes = ['C', 'F', 'G']
    selected_chord_types = ['Major', 'Minor']
    seconds_per_measure = 2.0
    
    midi_sequence, display_sequence = generate_chord_sequence(
        num_chords,
        progression_type,
        selected_notes,
        selected_chord_types,
        seconds_per_measure
    )
    
    # Check sequence lengths
    assert len(midi_sequence) == num_chords
    assert len(display_sequence) == num_chords
    
    # Check MIDI sequence properties
    for i, event in enumerate(midi_sequence):
        assert 'note' in event
        assert 'time' in event
        assert 'duration' in event
        assert event['time'] == i * seconds_per_measure
        assert event['duration'] == seconds_per_measure * 0.95
        
    # Check display sequence format
    for chord in display_sequence:
        root = chord[0]
        assert root in selected_notes
        assert any(chord.endswith(suffix) for suffix in ['', 'm'])

def test_metronome_sequence():
    """Test metronome sequence generation."""
    num_measures = 4
    beats_per_measure = 4
    seconds_per_beat = 0.5
    
    sequence = generate_metronome_sequence(
        num_measures,
        beats_per_measure,
        seconds_per_beat
    )
    
    total_beats = num_measures * beats_per_measure
    assert len(sequence) == total_beats
    
    for i, event in enumerate(sequence):
        # Check timing
        assert event['time'] == i * seconds_per_beat
        
        # Check accent pattern (first beat of measure should be accented)
        if i % beats_per_measure == 0:
            assert event['note'] == 'G5'  # Accented beat
        else:
            assert event['note'] == 'E5'  # Normal beat
