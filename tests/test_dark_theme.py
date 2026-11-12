"""Static palette/request receipts; these do not establish browser or human acceptance."""

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
THEME = ROOT / "growth/static/growth/dark_theme.css"


def tokens():
    return dict(re.findall(r"--([\w-]+):\s*(#[\da-f]{6});", THEME.read_text()))


def contrast(a, b):
    def luminance(value):
        rgb = [int(value[i : i + 2], 16) / 255 for i in (1, 3, 5)]
        linear = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
        return sum(c * weight for c, weight in zip(linear, (0.2126, 0.7152, 0.0722), strict=True))

    lighter, darker = sorted((luminance(a), luminance(b)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


def test_exact_tranquilworks_palette_and_native_dark_controls():
    palette = tokens()
    assert {
        key: palette[key]
        for key in (
            "paper",
            "surface",
            "surface-muted",
            "surface-deep",
            "ink",
            "ink-soft",
            "accent",
            "accent-dark",
            "accent-hover",
            "danger",
        )
    } == {
        "paper": "#081114",
        "surface": "#0d181c",
        "surface-muted": "#142328",
        "surface-deep": "#050b0e",
        "ink": "#edf3ef",
        "ink-soft": "#a8b5b0",
        "accent": "#e6ad4b",
        "accent-dark": "#79bea9",
        "accent-hover": "#ffd486",
        "danger": "#e17555",
    }
    source = THEME.read_text()
    assert "color-scheme: dark" in source
    assert "@media (forced-colors: active)" in source
    assert "forced-color-adjust: none" not in source
    assert "input:autofill" in source
    assert "@import" not in source and "url(" not in source


@pytest.mark.parametrize(
    ("foreground", "background", "minimum"),
    [
        ("ink", surface, 4.5)
        for surface in ("paper", "surface", "surface-muted", "surface-deep", "accent-pale")
    ]
    + [
        ("ink-soft", surface, 4.5)
        for surface in ("paper", "surface", "surface-muted", "accent-pale")
    ]
    + [
        ("accent-dark", "surface", 4.5),
        ("accent-dark", "accent-pale", 4.5),
        ("on-accent", "accent", 4.5),
        ("on-accent", "accent-hover", 4.5),
        ("on-accent", "danger", 4.5),
        ("warning", "warning-bg", 4.5),
        ("danger", "danger-bg", 4.5),
        ("danger", "surface", 4.5),
        ("line-strong", "surface-muted", 3),
        ("line-strong", "surface", 3),
        ("accent", "surface-muted", 3),
    ],
)
def test_palette_text_control_and_focus_contrast(foreground, background, minimum):
    palette = tokens()
    assert contrast(palette[foreground], palette[background]) >= minimum


@pytest.mark.django_db
@pytest.mark.parametrize("path", ["/accounts/login/", "/accounts/create/", "/data-policy/"])
def test_public_shell_loads_dark_theme_last_without_scripts(client, path):
    response = client.get(path)
    assert response.status_code == 200
    html = response.content.decode()
    assert '<meta name="color-scheme" content="dark">' in html
    assert '<meta name="theme-color" content="#081114">' in html
    sheets = re.findall(r'<link rel="stylesheet" href="([^"]+)"', html)
    assert sheets[-1] == "/static/growth/dark_theme.css"
    assert sheets.index("/static/growth/app.css") < sheets.index("/static/growth/application.css")


@pytest.mark.django_db
def test_authenticated_routes_inherit_one_shared_theme_and_preserve_records(client, user, seeded):
    from growth.models import AssessmentRun, EvidenceEvent, PersonalOSRevision

    client.force_login(user)
    before = list(AssessmentRun.objects.filter(user=user).values())
    for path in (
        "/",
        "/profile/",
        "/assessment/",
        "/personal-os/",
        "/practices/",
        "/weekly/",
        "/history/",
        "/evidence/",
        "/account/data/",
        "/account/pilot-feedback/",
    ):
        response = client.get(path)
        assert response.status_code == 200, path
        assert response.content.count(b"growth/dark_theme.css") == 1, path
    assert list(AssessmentRun.objects.filter(user=user).values()) == before
    assert not EvidenceEvent.objects.exists()
    assert not PersonalOSRevision.objects.filter(user=user).exists()
