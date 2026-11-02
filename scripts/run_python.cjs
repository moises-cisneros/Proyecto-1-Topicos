const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const rootDir = path.resolve(__dirname, '..');
const isWin = process.platform === 'win32';

// Detectar Python dentro de .venv
const venvPython = isWin
  ? path.join(rootDir, '.venv', 'Scripts', 'python.exe')
  : path.join(rootDir, '.venv', 'bin', 'python');

const pythonBin = fs.existsSync(venvPython) ? venvPython : 'python';

const args = process.argv.slice(2);
if (args.length === 0) {
  console.error('[SMS Sentinel] Debe especificar un script o modulo para ejecutar.');
  process.exit(1);
}

// Cargar variables desde .env si existe en la raíz
function loadDotenv(dotenvPath) {
  if (!fs.existsSync(dotenvPath)) return {};
  const parsed = {};
  try {
    const raw = fs.readFileSync(dotenvPath, 'utf-8');
    for (const line of raw.split('\n')) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith('#') || !trimmed.includes('=')) continue;
      const idx = trimmed.indexOf('=');
      const key = trimmed.slice(0, idx).trim();
      let val = trimmed.slice(idx + 1).trim();
      if ((val.startsWith('"') && val.endsWith('"')) || (val.startsWith("'") && val.endsWith("'"))) {
        val = val.slice(1, -1);
      }
      if (key) parsed[key] = val;
    }
  } catch (_) {}
  return parsed;
}

const fileEnv = loadDotenv(path.join(rootDir, '.env'));

const env = {
  ...fileEnv,
  ...process.env,
  PYTHONPATH: [rootDir, path.join(rootDir, 'packages')].join(path.delimiter),
};

const child = spawn(pythonBin, args, {
  cwd: rootDir,
  env,
  stdio: 'inherit',
  shell: false,
});

child.on('error', (err) => {
  console.error('[SMS Sentinel] Error al ejecutar Python:', err.message);
  process.exit(1);
});

child.on('exit', (code) => {
  process.exit(code || 0);
});
