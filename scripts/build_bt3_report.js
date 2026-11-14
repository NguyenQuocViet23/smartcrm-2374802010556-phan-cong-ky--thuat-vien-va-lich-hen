// NOTE: this script only produced the FIRST DRAFT of the report. The file that is submitted is
// docs/BT3_2374802010556_NguyenQuocViet_HoanChinh.docx, which was then edited directly (Session 16
// structure: cover, sections 1-7, appendices A-B). Do not re-run this script over it.
//
// Builds docs/BT3_2374802010556_NguyenQuocViet.docx following the 7 parts of the
// "Minh chứng cho checklist buổi 14" template: 1 Repo · 2 Phản hồi BT2 · 3 Test Plan ·
// 4 Test Report · 5 Bug Log · 6 Test một lệnh + CI · 7 Việc còn lại; appendices A Deployment
// Guide (+ Docker evidence) · B Security checklist · C API docs · D AI disclosure.
// Usage: node scripts/build_bt3_report.js <repo-dir> [output.docx]
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, ShadingType,
  AlignmentType, HeadingLevel, ImageRun, PageBreak, Footer, PageNumber, TableOfContents,
  LevelFormat, PageOrientation, BorderStyle, VerticalAlign, ExternalHyperlink, TableLayoutType,
} = require("docx");

const REPO_DIR = process.argv[2];
const OUT = process.argv[3] || path.join(REPO_DIR, "docs", "BT3_2374802010556_NguyenQuocViet.docx");
const SHOTS = path.join(REPO_DIR, "docs", "screenshots");
const REPO = "https://github.com/NguyenQuocViet23/smartcrm-2374802010556-phan-cong-ky--thuat-vien-va-lich-hen";
const commit = (sha) => `${REPO}/commit/${sha}`;
const blob = (rel) => `${REPO}/blob/main/${rel}`;
const git = (...a) => require("child_process").execFileSync("git", a, { cwd: REPO_DIR, encoding: "utf8" }).trim();
const HEAD = git("rev-parse", "HEAD");
const HEAD_SUBJECT = git("log", "-1", "--format=%s");
const HEAD_DATE = git("log", "-1", "--format=%cd", "--date=format:%d/%m/%Y %H:%M");

const FONT = "Times New Roman";
const MONO = "Consolas";
const BODY = 24; // 12 pt
const PORTRAIT = { width: 11906, height: 16838 };
const P_MARGIN = { top: 1134, bottom: 1134, left: 1701, right: 1134 };
const P_WIDTH = PORTRAIT.width - P_MARGIN.left - P_MARGIN.right; // 9071
const L_MARGIN = { top: 1134, bottom: 1134, left: 1134, right: 1134 };
const L_WIDTH = PORTRAIT.height - L_MARGIN.left - L_MARGIN.right; // 14570

// ---------- text helpers ----------
function runs(text, o = {}) {
  const size = o.size || BODY;
  return String(text).split(/(\*\*[^*]+\*\*|`[^`]+`)/).filter(Boolean).map((part) => {
    if (part.startsWith("**")) return new TextRun({ text: part.slice(2, -2), bold: true, italics: o.italics, size, font: FONT, color: o.color });
    if (part.startsWith("`")) return new TextRun({ text: part.slice(1, -1), font: MONO, size: size - 3, color: o.color });
    return new TextRun({ text: part, bold: o.bold, italics: o.italics, size, font: FONT, color: o.color, highlight: o.highlight });
  });
}
const P = (text, o = {}) => new Paragraph({
  alignment: o.align || AlignmentType.JUSTIFIED,
  spacing: { before: o.before ?? 0, after: o.after ?? 100, line: o.line ?? 276 },
  keepNext: o.keepNext, indent: o.indent,
  children: runs(text, o),
});
const H1 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun({ text: t })] });
const H2 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun({ text: t })] });
const H3 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun({ text: t })] });
const bullet = (t, level = 0) => new Paragraph({
  numbering: { reference: "bullets", level }, spacing: { after: 60, line: 276 },
  alignment: AlignmentType.JUSTIFIED, children: runs(t),
});
const code = (lines) => lines.map((l, i) => new Paragraph({
  shading: { type: ShadingType.CLEAR, color: "auto", fill: "F2F2F2" },
  spacing: { before: i === 0 ? 60 : 0, after: i === lines.length - 1 ? 120 : 0, line: 240 },
  indent: { left: 200 },
  children: [new TextRun({ text: l || " ", font: MONO, size: 18 })],
}));
const pageBreak = () => new Paragraph({ children: [new PageBreak()] });
const link = (text, url, size = BODY) => new ExternalHyperlink({
  link: url, children: [new TextRun({ text, style: "Hyperlink", font: FONT, size })],
});

// ---------- tables ----------
const BORDER = { style: BorderStyle.SINGLE, size: 4, color: "8C8C8C" };
const BORDERS = { top: BORDER, bottom: BORDER, left: BORDER, right: BORDER, insideHorizontal: BORDER, insideVertical: BORDER };
function cell(content, width, o = {}) {
  const items = Array.isArray(content) ? content : [content];
  return new TableCell({
    width: { size: width, type: WidthType.DXA },
    shading: o.fill ? { type: ShadingType.CLEAR, color: "auto", fill: o.fill } : undefined,
    verticalAlign: o.vAlign || VerticalAlign.TOP,
    margins: { top: 50, bottom: 50, left: 90, right: 90 },
    columnSpan: o.span,
    children: items.map((t) => (t instanceof Paragraph ? t : new Paragraph({
      alignment: o.align || AlignmentType.LEFT, spacing: { after: 30, line: 250 },
      children: runs(t, { size: o.size || 20, bold: o.bold, color: o.color }),
    }))),
  });
}
function table(headers, rows, widths, o = {}) {
  const size = o.size || 20;
  const total = widths.reduce((a, b) => a + b, 0);
  const head = headers ? [new TableRow({
    tableHeader: true, cantSplit: true,
    children: headers.map((h, i) => cell(h, widths[i], { fill: "1F2A37", bold: true, color: "FFFFFF", size })),
  })] : [];
  const body = rows.map((r, ri) => new TableRow({
    cantSplit: o.cantSplit ?? true,
    children: r.map((c, i) => cell(c, widths[i], {
      size, fill: o.firstColFill && i === 0 ? "EEF2F6" : (o.zebra && ri % 2 ? "F7F9FB" : undefined),
      bold: o.firstColBold && i === 0,
    })),
  }));
  return new Table({ layout: TableLayoutType.FIXED, width: { size: total, type: WidthType.DXA }, columnWidths: widths, borders: BORDERS, rows: [...head, ...body] });
}
function box(title, lines, fill = "FBEDEB", borderColor = "C0392B", width = P_WIDTH) {
  const b = { style: BorderStyle.SINGLE, size: 8, color: borderColor };
  return new Table({
    width: { size: width, type: WidthType.DXA }, columnWidths: [width],
    borders: { top: b, bottom: b, left: b, right: b, insideHorizontal: b, insideVertical: b },
    rows: [new TableRow({ children: [new TableCell({
      width: { size: width, type: WidthType.DXA },
      shading: { type: ShadingType.CLEAR, color: "auto", fill },
      margins: { top: 100, bottom: 100, left: 160, right: 160 },
      children: [
        new Paragraph({ spacing: { after: 100 }, children: runs(title, { bold: true, color: borderColor }) }),
        ...lines.map((l) => new Paragraph({ alignment: AlignmentType.JUSTIFIED, spacing: { after: 80, line: 264 }, children: Array.isArray(l) ? l : runs(l, { size: 22 }) })),
      ],
    })] })],
  });
}

// ---------- images ----------
let fig = 0;
let SEC = "1";
const section = (s) => { SEC = s; fig = 0; return []; };
function pngSize(file) { const b = fs.readFileSync(file); return [b.readUInt32BE(16), b.readUInt32BE(20)]; }
function figure(file, caption, maxW = 580, maxH = 760) {
  const full = path.join(SHOTS, file);
  if (!fs.existsSync(full)) throw new Error(`missing image ${file}`);
  const [w, h] = pngSize(full);
  const scale = Math.min(maxW / w, maxH / h);
  fig += 1;
  return [
    new Paragraph({ alignment: AlignmentType.CENTER, keepNext: true, spacing: { before: 120, after: 60 },
      children: [new ImageRun({ type: "png", data: fs.readFileSync(full), transformation: { width: Math.round(w * scale), height: Math.round(h * scale) } })] }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 },
      children: runs(`Hình ${SEC}.${fig}. ${caption} (docs/screenshots/${file})`, { italics: true, size: 20 }) }),
  ];
}
function placeholder(file, what, how) {
  if (fs.existsSync(path.join(SHOTS, file))) return figure(file, what);
  fig += 1;
  return [
    box(`[CHÈN ẢNH] Hình ${SEC}.${fig}. ${what}`, [
      `Tệp cần chụp: **docs/screenshots/${file}**`,
      `Cách chụp: ${how}`,
      "Ảnh phải thấy rõ lệnh đã chạy và kết quả. Chụp xong thay khung này bằng ảnh (Insert → Pictures).",
    ], "FFF6D5", "B7791F"),
    new Paragraph({ spacing: { after: 160 }, children: [] }),
  ];
}

// =====================================================================================
// CONTENT
// =====================================================================================

// ---------- cover ----------
const center = (t, o = {}) => P(t, { align: AlignmentType.CENTER, ...o });
const cover = [
  center("TRƯỜNG ĐẠI HỌC VĂN LANG", { bold: true, size: 28, after: 40 }),
  center("KHOA CÔNG NGHỆ THÔNG TIN", { bold: true, size: 28, after: 600 }),
  center("CHUYÊN ĐỀ TỐT NGHIỆP 1 (71ITGR40203) · HỌC KỲ 1, NĂM HỌC 2026 – 2027", { size: 24, after: 900 }),
  center("BÁO CÁO BÀI TẬP 3", { bold: true, size: 40, after: 160 }),
  center("KIỂM THỬ HỆ THỐNG, SỬA LỖI VÀ ĐÓNG GÓI TRIỂN KHAI", { bold: true, size: 30, after: 400 }),
  center("Đề tài: Smart CRM – Mekong Mobile", { size: 26, after: 60 }),
  center("Luồng L04: Phân công kỹ thuật viên và lịch hẹn", { size: 26, after: 700 }),
  new Table({
    width: { size: 8200, type: WidthType.DXA }, columnWidths: [2600, 5600], borders: BORDERS,
    alignment: AlignmentType.CENTER,
    rows: [
      ["Sinh viên", "Nguyễn Quốc Việt"],
      ["MSSV", "2374802010556"],
      ["Lớp", "261_71ITGR40203_05"],
      ["Track", "SE – Kỹ thuật phần mềm"],
      ["Mã luồng", "L04 – Phân công kỹ thuật viên và lịch hẹn"],
      ["Giảng viên", "……………………………………………"],
      ["Repo GitHub (PUBLIC)", new Paragraph({ children: [link(REPO, REPO, 18)] })],
      ["Tag nộp bài", new Paragraph({ children: [link("v1.0", `${REPO}/tree/v1.0`, 20)] })],
      ["CI (GitHub Actions)", new Paragraph({ children: [link("Tab Actions – lần chạy #1 Success", `${REPO}/actions/runs/42468831038`, 20)] })],
      ["Link deploy thử", "Không có – hệ thống chạy cục bộ bằng Docker Compose (Phụ lục A)"],
    ].map(([k, v]) => new TableRow({ children: [cell(k, 2600, { fill: "EEF2F6", bold: true, size: 22 }), cell(v, 5600, { size: 22 })] })),
  }),
  center("TP. Hồ Chí Minh, tháng 11 năm 2026", { size: 24, before: 1400, after: 0 }),
];

