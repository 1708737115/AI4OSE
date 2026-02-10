//!实现了一个最简单的 RISC-V S 态裸机程序，展示操作系统的最小执行环境。

#![no_std]
#![no_main]
// RISC-V64 架构下启用严格警告和文档检查
#![cfg_attr(target_arch = "riscv64", deny(warnings, missing_docs))]
// 非 RISC-V64 架构允许死代码（用于 cargo publish --dry-run 在主机上通过编译）
#![cfg_attr(not(target_arch = "riscv64"), allow(dead_code))]

use tg_sbi::{console_putchar, shutdown};


#[cfg(target_arch = "riscv64")]
#[unsafe(naked)]  //裸函数
#[unsafe(no_mangle)]  //保留函数原始名,_start作为入口函数
#[unsafe(link_section = ".text.entry")] //放在.text.entry段

unsafe extern "C" fn _start() -> ! {
    const STACK_SIZE: usize = 4096;

    #[unsafe(link_section = ".bss.uninit")]
    static mut STACK: [u8; STACK_SIZE] = [0u8; STACK_SIZE];

    core::arch::naked_asm!(
        "la sp, {stack} + {stack_size}", // 将 sp 设置为栈顶地址
        "j  {main}",                      // 跳转到 rust_main
        stack_size = const STACK_SIZE,
        stack      =   sym STACK,
        main       =   sym rust_main,
    )
}

extern "C" fn rust_main() -> ! {
    // 在这里编写你的代码
    for c in b"Hello,World!\n" {
        console_putchar(*c);
    }
    shutdown(false) // false 表示正常关机
}

#[panic_handler]
fn panic(_info: &core::panic::PanicInfo) -> ! {
    shutdown(true)
}


//非 RISC-V64 架构的占位模块。
#[cfg(not(target_arch = "riscv64"))]
mod placeholder {
    // 主机
    #[unsafe(no_mangle)]
    pub extern "C" fn main() -> i32 {
        0
    }

    //c运行
    #[unsafe(no_mangle)]
    pub extern "C" fn _libc_start_main() -> i32 {
        0
    }

    // Rust 异常
    #[unsafe(no_mangle)]
    pub extern "C" fn rust_eh_personality() {}
}   