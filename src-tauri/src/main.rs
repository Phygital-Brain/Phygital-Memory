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
    let token = app.state::<ShellToken>().0.clone();
    let mut s = TcpStream::connect_timeout(&"127.0.0.1:8790".parse().unwrap(), Duration::from_secs(2)).ok()?;
    s.set_read_timeout(Some(Duration::from_secs(10))).ok()?;
    let req = format!("POST /shell/{action} HTTP/1.1\r\nHost: 127.0.0.1:8790\r\nX-Shell-Token: {token}\r\n\
                       Content-Length: 0\r\nConnection: close\r\n\r\n");
    s.write_all(req.as_bytes()).ok()?;
    let mut out = String::new();
    s.read_to_string(&mut out).ok()?;
    out.split_once("\r\n\r\n").map(|(_, body)| body.to_string())
}

fn quit(app: &tauri::AppHandle) {
    let _ = shell(app, "lockall");   // lock every folder and close every Finder view before we go
    MAY_EXIT.store(true, Ordering::SeqCst);
    app.exit(0);
}

// The window is closing (or Cmd+Q). If a folder is open in Finder, the page asks how long to keep it open;
// keeping it hides the window, and the app quits by itself once the server has locked everything.
fn handle_close(app: tauri::AppHandle) {
    if CLOSING.swap(true, Ordering::SeqCst) { return; }
    std::thread::spawn(move || {
        let reply = shell(&app, "close").unwrap_or_default();
        if !reply.replace(' ', "").contains("\"ask\":true") { return quit(&app); }
        if let Some(w) = app.get_webview_window("main") { let _ = w.show(); let _ = w.set_focus(); }
        let mut keep: Option<u64> = None;
        for _ in 0..600 {   // up to 3 minutes for an answer
            std::thread::sleep(Duration::from_millis(300));
            let a = shell(&app, "answer").unwrap_or_default().replace(' ', "");
            if let Some(i) = a.find("\"keep\":") {
                keep = a[i + 7..].chars().take_while(|c| c.is_ascii_digit()).collect::<String>().parse().ok();
                break;
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
    WebviewWindowBuilder::new(app, "main", WebviewUrl::External("http://127.0.0.1:8790/".parse().unwrap()))
        .title("Phygital Memory").inner_size(1200.0, 800.0).min_inner_size(720.0, 480.0)
        .on_navigation(|url| own_page(url))
        .build().map_err(|e| e.to_string())?;
    Ok(())
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
        RunEvent::Exit => {
            if let Some(c) = h.state::<Server>().0.lock().unwrap().take() { let _ = c.kill(); }
        }
        _ => {}
    });
}