// ---------- TOC + reading guide ----------
const linkLine = (rel, label = "Tệp trong repo") => new Paragraph({ spacing: { after: 120 }, children: [
  ...runs(`**${label}:** `), link(blob(rel), blob(rel), 20)] });
const toc = [
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 }, children: [new TextRun({ text: "MỤC LỤC", bold: true, size: 30, font: FONT })] }),
  new TableOfContents("Mục lục", { hyperlink: true, headingStyleRange: "1-2" }),
  pageBreak(),
  H1("Cách trình bày báo cáo"),
  P("Báo cáo trình bày theo đúng bảy phần của mẫu **\"Minh chứng cho checklist buổi 14\"**. Các thành phần còn lại của Bài tập 3 (gói đóng gói, Deployment Guide, checklist bảo mật, tài liệu API) và bảng khai báo AI bắt buộc đặt ở phụ lục. Mọi link mở được ở cửa sổ ẩn danh (repo PUBLIC); mọi số liệu lấy từ lần chạy thật."),
  table(["Thành phần của BT3", "Nằm ở", "Tệp trong repo"], [
    ["Repo PUBLIC, commit mới nhất, tag", "Phần 1", "–"],
    ["Phản hồi BT2 và quyết định xử lý", "Phần 2", "`docs/thay-doi-thiet-ke.md` (TD-20 … TD-24)"],
    ["TP1 – Test Plan rút gọn, bốn mục", "Phần 3", "`docs/test-plan.md`"],
    ["TP2 – Test Report 12 test case, tám cột, năm loại, chạy thật, có ảnh", "Phần 4", "`docs/test-report.md`, `tests/bt3/test_bt3.py`, `docs/screenshots/`"],
    ["TP3 – Bug Log ≥ 3 bug (≥ 1 Major), bảy dòng, link commit", "Phần 5", "`docs/bug-log.md`"],
    ["Toàn bộ test PASS bằng một lệnh; CI", "Phần 6", "`pytest.ini`, `.github/workflows/ci.yml`"],
    ["Việc còn lại trước hạn BT3", "Phần 7", "–"],
    ["TP4 – Gói đóng gói ≤ 2 lệnh · TP5 – Deployment Guide (EN)", "Phụ lục A", "`docker-compose.yml`, `Dockerfile.backend`, `docs/deployment-guide.md`"],
    ["TP5 – Checklist bảo mật bảy mục (EN)", "Phụ lục B", "`docs/security-checklist.md`"],
    ["TP6 – Tài liệu kỹ thuật: API docs [SE] (EN)", "Phụ lục C", "`docs/api.md`, `docs/api-requests.http`"],
    ["Khai báo sử dụng công cụ AI (bắt buộc)", "Phụ lục D", "`docs/ai-disclosure.md`"],
  ], [4000, 1400, 3671], { firstColBold: true }),
];

// ---------- 1. Repo ----------
const part1 = [
  pageBreak(), ...section("1"),
  H1("1. Repo"),
  table(["Mục", "Giá trị"], [
    ["Repo GitHub (PUBLIC)", new Paragraph({ children: [link(REPO, REPO, 18)] })],
    ["Commit mới nhất", new Paragraph({ children: [link(commit(HEAD), commit(HEAD), 17),
      ...runs(` – \"${HEAD_SUBJECT}\" (${HEAD_DATE}, commit mới nhất trên nhánh main khi lập báo cáo)`, { size: 20 })] })],
    ["Tag nộp bài", new Paragraph({ children: [link(`${REPO}/tree/v1.0`, `${REPO}/tree/v1.0`, 18), ...runs(" – gắn khi hoàn tất (phần 7)", { size: 20 })] })],
    ["Track · mã luồng", "SE · L04 – Phân công kỹ thuật viên và lịch hẹn"],
    ["Kiểm tra PUBLIC", "GitHub API trả `\"visibility\": \"public\"`; trang commit mở được khi không đăng nhập (Hình 1.1)."],
  ], [2300, 6771], { firstColBold: true, size: 21 }),
  P("", { after: 60 }),
  P("Vì giảng viên không được mời làm collaborator, mọi link phải mở được với người **không đăng nhập**. Ảnh dưới chụp ngày 10/11/2026 bằng trình duyệt mới, không cookie, không đăng nhập (tương đương cửa sổ ẩn danh): trang hiện nút \"Sign in\" và nội dung commit sửa BUG-08."),
  ...figure("BUG-08-commit-an-danh.png", "Trang commit sửa BUG-08 mở khi không đăng nhập (cửa sổ ẩn danh)"),
];

// ---------- 1. Test Plan ----------
const testPlan = [
  pageBreak(),
  H1("3. Test Plan"),
  linkLine("docs/test-plan.md"),
  P("Kế hoạch gồm bốn mục theo mẫu Buổi 13: phạm vi và phần chủ ý không kiểm · loại test và số lượng mỗi tầng · tiêu chí thành công đo được · môi trường và dữ liệu thử."),
  H2("3.1. Phạm vi và phần chủ ý KHÔNG kiểm"),
  P("**Kiểm:** các quy tắc nghiệp vụ đã hiện thực của L04, qua API thật trên dữ liệu case-study thật: gợi ý kỹ thuật viên (FR2, QT-08), phân công và đổi kỹ thuật viên (FR3, FR4, QT-07), đặt lịch hẹn và chống trùng (FR6, FR7), vòng đời trạng thái (FR8, QT-06), tạo/sửa phiếu (QT-02), phân quyền theo trung tâm/kỹ thuật viên (QT-14), che số điện thoại (QT-15), hợp đồng lỗi của API (400/401/403/404/409, không 500), năm mục OWASP mức nhận biết (A01, A02, A04, A05, A07) và tính tái lập của bước dựng cơ sở dữ liệu."),
  P("**Chủ ý KHÔNG kiểm:**", { keepNext: true }),
  table(["Không kiểm", "Lý do"], [
    ["Hiệu năng, tải đồng thời lớn", "Prototype một người dùng; NFR hiệu năng ngoài phạm vi BT3"],
    ["Giao diện trên nhiều trình duyệt / di động", "Chỉ kiểm Chromium; giao diện đã có TC14–TC18 của Buổi 10"],
    ["UC8 báo cáo khối lượng, SMS/Zalo, tồn kho linh kiện", "Ngoài phạm vi L04 (TD-05, TD-15)"],
    ["Luồng tiếp nhận phiếu L2 đầy đủ", "Ngoài phạm vi; tạo phiếu chỉ là CRUD tối giản (TD-17)"],
    ["Rà soát bảo mật đầy đủ, kiểm thử xâm nhập", "Thuộc Chuyên đề tốt nghiệp 2; BT3 chỉ kiểm năm mục OWASP"],
    ["A04 bằng truy vấn bảng users", "Hệ thống không có bảng tài khoản (TD-02); kiểm băm mật khẩu trong `demo_accounts.json` ở Phụ lục B, mục 3"],
  ], [3800, 5271]),
  P("", { after: 60 }),
  P("**Kỹ thuật chọn dữ liệu:** phân vùng tương đương (hợp lệ / sai định dạng / sai quyền) và giá trị biên hai bên ranh giới: tay nghề **3 | 2** (TC-04); lịch liền kề **10:00 = 10:00 | chồng 1 phút 09:01** (TC-05); mã phiếu **không tồn tại | vượt BIGINT** (TC-08); chuỗi **có chữ | chỉ khoảng trắng** (TC-06, TC-07)."),
  H2("3.2. Loại test và số lượng mỗi tầng"),
  table(["Tầng", "Công cụ", "Số lượng", "Lệnh"], [
    ["Unit (lớp service, không CSDL)", "pytest", "104 test: quy tắc phiếu, lịch hẹn, ánh xạ lỗi, xác thực", "`python -m pytest`"],
    ["Integration (PostgreSQL thật)", "pytest + TestClient", "7 test: CRUD, chạy lại không nhân đôi, TC22–TC25", "`python -m pytest tests/integration -m integration`"],
    ["API / end-to-end (HTTP thật, Swagger, UI)", "pytest + Playwright", "12 test case TC-01 … TC-12 của Test Report", "`python -m pytest -m bt3`"],
  ], [2500, 1700, 2671, 2200]),
  P("", { after: 60 }),
  P("12 test case phủ đủ năm loại: **luồng đúng** (TC-01, TC-02, TC-03) · **giá trị biên** (TC-04, TC-05) · **dữ liệu sai** (TC-06, TC-07, TC-08) · **bảo mật/chất lượng dữ liệu** (TC-09, TC-10, TC-11) · **tái lập** (TC-12). Mỗi quy tắc nghiệp vụ đã hiện thực có ít nhất một test."),
  H2("3.3. Tiêu chí thành công đo được"),
  bullet("12/12 test case đã chạy thật, mỗi case có kết quả thực tế cụ thể (mã HTTP, mã lỗi, đếm bản ghi trước/sau) và ảnh chụp trong `docs/screenshots/`."),
  bullet("Sau khi sửa bug: unit, integration và `-m bt3` đều 0 FAIL."),
  bullet("Không còn bug Critical mở; mọi bug Major trở lên có commit sửa riêng và test case chạy lại PASS."),
  bullet("Mọi lỗi nghiệp vụ biết trước trả đúng 400/401/403/404/409, không có phản hồi 500; phản hồi lỗi không chứa traceback, tên bảng hay câu SQL."),
  bullet("Bước dựng cơ sở dữ liệu chạy lần hai cho cùng số dòng ở cả sáu bảng."),
  H2("3.4. Môi trường và dữ liệu thử"),
  table(["Mục", "Giá trị"], [
    ["Máy chạy", "Windows 11, Python 3.14 (venv, `requirements-dev.txt`), Node.js 24, PostgreSQL 18, Chromium của Playwright 1.64"],
    ["CSDL nguồn", "`smartcrm_test` = dữ liệu case-study đầy đủ: 7.317 phiếu, 35.719 dòng log, 300 lịch hẹn, 38 kỹ thuật viên, 6 trung tâm"],
    ["Cô lập", "Mỗi test case tạo lại `smartcrm_work_test` từ `smartcrm_test` và khởi động backend riêng trên bản sao (TD-12); không ghi vào `smartcrm`"],
    ["Tiền điều kiện", "Dựng bằng SQL trên bản sao từ bản ghi thật (ví dụ khối lượng 5/2/8, tay nghề 3/2), không dựa vào dữ liệu còn sót trên máy"],
    ["TC-12", "Bộ mẫu `data/sample` trong repo, nạp vào `smartcrm_load_test` (xoá trước và sau khi chạy)"],
    ["Tài khoản", "Tài khoản demo `QL_TT01…06`, `KT002…` sinh từ `DEMO_PASSWORD` trong `.env`; token ký bằng `SECRET_KEY`"],
    ["Cần trước khi chạy", "`.env` có `TEST_DB_NAME=smartcrm_test`; `python scripts/setup_all.py --with-test-db`; frontend `npm run dev` (cho TC-11); cổng 8000 trống"],
  ], [2200, 6871], { firstColBold: true }),
];

