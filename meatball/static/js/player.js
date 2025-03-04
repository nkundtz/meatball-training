// Global variables for audio
let audioContext = null;
let snarePlayer = null;
let bassPlayer = null;
let masterGain = null;
let isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;

// Listen for mute updates
window.addEventListener('message', function(event) {
    if (event.data.type === 'volume_update' && masterGain) {
        masterGain.gain.setValueAtTime(event.data.volume, audioContext.currentTime);
    }
});

// Create audio context
async function createAudioContext() {
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    const ctx = new AudioContext({ sampleRate: 44100 });
    const gain = ctx.createGain();
    gain.connect(ctx.destination);
    
    if (ctx.state === 'suspended') {
        await ctx.resume();
    }
    
    return { ctx, gain };
}

// Initialize audio context and players
async function initAudio() {
    try {
        if (!audioContext) {
            const { ctx, gain } = await createAudioContext();
            audioContext = ctx;
            masterGain = gain;
        }
        
        if (snarePlayer && bassPlayer) {
            return { audioContext, snarePlayer, bassPlayer };
        }
        
        // Initialize soundfont
        const soundfontOptions = {
            destination: masterGain,
            format: isIOS ? 'mp3' : 'ogg',
            soundfont: 'FluidR3_GM',
            nameToUrl: (name, soundfont, format) => {
                return `https://gleitz.github.io/midi-js-soundfonts/${soundfont}/${name}-${format}.js`;
            }
        };
        
        // Load both instruments in parallel
        const [snare, bass] = await Promise.all([
            Soundfont.instrument(audioContext, 'synth_drum', soundfontOptions),
            Soundfont.instrument(audioContext, 'acoustic_bass', soundfontOptions)
        ]);
        
        snarePlayer = snare;
        bassPlayer = bass;
        
        return { audioContext, snarePlayer, bassPlayer };
    } catch (error) {
        console.error('Error initializing audio:', error);
        throw error;
    }
}

// Schedule a note to play at a specific time
async function scheduleNote(noteName, time, duration, baseGain = 1, instrument = 'snare') {
    const player = instrument === 'snare' ? snarePlayer : bassPlayer;
    if (player) {
        try {
            if (audioContext.state === 'suspended') {
                await audioContext.resume();
            }
            await player.play(noteName, time, {
                duration: duration,
                gain: baseGain
            });
        } catch (error) {
            console.error('Error playing note:', error);
        }
    }
}

