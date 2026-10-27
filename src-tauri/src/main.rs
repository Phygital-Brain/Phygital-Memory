#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]
use std::{
    io::{Read, Write},
    net::TcpStream,
    path::PathBuf,
    sync::{atomic::{AtomicBool, Ordering}, Mutex},
    time::Duration,
};
use tauri::{Manager, RunEvent, WebviewUrl, WebviewWindowBuilder, WindowEvent};
use tauri_plugin_shell::{process::CommandChild, ShellExt};

struct Server(Mutex<Option<CommandChild>>);
// A secret only this app and the program it starts share, for the /shell/* calls (closing the window).
struct ShellToken(String);
static CLOSING: AtomicBool = AtomicBool::new(false);
static MAY_EXIT: AtomicBool = AtomicBool::new(false);

fn folder() -> PathBuf {
    std::env::var("PHYGITAL_MEMORY_FOLDER").map(PathBuf::from).unwrap_or_else(|_| {
        PathBuf::from(std::env::var("HOME").unwrap_or_default()).join("Phygital Memory")
    })
}

fn random_token() -> String {
    let mut buf = [0u8; 24];
    std::fs::File::open("/dev/urandom").and_then(|mut f| f.read_exact(&mut buf)).expect("no randomness");
    buf.iter().map(|b| format!("{b:02x}")).collect()
}

fn start_server(app: &tauri::AppHandle) -> Result<(), String> {
    let token = app.state::<ShellToken>().0.clone();
    let cmd = app.shell().sidecar("phygital-memory-server").map_err(|e| e.to_string())?
        .env("PHYGITAL_MEMORY_FOLDER", folder()).env("PHYGITAL_MEMORY_PORT", "8790")
        .env("PHYGITAL_MEMORY_SHELL_TOKEN", token)
        .env("PHYGITAL_MEMORY_APP_PID", std::process::id().to_string());
    let (mut rx, child) = cmd.spawn().map_err(|e| e.to_string())?;
    tauri::async_runtime::spawn(async move { while rx.recv().await.is_some() {} });
    *app.state::<Server>().0.lock().unwrap() = Some(child);
    for _ in 0..150 {
        if TcpStream::connect_timeout(&"127.0.0.1:8790".parse().unwrap(), Duration::from_millis(200)).is_ok() {
            std::thread::sleep(Duration::from_millis(200));
            return Ok(());
        }
        std::thread::sleep(Duration::from_millis(200));
    }
    Err("The server did not start.".into())
}

// One small local request to our own program: POST /shell/<action>, returns the reply body.
fn shell(app: &tauri::AppHandle, action: &str) -> Option<String> {
    shell_with(app, action, "")
}

fn shell_with(app: &tauri::AppHandle, action: &str, body: &str) -> Option<String> {
    let token = app.state::<ShellToken>().0.clone();
    let mut s = TcpStream::connect_timeout(&"127.0.0.1:8790".parse().unwrap(), Duration::from_secs(2)).ok()?;
    s.set_read_timeout(Some(Duration::from_secs(10))).ok()?;
    let req = format!("POST /shell/{action} HTTP/1.1\r\nHost: 127.0.0.1:8790\r\nX-Shell-Token: {token}\r\n\
                       Content-Type: application/json\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{body}",
                      body.len());
    s.write_all(req.as_bytes()).ok()?;
    let mut out = String::new();
    s.read_to_string(&mut out).ok()?;
    out.split_once("\r\n\r\n").map(|(_, body)| body.to_string())
}

// The opener file inside a locked folder was double-clicked (or dropped on the Dock icon). Wait for our server,
// let it add that folder to the list, then show the window on it.
fn open_folder_file(app: tauri::AppHandle, path: PathBuf) {
    std::thread::spawn(move || {
        let p = path.to_string_lossy().replace('\\', "\\\\").replace('"', "\\\"");
        let p: String = p.chars().filter(|c| !c.is_control()).collect();
        let mut reply = None;
        for _ in 0..150 {   // the server may still be starting (the app was opened by this double-click)
            reply = shell_with(&app, "openfolder", &format!("{{\"path\":\"{p}\"}}"));
            if reply.is_some() { break; }
            std::thread::sleep(Duration::from_millis(200));
        }
        let reply = reply.unwrap_or_default().replace(' ', "");
        let Some(i) = reply.find("\"id\":\"") else { return };
        let id: String = reply[i + 6..].chars().take_while(|c| c.is_ascii_hexdigit()).collect();
        if id.is_empty() { return; }
        for _ in 0..150 {   // the window appears once the server is up
            if let Some(w) = app.get_webview_window("main") {
                let _ = w.show();
                let _ = w.set_focus();
                let _ = w.eval(&format!("window.phygitalOpenFolder && window.phygitalOpenFolder('{id}')"));
                return;
            }
            std::thread::sleep(Duration::from_millis(200));
        }
    });
}

fn quit(app: &tauri::AppHandle) {
    let _ = shell(app, "lockall");   // lock every folder and close every Finder view before we go
    MAY_EXIT.store(true, Ordering::SeqCst);
    app.exit(0);
}

