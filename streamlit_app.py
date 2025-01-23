import streamlit as st
import time
import random
from streamlit.components.v1 import html
from collections import deque

# Initialize session state for practice status if it doesn't exist
if 'is_practicing' not in st.session_state:
    st.session_state.is_practicing = False
if 'chord_sequence' not in st.session_state:
    st.session_state.chord_sequence = deque(maxlen=4)  # Current + 3 upcoming

# Define the possible notes and chord types
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

# Set page title and description
st.title('Chord Practice Tool')

def generate_chord_sequence(num_chords):
    """Generate a sequence of chords and their corresponding MIDI notes"""
    sequence = []
    display_sequence = []
    seconds_per_beat = 60.0 / st.session_state.bpm
    beats_per_measure = st.session_state.time_signature
    seconds_per_measure = seconds_per_beat * beats_per_measure
    
    # Generate the sequence
    for i in range(num_chords):
        # Generate random note and chord type
        note = random.choice(st.session_state.selected_notes)
        chord_type = random.choice(st.session_state.selected_chord_types)
        
        # Create display version (e.g., "C-7")
        display_chord = f"{note}{CHORD_TYPES[chord_type]}"
        display_sequence.append(display_chord)
        
        # Create MIDI version (e.g., "C4")
        # Convert note to MIDI format (adding "4" for middle octave)
        midi_note = f"{note}4"
        sequence.append({
            'note': midi_note,
            'time': i * seconds_per_measure,
            'duration': seconds_per_measure * 0.95
        })
    
    return sequence, display_sequence

def play_sequence(sequence):
    """Play the MIDI sequence"""
    js_code = f"""
        <script src="https://cdn.jsdelivr.net/npm/soundfont-player@0.12.0/dist/soundfont-player.min.js"></script>
        <script>
        (async function() {{
            try {{
                // Initialize audio if needed
                if (!window.player) {{
                    window.audioContext = new (window.AudioContext || window.webkitAudioContext)();
                    window.player = await Soundfont.instrument(window.audioContext, 'acoustic_grand_piano');
                }}
                
                // Play the sequence
                const sequence = {sequence};
                const now = window.audioContext.currentTime;
                sequence.forEach(note => {{
                    window.player.play(note.note, now + note.time, {{duration: note.duration}});
                }});
            }} catch (error) {{
                console.error('Error:', error);
            }}
        }})();
        </script>
    """
    html(js_code, height=0)

def display_chord_sequence(display_sequence):
    """Display the chord sequence with a rolling window"""
    # Initialize the display window with first 4 chords (or pad with spaces if fewer)
    window = deque(display_sequence[:4] + [''] * (4 - len(display_sequence)), maxlen=4)
    st.session_state.chord_sequence = window
    
    # Create placeholder for chord display
    chord_display = st.empty()
    
    # Display and update chords
    for i in range(len(display_sequence)):
        # Update display
        display_html = f"""
        <div style='display: flex; align-items: center; justify-content: center; gap: 20px; margin: 20px;'>
            <span style='font-size: 72px;'>{window[0]}</span>
            <span style='font-size: 36px; color: #666;'>|</span>
            <span style='font-size: 36px;'>{window[1]}</span>
            <span style='font-size: 36px; color: #666;'>|</span>
            <span style='font-size: 36px;'>{window[2]}</span>
            <span style='font-size: 36px; color: #666;'>|</span>
            <span style='font-size: 36px;'>{window[3]}</span>
        </div>
        """
        chord_display.markdown(display_html, unsafe_allow_html=True)
        
        # Wait for next measure
        time.sleep(st.session_state.time_signature * 60.0 / st.session_state.bpm)
        
        # Rotate window and add next chord if available
        if i + 4 < len(display_sequence):
            window.append(display_sequence[i + 4])
        else:
            window.append('')

# Sidebar controls
with st.sidebar:
    st.header('Settings')
    
    # Note selection
    st.subheader('Select Root Notes')
    selected_notes = []
    for note in NOTES:
        if st.checkbox(note, value=True):
            selected_notes.append(note)
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
        if st.checkbox(description, value=False):
            selected_chord_types.append(chord_type)
    st.session_state.selected_chord_types = selected_chord_types
    
    # Time signature and tempo controls
    st.subheader('Rhythm Settings')
    time_signature = st.selectbox('Beats per measure', TIME_SIGNATURES, index=2, key="time_signature")  # Default to 4/4
    bpm = st.slider('Tempo (BPM)', min_value=30, max_value=200, value=120, key="bpm")
    num_chords = st.slider('Number of Chords', min_value=1, max_value=16, value=4, key="num_chords")
    
    # Add test sound button at bottom of sidebar
    st.markdown("---")
    html("""
        <script>
        async function testSound() {
            try {
                if (!window.player) {
                    window.audioContext = new (window.AudioContext || window.webkitAudioContext)();
                    window.player = await Soundfont.instrument(window.audioContext, 'acoustic_grand_piano');
                }
                window.player.play('C4', 0, {duration: 1});
            } catch (error) {
                console.error('Error playing test sound:', error);
            }
        }
        </script>
        <button onclick="testSound()" style="font-size: 0.8em;">Test Sound</button>
    """, height=50)

# Create the start/stop button at the top
if st.button('Start Practice' if not st.session_state.is_practicing else 'Stop Practice'):
    st.session_state.is_practicing = not st.session_state.is_practicing
    if st.session_state.is_practicing:
        # Generate the complete sequence first
        midi_sequence, display_sequence = generate_chord_sequence(st.session_state.num_chords)
        
        # Start both the sequence playback and chord display
        play_sequence(midi_sequence)  # Non-blocking
        display_chord_sequence(display_sequence)  # Blocking
