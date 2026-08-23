/**
 * DSP Interactive Studio - Web Audio Sonification Module
 * Converts discrete-time signals into audible sound waves and clicks.
 */

class SignalAudioPlayer {
  constructor() {
    this.audioCtx = null;
    this.currentSource = null;
    this.isPlaying = false;
  }

  initContext() {
    if (!this.audioCtx) {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      this.audioCtx = new AudioContext();
    }
    if (this.audioCtx.state === "suspended") {
      this.audioCtx.resume();
    }
  }

  /**
   * Play array of discrete-time samples as an audio waveform.
   * Repeats periodic or short sequences for 1.5 seconds for comfortable listening.
   */
  playSignalBuffer(samples, sampleRate = 8000, durationSec = 1.5) {
    this.initContext();
    this.stop();

    if (!samples || samples.length === 0) return;

    // Check if signal is all zeros
    const maxVal = Math.max(...samples.map(Math.abs));
    if (maxVal < 1e-6) {
      console.warn("Signal is all zero, nothing to play.");
      return;
    }

    // Normalize signal to range [-0.9, 0.9]
    const normalized = samples.map(v => (v / maxVal) * 0.85);

    // Build audio buffer repeating sequence to fill durationSec
    const totalSamples = Math.floor(sampleRate * durationSec);
    const audioBuffer = this.audioCtx.createBuffer(1, totalSamples, sampleRate);
    const channelData = audioBuffer.getChannelData(0);

    const seqLen = normalized.length;
    for (let i = 0; i < totalSamples; i++) {
      // Loop smoothly with envelope fade-in/fade-out
      const rawSample = normalized[i % seqLen];
      let envelope = 1.0;
      const fadeLen = Math.floor(sampleRate * 0.05); // 50ms fade
      if (i < fadeLen) envelope = i / fadeLen;
      else if (i > totalSamples - fadeLen) envelope = (totalSamples - i) / fadeLen;

      channelData[i] = rawSample * envelope;
    }

    const source = this.audioCtx.createBufferSource();
    source.buffer = audioBuffer;

    const gainNode = this.audioCtx.createGain();
    gainNode.gain.setValueAtTime(0.3, this.audioCtx.currentTime);

    source.connect(gainNode);
    gainNode.connect(this.audioCtx.destination);

    source.onended = () => {
      this.isPlaying = false;
    };

    source.start();
    this.currentSource = source;
    this.isPlaying = true;
  }

  /**
   * Play short click tone for step-by-step animation.
   */
  playClickTone(freq = 440, duration = 0.04) {
    try {
      this.initContext();
      const osc = this.audioCtx.createOscillator();
      const gain = this.audioCtx.createGain();

      osc.type = "sine";
      osc.frequency.setValueAtTime(freq, this.audioCtx.currentTime);

      gain.gain.setValueAtTime(0.15, this.audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, this.audioCtx.currentTime + duration);

      osc.connect(gain);
      gain.connect(this.audioCtx.destination);

      osc.start();
      osc.stop(this.audioCtx.currentTime + duration);
    } catch (e) {
      // Audio context might be restricted before user gesture
    }
  }

  stop() {
    if (this.currentSource) {
      try {
        this.currentSource.stop();
      } catch (e) {}
      this.currentSource = null;
    }
    this.isPlaying = false;
  }
}

// Global player instance
window.dspAudio = new SignalAudioPlayer();