// Initialize player with sequence data
async function initPlayer(chordSequence, metronomeSequence, displaySequence, timeSignature, bpm, masterVolume, bassVolume, metronomeVolume) {
    try {
        // Get current BPM from slider
        const bpmSlider = window.parent.document.querySelector('div[data-testid="stSlider"] input');
        if (bpmSlider) {
            bpm = parseInt(bpmSlider.value);
        }
        
        const loadingOverlay = document.getElementById('loading-overlay');
        const loadingText = document.querySelector('.loading-text');
        const displayContent = document.getElementById('display-content');
        const countdown = document.getElementById('countdown');
        
        // For iOS, we need user interaction before playing audio
        if (isIOS) {
            loadingText.textContent = 'Tap here to start...';
            loadingText.style.cursor = 'pointer';
            
            // Wait for user interaction before creating audio context
            await new Promise(resolve => {
                const startAudio = async () => {
                    try {
                        loadingText.textContent = 'Starting audio...';
                        await initAudio();
                        resolve();
                    } catch (error) {
                        console.error('Error starting audio:', error);
                        loadingText.textContent = 'Error starting audio. Please try again.';
                        loadingText.style.color = '#ff6b6b';
                    }
                };
                
                // Add both touch and click handlers
                const handleInteraction = (event) => {
                    event.preventDefault();
                    startAudio();
                };
                
                loadingText.addEventListener('touchend', handleInteraction, { once: true });
                loadingText.addEventListener('click', handleInteraction, { once: true });
            });
        }
        
        // Initialize audio after user interaction
        loadingText.textContent = 'Loading sounds...';
        await initAudio();
        
        // Set initial volume
        if (masterGain) {
            masterGain.gain.setValueAtTime(masterVolume, audioContext.currentTime);
        }
        
        // Clear previously scheduled notes
        const scheduledNotes = [];
        
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
        
        // Hide loading overlay
        loadingOverlay.style.opacity = '0';
        displayContent.style.opacity = '1';
        await new Promise(resolve => setTimeout(resolve, 300));
        loadingOverlay.style.display = 'none';
        
        // Calculate timing
        const secondsPerBeat = 60.0 / bpm;
        const secondsPerMeasure = secondsPerBeat * timeSignature;
        const totalMeasures = displaySequence.length;
        const totalDuration = totalMeasures * secondsPerMeasure;
        
        // For iOS, ensure we're still running
        if (isIOS) {
            await audioContext.resume();
        }
        
        // Schedule all notes starting one measure in the future
        const startTime = audioContext.currentTime + secondsPerMeasure;
        
        // Do countdown
        countdown.style.display = 'block';
        for (let i = timeSignature; i > 0; i--) {
            const countdownTime = startTime - (i * secondsPerBeat);
            countdown.textContent = i;
            scheduleNote('C3', countdownTime, 0.1, metronomeVolume, 'snare');
            await new Promise(resolve => setTimeout(resolve, secondsPerBeat * 1000));
        }
        countdown.style.display = 'none';
        
        // Schedule chord sequence
        for (const chord of chordSequence) {
            scheduledNotes.push(
                scheduleNote(
                    chord.note,
                    startTime + chord.time,
                    chord.duration,
                    bassVolume,
                    'bass'
                )
            );
        }
        
        // Schedule metronome sequence
        for (const time of metronomeSequence) {
            const isDownbeat = (Math.floor(time / secondsPerMeasure) * secondsPerMeasure) === time;
            scheduledNotes.push(
                scheduleNote(
                    'C3',
                    startTime + time,
                    0.1,
                    isDownbeat ? metronomeVolume : metronomeVolume * 0.5,
                    'snare'
                )
            );
        }
        
        // For iOS, we need a more precise timing mechanism
        let lastUpdateTime = performance.now();
        const frameInterval = 1000 / 60; // 60fps
        
        function updateDisplay(timestamp) {
            // Throttle updates on iOS
            if (isIOS) {
                const elapsed = timestamp - lastUpdateTime;
                if (elapsed < frameInterval) {
                    requestAnimationFrame(updateDisplay);
                    return;
                }
                lastUpdateTime = timestamp;
                
                // Keep audio context running
                if (audioContext.state === 'suspended') {
                    audioContext.resume();
                }
            }
            
            const elapsedTime = audioContext.currentTime - startTime;
            const currentBeat = Math.floor(elapsedTime / secondsPerBeat) % timeSignature;
            const currentMeasure = Math.floor(elapsedTime / secondsPerMeasure);
            
            updateBeatDisplay(currentBeat);
            updateChordDisplay(currentMeasure);
            
            // Continue animation until all measures are complete
            if (elapsedTime < totalDuration) {
                requestAnimationFrame(updateDisplay);
            } else {
                // Clear all scheduled notes
                scheduledNotes.forEach(note => {
                    if (note.timeout) {
                        clearTimeout(note.timeout);
                    }
                });
                scheduledNotes.length = 0;
                
                // Reset display
                updateBeatDisplay(-1);
                updateChordDisplay(0);
            }
        }
        
        requestAnimationFrame(updateDisplay);
        
    } catch (error) {
        console.error('Error initializing player:', error);
        const loadingText = document.querySelector('.loading-text');
        loadingText.textContent = 'Error: ' + error.message;
        loadingText.style.color = '#ff6b6b';
    }
}

// Play a note immediately
async function playNote(noteName, duration, baseGain = 1, instrument = 'snare') {
    const player = instrument === 'snare' ? snarePlayer : bassPlayer;
    if (player) {
        try {
            if (audioContext.state === 'suspended') {
                await audioContext.resume();
            }
            await player.play(noteName, 0, {
                duration: duration,
                gain: baseGain
            });
        } catch (error) {
            console.error('Error playing note:', error);
        }
    }
}
