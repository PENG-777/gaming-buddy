"""
NL2SQL 自由查询工具（自由查询 Agent 专用, 只读兜底）

预置统计工具覆盖不到的细粒度问题由本工具回答: LLM 先调 get_table_schemas 了解
白名单表结构, 再生成一条 MySQL SELECT 语句调 run_select_sql 执行。

安全防护(五重):
1. sqlparse 解析且语句类型必须为 SELECT(拒绝 INSERT/UPDATE/DELETE/DDL)
2. 禁止分号多语句 / 注入语句
3. 禁止 INTO OUTFILE/DUMPFILE/FOR UPDATE/LOCK 等危险片段
4. 表名白名单: 只允许业务表(排除 menu/role/role_menu 等权限结构表)
5. 无 LIMIT 自动包裹外层 LIMIT 1000, 结果剔除 password 等敏感列
"""
import json  # 标准库: 结果序列化
import re  # 标准库: 正则(表名提取/危险片段检测)

import sqlparse  # 第三方: SQL 解析与语句类型判定
from langchain_core.tools import tool  # 第三方: 工具装饰器
from sqlalchemy import text  # 第三方: 原生 SQL 文本

from core.database import SessionLocal  # 项目内: Session 工厂

# 结果行数上限(自动包裹 LIMIT)
_MAX_ROWS = 1000
# 单次返回给 LLM 的最大字符数
_MAX_RESULT_CHARS = 8000
# 结果集中必须剔除的敏感列(不区分大小写)
_SENSITIVE_COLS = {"password"}

# 业务表白名单: 表名 -> 结构摘要(供 LLM 生成 SQL, 敏感列与权限表不入内)
# 字段口径: 名称 + 简要说明; 订单成交口径 status in (booked/ongoing/completed/refunding)
_TABLE_SCHEMAS = {
    "user": "user(user_id 用户ID, user_name 用户名, sex 性别(0男1女), avatar 头像, role_id 角色ID(1管理员2普通用户3陪玩师4客服), balance 钱包余额元, create_time 注册时间)",
    "companion": "companion(companion_id 陪玩师ID, user_id 关联用户ID, nick_name 昵称, gender 性别(0男1女), age 年龄, city 城市, voice 声线, price 起步价元/小时, intro 简介, tags 标签逗号分隔, certified 认证(0未1已), status 状态(0启用1停用), main_game_id 主游戏ID, main_rank 主游戏段位, create_time 入驻时间)",
    "companion_game": "companion_game(companion_id 陪玩师ID, game_id 游戏ID, game_rank 该游戏段位)",
    "companion_service": "companion_service(companion_id 陪玩师ID, service_id 服务项目ID, price 该服务价格元/小时, description 服务说明)",
    "game_category": "game_category(game_id 游戏ID, game_name 游戏名, tags 标签, description 描述, status 状态(0启用1停用), create_time 创建时间)",
    "service_item": "service_item(service_id 服务项目ID, service_name 服务名, description 描述, status 状态(0启用1停用))",
    "companion_order": "companion_order(order_id 订单ID, order_no 订单号, user_id 下单用户ID, companion_id 陪玩师ID, service_name 服务名快照, price 单价元/小时, hours 时长小时, service_date 预约日期, start_hour 开始时段, note 备注, coupon_name 优惠券名, coupon_amount 优惠金额元, gross_amount 原价元, amount 实付元, pay_method 支付方式(balance/wechat/alipay), status 状态(pending待支付/booked待开始/ongoing进行中/completed已完成/refunding退款中/cancelled已取消; 成交口径为后四种), pay_time 支付时间, review_rating 评价星级1-5, review_content 评价内容, create_time 下单时间)",
    "complaint": "complaint(complaint_id 投诉ID, order_id 订单ID, user_id 投诉用户ID, complaint_type 投诉类型, content 投诉内容, status 处理状态(0待处理1已处理), handle_result 处理结果, reply 处理说明, create_time 提交时间)",
    "coupon": "coupon(coupon_id 优惠券ID, coupon_name 券名, amount 面额元, threshold 使用门槛元(0无门槛), valid_days 领取后有效天数, per_limit 每人限领, total_count 发放总量(0不限), status 状态(0启用1停用), create_time 创建时间)",
    "user_coupon": "user_coupon(id 记录ID, user_id 用户ID, coupon_id 优惠券ID, status 状态(0未使用1已使用), receive_time 领取时间, expire_time 过期时间, use_time 使用时间)",
    "wallet_transaction": "wallet_transaction(tx_id 流水ID, user_id 用户ID, type 类型(recharge充值/consume消费/refund退款/reward打赏/adjust调整), amount 变动金额元(正收入负支出), balance_after 变动后余额, note 备注, create_time 时间)",
    "gift": "gift(gift_id 礼物ID, gift_name 礼物名, price 价格元, status 状态, create_time 创建时间)",
    "reward": "reward(reward_id 打赏ID, user_id 打赏用户ID, companion_id 陪玩师ID, gift_name 礼物名快照, amount 打赏金额元, create_time 打赏时间)",
    "follow": "follow(id 记录ID, user_id 用户ID, companion_id 陪玩师ID, create_time 关注时间)",
    "notice": "notice(notice_id 公告ID, title 标题, notice_type 类型(保障/活动/上新/安全), content 正文, status 状态(0发布1撤下), create_time 发布时间)",
    "faq": "faq(faq_id ID, category 分组, question 问题, answer 答案, sort 排序, status 状态(0显示1隐藏))",
    "feedback": "feedback(feedback_id 反馈ID, user_id 用户ID, feedback_type 类型, content 内容, status 处理状态(0待处理1已处理), reply 回复, create_time 提交时间)",
    "banner": "banner(banner_id 轮播图ID, title 标题, subtitle 副标题, status 状态, create_time 创建时间)",
}

