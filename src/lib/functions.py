import numpy as np
from scipy.special import erfc, gammaln


def resolution(x, p0, p1, p2, b):
    """
    Resolution function.
    """
    residuals = np.sqrt(
        np.power(p2, 2) + np.power(p1 / np.sqrt(x - b), 2) + np.power(p0 / (x - b), 2)
    )
    residuals[np.isnan(residuals)] = 0
    residuals[np.isinf(residuals)] = 0
    return residuals


def gaussian(x, a, b, c):
    return a * np.exp(-0.5 * ((x - b) / c) ** 2)


def gaussian_train(x, *params):
    """
    Sum of an arbitrary number of Gaussians, each described by an
    (amplitude, mean, sigma) triplet in `params`.
    """
    total = np.zeros_like(np.asarray(x, dtype=float))
    for a, b, c in zip(params[0::3], params[1::3], params[2::3]):
        total = total + gaussian(x, a, b, c)
    return total


def vinogradov_crosstalk(x, lam, ct):
    """
    Generalized Poisson (Vinogradov) distribution used to fit SiPM optical
    crosstalk PE spectra: `lam` is the mean number of primary fired cells and
    `ct` is the branching (crosstalk) probability, both from the Poisson
    process being fed into a Borel branching process.
    """
    x = np.asarray(x, dtype=float)
    mu = lam + x * ct
    log_p = np.log(lam) + (x - 1) * np.log(mu) - mu - gammaln(x + 1)
    return np.exp(log_p)


def vinogradov_crosstalk_truncated(x, lam, ct):
    """
    `vinogradov_crosstalk` renormalized over the discrete PE range spanned by
    `x` (0 to the observed max PE). Use this when the measured PE histogram
    itself is truncated to a finite range (e.g. by the charge/ADC window),
    so its density only sums to 1 over the visible bins rather than over the
    full infinite support of the underlying distribution.
    """
    x = np.asarray(x, dtype=float)
    n_max = int(np.round(np.max(x)))
    n = np.arange(0, n_max + 1)
    norm = vinogradov_crosstalk(n, lam, ct).sum()
    return vinogradov_crosstalk(x, lam, ct) / norm


def exp_gauss_component(t, sig, amp, tau, phi):
    """
    Single Gaussian-smeared-exponential pulse component:
    A * exp(-(t-phi)/tau) * exp(-sig**2/(2*tau**2)) * erfc((phi-t)/(sqrt(2)*sig) + sig/(sqrt(2)*tau))
    i.e. an exponential decay of time constant `tau` starting at `phi`,
    convolved with a Gaussian of width `sig` representing detector timing
    jitter.
    """
    return (
        amp
        * np.exp(-(t - phi) / tau)
        * np.exp(-(sig**2) / (2 * tau**2))
        * erfc((phi - t) / (np.sqrt(2) * sig) + sig / (np.sqrt(2) * tau))
    )


def scintillation_pulse(t, ped, phi, sig1, amp1, tau1, sig2, amp2, tau2):
    """
    Scintillation pulse-shape model: h(t) = PED + sum_{i=1,2} A_i exp(-(t-phi)/tau_i)
    exp(-sig_i**2/(2*tau_i**2)) erfc((phi-t)/(sqrt(2)*sig_i) + sig_i/(sqrt(2)*tau_i)),
    a pedestal plus two Gaussian-smeared-exponential components (fast + slow
    scintillation decay) sharing a common onset time `phi`.
    """
    return (
        ped
        + exp_gauss_component(t, sig1, amp1, tau1, phi)
        + exp_gauss_component(t, sig2, amp2, tau2, phi)
    )


def scintillation_quenched_pulse(
    t, ped, phi, sig, kq, amp_s, amp_t, tau_s, tau_t, a_st_ratio=None, alpha=None
):
    """
    Scintillation pulse-shape model that extracts the N2 quenching
    coefficient `kq` while leaving the two components' amplitudes free to
    fit, so the doubly-corrected (quenched and absorption-corrected)
    amplitude ratio A''_S/A''_T (needed for the purity absorption correction
    alpha, Eq. absorption_correction) comes directly from the fit rather than
    being forced through the quenching-only relation of Eq. quenching (single
    primes: A'_i = A_i/(1+tau_i*kq), pure quenching from the truth A_i) --
    the discrepancy between that quenching-only prediction and this fit's
    actual amplitudes is exactly the absorption effect alpha is meant to
    capture:

        1/tau'_i = 1/tau_i + kq
        h(t) = ped + sum_{i in {s,t}} amp_i exp(-(t-phi)/tau'_i)
               exp(-sig**2/(2*tau'_i**2)) erfc((phi-t)/(sqrt(2)*sig) + sig/(sqrt(2)*tau'_i))

    `tau_s`, `tau_t` are held fixed at published "truth" alpha-scintillation
    time constants (e.g. Hitachi et al.); `ped`, `phi`, `sig`, `kq`, `amp_s`
    (A'''_S), `amp_t` (A'''_T) are the free fit parameters -- `kq` sets both
    quenched time constants simultaneously, while `amp_s`/`amp_t` are
    independent.

    `amp_s`/`amp_t` (A'''_S, A'''_T) are h(t)'s raw exponential prefactors,
    so they are not themselves the doubly-corrected amplitude fractions
    A''_i (which share the same normalization as the truth A_S/A_T):
    recovering those needs A''_i = amp_i * tau'_i (undoing the a_i/tau_i
    prefactor convention of Eq. scintillation_profile). `a_st_ratio` is
    A''_{S/T} = A''_S/A''_T, used directly in Eq. absorption_correction
    (with beta = (1+tau_t*kq)/(1+tau_s*kq)) to solve for the absorption
    correction `alpha`. Both are passed through only for display in the fit
    legend and not used in the pulse shape itself.
    """
    tau_s_q = 1.0 / (1.0 / tau_s + kq)
    tau_t_q = 1.0 / (1.0 / tau_t + kq)
    return (
        ped
        + exp_gauss_component(t, sig, amp_s, tau_s_q, phi)
        + exp_gauss_component(t, sig, amp_t, tau_t_q, phi)
    )


