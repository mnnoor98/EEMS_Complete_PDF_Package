const { default: makeWASocket, useMultiFileAuthState, DisconnectReason, fetchLatestBaileysVersion } = require('@whiskeysockets/baileys');
const pino = require('pino');
const QRCode = require('qrcode');
const express = require('express');
const cors = require('cors');
const path = require('path');
const fs = require('fs');

const app = express();
app.use(cors());
app.use(express.json());

const PORT = 5140;
const AUTH_DIR = path.join(__dirname, 'auth_info_baileys');

if (!fs.existsSync(AUTH_DIR)) {
  fs.mkdirSync(AUTH_DIR, { recursive: true });
}

let sock = null;
let currentQR = null;
let qrDataUrl = null;
let isConnected = false;
let userPhone = null;
let isConnecting = false;
let connectionAttempts = 0;

// Queue management for auto-sending
let messageQueue = [];
let isQueueProcessing = false;
let queueStats = {
  total: 0,
  sent: 0,
  failed: 0,
  currentVoter: null,
  status: 'IDLE' // IDLE, PROCESSING, PAUSED, COMPLETED
};

async function startBot() {
  if (isConnecting) return;
  isConnecting = true;

  try {
    const { state, saveCreds } = await useMultiFileAuthState(AUTH_DIR);
    const { version } = await fetchLatestBaileysVersion().catch(() => ({ version: [2, 3000, 1015901307] }));

    sock = makeWASocket({
      version,
      logger: pino({ level: 'silent' }),
      auth: state,
      printQRInTerminal: false,
      connectTimeoutMs: 60000,
      defaultQueryTimeoutMs: 60000,
      keepAliveIntervalMs: 25000,
      emitOwnEvents: false,
      browser: ['EEMS Election War Room', 'Chrome', '1.0.0']
    });

    sock.ev.on('creds.update', saveCreds);

    sock.ev.on('connection.update', async (update) => {
      const { connection, lastDisconnect, qr } = update;

      if (qr) {
        currentQR = qr;
        try {
          qrDataUrl = await QRCode.toDataURL(qr);
          console.log('[WhatsApp Bot] New pairing QR generated. Scan from Candidate War Room.');
        } catch (err) {
          console.error('[WhatsApp Bot] QR render error:', err);
        }
      }

      if (connection === 'close') {
        const statusCode = lastDisconnect?.error?.output?.statusCode;
        const shouldReconnect = statusCode !== DisconnectReason.loggedOut;
        console.log(`[WhatsApp Bot] Connection closed. Reason: ${statusCode}, Reconnecting: ${shouldReconnect}`);
        isConnected = false;
        isConnecting = false;
        userPhone = null;

        if (shouldReconnect) {
          setTimeout(() => startBot(), 3000);
        } else {
          console.log('[WhatsApp Bot] Device logged out. Resetting auth directory.');
          try {
            fs.rmSync(AUTH_DIR, { recursive: true, force: true });
          } catch (e) {}
          setTimeout(() => startBot(), 2000);
        }
      } else if (connection === 'open') {
        console.log('[WhatsApp Bot] Connection established successfully!');
        isConnected = true;
        isConnecting = false;
        currentQR = null;
        qrDataUrl = null;
        userPhone = sock.user?.id ? sock.user.id.split(':')[0] : 'Connected User';
      }
    });

  } catch (err) {
    console.error('[WhatsApp Bot] Startup error:', err);
    isConnecting = false;
    setTimeout(() => startBot(), 5000);
  }
}

// Background Queue Dispatcher
async function processQueue() {
  if (isQueueProcessing || messageQueue.length === 0 || !isConnected) return;
  isQueueProcessing = true;
  queueStats.status = 'PROCESSING';

  while (messageQueue.length > 0 && isConnected) {
    const item = messageQueue.shift();
    queueStats.currentVoter = item.name || item.phone;

    try {
      let cleanPhone = String(item.phone || '').replace(/\D/g, '');
      if (cleanPhone.startsWith('880')) {
        // already fine
      } else if (cleanPhone.startsWith('01')) {
        cleanPhone = '88' + cleanPhone;
      } else if (cleanPhone.length === 10 && cleanPhone.startsWith('1')) {
        cleanPhone = '880' + cleanPhone;
      }

      const jid = `${cleanPhone}@s.whatsapp.net`;
      console.log(`[WhatsApp Bot] Auto-sending to ${jid}...`);

      await sock.sendMessage(jid, { text: item.message });
      queueStats.sent++;
      console.log(`[WhatsApp Bot] Successfully delivered to ${item.name || cleanPhone} (${queueStats.sent}/${queueStats.total})`);

      // Human-like delay between messages (3.5 seconds) to avoid spam rate limits
      await new Promise(resolve => setTimeout(resolve, 3500));
    } catch (err) {
      console.error(`[WhatsApp Bot] Failed sending to ${item.phone}:`, err?.message || err);
      queueStats.failed++;
    }
  }

  isQueueProcessing = false;
  queueStats.currentVoter = null;
  queueStats.status = messageQueue.length === 0 ? 'COMPLETED' : 'IDLE';
}

