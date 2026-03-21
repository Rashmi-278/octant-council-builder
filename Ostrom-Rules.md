# Elinor Ostrom's 8 Design Principles for Long-Enduring Commons Institutions

Source: Elinor Ostrom, *Governing the Commons: The Evolution of Institutions for Collective Action* (Cambridge University Press, 1990), pp. 90–102. Nobel Prize in Economics 2009. Academic formulations below are from the original text. Digital commons translations draw on [Mozilla's Data Commons Framework](https://www.mozillafoundation.org/en/blog/a-practical-framework-for-applying-ostroms-principles-to-data-commons-governance/), [Rozas et al. (2021)](https://journals.sagepub.com/doi/full/10.1177/21582440211002526), and [Frontiers in Blockchain (2025)](https://www.frontiersin.org/journals/blockchain/articles/10.3389/fbloc.2025.1538227/full).

---

## The 8 Design Principles

### 1. Clearly Defined Boundaries

> "Individuals or households who have rights to withdraw resource units from the CPR must be clearly defined, as must the boundaries of the CPR itself."

**Digital public goods translation:** Who can use, contribute to, and benefit from this project? What is the scope of the shared resource — is it a protocol, a dataset, a tool, an ecosystem service? Are contribution rights (commit access, governance weight) and usage rights (open-source license, access tiers) explicitly documented?

**Look for:** LICENSE files, contributor guidelines, membership criteria, token-gating rules, defined user personas, explicit scope documents.

---

### 2. Congruence Between Rules and Local Conditions

> "Appropriation rules restricting time, place, technology, and/or quantity of resource units are related to local conditions and to provision rules requiring labor, materials, and/or money."

**Digital public goods translation:** Are the project's governance rules tailored to its specific domain, community size, and technical context — or are they generic templates? Do the rules around funding distribution, contribution requirements, and resource allocation match the actual needs of the ecosystem the project serves?

**Look for:** Custom governance frameworks (not copy-pasted DAO templates), context-specific allocation mechanisms, rules that evolved from experience, epoch-based adaptation in Octant.

---

### 3. Collective-Choice Arrangements

> "Most individuals affected by the operational rules can participate in modifying the operational rules."

**Digital public goods translation:** Can the people who use, build, and depend on this project actually change how it's governed? Is there a mechanism — voting, proposals, rough consensus, forum deliberation — that gives affected stakeholders a real voice, not just a comment box that gets ignored?

**Look for:** Snapshot votes, governance forums (Discourse, Commonwealth), proposal processes (EIPs, RFCs), multisig with community signers, on-chain governance, contributor assemblies.

---

### 4. Monitoring

> "Monitors, who actively audit CPR conditions and appropriator behavior, are accountable to the appropriators or are the appropriators."

**Digital public goods translation:** Is there transparent tracking of how resources are used, how funds are spent, and whether commitments are met? Critically — are the monitors accountable to the community, not just the core team? In digital commons, monitoring includes data integrity validation, milestone tracking, financial transparency, and code audit.

**Look for:** Karma GAP milestone tracking, public financial reports, on-chain treasury transparency, GitHub activity dashboards, community-elected reviewers, open analytics (Dune, OSO).

---

### 5. Graduated Sanctions

> "Appropriators who violate operational rules are likely to be assessed graduated sanctions (depending on the seriousness and context of the offense) by other appropriators, by officials accountable to these appropriators, or both."

**Digital public goods translation:** When someone breaks the rules — misuses funds, fails to deliver, acts in bad faith — does the response scale proportionally? First offense might be a conversation; repeated violations lead to funding cuts, role removal, or exclusion. The opposite failure modes are equally bad: zero enforcement (free-riding thrives) and all-or-nothing punishment (mistakes become catastrophic).

**Look for:** Code of conduct with enforcement ladder, documented responses to past incidents, defunding criteria, contributor removal processes, slashing mechanisms, grant clawback provisions.

---

### 6. Conflict-Resolution Mechanisms

> "Appropriators and their officials have rapid access to low-cost local arenas to resolve conflicts among appropriators or between appropriators and officials."

**Digital public goods translation:** When disputes arise — about direction, resource allocation, contributor behavior, or governance decisions — is there a fast, accessible, low-barrier way to resolve them? "Low-cost" in digital means: no lawyers needed, no formal legal proceedings, accessible across time zones. The key word is *rapid* — conflicts that fester destroy communities.

**Look for:** Governance forums with dispute threads, mediation processes, appeal mechanisms for governance votes, ombudsman roles, arbitration DAOs (Kleros, Aragon Court), documented conflict resolution procedures.

---

### 7. Minimal Recognition of Rights to Organize

> "The rights of appropriators to devise their own institutions are not challenged by external governmental authorities."

**Digital public goods translation:** Can this project self-govern without external authorities overriding its decisions? In digital commons, this means: do grant programs, foundations, L1 protocols, and regulators respect the project's autonomy? A project whose governance can be vetoed by a foundation or whose treasury can be frozen by a single entity fails this principle. Also: does the project have legal clarity to operate (legal wrapper, regulatory compliance)?

**Look for:** Legal entity or DAO wrapper, foundation non-interference commitments, regulatory compliance, recognition by Octant/Gitcoin/RetroPGF as a legitimate self-governing entity, absence of hostile external overrides.

---

### 8. Nested Enterprises

> "Appropriation, provision, monitoring, enforcement, conflict resolution, and governance activities are organized in multiple layers of nested enterprises."

**Digital public goods translation:** Governance happens at multiple scales — a working group handles day-to-day decisions, the full community votes on major changes, and the project plugs into ecosystem-level governance (Octant epochs, Ethereum governance, broader public goods funding). No single layer holds all power. This is subsidiarity: decisions are made at the lowest effective level.

**Look for:** Working groups/sub-DAOs, tiered decision rights (contributors → council → token holders), participation in ecosystem governance (Octant, Gitcoin, EF), cross-project coordination, multi-chain presence with local governance per chain.

---

## Scoring Guide for Digital Public Goods

When scoring a project against these principles:

| Score | Meaning | What it looks like |
|-------|---------|-------------------|
| **80–100** | Principle is deeply embedded | Documented, practiced, community-driven, evolved over time |
| **60–79** | Principle is present but incomplete | Mechanism exists but underused, or partially implemented |
| **40–59** | Principle is aspirational | Some evidence of intent, but not yet functional |
| **20–39** | Principle is weak | Minimal evidence; governance is mostly centralized or informal |
| **0–19** | Principle is absent | No evidence; governance structure doesn't address this |

**Key scoring rules:**
- **Evidence over intent.** A governance doc that nobody reads scores lower than an informal process that actually works.
- **Absence is signal.** If you can't find evidence of dispute resolution, that IS the score — it tells you the project hasn't needed or built one.
- **Digital ≠ physical, but the logic holds.** Open-source code is a commons. Token treasuries are shared resources. Contributors are appropriators. The principles translate; the artifacts change.
- **Context matters.** A 3-person team doesn't need nested enterprises. Score relative to the project's scale and maturity.
