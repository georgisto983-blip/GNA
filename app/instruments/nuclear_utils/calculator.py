"""Nuclear physics calculation functions.

Constants and formulae used throughout:
    N_A  = 6.02214076e23  mol^-1   (Avogadro, CODATA 2018)
    e    = 1.602176634e-19 C        (elementary charge, exact SI 2019)
    c    = 299792458 m/s            (speed of light, exact)
    u    = 931.494 MeV/c^2          (atomic mass unit, AME 2020)

Nuclear radius conventions (two distinct r₀ values are used):
    R0_FM = 1.2 fm   — nuclear matter radius parameter, most widely quoted
                       value from modern electron-scattering measurements
                       (Angeli & Marinova, At.Data Nucl.Data Tables 99(2013)69;
                        PDG 2022; Blatt & Weisskopf; Krane "Introductory
                        Nuclear Physics").  R_matter = 1.2 × A^(1/3) fm.

    For the Coulomb barrier (touching-spheres approximation), the default
    r₀ = 1.35 fm is used instead, because it gives better empirical
    agreement with measured sub-barrier fusion cross sections and matches
    LISE++ / PACE4 calculations.  This larger value accounts for the
    nuclear surface diffuseness: the nuclear interaction begins before
    hard-sphere contact.  r₀_Coulomb = 1.35 fm is standard in reaction
    codes (see Bass 1980 Nucl.Phys. A231).
"""

import math
from fractions import Fraction
from itertools import product

# ── Physical constants (SI) ──
N_AVOGADRO = 6.02214076e23   # mol^-1
E_CHARGE = 1.602176634e-19   # C
C_LIGHT = 299_792_458        # m/s
AMU_MEV = 931.494             # MeV/c^2
R0_FM = 1.2                   # fm — nuclear matter radius (PDG/AME value)


# ═══════════════════════════════════════════════════════
#  1. Beam-on-target yield  (from Smetki.ods logic)
# ═══════════════════════════════════════════════════════

def beam_yield(
    beam_current_pnA,
    cross_section_mb,
    target_thickness_mg_cm2,
    target_A,
    detector_efficiency=1.0,
    excitation_ratio=1.0,
    sorter_efficiency=1.0,
):
    """Calculate expected gamma-ray yield (counts/s) for a beam-on-target experiment.

    The yield formula is:
        Y = (I_c / e) * sigma * (d * N_A / A)
          × epsilon_det × ratio_exc × epsilon_sort

    where
        I_c    = beam current [pnA → A] (particle-nA)
        sigma  = reaction cross-section [mb → cm^2]
        d      = target areal density [mg/cm^2 → g/cm^2]
        A      = target mass number [g/mol]
        N_A    = Avogadro's number

    Parameters
    ----------
    beam_current_pnA : float
        Beam current in particle-nanoamperes.
    cross_section_mb : float
        Reaction cross-section in millibarns.
    target_thickness_mg_cm2 : float
        Target thickness in mg/cm^2.
    target_A : float
        Target mass number (g/mol).
    detector_efficiency : float
        Gamma-ray detector efficiency (0–1).
    excitation_ratio : float
        Fraction of the reaction populating the state of interest (0–1).
    sorter_efficiency : float
        Data sorting / trigger efficiency (0–1).

    Returns
    -------
    dict with 'per_second', 'per_hour', 'per_shift_8h'
    """
    I_A = beam_current_pnA * 1e-9                # pnA -> A
    sigma_cm2 = cross_section_mb * 1e-27          # mb -> cm^2
    d_g_cm2 = target_thickness_mg_cm2 * 1e-3      # mg/cm^2 -> g/cm^2

    particles_per_s = I_A / E_CHARGE
    target_atoms_per_cm2 = d_g_cm2 * N_AVOGADRO / target_A

    Y = (particles_per_s * sigma_cm2 * target_atoms_per_cm2
         * detector_efficiency * excitation_ratio * sorter_efficiency)

    return {
        "per_second": Y,
        "per_hour": Y * 3600,
        "per_shift_8h": Y * 3600 * 8,
    }


# ═══════════════════════════════════════════════════════
#  2. Coulomb barrier & nuclear radius
# ═══════════════════════════════════════════════════════

def nuclear_radius_fm(A):
    """R = r_0 * A^(1/3)  in femtometers."""
    return R0_FM * A ** (1.0 / 3.0)


def coulomb_barrier_MeV(Z1, A1, Z2, A2, r0_fm=1.35):
    """Coulomb barrier in MeV:
        V_C = k_e * Z1 * Z2 * e^2 / (R1 + R2)
    Uses k_e = 1.43996 MeV·fm (the Coulomb constant in natural units).

    The default r0 = 1.35 fm is standard for Coulomb-barrier estimates
    (as opposed to r0 = 1.25 fm for nuclear matter radii).
    """
    k_e = 1.43996  # MeV·fm
    R1 = r0_fm * A1 ** (1.0 / 3.0)
    R2 = r0_fm * A2 ** (1.0 / 3.0)
    return k_e * Z1 * Z2 / (R1 + R2)


