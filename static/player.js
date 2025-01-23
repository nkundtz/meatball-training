// Global variables for audio
let audioContext = null;
let player = null;

// Initialize audio context and player
async function initAudio() {
    if (!audioContext) {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
    }
    if (!player) {
        try {
            player = await Soundfont.instrument(audioContext, 'acoustic_grand_piano');
        } catch (error) {
            throw new Error('Failed to load piano sound: ' + error.message);
        }
    }
    return { audioContext, player };
}

// Test sound function
async function testSound() {
    try {
        const testButton = document.getElementById('test-sound-button');
        const originalText = testButton.textContent;
        testButton.disabled = true;
        testButton.textContent = 'Loading...';

        const { audioContext, player } = await initAudio();
        
        // Resume audio context (needed for Chrome)
        if (audioContext.state === 'suspended') {
            await audioContext.resume();
        }
        
        // Play a middle C note
        await player.play('C4', audioContext.currentTime, { duration: 1 });
        
        testButton.textContent = '✓ Sound works!';
        setTimeout(() => {
            testButton.disabled = false;
            testButton.textContent = originalText;
        }, 2000);
        
    } catch (error) {
        const testButton = document.getElementById('test-sound-button');
        testButton.textContent = '❌ ' + error.message;
        testButton.style.color = '#ff6b6b';
        console.error('Test sound error:', error);
        
        // Reset button after 3 seconds
        setTimeout(() => {
            testButton.disabled = false;
            testButton.textContent = 'Test Sound';
            testButton.style.color = '';
        }, 3000);
    }
}

async function initPlayer(chordSequence, metronomeSequence, displaySequence, timeSignature, bpm) {
    try {
        // Initialize audio and wait for it to be ready
        const { audioContext, player } = await initAudio();
        
        // Initialize display functions
        function updateBeatDisplay(currentBeat) {
            const beats = Array(timeSignature).fill('○');
            for (let i = 0; i <= currentBeat; i++) {
                beats[i] = '●';
            }
            document.getElementById('beat-display').textContent = beats.join(' ');
        }
        
        function updateChordDisplay(currentMeasure) {
            const startIdx = currentMeasure;
            document.getElementById('current-chord').textContent = displaySequence[startIdx] || '';
            document.getElementById('next-chord1').textContent = displaySequence[startIdx + 1] || '';
            document.getElementById('next-chord2').textContent = displaySequence[startIdx + 2] || '';
            document.getElementById('next-chord3').textContent = displaySequence[startIdx + 3] || '';
        }
        
        // Show initial display
        updateBeatDisplay(-1);
        updateChordDisplay(0);
        
        // Fade transition
        const loadingOverlay = document.getElementById('loading-overlay');
        const displayContent = document.getElementById('display-content');
        const countdown = document.getElementById('countdown');
        
        loadingOverlay.style.opacity = '0';
        displayContent.style.opacity = '1';
        
        // Wait for fade
        await new Promise(resolve => setTimeout(resolve, 300));
        loadingOverlay.style.display = 'none';
        
        // Countdown
        for (let i = 4; i > 0; i--) {
            countdown.textContent = i;
            await new Promise(resolve => setTimeout(resolve, 1000));
        }
        countdown.style.display = 'none';
        
        const secondsPerBeat = 60.0 / bpm;
        const startTime = audioContext.currentTime + 0.1;
        
        // Schedule all audio
        chordSequence.forEach(note => {
            player.play(note.note, startTime + note.time, {duration: note.duration});
        });
        
        metronomeSequence.forEach(note => {
            player.play(note.note, startTime + note.time, {duration: note.duration, gain: note.gain});
        });
        
        // Animation frame handler
        let currentMeasure = 0;
        let currentBeat = -1;
        const totalMeasures = displaySequence.length;
        
        function animate(timestamp) {
            const elapsedTime = audioContext.currentTime - startTime;
            const totalBeats = Math.floor(elapsedTime / secondsPerBeat);
            const newMeasure = Math.floor(totalBeats / timeSignature);
            const newBeat = totalBeats % timeSignature;
            
            // Update if beat or measure changed
            if (newBeat !== currentBeat) {
                currentBeat = newBeat;
                updateBeatDisplay(currentBeat);
            }
            
            if (newMeasure !== currentMeasure) {
                currentMeasure = newMeasure;
                if (currentMeasure < totalMeasures) {
                    updateChordDisplay(currentMeasure);
                }
            }
            
            // Continue animation if not finished
            if (currentMeasure < totalMeasures) {
                requestAnimationFrame(animate);
            } else {
                // Reset button state when sequence finishes
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    data: false
                }, '*');
                window.parent.postMessage({
                    type: 'streamlit:rerun'
                }, '*');
                
                // Reset displays
                updateBeatDisplay(-1);
                updateChordDisplay(0);
            }
        }
        
        // Start animation
        requestAnimationFrame(animate);
        
    } catch (error) {
        console.error('Error:', error);
        const loadingText = document.querySelector('.loading-text');
        if (loadingText) {
            loadingText.textContent = 'Error loading sounds: ' + error.message;
            loadingText.style.color = '#ff6b6b';
        }
    }
}
