# 工作日报 - Day 3 (2026-02-14)

## 今日工作内容

### 1. rCore-Tutorial ch3 练习题实现

**目标**: 实现 `sys_trace` 系统调用（ID=410），支持三种功能：
- `trace_request=0`: 读取用户内存
- `trace_request=1`: 写入用户内存
- `trace_request=2`: 查询系统调用计数

### 2. 实现思路

#### 2.1 核心数据结构

在 `task.rs` 中扩展了 `TaskControlBlock`：

```rust
pub struct TaskControlBlock {
    ctx: LocalContext,
    pub finish: bool,
    stack: [usize; 1024],
    pub syscall_counts: [usize; 1024],  // 新增：统计各系统调用次数
}
```

#### 2.2 统计机制

在 `handle_syscall` 函数内部进行统计：

```rust
pub fn handle_syscall(&mut self) -> SyscallResult {
    let id: SyscallId = self.ctx.a(7).into();
    let syscall_id = id.0 as usize;
    
    // 在调用 tg_syscall::handle 之前统计！
    self.syscall_counts[syscall_id] += 1;
    
    // ... 处理系统调用
}
```

#### 2.3 全局变量设计

在 `main.rs` 中添加了两个全局变量：

```rust
static TCBS: Mutex<[TaskControlBlock; APP_CAPACITY]> = 
    Mutex::new([TaskControlBlock::ZERO; APP_CAPACITY]);
static CURRENT_TASK_IDX: Mutex<usize> = Mutex::new(0);
```

- `TCBS`: 存储所有任务控制块
- `CURRENT_TASK_IDX`: 记录当前执行的任务索引，供 trace 使用

#### 2.4 trace 实现

```rust
impl Trace for SyscallContext {
    fn trace(&self, _caller: Caller, trace_request: usize, id: usize, data: usize) -> isize {
        let idx = *CURRENT_TASK_IDX.lock();
        match trace_request {
            0 => unsafe { *(id as *const u8) as isize },  // 读内存
            1 => { unsafe { *(id as *mut u8) = data as u8 }; 0 },  // 写内存
            2 => TCBS.lock()[idx].syscall_counts[id] as isize,  // 查询计数
            _ => -1,
        }
    }
}
```

### 3. 遇到的问题及解决方案

#### 3.1 死锁问题（关键！）

**问题描述**：
- 初始方案是在主循环中获取 syscall_id 后统计
- 但主循环持有 `TCBS.lock()`，当调用 trace 时，trace 内部也尝试获取 `TCBS.lock()`
- 导致死锁，练习测试卡住无法运行

**解决思路**：
- 将统计逻辑移到 `handle_syscall` 内部
- 在调用 `tg_syscall::handle()` **之前**进行统计
- 这样 trace 函数内部获取锁时，主循环已经释放了锁

**关键代码**：

```rust
// task.rs - handle_syscall 内部
let syscall_id = id.0 as usize;
self.syscall_counts[syscall_id] += 1;  // 在调用 handle 之前统计
```

### 4. 当前状态

#### 4.1 基础测试 ✅
```
./test.sh base
Test PASSED: 4/4
```

#### 4.2 练习测试 ⚠️

日志显示三个任务正常交替执行：
```
get_time OK! 57
[DEBUG] app0 yield
current time_msec = 60
[DEBUG] app1 yield
[DEBUG] app2 yield
[DEBUG] app0 yield
...
Test sleep1 passed!
[ INFO] app1 exit with code 0
```

**困境**：练习测试运行时间过长（ch3_sleep 需要等待 3000ms），导致测试超时。ch3_trace 测试未能完成验证。

### 5. 技术细节

#### 5.1 Rust 所有权与生命周期

- 全局 `Mutex` 用于在中断上下文（单核环境）下安全共享数据
- `spin::Mutex` 是自旋锁，适合短临界区
- 必须在持有锁的时间窗口内完成所有操作，避免长时间阻塞

#### 5.2 系统调用参数

| 参数 | 含义 |
|-----|------|
| a0 | trace_request (0/1/2) |
| a1 | id (地址或 syscall_id) |
| a2 | data (写入值) |

### 6. 文件位置

- **ch3 代码**: `/home/fengxu/mylib/AI-Native OS/AI4OSE/blog-os-learning/os/ch3/`
- **原始代码**: `/home/fengxu/mylib/AI-Native OS/rCore-Tutorial-in-single-workspace/ch3/`
- **本工作日志**: `/home/fengxu/mylib/AI-Native OS/AI4OSE/blog-os-learning/work/week1/day3.md`

### 7. 待解决的问题

1. **练习测试超时**: ch3_sleep 需要等待 3000ms，测试时间过长
2. **ch3_trace 未验证**: 由于测试超时，未能看到 "Test trace OK!" 的输出

### 8. 今日完成度

- [x] 实现 sys_trace 系统调用（三种功能）
- [x] 解决死锁问题
- [x] 基础测试通过
- [ ] 练习测试完整验证（超时问题）
- [x] 代码整理和文档记录

---

*记录时间: 2026-02-14 04:00*  
*相关项目: rCore-Tutorial ch3 练习题*
