# GitHub Actions CI/CD 从零到一全流程实操讲义（通俗易懂版）

## 前言

本讲义为**纯实操、零基础可上手**教程，完整复刻企业多人开发 CI/CD 标准流程。全程无需自己搭建服务器、无需配置 Runner，GitHub 云端免费提供执行机器，开箱即用。

**核心目标**：掌握「分支开发 → PR审核 → CI自动质检 → 主干合并 → CD自动打包交付」整套工业级开发流程。

**配套代码**：Python业务代码 \+ 开发手写单元测试 \+ GitHub Actions 完整 CI/CD 配置

---

## 一、核心概念速记（必考）

### 1\. CI 持续集成（代码合并前执行）

触发时机：新建/更新 **PR 合并请求** 时自动运行

核心作用：**代码质检、拦截BUG**

自动执行：代码格式校验、语法检测、单元测试

团队规则：CI 不通过，**禁止合并代码到主干 main**

### 2\. CD 持续交付（代码合并后执行）

触发时机：代码**成功合并到 main 主干**后自动运行

核心作用：**自动化打包、产出可运行项目包**，替代人工重复操作

完整能力：打包项目 → 生成可交付压缩包 → 云端保存产物，可拓展自动传服务器、解压、重启服务

### 3\. 关键分工误区纠正

✅**单元测试代码：开发自己写**（谁写业务功能，谁写对应测试用例）

❌ 单元测试不属于测试 QA 工作，QA 只负责人工功能测试、系统测试

---

## 二、GitHub 专属 CI/CD 基础规则（区别 GitLab）

| 配置项         | GitHub Actions 规则                | 通俗解释                     |
| ----------- | -------------------------------- | ------------------------ |
| 配置文件路径      | 必须放在 `.github/workflows/xxx.yml` | 固定文件夹，放根目录不生效，这是最常见报错点   |
| 执行机器 Runner | 平台自带云端机器，无需手动部署                  | 零运维、开箱即用，个人免费额度足够练手      |
| 合并请求名称      | PR（Pull Request）                 | 等同于 GitLab 的 MR，用于代码评审合并 |
| 任务执行顺序      | 通过 `needs` 依赖控制先后                | 必须 CI 质检成功，才允许执行 CD 打包   |
| 产物保存方式      | 依赖官方插件 `upload-artifact`         | 打包后的文件可在网页端直接下载          |

---

## 三、实操环境准备

### 1\. 前置条件

- 注册 GitHub 账号，新建公开仓库（私有仓库有免费额度限制）

- 本地安装 Git、Python3\.11\+

- 本地配置 Git 用户名、邮箱

### 2\. 本地仓库初始化命令

```powershell
# 1. 新建项目文件夹，进入目录
mkdir github-cicd-demo
cd github-cicd-demo

# 2. 初始化本地 Git 仓库
git init

# 3. 绑定远端 GitHub 仓库地址（替换为自己的仓库地址）
git remote add origin https://github.com/xxx/xxx.git

# 4. 切换主干分支为 main（统一团队规范）
git checkout -b main

```

---

## 四、核心代码编写（双平台通用）

在项目根目录新建两个业务代码文件，模拟真实开发场景

### 1\. 业务代码：calc\.py（实现功能）

```python
# 基础加法业务功能
def add(a,b):
    return a + b
```

### 2\. 单元测试代码：test\_calc\.py（开发手写测试用例）

```python
# 验证业务逻辑正确性
import pytest

# 测试正常加法场景
def test_add_normal():
    assert add(1,2) == 3

# 测试边界场景（正负抵消）
def test_add_negative():
    assert add(-1,1) == 0

```

---

## 五、GitHub Actions CI/CD 核心配置（重点）

### 1\. 新建固定目录结构

根目录创建文件夹：`.github/workflows`，新建配置文件 `ci-cd.yml`

完整路径：`.github/workflows/ci-cd.yml`

### 2\. 完整 CI\+CD 配置文件（直接复制可用）

