import { describe, it, expect } from 'vitest';
import { formatGovtFees } from '../utils/formatters';

describe('formatGovtFees formatter utility', () => {
  it('formats positive numbers in Indian currency format', () => {
    expect(formatGovtFees(1500)).toBe('₹1,500');
    expect(formatGovtFees(100000)).toBe('₹1,00,000');
    expect(formatGovtFees(25000.5)).toBe('₹25,000.5');
  });

  it('formats numeric string inputs properly', () => {
    expect(formatGovtFees('1500')).toBe('₹1,500');
    expect(formatGovtFees('50000')).toBe('₹50,000');
  });

  it('uses formatted string when provided', () => {
    expect(formatGovtFees(5000, '₹5,000')).toBe('₹5,000');
    expect(formatGovtFees(0, '₹0')).toBe('₹0');
  });

  it('renders ₹0 when amount is 0', () => {
    expect(formatGovtFees(0)).toBe('₹0');
    expect(formatGovtFees('0')).toBe('₹0');
  });

  it('renders "-" when amount is null, undefined, empty, or NaN', () => {
    expect(formatGovtFees(null)).toBe('-');
    expect(formatGovtFees(undefined)).toBe('-');
    expect(formatGovtFees('')).toBe('-');
    expect(formatGovtFees('abc')).toBe('-');
  });

  it('supports passing an object with govt_fees or aliases', () => {
    expect(formatGovtFees({ govt_fees: 7500 })).toBe('₹7,500');
    expect(formatGovtFees({ govt_fee: 3000 })).toBe('₹3,000');
    expect(formatGovtFees({ government_fees: 12000 })).toBe('₹12,000');
    expect(formatGovtFees({ govt_fees: 0 })).toBe('₹0');
    expect(formatGovtFees({ govt_fees: null })).toBe('-');
    expect(formatGovtFees({ formatted_govt_fees: '₹4,500' })).toBe('₹4,500');
  });
});

