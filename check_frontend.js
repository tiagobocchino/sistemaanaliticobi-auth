/**
 * Script para verificar se o frontend está rodando
 * Execute com: node check_frontend.js
 */

const http = require('http');

const FRONTEND_URL = 'http://localhost:5173';
const BACKEND_URL = 'http://localhost:8000';

console.log('='.repeat(60));
console.log('VERIFICACAO DO FRONTEND');
console.log('='.repeat(60));
console.log(`URL do Frontend: ${FRONTEND_URL}`);
console.log(`URL do Backend: ${BACKEND_URL}`);
console.log();

// Teste 1: Verificar Frontend
console.log('1. Testando Frontend...');
const frontendReq = http.get(FRONTEND_URL, (res) => {
  console.log(`   Status: ${res.statusCode}`);
  if (res.statusCode === 200) {
    console.log('   FRONTEND ESTA RODANDO!');
  } else {
    console.log(`   FRONTEND RESPONDEU COM STATUS ${res.statusCode}`);
  }
});

frontendReq.on('error', (error) => {
  console.log('   ERRO: Frontend nao esta rodando!');
  console.log(`   ${error.message}`);
  console.log();
  console.log('   SOLUCAO:');
  console.log('   1. Abra um terminal na pasta frontend');
  console.log('   2. Execute: npm run dev');
  console.log('   3. Aguarde ver: "Local: http://localhost:5173/"');
});

frontendReq.setTimeout(3000, () => {
  frontendReq.destroy();
  console.log('   TIMEOUT: Frontend nao respondeu em 3 segundos');
});

// Teste 2: Verificar Backend
setTimeout(() => {
  console.log();
  console.log('2. Testando Backend...');
  const backendReq = http.get(`${BACKEND_URL}/health`, (res) => {
    let data = '';
    res.on('data', (chunk) => { data += chunk; });
    res.on('end', () => {
      console.log(`   Status: ${res.statusCode}`);
      console.log(`   Resposta: ${data}`);
      if (res.statusCode === 200) {
        console.log('   BACKEND ESTA RODANDO!');
      }
    });
  });

  backendReq.on('error', (error) => {
    console.log('   ERRO: Backend nao esta rodando!');
    console.log(`   ${error.message}`);
    console.log();
    console.log('   SOLUCAO:');
    console.log('   1. Execute: python main.py');
    console.log('   2. Aguarde ver: "Uvicorn running on http://0.0.0.0:8000"');
  });

  backendReq.setTimeout(3000, () => {
    backendReq.destroy();
    console.log('   TIMEOUT: Backend nao respondeu em 3 segundos');
  });
}, 500);

setTimeout(() => {
  console.log();
  console.log('='.repeat(60));
  console.log('INSTRUCOES:');
  console.log('='.repeat(60));
  console.log('Se o frontend nao esta rodando:');
  console.log('  1. cd frontend');
  console.log('  2. npm run dev');
  console.log();
  console.log('Se o backend nao esta rodando:');
  console.log('  1. python main.py');
  console.log();
  console.log('Apos ambos estarem rodando:');
  console.log('  Acesse: http://localhost:5173/test');
  console.log('='.repeat(60));
}, 3500);