def scintillation_quenched_pulse_hitachi(
    t, ped, phi, sig, kq, amp_s, amp_t, a_st_ratio=None, alpha=None
):
    """
    `scintillation_quenched_pulse` with tau_s, tau_t hardcoded to Hitachi et
    al.'s published alpha-scintillation time constants (Table
    theory_scintillation: tau_S = 7.1 ns, tau_T = 1.66 us) instead of taking
    them as fit-storage parameters -- they are fixed truth inputs, not fit
    quantities, so they don't need to appear alongside the actual fit
    parameters wherever this function's Params are stored/displayed.
    """
    return scintillation_quenched_pulse(
        t, ped, phi, sig, kq, amp_s, amp_t, 7.1e-9, 1.66e-6, a_st_ratio, alpha
    )


def purity_pulse(t, ped, phi, sig, amp, tau_l):
    """
    Single Gaussian-smeared-exponential pulse plus pedestal, as used for LAr
    purity-monitor PMT waveform fits: h(t) = PED + A exp(-(t-phi)/tau_L)
    exp(-sig**2/(2*tau_L**2)) erfc((phi-t)/(sqrt(2)*sig) + sig/(sqrt(2)*tau_L)).
    `tau_L` is the observed (impurity-quenched) long/triplet scintillation
    decay constant used as the purity figure of merit.
    """
    return ped + exp_gauss_component(t, sig, amp, tau_l, phi)


def purity_pulse_response_convolved(t, phi, amp_fast, amp_slow, tau_slow):
    """
    LAr purity-monitor full-waveform model: a fast (singlet, tau fixed at
    6 ns) plus a slow (triplet) LAr scintillation exponential, both starting
    at onset time `phi` and convolved with (a) a Gaussian representing the
    PMT/electronics response and (b) a fixed multi-exponential instrumental
    response kernel capturing non-exponential tail behavior not accounted
    for by the Gaussian alone. A naive single-exponential fit to the raw
    waveform tail is biased by this kernel's long (~3.5 us) delayed
    component, which is comparable in scale to tau_slow and therefore not
    negligible.

    The instrumental response kernel is modeled as the sum of three
    exponential components. Their time constants and weights are NOT a
    literature value for this apparatus (an earlier version borrowed
    Segreto et al.'s TPB wavelength-shifter response constants, which do
    not apply here since this setup has no TPB); instead they were
    calibrated by letting all three (tau, weight) pairs float in a fit to
    this same purity-monitor waveform, seeded from the TPB values only as a
    starting guess. That calibration converged to 8 ns/60%, 45 ns/32%,
    2497 ns/8%, improving chi2/ndof to 3.26 (vs 3.97 for a same-shape kernel
    fixed at the seed TPB values) -- these calibrated values are what is
    fixed below. A fourth, much smaller (~2%) component at 309 ns was
    tested during the earlier TPB-seeded exploration and dropped: letting
    all four weights float converges the smallest one to ~0 with no change
    in fit quality. Dropping any of the remaining three components, in
    contrast, roughly doubles chi2/ndof and shifts tau_slow well away from
    its 3-component value, so all three are load-bearing.

    `t`, `phi` are in seconds. The PMT/electronics Gaussian width (3 ns) and
    the LAr fast/singlet time constant (6 ns) are fixed rather than free,
    but both are independently confirmed rather than merely assumed: with
    the calibrated three-component kernel above (unlike the earlier
    TPB-seeded one, whose fastest ~5 ns component partly overlapped these),
    freeing either one converges tightly back to its fixed value (sigma to
    2.94+-0.03 ns, tau_fast to 5.98+-0.83 ns) with no improvement in
    chi2/ndof -- so fixing them costs nothing and keeps two fewer
    correlated parameters in the legend. Dropping the Gaussian convolution
    entirely, by contrast, does measurably worsen the fit (chi2/ndof 3.43
    vs 3.26), so it is needed. `phi` (the pulse onset time) is needed even
    though the tail-only fit didn't require one: without it, the symmetric
    Gaussian smearing leaks part of the sharp prompt peak backward past
    t=0, which collides with the data's genuine pre-trigger baseline there.
    """
    from scipy.signal import fftconvolve

    t = np.asarray(t, dtype=float)
    dt = 1e-9
    grid_max = 20e-6
    grid = np.arange(0, grid_max, dt)
    response_taus = np.array([8.1077e-9, 45.0075e-9, 2497.1606e-9])
    response_abundances = np.array([0.60440, 0.31578, 0.07982])
    response_abundances = response_abundances / response_abundances.sum()
    sigma_fixed = 3e-9
    tau_fast = 6e-9

    response_kernel = np.zeros_like(grid)
    for tau, ab in zip(response_taus, response_abundances):
        response_kernel += ab / tau * np.exp(-grid / tau)

    gauss = np.exp(-0.5 * ((grid - grid_max / 2) / sigma_fixed) ** 2)
    gauss /= gauss.sum()

    shifted = grid - phi
    fast = np.where(shifted >= 0, np.exp(-shifted / tau_fast) / tau_fast, 0.0)
    slow = np.where(shifted >= 0, np.exp(-shifted / tau_slow) / tau_slow, 0.0)
    total = amp_fast * fast + amp_slow * slow

    conv1 = fftconvolve(total, gauss, mode="same")
    conv2 = fftconvolve(conv1, response_kernel, mode="full")[: len(grid)] * dt

    return np.interp(t, grid, conv2)


