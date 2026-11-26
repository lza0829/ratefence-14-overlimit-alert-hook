import React, { useEffect, useState } from "react";
import { get, post } from "../api.js";

export default function 总览() {
  const [d, setD] = useState(null);
  const [msg, setMsg] = useState("");
  const 刷 = () => get("/总览").then(setD).catch((e) => setMsg(String(e)));
  useEffect(() => { 刷(); }, []);
  return (
    <div>
      <h1 className="题">限流篱</h1>
      <p className="述">路由匹配后扣配额；超限拒绝或排队，降级正文可落账。不是灰度下发，不是发版闸。</p>
      <div className="行">
        <button className="主钮" onClick={() => post("/样例/主链").then(() => { setMsg("主链样例已灌"); 刷(); }).catch((e) => setMsg(String(e)))}>跑通主链</button>
        <button onClick={刷}>刷新</button>
      </div>
      {msg && <p className="述">{msg}</p>}
      {d && (
        <div className="卡组">
          {Object.entries(d).map(([k, v]) => (
            <div className="卡" key={k}><b>{v}</b><span>{k}</span></div>
          ))}
        </div>
      )}
    </div>
  );
}
