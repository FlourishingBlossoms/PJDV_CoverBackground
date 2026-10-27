// BgToggle.cpp v1.0 — 2D 静态背景开关菜单 (DivaModLoader DLL mod)
//
// 功能:
//   - F10 打开/关闭菜单（纯鼠标，与 JudgmentWindow 同风格）
//   - 一行开关: "2D 静态背景" —— 翻转 mods/DarkMV/config.toml 的 enabled
//     (DML 只在游戏启动时读 mod 列表 => 切换后重启游戏生效, 菜单上有提示)
//   - 不扫描内存、不写游戏内存 —— 零卡顿
//
// 设计说明: LightDim(曝光压暗)方案已按用户要求废弃停用。
#include <windows.h>
#include <windowsx.h>
#include <cstdio>
#include <cstring>

static HMODULE g_self = nullptr;

BOOL WINAPI DllMain(HINSTANCE inst, DWORD reason, LPVOID)
{
    if (reason == DLL_PROCESS_ATTACH) g_self = inst;
    return TRUE;
}

static void Log(const char* msg)
{
    char path[MAX_PATH];
    GetModuleFileNameA(g_self, path, MAX_PATH);
    char* s = strrchr(path, '\\'); if (s) *(s + 1) = 0;
    strcat_s(path, "bgtoggle.log");
    FILE* f = nullptr;
    if (fopen_s(&f, path, "a") != 0 || !f) return;
    SYSTEMTIME st; GetLocalTime(&st);
    fprintf(f, "[%02d:%02d:%02d] %s\n", st.wHour, st.wMinute, st.wSecond, msg);
    fclose(f);
}

// ---------- DarkMV 开关 ----------
static bool ReadDarkMvEnabled()
{
    char path[MAX_PATH];
    GetModuleFileNameA(g_self, path, MAX_PATH);
    char* s = strrchr(path, '\\');
    // .../mods/BgToggle/xxx.dll -> .../mods/DarkMV/config.toml
    *(s + 1) = 0;
    char root[MAX_PATH];
    strcpy_s(root, path);
    char* m = strstr(root, "mods\\"); if (!m) return true;
    *m = 0;
    sprintf_s(path, "%smods\\DarkMV\\config.toml", root);
    FILE* f = nullptr;
    if (fopen_s(&f, path, "rb") != 0 || !f) return true;
    char line[256];
    while (fgets(line, sizeof(line), f))
    {
        char* h = line; while (*h == ' ' || *h == '\t') h++;
        if (!_strnicmp(h, "enabled", 7)) { fclose(f); return strstr(h, "false") == nullptr; }
    }
    fclose(f);
    return true;
}

static void WriteDarkMvEnabled(bool on)
{
    char path[MAX_PATH];
    GetModuleFileNameA(g_self, path, MAX_PATH);
    char* s = strrchr(path, '\\'); *(s + 1) = 0;
    char root[MAX_PATH];
    strcpy_s(root, path);
    char* m = strstr(root, "mods\\"); if (!m) return;
    *m = 0;
    sprintf_s(path, "%smods\\DarkMV\\config.toml", root);
    FILE* f = nullptr;
    if (fopen_s(&f, path, "wb") != 0 || !f) return;
    fprintf(f, "enabled = %s\ninclude = [\".\"]\n\nname = \"Dark MV (video replacement)\"\nversion = \"1.1\"\nauthor = \"self\"\n\n# 每首歌自己 MV 的暗色静态帧; 关闭=恢复原版 MV (重启游戏生效)\n",
            on ? "true" : "false");
    fclose(f);
    Log(on ? "DarkMV -> ON (next launch)" : "DarkMV -> OFF (next launch)");
}

// ---------- 覆盖层菜单 ----------
static HWND g_hwnd = nullptr;
static HWND g_gameWnd = nullptr;
static bool g_menuOpen = false;
static bool g_dirty = true;
static bool g_hover = false;
static HFONT g_font = nullptr, g_fontBig = nullptr;
static const int X0 = 20, Y0 = 14, BARW = 400, BARH = 44, GAP = 10;

static bool EdgeKey(int vk)
{
    static bool prev[256] = {};
    bool now = (GetAsyncKeyState(vk) & 0x8000) != 0;
    bool edge = now && !prev[vk];
    prev[vk] = now;
    return edge;
}

static void PaintMenu(HDC mem, int w, int h)
{
    RECT rc = { 0, 0, w, h };
    HBRUSH bg = CreateSolidBrush(RGB(38, 44, 38));
    FillRect(mem, &rc, bg); DeleteObject(bg);
    SetBkMode(mem, TRANSPARENT);
    HBRUSH cyan = CreateSolidBrush(RGB(120, 210, 80));
    RECT title = { X0, Y0, X0 + BARW, Y0 + BARH };
    FillRect(mem, &title, cyan); DeleteObject(cyan);
    SetTextColor(mem, RGB(255, 255, 255));
    SelectObject(mem, g_fontBig);
    DrawTextW(mem, L"背景设置", -1, &title, DT_CENTER | DT_VCENTER | DT_SINGLELINE);

    bool on = ReadDarkMvEnabled();
    int y = Y0 + BARH + GAP;
    RECT row = { X0, y, X0 + BARW, y + BARH };
    HBRUSH r1 = CreateSolidBrush(g_hover ? RGB(120, 210, 80) : RGB(245, 245, 245));
    FillRect(mem, &row, r1); DeleteObject(r1);
    SetTextColor(mem, RGB(40, 40, 40));
    SelectObject(mem, g_font);
    wchar_t val[96];
    wsprintfW(val, on ? L"2D 静态背景：开" : L"2D 静态背景：关（原版 MV）");
    DrawTextW(mem, val, -1, &row, DT_CENTER | DT_VCENTER | DT_SINGLELINE);

    RECT hint = { X0, y + BARH + 6, X0 + BARW + 60, y + BARH + 30 };
    SetTextColor(mem, RGB(185, 200, 185));
    SelectObject(mem, g_font);
    DrawTextW(mem, L"点击切换   F10 关闭   切换后重启游戏生效", -1, &hint, DT_LEFT | DT_VCENTER | DT_SINGLELINE);
}

