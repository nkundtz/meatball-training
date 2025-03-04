"""Streamlit UI components."""

import os
import json
import streamlit as st
import streamlit.components.v1 as components
from typing import Dict, List, Any
from pkg_resources import resource_string

def read_file(path: str) -> str:
    """Read a file and return its contents.
    
    Args:
        path: Path to the file
        
    Returns:
        File contents as string
    """
    return resource_string('meatball', path).decode('utf-8')

def play_sequence(
    chord_sequence: List[Dict[str, Any]],
    metronome_sequence: List[Dict[str, Any]],
    display_sequence: List[str]
) -> None:
    """Create and display the audio player component.
    
    Args:
        chord_sequence: List of chord events
        metronome_sequence: List of metronome events
        display_sequence: List of chord symbols to display
    """
    # Read external files
    js_code = read_file('static/js/player.js')
    css_code = read_file('static/css/styles.css')
    
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
            {st.session_state.volume},
            {st.session_state.bass_volume},
            {st.session_state.metronome_volume}
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

def create_sound_controls() -> None:
    """Create sound control UI elements in the sidebar.
    
    Creates:
        - Bass volume slider: Controls the volume of the bass instrument
        - Metronome volume slider: Controls the volume of the metronome clicks
    """
    st.sidebar.subheader('Sound Controls')
    
    # Update session state from sliders without triggering rerun
    if 'bass_volume' in st.session_state:
        bass_vol = st.session_state.bass_volume
    else:
        bass_vol = 1.0
        st.session_state.bass_volume = bass_vol
        
    if 'metronome_volume' in st.session_state:
        metro_vol = st.session_state.metronome_volume
    else:
        metro_vol = 0.4
        st.session_state.metronome_volume = metro_vol
    
    # Use on_change callback to update values without triggering rerun
    def update_bass_volume():
        st.session_state.bass_volume = st.session_state.bass_volume_slider
        
    def update_metro_volume():
        st.session_state.metronome_volume = st.session_state.metro_volume_slider
    
    st.sidebar.slider('Bass Volume', 0.0, 5.0, value=bass_vol, key='bass_volume_slider', 
                     on_change=update_bass_volume, help='Adjust bass volume')
    st.sidebar.slider('Metronome Volume', 0.0, 1.0, value=metro_vol, key='metro_volume_slider',
                     on_change=update_metro_volume, help='Adjust metronome volume')
