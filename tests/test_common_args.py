from scripts.common_args import parse_plot_label


def test_parse_plot_label_shell_collapsed_raw_literal():
    value = "rCross Section (10^{-38} cm^{2})"

    parsed = parse_plot_label(value)

    assert parsed == "Cross Section ($10^{-38} cm^{2}$)"


def test_parse_plot_label_python_raw_literal_token():
    value = "r'Cross Section (10^{-38} cm^{2})'"

    parsed = parse_plot_label(value)

    assert parsed == "Cross Section ($10^{-38} cm^{2}$)"


def test_parse_plot_label_explicit_r_star_prefix():
    value = "r*Cross Section (10^{-38} cm^{2})"

    parsed = parse_plot_label(value)

    assert parsed == "Cross Section ($10^{-38} cm^{2}$)"


def test_parse_plot_label_keeps_existing_mathtext():
    value = "Cross Section ($10^{-38}\\ \mathrm{cm}^{2}$)"

    parsed = parse_plot_label(value)

    assert parsed == value
