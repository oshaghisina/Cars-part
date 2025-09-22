/**
 * Persian Number Utilities
 * Convert Western Arabic numerals to Persian/Eastern Arabic numerals
 */

// Persian/Eastern Arabic numerals
const persianDigits = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹'];

/**
 * Convert Western Arabic numerals to Persian numerals
 * @param {string|number} input - The input string or number to convert
 * @returns {string} - String with Persian numerals
 */
export function toPersianNumbers(input) {
  if (input === null || input === undefined) return '';
  
  const str = String(input);
  return str.replace(/[0-9]/g, (digit) => persianDigits[parseInt(digit)]);
}

/**
 * Format number with Persian numerals and proper RTL formatting
 * @param {number} number - The number to format
 * @param {string} suffix - Optional suffix (e.g., 'محصول', 'تومان')
 * @returns {string} - Formatted string with Persian numerals
 */
export function formatPersianNumber(number, suffix = '') {
  if (number === null || number === undefined) return '';
  
  const persianNumber = toPersianNumbers(number.toLocaleString('fa-IR'));
  return suffix ? `${persianNumber} ${suffix}` : persianNumber;
}

/**
 * Format price with Persian numerals
 * @param {number} price - The price to format
 * @param {string} currency - Currency symbol (default: 'تومان')
 * @returns {string} - Formatted price with Persian numerals
 */
export function formatPersianPrice(price, currency = 'تومان') {
  if (price === null || price === undefined) return '';
  
  const persianPrice = toPersianNumbers(price.toLocaleString('fa-IR'));
  return `${persianPrice} ${currency}`;
}
