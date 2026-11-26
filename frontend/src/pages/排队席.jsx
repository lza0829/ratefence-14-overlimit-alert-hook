import React, { useEffect, useState } from "react";
import { get } from "../api.js";
export default function 排队席() {
  const [rows, setRows] = useState([]);
  useEffect(() => { get("/排队席").then(setRows); }, []);
  return (
    <div>
      <h1 className="题">排队席</h1>
      <p className="述">策略=排队时的等候席位</p>
      <table><thead><tr><th>席号</th><th>路由</th><th>桶</th><th>状态</th><th>入席</th></tr></thead>
      <tbody>{rows.map((r) => <tr key={r.席号}><td>{r.席号}</td><td>{r.路由键}</td><td>{r.桶键}</td><td>{r.状态}</td><td>{r.入席时}</td></tr>)}</tbody></table>
    </div>
  );
}
