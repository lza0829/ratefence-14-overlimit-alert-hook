import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.db import 连接, 样例目录
from app.seed import 现在

api = APIRouter()


def 行(r):
    return dict(r) if r is not None else None


@api.get("/健康")
def 健康():
    return {"ok": True, "服务": "限流篱"}


@api.get("/总览")
def 总览():
    c = 连接()
    out = {
        "配额桶": c.execute("SELECT COUNT(*) n FROM 配额桶").fetchone()["n"],
        "路由": c.execute("SELECT COUNT(*) n FROM 路由册 WHERE 状态='生效'").fetchone()["n"],
        "试流": c.execute("SELECT COUNT(*) n FROM 试流单").fetchone()["n"],
        "放行": c.execute("SELECT COUNT(*) n FROM 试流单 WHERE 结果='放行'").fetchone()["n"],
        "拒绝": c.execute("SELECT COUNT(*) n FROM 拒绝账").fetchone()["n"],
        "排队": c.execute("SELECT COUNT(*) n FROM 排队席 WHERE 状态='等候'").fetchone()["n"],
        "空桩": c.execute("SELECT COUNT(*) n FROM 空桩").fetchone()["n"],
    }
    c.close()
    return out


@api.get("/空桩")
def 空桩列表():
    c = 连接()
    rows = [行(r) for r in c.execute("SELECT * FROM 空桩 ORDER BY 名").fetchall()]
    c.close()
    return rows


@api.get("/配额桶")
def 列配额():
    c = 连接()
    rows = [行(r) for r in c.execute("SELECT * FROM 配额桶 ORDER BY 更新时 DESC").fetchall()]
    c.close()
    return rows


class 配额入(BaseModel):
    桶键: str
    名称: str
    容量: int = Field(ge=1)
    窗口秒: int = Field(ge=1)
    策略: str = "拒绝"


@api.post("/配额桶")
def 写配额(body: 配额入):
    if body.策略 not in ("拒绝", "排队"):
        raise HTTPException(400, "策略须为拒绝或排队")
    c = 连接()
    ts = 现在()
    c.execute(
        "INSERT INTO 配额桶(桶键,名称,容量,窗口秒,策略,状态,更新时) VALUES(?,?,?,?,?,'生效',?) "
        "ON CONFLICT(桶键) DO UPDATE SET 名称=excluded.名称,容量=excluded.容量,窗口秒=excluded.窗口秒,"
        "策略=excluded.策略,更新时=excluded.更新时",
        (body.桶键, body.名称, body.容量, body.窗口秒, body.策略, ts),
    )
    c.execute(
        "INSERT INTO 扣减计数(桶键,窗起点,已用) VALUES(?,?,0) ON CONFLICT(桶键) DO NOTHING",
        (body.桶键, ts),
    )
    c.commit()
    c.close()
    return {"ok": True, "桶键": body.桶键}


@api.get("/路由册")
def 列路由():
    c = 连接()
    rows = [行(r) for r in c.execute("SELECT * FROM 路由册 ORDER BY 更新时 DESC").fetchall()]
    c.close()
    return rows


class 路由入(BaseModel):
    路由键: str
    方法: str = "GET"
    路径模式: str
    桶键: str


@api.post("/路由册")
def 写路由(body: 路由入):
    c = 连接()
    if not c.execute("SELECT 1 FROM 配额桶 WHERE 桶键=?", (body.桶键,)).fetchone():
        c.close()
        raise HTTPException(400, "配额桶不存在")
    ts = 现在()
    c.execute(
        "INSERT INTO 路由册(路由键,方法,路径模式,桶键,状态,更新时) VALUES(?,?,?,?,'生效',?) "
        "ON CONFLICT(路由键) DO UPDATE SET 方法=excluded.方法,路径模式=excluded.路径模式,"
        "桶键=excluded.桶键,更新时=excluded.更新时",
        (body.路由键, body.方法.upper(), body.路径模式, body.桶键, ts),
    )
    c.commit()
    c.close()
    return {"ok": True, "路由键": body.路由键}


