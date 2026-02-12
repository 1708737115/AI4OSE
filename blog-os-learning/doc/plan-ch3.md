# rCore Ch3 学习计划

## 一、章节核心概念

### 1.1 从批处理到多道程序
- **批处理系统**：串行执行，一个程序完成后才加载下一个，CPU利用率低
- **多道程序系统**：多个程序同时驻留内存，交替执行，提高CPU利用率

### 1.2 本章新增能力
1. **任务控制块(TCB)**：管理任务状态、上下文和栈空间
2. **协作式调度**：通过 `yield` 系统调用主动让出CPU
3. **抢占式调度**：通过时钟中断强制切换任务（时间片轮转）
4. **时间管理**：`clock_gettime` 系统调用

---

## 二、代码结构分析

### 2.1 文件结构

```
ch3/
├── src/
│   ├── main.rs      # 内核主循环、Trap处理、系统调用接口实现
│   └── task.rs      # 任务控制块(TCB)和调度事件定义
├── build.rs         # 构建脚本：编译用户程序、生成链接脚本
├── Cargo.toml       # 项目配置（features: coop, exercise）
└── README.md        # 详细文档
```

### 2.2 核心数据结构

#### TaskControlBlock (task.rs:16-29)
```rust
pub struct TaskControlBlock {
    ctx: LocalContext,        // 用户态上下文（寄存器+CSR）
    pub finish: bool,         // 任务完成标志
    stack: [usize; 1024],     // 独立用户栈（8KiB）
}
```

**关键方法**：
- `init(entry)`：初始化任务，设置入口地址和栈指针
- `execute()`：切换到U-mode执行任务
- `handle_syscall()`：处理系统调用，返回调度事件

#### SchedulingEvent (task.rs:31-44)
```rust
pub enum SchedulingEvent {
    None,                     // 继续执行（write/clock_gettime）
    Yield,                    // 主动让出CPU
    Exit(usize),              // 任务退出
    UnsupportedSyscall(SyscallId),  // 不支持，杀死任务
}
```

### 2.3 主循环逻辑 (main.rs:98-170)

```
初始化 → 加载所有应用到TCB数组 → 开启时钟中断
   ↓
while remain > 0:
    if !tcb.finish:
        set_timer(当前时间 + 12500)  // 设置时间片
        tcb.execute()               // 切换到用户态
        
        match Trap原因:
            SupervisorTimer:        // 时钟中断
                set_timer(MAX)      // 清除中断
                切换到下一个任务
            
            UserEnvCall:            // 系统调用
                match handle_syscall():
                    Event::None  →  continue      // 如write
                    Event::Yield →  切换任务      // yield系统调用
                    Event::Exit  →  标记完成
                    Event::Unsupported → 杀死任务
            
            Exception/Interrupt:    // 异常
                杀死任务
    
    i = (i + 1) % n  // 轮转调度
shutdown()
```

### 2.4 系统调用接口 (main.rs:185-293)

| Trait | 功能 | 系统调用 |
|-------|------|---------|
| `IO` | write | fd=1输出到控制台 |
| `Process` | exit | 返回0 |
| `Scheduling` | sched_yield | 返回0（实际调度在主循环处理） |
| `Clock` | clock_gettime | time * 10000 / 125 转换为纳秒 |
| `Trace` | trace | **练习题**：需实现内存读写和调用计数 |

---

## 三、关键机制详解

### 3.1 时钟中断实现

**初始化** (main.rs:95):
```rust
unsafe { sie::set_stimer() };  // 开启S特权级时钟中断
```

**设置时间片** (main.rs:108):
```rust
tg_sbi::set_timer(time::read64() + 12500);  // 12500周期后中断
```

**中断处理** (main.rs:119-124):
```rust
Trap::Interrupt(Interrupt::SupervisorTimer) => {
    tg_sbi::set_timer(u64::MAX);  // 清除中断
    false  // 不结束任务，切换
}
```

### 3.2 任务切换流程

