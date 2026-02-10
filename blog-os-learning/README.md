# OS 内核学习记录

> 通过实践学习操作系统内核，记录学习过程、思考与实现

---

## 项目介绍

这是我学习 rCore-Tutorial 和 AI4OSE Lab1 的学习记录仓库。

### 学习目标

- 理解操作系统内核的核心原理
- 掌握 Rust 在裸机编程中的应用
- 学习 RISC-V 架构和 QEMU 模拟
- 培养系统设计和实现能力

### 学习资源

- **参考仓库**: https://github.com/rcore-os/rCore-Tutorial-in-single-workspace/tree/test
- **OS 课程**: https://learningos.cn/os-lectures/
- **教材参考**: https://pages.cs.wisc.edu/~remzi/OSTEP/Chinese/

---

## 项目结构

```
blog-os-learning/
├── README.md              # 项目介绍
│
├── work/                  # 每周工作记录
│   ├── week1.md
│   ├── week2.md
│   ├── week3.md
│   └── week4.md
│
├── blog/                  # 学习博客
│   ├── README.md          # 博客总览
│   ├── ch01-执行环境.md
│   ├── ch02-批处理系统.md
│   ├── ch03-多道程序.md
│   └── ch04-虚拟内存.md
│
└── os/                    # 组件实现
    ├── README.md          # 组件说明
    ├── components/        # 组件实现
    │   ├── console/
    │   ├── syscall/
    │   ├── vm/
    │   └── task/
    └── experiments/      # 实验代码
        ├── ch1/
        ├── ch2/
        ├── ch3/
        └── ch4/
```

---

## 目录说明

### work/ - 每周工作记录

记录每周的学习进展、完成的工作、遇到的问题和解决方法。

类似老师的日报格式：
- 事件：做了什么
- 问题：遇到什么问题
- 计划：下一步要做什么

**示例**：
```markdown
# Week 1

## Day 1
### 事件：环境搭建
- 安装 Rust 工具链
- 添加 RISC-V 编译目标
- 运行 ch1

### 问题
- QEMU 版本太旧，运行失败
- 解决：使用 apt 安装最新版本

### 计划
- 继续学习 ch2
```

---

### blog/ - 学习博客

记录学习过程中的思考、对架构和设计的理解。

**内容**：
- 学习流程
- 核心概念理解
- 架构设计思考
- 与参考环境的对比

**示例**：
```markdown
# ch01: 执行环境

## 学习流程

1. 阅读 rCore-Tutorial ch1 文档
2. 理解裸机程序的概念
3. 学习 SBI 调用
4. 运行 ch1，观察输出

## 核心概念

### 裸机程序
...
```

---

### os/ - 组件实现

记录对相关组件的实现和改进。

**内容**：
- 组件的实现
- 代码注释
- 改进记录
- 测试验证

**示例**：
```markdown
# 组件实现

## console

### 功能
- 封装 SBI console_putchar
- 提供 print/println 宏

### 实现
...
```

---

## 快速开始

### 环境准备

```bash
# 1. 安装 Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source "$HOME/.cargo/env"

# 2. 添加 RISC-V 编译目标
rustup target add riscv64gc-unknown-none-elf

# 3. 安装 QEMU
sudo apt update
sudo apt install qemu-system-misc
```

### 克隆参考仓库

```bash
cd ..
git clone https://github.com/rcore-os/rCore-Tutorial-in-single-workspace.git
cd rCore-Tutorial-in-single-workspace
```

### 运行实验

```bash
# ch1
cd ch1
cargo run

# ch2-ch4 (需要设置 TG_USER_DIR)
cd ch2
TG_USER_DIR="../tg-user" cargo run
```

---

## 学习路径

### Week 1: 基础学习

- [ ] 学习 ch1：执行环境
- [ ] 学习 ch2：批处理系统
- [ ] 学习 ch3：多道程序
- [ ] 学习 ch4：虚拟内存
- [ ] 每天记录工作进展

### Week 2: 深入理解

- [ ] 撰写博客文章（ch1-ch4）
- [ ] 记录对架构的理解
- [ ] 记录对设计的思考
- [ ] 与参考环境对比

### Week 3: 组件实现

- [ ] 分析参考代码
- [ ] 实现核心组件
- [ ] 添加代码注释
- [ ] 测试验证

### Week 4: 整合优化

- [ ] 整合所有文档
- [ ] 完善实现代码
- [ ] 准备提交
- [ ] 面试准备

---

## 进度跟踪

- [x] 创建项目结构
- [x] 环境配置
- [x] 验证 ch1-ch4 可运行
- [ ] Week 1 学习
- [ ] Week 2 深入
- [ ] Week 3 实现
- [ ] Week 4 优化

---

## 核心理念

> **自己实现是理解功能的必要条件**

通过"学习 → 思考 → 实现"的路径，真正掌握 OS 内核的核心原理。

---

## 致谢

感谢以下项目的启发和支持：
- rCore-Tutorial: https://github.com/rcore-os/rCore-Tutorial
- rCore-Tutorial-Book: https://rcore-os.cn/rCore-Tutorial-Book-v3/
- LearningOS: https://learningos.cn/

---

**让我们一起探索 OS 内核的奥秘！🚀**
