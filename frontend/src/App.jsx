import React from "react";
import { NavLink, Route, Routes } from "react-router-dom";
import 总览 from "./pages/总览.jsx";
import 配额桶 from "./pages/配额桶.jsx";
import 路由册 from "./pages/路由册.jsx";
import 试流台 from "./pages/试流台.jsx";
import 拒绝账 from "./pages/拒绝账.jsx";
import 排队席 from "./pages/排队席.jsx";
import 降级本 from "./pages/降级本.jsx";

const 链 = [
  ["/", "总览"],
  ["/配额桶", "配额桶"],
  ["/路由册", "路由册"],
  ["/试流台", "试流台"],
  ["/拒绝账", "拒绝账"],
  ["/排队席", "排队席"],
  ["/降级本", "降级本"],
];

export default function App() {
  return (
    <div className="壳">
      <aside className="侧">
        <div>
          <div className="侧英">Ratefence</div>
          <div className="侧名">限流篱</div>
          <div className="侧骨">路由 → 扣减 → 超限拒绝/排队 → 降级落账</div>
        </div>
        <nav className="侧导">
          {链.map(([to, l]) => (
            <NavLink key={to} to={to} end={to === "/"} className={({ isActive }) => (isActive ? "亮" : "")}>
              {l}
            </NavLink>
          ))}
        </nav>
        <div className="侧脚">INFRA · SRE · :6900</div>
      </aside>
      <main className="主">
        <Routes>
          <Route path="/" element={<总览 />} />
          <Route path="/配额桶" element={<配额桶 />} />
          <Route path="/路由册" element={<路由册 />} />
          <Route path="/试流台" element={<试流台 />} />
          <Route path="/拒绝账" element={<拒绝账 />} />
          <Route path="/排队席" element={<排队席 />} />
          <Route path="/降级本" element={<降级本 />} />
        </Routes>
      </main>
    </div>
  );
}
