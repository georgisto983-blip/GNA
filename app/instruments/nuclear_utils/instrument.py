"""Nuclear Utilities — shared library module.

This package provides shared physics code (calculator.py, pace4_parser.py)
and the individual UI panels (ui/) used by the separate instruments:
  beam_yield, kinematics, j_coupling, pace4

This module does NOT register as a sidebar instrument; it exists only as
a shared dependency for the instruments listed above.
"""
# No create_instrument() — intentionally not registered as sidebar instrument.