// ---------- 2. Test Report (landscape) ----------
const tc = [
  ["TC-01", "Luồng đúng", "Bản sao từ dữ liệu thật. Trung tâm TT03, nhóm KHAC có ≥ 3 KTV đủ điều kiện; dựng khối lượng KT003 = 5, KT022 = 2, KT027 = 8 phiếu đang làm; tắt các KTV đủ điều kiện khác; tạo phiếu MỚI TEST-7816.",
    "1. Đăng nhập QL_TT03, lấy token.\n2. Authorize trên Swagger.\n3. GET /api/tickets/7816/technician-suggestions.",
    "Token QL_TT03; ticket_id = 7816", "HTTP 200; đúng 3 KTV theo thứ tự KT022 (2) → KT003 (5) → KT027 (8).", "Cao",
    "HTTP 200; thứ tự KT022 (2) → KT003 (5) → KT027 (8).", "PASS"],
  ["TC-02", "Luồng đúng", "Như TC-01: phiếu MỚI TEST-7816 chưa có KTV, có 1 dòng log.",
    "1. Đăng nhập QL_TT03.\n2. POST /api/tickets/7816/assignment.\n3. Đọc lại bảng ticket, đếm ticket_status_log.",
    "{\"technician_id\": 22} (KT022, tay nghề 3)", "HTTP 201; status = DA_PHAN_CONG, technician_id = 22; log của phiếu tăng đúng 1 dòng.", "Cao",
    "HTTP 201; status = DA_PHAN_CONG, technician_id = 22; log 1 → 2.", "PASS"],
  ["TC-03", "Luồng đúng", "Phiếu thật BH-000009/2026 ở DA_PHAN_CONG, KTV KT008 (id 8), trung tâm TT01; KT008 trống 10/12/2026 09:00–10:00 (ngày chọn tự động, cách ngày chạy ~30 ngày).",
    "1. Đăng nhập QL_TT01.\n2. Đếm bảng appointment.\n3. POST /api/appointments.\n4. Đếm lại.",
    "ticket_id 9, NHAN, 2026-12-10T09:00+07:00 → 10:00+07:00, note \"BT3 TC-03\"", "HTTP 201; lịch DA_HEN, technician_id = 8 (KTV của phiếu); appointment +1.", "Cao",
    "HTTP 201; status = DA_HEN, technician_id = 8; appointment 300 → 301.", "PASS"],
  ["TC-04", "Biên", "Trung tâm TT01: KT020 tay nghề MAN_HINH = 3, KT033 tay nghề MAN_HINH = 2 (cả hai đang làm); tạo phiếu MỚI nhóm MAN_HINH.",
    "1. Đăng nhập QL_TT01.\n2. GET …/technician-suggestions.\n3. POST …/assignment với KT033.\n4. Đọc lại phiếu.",
    "Ranh giới QT-08 \"tay nghề ≥ 3\": 3 (trong) và 2 (ngoài)", "(a) 200, KT020 có (proficiency 3), KT033 không có. (b) 400 TECHNICIAN_NOT_ELIGIBLE; phiếu vẫn MOI, chưa có KTV.", "Cao",
    "(a) HTTP 200: KT020 có, KT033 không có. (b) HTTP 400 TECHNICIAN_NOT_ELIGIBLE; phiếu còn MOI, technician_id = None.", "PASS"],
  ["TC-05", "Biên", "Phiếu BH-000009/2026, KT008; ngày 10/12/2026 trống 08:00–11:00; tạo trước lịch A 09:00–10:00.",
    "1. Đăng nhập QL_TT01.\n2. Đếm lịch DA_HEN của KT008.\n3. POST lịch 10:00–11:00.\n4. POST lịch 08:00–09:01.\n5. Đếm lại.",
    "(a) 10:00–11:00 (bắt đầu = kết thúc của A); (b) 08:00–09:01 (chồng A 1 phút)", "(a) 201. (b) 409 APPOINTMENT_OVERLAP kèm khung trống gợi ý. Lịch DA_HEN của KTV chỉ tăng 1.", "Cao",
    "(a) HTTP 201. (b) HTTP 409 APPOINTMENT_OVERLAP, gợi ý 2 khung trống. Lịch DA_HEN của KT008: 8 → 9.", "PASS"],
  ["TC-06", "Dữ liệu sai", "Phiếu BH-000009/2026 của KT008 (DA_PHAN_CONG); KT012 cùng trung tâm, đang làm, tay nghề ≥ 3.",
    "1. Đăng nhập QL_TT01.\n2. PUT /api/tickets/9/assignment.\n3. Đọc lại phiếu, đếm log.",
    "{\"technician_id\": 12, \"reason\": \"   \"} (3 dấu cách)", "400 REASON_REQUIRED; phiếu vẫn của KT008; log không thêm dòng.", "Trung bình",
    "HTTP 400 REASON_REQUIRED \"Lý do đổi kỹ thuật viên là bắt buộc.\"; technician_id vẫn 8; log 2 → 2.", "PASS"],
  ["TC-07", "Dữ liệu sai", "Dữ liệu thật trên bản sao: 7.317 phiếu, không phiếu nào có tên/mô tả rỗng.",
    "1. Đăng nhập QL_TT01.\n2. Đếm bảng ticket.\n3. POST /api/tickets với SĐT sai.\n4. POST /api/tickets với 3 trường chữ chỉ có khoảng trắng.\n5. Đếm lại.",
    "Phần còn lại hợp lệ (PIN, CAO, hạn +3 ngày). (a) customer_phone = \"09123\"; (b) customer_name = serial_no = issue_desc = \"   \"",
    "(a) 400 INVALID_PHONE. (b) 400, phản hồi nêu tên trường customer_name. Bảng ticket không thêm bản ghi.", "Trung bình",
    "Lần 1 (commit 9cccebd): (a) 400 INVALID_PHONE; (b) **HTTP 201, tạo BH-007801/2026 với tên, serial, mô tả rỗng; ticket 7317 → 7318.**\nLần 2 (sau sửa, commit 224fd69): (a) 400 INVALID_PHONE; (b) 400 REQUIRED_FIELD_BLANK, fields = [customer_name, serial_no, issue_desc]; ticket 7317 → 7317.",
    "Lần 1: **FAIL** → BUG-08\nLần 2: PASS"],
  ["TC-08", "Dữ liệu sai", "Mã phiếu lớn nhất trong dữ liệu thật là 7800.",
    "1. Đăng nhập QL_TT01.\n2. GET /api/tickets/99999999.\n3. GET /api/tickets/99999999999999999999.",
    "(a) 99 999 999 (không tồn tại); (b) 99 999 999 999 999 999 999 (> 2^63 − 1)", "Cả hai: 404 TICKET_NOT_FOUND, không phải 500.", "Trung bình",
    "(a) HTTP 404 TICKET_NOT_FOUND. (b) HTTP 404 TICKET_NOT_FOUND.", "PASS"],
  ["TC-09", "Bảo mật A01", "Phiếu BH-000009/2026 của KT008 ở DA_PHAN_CONG; KT002 là KTV khác. Phiếu MỚI BH-000001/2025 thuộc trung tâm 5, khách \"Hoàng Anh Dung\".",
    "1. Đăng nhập KT002, PATCH /api/tickets/9/status.\n2. Đăng nhập QL_TT01, PUT /api/tickets/{id BH-000001/2025}.\n3. Đọc lại hai phiếu và log.",
    "(a) token KT002, {\"to_status\": \"DANG_XU_LY\"}; (b) token QL_TT01, customer_name = \"Đã bị sửa\"", "(a) 403, phiếu 9 vẫn DA_PHAN_CONG, log không đổi. (b) 403, tên khách không đổi.", "Cao",
    "(a) HTTP 403 FORBIDDEN, phiếu vẫn DA_PHAN_CONG, log 2 → 2. (b) HTTP 403 FORBIDDEN, tên khách vẫn \"Hoàng Anh Dung\".", "PASS"],
  ["TC-10", "Bảo mật A07", "Backend chạy với SECRET_KEY của .env; QL_TT01 đăng nhập được.",
    "1. GET /api/auth/me không token.\n2. Authorize token hết hạn, gọi lại.\n3. Authorize token bị sửa, gọi lại.\n4. Đối chứng bằng token gốc.",
    "(b) token QL_TT01 ký đúng khoá, exp = now − 60 s; (c) token QL_TT01 hợp lệ, đổi ký tự đầu của chữ ký", "Cả ba: 401; token gốc vẫn 200.", "Cao",
    "(a) HTTP 401 UNAUTHORIZED. (b) HTTP 401 INVALID_TOKEN. (c) HTTP 401 INVALID_TOKEN. Đối chứng: HTTP 200.", "PASS"],
  ["TC-11", "Bảo mật A05, A02", "Frontend chạy ở http://localhost:5173; QL_TT01 có 5 phiếu MỚI.",
    "1. GET /api/tickets?status=' OR 1=1 --\n2. GET /api/tickets?status=MOI&category_code=' OR 1=1 --\n3. Tạo phiếu có mô tả chứa thẻ script, mở M2 trên giao diện, theo dõi hộp thoại.\n4. Preflight OPTIONS từ http://evil.example và từ frontend.",
    "' OR 1=1 --; issue_desc = <script>alert('XSS')</script><img src=x onerror=alert(1)>", "(a) 400 INVALID_STATUS, không có traceback/SQL. (b) 200, total = 0. (c) Chuỗi hiện nguyên văn, không hộp thoại. (d) Không có Access-Control-Allow-Origin cho evil.example; có cho frontend.", "Cao",
    "(a) HTTP 400 INVALID_STATUS, không có traceback/SQL. (b) HTTP 200, total = 0. (c) Chuỗi hiện nguyên văn, 0 hộp thoại. (d) evil.example: không có header; localhost:5173: có.", "PASS"],
  ["TC-12", "Tái lập", "Database smartcrm_load_test không tồn tại (test xoá trước và sau).",
    "1. DATA_DIR=data/sample DB_NAME=smartcrm_load_test python scripts/setup_all.py\n2. Đếm sáu bảng.\n3. Chạy lại bước 1.\n4. Đếm lại, đếm phiếu MOI.",
    "Bộ mẫu data/sample trong repo", "Hai lần cùng số dòng: service_center 6, technician 38, technician_skill 159, ticket 939, ticket_status_log 3237, appointment 300; phiếu MOI = 30.", "Trung bình",
    "Lần 1 và lần 2 đều: 6 / 38 / 159 / 939 / 3237 / 300; phiếu MOI = 30.", "PASS"],
];
const TCW = [1050, 2150, 2300, 1950, 2200, 950, 2650, 1320]; // = 14570
const split = (t) => String(t).split("\n");
const tcTable = new Table({
  layout: TableLayoutType.FIXED, width: { size: L_WIDTH, type: WidthType.DXA }, columnWidths: TCW, borders: BORDERS,
  rows: [
    new TableRow({ tableHeader: true, cantSplit: true, children: ["Mã", "Tiền điều kiện", "Các bước", "Dữ liệu thử", "Kết quả mong đợi", "Ưu tiên", "Kết quả thực tế", "PASS / FAIL"]
      .map((h, i) => cell(h, TCW[i], { fill: "1F2A37", bold: true, color: "FFFFFF", size: 18 })) }),
    ...tc.map((r) => new TableRow({ cantSplit: true, children: [
      cell([`**${r[0]}**`, `(${r[1]})`], TCW[0], { size: 17, fill: "EEF2F6" }),
      cell(split(r[2]), TCW[1], { size: 17 }), cell(split(r[3]), TCW[2], { size: 17 }), cell(split(r[4]), TCW[3], { size: 17 }),
      cell(split(r[5]), TCW[4], { size: 17 }), cell(r[6], TCW[5], { size: 17 }), cell(split(r[7]), TCW[6], { size: 17 }),
      cell(split(r[8]).map((x) => (x.includes("FAIL") || x === "PASS" || x.endsWith("PASS") ? `**${x.replace(/\*\*/g, "")}**` : x)), TCW[7], { size: 17,
        fill: r[8].includes("FAIL") ? "FDE2DE" : "E3F4E8" }),
    ] })),
  ],
});
const testReport = [
  H1("4. Test Report"),
  linkLine("docs/test-report.md"),
  bullet("**Số test case đã chạy thật: 12 / Số PASS: 12 / Số FAIL: 0** (lần chạy cuối 10/11/2026). Ghi trung thực: lần chạy đầu 08/11/2026 có 11 PASS, 1 FAIL (TC-07 → BUG-08, đã sửa)."),
  bullet("**Đủ 5 loại (luồng đúng, biên, dữ liệu sai, bảo mật/chất lượng dữ liệu, tái lập): Có** – không thiếu loại nào (bảng ở mục 4.1)."),
  new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 120 }, children: [
    ...runs("**Ảnh chụp kết quả:** "), link(`${REPO}/tree/main/docs/screenshots`, `${REPO}/tree/main/docs/screenshots`, 18),
    ...runs(" – mỗi test case có ảnh đặt tên theo mã test (mục 4.3).")] }),
  P("**Cách chạy.** Mã nguồn test: `tests/bt3/test_bt3.py`. Mỗi test case dựng tiền điều kiện bằng SQL trên bản sao `smartcrm_work_test` (clone từ dữ liệu thật), thực hiện bước bằng **Swagger của backend thật**, chụp ảnh bằng Playwright, ghi kết quả đọc được từ API/CSDL, rồi mới so với kết quả mong đợi. Kết quả thực tế của mỗi lần chạy được test tự ghi vào `docs/screenshots/bt3-ket-qua-chay.md`. Chạy cả bộ: `python -m pytest -m bt3`; chạy lại một case: `python -m pytest -m bt3 -k tc05` (thay số)."),
  H2("4.1. Tổng kết"),
  table(["Lần chạy", "Commit", "Số TC", "PASS", "FAIL", "Ghi chú"], [
    ["Lần 1 – 08/11/2026 16:35", "`9cccebd`", "12", "11", "1", "TC-07 FAIL → ghi BUG-08 (phần 5), sửa ở commit `224fd69`"],
    ["Lần 2 – 08/11/2026 16:47, sau khi sửa BUG-08", "`224fd69`", "12", "12", "0", "TC-07 chạy lại PASS; các case khác không đổi"],
    ["Lần 3 – 10/11/2026 14:29–14:34 (lần chạy cho ảnh hiện tại)", "`4e16cf3`", "12", "12", "0", "Kết quả như lần 2; TC-03, TC-05 đặt lịch ngày 10/12/2026 vì test chọn ngày trống cách ngày chạy ~30 ngày (ảnh `BT3-12-passed.png`, phần 6)"],
  ], [3300, 1300, 900, 900, 900, 7270], { size: 20 }),
  P("", { after: 40 }),
  table(["Loại test (năm loại của BT3)", "Test case", "Truy vết"], [
    ["Luồng đúng", "TC-01, TC-02, TC-03", "US2/FR2/QT-08 · US3/FR3/QT-07 · FR6"],
    ["Giá trị biên (hai bên ranh giới)", "TC-04 (tay nghề 3 | 2), TC-05 (liền kề | chồng 1 phút)", "QT-08 · FR7, A3"],
    ["Dữ liệu sai", "TC-06, TC-07, TC-08", "FR4/QT-07 · QT-02 · hợp đồng lỗi README §4"],
    ["Bảo mật / chất lượng dữ liệu", "TC-09 (A01), TC-10 (A07), TC-11 (A05, A02)", "QT-14, OWASP Top 10:2025"],
    ["Tái lập", "TC-12", "C5, TD-19"],
  ], [3800, 5500, 5270], { size: 20, firstColBold: true }),
  H2("4.2. Bảng tám cột"),
  P("Tám cột theo mẫu Buổi 13: Mã · Tiền điều kiện · Các bước · Dữ liệu thử · Kết quả mong đợi · Ưu tiên · Kết quả thực tế · PASS/FAIL. Ảnh của từng case ở mục 4.3.", { size: 22 }),
  tcTable,
  P("", { after: 60 }),
  P("**Ghi chú trung thực.** Trước khi chạy, em dự đoán TC-08 (b) sẽ trả 500 vì mã vượt giới hạn BIGINT. Chạy thật cho kết quả 404 (PostgreSQL so sánh như số và không tìm thấy dòng nào), nên TC-08 ghi PASS và không có mục Bug Log nào cho dự đoán này.", { size: 22 }),
];

