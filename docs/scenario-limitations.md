# BlastShield — Scenario Limitations, Risk Register, and Upgrade Acceptance Plan

**Scope:** Current Member 1 graph/database/service implementation for Scenarios 1–4.  
**Purpose:** Identify the gaps that matter for the Graph Hacks / FalkorDB Track 01 submission and the additional controls expected of a credible production-oriented security design.  
**Data boundary:** Current scenarios use synthetic data in a local FalkorDB instance. No real cloud remediation is performed.

---

## 1. Executive Assessment

The current four scenario foundations and their current service tests pass. That is a useful milestone, but it demonstrates the implemented query behavior against a small, seeded graph. It does **not** yet establish production readiness, complete attack-path coverage, or the correctness of a security conclusion against a real cloud estate.

The earlier limitation list was a useful first pass, but it was **not exhaustive enough** for our goals. This document replaces it with a fuller risk register.

The main gaps are:

1. Several queries recognise only one hard-coded path shape, not all relevant paths through a connected cloud environment.
2. Some security conclusions rely on labels already written into the graph (for example, `assessment = 'EXCESSIVE'`) instead of independently evaluating the underlying policy evidence.
3. The graph is seeded synthetic data; there is no ingestion, provenance, freshness, or completeness guarantee.
4. An empty result means only that the current query found no qualifying path in the represented graph. It does not establish that no real access path exists.
5. Scenario 4 changes a graph property to simulate containment. It does not revoke a live session or policy, and its query verifies only the path patterns explicitly modelled.
6. The current service layer is not yet a complete agent workflow with constrained tool selection, a decision/recommendation step, action controls, and path-backed explanations.
7. Tests focus on known seeded paths and selected negative inputs. They do not yet cover enough adversarial graph shapes, missing data, stale data, concurrency, scale, or integration behavior.

### Important distinction

There is no finite document that lists every limitation a future enterprise deployment might have. This register is intended to be a comprehensive assessment of the limitations visible in the current implementation and the upgrade requirements most relevant to a strong hackathon prototype and credible industrial architecture.

We should **not** try to build an entire enterprise cloud-security platform during the hackathon. We should build a narrow, complete, demonstrable vertical slice, make its safety boundaries explicit, and document the remaining production work honestly.

---

## 2. What the Current Foundations Actually Demonstrate

| Scenario | Demonstrated behavior | Not demonstrated yet |
|---|---|---|
| 1 — Identity investigation | Finds the specific represented chain from an identity through an active session, running workload, IAM roles, and a critical asset. | That a login is genuinely suspicious; complete identity reachability; all possible routes; real cloud-state accuracy. |
| 2 — Excessive IAM permissions | Finds a path whose `CAN_ASSUME` relationship is already marked `assessment = 'EXCESSIVE'`. | An independent least-privilege evaluation over actual permission and policy evidence. |
| 3 — Exposed workload | Finds critical assets reached through the modeled public workload → assigned role → `CAN_READ` pattern. | Actual exploitability, complete cloud/network exposure analysis, or all multi-hop privilege paths. |
| 4 — Containment verification | Marks a modeled session-route relationship `BLOCKED`, detects a remaining matching route, and confirms that no matching active route remains after both modeled routes are blocked. | Actual remediation, complete route coverage, authoritative containment verification, durable audit history, approval controls, or race-safe state changes. |

Passing tests should therefore be described as **validated behavior on the current synthetic model**, not proof of complete real-world security.

---

## 3. Scenario 1 — Identity Investigation

### Current query shape

`Identity → ACTIVE Session → RUNNING Workload → IAMRole → CAN_ASSUME → IAMRole → CAN_READ → critical DataAsset`

### Limitations

**S1.1 — Suspicious-login detection is not implemented.**  
The current query starts with an identity and follows access relationships. It does not evaluate a login event, authentication anomaly, unfamiliar device/IP, impossible travel, risk signal, or alert. Calling this a suspicious-login detector would overstate what the implementation proves.

**S1.2 — One fixed relationship sequence.**  
The query requires a particular number, type, and direction of hops. Access paths involving direct permissions, additional role assumptions, groups, temporary credentials, service identities, resource policies, or other intermediaries may be missed.

