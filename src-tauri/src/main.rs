#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]
use std::{net::TcpStream, path::PathBuf, sync::Mutex, time::Duration};
use tauri::{Manager, WebviewUrl, WebviewWindowBuilder};
use tauri_plugin_shell::{process::CommandChild, ShellExt};

struct Server(Mutex<Option<CommandChild>>);

fn folder() -> PathBuf {
    std::env::var("PHYGITAL_MEMORY_FOLDER").map(PathBuf::from).unwrap_or_else(|_| {
        PathBuf::from(std::env::var("HOME").unwrap_or_default()).join("Phygital Memory")
    })
}

fn start_server(app: &tauri::AppHandle) -> Result<(), String> {
    let cmd = app.shell().sidecar("phygital-memory-server").map_err(|e| e.to_string())?
        .env("PHYGITAL_MEMORY_FOLDER", folder()).env("PHYGITAL_MEMORY_PORT", "8790");
    let (mut rx, child) = cmd.spawn().map_err(|e| e.to_string())?;
    tauri::async_runtime::spawn(async move { while rx.recv().await.is_some() {} });
    *app.state::<Server>().0.lock().unwrap() = Some(child);
    for _ in 0..100 {
        if TcpStream::connect_timeout(&"127.0.0.1:8790".parse().unwrap(), Duration::from_millis(200)).is_ok() {
            std::thread::sleep(Duration::from_millis(200));
            return Ok(());
        }
        std::thread::sleep(Duration::from_millis(200));
    }
    Err("The server did not start.".into())
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

#[tauri::command]
async fn create_vault(app: tauri::AppHandle, password: String) -> Result<(), String> {
    use tauri_plugin_shell::process::CommandEvent;
    let (mut rx, mut child) = app.shell().sidecar("phygital-memory-server").map_err(|e| e.to_string())?
        .args(["create"]).env("PHYGITAL_MEMORY_FOLDER", folder()).spawn().map_err(|e| e.to_string())?;
    child.write(format!("{password}\n{password}\n").as_bytes()).map_err(|e| e.to_string())?;
    let mut ok = false;
    while let Some(ev) = rx.recv().await {
        if let CommandEvent::Terminated(p) = ev { ok = p.code == Some(0); break; }
    }
    if !ok { return Err("Could not create the folder.".into()); }
    start_server(&app)?;
    if let Some(w) = app.get_webview_window("setup") { let _ = w.close(); }
    main_window(&app)
}

fn main() {
    let app = tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .manage(Server(Mutex::new(None)))
        .invoke_handler(tauri::generate_handler![create_vault])
        .setup(|app| {
            let h = app.handle().clone();
            if folder().join("masterkey.cryptomator").exists() {
                std::thread::spawn(move || {
                    let h2 = h.clone();
                    if start_server(&h2).is_ok() { let h3 = h2.clone(); let _ = h2.run_on_main_thread(move || { let _ = main_window(&h3); }); }
                });
            } else {
                WebviewWindowBuilder::new(app, "setup", WebviewUrl::App("index.html".into()))
                    .title("Phygital Memory").inner_size(480.0, 420.0)
                    .on_navigation(|url| url.scheme() == "tauri" || url.host_str() == Some("tauri.localhost"))
                    .build()?;
            }
            Ok(())
        })
        .build(tauri::generate_context!())
        .expect("build failed");
    app.run(|h, e| {
        if let tauri::RunEvent::Exit = e {
            if let Some(c) = h.state::<Server>().0.lock().unwrap().take() { let _ = c.kill(); }
        }
    });
}
