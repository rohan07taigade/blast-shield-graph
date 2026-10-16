import ReactMarkdown from "react-markdown";
import { useEffect, useMemo, useState } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  // MiniMap,
  MarkerType,
} from "@xyflow/react";

import "@xyflow/react/dist/style.css";
import "./App.css";

const API = "http://127.0.0.1:8000";

async function apiRequest(url, options = {}) {
  const response = await fetch(url, options);
  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    const detail = data.detail;
    throw new Error(
      typeof detail === "string"
        ? detail
        : JSON.stringify(detail || `HTTP ${response.status}`)
    );
  }

  return data;
}

export default function App() {
  const [alerts, setAlerts] = useState([]);
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [investigation, setInvestigation] = useState(null);
  const [apiOnline, setApiOnline] = useState(false);
  const [loading, setLoading] = useState(true);
  const [investigating, setInvestigating] = useState(false);
  const [error, setError] = useState("");
  const [agentAnswer, setAgentAnswer] = useState("");
  const [agentError, setAgentError] = useState("");
  const [agentLoading, setAgentLoading] = useState(false);

  useEffect(() => {
    let active = true;

    async function initialise() {
      try {
        await apiRequest(`${API}/api/health`);
        const result = await apiRequest(`${API}/api/alerts`);

        if (!active) return;

        setApiOnline(true);
        setAlerts(result.items);
        setSelectedAlert(result.items[0] || null);
      } catch {
        if (!active) return;
        setApiOnline(false);
        setError(
          "Cannot reach FastAPI. Check that your backend is running."
        );
      } finally {
        if (active) setLoading(false);
      }
    }

    initialise();

    return () => {
      active = false;
    };
  }, []);


  async function investigate() {
    if (!selectedAlert) return;

    setInvestigating(true);
    setInvestigation(null);
    setAgentAnswer("");
    setAgentError("");
    setError("");

    try {
      // First retrieve structured data for the graph UI.
      const result = await apiRequest(
        `${API}/api/investigations`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            alert_id: selectedAlert.id,
          }),
        }
      );

      setInvestigation(result);

      // Then ask Gemini to investigate through MCP.
      setAgentLoading(true);

      try {
        const agentResult = await apiRequest(
          `${API}/api/agent/investigate`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              alert_id: selectedAlert.id,
            }),
          }
        );

        setAgentAnswer(agentResult.answer);
      } catch (err) {
        setAgentError(
          err.message || "Gemini investigation failed."
        );
      } finally {
        setAgentLoading(false);
      }
    } catch (err) {
      setError(
        err.message || "Could not retrieve the investigation."
      );
    } finally {
      setInvestigating(false);
    }
  }


  const path = investigation?.paths?.[0];

  const nodes = useMemo(() => {
    if (!path) return [];

    return path.nodes.map((item, index) => ({
      id: item.id,
      position: {
        x: index * 190,
        y: index % 2 === 0 ? 45 : 155,
      },
      data: {
        label: `${item.label}\n${item.type}`,
      },
      style: {
        width: 155,
        padding: 12,
        whiteSpace: "pre-line",
        textAlign: "center",
        borderRadius: 10,
        color: "#edf3ff",
        background:
          item.type === "DataAsset"
            ? "#472332"
            : item.type === "IAMRole"
              ? "#202f4d"
              : "#17313a",
        border:
          item.type === "DataAsset"
            ? "1px solid #f18aa8"
            : "1px solid #486681",
        fontSize: 12,
      },
    }));
  }, [path]);

  const edges = useMemo(() => {
    if (!path) return [];

    return path.edges.map((edge, index) => ({
      id: `edge-${index}`,
      source: edge.source,
      target: edge.target,
      label: edge.type,
      type: "smoothstep",
      markerEnd: {
        type: MarkerType.ArrowClosed,
        color: "#8ca8ca",
      },
      style: {
        stroke: "#8ca8ca",
        strokeWidth: 2,
      },
      labelStyle: {
        fill: "#dbe7fa",
        fontSize: 10,
      },
      labelBgStyle: {
        fill: "#101a2b",
      },
    }));
  }, [path]);

  const riskScore = Math.max(
    0,
    Math.min(100, investigation?.risk_score ?? 0)
  );

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">
          <div className="brand-logo">B</div>
          <div>
            <strong>BlastShield</strong>
            <p>Graph-powered cloud security</p>
          </div>
        </div>

        <div className="connection">
          <span className={apiOnline ? "dot online" : "dot"} />
          {apiOnline ? "API connected" : "API disconnected"}
        </div>
      </header>

      <section className="page-heading">
        <div>
          <p className="eyebrow">SECURITY OPERATIONS</p>
          <h1>Investigation workspace</h1>
          <p className="muted">
            Investigate security findings and trace potential
            access paths to critical resources.
          </p>
        </div>
        <span className="mock-label">MOCK DATA</span>
      </section>

      {error && <div className="error-banner">{error}</div>}

      <div className="workspace">
        <aside className="sidebar panel">
          <div className="section-heading">
            <span>INCIDENT QUEUE</span>
            <span className="count">{alerts.length}</span>
          </div>

          {loading && <p className="muted">Loading incidents...</p>}

          {!loading &&
            alerts.map((alert) => (
              <button
                key={alert.id}
                className={`incident ${selectedAlert?.id === alert.id ? "selected" : ""
                  }`}
                onClick={() => {
                  setSelectedAlert(alert);
                  setInvestigation(null);
                  setAgentAnswer("");
                  setAgentError("");
                  setAgentLoading(false);
                  setError("");
                }}
              >
                <span className="incident-id">{alert.id}</span>
                <strong>{alert.title}</strong>
                <span className="incident-status">{alert.status}</span>
              </button>
            ))}

          {!loading && alerts.length === 0 && (
            <p className="muted">No incidents available.</p>
          )}

          <div className="sidebar-note">
            <strong>Development mode</strong>
            <p>
              Findings currently come from the mock service.
              Live graph integration is a later step.
            </p>
          </div>
        </aside>

        <main className="main-content">
          <section className="incident-header">
            <div>
              <p className="eyebrow">SELECTED INCIDENT</p>
              <h2>{selectedAlert?.id || "No incident selected"}</h2>
              <p className="muted">
                {selectedAlert?.title || "Select an incident to begin."}
              </p>
            </div>

            <button
              className="primary-button"
              disabled={!selectedAlert || investigating || !apiOnline}
              onClick={investigate}
            >
              {investigating ? "Investigating..." : "Investigate alert"}
            </button>
          </section>

          {!investigation && !investigating && (
            <section className="panel empty-state">
              <div className="empty-icon">⌕</div>
              <h3>Ready to investigate</h3>
              <p className="muted">
                Select an incident and investigate it to display
                the findings returned by the API.
              </p>
            </section>
          )}

          {investigating && (
            <section className="panel empty-state">
              <h3>Retrieving investigation</h3>
              <p className="muted">
                Requesting results from the mock backend...
              </p>
            </section>
          )}

          {investigation && (
            <>
              <section className="panel findings">
                <div className="finding-heading">
                  <div>
                    <p className="eyebrow">INVESTIGATION RESULT</p>
                    <h3>
                      {investigation.outcome === "path_found"
                        ? "Potential access path identified"
                        : "No qualifying path in mock graph"}
                    </h3>
                  </div>

                  <span
                    className={`severity ${investigation.severity.toLowerCase()}`}
                  >
                    {investigation.severity}
                  </span>
                </div>

                <p>{investigation.summary}</p>

                <div className="risk-heading">
                  <span>Illustrative risk score</span>
                  <strong>{riskScore}/100</strong>
                </div>

                <div className="risk-track">
                  <div
                    className="risk-fill"
                    style={{ width: `${riskScore}%` }}
                  />
                </div>
              </section>


              <section className="panel agent-panel">
                <div className="section-title">
                  <div>
                    <p className="eyebrow">AI INVESTIGATION</p>
                    <h3>Gemini's explanation</h3>
                  </div>

                  <span className="source-label">MCP · MOCK DATA</span>
                </div>

                {agentLoading && (
                  <p className="muted">
                    Gemini is reviewing the investigation evidence...
                  </p>
                )}

                {agentError && (
                  <div className="error-banner">
                    AI explanation unavailable: {agentError}
                  </div>
                )}

                {!agentLoading && agentAnswer && (
                  <div className="markdown-answer">
                    <ReactMarkdown>{agentAnswer}</ReactMarkdown>
                  </div>
                )}

                {!agentLoading && !agentAnswer && !agentError && (
                  <p className="muted">
                    Run an investigation to view the AI explanation.
                  </p>
                )}
              </section>


              <section className="panel">
                <div className="section-title">
                  <div>
                    <p className="eyebrow">GRAPH EVIDENCE</p>
                    <h3>Represented access path</h3>
                  </div>
                  <span className="source-label">
                    {investigation.data_source}
                  </span>
                </div>

                {path ? (
                  <div className="graph-canvas">
                    <ReactFlow
                      nodes={nodes}
                      edges={edges}
                      fitView
                      fitViewOptions={{ padding: 0.15 }}
                      nodesDraggable={false}
                      nodesConnectable={false}
                    >
                      <Background color="#29384c" />
                      <Controls />
                      {/* <MiniMap /> */}
                    </ReactFlow>
                  </div>
                ) : (
                  <div className="no-path">
                    <h4>No qualifying path returned</h4>
                    <p>
                      This mock result has no qualifying path to
                      critical data. That does not prove a real
                      environment is safe.
                    </p>
                  </div>
                )}
              </section>

              <div className="detail-grid">
                <section className="panel">
                  <div className="section-title">
                    <h3>Investigation evidence</h3>
                  </div>

                  {investigation.evidence.map((item, index) => (
                    <div className="evidence-item" key={index}>
                      <span>{index + 1}</span>
                      <p>{item}</p>
                    </div>
                  ))}
                </section>

                <section className="panel">
                  <div className="section-title">
                    <h3>Proposed response</h3>
                    <span className="source-label">PREVIEW</span>
                  </div>

                  {investigation.proposed_actions.length > 0 ? (
                    investigation.proposed_actions.map((action) => (
                      <div className="action-card" key={action.action_id}>
                        <span className="action-type">
                          {action.action_type}
                        </span>
                        <h4>{action.title}</h4>
                        <p>{action.reason}</p>
                        <p className="muted">
                          Target: {action.target_id}
                        </p>
                      </div>
                    ))
                  ) : (
                    <p className="muted">
                      No response action was proposed by the mock service.
                    </p>
                  )}
                </section>
              </div>

              {investigation.warnings.length > 0 && (
                <section className="warning-panel">
                  <h3>Important limitations</h3>
                  {investigation.warnings.map((warning, index) => (
                    <p key={index}>• {warning}</p>
                  ))}
                </section>
              )}
            </>
          )}
        </main>
      </div>
    </div>
  );
}
