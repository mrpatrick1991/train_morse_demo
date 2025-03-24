import morse from 'morse';
import * as Tone from "tone";
import Peer from 'peerjs';

// Setup display elements
const morseTextEl = document.getElementById('morseText');
const typedTextEl = document.getElementById('typedText');

const lastMorseTextEl = document.getElementById('lastMorseText');
const lastTypedTextEl = document.getElementById('lastTypedText');

let typedText = '';
let morseText = '';

let lastMorseText = '';
let lastTypedText = '';

// Audio synth
const oscBeep = (freq = 600, duration = 0.1, time = Tone.now()) => {
  const osc = new Tone.Oscillator(freq, 'sine').toDestination();
  osc.start(time).stop(time + duration);
};

// === PeerJS Setup ===
const peerId = '' + Math.floor(Math.random() * 10000).toString().padStart(4, '0');
const peer = new Peer(peerId); // Connects to default PeerJS signaling server
let conn = null;

peer.on('open', id => {
  document.getElementById('yourId').textContent = "ID: " + id;
});

document.getElementById('connectBtn').addEventListener('click', () => {
  const targetId = document.getElementById('peerIdInput').value.trim();
  conn = peer.connect(targetId);

  conn.on('open', () => {
    console.log('Connected to peer:', targetId);
  });

  conn.on('data', data => {
    console.log('Received:', data);
    typedText = data.typedText;
    morseText = data.morseText;
    playMorseSound(data.morseText.trim().split(' ').pop()); // Only play the most recent Morse chunk
    updateDisplay();
  });
});

// Listen for incoming connections
peer.on('connection', incoming => {
  conn = incoming;

  conn.on('data', data => {
    typedText = data.typedText;
    morseText = data.morseText;
    playMorseSound(data.morseText.trim().split(' ').pop()); // Only play the most recent Morse chunk
    updateDisplay();
  });
});

// === Typing ===
window.addEventListener('keydown', (event) => {

  const active = document.activeElement;
  if (active && (active.tagName === 'INPUT' || active.tagName === 'TEXTAREA')) {
      return; // Ignore keystrokes while typing in inputs
  }
  const key = event.key.toUpperCase();

  if (/^[A-Z0-9]$/.test(key)) {
    typedText += key;
    const encoded = morse.encode(key);
    morseText += encoded + ' ';
    playMorseSound(encoded);
    broadcastState();
  }

  if (event.key === ' ') {
    typedText += ' ';
    morseText += '/ ';
    broadcastState();
  }

  if (event.key === 'Backspace') {
    typedText = typedText.slice(0, -1);
    let parts = morseText.trim().split(' ');
    parts.pop();
    morseText = parts.join(' ') + (parts.length ? ' ' : '');
    broadcastState();
  }

  updateDisplay();
});

function updateDisplay() {
  typedTextEl.textContent = typedText;
  morseTextEl.textContent = morseText;
  const splitMorseText = morseText.split([' '])
  console.log(splitMorseText)
  lastTypedTextEl.textContent = typedText.split(' ').pop();
  lastMorseTextEl.textContent = splitMorseText[splitMorseText.length - 2];
}

function broadcastState() {
  if (conn && conn.open) {
    conn.send({ typedText, morseText });
  }
}

function playMorseSound(code) {
  let time = Tone.now();
  for (let symbol of code) {
    if (symbol === '.') {
      oscBeep(600, 0.1, time);
      time += 0.2;
    } else if (symbol === '-') {
      oscBeep(600, 0.3, time);
      time += 0.4;
    } else {
      time += 0.2;
    }
  }
}