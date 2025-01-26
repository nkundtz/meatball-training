"""Main Streamlit application for chord practice."""

import streamlit as st
import streamlit.components.v1 as components
import os

from meatball.ui.session import init_session_state
from meatball.ui.components import play_sequence
from meatball.music.sequence import generate_chord_sequence, generate_metronome_sequence
from meatball.music.theory import NOTES, CHORD_TYPES, get_note_display

# Initialize session state
init_session_state()

st.title('Chord Practice Tool')

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

with st.sidebar:
    st.header('Settings')
    
    if 'volume' not in st.session_state:
        st.session_state.volume = 1.0
    
    is_muted = not st.checkbox("🔊 Enable Sound", value=not st.session_state.volume == 0, key="mute_toggle")
    st.session_state.volume = 0 if is_muted else 1.0

    st.subheader('Select Root Notes')
    selected_notes = []
    note_pairs = list(zip(NOTES, [get_note_display(note) for note in NOTES]))
    for note, display_note in note_pairs:
        if st.checkbox(display_note, value=note in st.session_state.selected_notes, key=f"note_{note}"):
            selected_notes.append(note)
    # Ensure at least one note is selected
    if not selected_notes:
        selected_notes = ['C']
    st.session_state.selected_notes = selected_notes
    
    st.subheader('Select Chord Types')
    chord_descriptions = {
        'Major': 'Major',
        'Minor': 'Minor',
        'Major 7': 'Major 7',
        'Minor 7': 'Minor 7',
        'Dominant 7': 'Dominant 7',
        'Minor 7 flat 5': 'Minor 7 flat 5',
        'Diminished': 'Diminished',
        'Augmented': 'Augmented',
        'Sus4': 'Suspended 4th',
        'Sus2': 'Suspended 2nd'
    }
    selected_chord_types = []
    for chord_type, description in chord_descriptions.items():
        if st.checkbox(description, value=chord_type in st.session_state.selected_chord_types, key=f"chord_{chord_type}"):  
            selected_chord_types.append(chord_type)
    if not selected_chord_types:
        selected_chord_types = ['Major']  
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