// ---------- 3. Bug Log ----------
const B = (n, t) => [new TextRun({ text: `${n}. `, bold: true, font: FONT, size: 22 }), ...runs(t, { size: 22 })];
const bugLog = [
  pageBreak(),
  H1("5. Bug Log"),
  linkLine("docs/bug-log.md"),
  P("Mỗi bug ghi đủ bảy dòng theo mẫu Buổi 13 và được gỡ theo bốn bước của Buổi 11 (tái lập → khoanh vùng → sửa nguyên nhân → xác nhận). Mức độ phân loại bằng ba câu hỏi: **người dùng có làm được việc không · dữ liệu có sai hay bị lộ không · có cách làm tạm không**. Ba bug nộp cho BT3 đều là Major, mỗi bug có một commit `fix` chỉ chứa thay đổi của bug đó."),
  ...[
    ["BUG-08", "Major", "Phiếu được tạo khi tên khách, serial, mô tả chỉ có khoảng trắng (phát hiện bởi TC-07)", "224fd6902da028a096100d077e80a1e752fbf600"],
    ["BUG-07", "Major", "API treo hơn 2 phút khi không kết nối được cơ sở dữ liệu", "25e3d1ebaa7eeba552f7bc05d0d379181a082546"],
    ["BUG-03", "Major", "Bản clone mới không dựng được hệ thống theo README", "a947ed735765dc34ccd58b37b222f9b6c4cbdcf5"],
  ].map(([id, sev, sum, sha]) => new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 80 }, children: [
    ...runs(`**${id}** · ${sev} · ${sum} · `), link(commit(sha), commit(sha), 18)] })),
  P("Mã bug giữ đúng như trong `docs/bug-log.md` để link, Test Report và tài liệu khớp nhau. Mỗi link trỏ tới một commit `fix` chỉ chứa thay đổi của bug đó.", { size: 22 }),
  H2("5.1. Ba bug nộp BT3 – mỗi bug bảy dòng"),
  P("", { after: 120 }),
  box("BUG-08 — Phiếu được tạo khi tên khách, serial và mô tả chỉ có khoảng trắng", [
    B(1, "**Mã và mức độ:** BUG-08 · MAJOR — dữ liệu sai được lưu thật vào bảng `ticket`: phiếu không có tên khách, serial, mô tả nên kỹ thuật viên không biết máy nào, lỗi gì (người dùng phía sau không làm được việc). Không phải Critical vì không lộ dữ liệu, không mất dữ liệu cũ, và có cách làm tạm (Quản lý sửa lại phiếu khi còn MỚI)."),
    B(2, "**Phát hiện bởi:** TC-07 (b), lần chạy 1 ngày 08/11/2026, commit `9cccebd` — mong đợi 400, nhận 201."),
    B(3, "**Triệu chứng:** `POST /api/tickets` trả 201 và tạo phiếu BH-007801/2026 với `customer_name = \"\"`, `serial_no = \"\"`, `issue_desc = \"\"`; bảng ticket 7317 → 7318. `PUT /api/tickets/{id}` có cùng lỗi vì dùng chung hàm."),
    B(4, "**Cách tái lập:** đăng nhập QL_TT01; gọi `POST /api/tickets` với customer_name, serial_no, issue_desc = \"   \", customer_phone = \"0912345678\", category PIN, priority CAO, due_date sau 3 ngày; truy vấn `SELECT count(*) FROM ticket WHERE btrim(customer_name) = ''` ra 1 (ảnh trước khi sửa ở mục 5.3)."),
    B(5, "**Nguyên nhân:** `TicketRequest` (`schemas/tickets.py`) chỉ kiểm `min_length=1`, mà \"   \" dài 3 ký tự nên qua được; sau đó `_clean_fields` trong `services/ticket_service.py` gọi `.strip()` biến chúng thành chuỗi rỗng nhưng không kiểm lại. Cột trong CSDL là NOT NULL nên chuỗi rỗng vẫn được nhận."),
    B(6, "**Cách sửa:** thêm quy tắc thuần `require_text_fields()` trong `services/ticket_rules.py`: cắt khoảng trắng ba trường và ném `DomainError(INVALID, \"REQUIRED_FIELD_BLANK\", …, fields=[…])` nêu tên mọi trường trống; `_clean_fields` dùng hàm này cho cả tạo và sửa phiếu; `app/main.py` đã ánh xạ sẵn INVALID → 400. Thêm 4 unit test trong `tests/test_crud_rules.py` (một luồng đúng, ba dữ liệu sai) để bug không quay lại."),
    [new TextRun({ text: "7. ", bold: true, font: FONT, size: 22 }), new TextRun({ text: "Commit và xác nhận: ", bold: true, font: FONT, size: 22 }),
      link(commit("224fd6902da028a096100d077e80a1e752fbf600"), commit("224fd6902da028a096100d077e80a1e752fbf600"), 18),
      ...runs(" · chạy lại TC-07 → (b) HTTP 400 `REQUIRED_FIELD_BLANK`, bảng ticket 7317 → 7317 → **PASS** (ảnh `TC-07.png`, `TC-07_b.png` ở mục 4.3). Luồng đúng không hỏng: TC-11 vẫn tạo được phiếu hợp lệ (201) → PASS; integration `test_ticket_create_read_update_cancel` → PASS; toàn bộ unit `python -m pytest` → 104 passed (ảnh `BUG-08-fixed.png`, phần 6).", { size: 22 })],
  ]),
  P("", { after: 160 }),
  box("BUG-07 — API treo vài phút khi cơ sở dữ liệu không kết nối được", [
    B(1, "**Mã và mức độ:** BUG-07 · MAJOR — khi CSDL gặp sự cố, mọi màn hình quay chờ hơn 2 phút rồi mới lỗi: người dùng không làm được việc và không biết hệ thống đang hỏng; không có cách làm tạm phía người dùng. Không Critical vì không sai hay lộ dữ liệu."),
    B(2, "**Phát hiện bởi:** phép thử \"suy giảm có kiểm soát\" của BT2 (tắt CSDL rồi gọi API, ảnh `docs/bt2-evidence/BT2_07_M1_csdl_tat_503_thu_lai.png`); nay được giữ bởi unit test `test_database_connection_has_a_timeout`."),
    B(3, "**Triệu chứng:** backend trỏ tới cổng CSDL không có PostgreSQL; `GET /api/tickets` không trả lời sau hơn 2 phút, giao diện M1 hiện \"Đang tải…\" mãi."),
    B(4, "**Cách tái lập:** đặt `DB_PORT=1` trong `.env`, chạy backend, đăng nhập QL_TT01 rồi gọi `GET /api/tickets`."),
    B(5, "**Nguyên nhân:** engine SQLAlchemy không đặt thời gian chờ kết nối; trên Windows kết nối tới cổng đóng không bị từ chối ngay. Đo riêng `psycopg.connect(port=1)`: không có `connect_timeout` thì treo > 2 phút, có `connect_timeout=3` thì lỗi sau 3 giây."),
    B(6, "**Cách sửa:** `get_engine()` trong `core/database.py` truyền `connect_args={\"connect_timeout\": DB_CONNECT_TIMEOUT}` (mặc định 3 giây, khai báo trong `.env.example`); lỗi kết nối đã được `app/main.py` ánh xạ thành 503 `DATABASE_UNAVAILABLE`."),
    [new TextRun({ text: "7. Commit và xác nhận: ", bold: true, font: FONT, size: 22 }),
      link(commit("25e3d1ebaa7eeba552f7bc05d0d379181a082546"), commit("25e3d1ebaa7eeba552f7bc05d0d379181a082546"), 18),
      ...runs(" · gọi lại API: HTTP 503 `DATABASE_UNAVAILABLE` sau 3,0 giây, có dòng log; unit test `test_database_connection_has_a_timeout` → PASS (nằm trong 104 passed ngày 08/11/2026).", { size: 22 })],
  ]),
  P("", { after: 160 }),
  box("BUG-03 — Bản clone mới không dựng được hệ thống theo README", [
    B(1, "**Mã và mức độ:** BUG-03 · MAJOR — người khác (giảng viên) làm đúng README trên thư mục trống thì không dựng được hệ thống; không sai/lộ dữ liệu; cách làm tạm là tự tạo thư mục `data/raw` (người mới không biết)."),
    B(2, "**Phát hiện bởi:** phép thử clone vào thư mục trống và làm theo README từng bước (Buổi 11)."),
    B(3, "**Triệu chứng:** đến bước chép dữ liệu, `Copy-Item <thư-mục-CSV>\\*.csv data\\raw\\` báo \"The directory name is invalid\"."),
    B(4, "**Cách tái lập:** `git clone` repo vào thư mục mới, làm theo README đến bước chép CSV vào `data\\raw\\`."),
    B(5, "**Nguyên nhân:** `.gitignore` có dòng `data/raw/` bỏ qua cả thư mục; Git không lưu thư mục rỗng nên bản clone không có `data/raw/`."),
    B(6, "**Cách sửa:** `.gitignore` đổi thành `data/raw/*` + `!data/raw/.gitkeep` và thêm `data/raw/.gitkeep`; CSV vẫn không bị commit. Về sau thêm bộ mẫu `data/sample/` để clone không cần CSV từ LMS (TD-19)."),
    [new TextRun({ text: "7. Commit và xác nhận: ", bold: true, font: FONT, size: 22 }),
      link(commit("a947ed735765dc34ccd58b37b222f9b6c4cbdcf5"), commit("a947ed735765dc34ccd58b37b222f9b6c4cbdcf5"), 18),
      ...runs(" · clone lại từ đầu: bản clone có `data/raw/`, bước chép dữ liệu chạy được, `setup_all.py` nạp xong. Hiện TC-12 kiểm bước dựng CSDL từ bộ mẫu chạy hai lần không nhân đôi → PASS.", { size: 22 })],
  ]),
  P("", { after: 160 }),
  H2("5.2. Bug của các buổi trước không dùng làm bug nộp BT3"),
  P("Năm bug dưới đây là bug thật đã sửa ở Buổi 10–12 và có đủ bảy dòng trong `docs/bug-log.md`. Em không dùng chúng làm minh chứng \"một bug – một commit\" vì commit sửa gộp với việc khác hoặc không phải commit `fix`.", { size: 22 }),
  table(["Mã", "Mức độ", "Tóm tắt", "Commit", "Lý do không dùng"], [
    ["BUG-01", "Minor", "pytest dừng khi tên test có tiếng Việt (stdout cp1252)", "eae4931", "Commit `test`, gộp với việc thêm unit test"],
    ["BUG-02", "Minor", "M3 nhấp nháy \"Đang tải…\" khi chọn phiếu", "ebfbb35", "Commit gộp ba thay đổi giao diện"],
    ["BUG-04", "Minor", "Lỗi DLL khi clone vào đường dẫn quá dài", "2febebd", "Commit `docs` (chỉ thêm cảnh báo README)"],
    ["BUG-05", "Minor", "M3 dài hơn 20.000 px, hiện mã thô DA_DONG", "7707702", "Commit `feat`"],
    ["BUG-06", "Minor", "Service trả mã HTTP, vi phạm tách lớp", "ee4013f", "Commit `refactor` lớn"],
  ], [1000, 900, 3271, 1200, 2700], { size: 20, firstColBold: true }),
];

