import React, { useEffect, useState } from "react";
import { get } from "../api.js";
export default function 拒绝账() {
  const [rows, setRows] = useState([]);
  useEffect(() => { get("/拒绝账").then(setRows); }, []);
  return (
    <div>
      <h1 className="题">拒绝账</h1>
      <p className="述">策略=拒绝时的超限记录</p>
      <table><thead><tr><th>#</th><th>路由</th><th>桶</th><th>路径</th><th>说明</th><th>时刻</th></tr></thead>
      <tbody>{rows.map((r) => <tr key={r.编号}><td>{r.编号}</td><td>{r.路由键}</td><td>{r.桶键}</td><td>{r.路径}</td><td>{r.说明}</td><td>{r.时刻}</td></tr>)}</tbody></table>
    </div>
  );
}
