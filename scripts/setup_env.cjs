const { spawnSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const rootDir = path.resolve(__dirname, '..');
const isWin = process.platform === 'win32';
const venvDir = path.join(rootDir, '.venv');
const venvPython = isWin
  ? path.join(venvDir, 'Scripts', 'python.exe')
  : path.join(venvDir, 'bin', 'python');

console.log('[SMS Sentinel] Configurando entorno de desarrollo unificado...');

// 1. Crear .venv si no existe
if (!fs.existsSync(venvPython)) {
  console.log('==> Creando entorno virtual de Python en .venv...');
  const venvRes = spawnSync('python', ['-m', 'venv', '.venv'], {
    cwd: rootDir,
    stdio: 'inherit',
    shell: false,
  });
  if (venvRes.status !== 0) {
    console.error('[ERROR] No se pudo crear .venv. Verifique que Python 3.10+ esté instalado.');
    process.exit(1);
  }
}

// 2. Instalar dependencias de Python
console.log('==> Instalando/actualizando dependencias de API y Machine Learning...');
const pipRes = spawnSync(venvPython, ['-m', 'pip', 'install', '--upgrade', 'pip'], {
  cwd: rootDir,
  stdio: 'inherit',
  shell: false,
});

const reqRes = spawnSync(venvPython, ['-m', 'pip', 'install', '-r', 'api/requirements.txt'], {
  cwd: rootDir,
  stdio: 'inherit',
  shell: false,
});

if (reqRes.status !== 0) {
  console.error('[ERROR] Fallo al instalar api/requirements.txt');
  process.exit(1);
}

console.log('[OK] Entorno de Python sincronizado y listo para ejecutar.');
