# scan-pdf-to-reflowable-epub

一个面向 Codex 的通用工作流，用于把合法可读取的文本型或扫描型 PDF 转成可搜索、可调字号、适合 Kindle 等阅读器的可重排 EPUB。

它不把每页简单包装成图片。流程先诊断文本层和扫描质量，再建立页面角色表与章节边界，执行 OCR/版面重建，最后分别检查内容、结构、视觉和 EPUB 包。中文出版物、双语书、脚注、图片、页码和角注都有专门规则。

## 核心原则

- 默认采用 `structure-only`：只改结构和排版，不静默修改可见文字。
- 原书目录、印刷页码和可视章节页优先于固定 PDF 页差或标题正则。
- 数字不等于脚注。数量、年份、序号、词义编号、英文 OCR 中的 `1` 都必须排除误判。
- 页码锚点位于真实换页处，即使换页发生在一个连续段落中。
- 双语书先判断是逐段、对页还是前后两部分，再决定导航和对照方式。
- EPUBCheck 只证明包结构，不证明章节正确、文字未变或 Kindle 上排版良好。

## 仓库结构

```text
SKILL.md                         主工作流和约束
agents/openai.yaml               Codex 界面元数据
scripts/inspect_pdf.py           PDF 结构和文本层检查
scripts/render_pages.py          页面渲染
scripts/build_epub.py            从规范化 JSON 构建 EPUB 3
scripts/validate_epub.py         包、XML、链接、封面和 EPUBCheck 验证
scripts/text_fingerprint.py       可见文字指纹与不变性比较
scripts/compare_text_inventory.py 构建前文字清单与 EPUB 顺序一致性比较
scripts/audit_reflow.py           编号项疑似误断段候选审计
references/conversion-workflow.md 端到端流程和常见失败模式
references/text-layer-and-complex-pages.md 文本层、页眉、图表和多栏页面规则
references/chinese-document-structure.md 中文出版物结构知识
references/paragraph-and-list-reconstruction.md 段落、列表与跨页续接规则
references/                      OCR、重建、脚注和 QA 规则
tests/smoke_test.py              使用合成内容进行 EPUB 构建与验证
tests/reflow_audit_test.py        编号块误断段回归测试
tests/content_inventory_test.py   可见文字顺序守恒回归测试
scripts/repo_check.py            发布前结构、语法、链接与隐私检查
.github/workflows/validate.yml   GitHub Actions 自动验证
docs/PUBLISHING.md               GitHub 发布步骤
```

## 安装与依赖

获取完整仓库，不要只复制 Raw `SKILL.md`，因为工作流依赖
`references/` 与 `scripts/`：

```bash
git clone https://github.com/OWNER/scan-pdf-to-reflowable-epub.git
python3 -m pip install -r scan-pdf-to-reflowable-epub/requirements.txt
```

把仓库目录放入 Codex 的 skills 目录，或使用 Codex 自带的 Skill 安装流程。
将 `OWNER` 替换为实际 GitHub 用户或组织名。PDF 检查和渲染推荐安装
Poppler；没有 Poppler 时可以安装 `requirements-optional.txt` 中的 PyMuPDF
作为检查后备。OCR 引擎、EPUBCheck 和 Calibre 按任务需要另行安装。

发布前与修改后运行：

```bash
python3 scripts/repo_check.py
python3 tests/smoke_test.py
```

GitHub 建仓、网页上传与终端推送的完整说明见
[docs/PUBLISHING.md](docs/PUBLISHING.md)。

## 建议流程

```bash
python3 scripts/inspect_pdf.py input.pdf --json work/inspection.json
python3 scripts/render_pages.py input.pdf work/pages --dpi 220
python3 scripts/build_epub.py work/manifest.json output/book.epub
python3 scripts/compare_text_inventory.py work/source-visible.txt output/book.epub \
  --exclude-tag h1 --exclude-tag figure --exclude-epub-type pagebreak \
  --json work/content-inventory.json
python3 scripts/audit_reflow.py output/book.epub --json work/reflow-audit.json
python3 scripts/validate_epub.py output/book.epub --strict --json work/validation.json
python3 scripts/text_fingerprint.py output/book.epub --write work/text-fingerprint.json --ignore-whitespace
```

如本地已有 EPUBCheck：

```bash
python3 scripts/validate_epub.py output/book.epub --strict --epubcheck /path/to/epubcheck.jar
```

再次构建后比较可见文字：

```bash
python3 scripts/text_fingerprint.py output/book-v2.epub --compare work/text-fingerprint.json
```

`compare_text_inventory.py` 用于核对“经过页面分类、页眉页码清理和版面重建后、打包前”的可见文字是否按同一顺序进入 EPUB。排除生成章标题、图像页和页码锚点时必须显式声明。精确匹配能发现打包阶段的漏字、增字和乱序，但不能发现清单建立之前发生的误删，因此仍需审查删除账本和原页抽样。

`text_fingerprint.py` 适合比较两次 EPUB 构建。注意：若重建时故意删除重复标题、移出封底 OCR 或改变生成文字，需要在 QA 报告中解释差异，不能把指纹相等当作语义校对。

`audit_reflow.py` 只报告需要回看扫描版的候选位置，不会自动改书。典型候选是：一个编号段落没有句末标点，却在 XHTML 中紧接着另一个普通段落。它可能是被错误拆开的列表续行，也可能是合法的编号式小标题；必须结合行距、缩进、字体和原页结构判断。

## 构建清单格式

最小示例：

```json
{
  "identifier": "example-book",
  "title": "Book title",
  "author": "Author",
  "language": "zh-CN",
  "cover": "assets/cover.jpg",
  "sections": [
    {
      "id": "chapter-1",
      "title": "第一章",
      "part": "中文",
      "language": "zh-CN",
      "epub_type": ["chapter"],
      "html": "<p>……</p>",
      "toc": [{"title": "第一节", "fragment": "section-1"}]
    }
  ]
}
```

`html` 是上游版面重建阶段生成并审核过的 XHTML 片段，不应把未经转义的原始 OCR 直接塞入。可选字段：

- `file_name`：章节在 EPUB 中的相对路径；
- `show_title`：是否由构建器生成章标题；
- `include_in_toc`：是否进入导航；
- `resources`：图片或其他资源，每项包含 `source`、`href`，可选 `id`、`media_type`；
- `css` 或 `css_file`：覆盖默认阅读样式；
- `cover_href`、`cover_title`：封面资源路径和标签。

所有任务特有的页码、书名、坐标阈值、OCR 结果、报告和绝对路径都应留在任务工作目录，不进入这个通用仓库。复杂图表可以少量保留为图片，但普通正文仍应保持可搜索、可重排；双栏索引必须先分栏再合并行。

## 安全边界

- 仅处理用户有权读取的文件；不绕过 DRM、密码或访问控制。
- 默认本地 OCR，不上传页面或正文。
- 下载、安装和运行第三方工具分别处理。
- 不提交私人 PDF、OCR 数据、用户名、绝对路径或含个人信息的测试样本。

标准交付物是 EPUB 与 QA 报告。只有本地存在合适转换器时才额外生成 AZW3；没有实际设备测试时，不声称已经完成 Kindle 实机验证。

## 参与和许可

提交改进前请阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 与
[SECURITY.md](SECURITY.md)。项目采用 [MIT License](LICENSE)。
