import subprocess

code = """
const qrcode = require('./node_modules/qrcode');
qrcode.toDataURL('EEMS:TEST:123').then(x => {
  console.log('SUCCESS! QR Code data URL length:', x.length);
  console.log('Sample prefix:', x.substring(0, 50));
}).catch(console.error);
"""

p = subprocess.run(['node', '-e', code], cwd='frontend', capture_output=True, text=True)
print("STDOUT:", p.stdout)
print("STDERR:", p.stderr)

