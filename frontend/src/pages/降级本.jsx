import React, { useEffect, useState } from "react";
import { get, post } from "../api.js";
export default function 降级本() {
  const [rows, setRows] = useState([]);
  const 刷 = () => get("/降级本").then(setRows);
  useEffect(() => { 刷(); }, []);
  return (
    <div>
      <h1 className="题">降级本</h1>
      <p className="述">超限拒绝时回写到拒绝账的正文</p>
      <div className="行">
        <button className="主钮" onClick={() => post("/样例/降级").then(刷)}>降级样例</button>
        <button onClick={刷}>刷新</button>
      </div>
      <table><thead><tr><th>桶键</th><th>版本</th><th>正文</th><th>更新时</th></tr></thead>
      <tbody>{rows.map((r) => <tr key={r.桶键}><td>{r.桶键}</td><td>{r.版本}</td><td>{r.正文}</td><td>{r.更新时}</td></tr>)}</tbody></table>
    </div>
  );
}
