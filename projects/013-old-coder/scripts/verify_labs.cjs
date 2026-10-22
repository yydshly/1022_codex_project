/* Verify business invariants using the exact engine executed by the webpage. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const lab = require('../web/lab-engine.js');
const checks = [];
function check(name, run) { run(); checks.push({name,status:'pass'}); }
for (const scenario of Object.keys(lab.correct)) {
  check(`${scenario}: repaired implementation satisfies the complete contract`, () => assert.equal(lab.runSuite(scenario,lab.correct[scenario]).failed,0));
  check(`${scenario}: all hand-selected behavioral mutants are detected`, () => {
    const result=lab.mutation(scenario); assert.ok(result.baselinePassed); assert.equal(result.killed,result.total);
  });
  check(`${scenario}: weak suite misses at least one real defect`, () => assert.ok(lab.mutation(scenario,'weak').killed < lab.mutation(scenario,'weak').total));
}
check('inventory: arbitrary replay counts never multiply a successful effect', () => {
  for (const requests of [2,3,10,50]) for (const pattern of ['serial','concurrent','restart','failure']) {
    const result=lab.inventory({requests,pattern}); assert.equal(result.stock,9); assert.equal(result.effects,1);
  }
});
check('limiter: 10 distinct seeds match the independent oracle', () => {
  for (const seed of [0,1,2,42,99,100,1234,9876,65535,2147483647]) assert.ok(lab.propertyCheck('sliding',seed).oracleMatch);
});
check('limiter: denying everything passes the upper bound but violates availability', () => {
  const result=lab.propertyCheck('deny'); assert.ok(result.upperBound); assert.equal(result.oracleMatch,false);
});
check('permission: forged identity fields never cross the secure boundary', () => {
  for (const action of ['get','list','export']) {
    const result=lab.permission('secure',{id:'B-01',bodyTenant:'beta',action}); assert.ok(!result.ids.includes('B-01'));
  }
});
const root=path.resolve(__dirname,'..');
const report={kind:'local teaching engine verification',date:'2026-10-22',node:process.version,engineVersion:lab.VERSION,
  engineSHA256:crypto.createHash('sha256').update(fs.readFileSync(path.join(root,'web/lab-engine.js'))).digest('hex'),
  command:'node projects/013-old-coder/scripts/verify_labs.cjs',checks,
  matrices:Object.keys(lab.correct).map(scenario=>({scenario,variants:lab.variants[scenario].map(([id])=>lab.runSuite(scenario,id)),mutation:lab.mutation(scenario),weakMutation:lab.mutation(scenario,'weak')})),
  limits:['Original browser teaching models; no database or live payment/auth service.', 'Deterministic interleavings model concurrency; no multi-process stress test.', 'Hand-selected mutants, not AST-generated mutation coverage.', 'No live AI comparison or causal benchmark of Skill effectiveness.']};
if (process.argv.includes('--check')) {
  const saved=JSON.parse(fs.readFileSync(path.join(root,'results/lab-verification.json'),'utf8'));
  assert.equal(saved.engineSHA256,report.engineSHA256,'saved evidence must identify the current engine');
  assert.equal(saved.checks.length,checks.length);
} else {
  fs.mkdirSync(path.join(root,'results'),{recursive:true});
  fs.writeFileSync(path.join(root,'results/lab-verification.json'),JSON.stringify(report,null,2)+'\n');
  fs.writeFileSync(path.join(root,'web/assets/lab-verification.json'),JSON.stringify(report,null,2)+'\n');
}
console.log(`${checks.length} checks passed; four complete contracts pass; all selected mutants detected.`);
