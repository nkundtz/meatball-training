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

// Create and unlock iOS audio context
async function unlockAudioContext(audioContext) {
    if (audioContext.state === 'suspended') {
        const buffer = audioContext.createBuffer(1, 1, 22050);
        const source = audioContext.createBufferSource();
        source.buffer = buffer;
        source.connect(audioContext.destination);
        source.start(0);
        await audioContext.resume();
    }
}

// Initialize audio context and players
async function initAudio() {
    try {
        // For iOS, we need to create the audio context on user interaction
        if (!audioContext) {
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            audioContext = new AudioContext({ sampleRate: 44100 });
            masterGain = audioContext.createGain();
            masterGain.connect(audioContext.destination);
        }

        // On iOS, we need to unlock the audio context
        if (isIOS) {
            await unlockAudioContext(audioContext);
        }
        
        // Initialize soundfont with specific audio settings for iOS
        const soundfontOptions = {
            destination: masterGain,
            format: isIOS ? 'mp3' : 'ogg',
            soundfont: 'FluidR3_GM',
            nameToUrl: (name, soundfont, format) => {
                return `https://gleitz.github.io/midi-js-soundfonts/${soundfont}/${name}-${format}.js`;
            }
        };
        
        if (!snarePlayer) {
            snarePlayer = await Soundfont.instrument(audioContext, 'synth_drum', soundfontOptions);
        }
        if (!bassPlayer) {
            bassPlayer = await Soundfont.instrument(audioContext, 'acoustic_bass', soundfontOptions);
        }
        
        // Test the audio context with a silent note
        if (isIOS) {
            await snarePlayer.play('C3', 0, { duration: 0.1, gain: 0 });
            await bassPlayer.play('C2', 0, { duration: 0.1, gain: 0 });
        }
        
        return { audioContext, snarePlayer, bassPlayer };
    } catch (error) {
        console.error('Error initializing audio:', error);
        throw error;
    }
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
        timeout: setTimeout(async () => {
            const player = instrument === 'snare' ? snarePlayer : bassPlayer;
            if (player) {
                try {
                    // For iOS, ensure context is running before playing
                    if (isIOS && audioContext.state === 'suspended') {
                        await audioContext.resume();
                    }
                    await player.play(noteName, scheduleTime, {
                        duration: duration,
                        gain: baseGain,
                        attack: 0,  // Immediate attack for better timing
                        release: isIOS ? 0.1 : 0.2  // Shorter release on iOS
                    });
                } catch (error) {
                    console.error('Error playing note:', error);
                }
            }
        }, Math.max(0, (scheduleTime - audioContext.currentTime) * 1000))
    };
    return note;
}

async function initPlayer(chordSequence, metronomeSequence, displaySequence, timeSignature, bpm, currentVolume) {
    try {
        const loadingOverlay = document.getElementById('loading-overlay');
        const loadingText = document.querySelector('.loading-text');
        const displayContent = document.getElementById('display-content');
        const countdown = document.getElementById('countdown');
        
        // Show loading overlay with tap instruction on iOS
        if (isIOS) {
            loadingText.textContent = 'Tap here to start...';
            loadingText.style.cursor = 'pointer';
            
            // Wait for user interaction
            await new Promise(resolve => {
                const startAudio = async () => {
                    try {
                        // Create a silent audio buffer and play it
                        const buffer = audioContext.createBuffer(1, 1, 22050);
                        const source = audioContext.createBufferSource();
                        source.buffer = buffer;
                        source.connect(audioContext.destination);
                        source.start(0);
                        resolve();
                    } catch (error) {
                        console.error('Error starting audio:', error);
                    }
                };
                loadingText.addEventListener('touchend', startAudio, { once: true });
                loadingText.addEventListener('click', startAudio, { once: true });
            });
        }
        
        // Initialize audio after user interaction
        loadingText.textContent = 'Loading sounds...';
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
        
        // Hide loading overlay
        loadingOverlay.style.opacity = '0';
        displayContent.style.opacity = '1';
        await new Promise(resolve => setTimeout(resolve, 300));
        loadingOverlay.style.display = 'none';
        
        // Countdown with iOS-compatible sound playing
        for (let i = 4; i > 0; i--) {
            countdown.textContent = i;
            if (isIOS) {
                await audioContext.resume();
            }
            try {
                await snarePlayer.play('C3', audioContext.currentTime, { 
                    duration: 0.1, 
                    gain: 0.3,
                    attack: 0,
                    release: isIOS ? 0.1 : 0.2
                });
            } catch (error) {
                console.error('Error playing countdown:', error);
            }
            await new Promise(resolve => setTimeout(resolve, 1000));
        }
        countdown.style.display = 'none';
        
        // Calculate timing
        const totalMeasures = displaySequence.length;
        const secondsPerBeat = 60.0 / bpm;
        const secondsPerMeasure = secondsPerBeat * timeSignature;
        const totalDuration = totalMeasures * secondsPerMeasure;
        
        // For iOS, ensure we're still running
        if (isIOS) {
            await audioContext.resume();
        }
        
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
                
                // Keep audio context running
                if (audioContext.state === 'suspended') {
                    audioContext.resume();
                }
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
        const loadingText = document.querySelector('.loading-text');
        loadingText.textContent = 'Error: ' + error.message;
        loadingText.style.color = '#ff6b6b';
    }
}

async function testSound() {
    try {
        const { audioContext, bassPlayer } = await initAudio();
        if (isIOS) {
            await audioContext.resume();
        }
        if (bassPlayer) {
            await bassPlayer.play('C2', audioContext.currentTime, { 
                duration: 0.5, 
                gain: 0.5,
                attack: 0,
                release: isIOS ? 0.1 : 0.2
            });
        }
    } catch (error) {
        console.error('Error testing sound:', error);
    }
}