@api.get("/拒绝账")
def 列拒绝():
    c = 连接()
    rows = [行(r) for r in c.execute("SELECT * FROM 拒绝账 ORDER BY 编号 DESC LIMIT 100").fetchall()]
    c.close()
    return rows


@api.get("/排队席")
def 列排队():
    c = 连接()
    rows = [行(r) for r in c.execute("SELECT * FROM 排队席 ORDER BY 入席时 DESC LIMIT 100").fetchall()]
    c.close()
    return rows


@api.get("/降级本")
def 列降级():
    c = 连接()
    rows = [行(r) for r in c.execute("SELECT * FROM 降级本").fetchall()]
    c.close()
    return rows


class 降级入(BaseModel):
    桶键: str
    正文: str


@api.post("/降级本")
def 写降级(body: 降级入):
    c = 连接()
    if not c.execute("SELECT 1 FROM 配额桶 WHERE 桶键=?", (body.桶键,)).fetchone():
        c.close()
        raise HTTPException(400, "配额桶不存在")
    ts = 现在()
    old = c.execute("SELECT 版本 FROM 降级本 WHERE 桶键=?", (body.桶键,)).fetchone()
    ver = (old["版本"] + 1) if old else 1
    c.execute(
        "INSERT INTO 降级本(桶键,正文,版本,更新时) VALUES(?,?,?,?) "
        "ON CONFLICT(桶键) DO UPDATE SET 正文=excluded.正文,版本=excluded.版本,更新时=excluded.更新时",
        (body.桶键, body.正文, ver, ts),
    )
    c.commit()
    c.close()
    return {"ok": True, "版本": ver}


@api.get("/试流单")
def 列试流():
    c = 连接()
    rows = [行(r) for r in c.execute("SELECT * FROM 试流单 ORDER BY 时刻 DESC LIMIT 100").fetchall()]
    c.close()
    return rows


class 试流入(BaseModel):
    方法: str = "GET"
    路径: str


def _匹配路由(c, 方法: str, 路径: str):
    rows = c.execute(
        "SELECT * FROM 路由册 WHERE 状态='生效' AND 方法=? ORDER BY length(路径模式) DESC",
        (方法.upper(),),
    ).fetchall()
    for r in rows:
        pat = r["路径模式"]
        if pat.endswith("*"):
            if 路径.startswith(pat[:-1]):
                return r
        elif 路径 == pat:
            return r
    return None


