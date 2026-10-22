"""Build the research documents from the page's reviewed content (stdlib only)."""
from pathlib import Path
import json

PROJECT=Path(__file__).resolve().parents[1]
data=json.loads((PROJECT/'web/research.json').read_text(encoding='utf-8'))
evidence=json.loads((PROJECT/'research-evidence.json').read_text(encoding='utf-8'))
guide=json.loads((PROJECT/'assets/guide-manifest.json').read_text(encoding='utf-8'))
upstream=data['upstream']
sha=data['commit']
def pinned(path): return upstream+'/blob/'+sha+'/'+path
def write(path,body): (PROJECT/path).write_bytes((body.rstrip()+'\n').encode('utf-8'))
def table(headers,rows):
 def esc(value): return str(value).replace('|','\\|').replace('\n',' ')
 return '\n'.join(['| '+' | '.join(map(esc,headers))+' |','| '+' | '.join('---' for _ in headers)+' |']+['| '+' | '.join(map(esc,row))+' |' for row in rows])
def title(value): return '\n## '+value+'\n\n'

readme='# 018 · Orchard-Agentic：Agent 沙箱与评测训练\n\n> '+data['summary']+'\n\n'
readme+=table(['信息','内容'],[
 ['上游','['+upstream+']('+upstream+')'],
 ['研究版本','['+sha+']('+upstream+'/commit/'+sha+')；提交日期 2026-10-09'],
 ['trainer/slime 子模块',data['trainerCommit']+'；不是其随后更新的 main'],
 ['论文','[arXiv:2605.15040v3](https://arxiv.org/html/2605.15040v3)，2026-07-30'],
 ['许可','上游 MIT，见 [LICENSE.upstream.txt](LICENSE.upstream.txt)；模型、数据及后续项目分别核对'],
 ['收录日期','2026-10-22（Asia/Shanghai）'],
 ['网页','[公开研究页](https://yydshly.github.io/1022_codex_project/018-orchard-agentic/) · [本地静态入口](web/index.html)；[部署证据](deployment-verification.json)'],
 ['验证范围','固定版本代码与文档、引导图、静态网页和公开发布；未运行上游集群、模型或训练']])
readme+='\n\n![Orchard-Agentic 理解引导图：角色分工、执行架构、沙箱功能、Docker 对比、价值与效果](assets/orchard-agentic-overview.png)\n\n'
readme+='沿用本次讨论最终确认的 2400 × 5480 中文长图，PNG 与 SVG 保持原始字节。最终是文字与矢量排版绘图；ImageGen 初次调用因网络错误失败，没有使用模型生成结果。见 [图片来源与哈希](assets/README.md)。\n'
readme+=title('先用一句话理解')
readme+='Orchard Env 是“容器隔离环境 + Agent 操作接口 + 批量管理服务”。整个仓库在此基础上组织评测、训练配方与研究数据。\n\n'
readme+=table(['角色','负责什么','配置边界'],data['roles'])+'\n'
readme+=title('能力与工作原理')
readme+=table(['沙箱能力','具体行为','接口 / 模块'],[r[:3] for r in data['capabilities']])+'\n\n'
readme+='Python、浏览器、项目依赖和数据按任务镜像或准备步骤配置。实际隔离强度取决于底层容器和集群，不应据名称推断为虚拟机级隔离。\n\n'
for i,(name,body) in enumerate(data['steps'],1): readme+=str(i)+'. **'+name+'**：'+body+'\n'
readme+='\n编排服务通过 Kubernetes 管理创建、调度、策略和删除；高频命令与文件请求经 Pod 内执行服务处理。多副本可用 Redis 共享状态，CPU 沙箱与模型推理/训练资源可独立配置。\n\n'
readme+=table(['组成','定位','能力'],data['layers'])+'\n'
readme+=title('效果与评测口径')
readme+=table(['对象','作者报告','条件'],[[x['title'],x['value']+'；'+x['body'],x['condition']] for x in data['metrics']])+'\n\n'
readme+='以上来自作者论文与仓库，本研究未复现。不同基座与框架的成绩不应串成同一模型升级过程；pass@3 与三次都成功的 pass³ 也不同。环境服务改善执行与管理，模型能力提升依赖训练和推理方法。\n'
readme+=title('与直接使用 Docker 的区别')
readme+=table(['对比项','直接 Docker','Orchard'],data['comparisons'])+'\n\n'
readme+='本机、少量固定任务或现有脚本稳定时，Docker + 脚本通常足够。统一远程服务、跨机器任务、批量评测或训练有实际需求时再评估 Orchard；没有只由数量决定的切换阈值。GitHub Pages 仅承载本研究静态网站，不运行真正的沙箱控制面。\n'
readme+=title('可沉淀的技术')
readme+='以下为研究归纳，尚未抽取为独立产品或 SDK。\n\n'
readme+=table(['顺序','技术资产','可沉淀内容','验收前提'],[[x['priority'],x['name'],x['description'],x['acceptance']] for x in data['techniques']])+'\n\n'
readme+='输入输出和分阶段顺序见 [REUSE.md](REUSE.md)。\n'
readme+=title('后期可扩展的使用场景')
readme+=table(['场景','可复用底座','仍需补充','状态'],[[x['name'],x['reuse'],x['extra'],x['stage']] for x in data['scenarios']])+'\n\n'
readme+='完整状态快照、暂停/恢复、分叉和前缀共享仍列在上游 Roadmap；评测中断后继续集合中的任务不等于恢复进程与内存快照。身份、计费、多租户业务授权等需另外设计。\n'
readme+=title('运行与验证')
readme+='网页使用无依赖 HTML/CSS/JavaScript，内容从 research.json 加载，未连接模型或沙箱服务。仓库根目录执行：\n\n'
readme+='\x60\x60\x60bash\npython scripts/project_catalog.py check\npython projects/018-orchard-agentic/scripts/verify_web.py\npython scripts/build_site.py --output _site/orchard-preview-1\npython -m http.server 8927 --bind 127.0.0.1 --directory _site/orchard-preview-1\n\x60\x60\x60\n\n'
readme+='预览 /018-orchard-agentic/。重新构建需另选空目录，构建器不会删除旧产物。文档由 scripts/build_docs.py 从同一份研究内容生成。\n\n'
readme+='真正运行上游需另按[固定部署文档]('+pinned('orchard_env/docs/deployment.md')+')配置 Kubernetes、Calico、镜像仓库和服务。SDK 要求 Python 3.11+；模型接口、凭据、任务环境与训练 GPU 另外准备。本文未执行云资源创建。\n'
readme+=title('来源与研究记录')
readme+='- [研究笔记](notes.md)\n- [固定文件来源与 SHA-256](research-evidence.json)\n- [上游许可与来源声明](THIRD_PARTY_NOTICES.md)\n'
for source in data['sources']: readme+='- ['+source['label']+']('+source['url']+')\n'
readme+='- [论文第三版](https://arxiv.org/html/2605.15040v3)\n- [Docker Engine](https://docs.docker.com/engine/)\n\n'
readme+='公开字节核对使用 scripts/verify_deployment.py 的 --commit 和 --run-url 参数；网络传输中断时可选 --transport curl，需安装 curl。每个请求最多尝试三次，curl 连接上限 10 秒、单次总时限 45 秒；不会跳过内容哈希验证。\n\n'
readme+='本研究未实测集群并发、隔离强度、真实浏览器任务、论文成绩、训练和成本。技术沉淀及扩展场景是后续实施建议，不宣称已交付这些服务。网页验证和公开部署以相应 JSON 记录为准。'
write('README.md',readme)

