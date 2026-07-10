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


def exponential_decay(x, a, b, c):
    return a * np.exp(-abs(x) / abs(c)) - b


def correction_func(x, a, b, c, d):
    return a * np.exp(-b * x) + c / (1 + np.exp(-d * x))


def quadratic_cut(x, a, b, c):
    y = a - a * b * x / x[-1] + c * (x / x[-1]) ** 2  # Quadratic attenuation
    return 10**y


def quadratic_function(x, a, b, c):
    return a * x**2 + b * x + c