**S1.3 — Narrow status assumptions.**  
The query requires `Session.status = 'ACTIVE'` and `Workload.status = 'RUNNING'`. Missing, stale, differently named, or differently encoded properties can exclude relevant paths.

**S1.4 — No authentication-to-access correlation.**  
There is no durable `LoginEvent`/`Finding` node carrying fields such as source, timestamp, severity, reason, or confidence and linked to the identity being investigated.

**S1.5 — No temporal reasoning.**  
The query does not establish whether an event occurred before or after a permission change, session creation, or suspicious activity window.

**S1.6 — No route prioritisation.**  
Results are returned without a transparent risk score or ordering based on evidence strength, asset importance, privilege breadth, and path length.

**S1.7 — Incomplete identity model.**  
The schema does not yet model identity-provider principals, groups, credential types, role trust policies, resource policies, or session provenance comprehensively.

### Required upgrades

1. Either rename the current capability to **identity access-path investigation**, or add a synthetic security finding/login event with explicit evidence and link it to the identity. Do not claim anomaly detection without an implemented signal.
2. Preserve the source finding, timestamp, severity/reason, and graph path in the returned evidence.
3. Add at least one additional legitimate access-path shape and tests proving it is found.
4. Add tests for inactive sessions, stopped workloads, missing properties, and an identity that exists but has no matching path.
5. Return a bounded, evidence-backed result and explicitly state that the graph describes modeled reachability.

---

## 4. Scenario 2 — Excessive IAM Permissions

### Current query shape

`IAMRole -[CAN_ASSUME {assessment: 'EXCESSIVE'}]→ IAMRole → critical DataAsset`

### Limitations

**S2.1 — The excessive label is trusted rather than derived.**  
The query finds a relationship already labelled `EXCESSIVE`. It does not itself determine excessiveness from the role's intended scope, allowed actions, resource scope, trust policy, or effective permissions.

**S2.2 — Incomplete policy semantics.**  
Real IAM authorization can depend on identity policies, resource policies, trust relationships, permission boundaries, organization-level policies, conditions, explicit denies, session policies, and provider-specific evaluation rules. The current graph does not represent or evaluate those dimensions.

**S2.3 — Narrow privilege-chain pattern.**  
The query follows one `CAN_ASSUME` relationship and then one `CAN_READ` relationship. Longer role chains, alternative actions, resource-based grants, group membership, or other routes can be missed.

**S2.4 — Intended scope is not enforced by the query.**  
Although the seed data records intended-scope metadata, the current query's conclusion depends on the pre-labelled relationship. It does not compare requested/granted capability with an explicit policy rule.

**S2.5 — No impact or priority calculation.**  
A path to a critical asset is returned, but the service does not rank findings by breadth of privilege, asset sensitivity, reachable asset count, confidence, or policy evidence.

**S2.6 — No policy provenance or freshness.**  
There is no source document/version, last-checked timestamp, or clear indication of whether the permission data reflects current state.

### Required upgrades

1. Implement a small, explicit, deterministic least-privilege rule for the synthetic dataset; return the policy facts that triggered it.
2. Keep the rule explainable: distinguish **policy evidence**, **rule result**, and **impact path**.
3. Test a non-excessive role, an explicit-deny case if modelled, and a role with no route to a critical asset.
4. Add at least one alternative or multi-hop privilege path, with bounded traversal limits.
5. Include source/freshness metadata or clearly identify the evidence as synthetic fixture data.

---

## 5. Scenario 3 — Exposed Workload and Blast Radius

### Current query shape

`PUBLIC + RUNNING Workload → RUNS_AS IAMRole → CAN_READ critical DataAsset`

### Limitations

**S3.1 — Fixed two-edge access pattern.**  
The query only covers the direct workload-role-asset pattern. It can miss paths that require role assumption, intermediary services, service accounts, inherited permissions, or other relationship types.

**S3.2 — Public exposure is a single property.**  
`exposure = 'PUBLIC'` is trusted as an input fact. There is no derivation from load balancers, public IPs, routing, firewall/security-group rules, ingress policies, or provider exposure configuration.

