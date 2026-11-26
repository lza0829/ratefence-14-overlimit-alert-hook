import React, { useEffect, useState } from "react";
import { get, post } from "../api.js";
export default function 试流台() {
  const [rows, setRows] = useState([]);
  const [last, setLast] = useState(null);
  const 刷 = () => get("/试流单").then(setRows);
  useEffect(() => { 刷(); }, []);
  return (
    <div>
      <h1 className="题">试流台</h1>
      <p className="述">向匹配路由发起探测；看放行 / 拒绝 / 排队</p>
      <div className="行">
        <button className="主钮" onClick={() => post("/样例/试流").then((x) => { setLast(x); 刷(); })}>试流样例</button>
        <button onClick={刷}>刷新</button>
      </div>
      {last && <p className="述">最近：{last.结果} · 剩余 {last.剩余配额}</p>}
      <table><thead><tr><th>单号</th><th>路径</th><th>结果</th><th>剩余</th><th>时刻</th></tr></thead>
      <tbody>{rows.map((r) => <tr key={r.单号}><td>{r.单号}</td><td>{r.路径}</td><td className={r.结果 === "放行" ? "好" : "坏"}>{r.结果}</td><td>{r.剩余配额}</td><td>{r.时刻}</td></tr>)}</tbody></table>
    </div>
  );
}