// ---------- 4. Deployment Guide (English) ----------
const deploy = [
  pageBreak(),
  H1("Phụ lục A. Deployment Guide (English)"),
  P("Audience: anyone who needs to run the system from an empty folder (a reviewer, a new developer, an operator). Version: tag `v1.0`. Source: `docs/deployment-guide.md`."),
  H2("A.1. Prerequisites"),
  table(["Item", "Version", "Notes"], [
    ["Git", "any recent", "On Windows clone into a short path such as `D:\\Projects` (BUG-04)"],
    ["Docker Desktop or Docker Engine with Compose v2", "Compose v2 (needs `service_completed_successfully`)", "Must be running"],
    ["Free ports", "–", "5173 (UI), 8000 (API), 5433 on 127.0.0.1 (PostgreSQL); change `APP_PORT` / `DB_HOST_PORT` if taken"],
    ["Internet during the first build", "–", "Pulls `postgres:16`, `python:3.12-slim`, `node:22-alpine` and the locked packages"],
  ], [3000, 2600, 3471]),
  P("", { after: 40 }),
  P("Nothing else is needed: Python, Node.js and PostgreSQL run inside containers, and the sample data (`data/sample/`, extracted from the real case-study data) is part of the repository."),
  H2("A.2. Configuration"),
  P("All configuration is read from environment variables in `.env`, which is never committed (`.gitignore`). `.env.example` lists every variable with a placeholder value."),
  table(["Variable", "Used by", "Meaning"], [
    ["`DB_NAME`, `DB_USER`, `DB_PASSWORD`", "db, init, backend", "PostgreSQL database and credentials"],
    ["`DB_HOST_PORT`", "db", "Host port for PostgreSQL, bound to 127.0.0.1 only (default 5433)"],
    ["`DB_CONNECT_TIMEOUT`", "backend", "Seconds before a database connection attempt fails with HTTP 503 (default 3)"],
    ["`SECRET_KEY`", "backend", "HMAC key for login tokens; at least 32 random characters"],
    ["`DEMO_PASSWORD`", "init, backend", "Password of every demo account; stored only as a PBKDF2 hash"],
    ["`APP_PORT`", "backend, frontend", "API port on the host (default 8000)"],
  ], [3000, 1800, 4271]),
  P("", { after: 40 }),
  P("The placeholder values in `.env.example` are enough for a local demo. For any shared or public deployment, replace `DB_PASSWORD`, `SECRET_KEY` and `DEMO_PASSWORD` with fresh random values, for example:"),
  ...code(["python -c \"import secrets; print(secrets.token_urlsafe(48))\""]),
  H2("A.3. Build and run (two commands)"),
  P("Get the code into an empty folder:"),
  ...code([`git clone --branch v1.0 ${REPO}.git smartcrm`, "cd smartcrm"]),
  P("Then the two commands:"),
  ...code(["cp .env.example .env            # Windows PowerShell: Copy-Item .env.example .env", "docker compose up -d --build"]),
  P("What happens:", { keepNext: true }),
  bullet("`db` starts PostgreSQL 16 and waits until it is healthy."),
  bullet("`init` (one-shot) runs `scripts/setup_all.py`: create the database if missing → apply `db/migrations` → load the sample data (939 tickets, 3,237 status-log rows, 300 appointments, 38 technicians, 6 centers) → create the demo accounts in the `demo_accounts` volume. Running it again duplicates nothing (TC-12)."),
  bullet("`backend` (FastAPI, non-root user) starts only after `init` succeeded; it is healthy when `GET /db-check` answers."),
  bullet("`frontend` (React + Vite) starts after the backend is healthy."),
  H2("A.4. Verify"),
  ...code(["docker compose ps"]),
  P("Expected: `db`, `backend` and `frontend` show `running (healthy)`; `init` shows `exited (0)`."),
  table(["Check", "How", "Expected"], [
    ["Database reachable from the API", "Open http://localhost:8000/db-check", "`{\"database_time\": \"...\"}`"],
    ["API documentation", "Open http://localhost:8000/docs", "Swagger UI lists the endpoints"],
    ["Login", "http://localhost:5173 → `QL_TT01`, password = `DEMO_PASSWORD`", "Screen M1 lists the new tickets of center TT01"],
    ["Technician view", "Log in as `KT002`", "Screen M3 \"Phiếu của tôi\""],
    ["Data loaded", "`docker compose logs init`", "Shows `ticket=939, ticket_status_log=3237`, `appointment=300` and ends with `HOÀN TẤT`"],
  ], [2600, 3400, 3071]),
  H2("A.5. Operations, troubleshooting and rollback"),
  table(["Situation", "Action"], [
    ["Stop", "`docker compose down` (data is kept in the `postgres_data` volume)"],
    ["Reset everything", "`docker compose down -v`, then `docker compose up -d --build`"],
    ["Logs", "`docker compose logs -f backend` (errors are logged without being sent to clients)"],
    ["`init` exited with an error", "`docker compose logs init`; usually `DB_USER`/`DB_PASSWORD` changed after the volume was created → `docker compose down -v`"],
    ["Port already in use", "Change `APP_PORT` or `DB_HOST_PORT` in `.env`, or stop the other service"],
    ["Login answers 503 `AUTH_CONFIGURATION_ERROR`", "`SECRET_KEY` is shorter than 32 characters"],
    ["API answers 503 `DATABASE_UNAVAILABLE`", "The database is down or unreachable; the API fails after `DB_CONNECT_TIMEOUT` seconds instead of hanging (BUG-07)"],
    ["Roll back to an earlier version", "`docker compose down`, `git checkout <tag>` (e.g. `v0.2`), `docker compose up -d --build`; use `down -v` if the schema differs"],
  ], [3200, 5871]),
  P("", { after: 40 }),
  P("Limits of this setup: the frontend runs the Vite development server and Swagger UI is enabled, which suits a demo or review environment. A production deployment would serve a static build (`npm run build`) behind HTTPS, disable `/docs`, and keep PostgreSQL unreachable from outside the Docker network."),
];