**S3.3 — Reachability is not exploitability.**  
Public exposure plus a graph access path does not establish that the workload is vulnerable, compromised, or able to execute the read in a live cloud environment.

**S3.4 — Critical assets only.**  
The query only returns assets marked `sensitivity = 'critical'`. Important non-critical dependencies and indirect impact paths are not represented in the reported blast radius.

**S3.5 — No asset fan-out controls or ranking.**  
As the graph grows, one workload may have many paths to many assets. There is no explicit result cap, pagination, deduplication policy for alternative paths to the same asset, or deterministic prioritisation rule.

**S3.6 — No exposure source or freshness.**  
The result does not show when or where the public exposure fact was obtained, or whether it is still current.

**S3.7 — No dependency-impact context.**  
The scenario does not yet connect findings to service ownership, business function, environment criticality, or a clear remediation recommendation.

### Required upgrades

1. Expand the supported traversal to at least one multi-hop route that is relevant to the synthetic security model; make maximum depth explicit and bounded.
2. Return per-path evidence and a deduplicated list of reachable assets, while preserving alternative paths when they matter.
3. Include an explicit statement distinguishing **publicly exposed in the model**, **potentially reachable**, and **confirmed compromised**.
4. Test no critical asset, stopped workload, non-public workload, multiple paths to the same asset, and a bounded-traversal case.
5. Add deterministic prioritisation of the most relevant assets or paths for the demo.

---

## 6. Scenario 4 — Containment and Alternative-Path Verification

### Current implementation

Containment sets `containment_status = 'BLOCKED'` on a selected `HAS_SESSION` relationship. The verification query follows only active `HAS_SESSION` relationships and one predefined session/workload/role/data sequence.

### Limitations

**S4.1 — This is a graph simulation, not cloud remediation.**  
No real token is revoked, session terminated, IAM policy changed, workload isolated, or network rule updated. The user interface and agent must never present it as an executed cloud action.

**S4.2 — Verification covers only represented, matching paths.**  
An empty result means no path matched this query in the current graph. It does not prove there are no routes through other identities, credentials, resource policies, network paths, role chains, or relationships the schema does not model.

**S4.3 — Containment changes an edge annotation only.**  
The `Session` node itself remains `ACTIVE`. This can be a valid way to model a blocked route, but the result must clearly mean **this modeled access route is blocked**, not that the underlying session or principal is disabled.

**S4.4 — No action ledger.**  
There is no durable `ContainmentAction` record of action ID, selected route, reason, actor, timestamp, prior state, resulting state, or verification result.

**S4.5 — No approval or authorisation gate.**  
The service directly changes the graph when called. It does not check caller permissions, risk level, approval state, or whether an action is allowed for the selected resource.

**S4.6 — No atomic compare-and-set behavior.**  
The current flow reads route status, then updates it. Concurrent calls could both observe the same initial state. The state transition is not protected by an explicit conditional update/transaction strategy.

**S4.7 — No action-plan or rollback semantics.**  
The service does not show expected side effects, impacted identities/assets, reversibility, or a rollback plan before a simulated action.

**S4.8 — No verification coverage report.**  
The service does not state which path patterns were checked, which data was missing/stale, or what was outside its verification boundary.

**S4.9 — Seed/test isolation.**  
The Scenario 4 seed reuses `customer-db`, which is also used by other fixtures, and resets its properties. Shared fixtures can become coupled as the schema evolves. Scenario-specific IDs or an isolated test graph would reduce accidental interference.

**S4.10 — No explicit partial-containment state.**  
The service can report the paths it finds, but there is no first-class final outcome such as `ALTERNATIVE_PATH_REMAINS`, `NO_MODELED_PATH_FOUND`, or `VERIFICATION_INCOMPLETE`.

### Required upgrades

1. Keep every action explicitly labelled **SIMULATED**; make it impossible for the current code path to imply real cloud remediation.
2. Persist a synthetic action/audit record with action ID, target route, reason, before/after status, and verification summary.
3. After every simulated action, rerun the bounded reachability query and report remaining paths plus reachable assets.
4. Use cautious verification outcomes: `ALTERNATIVE_PATH_REMAINS`, `NO_QUALIFYING_PATH_IN_MODEL`, and `VERIFICATION_INCOMPLETE` when coverage/data checks are insufficient. Avoid claiming absolute containment based on one query.
5. Test unknown routes, repeated requests, failed updates, missing route evidence, and concurrent/repeated operation behavior to the degree feasible in the prototype.
6. Isolate or namespace scenario fixtures so seeding one scenario does not unexpectedly change another scenario's test data.

