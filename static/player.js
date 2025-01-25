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
    try {
        if (!audioContext) {
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            audioContext = new AudioContext();
            masterGain = audioContext.createGain();
            masterGain.connect(audioContext.destination);
        }

        // For iOS, we need to unlock the audio context
        if (isIOS && audioContext.state === 'suspended') {
            // Create and play a short silent buffer
            const silentBuffer = audioContext.createBuffer(1, 1, 22050);
            const source = audioContext.createBufferSource();
            source.buffer = silentBuffer;
            source.connect(audioContext.destination);
            source.start(0);
            await audioContext.resume();
        }

        // Initialize soundfont with specific audio settings for iOS
        const soundfontOptions = {
            destination: masterGain,
            format: 'mp3', // Always use mp3 for better iOS compatibility
            soundfont: 'FluidR3_GM'
        };

        // Load instruments if not already loaded
        if (!snarePlayer) {
            snarePlayer = await Soundfont.instrument(audioContext, 'synth_drum', soundfontOptions);
        }
        if (!bassPlayer) {
            bassPlayer = await Soundfont.instrument(audioContext, 'acoustic_bass', soundfontOptions);
        }

        return { audioContext, snarePlayer, bassPlayer };
    } catch (error) {
        console.error('Error initializing audio:', error);
        throw error;
    }
}

// Schedule a note to play
async function playNote(player, noteName, time, duration, gain) {
    if (isIOS && audioContext.state === 'suspended') {
        await audioContext.resume();
    }
    return player.play(noteName, time, {
        duration: duration,
        gain: gain,
        attack: 0
    });
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
            await new Promise((resolve) => {
                const handleTap = async () => {
                    loadingText.removeEventListener('touchend', handleTap);
                    loadingText.removeEventListener('click', handleTap);
                    try {
                        // Create a user gesture triggered sound
                        const oscillator = audioContext.createOscillator();
                        oscillator.connect(audioContext.destination);
                        oscillator.start(0);
                        oscillator.stop(0.001);
                        await audioContext.resume();
                        resolve();
                    } catch (error) {
                        console.error('Error starting audio:', error);
                        loadingText.textContent = 'Tap again to retry...';
                    }
                };

                loadingText.addEventListener('touchend', handleTap);
                loadingText.addEventListener('click', handleTap);
            });
        }

        // Initialize audio after user interaction
        loadingText.textContent = 'Loading sounds...';
        const { audioContext, snarePlayer, bassPlayer } = await initAudio();

        // Set initial volume
        if (masterGain) {
            masterGain.gain.setValueAtTime(currentVolume, audioContext.currentTime);
        }

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

        // Countdown with sound
        for (let i = 4; i > 0; i--) {
            countdown.textContent = i;
            try {
                await playNote(snarePlayer, 'C3', audioContext.currentTime, 0.1, 0.3);
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

        // Schedule all notes
        const startTime = audioContext.currentTime + 0.1;
        let currentBeat = -1;
        let currentMeasure = 0;

        // Function to play a note at the scheduled time
        async function scheduleNote(noteName, time, duration, gain, isChord = false) {
            const player = isChord ? bassPlayer : snarePlayer;
            const scheduleTime = startTime + time;
            
            setTimeout(async () => {
                try {
                    await playNote(player, noteName, audioContext.currentTime, duration, gain);
                } catch (error) {
                    console.error('Error playing note:', error);
                }
            }, (scheduleTime - audioContext.currentTime) * 1000);
        }

        // Schedule chord sequence
        for (const chord of chordSequence) {
            scheduleNote(chord.note, chord.time, chord.duration, 0.8, true);
        }

        // Schedule metronome sequence
        for (let time = 0; time < totalDuration; time += secondsPerBeat) {
            const isDownbeat = (Math.floor(time / secondsPerMeasure) * secondsPerMeasure) === time;
            scheduleNote('C3', time, 0.1, isDownbeat ? 0.4 : 0.2, false);
        }

        // Update display
        function updateDisplay() {
            if (audioContext.state === 'suspended') {
                audioContext.resume();
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
        if (!audioContext) {
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            audioContext = new AudioContext();
            masterGain = audioContext.createGain();
            masterGain.connect(audioContext.destination);
        }

        if (audioContext.state === 'suspended') {
            await audioContext.resume();
        }

        const soundfontOptions = {
            destination: masterGain,
            format: 'mp3'
        };

        const player = await Soundfont.instrument(audioContext, 'acoustic_bass', soundfontOptions);
        await playNote(player, 'C2', audioContext.currentTime, 0.5, 0.5);
    } catch (error) {
        console.error('Error testing sound:', error);
    }
}