def _扣减(c, 桶) -> tuple[bool, int, str]:
    """返回 (是否放行, 剩余, 说明)。"""
    ts = 现在()
    cnt = c.execute("SELECT * FROM 扣减计数 WHERE 桶键=?", (桶["桶键"],)).fetchone()
    if not cnt:
        c.execute("INSERT INTO 扣减计数(桶键,窗起点,已用) VALUES(?,?,0)", (桶["桶键"], ts))
        cnt = c.execute("SELECT * FROM 扣减计数 WHERE 桶键=?", (桶["桶键"],)).fetchone()
    # 简化：固定窗——窗起点距今超过窗口秒则重置（用字符串比较粗糙，冒烟够用）
    try:
        start = datetime.strptime(cnt["窗起点"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        if (now - start).total_seconds() >= 桶["窗口秒"]:
            c.execute("UPDATE 扣减计数 SET 窗起点=?, 已用=0 WHERE 桶键=?", (ts, 桶["桶键"]))
            已用 = 0
        else:
            已用 = cnt["已用"]
    except Exception:
        已用 = cnt["已用"]
    if 已用 >= 桶["容量"]:
        return False, 0, "配额耗尽"
    c.execute("UPDATE 扣减计数 SET 已用=已用+1 WHERE 桶键=?", (桶["桶键"],))
    剩余 = 桶["容量"] - 已用 - 1
    return True, 剩余, "扣减成功"


@api.post("/试流")
def 试流(body: 试流入):
    c = 连接()
    路由 = _匹配路由(c, body.方法, body.路径)
    单号 = "TF-" + uuid.uuid4().hex[:10]
    ts = 现在()
    if not 路由:
        c.execute(
            "INSERT INTO 试流单(单号,路由键,方法,路径,结果,剩余配额,时刻,说明) VALUES(?,?,?,?,?,?,?,?)",
            (单号, "", body.方法.upper(), body.路径, "未命中", 0, ts, "无匹配路由"),
        )
        c.commit()
        c.close()
        return {"单号": 单号, "结果": "未命中", "剩余配额": 0}
    桶 = c.execute("SELECT * FROM 配额桶 WHERE 桶键=?", (路由["桶键"],)).fetchone()
    if not 桶 or 桶["状态"] != "生效":
        c.close()
        raise HTTPException(400, "绑定配额桶不可用")
    ok, 剩余, 说明 = _扣减(c, 桶)
    if ok:
        结果 = "放行"
        c.execute(
            "INSERT INTO 试流单(单号,路由键,方法,路径,结果,剩余配额,时刻,说明) VALUES(?,?,?,?,?,?,?,?)",
            (单号, 路由["路由键"], body.方法.upper(), body.路径, 结果, 剩余, ts, 说明),
        )
    else:
        if 桶["策略"] == "排队":
            结果 = "排队"
            席号 = "Q-" + uuid.uuid4().hex[:10]
            c.execute(
                "INSERT INTO 排队席(席号,路由键,桶键,状态,入席时) VALUES(?,?,?,'等候',?)",
                (席号, 路由["路由键"], 桶["桶键"], ts),
            )
            c.execute(
                "INSERT INTO 试流单(单号,路由键,方法,路径,结果,剩余配额,时刻,说明) VALUES(?,?,?,?,?,?,?,?)",
                (单号, 路由["路由键"], body.方法.upper(), body.路径, 结果, 0, ts, f"入席 {席号}"),
            )
        else:
            结果 = "拒绝"
            降 = c.execute("SELECT 正文 FROM 降级本 WHERE 桶键=?", (桶["桶键"],)).fetchone()
            说明2 = 降["正文"] if 降 else 说明
            c.execute(
                "INSERT INTO 拒绝账(路由键,桶键,路径,时刻,说明) VALUES(?,?,?,?,?)",
                (路由["路由键"], 桶["桶键"], body.路径, ts, 说明2),
            )
            c.execute(
                "INSERT INTO 试流单(单号,路由键,方法,路径,结果,剩余配额,时刻,说明) VALUES(?,?,?,?,?,?,?,?)",
                (单号, 路由["路由键"], body.方法.upper(), body.路径, 结果, 0, ts, 说明2),
            )
    c.commit()
    c.close()
    return {"单号": 单号, "结果": 结果, "剩余配额": 剩余 if ok else 0, "路由键": 路由["路由键"]}


def _读样例(名: str) -> dict:
    p = 样例目录 / f"{名}.json"
    if not p.exists():
        raise HTTPException(404, f"缺少样例 {名}")
    return json.loads(p.read_text(encoding="utf-8"))


@api.post("/样例/配额")
def 灌配额样例():
    data = _读样例("配额样例")
    return 写配额(配额入(**data))


@api.post("/样例/路由")
def 灌路由样例():
    data = _读样例("路由样例")
    return 写路由(路由入(**data))


@api.post("/样例/降级")
def 灌降级样例():
    data = _读样例("降级样例")
    return 写降级(降级入(**data))


@api.post("/样例/试流")
def 灌试流样例():
    data = _读样例("试流样例")
    return 试流(试流入(**data))


@api.post("/样例/主链")
def 灌主链():
    灌配额样例()
    灌降级样例()
    灌路由样例()
    outs = []
    for _ in range(5):
        outs.append(灌试流样例())
    return {"ok": True, "试流": outs}
