# Week 1 Day 4 - 2026.02.14

## 事件

### 1. ch3 测试问题排查与修复

#### 问题现象
- 基础测试 (`./test.sh base`) 正常运行
- 练习测试 (`./test.sh exercise`) 运行时会卡死
- 使用 `--features exercise` 运行时，ch3_trace 测试应用无法正常退出

#### 排查过程

**第一步：定位问题范围**
- 注释掉 trace 功能 2（查询系统调用计数）后，程序可以正常运行完成
- 说明问题出在 trace 功能 2 的实现上

**第二步：添加调试日志**
- 在 trace 功能 2 中添加日志输出
- 发现日志输出到 `trace count: idx=2, syscall_id=113` 后程序卡死

**第三步：分析根本原因**
- 死锁问题！
- 调用链分析：
  1. `main.rs` 中 `TCBS.lock()` 获取锁
  2. 调用 `tcb.handle_syscall()` 处理系统调用
  3. `handle_syscall` 内部调用 `tg_syscall::handle`
  4. `tg_syscall::handle` 调用 `SyscallContext::trace`
  5. `trace` 功能 2 尝试再次获取 `TCBS.lock()` → **死锁**

#### 解决方案

**核心思路**：将 trace 系统调用的处理移到 `handle_syscall` 函数中，因为此时已经持有锁。

**修改文件**：

1. **src/task.rs** - 在 `handle_syscall` 中直接处理 trace 系统调用
   - 添加 `syscall_counts` 数组字段到 `TaskControlBlock`
   - 在处理系统调用前先统计调用次数
   - 在调用 `tg_syscall::handle` 之前拦截 TRACE 系统调用

2. **src/main.rs** - 简化 `SyscallContext::trace` 实现
   - 功能 0（读内存）和功能 1（写内存）直接在 trace 中处理
   - 功能 2（查询计数）不再需要，因为已在 task.rs 中处理

#### 代码改动详情

**task.rs 主要改动**：
```rust
// 新增字段
pub syscall_counts: [usize; 512]

// init 中清零计数数组
self.syscall_counts.fill(0);

// handle_syscall 中统计系统调用
let syscall_id = id.0 as usize;
if syscall_id < self.syscall_counts.len() {
    self.syscall_counts[syscall_id] += 1;
}

// 在调用 tg_syscall::handle 之前处理 trace
if let Id::TRACE = id {
    // 直接访问 self.syscall_counts（已持有锁）
    let ret = match trace_request {
        0 => unsafe { *(trace_id as *const u8) as isize },
        1 => { unsafe { *(trace_id as *mut u8) = trace_data as u8 }; 0 }
        2 => if trace_id < self.syscall_counts.len() { 
            self.syscall_counts[trace_id] as isize 
        } else { -1 },
        _ => -1,
    };
    *self.ctx.a_mut(0) = ret as _;
    self.ctx.move_next();
    return Event::None;
}
```

**main.rs 主要改动**：
- 移除 `CURRENT_TASK_IDX` 和 `TCBS` 在 impls 模块中的导入（不再需要）
- 简化 trace 实现，只处理功能 0 和 1

### 2. 文件同步

将修复后的代码从 `~/mylib/AI-Native OS/rCore-Tutorial-in-single-workspace/ch3` 覆盖到 `~/mylib/AI-Native OS/AI4OSE/blog-os-learning/os/ch3`

### 3. 测试验证

修复后运行结果：
![img.png](../../img/work/img.png)

## 技术总结

### 死锁问题分析
- 原因：Spin 锁在持有锁的状态下再次尝试获取同一把锁
- 解决：在持有锁的函数内部直接处理，避免跨函数调用链再次获取锁

### trace 系统调用实现要点
- trace 功能 2 需要访问 `syscall_counts`，必须在持有 `TCBS` 锁的上下文中处理
- 系统调用统计在 `handle_syscall` 开始时进行
- TRACE 系统调用需要特殊处理，在调用通用分发函数之前拦截

## 今日完成度

- [x] 定位 ch3 练习测试卡死原因
- [x] 分析死锁问题根因
- [x] 实现 trace 系统调用（三种功能）
- [x] 解决死锁问题
- [x] 基础测试通过
- [x] 练习测试通过
- [x] 代码同步到 blog-os-learning
- [x] 整理工作日志

---

*记录时间: 2026-02-14*  
*相关项目: rCore-Tutorial ch3 练习题*
