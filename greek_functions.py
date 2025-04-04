# -*- coding: utf-8 -*-
"""
Created on Tue Apr  1 19:48:45 2025

@author: Nicolas 
"""

# greek_functions.py
import numpy as np
from scipy.stats import norm

def d1(S, K, T, r, sigma):
    return (np.log(S/K) + (r + sigma**2 / 2.) * T) / (sigma * np.sqrt(T))

def d2(S, K, T, r, sigma):
    return d1(S, K, T, r, sigma) - sigma * np.sqrt(T)

def put_price(S, K, T, r, sigma):
    return K * np.exp(-r*T) * norm.cdf(-d2(S, K, T, r, sigma)) - S * norm.cdf(-d1(S, K, T, r, sigma))

def delta_put(S, K, T, r, sigma):
    return norm.cdf(d1(S, K, T, r, sigma)) - 1

def rho_put(S, K, T, r, sigma):
    return -K * T * np.exp(-r * T) * norm.cdf(-d2(S, K, T, r, sigma))

def gamma(S, K, T, r, sigma):
    return norm.pdf(d1(S, K, T, r, sigma)) / (S * sigma * np.sqrt(T))

def vega(S, K, T, r, sigma):
    return S * norm.pdf(d1(S, K, T, r, sigma)) * np.sqrt(T)

def theta_put(S, K, T, r, sigma):
    term1 = - (S * norm.pdf(d1(S, K, T, r, sigma)) * sigma) / (2 * np.sqrt(T))
    term2 = r * K * np.exp(-r * T) * norm.cdf(-d2(S, K, T, r, sigma))
    return term1 + term2
