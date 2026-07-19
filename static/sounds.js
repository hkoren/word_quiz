/* Spellaroo sound effects — synthesized with the Web Audio API so there are no
   audio files to download. Correct/incorrect sounds come in selectable themes;
   the choice is stored in localStorage under 'spellaroo_sound'.
   Values: 'classic' | 'arcade' | 'cheer' | 'chime' | 'random' | 'off'. */
(function () {
    var ctx = null;

    function ac() {
        if (!ctx) {
            var AC = window.AudioContext || window.webkitAudioContext;
            if (!AC) return null;
            ctx = new AC();
        }
        if (ctx.state === 'suspended') { try { ctx.resume(); } catch (e) {} }
        return ctx;
    }

    // A single enveloped oscillator note.
    function tone(freq, startOffset, dur, type, peak) {
        var c = ac(); if (!c) return;
        var t0 = c.currentTime + (startOffset || 0);
        var osc = c.createOscillator();
        var g = c.createGain();
        osc.type = type || 'sine';
        osc.frequency.setValueAtTime(freq, t0);
        peak = (peak == null) ? 0.2 : peak;
        g.gain.setValueAtTime(0.0001, t0);
        g.gain.exponentialRampToValueAtTime(peak, t0 + 0.01);
        g.gain.exponentialRampToValueAtTime(0.0001, t0 + dur);
        osc.connect(g); g.connect(c.destination);
        osc.start(t0); osc.stop(t0 + dur + 0.02);
    }

    // A note that slides from f1 to f2 (for buzzes / sad-trombone glides).
    function glide(f1, f2, startOffset, dur, type, peak) {
        var c = ac(); if (!c) return;
        var t0 = c.currentTime + (startOffset || 0);
        var osc = c.createOscillator();
        var g = c.createGain();
        osc.type = type || 'sawtooth';
        osc.frequency.setValueAtTime(f1, t0);
        osc.frequency.linearRampToValueAtTime(f2, t0 + dur);
        peak = (peak == null) ? 0.2 : peak;
        g.gain.setValueAtTime(0.0001, t0);
        g.gain.exponentialRampToValueAtTime(peak, t0 + 0.02);
        g.gain.exponentialRampToValueAtTime(0.0001, t0 + dur);
        osc.connect(g); g.connect(c.destination);
        osc.start(t0); osc.stop(t0 + dur + 0.02);
    }

    // A filtered noise burst (for arcade "explosion").
    function noise(startOffset, dur, peak, filterFreq) {
        var c = ac(); if (!c) return;
        var t0 = c.currentTime + (startOffset || 0);
        var n = Math.floor(c.sampleRate * dur);
        var buf = c.createBuffer(1, n, c.sampleRate);
        var d = buf.getChannelData(0);
        for (var i = 0; i < n; i++) d[i] = Math.random() * 2 - 1;
        var src = c.createBufferSource(); src.buffer = buf;
        var lp = c.createBiquadFilter(); lp.type = 'lowpass';
        lp.frequency.setValueAtTime(filterFreq || 1000, t0);
        var g = c.createGain();
        peak = (peak == null) ? 0.3 : peak;
        g.gain.setValueAtTime(peak, t0);
        g.gain.exponentialRampToValueAtTime(0.0001, t0 + dur);
        src.connect(lp); lp.connect(g); g.connect(c.destination);
        src.start(t0); src.stop(t0 + dur);
    }

    var THEMES = {
        classic: {
            label: 'Ding / Buzz',
            correct: function () { tone(880, 0, 0.12, 'sine', 0.25); tone(1318.5, 0.09, 0.25, 'sine', 0.25); },
            incorrect: function () { glide(200, 110, 0, 0.35, 'sawtooth', 0.2); }
        },
        arcade: {
            label: 'Arcade',
            correct: function () { tone(987.77, 0, 0.08, 'square', 0.16); tone(1318.5, 0.08, 0.18, 'square', 0.16); }, // coin
            incorrect: function () { noise(0, 0.4, 0.3, 800); glide(320, 70, 0, 0.4, 'square', 0.1); } // explosion
        },
        cheer: {
            label: 'Woohoo / Womp',
            correct: function () { // rising fanfare
                [523.25, 659.25, 783.99, 1046.5].forEach(function (f, i) { tone(f, i * 0.09, 0.2, 'triangle', 0.22); });
            },
            incorrect: function () { // sad-trombone "womp womp" — descending glides
                [233.08, 220, 207.65, 185].forEach(function (f, i) { glide(f, f * 0.93, i * 0.19, 0.22, 'sawtooth', 0.18); });
            }
        },
        chime: {
            label: 'Chime',
            correct: function () { tone(1046.5, 0, 0.5, 'sine', 0.2); tone(1568, 0, 0.5, 'sine', 0.1); },
            incorrect: function () { tone(196, 0, 0.45, 'sine', 0.22); tone(185, 0.05, 0.4, 'sine', 0.15); }
        }
    };
    var THEME_KEYS = ['classic', 'arcade', 'cheer', 'chime'];

    function getPref() { return localStorage.getItem('spellaroo_sound') || 'classic'; }
    function setPref(v) { localStorage.setItem('spellaroo_sound', v); }

    function resolveTheme() {
        var p = getPref();
        if (p === 'off') return null;
        if (p === 'random') return THEMES[THEME_KEYS[Math.floor(Math.random() * THEME_KEYS.length)]];
        return THEMES[p] || THEMES.classic;
    }

    window.SpellarooSounds = {
        THEMES: THEMES,
        THEME_KEYS: THEME_KEYS,
        play: function (isCorrect) {
            var t = resolveTheme();
            if (!t) return;
            try { (isCorrect ? t.correct : t.incorrect)(); } catch (e) {}
        },
        // Preview a theme (plays its correct sound) — used when changing the selector.
        preview: function (theme) {
            if (theme === 'off') return;
            var t = (theme === 'random')
                ? THEMES[THEME_KEYS[Math.floor(Math.random() * THEME_KEYS.length)]]
                : THEMES[theme];
            if (!t) return;
            try { t.correct(); } catch (e) {}
        },
        getPref: getPref,
        setPref: setPref
    };
})();
