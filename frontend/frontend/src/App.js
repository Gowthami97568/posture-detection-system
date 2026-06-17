import React, { useEffect, useState } from "react";

function App() {
  const [data, setData] = useState({ current_bad: 0, total_bad: 0 });

  useEffect(() => {
    const interval = setInterval(() => {
      fetch("http://127.0.0.1:5000/posture")
        .then((res) => res.json())
        .then((data) => setData(data))
        .catch((err) => console.log(err));
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ textAlign: "center", marginTop: "50px" }}>
      <h1>🧠 Posture Dashboard</h1>

      <h2 style={{ color: "red" }}>
        ⏱️ Current Bad Time: {data.current_bad}s
      </h2>

      <h2 style={{ color: "blue" }}>
        📊 Total Bad Time: {data.total_bad}s
      </h2>
    </div>
  );
}

export default App;