```
1. 用户程序运行
2. 触发Trap（时钟中断/yield/异常）
3. 硬件保存部分状态，切换到S-mode
4. 内核读取scause判断原因
5. 处理Trap（保存/恢复上下文）
6. 决定下一个任务
7. sret返回用户态
```

### 3.3 Features说明

| Feature | 作用 |
|---------|------|
| `coop` | 协作式调度：禁用时钟中断，仅通过yield切换 |
| `exercise` | 练习模式：加载练习专用测例 |

---

## 四、练习任务：实现 sys_trace

### 4.1 需求分析

**系统调用ID**: 410

**功能**（根据trace_request）：

| request | 功能 | 参数 | 返回值 |
|---------|------|------|--------|
| 0 | 读用户内存 | id = *const u8 | 该地址字节值 |
| 1 | 写用户内存 | id = *mut u8, data = 值 | 0 |
| 2 | 查询调用计数 | id = syscall编号 | 调用次数（含本次） |
| 其他 | 无效 | - | -1 |

### 4.2 实现思路

**步骤1**：扩展TCB结构，添加系统调用计数器
```rust
// task.rs
pub struct TaskControlBlock {
    ctx: LocalContext,
    pub finish: bool,
    stack: [usize; 1024],
    syscall_count: [usize; 512],  // 新增：记录各系统调用次数
}
```

**步骤2**：在handle_syscall中统计调用
```rust
pub fn handle_syscall(&mut self) -> SchedulingEvent {
    let id = self.ctx.a(7).into();
    // ... 在返回前增加计数
    self.syscall_count[id] += 1;
}
```

**步骤3**：实现trace系统调用 (main.rs:280-292)
```rust
impl Trace for SyscallContext {
    fn trace(&self, caller: Caller, request: usize, id: usize, data: usize) -> isize {
        match request {
            0 => { /* 读取 *(id as *const u8) */ },
            1 => { /* 写入 *(id as *mut u8) = data as u8 */ },
            2 => { /* 返回 caller 的 syscall_count[id] */ },
            _ => -1,
        }
    }
}
```

**关键问题**：如何获取当前任务的TCB？
- 方案A：在SyscallContext中保存当前任务索引
- 方案B：通过Caller参数传递（需修改框架）

### 4.3 测试方式

```bash
# 运行练习测例
cargo run --features exercise

# 测试
./test.sh exercise
```

---

## 五、调试与学习建议

### 5.1 推荐的探索路径

1. **先跑通基础版本**：`cargo run`
   - 观察抢占式调度效果（输出交替）
   
2. **体验协作式调度**：`cargo run --features coop`
   - 对比无时间片轮转的区别
   
3. **阅读关键代码**：
   - task.rs中的TCB结构和方法
   - main.rs中的主循环逻辑
   
4. **实现trace练习**：
   - 先实现syscall_count统计
   - 再实现内存读写
   - 最后处理trace_request=2的查询

### 5.2 常见问题

1. **如何理解TCB.execute()?**
   - 调用`tg-kernel-context`库的`LocalContext::execute()`
   - 恢复所有用户寄存器 + sret指令
   - 返回时机：用户态触发Trap

2. **时间片大小的影响？**
   - 太大：退化为批处理，响应性差
   - 太小：切换开销占比高

3. **为什么需要SchedulingEvent枚举？**
   - 将系统调用处理与调度决策解耦
   - 便于扩展新的调度策略

---

## 六、相关依赖库说明

| 库名 | 功能 |
|------|------|
| `tg-kernel-context` | LocalContext：用户上下文管理、execute实现 |
| `tg-syscall` | 系统调用定义和分发 |
| `tg-sbi` | SBI调用封装（set_timer/shutdown等） |
| `tg-linker` | 链接脚本生成、App元数据 |
| `tg-console` | print!/println!宏和日志系统 |

---

## 七、下一步学习

完成ch3后，建议继续：
- **ch4**: 地址空间（虚拟内存）
- **ch5**: 进程管理
- 思考当前设计的不足：无内存隔离、栈溢出风险等