# ═══════════════════════════════════════════════════════
#  3. Beam kinematics (non-relativistic)
# ═══════════════════════════════════════════════════════

def beam_beta_and_velocity(E_MeV, A):
    """Calculate beta = v/c and v [m/s] for a beam of mass A at energy E_MeV.

    Uses non-relativistic kinetic energy:
        E_k = 1/2 * m * v^2
        v = sqrt(2 * E_k / m)
        beta = v / c

    Parameters
    ----------
    E_MeV : float
        Kinetic energy in MeV.
    A : float
        Mass number (amu).

    Returns
    -------
    beta : float
        v/c (dimensionless).
    v_ms : float
        Velocity in m/s.
    """
    m_kg = A * AMU_MEV * 1e6 * E_CHARGE / (C_LIGHT ** 2)
    E_J = E_MeV * 1e6 * E_CHARGE
    v = math.sqrt(2 * E_J / m_kg)
    beta = v / C_LIGHT
    return beta, v


def recoil_velocity_two_body(E_MeV, A_beam, A_target):
    """Compound-nucleus recoil velocity (lab frame, assuming full momentum transfer).

    In fusion-evaporation at energies near the Coulomb barrier:
        p_CN = p_beam  (target at rest)
        v_CN = p_beam / m_CN
             = (A_beam / A_CN) * v_beam

    where A_CN = A_beam + A_target.

    Returns beta_CN, v_CN (m/s).
    """
    beta_beam, v_beam = beam_beta_and_velocity(E_MeV, A_beam)
    A_CN = A_beam + A_target
    v_CN = (A_beam / A_CN) * v_beam
    return v_CN / C_LIGHT, v_CN


# ═══════════════════════════════════════════════════════
#  4. Angular momentum coupling (J-value enumerator)
# ═══════════════════════════════════════════════════════

def enumerate_J_values(j_orbital, n_particles):
    """Enumerate all allowed total J for n identical nucleons in orbital j.

    Uses the angular momentum coupling rule:
        |j1 - j2| <= J <= j1 + j2
    applied iteratively for n particles, respecting the Pauli exclusion
    principle (seniority scheme): n identical fermions in a j-shell
    can couple to J = 0, 2, 4, ..., (2j-1) for even n, and
    J = j, j-2, ..., 1/2 for odd n=1; but for n > 1 the allowed J
    values follow from the antisymmetrization of the wave function.

    For the general case with n particles in a single-j shell, the
    allowed J values come from the seniority quantum number v:
      - v = 0: J = 0 (only for even n)
      - v = 1: J = j (only for odd n)
      - v = 2: J = 2, 4, ..., 2j-1  (the paired states)
      - higher v: more complex

    This function returns the allowed J values using the simple
    angular momentum coupling. For a rigorous treatment of identical
    fermions (antisymmetrization), the seniority scheme should be used.

    Parameters
    ----------
    j_orbital : str or Fraction
        Single-particle angular momentum, e.g. "9/2" or Fraction(9, 2).
    n_particles : int
        Number of particles (or holes) in the orbital.

    Returns
    -------
    sorted list of Fraction
        All distinct allowed J values, sorted ascending.
    """
    if isinstance(j_orbital, str):
        parts = j_orbital.split("/")
        if len(parts) == 2:
            j = Fraction(int(parts[0]), int(parts[1]))
        else:
            j = Fraction(int(parts[0]))
    else:
        j = Fraction(j_orbital)

    if n_particles == 0:
        return [Fraction(0)]

    if n_particles == 1:
        return [j]

    # Build m-scheme: each particle has m in {-j, -j+1, ..., j}
    m_values = [Fraction(-j.numerator + 2 * k, j.denominator)
                for k in range(int(2 * j) + 1)]

    # For identical fermions (Pauli): pick n distinct m-values
    from itertools import combinations
    configs = list(combinations(m_values, n_particles))

    # Total M for each configuration
    M_totals = sorted(set(sum(config) for config in configs), reverse=True)

    # Extract J values: for each M >= 0, the number of states with
    # J >= M equals the number of times M appears.
    M_counts = {}
    for config in configs:
        M = sum(config)
        M_counts[M] = M_counts.get(M, 0) + 1

    # J values from the M-scheme decomposition:
    # n(J) = count(M=J) - count(M=J+1)
    J_values = []
    M_positive = sorted([M for M in M_counts if M >= 0], reverse=True)

    for M in M_positive:
        n_at_M = M_counts.get(M, 0)
        n_at_M_plus_1 = M_counts.get(M + 1, 0)
        n_J = n_at_M - n_at_M_plus_1
        if n_J > 0:
            J_values.extend([M] * n_J)

    return sorted(set(J_values))


