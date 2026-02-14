# chapter3 练习答案

## trace 系统调用实现思路

### 1. 核心数据结构

在 `TaskControlBlock` 中添加系统调用计数数组：

```rust
// src/task.rs
pub struct TaskControlBlock {
    ctx: LocalContext,
    pub finish: bool,
    stack: [usize; 1024],
    /// 系统调用计数数组，索引为系统调用号，值为调用次数
    pub syscall_counts: [usize; 512],
}
```

初始化时清零计数数组：

```rust
pub fn init(&mut self, entry: usize) {
    self.stack.fill(0);
    self.finish = false;
    self.syscall_counts.fill(0);  // 清零计数
    // ...
}
```

### 2. 系统调用统计

在 `handle_syscall` 函数中，在调用 `tg_syscall::handle` 之前统计系统调用次数：

```rust
pub fn handle_syscall(&mut self) -> SchedulingEvent {
    let id: SyscallId = self.ctx.a(7).into();
    let syscall_id = id.0 as usize;

    // 统计系统调用次数
    if syscall_id < self.syscall_counts.len() {
        self.syscall_counts[syscall_id] += 1;
    }
    // ...
}
```

### 3. trace 系统调用处理

**关键点**：将 trace 系统调用的处理直接放在 `handle_syscall` 内部，而不是通过 `tg_syscall::handle` 分发。这是因为：

1. trace 功能 2（查询系统调用计数）需要访问 `syscall_counts`
2. 此时已经持有 `TCBS` 锁（在 main.rs 的调度循环中）
3. 如果通过 `tg_syscall::handle` → `SyscallContext::trace` 路径，会再次尝试获取 `TCBS.lock()`，导致**死锁**

```rust
// 在 handle_syscall 中，直接处理 trace 系统调用
if let Id::TRACE = id {
    let trace_request = args[0];
    let trace_id = args[1];
    let trace_data = args[2];
    
    let ret = match trace_request {
        0 => {
            // 读取用户内存
            unsafe { *(trace_id as *const u8) as isize }
        }
        1 => {
            // 写入用户内存
            unsafe { *(trace_id as *mut u8) = trace_data as u8 };
            0
        }
        2 => {
            // 查询系统调用计数
            // 直接访问 self.syscall_counts（已持有锁）
            if trace_id < self.syscall_counts.len() {
                self.syscall_counts[trace_id] as isize
            } else {
                -1
            }
        }
        _ => -1,
    };
    
    *self.ctx.a_mut(0) = ret as _;
    self.ctx.move_next();
    return Event::None;
}
```

### 4. SyscallContext::trace 实现

由于 trace 功能 2 已在 task.rs 中处理，这里只需要实现功能 0 和 1：

```rust
// src/main.rs
impl Trace for SyscallContext {
    fn trace(&self, _caller: Caller, trace_request: usize, id: usize, data: usize) -> isize {
        match trace_request {
            0 => {
                // 读取用户内存
                unsafe { *(id as *const u8) as isize }
            }
            1 => {
                // 写入用户内存
                unsafe { *(id as *mut u8) = data as u8 };
                0
            }
            2 => {
                // 功能 2 已在 task.rs 的 handle_syscall 中处理
                -1
            }
            _ => -1,
        }
    }
}
```

### 5. 死锁问题总结

**问题**：初始实现中，trace 功能 2 在 `SyscallContext::trace` 中尝试获取 `TCBS.lock()`，但此时已经持有该锁（通过 `handle_syscall` 调用链），导致死锁。

**解决**：将 trace 系统调用处理移到 `handle_syscall` 函数内部，在持有锁的上下文中直接访问 `syscall_counts`。

### 6. 测试验证

```bash
./test.sh base     # 基础测试
./test.sh exercise # 练习测试
```

输出示例：
```
get_time OK! 43
current time_msec = 48
time_msec = 151 after sleeping 100 ticks, delta = 103ms!
Test sleep1 passed!
[ INFO] app1 exit with code 0
string from task trace test

Test trace OK!
[ INFO] app2 exit with code 0
Test sleep OK!
[ INFO] app0 exit with code 0
```
