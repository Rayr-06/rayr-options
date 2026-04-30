"""
Options Pricing Engine - Black-Scholes Model
"""
import numpy as np
from scipy.stats import norm

class OptionsEngine:
    def __init__(self, risk_free_rate=0.05):
        self.risk_free_rate = risk_free_rate
    
    def find_strike_for_delta(self, S, target_delta, T, r, sigma, option_type='put'):
        """Find strike price for target delta using binary search"""
        K_low = S * 0.5 if option_type == 'put' else S * 1.0
        K_high = S * 1.0 if option_type == 'put' else S * 1.5
        
        for _ in range(50):
            K_mid = (K_low + K_high) / 2
            d1 = (np.log(S / K_mid) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
            delta = abs(norm.cdf(d1) - 1) if option_type == 'put' else norm.cdf(d1)
            
            if abs(delta - target_delta) < 0.01:
                return K_mid
            
            if delta < target_delta:
                K_low = K_mid if option_type == 'put' else K_high
            else:
                K_high = K_mid if option_type == 'put' else K_low
        
        return K_mid
    
    def black_scholes_price(self, S, K, T, r, sigma, option_type='put'):
        """Calculate option price using Black-Scholes"""
        if T <= 0:
            return max(0, K - S) if option_type == 'put' else max(0, S - K)
        
        d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        
        if option_type == 'put':
            return K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
        else:
            return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
