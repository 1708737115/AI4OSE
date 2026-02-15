# Ch4 Exercise 详细实现指南

## 一、概述

Ch4 在 Ch3 基础上引入**地址空间（Address Space）**机制，通过 Sv39 虚拟内存实现进程隔离。本章 Exercise 主要实现：

1. **mmap/munmap** - 内存映射系统调用
2. **trace** - 安全内存读写系统调用
3. **clock_gettime/sleep** - 时钟相关系统调用

---

## 二、测试用例分析

根据 `tg-checker/src/cases/ch4.rs`，Exercise 需要通过的输出：

```
get_time OK! (\d+)
Test sleep OK!
current time_msec = (\d+)
time_msec = (\d+) after sleeping (\d+) ticks, delta = (\d+)ms!
Test sleep1 passed!
string from task trace test
Test trace OK!
Test 04_1 OK!
Test 04_4 test OK!
Test 04_5 ummap OK!
Test 04_6 ummap2 OK!
Test trace_1 OK!
```

**不能出现的输出：**
- `FAIL: T.T`
- `Test sbrk failed!`
- `Should cause error, Test 04_2 fail!`
- `Should cause error, Test 04_3 fail!`

---

## 三、需要实现的测试程序

### 3.1 用户态程序（位于 `tg-user/src/bin/`）

| 文件 | 功能 | 期望输出 |
|------|------|----------|
| `ch4_mmap.rs` | 验证 mmap 可读可写 | `Test 04_1 OK!` |
| `ch4_mmap1.rs` | 验证只读页写入异常 | 进程被杀死，不输出任何内容 |
| `ch4_mmap2.rs` | 验证非法保护位异常 | 进程被杀死，不输出任何内容 |
| `ch4_mmap3.rs` | 验证 mmap 参数校验 | `Test 04_4 test OK!` |
| `ch4_unmap.rs` | 验证 munmap 后重新映射 | `Test 04_5 ummap OK!` |
| `ch4_unmap2.rs` | 验证 munmap 错误路径 | `Test 04_6 ummap2 OK!` |
| `ch4_trace.rs` | 综合 trace + mmap 测试 | `Test trace_1 OK!` |

---

## 四、内核实现（位于 `ch4/src/main.rs`）

### 4.1 Memory 系统调用实现

在 `impls` 模块中实现 `Memory` trait：

```rust
impl Memory for SyscallContext {
    fn mmap(
        &self,
        caller: Caller,
        addr: usize,
        len: usize,
        prot: i32,
        _flags: i32,
        _fd: i32,
        _offset: usize,
    ) -> isize {
        // 参数校验
        // 1. 地址必须页对齐 (addr % 4096 == 0)
        // 2. 长度必须 > 0
        // 3. prot 必须合法: 
        //    - prot = 1 (只读 R)
        //    - prot = 2 (只写，在 RISC-V 非法)
        //    - prot = 3 (可读可写 R+W)
        //    - prot = 0 或 prot > 7 非法
        
        let process = unsafe { PROCESSES.get_mut() }.get_mut(caller.entity)?;
        
        // 调用 address_space.map() 映射页面
        // 返回映射后的地址（成功返回 addr，失败返回 -1）
    }

    fn munmap(&self, caller: Caller, addr: usize, len: usize) -> isize {
        // 参数校验
        // 1. 地址必须页对齐
        // 2. 长度必须 > 0
        // 3. 映射范围必须完全覆盖已映射区域
        
        let process = unsafe { PROCESSES.get_mut() }.get_mut(caller.entity)?;
        
        // 调用 address_space.unmap() 解除映射
    }
}
```

### 4.2 Trace 系统调用实现

```rust
impl Trace for SyscallContext {
    fn trace(&self, caller: Caller, trace_request: usize, id: usize, data: usize) -> isize {
        // trace_request:
        //   0 = trace_read: 读取 id 地址处的字节
        //   1 = trace_write: 向 id 地址写入 data 字节
        //   2 = count_syscall: 统计系统调用次数
        
        let process = unsafe { PROCESSES.get_mut() }.get_mut(caller.entity)?;
        
        match trace_request {
            0 => {
                // 使用 address_space.translate() 检查地址是否可读
                // 可读返回读取的字节值，否则返回 -1
            }
            1 => {
                // 使用 address_space.translate() 检查地址是否可写
                // 可写写入并返回 0，否则返回 -1
            }
            2 => {
                // 统计 syscall 次数（可选）
            }
            _ => -1,
        }
    }
}
```

---

## 五、详细实现步骤

### 5.1 mmap 实现

