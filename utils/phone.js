function validateAndCleanPhone(phone) {
  if (!phone) return { valid: false, error: 'Telefone ausente', num: '' };
  let cleaned = String(phone).replace(/\D/g, '');
  if (cleaned.startsWith('550')) {
    cleaned = '55' + cleaned.substring(3);
  }
  if (cleaned.length === 10 || cleaned.length === 11) {
    cleaned = '55' + cleaned;
  }
  if (cleaned.startsWith('55') && cleaned.length === 12) {
    const firstDig = cleaned.charAt(4);
    if (['9', '8', '7'].includes(firstDig)) {
      cleaned = cleaned.substring(0, 4) + '9' + cleaned.substring(4);
    }
  }
  if (cleaned.length !== 12 && cleaned.length !== 13) {
    return { valid: false, error: 'Tamanho invalido (' + cleaned.length + ' digitos)', num: cleaned };
  }
  if (cleaned.startsWith('55') && cleaned.length === 12) {
    const firstDig = cleaned.charAt(4);
    if (['2', '3', '4', '5'].includes(firstDig)) {
      return { valid: false, error: 'Telefone Fixo (Sem WhatsApp ativo)', num: cleaned };
    }
  }
  return { valid: true, num: cleaned };
}

module.exports = { validateAndCleanPhone };
