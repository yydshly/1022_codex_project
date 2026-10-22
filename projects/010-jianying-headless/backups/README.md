# 两个原始仓库的离线保全包

为防止上游仓库删除、封禁或访问中断，本子项目将已下载的两个仓库合并保存为 **upstream-preservation-20261022.zip**。这是个人非商业学习研究用的固定快照归档，不是官方 SDK、剪映安装包或可自由商用的技能产品。

原始抓取时间：**2026-10-22 13:58（北京时间）**。统一打包日期：**2026-10-23**。打包没有联网更新上游，因此两个日期代表抓取和整理两个不同动作。

| 来源 | 保存范围 | 固定主分支提交 | 引用 / 可达提交 / 主分支文件 |
| --- | --- | --- | --- |
| https://github.com/mcncarl/jianying-headless | 全部当时可获取的 Git 引用及可达历史、主分支源码 | `27c2627bbd0fccc8484000f32e9d66a820f4b698` | 38 / 79 / 108 |
| https://github.com/mcncarl/yichen-skills | **整个 yichen-skills 仓库**，包含 `yichen-jianying-edit` | `9bd78982aa75aa179258bc9009fe4dcf2f2973b9` | 29 / 108 / 249 |

合计：2 个完整仓库、67 个 Git 引用、187 个全引用可达提交、357 个主分支文件。引用包括当时可获取的分支、标签和 PR 引用；不代表所有曾存在但已经删除或不公开的对象。

## 归档结构

```text
upstream-preservation-20261022.zip
└── preservation-20261022/
    ├── README.md                    # 本恢复说明
    ├── CONTENTS.json                # 本包所有其他条目的大小与 SHA-256
    ├── snapshot/
    │   ├── jianying-headless.bundle # 可独立恢复 Git 历史
    │   ├── yichen-skills.bundle
    │   ├── jianying-headless-27c2627bbd0f.zip # 主分支源码，便于直接阅读
    │   ├── yichen-skills-9bd78982aa75.zip
    │   ├── *-refs.json              # 全部 Git 引用映射
    │   ├── manifest.json            # 原始来源、版本、357 文件哈希
    │   ├── SHA256SUMS.txt
    │   └── verification.json        # 首次离线验证记录
    └── licenses/                    # 按仓库与原路径保留的许可及第三方声明
```

两个源码 ZIP 和 bundle 本身也保留原始仓库中的许可证、第三方声明与已有公开媒体。顶层 `licenses/` 再保留一份便于查阅的声明。本包不包含本机裸镜像配置、凭据、GitHub Issue/评论、Release 独立附件、剪映安装包或官方程序库、外部素材和在线服务；LFS 与子模块检查未发现需要额外保全的对象。

## 从研究仓库离线核验

克隆本研究仓库即可取得本 ZIP、`.sha256`、恢复说明与项目根的 `preservation-package.json`，不依赖原机器上的 `_upstream/`。

在研究仓库根目录执行（Python 3.10+）：

```powershell
python projects/010-jianying-headless/scripts/package_preservation.py --check
```

此命令只读取最终 ZIP、校验文件和记录，核对外层条目及哈希、两个源码 ZIP 内全部 357 个文件、原始清单与许可副本，不需要联网或本地原始镜像。

原始源码 ZIP 由 Windows 上的 `git archive` 生成，249 个文件采用 CRLF 换行，与清单中的精确 Git blob 仅换行不同。归档保留原 ZIP 字节与原校验值；检查先验证整个 ZIP 的原始哈希，再逐文件按原字节或仅 CRLF→LF 对照清单。精确 Git blob 保存在 bundle 中，独立恢复检查会直接读取恢复仓库的全部 357 个原始 blob 核对，不将换行转换误写为原字节完全一致。

需要实际验证历史可恢复时，另外安装 Git，在同一位置执行；目标目录必须尚不存在：

```powershell
python projects/010-jianying-headless/scripts/package_preservation.py --restore-check _upstream/my-archive-recovery
```

目标路径相对于本子项目，且限定在本子项目的 `_upstream/` 内。脚本仅从最终 ZIP 提取 bundle，再创建全新的裸仓库，核对全部引用、HEAD、提交数量，并执行严格 `git fsck`。不执行上游代码，不联网，不删除既有目录。真实核验结果记录在 `preservation-package.json`；复制该归档不能证明剪映原生流程已经运行通过。

## 不使用 Python 脚本的手工恢复

先核对 ZIP 的 SHA-256 与旁边 `.sha256` 文件一致，再解压到一个新目录。进入解压得到的 `preservation-20261022`，在下列目录尚不存在时运行：

```powershell
git clone --mirror ./snapshot/jianying-headless.bundle ./restored-jianying-headless.git
git clone --mirror ./snapshot/yichen-skills.bundle ./restored-yichen-skills.git
git -c core.autocrlf=false clone ./restored-jianying-headless.git ./jianying-headless
git -c core.autocrlf=false clone ./restored-yichen-skills.git ./yichen-skills
```

固定主分支快照可直接阅读两个源码 ZIP；其他分支及 PR 内容通过恢复后的 Git 仓库检出。`yichen-jianying-edit` 位于恢复后的 `yichen-skills/yichen-jianying-edit/`。

## 许可与用途

两仓原创部分采用 **Personal Learning and Non-Commercial Use License**；原 `LICENSE`、核心的 `NOTICE`、`THIRD_PARTY_NOTICES.md`、各层 `licenses/` 和 Skill 内的原有声明均原样保留。允许个人学习研究 fork；第 2 条限制未经书面许可作为公开技能集合、模板包、市场商品或商业/公司工具重新发布、打包和营销。该备份不授予额外分发、商业使用、剪映程序库、字体、素材、账号或服务权益；第三方材料仍遵循各自许可。

本包用于保存研究材料的固定版本，防止丢失。使用或传播仍须遵守包内原许可；不要将其描述为可自由再分发、自由商用的 Skill 集合。
