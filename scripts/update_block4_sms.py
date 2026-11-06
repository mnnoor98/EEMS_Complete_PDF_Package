with open('scripts/war_room_blocks/block4_class.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Update signals
old_signals = '''  smsConfigProvider = signal('SIMULATOR');
  smsConfigApiKey = signal('');
  smsConfigSenderId = signal('SCALE_FARUK');
  smsConfigEndpoint = signal('http://api.greenweb.com.bd/api.php');'''

new_signals = '''  smsConfigProvider = signal('SMS_NET_BD');
  smsConfigApiKey = signal('Y68UVFD1flDgDCb6AgvC2i3uL7volImeKoSUSFf93');
  smsConfigSenderId = signal('');
  smsConfigEndpoint = signal('https://api.sms.net.bd/sendsms');'''

assert old_signals in text, "old_signals not found"
text = text.replace(old_signals, new_signals)

# Update loadSmsConfig and add onSmsProviderChange
old_load = '''        this.smsConfig.set(cfg);
        this.smsConfigProvider.set(cfg.provider);
        this.smsConfigApiKey.set(cfg.apiKey || '');
        this.smsConfigSenderId.set(cfg.senderId || 'SCALE_FARUK');
        this.smsConfigEndpoint.set(cfg.endpointUrl || 'http://api.greenweb.com.bd/api.php');'''

new_load = '''        this.smsConfig.set(cfg);
        this.smsConfigProvider.set(cfg.provider || 'SMS_NET_BD');
        this.smsConfigApiKey.set(cfg.apiKey || 'Y68UVFD1flDgDCb6AgvC2i3uL7volImeKoSUSFf93');
        this.smsConfigSenderId.set(cfg.senderId || '');
        this.smsConfigEndpoint.set(cfg.endpointUrl || 'https://api.sms.net.bd/sendsms');'''

assert old_load in text, "old_load not found"
text = text.replace(old_load, new_load)

# Add onSmsProviderChange method
method_anchor = '  openSmsConfigModal() {'
new_method = '''  onSmsProviderChange(prov: string) {
    if (prov === 'SMS_NET_BD') {
      this.smsConfigEndpoint.set('https://api.sms.net.bd/sendsms');
      if (!this.smsConfigApiKey()) {
        this.smsConfigApiKey.set('Y68UVFD1flDgDCb6AgvC2i3uL7volImeKoSUSFf93');
      }
    } else if (prov === 'GREENWEB') {
      this.smsConfigEndpoint.set('http://api.greenweb.com.bd/api.php');
    }
  }

  openSmsConfigModal() {'''

assert method_anchor in text, "method_anchor not found"
text = text.replace(method_anchor, new_method)

with open('scripts/war_room_blocks/block4_class.py', 'w', encoding='utf-8') as f:
    f.write(text)

print('Updated block4_class.py successfully!')

