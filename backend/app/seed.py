from datetime import datetime, timezone

from app.db import 连接

STUBS = ['突发倍增', '多路由共桶', '排队超时出队', '降级正文版本', '白名单旁路', '桶热切换', '窗口滑动对照', '并发扣减半截', '路由优先级', '租户分桶', '冷启动预热', '熔断联动', '重试预算', '探针豁免', '配额借还', '超限告警钩', '路径参数归一', '方法覆盖', '夜间扩容', '影子配额']

建表 = """
CREATE TABLE IF NOT EXISTS 配额桶 (
  桶键 TEXT PRIMARY KEY,
  名称 TEXT NOT NULL,
  容量 INTEGER NOT NULL,
  窗口秒 INTEGER NOT NULL,
  策略 TEXT NOT NULL DEFAULT '拒绝',
  状态 TEXT NOT NULL DEFAULT '生效',
  更新时 TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS 路由册 (
  路由键 TEXT PRIMARY KEY,
  方法 TEXT NOT NULL,
  路径模式 TEXT NOT NULL,
  桶键 TEXT NOT NULL,
  状态 TEXT NOT NULL DEFAULT '生效',
  更新时 TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS 试流单 (
  单号 TEXT PRIMARY KEY,
  路由键 TEXT NOT NULL DEFAULT '',
  方法 TEXT NOT NULL,
  路径 TEXT NOT NULL,
  结果 TEXT NOT NULL,
  剩余配额 INTEGER NOT NULL DEFAULT 0,
  时刻 TEXT NOT NULL,
  说明 TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS 拒绝账 (
  编号 INTEGER PRIMARY KEY AUTOINCREMENT,
  路由键 TEXT NOT NULL,
  桶键 TEXT NOT NULL,
  路径 TEXT NOT NULL,
  时刻 TEXT NOT NULL,
  说明 TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS 排队席 (
  席号 TEXT PRIMARY KEY,
  路由键 TEXT NOT NULL,
  桶键 TEXT NOT NULL,
  状态 TEXT NOT NULL DEFAULT '等候',
  入席时 TEXT NOT NULL,
  出席时 TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS 降级本 (
  桶键 TEXT PRIMARY KEY,
  正文 TEXT NOT NULL,
  版本 INTEGER NOT NULL DEFAULT 1,
  更新时 TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS 空桩 (
  名 TEXT PRIMARY KEY,
  状态 TEXT NOT NULL DEFAULT '空桩'
);
CREATE TABLE IF NOT EXISTS 扣减计数 (
  桶键 TEXT PRIMARY KEY,
  窗起点 TEXT NOT NULL,
  已用 INTEGER NOT NULL DEFAULT 0
);
"""


def 现在() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def 初始化库() -> None:
    c = 连接()
    c.executescript(建表)
    c.execute("DELETE FROM 空桩")
    c.executemany("INSERT INTO 空桩(名, 状态) VALUES (?, ?)", [(s, "空桩") for s in STUBS])
    c.commit()
    c.close()
