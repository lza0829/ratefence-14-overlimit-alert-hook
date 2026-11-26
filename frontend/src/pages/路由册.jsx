import React, { useEffect, useState } from "react";
import { get, post } from "../api.js";
export default function 路由册() {
  const [rows, setRows] = useState([]);
  const 刷 = () => get("/路由册").then(setRows);
  useEffect(() => { 刷(); }, []);
  return (
    <div>
      <h1 className="题">路由册</h1>
      <p className="述">方法 + 路径模式绑定配额桶</p>
      <div className="行">
        <button className="主钮" onClick={() => post("/样例/路由").then(刷)}>路由样例</button>
        <button onClick={刷}>刷新</button>
      </div>
      <table><thead><tr><th>路由键</th><th>方法</th><th>路径</th><th>桶键</th><th>状态</th></tr></thead>
      <tbody>{rows.map((r) => <tr key={r.路由键}><td>{r.路由键}</td><td>{r.方法}</td><td>{r.路径模式}</td><td>{r.桶键}</td><td>{r.状态}</td></tr>)}</tbody></table>
    </div>
  );
}
