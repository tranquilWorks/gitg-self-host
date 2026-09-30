import pytest
from playwright.sync_api import expect

from tests.e2e.test_application_consistency import audit_page
from tests.e2e.test_core_flow import create_browser_user, log_in, save_walkthrough_screenshot

pytestmark = [pytest.mark.e2e, pytest.mark.django_db(transaction=True)]


@pytest.mark.parametrize("width", [320, 1280])
def test_personal_start_installation_help(live_server, page, settings, tmp_path, width):
    from growth.models import AssessmentRun
    from growth.services.library_import import seed_library_data

    create_browser_user()
    seed_library_data()
    # Only the revision reader uses BASE_DIR during this page's rendering.
    (tmp_path / "BUILD_REVISION").write_text("a" * 40)
    settings.BASE_DIR = tmp_path
    settings.SEED_DEMO = False
    page.set_viewport_size({"width": width, "height": 900})
    log_in(live_server, page)
    page.goto(live_server.url + "/account/data/")
    page.get_by_role("link", name="Installation version and recovery help").click()
    audit_page(page)
    expect(page.get_by_text("a" * 40, exact=True)).to_be_visible()
    expect(page.get_by_text("Personal start is selected.", exact=False)).to_be_visible()
    page.get_by_text("Operator commands and recovery guide", exact=True).focus()
    page.keyboard.press("Enter")
    expect(
        page.get_by_text("docker compose exec app python manage.py", exact=False)
    ).to_be_visible()
    expect(page.locator('.site-nav [aria-current="page"]')).to_have_text("Account")
    expect(page.locator(".nav-more > summary")).to_have_text("More · Account")
    page.evaluate("window.scrollTo(0, 0)")
    save_walkthrough_screenshot(page, f"operator-installation-{width}")
    page.add_style_tag(content="html { font-size: 200%; }")
    audit_page(page)
    assert not AssessmentRun.objects.exists()
