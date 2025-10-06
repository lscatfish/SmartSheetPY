import dis, types, sys, functools


class ExitWhenTriggered(Exception):
    """探针触发后用于跳出函数的执行"""
    pass


# ------------------ 探针钩子 ------------------
def _probe_hook(frame, target_type, target_key, expect, ns):
    """
    在每条语句前运行：
      frame : 当前帧（探针插入时把当前帧作为常量塞进来）
      ns    : 装饰器传来的命名空间（用于全局变量）
    """
    # 1. 按类型抓值
    val = None
    if target_type == 'local':
        val = frame.f_locals.get(target_key, None)
    elif target_type == 'param':
        val = frame.f_locals.get(target_key, None)
    elif target_type == 'global':
        val = frame.f_globals.get(target_key, None)
    elif target_type == 'self_attr':
        self = frame.f_locals.get('self', None)
        if self is not None:
            val = getattr(self, target_key, None)
    # 2. 判条件
    if val is None:
        return
    hit = expect(val) if callable(expect) else val == expect
    if hit:
        raise ExitWhenTriggered


# ------------------  3.11+ 字节码注入 ------------------
def _instrument(func, target_type, target_key, expect):
    co = func.__code__
    # 1. 预生成偏函数，字节码里只需传 frame
    probe_fn = functools.partial(_probe_hook,
        target_type = target_type,
        target_key = target_key,
        expect = expect,
        ns = None)
    new_consts = co.co_consts + (probe_fn,)  # 常量下表 probe_id
    probe_id = len(co.co_consts)

    bytecode = bytearray(co.co_code)
    stmt_offs = [0]
    for instr in dis.get_instructions(co):
        if instr.is_jump_target and instr.offset != 0:
            stmt_offs.append(instr.offset)

    CALL_CACHE = bytes([
        dis.opmap['CALL'], 1, 0,  # argc=1
        dis.opmap['CACHE'], 0, 0
    ])

    for off in reversed(stmt_offs):
        patch = bytes([
            dis.opmap['LOAD_CONST'], probe_id,  # 偏函数
            dis.opmap['LOAD_CONST'], 0,  # 占位，运行时用 frame
        ]) + CALL_CACHE + bytes([dis.opmap['POP_TOP'], 0])
        bytecode[off:off] = patch

    new_code = co.replace(co_code = bytes(bytecode), co_consts = new_consts)
    return types.FunctionType(new_code,
        func.__globals__,
        func.__name__,
        func.__defaults__,
        func.__closure__)


# ------------------ 装饰器 ------------------
def watch(target_type, target_key, expect):
    """
    target_type : 'local' | 'param' | 'global' | 'self_attr'
    target_key  : 变量名（self_attr 可写 a.b.c）
    expect      : 值 或 lambda
    """
    if target_type not in {'local', 'param', 'global', 'self_attr'}:
        raise ValueError('bad target_type')

    def deco(func):
        # 1. 注入探针
        func = _instrument(func, target_type, target_key, expect)

        # 2. 包一层 try/except 让触发时静默返回
        @functools.wraps(func)
        def wrapper(*a, **k):
            try:
                return func(*a, **k)
            except ExitWhenTriggered:
                return None

        # 把元数据搬回来，避免“不是方法”
        functools.update_wrapper(wrapper, func)
        return wrapper

    return deco


# 1. 全局变量
G = 0


# 2. 类成员
class Counter:
    def __init__(self):
        self.n = 0

    @watch('self_attr', 'n', 3)
    def inc(self):
        while self.n < 5:
            self.n += 1
            print('inc', self.n)
            self.helper()  # 子函数里 self.n=3 不会触发
        return self.n

    def helper(self):
        self.n = 3
        print('helper set n=3, but NOT exit')


# 3. 局部 / 参数 / 递归
@watch('local', 'x', lambda v: v <= 0)
def dfs(x):
    print('dfs', x)
    if x == 0:
        return
    dfs(x - 1)  # 递归调用，探针仍在原函数字节码里，继续检测
    print('dfs return', x)


# 4. 三方库调用
@watch('local', 'buf', 'quit')
def main():
    import subprocess
    buf = 'go'
    while buf != 'quit':
        subprocess.run(['echo', 'inside三方库，不会触发探针'])
        buf = 'quit'
    print('never reach here')


if __name__ == '__main__':
    c = Counter()
    c.inc()
    dfs(3)
    main()
