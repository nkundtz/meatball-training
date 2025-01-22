import streamlit as st
import time

# List of chord types
chord_types = ['major7', '7', 'minor7', 'minor7flat5']

# Set page title
st.title('Chord Name Display')

# Create a placeholder for the chord display
placeholder = st.empty()

# Main loop to display chords
while True:
    for chord in chord_types:
        # Display the chord name in large text
        placeholder.markdown(f"<h1 style='text-align: center; font-size: 72px;'>{chord}</h1>", unsafe_allow_html=True)
        # Wait for 4 seconds
        time.sleep(4)