// Endpoints
app.get('/api/whatsapp/status', (req, res) => {
  res.json({
    connected: isConnected,
    phone: userPhone,
    isConnecting,
    hasQR: !!qrDataUrl,
    queueStats,
    queueRemaining: messageQueue.length
  });
});

app.get('/api/whatsapp/qr', (req, res) => {
  res.json({
    connected: isConnected,
    phone: userPhone,
    qrDataUrl
  });
});

app.post('/api/whatsapp/send', async (req, res) => {
  if (!isConnected) {
    return res.status(400).json({ error: 'not_connected', message: 'হোয়াটসঅ্যাপ বট সংযুক্ত নয়। অনুগ্রহ করে কিউআর স্ক্যান করুন।' });
  }

  const { to, message } = req.body;
  if (!to || !message) {
    return res.status(400).json({ error: 'missing_params', message: 'মোবাইল নম্বর ও মেসেজ আবশ্যক।' });
  }

  try {
    let cleanPhone = String(to).replace(/\D/g, '');
    if (cleanPhone.startsWith('01')) cleanPhone = '88' + cleanPhone;
    const jid = `${cleanPhone}@s.whatsapp.net`;

    const sent = await sock.sendMessage(jid, { text: message });
    res.json({ success: true, messageId: sent.key.id, to: cleanPhone });
  } catch (err) {
    res.status(500).json({ error: 'send_failed', message: err.message });
  }
});

app.post('/api/whatsapp/broadcast', (req, res) => {
  if (!isConnected) {
    return res.status(400).json({ error: 'not_connected', message: 'হোয়াটসঅ্যাপ বট সংযুক্ত নয়। অনুগ্রহ করে কিউআর স্ক্যান করুন।' });
  }

  const rawItems = req.body.items || req.body.Items || [];
  if (!Array.isArray(rawItems) || rawItems.length === 0) {
    return res.status(400).json({ error: 'empty_items', message: 'কোনো প্রাপক ভোটার তালিকা প্রদান করা হয়নি।' });
  }

  const items = rawItems.map(it => ({
    id: it.id || it.Id,
    name: it.name || it.Name,
    phone: it.phone || it.Phone,
    message: it.message || it.Message
  }));

  // Add to queue
  messageQueue.push(...items);
  queueStats.total += items.length;
  queueStats.status = 'PROCESSING';

  // Trigger processor asynchronously
  processQueue();

  res.json({
    success: true,
    message: `${items.length} জন ভোটারের হোয়াটসঅ্যাপ বার্তা অটো-ডিসপ্যাচ কিউতে যুক্ত হয়েছে। ব্যাকগ্রাউন্ডে একা একা পাঠানো হচ্ছে।`,
    queueStats
  });
});

app.post('/api/whatsapp/clear-queue', (req, res) => {
  const cancelledCount = messageQueue.length;
  messageQueue = [];
  queueStats.status = 'IDLE';
  queueStats.currentVoter = null;
  res.json({ success: true, cancelledCount });
});

app.post('/api/whatsapp/logout', async (req, res) => {
  try {
    if (sock) {
      await sock.logout().catch(() => {});
    }
  } catch (e) {}

  try {
    fs.rmSync(AUTH_DIR, { recursive: true, force: true });
  } catch (e) {}

  isConnected = false;
  userPhone = null;
  currentQR = null;
  qrDataUrl = null;
  messageQueue = [];
  queueStats = { total: 0, sent: 0, failed: 0, currentVoter: null, status: 'IDLE' };

  setTimeout(() => startBot(), 1000);
  res.json({ success: true, message: 'সফলভাবে লগআউট করা হয়েছে। নতুন QR কোড প্রস্তুত হচ্ছে।' });
});

// Start Express and Bot
app.listen(PORT, () => {
  console.log(`[WhatsApp Bot] Server listening on http://localhost:${PORT}`);
  startBot();
});

