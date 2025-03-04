"""Session state management for the Streamlit app."""

from collections import deque
import streamlit as st
from ..music.theory import NOTES, CHORD_TYPES

def init_session_state() -> None:
    """Initialize all session state variables if they don't exist."""
    if 'is_practicing' not in st.session_state:
        st.session_state.is_practicing = False
        
    if 'chord_sequence' not in st.session_state:
        st.session_state.chord_sequence = deque(maxlen=4)
        
    if 'selected_notes' not in st.session_state:
        st.session_state.selected_notes = NOTES.copy()
        
    if 'selected_chord_types' not in st.session_state:
        st.session_state.selected_chord_types = ['Major', 'Minor']
        
    if 'volume' not in st.session_state:
        st.session_state.volume = 1.0
        
    if 'bass_volume' not in st.session_state:
        st.session_state.bass_volume = 0.8
        
    if 'metronome_volume' not in st.session_state:
        st.session_state.metronome_volume = 0.4
        
    if 'progression_type' not in st.session_state:
        st.session_state.progression_type = "Random"
        
    if 'time_signature' not in st.session_state:
        st.session_state.time_signature = 4
        
    if 'bpm' not in st.session_state:
        st.session_state.bpm = 120
        
    if 'num_chords' not in st.session_state:
        st.session_state.num_chords = 16
        
    if 'current_progression' not in st.session_state:
        st.session_state.current_progression = None
        
    # Initialize sequence storage
    if 'midi_sequence' not in st.session_state:
        st.session_state.midi_sequence = []
        
    if 'display_sequence' not in st.session_state:
        st.session_state.display_sequence = []
        
    if 'metronome_sequence' not in st.session_state:
        st.session_state.metronome_sequence = []
