const https = require('https');

const SUPABASE_URL = 'https://nfxehlmkohmemsjldsbc.supabase.co';
const ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5meGVobG1rb2htZW1zamxkc2JjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODA4Mzc2MzgsImV4cCI6MjA5NjQxMzYzOH0.fhOEKAd4NQjignN3MQEAegghrIMgSj9cRdeyJMYrE6g';

const today = new Date('2026-06-07T00:00:00Z');
function daysAgo(n) { const d = new Date(today); d.setDate(d.getDate() - n); return d.toISOString().slice(0, 10); }
function daysAhead(n) { const d = new Date(today); d.setDate(d.getDate() + n); return d.toISOString().slice(0, 10); }

function genWQ(pondId, baseTemp) {
  const arr = [];
  for (let i = 29; i >= 0; i--) {
    const wobble = Math.sin(i/3) * 0.4;
    arr.push({
      _id: `wq-${pondId}-${i}`, date: daysAgo(i), pond: pondId, time: i%2===0?'Pagi':'Petang',
      ph: +(8.0+wobble*0.3+(Math.random()-0.5)*0.2).toFixed(2),
      do: +(5.2+wobble*0.6+(Math.random()-0.5)*0.5).toFixed(2),
      temp: +(baseTemp+wobble+(Math.random()-0.5)*0.6).toFixed(1),
      salinity: +(18+wobble*1.5+(Math.random()-0.5)).toFixed(1),
      transparency: +(35+wobble*4+(Math.random()-0.5)*5).toFixed(0),
      ammonia: +Math.max(0,(0.05+(Math.random()-0.4)*0.06)).toFixed(3),
      nitrite: +Math.max(0,(0.04+(Math.random()-0.4)*0.05)).toFixed(3),
      alkalinity: +(120+wobble*8+(Math.random()-0.5)*10).toFixed(0),
    });
  }
  return arr;
}

function genFeed(pondId, base) {
  const arr = [];
  for (let i = 13; i >= 0; i--) {
    arr.push({
      _id: `feed-${pondId}-${i}`, id: `${pondId}-${i}`, date: daysAgo(i), pond: pondId,
      feedType: base>200?'Finisher (2.5mm)':base>120?'Grower (1.5mm)':'Starter (0.5mm)',
      kg: +(base+(Math.random()-0.3)*12).toFixed(1), times: 'Pagi/Tengahari/Petang/Malam'
    });
  } return arr;
}

function genGrowth(pondId, startW, adg) {
  const arr = []; let w = startW;
  for (let wk=1; wk<=8; wk++) {
    w=+(w+adg*7*(0.9+Math.random()*0.2)).toFixed(2);
    arr.push({ _id:`gr-${pondId}-w${wk}`, id:`${pondId}-w${wk}`, week:wk, date:daysAgo((8-wk)*7), pond:pondId,
      abw:w, length:+(Math.pow(w,0.32)*5.2).toFixed(1), target:+(startW+adg*7*wk).toFixed(2), adg:+adg.toFixed(3) });
  } return arr;
}

const seeds = {
  ponds: [
    {_id:'p1',name:'Kolam A1',area:0.5,depth:1.2,status:'Aktif',species:'Udang Vannamei (L. vannamei)',stock:50000,stockDate:'2026-01-15',harvestEst:'2026-04-20'},
    {_id:'p2',name:'Kolam A2',area:0.5,depth:1.0,status:'Persediaan',species:'Udang Harimau (P. monodon)',stock:0,stockDate:'',harvestEst:''},
    {_id:'p3',name:'Kolam B1',area:0.8,depth:1.2,status:'Aktif',species:'Udang Vannamei (L. vannamei)',stock:80000,stockDate:'2026-02-01',harvestEst:'2026-05-15'},
    {_id:'p4',name:'Kolam B2',area:0.8,depth:1.0,status:'Kosong',species:'',stock:0,stockDate:'',harvestEst:''},
    {_id:'p5',name:'Kolam C1',area:1.0,depth:1.5,status:'Tuaian',species:'Udang Vannamei (L. vannamei)',stock:100000,stockDate:'2025-12-01',harvestEst:'2026-03-10'},
  ],
  water: [],
  seed: [
    {_id:'sr1',pond:'Kolam A1',species:'Udang Vannamei (L. vannamei)',quantity:50000,date:'2026-01-15',supplier:'Benur Sejahtera',cost:2500},
  ],
  feed: [
    {_id:'f1',date:'2026-01-16',pond:'Kolam A1',feedType:'5001',quantity:50,method:'Tabur'},
    {_id:'f2',date:'2026-01-16',pond:'Kolam B1',feedType:'5002',quantity:80,method:'Feeder'},
  ],
  feedstock: [
    {_id:'fs1',item:'Feed 5001',unit:'kg',qty:2000,price:185},
    {_id:'fs2',item:'Feed 5002',unit:'kg',qty:1500,price:175},
    {_id:'fs3',item:'Feed 5003',unit:'kg',qty:1000,price:165},
    {_id:'fs4',item:'Feed 7704',unit:'kg',qty:800,price:195},
    {_id:'fs5',item:'Feed 7705',unit:'kg',qty:600,price:188},
    {_id:'fs6',item:'Feed 7706',unit:'kg',qty:400,price:182},
    {_id:'fs7',item:'Hydrated Lime',unit:'kg',qty:500,price:45},
    {_id:'fs8',item:'Calcium Carbonate',unit:'kg',qty:300,price:55},
    {_id:'fs9',item:'Molasses',unit:'L',qty:200,price:12},
  ],
  growth: [],
  health: [],
  medstock: [],
  harvest: [],
};

async function upsert(key, data) {
  const body = JSON.stringify({id:key, data});
  return new Promise((resolve, reject) => {
    const req = https.request(SUPABASE_URL+'/rest/v1/farm_data', {
      method:'POST',
      headers:{
        'apikey': ANON_KEY, 'Authorization': 'Bearer '+ANON_KEY,
        'Content-Type':'application/json', 'Content-Length': Buffer.byteLength(body),
        'Prefer': 'resolution=merge-duplicates,return=representation'
      }
    }, res => {
      let d=''; res.on('data',c=>d+=c);
      res.on('end',()=>{ if(res.statusCode<300){ console.log('  ✅ '+key+': '+data.length+' rekod'); resolve(); }
        else reject('HTTP '+res.statusCode+' '+d.slice(0,100)); });
    });
    req.on('error', reject);
    req.write(body);
    req.end();
  });
}

(async ()=>{
  console.log('🌊 Seeding data ke Supabase...\n');
  for(const [key,data] of Object.entries(seeds)){
    try{ await upsert(key,data); }catch(e){ console.error('  ❌ '+key+': '+e); }
  }
  console.log('\n✅ Selesai! Refresh https://nephicrosis-boop.github.io/UdangPro/');
})();
