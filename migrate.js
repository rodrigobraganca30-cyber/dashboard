const { createClient } = require('redis');
const { Pool } = require('pg');

const redis = createClient({ url: process.env.REDIS_URL || 'redis://redis:6379' });
redis.on('error', err => console.log('Redis Error', err));

const pgPool = new Pool({
  connectionString: process.env.DATABASE_URL || 'postgresql://agenda_user:svoboda2025@agenda-db:5432/agenda'
});

async function migrate() {
  await redis.connect();
  console.log('Connected to Redis and Postgres.');

  // 1. Migrar Clientes
  const clientsRaw = await redis.get('agenda:clients');
  if (clientsRaw) {
    const clients = JSON.parse(clientsRaw);
    console.log(`Migrating ${clients.length} clients...`);
    for (const c of clients) {
      try {
        await pgPool.query(`
          INSERT INTO clientes (id, nome, telefone, data, cidade, horario, endereco, tipo, fase, status_ofs, status_atual)
          VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
          ON CONFLICT (id) DO NOTHING
        `, [c.id, c.nome, c.telefone, c.data, c.cidade, c.horario, c.endereco, c.tipo, c.fase, c.status || 'Pendente', 'pendente']);
      } catch (e) {
        console.error(`Error inserting client ${c.id}:`, e.message);
      }
    }
  }

  // 2. Migrar Status
  const statusKeys = await redis.keys('agenda:status:*');
  console.log(`Migrating ${statusKeys.length} statuses...`);
  for (const key of statusKeys) {
    const clientId = key.replace('agenda:status:', '');
    const statusRaw = await redis.get(key);
    if (statusRaw) {
      try {
        const s = JSON.parse(statusRaw);
        await pgPool.query(`
          UPDATE clientes SET status_atual = $1, obs_status = $2 
          WHERE id = $3
        `, [s.status, s.obs, clientId]);
      } catch (e) {
        console.error(`Error updating status for ${clientId}:`, e.message);
      }
    }
  }

  // 3. Migrar Mensagens
  const msgKeys = await redis.keys('agenda:msgs:*');
  console.log(`Migrating ${msgKeys.length} message threads...`);
  for (const key of msgKeys) {
    const phone = key.replace('agenda:msgs:', '');
    const msgRaw = await redis.get(key);
    if (msgRaw) {
      try {
        const msgs = JSON.parse(msgRaw);
        for (const msg of msgs) {
          await pgPool.query(`
            INSERT INTO mensagens (telefone, remetente, texto, timestamp, instancia, is_auto) 
            VALUES ($1, $2, $3, $4, $5, $6)
          `, [phone, msg.from, msg.text, msg.ts, msg.instance || null, msg.auto || false]);
        }
      } catch (e) {
        // Ignora duplicatas se rodar duas vezes
      }
    }
  }

  // 4. Migrar Blacklist
  const blacklist = await redis.sMembers('agenda:blacklist');
  console.log(`Migrating ${blacklist.length} blacklist entries...`);
  for (const phone of blacklist) {
    try {
      await pgPool.query(`
        INSERT INTO blacklist (telefone, motivo) VALUES ($1, $2)
        ON CONFLICT (telefone) DO NOTHING
      `, [phone, 'Migrado do Redis']);
    } catch(e) {}
  }

  console.log('Migration completed successfully!');
  process.exit(0);
}

migrate().catch(console.error);
