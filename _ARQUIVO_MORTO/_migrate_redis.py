#!/usr/bin/env python3
"""Migra chaves Redis de 12 digitos (sem 9) para 13 digitos (com 9)"""
import redis
import json

r = redis.from_url("redis://localhost:6379")

# 1. Migrar agenda:msgs:*
keys = r.keys("agenda:msgs:*")
migrated = 0
merged = 0
for key in keys:
    phone = key.decode().replace("agenda:msgs:", "")
    digits = ''.join(c for c in phone if c.isdigit())
    
    if len(digits) == 12 and digits.startswith("55"):
        # Adicionar o 9 apos o DDD (posicao 4)
        correct = digits[:4] + "9" + digits[4:]
        correct_key = f"agenda:msgs:{correct}"
        
        old_msgs = json.loads(r.get(key) or "[]")
        existing = json.loads(r.get(correct_key) or "[]")
        
        if existing:
            # Mesclar: juntar + ordenar por timestamp + deduplicar
            all_msgs = existing + old_msgs
            seen = set()
            unique = []
            for m in all_msgs:
                sig = f"{m.get('from','')}{m.get('text','')}{m.get('ts',0)}"
                if sig not in seen:
                    seen.add(sig)
                    unique.append(m)
            unique.sort(key=lambda x: x.get("ts", 0))
            r.set(correct_key, json.dumps(unique))
            r.delete(key)
            merged += 1
            print(f"  MERGED: {phone} -> {correct} ({len(old_msgs)} + {len(existing)} = {len(unique)} msgs)")
        else:
            # Renomear
            r.rename(key, correct_key)
            migrated += 1
            print(f"  RENAMED: {phone} -> {correct} ({len(old_msgs)} msgs)")

print(f"\n[OK] msgs: {migrated} renomeadas, {merged} mescladas")

# 2. Migrar agenda:phone2id:*
p2i_keys = r.keys("agenda:phone2id:*")
p2i_migrated = 0
for key in p2i_keys:
    phone = key.decode().replace("agenda:phone2id:", "")
    digits = ''.join(c for c in phone if c.isdigit())
    if len(digits) == 12 and digits.startswith("55"):
        correct = digits[:4] + "9" + digits[4:]
        correct_key = f"agenda:phone2id:{correct}"
        if not r.exists(correct_key):
            r.rename(key, correct_key)
        else:
            r.delete(key)
        p2i_migrated += 1

print(f"[OK] phone2id: {p2i_migrated} migradas")

# 3. Migrar agenda:unread:*
ur_keys = r.keys("agenda:unread:*")
ur_migrated = 0
for key in ur_keys:
    phone = key.decode().replace("agenda:unread:", "")
    digits = ''.join(c for c in phone if c.isdigit())
    if len(digits) == 12 and digits.startswith("55"):
        correct = digits[:4] + "9" + digits[4:]
        correct_key = f"agenda:unread:{correct}"
        old_val = r.get(key)
        existing_val = r.get(correct_key)
        if existing_val:
            total = int(old_val or 0) + int(existing_val or 0)
            r.set(correct_key, str(total))
        else:
            r.rename(key, correct_key)
        r.delete(key) if r.exists(key) else None
        ur_migrated += 1

print(f"[OK] unread: {ur_migrated} migradas")

# 4. Verificar: contar chaves de 12 digitos restantes
remaining = 0
for key in r.keys("agenda:msgs:55*"):
    phone = key.decode().replace("agenda:msgs:", "")
    if len(phone) == 12:
        remaining += 1

print(f"\n[RESULTADO] Chaves orfas restantes: {remaining}")
print("[SUCESSO] Migracao concluida!")