```yaml
name: GitHub完整CI&CD自动化流水线

# 触发规则：PR阶段跑CI，main推送阶段跑CD
on:
  pull_request:   # 新建/更新PR：触发代码质检CI
  push:
    branches: [ main ] # 仅主干合并：触发打包交付CD

jobs:
  # 【CI阶段】代码格式校验 + 单元测试（所有分支、PR必跑）
  ci_quality_check:
    runs-on: ubuntu-latest
    steps:
      - name: 拉取仓库全部代码
        uses: actions/checkout@v4

      - name: 配置Python3.11环境
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: 安装代码校验、单元测试依赖
        run: pip install flake8 pytest

      - name: 全局代码格式校验（Lint）
        run: flake8 .

      - name: 执行全部单元测试
        run: pytest test_calc.py -v

  # 【CD阶段】主干合并后自动打包交付（仅main分支执行）
  cd_package_build:
    needs: ci_quality_check # 前置CI必须全部通过才执行
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' # 严格限定仅主干触发
    steps:
      - name: 拉取main主干最新代码
        uses: actions/checkout@v4

      - name: 自动打包可运行项目
        run: zip -r release.zip calc.py test_calc.py

      - name: 云端保存打包产物
        uses: actions/upload-artifact@v4
        with:
          name: 项目可运行包
          path: release.zip

```

### 3\. 配置文件核心逻辑解读

- **CI 环节**：PR 提交自动校验代码格式、跑单元测试，有BUG直接拦截，禁止合并

- **CD 环节**：仅代码合并到 main 主干后执行，自动打包项目、保存可运行安装包

- **依赖限制**：通过 `needs` 保证质检失败时，绝对不会执行打包上线

---

## 六、企业标准全流程实操步骤

完整复刻多人团队开发规范，一步不跳、标准落地

### 步骤1：新建开发分支（禁止直接操作main）

```powershell
# 新建并切换到开发分支 v1.0
git checkout -b v1.0

```

规范：所有功能开发、代码修改，全部在个人分支完成，**绝对禁止直接push main主干**

### 步骤2：提交代码并推送到远端

```powershell
# 暂存全部文件
git add .

# 本地提交
git commit -m "新增加法业务代码+单元测试+CI/CD自动化配置"

# 推送远端个人分支
git push origin v1.0

```

### 步骤3：网页端创建 PR 合并请求

1. 推送成功后，打开 GitHub 仓库主页，点击页面蓝色按钮 **Compare \& pull request**

2. 源分支（compare）：`v1.0`（自己的开发分支）

3. 目标分支（base）：`main`（主干分支）

4. 填写标题、描述，点击 **Create pull request** 创建PR

### 步骤4：CI 自动质检（关键拦截环节）

1. PR 创建瞬间，GitHub 自动触发 Actions 流水线

2. 网页切换到 **Actions** 菜单，查看运行日志

3. 绿色✅：CI质检通过，允许人工评审合并

4. 红色❌：代码格式错误/单元测试失败，必须修改代码重新推送

### 步骤5：人工代码评审 \+ 合并主干

1. 团队负责人审核代码逻辑、测试用例合理性

2. 确认无误后，点击 **Merge pull request** 合并代码到main

3. 完成后关闭PR，删除远端临时开发分支（保持仓库整洁）

### 步骤6：CD 自动打包交付（合并后自动触发）

1. 代码合并到main主干后，自动触发CD流水线

2. 自动完成项目打包，生成可运行压缩包

3. 在 Actions 对应执行记录的 **Artifacts** 位置，下载打包好的项目包

---

## 七、主干分支保护配置（企业必备）

防止乱改主干、绕过CI直接合并代码，配置一次永久生效

1. 仓库主页 → Settings → Branches → Add rule

2. 分支名称填写：`main`

3. 开启核心配置：

    - 禁止直接 Push 到 main 主干
    
    - PR 必须通过 CI 检查才能合并
    
    - 必须人工评审通过才能合并

---

## 八、高频问题\&易错点总结

#### 1\. 流水线不触发怎么办？

90%原因：CI配置文件路径错误，必须严格放在`.github/workflows/` 目录，文件名后缀为 yml/yaml

#### 2\. 单元测试报错？

优先检查业务代码逻辑、测试用例断言是否正确，CI会精准打印报错日志，根据日志修改即可

#### 3\. CI和CD为什么不同时跑？

规范设计：PR阶段只做CI质检拦BUG，**未评审代码绝不打包上线**，只有合并主干后才触发CD交付

#### 4\. 和GitLab CI/CD核心区别？

GitHub无需部署Runner、开箱即用；GitLab私有化需要自己搭建维护执行机器，适合企业内网部署

---

## 九、流程终极总结

**完整闭环：分支开发 → 推送远端 → 提交PR → CI自动质检拦错 → 人工评审 → 合并主干 → CD自动打包交付**

✅ CI = 代码质量守门员（合并前防BUG）

✅ CD = 自动化交付工人（合并后省人工）

> （注：部分内容可能由 AI 生成）
