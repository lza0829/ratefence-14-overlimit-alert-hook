import React, { useEffect, useState } from "react";
import { get, post } from "../api.js";
export default function 配额桶() {
  const [rows, setRows] = useState([]);
  const 刷 = () => get("/配额桶").then(setRows);
  useEffect(() => { 刷(); }, []);
  return (
    <div>
      <h1 className="题">配额桶</h1>
      <p className="述">容量 · 窗口秒 · 策略（拒绝 / 排队）</p>
      <div className="行">
        <button className="主钮" onClick={() => post("/样例/配额").then(刷)}>配额样例</button>
        <button onClick={刷}>刷新</button>
      </div>
      <table><thead><tr><th>桶键</th><th>名称</th><th>容量</th><th>窗口秒</th><th>策略</th><th>状态</th></tr></thead>
      <tbody>{rows.map((r) => <tr key={r.桶键}><td>{r.桶键}</td><td>{r.名称}</td><td>{r.容量}</td><td>{r.窗口秒}</td><td>{r.策略}</td><td>{r.状态}</td></tr>)}</tbody></table>
    </div>
  );
}
