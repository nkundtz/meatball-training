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

// Initialize audio context and players
async function initAudio() {
    // For iOS, we need to create the audio context on user interaction
    if (!audioContext) {
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        audioContext = new AudioContext();
        masterGain = audioContext.createGain();
        masterGain.connect(audioContext.destination);
        
        // On iOS, we need to resume the audio context
        if (isIOS && audioContext.state === 'suspended') {
            await audioContext.resume();
        }
    }
    
    if (!snarePlayer) {
        try {
            snarePlayer = await Soundfont.instrument(audioContext, 'synth_drum', {
                destination: masterGain
            });
        } catch (error) {
            throw new Error('Failed to load snare sound: ' + error.message);
        }
    }
    if (!bassPlayer) {
        try {
            bassPlayer = await Soundfont.instrument(audioContext, 'acoustic_bass', {
                destination: masterGain
            });
        } catch (error) {
            throw new Error('Failed to load bass sound: ' + error.message);
        }
    }
    return { audioContext, snarePlayer, bassPlayer };
}

// Schedule a note to play
function scheduleNote(noteName, time, duration, baseGain = 1, instrument = 'snare') {
    // For iOS, we need to schedule relative to current time
    const scheduleTime = isIOS ? audioContext.currentTime + time : time;
    
    const note = {
        noteName,
        time: scheduleTime,
        duration,
        baseGain,
        timeout: setTimeout(() => {
            const player = instrument === 'snare' ? snarePlayer : bassPlayer;
            if (player) {
                // On iOS, we need to resume the context before playing
                if (isIOS && audioContext.state === 'suspended') {
                    audioContext.resume().then(() => {
                        player.play(noteName, scheduleTime, {
                            duration: duration,
                            gain: baseGain
                        });
                    });
                } else {
                    player.play(noteName, scheduleTime, {
                        duration: duration,
                        gain: baseGain
                    });
                }
            }
        }, Math.max(0, (scheduleTime - audioContext.currentTime) * 1000))
    };
    return note;
}

async function initPlayer(chordSequence, metronomeSequence, displaySequence, timeSignature, bpm, currentVolume) {
    try {
        // Initialize audio and wait for it to be ready
        const { audioContext, snarePlayer, bassPlayer } = await initAudio();
        
        // Set initial volume
        if (masterGain) {
            masterGain.gain.setValueAtTime(currentVolume, audioContext.currentTime);
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
        
        // Fade transition
        const loadingOverlay = document.getElementById('loading-overlay');
        const displayContent = document.getElementById('display-content');
        const countdown = document.getElementById('countdown');
        
        loadingOverlay.style.opacity = '0';
        displayContent.style.opacity = '1';
        
        // Wait for fade
        await new Promise(resolve => setTimeout(resolve, 300));
        loadingOverlay.style.display = 'none';
        
        // On iOS, we need user interaction to start audio
        if (isIOS) {
            countdown.textContent = "Tap to start";
            countdown.style.cursor = "pointer";
            await new Promise(resolve => {
                countdown.addEventListener('click', resolve, { once: true });
            });
        }
        
        // Countdown
        for (let i = 4; i > 0; i--) {
            countdown.textContent = i;
            scheduleNote('C3', audioContext.currentTime, 0.1, 0.3, 'snare');
            await new Promise(resolve => setTimeout(resolve, 1000));
        }
        countdown.style.display = 'none';
        
        // Calculate total measures needed
        const totalMeasures = displaySequence.length;
        const secondsPerBeat = 60.0 / bpm;
        const secondsPerMeasure = secondsPerBeat * timeSignature;
        const totalDuration = totalMeasures * secondsPerMeasure;
        
        // Schedule all notes
        const startTime = audioContext.currentTime + 0.1;
        let currentTime = startTime;
        let currentBeat = -1;
        let currentMeasure = 0;
        
        // Schedule chord sequence
        for (const chord of chordSequence) {
            scheduledNotes.push(
                scheduleNote(
                    chord.note,
                    currentTime + chord.time,
                    chord.duration,
                    0.8,
                    'bass'
                )
            );
        }
        
        // Schedule metronome sequence
        // Generate enough metronome clicks for all measures
        for (let time = 0; time < totalDuration; time += secondsPerBeat) {
            const isDownbeat = (Math.floor(time / secondsPerMeasure) * secondsPerMeasure) === time;
            scheduledNotes.push(
                scheduleNote(
                    'C3',
                    currentTime + time,
                    0.1,
                    isDownbeat ? 0.4 : 0.2,
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
            }
            
            const elapsedTime = audioContext.currentTime - startTime;
            const newBeat = Math.floor(elapsedTime / secondsPerBeat) % timeSignature;
            const newMeasure = Math.floor(elapsedTime / secondsPerMeasure);
            
            if (newBeat !== currentBeat) {
                currentBeat = newBeat;
                updateBeatDisplay(currentBeat);
            }
            
            if (newMeasure !== currentMeasure) {
                currentMeasure = newMeasure;
                updateChordDisplay(currentMeasure);
            }
            
            // Continue animation until all measures are complete
            if (elapsedTime < totalDuration) {
                requestAnimationFrame(updateDisplay);
            }
        }
        
        requestAnimationFrame(updateDisplay);
        
    } catch (error) {
        console.error('Error initializing player:', error);
        throw error;
    }
}

async function testSound() {
    try {
        const { audioContext, bassPlayer } = await initAudio();
        // For iOS, we need to resume the context before playing
        if (isIOS && audioContext.state === 'suspended') {
            await audioContext.resume();
        }
        if (bassPlayer) {
            bassPlayer.play('C2', audioContext.currentTime, { duration: 0.5, gain: 0.5 });
        }
    } catch (error) {
        console.error('Error testing sound:', error);
    }
}