---

## 7. Cross-Cutting Limitations

### 7.1 Graph model, ingestion, and data quality

- The graph is populated from synthetic seed scripts; no live or periodic cloud inventory synchronisation exists.
- No canonical ingestion/normalisation layer maps cloud-provider entities into consistent identity, workload, role, relationship, and asset semantics.
- Nodes and relationships lack consistent source, source-record ID, observed-at time, last-verified time, and confidence metadata.
- There is no data freshness threshold or stale-data warning.
- Missing facts and false facts are not differentiated systematically.
- Referential integrity, uniqueness assumptions, schema evolution, and duplicate/conflicting records are not comprehensively validated.
- There is no explicit inventory coverage indicator explaining which accounts, projects, regions, resource types, or relationship types have been modelled.

### 7.2 Result semantics and uncertainty

- `no_path` is easy to misinterpret as proof of safety. It should mean only **no qualifying path matched in the current model/query**.
- An entity existing in the graph does not guarantee that the relevant relationships are complete or current.
- Results need to distinguish at minimum: invalid input, unknown entity, qualifying path found, no qualifying path found in the model, incomplete/stale evidence, and query failure.
- The service does not return graph coverage, source freshness, confidence, or an explanation of which query/constraints were applied.
- The output should distinguish observed facts, policy-derived findings, inferred risk, recommendations, simulated changes, and verified graph state.

### 7.3 Risk calculation and recommendation quality

- No documented scoring method combines asset criticality, public exposure, privilege level, path length, confidence, and evidence freshness.
- No separate likelihood and impact dimensions exist.
- There is no policy for how uncertainty changes prioritisation.
- No structured recommendation connects the finding to a suggested next step and its evidence.
- There is no evaluation set for measuring false positives, false negatives, path recall, or recommendation quality.

### 7.4 Query safety and performance

- Current queries are predefined and parameterised, which is a good foundation; this must be preserved when the agent/MCP layer is integrated.
- Traversals do not yet have a shared, explicit policy for maximum hop count, number of returned paths, result size, execution time, or pagination.
- Query performance has not been benchmarked against a larger graph or high-fan-out nodes.
- The implementation has no performance budget, slow-query telemetry, or plan review for every production-critical query.
- Any future variable-length traversal must have a bounded depth and result limit to avoid path explosion.
- Query result formatting assumes expected columns and property shapes. Unexpected/null values need validated handling rather than unhandled exceptions.

### 7.5 Service contracts and error handling

- Service responses are plain dictionaries rather than centrally validated response models.
- Response field semantics and allowable status values are not yet versioned in a strict contract.
- Errors are logged and converted to a generic `query_error`, but no request/trace ID, query duration, structured error category, or retryability indicator is returned.
- Connection lifecycle and local defaults are suitable for development but do not establish production connection pooling, health checks, retry/backoff, credentials, TLS, or deployment configuration.
- There is no explicit transaction/concurrency design for state-changing operations.

### 7.6 Security and tenant isolation

- The current local graph has no demonstrated application-level authentication or role-based authorisation.
- There is no tenant separation/access-control design for data belonging to multiple organisations.
- Production credentials, secrets management, TLS, encryption-at-rest assumptions, retention, and backup/restore procedures are not covered.
- A future action tool must validate target identity, route, permitted operation, user approval, and action scope before it writes.
- The LLM must not be allowed to construct arbitrary Cypher or bypass service validation. Fixed tools with typed arguments and bounded operations should be used.
- Outputs supplied to an LLM must be treated as untrusted data; strings in graph properties must not be allowed to override system/tool instructions.

### 7.7 Observability, audit, and operations