static LRESULT CALLBACK WndProc(HWND hwnd, UINT msg, WPARAM wp, LPARAM lp)
{
    switch (msg)
    {
    case WM_PAINT:
    {
        PAINTSTRUCT ps;
        HDC dc = BeginPaint(hwnd, &ps);
        PaintMenu(dc, ps.rcPaint.right, ps.rcPaint.bottom);
        EndPaint(hwnd, &ps);
        return 0;
    }
    case WM_MOUSEMOVE:
    {
        int y = GET_Y_LPARAM(lp);
        int top = Y0 + BARH + GAP;
        bool h = y >= top && y < top + BARH;
        if (h != g_hover) { g_hover = h; g_dirty = true; }
        return 0;
    }
    case WM_LBUTTONDOWN:
    {
        int y = GET_Y_LPARAM(lp);
        int top = Y0 + BARH + GAP;
        if (y >= top && y < top + BARH)
        {
            WriteDarkMvEnabled(!ReadDarkMvEnabled());
            Beep(880, 60);
            g_dirty = true;
        }
        return 0;
    }
    default: break;
    }
    return DefWindowProcW(hwnd, msg, wp, lp);
}

static void SafeLayout()
{
    __try
    {
        HWND game = g_gameWnd;
        if (!game || !IsWindow(game))
        {
            g_gameWnd = nullptr;
            EnumWindows([](HWND hwnd, LPARAM lp) -> BOOL {
                DWORD pid = 0;
                GetWindowThreadProcessId(hwnd, &pid);
                if (pid != GetCurrentProcessId()) return TRUE;
                if (!IsWindowVisible(hwnd)) return TRUE;
                if (!(GetWindowLongW(hwnd, GWL_STYLE) & WS_CAPTION)) return TRUE;
                *(HWND*)lp = hwnd;
                return FALSE;
            }, (LPARAM)&g_gameWnd);
            game = g_gameWnd;
            if (!game) return;
        }
        RECT rc; GetClientRect(game, &rc);
        POINT tl = { 0, 0 };
        ClientToScreen(game, &tl);
        int x = tl.x + (int)(rc.right * 0.06);
        int y = tl.y + (int)(rc.bottom * 0.55);
        SetWindowPos(g_hwnd, HWND_TOPMOST, x, y, 460, 220, SWP_NOACTIVATE | SWP_SHOWWINDOW);
        if (g_dirty)
        {
            InvalidateRect(g_hwnd, nullptr, TRUE);
            UpdateWindow(g_hwnd);
            g_dirty = false;
        }
    }
    __except (EXCEPTION_EXECUTE_HANDLER) {}
}

DWORD WINAPI MainThread(LPVOID)
{
    WNDCLASSEXW wc = { sizeof(wc) };
    wc.lpfnWndProc = WndProc;
    wc.hInstance = g_self;
    wc.lpszClassName = L"BgToggleOverlay";
    RegisterClassExW(&wc);
    g_hwnd = CreateWindowExW(
        WS_EX_LAYERED | WS_EX_TOPMOST | WS_EX_NOACTIVATE | WS_EX_TOOLWINDOW,
        L"BgToggleOverlay", L"", WS_POPUP,
        100, 100, 460, 220, nullptr, nullptr, g_self, nullptr);
    SetLayeredWindowAttributes(g_hwnd, 0, 240, LWA_ALPHA);
    g_font = CreateFontW(24, 0, 0, 0, FW_SEMIBOLD, FALSE, FALSE, FALSE, DEFAULT_CHARSET,
                         OUT_DEFAULT_PRECIS, CLIP_DEFAULT_PRECIS, CLEARTYPE_QUALITY,
                         VARIABLE_PITCH | FF_SWISS, L"Microsoft YaHei UI");
    g_fontBig = CreateFontW(27, 0, 0, 0, FW_BOLD, FALSE, FALSE, FALSE, DEFAULT_CHARSET,
                            OUT_DEFAULT_PRECIS, CLIP_DEFAULT_PRECIS, CLEARTYPE_QUALITY,
                            VARIABLE_PITCH | FF_SWISS, L"Microsoft YaHei UI");
    Log("BgToggle v1.0 running (F10=menu)");
    DWORD last_layout = 0;
    for (;;)
    {
        MSG msg;
        while (PeekMessageW(&msg, nullptr, 0, 0, PM_REMOVE))
        {
            TranslateMessage(&msg);
            DispatchMessageW(&msg);
        }
        if (EdgeKey(VK_F10))
        {
            g_menuOpen = !g_menuOpen;
            if (!g_menuOpen) ShowWindow(g_hwnd, SW_HIDE);
            else { g_dirty = true; Beep(620, 60); }
        }
        if (g_menuOpen)
        {
            DWORD now = GetTickCount();
            if (g_dirty || now - last_layout > 500)
            {
                last_layout = now;
                SafeLayout();
            }
        }
        Sleep(30);
    }
    return 0;
}

extern "C" __declspec(dllexport) void Init()
{
    Log("BgToggle v1.0 init");
    HANDLE h = CreateThread(nullptr, 0, MainThread, nullptr, 0, nullptr);
    if (h) CloseHandle(h);
}