// ---------- 5. Security checklist (English) ----------
const security = [
  pageBreak(),
  H1("Phụ lục B. Security Checklist (English)"),
  P("Seven items, each with the evidence that was actually checked on 08/11/2026. OWASP references follow the OWASP Top 10:2025 items of the Session 13 guide. Source: `docs/security-checklist.md`."),
  table(["#", "Item", "Status", "Evidence"], [
    ["1", "No secret in the repository or its history", "Pass", "`git log --all -- .env` is empty: `.env` was never committed. Scanning `git log --all -p` for added `…PASSWORD=` / `SECRET_KEY=` lines with a value (excluding `.env.example`) returns 0 matches. CI uses throw-away values only for its own database."],
    ["2", "Configuration through environment variables; example file without real values", "Pass", "Every setting is read from the environment (`app/core/config.py`, `docker-compose.yml`). `.env.example` contains placeholders only; Deployment Guide §A.2 says to replace them for any shared deployment."],
    ["3", "Passwords stored as salted hashes (A04)", "Pass", "No users table (TD-02); demo accounts live in `data/processed/demo_accounts.json` (git-ignored). Checked: 41 accounts, all `pbkdf2_sha256$310000$<salt>$<hash>`, no plain `password` field. Comparison uses `hmac.compare_digest`."],
    ["4", "Authentication on every business endpoint; tokens cannot be forged or reused after expiry (A07)", "Pass", "All `/api/tickets`, `/api/appointments`, `/api/technicians`, `/api/auth/me` routes depend on `current_user`. Only `/`, `/db-check`, `/api/auth/login`, `/docs` are public. TC-10: no token, expired token, altered token → 401 ×3; original token → 200."],
    ["5", "Access control by role, center and technician (A01)", "Pass", "`check_ticket_scope` (QT-14) is called by every ticket/appointment use case. TC-09: technician changing another technician's ticket → 403, unchanged; manager editing another center's ticket → 403, unchanged. Technicians see masked phone numbers (QT-15)."],
    ["6", "Input validation and injection (A05)", "Pass", "All SQL uses bound parameters. TC-11: `' OR 1=1 --` as a filter → 400 or 0 rows; `<script>` in a ticket description is shown as text, no dialog fires. TC-07 / BUG-08: blank required fields are rejected with 400."],
    ["7", "Safe error handling and configuration (A02)", "Pass, with known limits", "Errors return `{\"error\", \"message\"}` only; unexpected errors give 500 `INTERNAL_ERROR`, logged server-side, no traceback (TC-11). CORS allows only `http://localhost:5173` (TC-11). Docker: PostgreSQL bound to 127.0.0.1, backend non-root, dependencies pinned."],
  ], [450, 2500, 1100, 5021], { size: 19 }),
  H2("B.1. Known limits (accepted for a demo, to fix before production)"),
  bullet("Swagger UI `/docs` is enabled and the frontend runs the Vite development server."),
  bullet("The login endpoint has no rate limiting or lockout, so passwords can be guessed repeatedly."),
  bullet("The token is kept in the browser's `localStorage`; item 6 keeps XSS out today, but an `HttpOnly` cookie would be safer."),
  bullet("The IDE's Docker scanner reports 2 high-severity vulnerabilities in the `python:3.12-slim` base image; rebuild on a newer patch image before production."),
  bullet("A full security review and penetration test are out of scope (Specialized Graduation Topic 2)."),
];

// ---------- 6. Technical documentation: API (English) ----------
const api = [
  pageBreak(),
  H1("Phụ lục C. Technical Documentation – API Reference (English)"),
  P("Base URL `http://localhost:8000`; interactive documentation generated from the code at `/docs` (Swagger UI). Bodies are JSON; times are ISO 8601 with a time zone (e.g. `2026-12-08T09:00:00+07:00`). Ticket statuses: `MOI → DA_PHAN_CONG → DANG_XU_LY → (CHO_LINH_KIEN) → HOAN_TAT`, plus `DA_DONG`, `DA_HUY`. Sources: `docs/api.md`, request file `docs/api-requests.http`."),
  H2("C.1. Authentication"),
  P("Log in with a demo account, then send `Authorization: Bearer <access_token>` on every other call. A token is valid for 8 hours. Roles: `QUAN_LY` (center manager, `QL_TT01…QL_TT06`) and `KY_THUAT_VIEN` (technician, named by `technician_code`, e.g. `KT002`). A manager sees only tickets of their own center; a technician sees only their own tickets, with the customer phone masked."),
  table(["Method", "Path", "Role", "Description"], [
    ["POST", "`/api/auth/login`", "public", "Body `{\"username\", \"password\"}` → 200 `{\"access_token\", \"token_type\": \"bearer\"}`; 401 `INVALID_CREDENTIALS`"],
    ["GET", "`/api/auth/me`", "any", "200 `{\"role\", \"center_id\", \"center_name\", \"technician_id\", \"full_name\", \"employee_id\"}`"],
  ], [900, 2400, 1000, 4771], { size: 19 }),
  H2("C.2. Tickets"),
  table(["Method", "Path", "Role", "Description"], [
    ["GET", "`/api/tickets?status=MOI&category_code=&priority=&page=&page_size=`", "manager", "Tickets of the manager's center → `{\"items\", \"total\", \"page\", \"page_size\"}`; page_size 1–100"],
    ["POST", "`/api/tickets`", "manager", "Create a ticket (status `MOI`) in the manager's center → 201"],
    ["GET", "`/api/tickets/{ticket_id}`", "any (scoped)", "Ticket detail with `technician` and `status_history`"],
    ["PUT", "`/api/tickets/{ticket_id}`", "manager", "Correct a ticket that is still `MOI`"],
    ["DELETE", "`/api/tickets/{ticket_id}?reason=`", "manager", "Soft delete: a `MOI` ticket becomes `DA_HUY`"],
    ["GET", "`/api/tickets/{ticket_id}/technician-suggestions`", "manager", "Same center, active, proficiency ≥ 3, ordered by workload ascending"],
    ["POST", "`/api/tickets/{ticket_id}/assignment`", "manager", "Body `{\"technician_id\"}` → 201; ticket becomes `DA_PHAN_CONG`, change logged"],
    ["PUT", "`/api/tickets/{ticket_id}/assignment`", "manager", "Change technician; body `{\"technician_id\", \"reason\"}`; reason required, not blank"],
    ["PATCH", "`/api/tickets/{ticket_id}/status`", "technician (owner)", "Body `{\"to_status\", \"note\"}`; forward lifecycle steps only"],
    ["GET", "`/api/tickets/{ticket_id}/appointments`", "any (scoped)", "Appointments of a ticket"],
    ["GET", "`/api/technicians/me/tickets`", "technician", "All tickets of the technician, ordered by due date, with `is_overdue`"],
  ], [900, 3600, 1300, 3271], { size: 19 }),
  P("", { after: 40 }),
  P("Ticket body for POST and PUT:", { keepNext: true }),
  ...code(["{", "  \"customer_name\": \"Nguyễn Văn An\",  \"customer_phone\": \"0912 345 678\",", "  \"serial_no\": \"SN10293A\",  \"issue_desc\": \"Máy không lên nguồn sau khi rơi\",", "  \"category_code\": \"PIN\",  \"priority\": \"CAO\",  \"due_date\": \"2026-11-11T17:00:00+07:00\"", "}"]),
  bullet("`customer_name`, `serial_no`, `issue_desc`: required and not blank (only spaces → 400 `REQUIRED_FIELD_BLANK`, BUG-08)."),
  bullet("`customer_phone`: normalised to 10 digits starting with 0; spaces, dots, dashes and `+84` are accepted."),
  bullet("`category_code`: `MAN_HINH`, `PIN`, `SAC`, `PHAN_MEM`, `NUOC_VAO`, `KHAC` · `priority`: `CAO`, `TRUNG_BINH`, `THAP` · `due_date`: with a time zone, in the future."),
  H2("C.3. Appointments"),
  table(["Method", "Path", "Role", "Description"], [
    ["POST", "`/api/appointments`", "any (scoped)", "Book a delivery/pick-up slot → 201"],
    ["GET", "`/api/appointments?status=&ticket_id=&page=&page_size=`", "any", "Manager: appointments of the center; technician: their own"],
    ["GET", "`/api/appointments/{appointment_id}`", "any (scoped)", "One appointment"],
    ["PUT", "`/api/appointments/{appointment_id}`", "any (scoped)", "Reschedule; overlap and working hours are checked again"],
    ["DELETE", "`/api/appointments/{appointment_id}`", "any (scoped)", "Soft cancel: `DA_HUY`, the slot becomes free"],
  ], [900, 3600, 1300, 3271], { size: 19 }),
  P("", { after: 40 }),
  ...code(["{\"ticket_id\": 9, \"appointment_type\": \"NHAN\",", " \"start_at\": \"2026-12-08T09:00:00+07:00\", \"end_at\": \"2026-12-08T10:00:00+07:00\", \"note\": \"optional\"}"]),
  P("Rules: `appointment_type` is `GIAO` or `NHAN`; the slot is in the future, Monday–Saturday, inside 08:00–18:00 (UTC+7), on one day, with `end_at > start_at`. The ticket must have a technician and must not be finished; the appointment belongs to the ticket's current technician. Slots are half-open `[start, end)`, so back-to-back appointments are allowed. An overlap returns 409 `APPOINTMENT_OVERLAP` with `conflicts` (appointment_id, ticket_code, start_at, end_at) and the nearest free 30-minute `free_slots`."),
  H2("C.4. Health"),
  table(["Method", "Path", "Description"], [
    ["GET", "`/`", "`Hello Smart CRM` (plain text)"],
    ["GET", "`/db-check`", "200 `{\"database_time\": \"...\"}` when the database answers; used by the Docker healthcheck"],
  ], [900, 2000, 6171], { size: 19 }),
  H2("C.5. Errors"),
  P("Every error has the shape `{\"error\": \"<CODE>\", \"message\": \"<Vietnamese message>\"}`, sometimes with `fields`, `conflicts` or `free_slots`. No error body contains a stack trace or SQL."),
  table(["HTTP", "Meaning", "Main codes"], [
    ["400", "Invalid input or broken business rule", "`VALIDATION_ERROR`, `INVALID_PHONE`, `REQUIRED_FIELD_BLANK`, `INVALID_STATUS`, `INVALID_PRIORITY`, `INVALID_CATEGORY`, `INVALID_DUE_DATE`, `INVALID_DATETIME`, `TECHNICIAN_NOT_ELIGIBLE`, `REASON_REQUIRED`, `SAME_TECHNICIAN`, `INVALID_TIME_RANGE`, `PAST_APPOINTMENT`, `OUTSIDE_WORKING_HOURS`, `TICKET_NOT_ASSIGNED` (booking), `TICKET_CLOSED`"],
    ["401", "Not logged in, expired or altered token, wrong password", "`UNAUTHORIZED`, `INVALID_TOKEN`, `INVALID_CREDENTIALS`"],
    ["403", "Wrong role, another center's or technician's ticket", "`FORBIDDEN`"],
    ["404", "Record does not exist", "`TICKET_NOT_FOUND`, `TECHNICIAN_NOT_FOUND`, `APPOINTMENT_NOT_FOUND`"],
    ["409", "Valid request, but the current state forbids it", "`TICKET_ALREADY_ASSIGNED`, `INVALID_STATUS_TRANSITION`, `TICKET_NOT_CHANGEABLE`, `TICKET_NOT_EDITABLE`, `TICKET_NOT_CANCELLABLE`, `TICKET_NOT_ASSIGNED` (technician change), `APPOINTMENT_OVERLAP`, `APPOINTMENT_NOT_EDITABLE`, `APPOINTMENT_NOT_CANCELLABLE`"],
    ["503", "Database or login configuration unavailable", "`DATABASE_UNAVAILABLE`, `DEMO_ACCOUNTS_NOT_READY`, `AUTH_CONFIGURATION_ERROR`"],
    ["500", "Unexpected error (logged on the server)", "`INTERNAL_ERROR`"],
  ], [800, 2800, 5471], { size: 19 }),
];

