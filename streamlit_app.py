import streamlit as st
import time
import random
from streamlit.components.v1 import html

# Initialize session state for practice status if it doesn't exist
if 'is_practicing' not in st.session_state:
    st.session_state.is_practicing = False

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

# Create the start/stop button at the top
if st.button('Start Practice' if not st.session_state.is_practicing else 'Stop Practice'):
    st.session_state.is_practicing = not st.session_state.is_practicing

st.write('Select the chords and tempo for your practice session')

# Sidebar controls
with st.sidebar:
    st.header('Settings')
    
    # Note selection
    st.subheader('Select Root Notes')
    selected_notes = []
    for note in NOTES:
        if st.checkbox(note, value=True):
            selected_notes.append(note)
    
    # Chord type selection
    st.subheader('Select Chord Types')
    # Add descriptions to make it clear what each symbol means
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
    
    # Time signature and tempo controls
    st.subheader('Rhythm Settings')
    time_signature = st.selectbox('Beats per measure', TIME_SIGNATURES, index=2)  # Default to 4/4
    bpm = st.slider('Tempo (BPM)', min_value=30, max_value=200, value=120)

def create_beat_display(num_beats, current_beat):
    # Create a simpler visual representation using Unicode characters
    beats = []
    for i in range(num_beats):
        if i < current_beat:
            beats.append("●")  # Filled circle
        else:
            beats.append("○")  # Empty circle
    return " ".join(beats)

# Main practice area
if st.session_state.is_practicing and selected_notes and selected_chord_types:
    # Create placeholders for display elements
    current_chord_placeholder = st.empty()
    beat_display_placeholder = st.empty()
    
    def generate_chord():
        note = random.choice(selected_notes)
        chord_type = random.choice(selected_chord_types)
        return f"{note}{CHORD_TYPES[chord_type]}"
    
    # Calculate time per beat in seconds
    seconds_per_beat = 60.0 / bpm
    
    # Main practice loop
    try:
        # Generate initial set of chords
        current_chord = generate_chord()
        next_chords = [generate_chord() for _ in range(3)]  # Generate 3 upcoming chords
        beat_count = 0
        
        while st.session_state.is_practicing:
            # Update current beat display
            beat_display = create_beat_display(time_signature, (beat_count % time_signature) + 1)
            beat_display_placeholder.markdown(
                f"<h2 style='text-align: center; font-size: 36px;'>{beat_display}</h2>",
                unsafe_allow_html=True
            )
            
            # Display current chord and upcoming chords in a horizontal layout
            current_chord_placeholder.markdown(
                f"""
                <div style='display: flex; align-items: center; justify-content: center; gap: 10px;'>
                    <span style='font-size: 72px;'>{current_chord}</span>
                    <span style='font-size: 24px; color: #666;'>|</span>
                    <span style='font-size: 24px;'>{next_chords[0]}</span>
                    <span style='font-size: 24px; color: #666;'>|</span>
                    <span style='font-size: 24px;'>{next_chords[1]}</span>
                    <span style='font-size: 24px; color: #666;'>|</span>
                    <span style='font-size: 24px;'>{next_chords[2]}</span>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            time.sleep(seconds_per_beat)
            beat_count += 1
            
            # Change chord when we reach the end of a measure
            if beat_count % time_signature == 0:
                current_chord = next_chords[0]
                next_chords = next_chords[1:] + [generate_chord()]
            
    except Exception as e:
        st.error(f"An error occurred: {e}")
elif st.session_state.is_practicing:
    st.warning('Please select at least one note and one chord type to begin practice.')
