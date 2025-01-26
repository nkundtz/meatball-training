"""Main Streamlit application for chord practice."""

import streamlit as st
import streamlit.components.v1 as components
import json
import random
import os

from meatball.ui.session import init_session_state
from meatball.ui.components import play_sequence, create_sound_controls
from meatball.music.sequence import generate_chord_sequence, generate_metronome_sequence
from meatball.music.theory import NOTES, CHORD_TYPES, get_note_display

# Initialize session state
init_session_state()

st.set_page_config(
    page_title="Meatball Training",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Main content
st.title('Meatball Training')

# Display chord progression
if st.session_state.current_progression:
    st.write('Current progression:')
    st.write(st.session_state.current_progression)

st.session_state.progression_type = st.selectbox(
    'Progression Type',
    ['Random', 'II-V-I', 'Diatonic Cycle'],
    index=0 if st.session_state.progression_type == "Random" else 
          1 if st.session_state.progression_type == "II-V-I" else 2
)

col1, col2 = st.columns(2)

with col1:
    if st.button('▶ Start Practice' if not st.session_state.is_practicing else '⏹ Stop Practice', key='practice_button'):
        st.session_state.is_practicing = not st.session_state.is_practicing
        if not st.session_state.is_practicing:
            st.session_state.chord_sequence.clear()
        st.rerun()

if st.session_state.is_practicing:
    seconds_per_beat = 60.0 / st.session_state.bpm
    seconds_per_measure = seconds_per_beat * st.session_state.time_signature
    
    midi_sequence, display_sequence = generate_chord_sequence(
        st.session_state.num_chords,
        st.session_state.progression_type,
        st.session_state.selected_notes,
        st.session_state.selected_chord_types,
        seconds_per_measure
    )
    
    metronome_sequence = generate_metronome_sequence(
        st.session_state.num_chords,
        st.session_state.time_signature,
        seconds_per_beat
    )
    
    play_sequence(midi_sequence, metronome_sequence, display_sequence)

# Sidebar
with st.sidebar:
    st.header('Settings')
    
    st.subheader('Select Root Notes')
    selected_notes = []
    note_pairs = list(zip(NOTES, [get_note_display(note) for note in NOTES]))
    
    for i in range(0, len(note_pairs), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(note_pairs):
                note, display = note_pairs[i + j]
                if cols[j].checkbox(display, value=True, key=f'note_{note}'):
                    selected_notes.append(note)

    st.subheader('Select Chord Types')
    selected_chord_types = []
    for chord_type in CHORD_TYPES:
        if st.checkbox(chord_type, value=True, key=f'chord_{chord_type}'):
            selected_chord_types.append(chord_type)

    st.session_state.selected_notes = selected_notes
    st.session_state.selected_chord_types = selected_chord_types
    
    st.subheader('Rhythm Settings')
    st.session_state.time_signature = st.selectbox('Beats per measure', [2, 3, 4, 5, 6], index=2)
    st.session_state.bpm = st.slider('Tempo (BPM)', min_value=40, max_value=200, value=st.session_state.bpm, step=1)
    
    # Initialize num_chords if not in session state
    if 'num_chords' not in st.session_state:
        st.session_state.num_chords = 16
        
    # Use the current session state value as the slider's default
    num_chords = st.slider('Number of Chords', 
                          min_value=4, 
                          max_value=128, 
                          value=st.session_state.num_chords,
                          step=1,
                          key='num_chords_slider')
    
    # Update session state with new value
    st.session_state.num_chords = num_chords
    
    # Sound controls at the bottom
    st.markdown('---')  # Add a separator
    create_sound_controls()
    
    if 'volume' not in st.session_state:
        st.session_state.volume = 1.0
    
    is_muted = not st.checkbox("🔊 Enable Sound", value=not st.session_state.volume == 0, key="mute_toggle")
    st.session_state.volume = 0 if is_muted else 1.0