// ---------- 4.3 Test case screenshots ----------
const tcFigs = [
  ...section("4"),
  H2("4.3. Ảnh chụp kết quả từng test case"),
  P("Ảnh Swagger được Playwright chụp từ backend thật trong lúc test chạy: khối thao tác gồm lệnh `curl`, URL yêu cầu và phản hồi thật của server. Ảnh giao diện chụp từ frontend React thật; ảnh terminal là ảnh chụp cửa sổ PowerShell thật vừa chạy lệnh (dòng cuối ghi lệnh, mã thoát và thời gian). Không có ảnh nào được vẽ bằng chương trình."),
  ...figure("TC-01.png", "TC-01 – gợi ý KT022 (2) → KT003 (5) → KT027 (8), HTTP 200"),
  ...figure("TC-02.png", "TC-02 – phân công KT022 cho phiếu TEST-7816, HTTP 201"),
  ...figure("TC-03.png", "TC-03 – đặt lịch NHẬN 09:00–10:00 ngày 10/12/2026, HTTP 201"),
  ...figure("TC-04.png", "TC-04 (a) – gợi ý có KT020 (tay nghề 3), không có KT033 (tay nghề 2)"),
  ...figure("TC-04_b.png", "TC-04 (b) – phân công KT033 bị từ chối 400 TECHNICIAN_NOT_ELIGIBLE"),
  ...figure("TC-05.png", "TC-05 (a) – lịch liền kề 10:00–11:00 được nhận, HTTP 201"),
  ...figure("TC-05_b.png", "TC-05 (b) – lịch chồng 1 phút 08:00–09:01 bị 409 APPOINTMENT_OVERLAP"),
  ...figure("TC-06.png", "TC-06 – đổi KTV với lý do chỉ có khoảng trắng, 400 REASON_REQUIRED"),
  ...figure("TC-07.png", "TC-07 (a) – SĐT \"09123\", 400 INVALID_PHONE"),
  ...figure("TC-07_b.png", "TC-07 (b) sau khi sửa BUG-08 – 400 REQUIRED_FIELD_BLANK, nêu đủ ba trường"),
  ...figure("TC-08.png", "TC-08 (a) – ticket_id 99999999, 404 TICKET_NOT_FOUND"),
  ...figure("TC-08_b.png", "TC-08 (b) – ticket_id vượt BIGINT, 404 TICKET_NOT_FOUND"),
  ...figure("TC-09.png", "TC-09 (a) – KT002 đổi trạng thái phiếu của KT008, 403 FORBIDDEN"),
  ...figure("TC-09_b.png", "TC-09 (b) – QL_TT01 sửa phiếu của trung tâm 5, 403 FORBIDDEN"),
  ...figure("TC-10.png", "TC-10 (a) – không gửi token, 401 UNAUTHORIZED"),
  ...figure("TC-10_b.png", "TC-10 (b) – token hết hạn, 401 INVALID_TOKEN"),
  ...figure("TC-10_c.png", "TC-10 (c) – token bị sửa một ký tự, 401 INVALID_TOKEN"),
  ...figure("TC-11.png", "TC-11 (a) – status=' OR 1=1 --, 400 INVALID_STATUS"),
  ...figure("TC-11_b.png", "TC-11 (b) – category_code=' OR 1=1 --, 200 total = 0"),
  ...figure("TC-11_c.png", "TC-11 (c) – giao diện M2 hiện thẻ script dạng chữ, không có hộp thoại"),
  ...figure("TC-12.png", "TC-12 – setup_all.py chạy hai lần, số dòng sáu bảng không đổi (terminal)"),
];

// ---------- 5.2 BUG-08 before the fix ----------
const bugFigs = [
  ...section("5"),
  H2("5.3. Ảnh TC-07 trước khi sửa BUG-08 (lần chạy 1)"),
  P("Hai ảnh dưới là lần chạy đầu ngày 08/11/2026 (commit `9cccebd`), giữ lại làm minh chứng FAIL. Ảnh sau khi sửa là `TC-07.png`, `TC-07_b.png` ở mục 4.3."),
  ...figure("BUG-08_truoc-sua_TC-07.png", "TC-07 (a) lần chạy 1, trước khi sửa – 400 INVALID_PHONE"),
  ...figure("BUG-08_truoc-sua_TC-07_b.png", "TC-07 (b) lần chạy 1, trước khi sửa – FAIL: HTTP 201, phiếu BH-007801/2026 lưu tên/serial/mô tả rỗng (BUG-08)"),
];

// ---------- 6. One command, CI ----------
const part6 = [
  pageBreak(), ...section("6"),
  H1("6. Toàn bộ test PASS bằng một lệnh sau khi sửa bug"),
  P("**Có.** Sau commit sửa BUG-08, mỗi tầng kiểm thử chạy bằng một lệnh và đều 0 FAIL (ảnh terminal thật bên dưới, chụp ngày 10/11/2026):"),
  table(["Tầng", "Một lệnh", "Kết quả"], [
    ["Unit (lớp service, không cần CSDL)", "`python -m pytest`", "104 passed (Hình 6.1)"],
    ["Integration (PostgreSQL thật)", "`python -m pytest tests/integration -m integration`", "7 passed (Hình 6.2)"],
    ["12 test case của Test Report", "`python -m pytest -m bt3`", "12 passed, 12/12 test case PASS (Hình 6.3)"],
  ], [3000, 3671, 2400], { firstColBold: true }),
  ...figure("BUG-08-fixed.png", "python -m pytest – 104 passed, mã thoát 0"),
  ...figure("integration-7-passed.png", "python -m pytest tests/integration -m integration – 7 passed, mã thoát 0"),
  ...figure("BT3-12-passed.png", "python -m pytest -m bt3 – 12/12 test case PASS, mã thoát 0"),
  H2("6.1. CI (GitHub Actions)"),
  new Paragraph({ spacing: { after: 120 }, children: [...runs("**Tab Actions:** "), link(`${REPO}/actions`, `${REPO}/actions`, 20)] }),
  P("Workflow `.github/workflows/ci.yml` chạy trên mỗi lần push: cài thư viện đã khoá → unit test → dựng `smartcrm` và `smartcrm_test` từ bộ mẫu → integration test trên PostgreSQL 16. Lần chạy #1 **Success** (Hình 6.4)."),
  ...figure("CI-actions-xanh.png", "GitHub Actions – workflow CI lần #1 Success (unit + integration trên PostgreSQL)"),
];

// ---------- 7. Remaining work ----------
const part7 = [
  H1("7. Việc còn lại trước hạn BT3"),
  bullet("Gắn tag `v1.0` trên commit cuối cùng (sau khi commit báo cáo và ảnh mới), push, rồi kiểm lại mọi link ở cửa sổ ẩn danh."),
  bullet("Nộp PDF và link repo lên VLU E-learning trước khi hết buổi 16."),
];

