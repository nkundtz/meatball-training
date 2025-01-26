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
        
    if 'progression_type' not in st.session_state:
        st.session_state.progression_type = "Random"
        
    if 'time_signature' not in st.session_state:
        st.session_state.time_signature = 4
        
    if 'bpm' not in st.session_state:
        st.session_state.bpm = 120
        
    if 'num_chords' not in st.session_state:
        st.session_state.num_chords = 16
