import streamlit as st
import random
from streamlit.components.v1 import html
from collections import deque
import os

# Initialize session state
if 'is_practicing' not in st.session_state:
    st.session_state.is_practicing = False
if 'chord_sequence' not in st.session_state:
    st.session_state.chord_sequence = deque(maxlen=4)
if 'selected_notes' not in st.session_state:
    st.session_state.selected_notes = ['A', 'Bb', 'B', 'C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab'].copy()
if 'selected_chord_types' not in st.session_state:
    st.session_state.selected_chord_types = ['Major', 'Minor']

# Constants
NOTES = ['A', 'Bb', 'B', 'C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab']
CHORD_TYPES = {
    'Major': '',  # C
    'Minor': '-',  # C-
    'Major 7': 'maj7',  # CΔ
    'Minor 7': '-7',  # C-7
    'Dominant 7': 'Δ7',  # C7
    'Minor 7 flat 5': '-7b5',  # C-7b5
    'Diminished': 'o',  # Co
    'Augmented': '+',  # C+
    'Sus4': 'sus4',  # Csus4
    'Sus2': 'sus2'  # Csus2
}
TIME_SIGNATURES = [2, 3, 4, 5, 6]

def read_file(path):
    with open(path, 'r') as f:
        return f.read()

def generate_chord_sequence(num_chords):
    """Generate a sequence of chords and their corresponding MIDI notes"""
    sequence = []
    display_sequence = []
    seconds_per_beat = 60.0 / st.session_state.bpm
    beats_per_measure = st.session_state.time_signature
    seconds_per_measure = seconds_per_beat * beats_per_measure
    
    for i in range(num_chords):
        note = random.choice(st.session_state.selected_notes)
        chord_type = random.choice(st.session_state.selected_chord_types)
        
        display_chord = f"{note}{CHORD_TYPES[chord_type]}"
        display_sequence.append(display_chord)
        
        midi_note = f"{note}4"
        sequence.append({
            'note': midi_note,
            'time': i * seconds_per_measure,
            'duration': seconds_per_measure * 0.95
        })
    
    return sequence, display_sequence

def generate_metronome_sequence(num_measures, beats_per_measure, seconds_per_beat):
    """Generate metronome clicks for each beat"""
    sequence = []
    total_beats = num_measures * beats_per_measure
    
    for i in range(total_beats):
        sequence.append({
            'note': 'G5' if i % beats_per_measure == 0 else 'E5',
            'time': i * seconds_per_beat,
            'duration': 0.1,
            'gain': 0.3
        })
    
    return sequence

def play_sequence(chord_sequence, metronome_sequence, display_sequence):
    """Play both chord and metronome sequences and handle visual updates"""
    # Read external files
    js_code = read_file(os.path.join('static', 'player.js'))
    css_code = read_file(os.path.join('static', 'styles.css'))
    
    html_code = f"""
        <style>
        {css_code}
        </style>
        
        <div class="app-container">
            <div id="loading-overlay">
                <div class="loading-text">Loading piano sounds...</div>
            </div>
            <div id="countdown"></div>
            <div id="display-content">
                <div id="beat-display"></div>
                <div id="chord-display">
                    <span id="current-chord" class="chord current-chord"></span>
                    <span class="separator">|</span>
                    <span id="next-chord1" class="chord next-chord"></span>
                    <span class="separator">|</span>
                    <span id="next-chord2" class="chord next-chord"></span>
                    <span class="separator">|</span>
                    <span id="next-chord3" class="chord next-chord"></span>
                </div>
            </div>
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/soundfont-player@0.12.0/dist/soundfont-player.min.js"></script>
        <script>
        {js_code}
        
        // Initialize player with sequences
        initPlayer(
            {chord_sequence},
            {metronome_sequence},
            {display_sequence},
            {st.session_state.time_signature},
            {st.session_state.bpm}
        );
        </script>
    """
    html(html_code, height=200)

st.title('Chord Practice Tool')

# Create the start/stop button at the top
if st.button('▶ Start Practice' if not st.session_state.is_practicing else '⏹ Stop Practice'):
    st.session_state.is_practicing = not st.session_state.is_practicing
    if not st.session_state.is_practicing:
        # Clear any existing sequences
        st.session_state.chord_sequence.clear()
    st.rerun()

# Display sequence if practicing
if st.session_state.is_practicing:
    # Generate the complete sequence first
    midi_sequence, display_sequence = generate_chord_sequence(st.session_state.num_chords)
    
    # Generate metronome sequence
    seconds_per_beat = 60.0 / st.session_state.bpm
    metronome_sequence = generate_metronome_sequence(
        st.session_state.num_chords,
        st.session_state.time_signature,
        seconds_per_beat
    )
    
    # Start both the sequence playback and chord display
    play_sequence(midi_sequence, metronome_sequence, display_sequence)

# Sidebar controls
with st.sidebar:
    st.header('Settings')
    
    # Note selection
    st.subheader('Select Root Notes')
    selected_notes = []
    for note in NOTES:
        if st.checkbox(note, value=note in st.session_state.selected_notes):
            selected_notes.append(note)
    # Ensure at least one note is selected
    if not selected_notes:
        selected_notes = ['C']  # Default to C if nothing selected
    st.session_state.selected_notes = selected_notes
    
    # Chord type selection
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
        if st.checkbox(description, value=chord_type in st.session_state.selected_chord_types):  
            selected_chord_types.append(chord_type)
    # Ensure at least one chord type is selected
    if not selected_chord_types:
        selected_chord_types = ['Major']  # Default to Major if nothing selected
    st.session_state.selected_chord_types = selected_chord_types
    
    # Time signature and tempo controls
    st.subheader('Rhythm Settings')
    st.session_state.time_signature = st.selectbox('Beats per measure', TIME_SIGNATURES, index=2)
    st.session_state.bpm = st.slider('Tempo (BPM)', min_value=30, max_value=200, value=120)
    st.session_state.num_chords = st.slider('Number of Chords', min_value=1, max_value=16, value=4)
    
    # Add test sound button at bottom of sidebar
    st.markdown("---")
    js_code = read_file(os.path.join('static', 'player.js'))
    html(f"""
        <script src="https://cdn.jsdelivr.net/npm/soundfont-player@0.12.0/dist/soundfont-player.min.js"></script>
        <script>{js_code}</script>
        <button id="test-sound-button" onclick="testSound()" style="
            font-size: 0.8em;
            padding: 0.5em 1em;
            border-radius: 0.3em;
            border: 1px solid #ccc;
            background: #fff;
            cursor: pointer;
            transition: all 0.2s;
        ">Test Sound</button>
    """, height=50)