// ---------- A.6 Docker evidence ----------
const dockerFigs = [
  ...section("A"),
  H2("A.6. Minh chứng gói Docker Compose"),
  P("Phép thử máy trắng ngày 10/11/2026: clone nhánh `main` (commit `4e16cf3`, tag `v1.0` chưa gắn) vào thư mục trống `C:\\BT3test`, rồi chạy đúng hai lệnh `Copy-Item .env.example .env` và `docker compose up -d --build` trong PowerShell. Máy dùng Docker 29.8.0, Compose v5.5.1; lần build đầu tải image mất khoảng 1 phút 50 giây. Kết quả: `db`, `backend`, `frontend` healthy, `init` thoát mã 0 sau khi tạo 41 tài khoản demo; đăng nhập `QL_TT01` bằng mật khẩu mẫu của `.env.example` thấy 5 phiếu MỚI của trung tâm TTBH Quận 10."),
  ...figure("may-trang-2-lenh.png", "Hai lệnh dựng từ thư mục trống – 10/10 bước xong, db/backend healthy, init exited, mã thoát 0 (dòng lệnh ở đầu đã cuộn khỏi cửa sổ vì output dài; lệnh được ghi ở đoạn trên)"),
  ...figure("docker-compose-ps-healthy.png", "docker compose ps -a – backend, db, frontend healthy; init Exited (0); PostgreSQL chỉ mở 127.0.0.1:5433"),
  ...figure("may-trang-dang-nhap.png", "Đăng nhập QL_TT01 trên bản dựng Docker từ thư mục trống – màn hình M1 có 5 phiếu MỚI"),
];

// ---------- Appendix A: AI disclosure ----------
const appendixA = [
  pageBreak(),
  H1("Phụ lục D. Bảng khai báo sử dụng công cụ AI"),
  P("Nguyên tắc: mọi phần có AI hỗ trợ đều được em đọc lại, chạy lại và giải thích được; kết quả ghi trong báo cáo là kết quả chạy thật, phần chưa làm được ghi rõ là chưa làm. Bảng đầy đủ: `docs/ai-disclosure.md`."),
  table(["Công cụ", "Việc AI hỗ trợ", "Tệp / hàm liên quan", "Cách em kiểm chứng"], [
    ["Claude (chat)", "BT1: bản nháp SRS, use case, kiến trúc, ERD, wireframe", "`docs/srs.md`, `docs/*.drawio`, `db/schema.sql`", "Đối chiếu từng QT-xx với case study; chạy `db/schema.sql` trên PostgreSQL thật"],
    ["GitHub Copilot", "Buổi 8–10: giao diện M1–M3, API ban đầu, script nạp dữ liệu, sinh lịch hẹn", "`src/frontend/src/**`, `scripts/load_*.py`, `scripts/gen_appointments.py`", "`npm run build`; đếm số dòng 6 bảng bằng SQL; xem `git diff` trước khi commit"],
    ["Claude Code", "BT2: tách ba lớp backend, quy tắc nghiệp vụ thuần, CRUD, xử lý CSDL tắt, bộ mẫu, TC01–TC18", "`app/routers`, `app/services`, `app/repositories`, `scripts/setup_all.py`, `tests/service`", "Toàn bộ test cũ vẫn pass sau khi tách; tắt PostgreSQL thật rồi gọi API"],
    ["Claude Code", "BT3: kế hoạch từ slide Buổi 14 và tài liệu Buổi 13; Test Plan; 12 test case TC-01…TC-12 trên backend thật với ảnh Swagger", "`docs/test-plan.md`, `tests/bt3/*`, `docs/screenshots/*`", "Chạy `python -m pytest -m bt3`: lần 1 11/12 (TC-07 FAIL, ghi trung thực), sau sửa 12/12; mở từng ảnh"],
    ["Claude Code", "BT3: sửa BUG-08 và 4 unit test", "`ticket_rules.require_text_fields`, `ticket_service._clean_fields`, `tests/test_crud_rules.py`", "TC-07 FAIL trước sửa, PASS sau sửa; TC-11 và integration CRUD vẫn tạo được phiếu hợp lệ; 104 passed"],
    ["Claude Code", "BT3: Test Report, Bug Log, TD-20…24, Deployment Guide, checklist bảo mật, API docs, Docker Compose 2 lệnh, CI, báo cáo này", "`docs/*.md`, `docker-compose.yml`, `Dockerfile.backend`, `.github/workflows/ci.yml`", "Đối chiếu từng số với lần chạy thật; CI lần #1 Success; Docker Compose: phép thử máy trắng 10/11/2026 – 2 lệnh, mã thoát 0, 3 dịch vụ healthy, init thoát 0, đăng nhập QL_TT01 được"],
  ], [1500, 2800, 2400, 2371], { size: 19 }),
  H2("D.1. Quyết định do em đưa ra khi rà soát kết quả AI"),
  bullet("Ảnh minh chứng chỉ là ảnh chụp thật (Playwright trên Swagger/giao diện thật); bỏ mọi ảnh vẽ bằng chương trình."),
  bullet("Săn bug mới bằng test case thay vì chỉ dùng lại bug cũ; không ghi bug nào chưa tái lập được (dự đoán TC-08 trả 500 đã chạy và không đúng)."),
  bullet("Chỉ nộp ba bug có commit `fix` riêng; bug cũ có commit gộp được ghi là lịch sử."),
  bullet("Đóng gói Docker Compose hai lệnh để người chấm không cần cài Python/PostgreSQL."),
  H2("D.2. Phần do em tự làm"),
  bullet("Chọn luồng nghiệp vụ L04, viết phiếu phạm vi và danh sách User Story sơ bộ (buổi 2)."),
  bullet("Cung cấp case study, tài liệu các buổi và bộ CSV cho công cụ; chỉnh bố cục sơ đồ trong draw.io."),
  bullet("Kiểm thử thủ công MT01–MT11 trong báo cáo Buổi 10; chụp ảnh Docker ở Phụ lục A.6."),
  new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: runs("[Em bổ sung các việc khác em đã thật sự làm.]", { highlight: "yellow" }) }),
  H2("D.3. Cam kết"),
  P("Em đã đọc, hiểu và chịu trách nhiệm về toàn bộ nội dung nộp, kể cả phần có AI hỗ trợ, và giải thích được từng hàm, từng test case khi được hỏi."),
  P("Sinh viên ký tên: ……………………………     Họ tên: Nguyễn Quốc Việt", { before: 300, align: AlignmentType.RIGHT }),
];

// ---------- Appendix B: BT2 feedback ----------
const appendixB = [
  H1("2. Phản hồi BT2 và quyết định xử lý"),
  linkLine("docs/thay-doi-thiet-ke.md"),
  P("Không có văn bản nhận xét riêng cho BT2; em đối chiếu sáu phản hồi thường gặp mà giảng viên nêu ở Buổi 14 với repo của em và ghi quyết định vào `docs/thay-doi-thiet-ke.md`."),
  table(["Mã", "Phản hồi", "Quyết định", "Dẫn chứng / ảnh hưởng"], [
    ["TD-20", "Chưa commit tệp khoá phiên bản", "GIỮ", "`requirements.txt`, `requirements-dev.txt` ghi phiên bản cố định; `package-lock.json` được Git theo dõi. Cài lại rồi chạy pytest: pass."],
    ["TD-21", "Có secret trong lịch sử commit", "GIỮ", "`.env` chưa từng được commit; quét lịch sử không có dòng mật khẩu/khoá thật; `.env.example` chỉ chứa giá trị mẫu."],
    ["TD-22", "Test quá ít, chỉ test luồng đúng", "SỬA", "Thêm 12 test case BT3 đủ năm loại; TC-07 phát hiện BUG-08, đã sửa ở `224fd69`."],
    ["TD-23", "Mâu thuẫn đặt lịch cho phiếu HOÀN TẤT (TD-10)", "GIỮ", "Mã theo SRS: không đặt lịch cho phiếu chưa có KTV hoặc đã kết thúc (400); có unit test."],
    ["TD-24", "README cần ~10 lệnh, chưa dựng được bằng ≤ 2 lệnh", "SỬA", "Docker Compose có dịch vụ `init`; hai lệnh `cp .env.example .env` và `docker compose up -d --build`."],
    ["–", "Service còn chứa req/res hoặc SQL", "Đã sửa ở BT2", "TD-18, BUG-06: service chỉ raise `DomainError`, SQL ở `repositories/`."],
  ], [900, 2700, 1200, 4271], { size: 20, firstColBold: true }),
];

// =====================================================================================
const footer = new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [
  new TextRun({ text: "BT3 · Nguyễn Quốc Việt · 2374802010556 · Trang ", font: FONT, size: 18, color: "666666" }),
  new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 18, color: "666666" }),
] })] });
const portrait = (children, extra = {}) => ({
  properties: { page: { size: PORTRAIT, margin: P_MARGIN }, ...extra }, footers: { default: footer }, children,
});

const headingStyle = (id, name, size, o = {}) => ({
  id, name, basedOn: "Normal", next: "Normal", quickFormat: true,
  run: { font: FONT, size, bold: true, color: o.color || "1F2A37", italics: o.italics },
  paragraph: { spacing: { before: o.before ?? 240, after: o.after ?? 120 }, keepNext: true, keepLines: true, outlineLevel: o.outline },
});

const doc = new Document({
  creator: "Nguyễn Quốc Việt", title: "BT3 – Smart CRM L04 – Nguyễn Quốc Việt – 2374802010556",
  features: { updateFields: true },
  styles: {
    default: { document: { run: { font: FONT, size: BODY } } },
    paragraphStyles: [
      headingStyle("Heading1", "Heading 1", 30, { before: 120, after: 160, outline: 0, color: "1F3A5F" }),
      headingStyle("Heading2", "Heading 2", 26, { before: 220, after: 100, outline: 1 }),
      headingStyle("Heading3", "Heading 3", 24, { before: 160, after: 80, outline: 2, italics: true }),
    ],
  },
  numbering: { config: [{ reference: "bullets", levels: [
    { level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 270 } } } },
    { level: 1, format: LevelFormat.BULLET, text: "–", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 1080, hanging: 270 } } } },
  ] }] },
  sections: [
    { properties: { page: { size: PORTRAIT, margin: P_MARGIN } }, children: cover },
    portrait([...toc, ...part1, pageBreak(), ...appendixB, ...testPlan]),
    { properties: { page: { size: { width: PORTRAIT.width, height: PORTRAIT.height, orientation: PageOrientation.LANDSCAPE }, margin: L_MARGIN } },
      footers: { default: footer }, children: testReport },
    portrait([...tcFigs, ...bugLog, ...bugFigs, ...part6, pageBreak(), ...part7,
      ...deploy, ...dockerFigs, ...security, ...api, ...appendixA]),
  ],
});

Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(OUT, buf); console.log("wrote", OUT, buf.length, "bytes, figures:", fig); });
