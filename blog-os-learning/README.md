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
负责存放相关代码

**让我们一起探索 OS 内核的奥秘！🚀**
