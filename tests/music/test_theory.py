"""Tests for music theory module."""

import pytest
from meatball.music.theory import get_scale_degrees, get_note_display, NOTES, NOTES_SHARP

def test_get_scale_degrees():
    """Test major scale generation from different roots."""
    # Test C major scale (no sharps/flats)
    assert get_scale_degrees('C') == ['C', 'D', 'E', 'F', 'G', 'A', 'B']
    
    # Test G major scale (one sharp)
    assert get_scale_degrees('G') == ['G', 'A', 'B', 'C', 'D', 'E', 'F#']
    
    # Test F major scale (one flat)
    assert get_scale_degrees('F') == ['F', 'G', 'A', 'Bb', 'C', 'D', 'E']

def test_get_note_display():
    """Test note display formatting."""
    # Test notes with both sharp and flat representations
    assert get_note_display('Gb') == 'F#/Gb'
    assert get_note_display('F#') == 'F#/Gb'
    
    # Test notes with single representation
    assert get_note_display('C') == 'C'
    assert get_note_display('F') == 'F'

def test_note_lists():
    """Test note list consistency."""
    # Test that both note lists have same length
    assert len(NOTES) == len(NOTES_SHARP)
    
    # Test that both lists have 12 notes (chromatic scale)
    assert len(NOTES) == 12
    assert len(NOTES_SHARP) == 12
