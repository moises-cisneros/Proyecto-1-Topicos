const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const rootDir = path.resolve(__dirname, '..');
const isWin = process.platform === 'win32';

// Buscar binarios en el entorno virtual .venv
const venvPython = isWin
  ? path.join(rootDir, '.venv', 'Scripts', 'python.exe')
  : path.join(rootDir, '.venv', 'bin', 'python');

const venvUvicorn = isWin
  ? path.join(rootDir, '.venv', 'Scripts', 'uvicorn.exe')
  : path.join(rootDir, '.venv', 'bin', 'uvicorn');

const uvicornBaseArgs = [
  'api.main:app',
  '--reload',
  '--reload-dir',
  path.join(rootDir, 'packages', 'api'),
  '--reload-dir',
  path.join(rootDir, 'packages', 'pipeline'),
  '--port',
  '8090',
];

let cmd = 'uvicorn';
let args = [...uvicornBaseArgs];

if (fs.existsSync(venvUvicorn)) {
  cmd = venvUvicorn;
} else if (fs.existsSync(venvPython)) {
  cmd = venvPython;
  args = ['-m', 'uvicorn', ...uvicornBaseArgs];
} else {
  cmd = 'python';
  args = ['-m', 'uvicorn', ...uvicornBaseArgs];
}

// Pasar argumentos adicionales de línea de comandos si los hay
const extraArgs = process.argv.slice(2);
if (extraArgs.length > 0) {
  args.push(...extraArgs);
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

const child = spawn(cmd, args, {
  cwd: rootDir,
  env,
  stdio: 'inherit',
  shell: false,
});

child.on('error', (err) => {
  console.error('[SMS Sentinel] Error al iniciar Uvicorn:', err.message);
  process.exit(1);
});

child.on('exit', (code) => {
  process.exit(code || 0);
});
