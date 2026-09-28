from pathlib import Path

import pytest
from django.contrib.auth import get_user_model
from playwright.sync_api import expect

from growth.models import PracticeProtocol
from growth.services.canonical_import import seed_canonical_data


@pytest.mark.e2e
@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize("width", [1280, 390])
def test_compiled_packet_tables_resources_and_keyboard_reveal(live_server, page, width):
    get_user_model().objects.create_user(username="packet-reader", password="Guide-Test-2047!")
    seed_canonical_data()
    protocol = PracticeProtocol.objects.get(parent_competency_id="14.03")
    page.set_viewport_size({"width": width, "height": 900})
    page.goto(live_server.url + "/")
    page.get_by_label("Username").fill("packet-reader")
    page.get_by_label("Password").fill("Guide-Test-2047!")
    page.get_by_role("button", name="Sign in").click()
    page.wait_for_url(live_server.url + "/")
    url = f"{live_server.url}/practices/{protocol.slug}/guide/"
    page.goto(url)
    expect(page.get_by_role("table").first).to_be_visible()
    expect(page.get_by_role("columnheader", name="Record", exact=True)).to_be_visible()
    assert "fictional app policy V2" not in page.content().lower()
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    artifacts = Path(__file__).resolve().parents[2] / "test-results/pilot-walkthrough"
    artifacts.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=artifacts / f"catalog-privacy-guide-{width}.png", full_page=True)
    page.get_by_role("link", name="Open Practice checks", exact=True).focus()
    page.keyboard.press("Enter")
    expect(page.get_by_role("heading", name="Changed-case attempt")).to_be_visible()
    assert "Changed-case answer" not in page.content()
    page.get_by_role("link", name="Reveal check for Practice checks", exact=True).focus()
    page.keyboard.press("Enter")
    expect(page.get_by_role("heading", name="Changed-case answer")).to_be_visible()
    page.get_by_role("link", name="Later packet", exact=True).click()
    expect(page.get_by_role("heading", name="Later packet", exact=True)).to_be_visible()
    assert "Changed-case answer" not in page.content()
    with page.expect_download() as download:
        page.get_by_role("link", name="Download this view as Markdown").click()
    assert "-guide.md" in download.value.suggested_filename
    page.goto(url)
    page.evaluate("document.documentElement.style.fontSize = '200%'")
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    page.screenshot(path=artifacts / f"catalog-privacy-guide-zoom-{width}.png", full_page=True)
    legacy = PracticeProtocol.objects.get(parent_competency_id="08.02")
    page.goto(f"{live_server.url}/practices/{legacy.slug}/guide/")
    expect(page.get_by_role("heading", level=1)).to_contain_text("Mindfulness")
    page.get_by_role("link", name="Open Practice checks", exact=True).click()
    expect(page.get_by_role("heading", name="Practice checks", exact=True)).to_be_visible()

    wide = PracticeProtocol.objects.get(parent_competency_id="09.14")
    page.goto(f"{live_server.url}/practices/{wide.slug}/guide/?resource=file-pilot-results-md")
    table = page.get_by_role("region", name="Lesson table").first
    expect(table).to_be_visible()
    assert table.evaluate("el => el.scrollWidth > el.clientWidth")
    table.focus()
    page.keyboard.press("ArrowRight")
    page.wait_for_function("document.querySelector('.guide-table').scrollLeft > 0")
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    page.screenshot(path=artifacts / f"catalog-wide-table-{width}.png", full_page=True)