def enumerate_J_with_projections(j_orbital, n_particles):
    """Enumerate allowed J values with their m_j projection combinations.

    For each allowed J, finds all ways to pick n distinct m_j values
    (Pauli exclusion) from {-j, -j+1, ..., j} that sum to M = J.
    Combinations are sorted by highest projection first, then second, etc.

    Parameters
    ----------
    j_orbital : str or Fraction
        Single-particle angular momentum, e.g. "9/2".
    n_particles : int
        Number of particles (or holes) in the orbital.

    Returns
    -------
    list of (Fraction, list[tuple[Fraction, ...]])
        Sorted by increasing J. Each entry is (J, [combos]).
    """
    if isinstance(j_orbital, str):
        parts = j_orbital.split("/")
        if len(parts) == 2:
            j = Fraction(int(parts[0]), int(parts[1]))
        else:
            j = Fraction(int(parts[0]))
    else:
        j = Fraction(j_orbital)

    if n_particles == 0:
        return [(Fraction(0), [()])]

    if n_particles == 1:
        return [(j, [(j,)])]

    m_values = [Fraction(-j.numerator + 2 * k, j.denominator)
                for k in range(int(2 * j) + 1)]

    from itertools import combinations
    configs = list(combinations(m_values, n_particles))

    # Get allowed J values
    M_counts: dict[Fraction, int] = {}
    for config in configs:
        M = sum(config)
        M_counts[M] = M_counts.get(M, 0) + 1

    J_set: set[Fraction] = set()
    M_positive = sorted([M for M in M_counts if M >= 0], reverse=True)
    for M in M_positive:
        n_at_M = M_counts.get(M, 0)
        n_at_M_plus_1 = M_counts.get(M + 1, 0)
        n_J = n_at_M - n_at_M_plus_1
        if n_J > 0:
            J_set.add(M)

    # For each J, collect combos where sum(m_j) = J
    result = []
    for J in sorted(J_set):
        combos = [c for c in configs if sum(c) == J]
        # Sort each combo descending by value, then sort combos
        # by highest projection first, then second, etc.
        combos_sorted = sorted(
            [tuple(sorted(c, reverse=True)) for c in combos],
            reverse=True,
        )
        result.append((J, combos_sorted))

    return result


def shell_model_occupancy(Z, N):
    """Determine proton and neutron orbital occupancy in the nuclear shell model.

    Returns a description of which orbitals are being filled and
    how many particles/holes exist relative to closed shells.

    Shell closures (magic numbers): 2, 8, 20, 28, 50, 82, 126

    Orbitals filled in order (simplified, no deformation):
        28-50 shell: 1f5/2, 2p3/2, 2p1/2, 1g9/2
        50-82 shell: 1g7/2, 2d5/2, 2d3/2, 3s1/2, 1h11/2

    Returns
    -------
    dict with 'protons' and 'neutrons', each containing
    'particles_above_closure', 'holes_below_closure', 'shell_info'
    """
    magic = [2, 8, 20, 28, 50, 82, 126]

    # Orbitals between magic numbers (label, j, capacity=2j+1)
    shell_orbitals = {
        (28, 50): [
            ("1f₅/₂", "5/2", 6),
            ("2p₃/₂", "3/2", 4),
            ("2p₁/₂", "1/2", 2),
            ("1g₉/₂", "9/2", 10),
        ],
        (50, 82): [
            ("1g₇/₂", "7/2", 8),
            ("2d₅/₂", "5/2", 6),
            ("2d₃/₂", "3/2", 4),
            ("3s₁/₂", "1/2", 2),
            ("1h₁₁/₂", "11/2", 12),
        ],
        (82, 126): [
            ("1h₉/₂", "9/2", 10),
            ("2f₇/₂", "7/2", 8),
            ("2f₅/₂", "5/2", 6),
            ("3p₃/₂", "3/2", 4),
            ("3p₁/₂", "1/2", 2),
            ("1i₁₃/₂", "13/2", 14),
        ],
    }

    def analyze(nucleon_count, label):
        # Find which shell we're in
        below = 0
        above_closure = 0
        for i, m in enumerate(magic):
            if nucleon_count <= m:
                above_closure = nucleon_count - (magic[i - 1] if i > 0 else 0)
                lower = magic[i - 1] if i > 0 else 0
                upper = m
                break
        else:
            lower = magic[-1]
            upper = None
            above_closure = nucleon_count - lower

        shell_key = (lower, upper) if upper else None
        orbitals = shell_orbitals.get(shell_key, [])

        # Fill orbitals
        remaining = above_closure
        filled = []
        active_orbital = None
        for orb_name, orb_j, capacity in orbitals:
            if remaining <= 0:
                break
            n_in = min(remaining, capacity)
            remaining -= n_in
            filled.append({
                "orbital": orb_name,
                "j": orb_j,
                "occupancy": n_in,
                "capacity": capacity,
            })
            if n_in < capacity:
                active_orbital = filled[-1]

        # Also compute holes from upper closure
        holes_from_top = (upper or 0) - nucleon_count if upper else 0

        return {
            "count": nucleon_count,
            "lower_closure": lower,
            "upper_closure": upper,
            "particles_above_closure": above_closure,
            "holes_below_closure": holes_from_top,
            "filled_orbitals": filled,
            "active_orbital": active_orbital,
        }

    return {
        "protons": analyze(Z, "protons"),
        "neutrons": analyze(N, "neutrons"),
    }
