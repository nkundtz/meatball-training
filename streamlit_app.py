import streamlit as st
import streamlit.components.v1 as components
from collections import deque
import random
import os
import json

# Initialize session state
if 'is_practicing' not in st.session_state:
    st.session_state.is_practicing = False
if 'chord_sequence' not in st.session_state:
    st.session_state.chord_sequence = deque(maxlen=4)
if 'selected_notes' not in st.session_state:
    st.session_state.selected_notes = ['A', 'Bb', 'B', 'C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab'].copy()
if 'selected_chord_types' not in st.session_state:
    st.session_state.selected_chord_types = ['Major', 'Minor']
if 'volume' not in st.session_state:
    st.session_state.volume = 1.0
if 'progression_type' not in st.session_state:
    st.session_state.progression_type = "Random"

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

def get_chord_qualities():
    """Return a dictionary mapping chord quality names to their symbols."""
    return {
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

CHORD_TYPES = get_chord_qualities()
TIME_SIGNATURES = [2, 3, 4, 5, 6]

def get_scale_degrees(root_note):
    """Get the scale degrees for a major scale starting from the given root note"""
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

def generate_two_five_one(root_note):
    """Generate a II-V-I progression in the key of the given root note, with I lasting two bars"""
    scale = get_scale_degrees(root_note)
    
    # II chord (minor 7)
    ii_chord = f"{scale[1]}{CHORD_TYPES['Minor 7']}"
    
    # V chord (dominant 7)
    v_chord = f"{scale[4]}{CHORD_TYPES['Dominant 7']}"
    
    # I chord (major 7) repeated for two bars
    i_chord = f"{scale[0]}{CHORD_TYPES['Major 7']}"
    
    return [ii_chord, v_chord, i_chord, i_chord]

def generate_diatonic_cycle(root_note):
    """Generate a I-IV-III-VI-II-V-I progression in the key of the given root note"""
    scale = get_scale_degrees(root_note)
    
    # I chord (major 7)
    i_chord_start = f"{scale[0]}{CHORD_TYPES['Major 7']}"
    
    # IV chord (major 7)
    iv_chord = f"{scale[3]}{CHORD_TYPES['Major 7']}"
    
    # III chord (minor 7)
    iii_chord = f"{scale[2]}{CHORD_TYPES['Minor 7']}"
    
    # VI chord (minor 7)
    vi_chord = f"{scale[5]}{CHORD_TYPES['Minor 7']}"
    
    # II chord (minor 7)
    ii_chord = f"{scale[1]}{CHORD_TYPES['Minor 7']}"
    
    # V chord (dominant 7)
    v_chord = f"{scale[4]}{CHORD_TYPES['Dominant 7']}"
    
    # I chord (major 7) to end
    i_chord_end = f"{scale[0]}{CHORD_TYPES['Major 7']}"
    
    return [i_chord_start, iv_chord, iii_chord, vi_chord, ii_chord, v_chord, i_chord_end]

def generate_chord_sequence(num_chords):
    """Generate a sequence of chords and their corresponding MIDI notes"""
    sequence = []
    display_sequence = []
    seconds_per_beat = 60.0 / st.session_state.bpm
    beats_per_measure = st.session_state.time_signature
    seconds_per_measure = seconds_per_beat * beats_per_measure
    
    if st.session_state.progression_type == "II-V-I":
        # Generate multiple II-V-I progressions
        chords_per_progression = 4  # II-V-I-I has 4 chords
        num_progressions = (num_chords + chords_per_progression - 1) // chords_per_progression
        for _ in range(num_progressions):
            root_note = random.choice(st.session_state.selected_notes)
            progression = generate_two_five_one(root_note)
            display_sequence.extend(progression)
            if len(display_sequence) >= num_chords:
                display_sequence = display_sequence[:num_chords]
                break
    elif st.session_state.progression_type == "Diatonic Cycle":
        # Generate multiple diatonic cycle progressions
        chords_per_progression = 7  # Diatonic cycle has 7 chords
        num_progressions = (num_chords + chords_per_progression - 1) // chords_per_progression
        for _ in range(num_progressions):
            root_note = random.choice(st.session_state.selected_notes)
            progression = generate_diatonic_cycle(root_note)
            display_sequence.extend(progression)
            if len(display_sequence) >= num_chords:
                display_sequence = display_sequence[:num_chords]
                break
    else:
        # Generate random chords
        for _ in range(num_chords):
            note = random.choice(st.session_state.selected_notes)
            chord_type = random.choice(list(st.session_state.selected_chord_types))
            display_chord = f"{note}{CHORD_TYPES[chord_type]}"
            display_sequence.append(display_chord)
    
    # Convert display chords to MIDI sequence
    for i, chord in enumerate(display_sequence):
        # Extract the root note from the chord symbol (first character)
        root_note = chord[0]
        if len(chord) > 1 and chord[1] in ['b', '#']:
            root_note += chord[1]
            
        # Use octave 2 for a deep double bass sound (two octaves lower than before)
        midi_note = f"{root_note}2"
        sequence.append({
            'note': midi_note,
            'time': i * seconds_per_measure,
            'duration': seconds_per_measure * 0.95,
            'instrument': 'bass'  # Use bass instrument sound
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
    
    # Get Streamlit theme
    is_dark_theme = st.get_option("theme.base") == "dark"
    theme_colors = {
        'text': '#FFFFFF' if is_dark_theme else '#000000',
        'background': '#0E1117' if is_dark_theme else '#FFFFFF',
        'border': '#31333F' if is_dark_theme else '#CCCCCC'
    }
    
    # Convert sequences to JSON
    chord_json = json.dumps(chord_sequence)
    metronome_json = json.dumps(metronome_sequence)
    display_json = json.dumps(display_sequence)
    volume = st.session_state.volume
    
    html_code = f"""
        <style>
        {css_code}
        :root {{
            --text-color: {theme_colors['text']};
            --background-color: {theme_colors['background']};
            --border-color: {theme_colors['border']};
        }}
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
            {chord_json},
            {metronome_json},
            {display_json},
            {st.session_state.time_signature},
            {st.session_state.bpm},
            {volume}
        );
        
        // Listen for mute toggle changes
        const checkbox = window.parent.document.querySelector('input[data-testid="stCheckbox"]');
        if (checkbox) {{
            checkbox.addEventListener('change', function() {{
                const volume = this.checked ? 1.0 : 0;
                window.postMessage({{
                    type: 'volume_update',
                    volume: volume
                }}, '*');
            }});
        }}
        </script>
    """
    components.html(html_code, height=200)

def get_note_display(note):
    """Get the display version of a note (showing both representations if applicable)"""
    idx = NOTES.index(note)
    flat_note = NOTES[idx]
    sharp_note = NOTES_SHARP[idx]
    if flat_note != sharp_note:
        return f"{sharp_note}/{flat_note}"
    return note

def read_file(path):
    with open(path, 'r') as f:
        return f.read()

st.title('Chord Practice Tool')

st.session_state.progression_type = st.selectbox(
    'Progression Type',
    ['Random', 'II-V-I', 'Diatonic Cycle'],
    index=0 if st.session_state.progression_type == "Random" else 
          1 if st.session_state.progression_type == "II-V-I" else 2
)

col1, col2 = st.columns(2)

with col1:
    if st.button('▶ Start Practice' if not st.session_state.is_practicing else '⏹ Stop Practice'):
        st.session_state.is_practicing = not st.session_state.is_practicing
        if not st.session_state.is_practicing:
            st.session_state.chord_sequence.clear()
        st.rerun()

if st.session_state.is_practicing:
    midi_sequence, display_sequence = generate_chord_sequence(st.session_state.num_chords)
    
    seconds_per_beat = 60.0 / st.session_state.bpm
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
    
    mute_col, label_col = st.columns([1, 3])
    with mute_col:
        is_muted = not st.checkbox("", value=not st.session_state.volume == 0, key="mute_toggle", on_change=None)
    with label_col:
        st.write("🔊 Enable Sound")
    
    st.session_state.volume = 0 if is_muted else 1.0

    st.subheader('Select Root Notes')
    selected_notes = []
    note_pairs = list(zip(NOTES, [get_note_display(note) for note in NOTES]))
    for note, display_note in note_pairs:
        if st.checkbox(display_note, value=note in st.session_state.selected_notes):
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
        if st.checkbox(description, value=chord_type in st.session_state.selected_chord_types):  
            selected_chord_types.append(chord_type)
    if not selected_chord_types:
        selected_chord_types = ['Major']  
    st.session_state.selected_chord_types = selected_chord_types
    
    st.subheader('Rhythm Settings')
    st.session_state.time_signature = st.selectbox('Beats per measure', TIME_SIGNATURES, index=2)
    st.session_state.bpm = st.slider('Tempo (BPM)', min_value=40, max_value=200, value=120, step=1)
    st.session_state.num_chords = st.slider('Number of Chords or Cycles', min_value=4, max_value=50, value=16, step=1)
    
    st.markdown("---")
    js_code = read_file(os.path.join('static', 'player.js'))
    components.html(f"""
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
