# Reviewer Guide

## One-sentence summary

This project abstracts a broader interactive-agent/game-AI state architecture into a clean-room symbolic estimator.

## What is new

The contribution is not the variance inequality itself. The contribution is the reduction from checked symbolic records to a finite bounded estimator with explicit assumptions.

## Why this matters

Uncontrolled text summaries make long-term behavior hard to audit. This artifact separates records, constraints, committed state, and downstream measurement.

## What to review

1. Is the reduction credible?
2. Are the assumptions explicit enough?
3. Is the synthetic convergence experiment a reasonable next step?