```rust
fn mmap(&self, caller: Caller, addr: usize, len: usize, prot: i32, ...) -> isize {
    const PAGE_SIZE: usize = 4096;
    
    // 1. 参数校验
    // 地址页对齐检查
    if addr & (PAGE_SIZE - 1) != 0 {
        return -1;
    }
    // 长度检查
    if len == 0 {
        return -1;
    }
    // prot 合法性检查 (RISC-V)
    // R=1(bit0), W=2(bit1), X=4(bit2)
    // 合法值: 1(R), 3(R+W), 5(R+X), 7(R+W+X)
    if prot == 0 || prot > 7 || (prot & !7) != 0 {
        return -1;
    }
    // R=0 && W=1 是非法的（RISC-V 只支持 R+W，不支持单独 W）
    if prot == 2 {
        return -1;
    }
    
    // 2. 获取进程地址空间
    let process = match unsafe { PROCESSES.get_mut() }.get_mut(caller.entity) {
        Some(p) => p,
        None => return -1,
    };
    
    // 3. 构建页表标志位
    let mut flags_str = *b"U___V";
    if prot & 1 != 0 { flags_str[3] = b'R'; }  // 读
    if prot & 2 != 0 { flags_str[2] = b'W'; }  // 写
    if prot & 4 != 0 { flags_str[1] = b'X'; }  // 执行
    
    let flags = parse_flags(unsafe { core::str::from_utf8_unchecked(&flags_str) }).unwrap();
    
    // 4. 映射虚拟地址范围
    let start_vpn = VPN::<Sv39>::new(addr >> Sv39::PAGE_BITS);
    let end_vpn = VPN::<Sv39>::new((addr + len + PAGE_SIZE - 1) >> Sv39::PAGE_BITS);
    
    process.address_space.map(
        start_vpn..end_vpn,
        &[],  // 无初始数据
        0,    // 数据偏移
        flags,
    );
    
    addr as isize
}
```

### 5.2 munmap 实现

```rust
fn munmap(&self, caller: Caller, addr: usize, len: usize) -> isize {
    const PAGE_SIZE: usize = 4096;
    
    // 1. 参数校验
    if addr & (PAGE_SIZE - 1) != 0 {
        return -1;  // 地址未对齐
    }
    if len == 0 {
        return -1;
    }
    
    // 2. 获取进程
    let process = match unsafe { PROCESSES.get_mut() }.get_mut(caller.entity) {
        Some(p) => p,
        None => return -1,
    };
    
    // 3. 检查映射范围是否完全有效
    // (需要检查 addr 到 addr+len 的范围是否都有对应的映射)
    // 简化实现：直接解除映射
    
    let start_vpn = VPN::<Sv39>::new(addr >> Sv39::PAGE_BITS);
    let end_vpn = VPN::<Sv39>::new((addr + len + PAGE_SIZE - 1) >> Sv39::PAGE_BITS);
    
    process.address_space.unmap(start_vpn..end_vpn);
    
    0
}
```

### 5.3 trace 实现

```rust
impl Trace for SyscallContext {
    fn trace(&self, caller: Caller, trace_request: usize, id: usize, data: usize) -> isize {
        let process = match unsafe { PROCESSES.get_mut() }.get_mut(caller.entity) {
            Some(p) => p,
            None => return -1,
        };
        
        match trace_request {
            0 => { // trace_read
                // 检查是否为内核地址（用户地址空间不能访问内核地址）
                // 用户态可访问地址范围: 0x0 ~ 0x4000000000 (256GB)
                if id >= 0x80000000 {
                    return -1;
                }
                
                let vaddr = VAddr::<Sv39>::new(id);
                // 检查可读权限
                const READABLE: VmFlags<Sv39> = build_flags("RV");
                if let Some(ptr) = process.address_space.translate::<u8>(vaddr, READABLE) {
                    unsafe { *ptr.as_ptr() } as isize
                } else {
                    -1
                }
            }
            1 => { // trace_write
                if id >= 0x80000000 {
                    return -1;
                }
                
                let vaddr = VAddr::<Sv39>::new(id);
                // 检查可写权限
                const WRITABLE: VmFlags<Sv39> = build_flags("WV");
                if let Some(ptr) = process.address_space.translate::<u8>(vaddr, WRITABLE) {
                    unsafe { *ptr.as_ptr() = data as u8; }
                    0
                } else {
                    -1
                }
            }
            _ => -1,
        }
    }
}
```

---

## 六、关键数据结构

### 6.1 VmFlags 标志位

```
R - Read (读)
W - Write (写)
X - Execute (执行)
V - Valid (有效)
U - User (用户态可访问)
G - Global (全局)
```

### 6.2 prot 参数含义

| prot 值 | 二进制 | 含义 |
|---------|--------|------|
| 1       | 001    | 只读 (R) |
| 2       | 010    | 只写 (非法) |
| 3       | 011    | 可读可写 (R+W) |
| 4       | 100    | 可执行 (X) |
| 5       | 101    | 可读可执行 (R+X) |
| 6       | 110    | 可写可执行 (非法) |
| 7       | 111    | 可读可写可执行 (R+W+X) |

---

## 七、验证方法

运行测试：

```bash
cd rCore-Tutorial-in-single-workspace
cargo run --release
```

预期输出应包含所有测试用例的成功信息。

---

## 八、常见问题

1. **mmap 返回 -1**: 检查地址对齐、prot 合法性、页表映射是否成功
2. **进程被异常杀死**: 检查页表权限设置是否正确
3. **trace 读写失败**: 检查地址是否在用户空间范围内，是否有正确的权限

---

## 九、参考文件

- 内核实现: `ch4/src/main.rs` (impls 模块)
- 用户库: `tg-user/src/lib.rs`
- 系统调用定义: `tg-syscall/src/kernel/mod.rs`
- 地址空间: `tg-kernel-vm/src/space/mod.rs`