// The window is closing (or Cmd+Q). If a folder is open, the page asks: lock all, or keep open. Keeping it hides
// the window and the app stays in the Dock; the server remembers that answer for 72 hours.
fn handle_close(app: tauri::AppHandle) {
    if CLOSING.swap(true, Ordering::SeqCst) { return; }
    std::thread::spawn(move || {
        let reply = shell(&app, "close").unwrap_or_default().replace(' ', "");
        let mut keep: Option<u64> = None;
        if reply.contains("\"keep\":true") {
            keep = Some(1);   // "Keep open" was chosen in the last 72 hours: no question
        } else if !reply.contains("\"ask\":true") {
            return quit(&app);
        } else {
            if let Some(w) = app.get_webview_window("main") { let _ = w.show(); let _ = w.set_focus(); }
            for _ in 0..150 {   // the page locks by itself after 30 s with no answer; 45 s here is the backstop
                std::thread::sleep(Duration::from_millis(300));
                let a = shell(&app, "answer").unwrap_or_default().replace(' ', "");
                if let Some(i) = a.find("\"keep\":") {
                    keep = a[i + 7..].chars().take_while(|c| c.is_ascii_digit()).collect::<String>().parse().ok();
                    break;
                }
            }
        }
        match keep {
            Some(n) if n > 0 => {
                if let Some(w) = app.get_webview_window("main") { let _ = w.hide(); }
                CLOSING.store(false, Ordering::SeqCst);
                loop {
                    std::thread::sleep(Duration::from_secs(5));
                    if shell(&app, "should-exit").unwrap_or_default().replace(' ', "").contains("\"exit\":true") {
                        return quit(&app);
                    }
                }
            }
            _ => quit(&app),   // "close and lock now", or no answer
        }
    });
}

// The window may only ever show our own local page. A note, a link or injected HTML that tries to send it
// anywhere else (a look-alike password page, say) is refused. Same class of bug as the "C1" finding
// reported to Baalda.
fn own_page(url: &tauri::Url) -> bool {
    url.scheme() == "http" && url.host_str() == Some("127.0.0.1") && url.port() == Some(8790)
}

fn main_window(app: &tauri::AppHandle) -> Result<(), String> {
    let win = WebviewWindowBuilder::new(app, "main", WebviewUrl::External("http://127.0.0.1:8790/".parse().unwrap()))
        .title("Phygital Memory").inner_size(1200.0, 800.0).min_inner_size(720.0, 480.0).center()
        // No title bar: the page fills the window and the close/minimise buttons float over the sidebar (as Baalda)
        .title_bar_style(tauri::TitleBarStyle::Overlay).hidden_title(true)
        .traffic_light_position(tauri::LogicalPosition::new(16.0, 22.0))
        .on_navigation(|url| own_page(url))
        .build().map_err(|e| e.to_string())?;
    fit_to_screen(&win);
    Ok(())
}

// Open big on any screen, like Baalda: 80% of the usable width and 88% of the height, centred. Never below
// 1200x800 (unless the screen is smaller) and never above 2000x1400, so a big monitor doesn't get a huge window.
fn fit_to_screen(win: &tauri::WebviewWindow) {
    let Some(screen) = win.current_monitor().ok().flatten().or_else(|| win.primary_monitor().ok().flatten()) else { return };
    let scale = screen.scale_factor();
    if scale <= 0.0 { return; }
    let (free_w, free_h) = (screen.work_area().size.width as f64 / scale, screen.work_area().size.height as f64 / scale);
    let fit = |free: f64, share: f64, least: f64, most: f64| (free * share).max(least.min(free)).min(most);
    let (w, h) = (fit(free_w, 0.80, 1200.0, 2000.0), fit(free_h, 0.88, 800.0, 1400.0));
    if win.set_size(tauri::LogicalSize::new(w, h)).is_ok() {
        let _ = win.center();
    }
}

fn main() {
    let app = tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .manage(Server(Mutex::new(None)))
        .manage(ShellToken(random_token()))
        .on_window_event(|window, event| {
            if let WindowEvent::CloseRequested { api, .. } = event {
                if window.label() == "main" && !MAY_EXIT.load(Ordering::SeqCst) {
                    api.prevent_close();
                    handle_close(window.app_handle().clone());
                }
            }
        })
        .setup(|app| {
            // No first-run window any more: the page itself offers to create or open a locked folder.
            let h = app.handle().clone();
            std::thread::spawn(move || {
                if start_server(&h).is_ok() {
                    let h2 = h.clone();
                    let _ = h.run_on_main_thread(move || { let _ = main_window(&h2); });
                }
            });
            Ok(())
        })
        .build(tauri::generate_context!())
        .expect("build failed");
    app.run(|h, e| match e {
        RunEvent::ExitRequested { api, .. } if !MAY_EXIT.load(Ordering::SeqCst) => {
            api.prevent_exit();
            handle_close(h.clone());
        }
        RunEvent::Reopen { .. } => {   // clicking the Dock icon brings the hidden window back and cancels the timer
            if let Some(w) = h.get_webview_window("main") { let _ = w.show(); let _ = w.set_focus(); }
            let h2 = h.clone();
            std::thread::spawn(move || { let _ = shell(&h2, "reopen"); });
        }
        #[cfg(target_os = "macos")]
        RunEvent::Opened { urls } => {
            for url in urls {
                if let Ok(path) = url.to_file_path() {
                    if path.extension().map_or(false, |e| e == "phygitalmemory") {
                        open_folder_file(h.clone(), path);
                    }
                }
            }
        }
        RunEvent::Exit => {
            if let Some(c) = h.state::<Server>().0.lock().unwrap().take() { let _ = c.kill(); }
        }
        _ => {}
    });
}