# 危险片段(大写不敏感): 文件导出/锁表/注释注入
_FORBIDDEN_PATTERNS = re.compile(  # 命中任一片段即拒绝执行
    r"(?i)\b(into\s+(outfile|dumpfile)|for\s+update|lock\s+in|load_file|information_schema|`\`|/\*|\*/|--|;)"
)

# 表名提取: from/join/into/update 后的标识符(反引号可选)
_TABLE_REF_PATTERN = re.compile(r"(?i)\b(?:from|join|into|update)\s+`?([a-z_][a-z0-9_]*)`?")  # 用于白名单比对


def build_sql_tools() -> list:
    """自由查询 Agent 工具集: 表结构查询 + 只读 SQL 执行"""

    @tool
    def get_table_schemas() -> str:
        """获取可查询业务表的结构说明(白名单表清单 + 每张表的字段/口径/状态码说明)。编写 SQL 前必须先调用本工具了解表结构。"""
        return json.dumps(_TABLE_SCHEMAS, ensure_ascii=False)  # 白名单结构说明直接序列化返回

    @tool
    def run_select_sql(sql: str) -> str:
        """执行一条只读 MySQL SELECT 查询并返回 JSON 结果(最多 1000 行)。要求: 只查白名单业务表; 禁止多语句; 涉及订单金额时注意成交口径为 status in (booked,ongoing,completed,refunding); 不要查询用户密码等敏感信息。"""
        error = _validate(sql)  # 执行前五重安全校验
        if error:  # 校验未通过
            return json.dumps({"error": error, "hint": "请调整 SQL 后重试, 仅允许单条 SELECT 且只能查白名单业务表"}, ensure_ascii=False)  # 拒绝原因交还 LLM 自行调整
        final_sql = sql.strip().rstrip(";").strip()  # 去首尾空白与结尾分号(多语句已被拒, 双保险)
        if not re.search(r"(?i)\blimit\s+\d+", final_sql):  # 无显式 LIMIT 则外层兑底
            final_sql = f"SELECT * FROM ({final_sql}) AS _t LIMIT {_MAX_ROWS}"  # 包裹子查询强制限行
        try:
            with SessionLocal() as db:  # 短会话: 工具执行独立于请求生命周期
                result = db.execute(text(final_sql))  # 以原生 SQL 执行(已过白名单校验)
                rows = [dict(r._mapping) for r in result.fetchmany(_MAX_ROWS)]  # 最多取 _MAX_ROWS 行, 行转字典
        except Exception as e:  # SQL 语法/执行错误交还 LLM 自行修正
            return json.dumps({"error": f"SQL 执行失败: {e}", "hint": "请检查表名字段名与语法后重试"}, ensure_ascii=False)
        for row in rows:  # 结果剔除敏感列(防 SELECT * 带出)
            for col in list(row.keys()):  # 复制键列表再删(遍历中不可直接改字典)
                if col.lower() in _SENSITIVE_COLS:  # 不区分大小写比对敏感列名
                    row.pop(col)  # 从结果中移除该列
        payload = json.dumps({"rowCount": len(rows), "rows": rows}, ensure_ascii=False, default=str)  # 行数 + 数据整体序列化
        if len(payload) > _MAX_RESULT_CHARS:  # 超长截断保护 LLM 上下文
            payload = payload[:_MAX_RESULT_CHARS] + "\n...(结果过长已截断)"
        return payload

    def _validate(sql: str) -> str | None:
        """执行前校验: 返回 None 表示通过, 否则返回拒绝原因"""
        stripped = (sql or "").strip()  # 容错 None 输入并去首尾空白
        if not stripped:
            return "SQL 不能为空"
        statements = [s for s in sqlparse.split(stripped) if s.strip()]  # 按分号切分并过滤空语句
        if len(statements) != 1:  # 多语句(分号拼接)直接拒绝
            return "仅允许单条 SQL 语句"
        parsed = sqlparse.parse(statements[0])  # 解析唯一语句
        if not parsed or parsed[0].get_type() != "SELECT":  # 语句类型必须是 SELECT
            return "仅允许 SELECT 查询"
        if _FORBIDDEN_PATTERNS.search(stripped):  # 危险片段检测(含注释与分号)
            return "SQL 包含不允许的片段(多语句/文件导出/锁表/注释)"
        tables = {m.lower() for m in _TABLE_REF_PATTERN.findall(stripped)}  # 提取引用的表名(统一小写)
        unknown = tables - set(_TABLE_SCHEMAS)  # 白名单校验: 求差集
        if unknown:
            return f"存在白名单之外的表: {', '.join(sorted(unknown))}"  # 列出越权表名供 LLM 修正
        return None  # 全部校验通过

    return [get_table_schemas, run_select_sql]