- There is no end-to-end trace connecting user request → selected tool → query → paths/evidence → recommendation → approval → simulated action → verification.
- No metrics track query latency, path counts, failures, data freshness, action outcomes, or tool-selection accuracy.
- No structured action audit history exists yet.
- There is no CI pipeline running regression tests on every change.
- The current scripts do not provide a coverage report or systematic generated/adversarial test graph suite.
- Backup/restore, upgrade/rollback, and recovery from database unavailability have not been tested.

### 7.8 Test completeness

Current tests verify the seeded happy paths and several invalid/unknown input cases. Additional coverage is still required for:

- Multiple routes to the same asset and duplicate path behavior.
- Alternate relationship sequences and multi-hop role chains.
- Missing, null, malformed, stale, or contradictory graph properties.
- Nonqualifying security findings and non-excessive permissions.
- Multiple identities sharing assets, and test-fixture isolation.
- No qualifying path versus incomplete graph coverage.
- Large fan-out graphs, traversal limits, query timing, and deterministic result ordering.
- Service behavior under FalkorDB unavailable/query failures.
- Repeated and concurrent containment requests.
- End-to-end agent/MCP/service/frontend integration, not only direct Python service calls.

### 7.9 Agent and hackathon-track fit

- The current Member 1 work is a graph-service foundation, not by itself the completed Track 01 product.
- The graph must materially influence the agent's investigation and action selection; FalkorDB cannot be a decorative visualisation or a passive lookup store.
- The agent should select among fixed, human-authored tools with validated arguments rather than generate arbitrary Cypher.
- Tool outputs should include the concrete graph path and evidence that support the answer.
- The demo must show an end-to-end incident: finding → graph traversal → evidence-backed decision/recommendation → explicitly simulated or approved action → post-action verification.
- The agent must clearly distinguish unknown entity, no qualifying path found in the model, and a verified post-action state.
- The agent should not assert that an identity is compromised or containment is complete unless the implemented evidence actually supports that claim.

---

## 8. Upgrade Priorities

The hackathon is time-boxed. Priorities below are intentionally divided between what is needed for a convincing, defensible submission and broader production hardening.

### P0 — Must be addressed before claiming the upgraded prototype is complete

1. **Accurate scenario naming and evidence:** do not call Scenario 1 suspicious-login detection unless a finding/login signal is represented and evaluated.
2. **Safe outcome semantics:** replace ambiguous claims like “safe” or “fully contained” with “no qualifying path found in the current model” unless full coverage can be established.
3. **Bounded graph reasoning:** add at least one meaningful multi-hop path/tool beyond the fixed happy-path patterns, with a maximum depth and result cap.
4. **Policy-backed IAM assessment:** show the synthetic permission facts and explicit rule that justify an excessive-permission conclusion, rather than relying only on a pre-set label.
5. **Evidence-rich response contract:** return paths, edge types/properties, finding reason/source, asset impact, status, and relevant uncertainty in a consistent schema.
6. **Containment audit trail:** persist a simulated action record with before/after states and a post-action alternative-path check.
7. **No arbitrary LLM Cypher:** use fixed query/service tools, typed/validated arguments, entity resolution, and bounded operations.
8. **Test the negative and alternative paths:** prove that the agent detects a surviving route and does not confuse unknown, no-path, stale/incomplete evidence, and query failure.
9. **End-to-end demonstrable graph use:** the agent must use FalkorDB results to select/explain the next step, and the graph must be central to the product behavior.
10. **Clear demo and repository:** README, graph schema, key Cypher, setup, tests, known limitations, demo video, and explicit synthetic/simulation labeling.

### P1 — Strong differentiators if time permits

- Transparent path/finding priority score with a short explanation of each score component.
- One relevant graph algorithm exposed as a controlled tool, if it adds genuine value (for example, shortest/lowest-cost path or a centrality-based criticality signal). Do not add an algorithm solely for decoration.
- Source/freshness fields and visible warnings for stale or incomplete evidence.
- A graph/path visualisation that lets a judge trace why an asset was returned.
- Additional seeded attack-path variants and automated regression tests.
- Structured logs with request IDs and query timing.

### P2 — Production-readiness backlog; do not fake these in a hackathon demo