reuse='# 技术沉淀与后期扩展计划\n\n这些是从固定源码归纳的复用建议，尚未抽取为独立模块。\n'
for t in data['techniques']:
 reuse+=title(t['priority']+' · '+t['name'])+t['description']+'\n\n'
 reuse+=table(['输入','输出','验收条件'],[[t['input'],t['output'],t['acceptance']]])+'\n\n'
 reuse+='[固定源码参照]('+pinned(t['source'])+')\n'
reuse+=title('分阶段落地')
for name,body in [
 ('一：单机任务协议','先用 Docker + 脚本跑一个真实需求，约定输入、镜像、时限、输出、日志与测试。验收：失败、超时、取消有记录，制品可定位、环境可回收；够用时可停在此阶段。'),
 ('二：远程环境服务','出现统一接口或跨机器需求后接入 Orchard Env，配置集群、网络策略、资源预算和生命周期。验收：远程创建、传输、执行、导出与清理可追踪，并在目标配置验证边界和容量。'),
 ('三：批量评测证据','锁定任务、模型、框架、镜像、推理预算和重试协议，保留原事件与标准轨迹。验收：补丁可重评分，环境故障与任务失败分开，中断评测可继续未完成任务。'),
 ('四：任务环境与训练','按需加入浏览器、文档或工具镜像，再接奖励器与训练器。验收：先小规模验证任务、观测、动作、结果、数据许可与评分闭环，再扩并发或训练。')]:
 reuse+='### '+name+'\n\n'+body+'\n\n'
reuse+=title('可扩展场景')
reuse+=table(['类型','场景','可复用','新增前提','状态'],[[x['type'],x['name'],x['reuse'],x['extra'],x['stage']] for x in data['scenarios']])
reuse+='\n\n完整状态快照和分叉属于后续路线图。统一身份、计费、多租户业务授权与任意恶意代码的强隔离也不能视为当前仓库已完整提供的产品能力。'
write('REUSE.md',reuse)
write('web/reuse-plan.md',reuse)

