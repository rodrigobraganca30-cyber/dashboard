const { createClient } = require('redis');
const { log } = require('./logger');

const redis = createClient({ url: process.env.REDIS_URL || 'redis://localhost:6379' });

redis.connect().then(() => log('info', 'Redis conectado'))
  .catch(e => log('error', 'Erro ao conectar Redis', { error: e.message }));

redis.on('error', e => log('error', 'Redis error', { error: e.message }));

// Helpers Redis
const KEY_STATUS   = (id) => `agenda:status:${id}`;
const KEY_MSGS     = (phone) => `agenda:msgs:${phone}`;
const KEY_PHONE_ID = (phone) => `agenda:phone2id:${phone}`;
const KEY_TEMPLATES = 'agenda:templates';
const KEY_CAMPAIGNS = 'agenda:campaigns';
const KEY_UNREAD   = (phone) => `agenda:unread:${phone}`;
const KEY_CLIENTS  = 'agenda:clients';
const KEY_BTN_CFG  = 'agenda:button-config';

async function scanKeys(pattern, count = 200) {
  const keys = [];
  let cursor = '0';
  do {
    const result = await redis.scan(cursor, { MATCH: pattern, COUNT: count });
    cursor = result.cursor.toString();
    keys.push(...result.keys);
  } while (cursor !== '0');
  return keys;
}

module.exports = {
  redis,
  KEY_STATUS,
  KEY_MSGS,
  KEY_PHONE_ID,
  KEY_TEMPLATES,
  KEY_CAMPAIGNS,
  KEY_UNREAD,
  KEY_CLIENTS,
  KEY_BTN_CFG,
  scanKeys
};
