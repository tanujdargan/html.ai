import React from "react";
import "./App.css";

// IMPORTANT: Do NOT import the custom tag JS inside React.
// It must be loaded in index.html so the browser registers the element.

function App() {
  return (
    <div className="App" style={{ padding: "40px" }}>
      <h1>React + AI Optimization SDK Demo</h1>
      <p>This shows that &lt;ai-opt&gt; works inside React seamlessly.</p>

      <ai-opt>
        <div style={{ padding: "20px", background: "#eee", borderRadius: "8px" }}>
          <h2>React Section</h2>
          <p>This content can be replaced by your backend variant.</p>
        </div>
      </ai-opt>

      <br /><br />

      <reward-button variant="A" reward="7">
        Reward From React
      </reward-button>
    </div>
  );
}

export default App;