notes='''# 研究笔记：从模型成绩到执行底座

日期：2026-10-22。上游固定为 bd8da32b3a075128700caab75bbc491fb6fdc16e。

## 讨论中澄清的理解

1. 最初的模型成绩介绍容易让读者误以为这是现成助手。应先说明容器、操作接口和批量治理，再介绍模型研究。
2. “类似 Docker 沙箱”抓住了基础。Docker 也能执行、限资源、控网络；Orchard 额外组合了任务 API、跨机器生命周期和研究配套。
3. 模型、Agent 框架和沙箱分工不同。Pod 内轻量 agent 是命令执行服务，CLI 预装也不等于模型已接入。
4. 整个仓库大于 Orchard Env。评测工具、训练方法、后续项目与未来路线图应分别标明，避免功能混同。

## 固定源码观察

- sandbox_client.py 暴露同步/异步生命周期、执行、文件、补丁与 PTY。
- exec_manager.py 取得 Pod IP 后调用 agent_client；后者通过 HTTP 请求 Pod 的 /exec 等端点。
- agent/server.py 真正启动子进程，收集 stdout、stderr、exit_code，并提供 PTY。
- sandbox_manager.py、settings.py 与 Redis 存储管理状态、预算、心跳、TTL 与回收。
- orchard_evalkit 区分执行与评分、环境故障与任务失败，并保留原始和标准化轨迹。

21 份原始文件的固定 URL、SHA-256 与字节数见 research-evidence.json。没有复制整个上游实现。

## 结果口径

论文初版 SWE 主模型为 Qwen3-30B-A3B；第三版扩展到 Qwen3.5-35B-A3B。页面以第三版为准。
61.4%、69.7%、73.0% 对应 Qwen3.5 的基础、RPR 与六候选价值重排。Claw pass@3 是三次至少一次成功，不是 pass³ 或单次成功率。
性能数字来自作者测试配置，未做本地复现或成本验证。

## 引导图与验证

沿用对话最终确认的 PNG/SVG，保持原始字节。首次 ImageGen 请求网络失败，最终长图为确定性文字与矢量排版。来源目录保留实际制作脚本与失败尝试指令，不能标成成功的模型生图。

本研究验证源码、文档、静态网页和公开部署；未运行云/K8s、模型、真实浏览器任务或 GPU 训练。
评测集合可恢复不等于进程内存快照恢复；上游快照与分叉仍列在 Roadmap。
'''
write('notes.md',notes)

assets='# 引导图、来源与使用说明\n\n'
assets+='沿用本次对话最终确认的原创理解长图，用于根索引封面、研究首页与网页首屏。替代文字描述角色分工、执行架构、十二项沙箱能力、Docker 对比、价值与效果。PNG 和 SVG 与对话原件逐字节一致。\n\n'
assets+=table(['文件','说明','SHA-256'],[[x['path'].removeprefix('assets/'),'2400×5480，PNG 展示 / SVG 编辑',x['sha256']] for x in guide['assets']])+'\n\n'
assets+='## 制作与事实来源\n\n最终采用 Python/Pillow 文字排版与同步 SVG 绘制，无第三方产品标识或官方界面截图。初次 ImageGen 请求网络失败，未使用其结果。source/ 保留实际脚本、来源说明和初次尝试指令。\n\n'
assets+='事实来自固定版本上游文档和论文第三版，见 ../research-evidence.json。图中实验是作者报告，非本次实测；使用建议为研究判断，快照分叉已标为后续计划。\n\n'
assets+='## 发布副本\n\nweb/assets/ 下同名文件与原件保持字节一致，verify_web.py 核对原件、发布副本与 guide-manifest.json。只使用相对路径，不依赖对话本地文件系统。'
assets+='\n\n## 网页验收截图\n\nweb-preview-mobile.png 为本地同源 iframe 的 375/768 宽度验收，截图中显示实际测量。publication-preview.png 为正式发布页面的浏览器截图；它们不是上游运行效果或训练证据。'
write('assets/README.md',assets)
write('THIRD_PARTY_NOTICES.md','''# 来源与许可

- 上游研究对象：Microsoft Orchard-Agentic，固定提交 bd8da32b3a075128700caab75bbc491fb6fdc16e；MIT 许可原文保存在 LICENSE.upstream.txt。
- 本项目没有复制整个上游实现；通过固定版本链接和来源 SHA-256 提供核查入口。
- 论文 arXiv:2605.15040v3 的实验指标为作者报告，未在本地复现。
- 图解是本次对话原创的中文文字与矢量排版，保留原始 PNG、SVG 与制作脚本；不是官方宣传图或界面截图。
- 网页与研究文字为独立整理，不是 Microsoft 官方网站，不提供真实沙箱或模型服务。
- trainer/slime、后续项目、模型权重与数据应分别核对许可；主仓库 MIT 不自动覆盖全部第三方材料。
''')
write('.gitattributes','''assets/*.svg -text whitespace=cr-at-eol
web/assets/*.svg -text whitespace=cr-at-eol
research-evidence.json -text
web/research-evidence.json -text
LICENSE.upstream.txt -text
web/LICENSE.upstream.txt -text
assets/source/* -text -whitespace
''')
if not (PROJECT/'deployment-verification.json').exists():
 write('deployment-verification.json',json.dumps({'status':'pending','scope':'Static research page publication only; upstream cluster, inference and training not run.'},ensure_ascii=False,indent=2))
print('Built README, reuse plan, notes, image provenance and notices.')