- Real provider connectors and incremental inventory/event ingestion.
- Full AWS/Azure/GCP effective-permission evaluation and provider-specific policy semantics.
- Multi-tenant authentication/authorisation and isolation.
- Production secrets management, network controls, TLS, encryption, backups, and recovery.
- Strong concurrency controls, transactional action handling, approval workflows, and real remediation adapters.
- Large-graph benchmarking, load testing, CI/CD, alerting, and operational runbooks.
- Formal security review, threat modelling, and independent evaluation of detection accuracy.

---

## 9. Acceptance Criteria for the Upgraded Four Scenarios

### Scenario 1

- The capability is accurately named as access-path investigation unless a login/finding evidence model is added.
- A result carries its motivating finding/evidence and a concrete path when relevant.
- Tests cover active and inactive sessions, running and stopped workloads, unknown identities, no matching path, and an alternative valid path.
- No result claims an identity is compromised merely because a path exists.

### Scenario 2

- The service evaluates a documented synthetic least-privilege rule.
- The result contains the policy facts, violated rule, affected role, path, and critical asset.
- Tests cover excessive and non-excessive cases, unknown roles, missing policy evidence, and an alternative/multi-hop route.
- A pre-existing `EXCESSIVE` label alone is not presented as independent policy analysis.

### Scenario 3

- The service can inspect more than one supported path topology with a bounded traversal.
- The result identifies reachable critical assets, preserves alternative paths where material, and includes exposure/role/asset evidence.
- Tests cover non-public, stopped, disconnected, multiple-path, missing-evidence, and multi-hop cases.
- The response explicitly distinguishes exposure/reachability from compromise or exploitability.

### Scenario 4

- Every current action is visibly and structurally marked simulated.
- The action record contains target route, reason, before/after state, and verification outcome.
- Following one containment action, the service identifies any alternative route that still reaches a critical asset.
- After blocking all relevant modelled routes, the response says no qualifying paths were found in the current model and includes coverage/uncertainty caveats.
- Tests cover unknown route, repeat call, no remaining path, alternative path, failure handling, and fixture cleanup.

### Cross-scenario / integration

- The four functions share consistent, validated response shapes.
- Queries remain predefined, parameterised, bounded, and traceable.
- Every security conclusion returned to the agent includes graph evidence or a clear reason no evidence was found.
- The agent cannot invent graph entities, call arbitrary queries, or represent simulated actions as live remediation.
- A complete demo can be run from the documented setup instructions and produces repeatable results.

---

## 10. Hackathon Submission Checklist

Before submission, verify the live official rules and check every applicable requirement. At minimum:

- Public source-code repository.
- README with project purpose, architecture, setup instructions, graph data model, key Cypher queries, test commands, and known limitations.
- Working end-to-end demo video.
- Live deployment if feasible; otherwise complete local setup instructions and reproducible local demo.
- Clearly identify the Track 01 entry.
- Use only permitted data; current demo uses synthetic data.
- Disclose AI coding-assistant use as required by the rules.
- Be prepared to explain the graph schema, Cypher, service boundaries, and technical decisions.
- Make FalkorDB visibly central to path reasoning and action/verification—not merely a graph picture behind an LLM.

The official track description emphasises multi-hop reasoning, graph queries/algorithms as agent tools, tool selection through MCP, actions based on graph evidence, and explainable results. The submission rules also require FalkorDB to be the primary graph database and require the repository, model/query documentation, demo, and setup/deployment instructions. These should guide our scope more directly than trying to make every production subsystem complete in the remaining hackathon time.

---

## 11. Final Status

- Scenario 1 foundation: current tests passing; investigation is not yet suspicious-login detection.
- Scenario 2 foundation: current tests passing; excessive-permission classification is currently seeded rather than independently derived.
- Scenario 3 foundation: current tests passing; blast radius is limited to the currently modelled path pattern.
- Scenario 4 foundation: current tests passing; containment is a synthetic graph-state simulation, with bounded verification coverage.
- Integration: the graph-service foundation still needs to be connected to the agent/MCP/frontend workflow and tested end to end.

**Exit rule:** Do not call the upgraded system production-ready. Call it a graph-powered security-agent prototype with explainable, synthetic-data investigations and simulated containment, and document the real-cloud integration, policy completeness, coverage, and operational controls that remain future work.
