# TODO

## Open

- [ ] **Test Handball booking on 22.06.2026 at 07:00** — this is when the buchen button for course 121401 appears; run the bot then to verify the full flow works for the actual target course
- [ ] **Handle prerequisite courses** — some courses require a Semesterkarte (or other prerequisite) to be booked first. The portal currently shows the prereq page but the bot needs to handle the case where the prereq is *not* yet satisfied (detect, warn, or auto-book it)
- [ ] **Verify email confirmation arrives** — after a successful booking the portal should send a confirmation email; confirm this works end-to-end
- [ ] **Add a dry-run mode** — stop after reaching the final confirmation page (before the last POST) so the user can verify everything looks correct without committing the booking

## Done

- [x] Rewrite bot from Selenium to `requests` + `BeautifulSoup` (no browser required)
- [x] Fix form discovery (form wraps entire page, not individual row)
- [x] Add `Origin` + `Referer` headers required by the portal
- [x] Fix `sex` field to uppercase
- [x] Handle both `"buchen"` and `"verbindlich buchen"` as final confirmation button labels
- [x] Live end-to-end test on Fußball course 121262 — bot reached and submitted the final confirmation