def exp_gauss_component_left_tail(x, sig, amp, tau, mu):
    """
    Gaussian-smeared-exponential with the exponential tail on the *low-x*
    side (mirror image of `exp_gauss_component`, which decays for t > phi),
    used for charge/PE spectra whose exponential tail sits below the peak
    rather than above it:
    A * exp((x-mu)/tau + sig**2/(2*tau**2)) * erfc((x-mu)/(sqrt(2)*sig) + sig/(sqrt(2)*tau)).
    """
    return (
        amp
        * np.exp((x - mu) / tau + (sig**2) / (2 * tau**2))
        * erfc((x - mu) / (np.sqrt(2) * sig) + sig / (np.sqrt(2) * tau))
    )


def alpha_charge_pulse(x, mu, sig1, amp1, tau1, sig2, amp2, tau2):
    """
    Two-component Gaussian-smeared-exponential model for an alpha-source
    charge/PE distribution: y(Q) = sum_{i=1,2} A_i exp((Q-mu)/tau_i +
    sig_i**2/(2*tau_i**2)) erfc((Q-mu)/(sqrt(2)*sig_i) + sig_i/(sqrt(2)*tau_i)),
    sharing a common onset/reference point `mu`.
    """
    return exp_gauss_component_left_tail(x, sig1, amp1, tau1, mu) + exp_gauss_component_left_tail(
        x, sig2, amp2, tau2, mu
    )


def exponential_decay(x, a, b, c):
    return a * np.exp(-abs(x) / abs(c)) - b


def correction_func(x, a, b, c, d):
    return a * np.exp(-b * x) + c / (1 + np.exp(-d * x))


def quadratic_cut(x, a, b, c):
    y = a - a * b * x / x[-1] + c * (x / x[-1]) ** 2  # Quadratic attenuation
    return 10**y


def quadratic_function(x, a, b, c):
    return a * x**2 + b * x + c


def _fresnel_unpolarized_transmittance(theta_rad, n):
    # n = n2/n1, light incident from medium 1 (angle theta_rad) into denser medium 2
    cos1 = np.cos(theta_rad)
    sin2 = np.clip(np.sin(theta_rad) / n, -1.0, 1.0)
    cos2 = np.sqrt(1.0 - sin2**2)
    rs = (cos1 - n * cos2) / (cos1 + n * cos2)
    rp = (n * cos1 - cos2) / (n * cos1 + cos2)
    return 1.0 - 0.5 * (rs**2 + rp**2)


def angular_pde_cosine_fresnel(x, A, n):
    # Geometric projection (cos theta) times Fresnel transmittance into a denser window
    theta = np.deg2rad(x)
    return A * np.cos(theta) * _fresnel_unpolarized_transmittance(theta, n)


def angular_pde_cosine_fresnel_inverse(x, A, n):
    # Geometric projection (cos theta) divided by Fresnel transmittance, modelling a
    # funnelling/gain effect that partially compensates the projection loss off-axis
    theta = np.deg2rad(x)
    return A * np.cos(theta) / _fresnel_unpolarized_transmittance(theta, n)


def angular_pde_sqrt_cosine(x, A):
    theta = np.deg2rad(x)
    return A * np.sqrt(np.cos(theta))

