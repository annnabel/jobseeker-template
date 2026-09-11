### ev:0000 — Short imperative headline of the accomplishment
role:       Title, Company            # ends in an employer (or institution)
                                      # spelled exactly as resume.yaml does
dates:      YYYY-MM → YYYY-MM
metric:     before → after (delta)    # or "n/a" if qualitative — plenty of
                                      # real work has no number, and inventing
                                      # one is the failure this system prevents
confidence: measured                  # measured | estimated | qualitative
source:     where the number is documented   # REQUIRED when confidence: measured
scope:      who/how many · how often · what was at stake — what sizes the win
tags:       comma, separated, lowercase — whatever your field calls its
            capabilities: tools, systems, procedures, languages, curricula,
            licences, methods, domains
angles:     which angle(s) this supports, comma separated — each must be
            declared in the bank's `## Angles` block (templates/angle-entry.md).
            Empty during the interview; `/setup` keeps a `# proves: …` note
            beside the entry until the angles exist, then fills this in
narrative: >
  Two to four sentences. What was broken, what you did, what happened. This is
  the STAR story, written once here — not regenerated per JD. The tailor quotes
  and trims it; it never invents beyond it.
