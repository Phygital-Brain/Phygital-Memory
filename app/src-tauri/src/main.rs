#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]
use std::{
    io::{Read, Write},
    net::TcpStream,
    path::PathBuf,
    sync::{atomic::{AtomicBool, Ordering}, Mutex},
    time::Duration,
};
use tauri::{Manager, RunEvent, WebviewUrl, WebviewWindowBuilder, WindowEvent};
use tauri::menu::{CheckMenuItemBuilder, Menu, MenuBuilder, MenuItemBuilder, PredefinedMenuItem, Submenu, SubmenuBuilder};
use tauri_plugin_shell::{process::{CommandChild, CommandEvent}, ShellExt};

struct Server(Mutex<Option<CommandChild>>);
// A secret only this app and the program it starts share, for the /shell/* calls (closing the window).
struct ShellToken(String);
// What the server must answer at /shell/hello: proves 8790 is really ours before the window goes there.
struct ServerProof(String);
static CLOSING: AtomicBool = AtomicBool::new(false);
static MAY_EXIT: AtomicBool = AtomicBool::new(false);
static SERVER_ENDED: AtomicBool = AtomicBool::new(false);   // the server stopped (it couldn't start, say)

fn folder() -> PathBuf {
    std::env::var("PHYGITAL_MEMORY_FOLDER").map(PathBuf::from).unwrap_or_else(|_| {
        // the home folder: HOME on Mac and Linux, USERPROFILE on Windows
        let home = std::env::var("HOME").or_else(|_| std::env::var("USERPROFILE")).unwrap_or_default();
        PathBuf::from(home).join("Phygital Memory")
    })
}

fn random_token() -> String {
    let mut buf = [0u8; 24];
    getrandom::fill(&mut buf).expect("no randomness");   // the system's own source, on every system
    buf.iter().map(|b| format!("{b:02x}")).collect()
}

fn start_server(app: &tauri::AppHandle) -> Result<(), String> {
    let token = app.state::<ShellToken>().0.clone();
    // The server is a folder in Resources (starts about twice as fast as one packed file, which unpacks itself
    // on every start). rclone, the cloud helper, sits in the same folder. The Mac app is one download for both
    // kinds of Mac: an Intel Mac runs the engine built for it, in server/intel.
    let name = if cfg!(windows) { "server/phygital-memory-server.exe" }
        else if cfg!(all(target_os = "macos", target_arch = "x86_64")) { "server/intel/phygital-memory-server" }
        else { "server/phygital-memory-server" };
    let exe = app.path().resource_dir().map_err(|e| e.to_string())?.join(name);
    let cmd = app.shell().command(exe)
        .env("PHYGITAL_MEMORY_FOLDER", folder()).env("PHYGITAL_MEMORY_PORT", "8790")
        .env("PHYGITAL_MEMORY_SHELL_TOKEN", token)
        .env("PHYGITAL_MEMORY_SERVER_PROOF", app.state::<ServerProof>().0.clone())
        .env("PHYGITAL_MEMORY_APP_PID", std::process::id().to_string());
    let (mut rx, child) = cmd.spawn().map_err(|e| e.to_string())?;
    tauri::async_runtime::spawn(async move {
        while let Some(ev) = rx.recv().await {
            if matches!(ev, CommandEvent::Terminated(_)) { SERVER_ENDED.store(true, Ordering::SeqCst); }
        }
    });
    *app.state::<Server>().0.lock().unwrap() = Some(child);
    for _ in 0..150 {
        if TcpStream::connect_timeout(&"127.0.0.1:8790".parse().unwrap(), Duration::from_millis(200)).is_ok() {
            // Something answers on 8790: it must be our own server, which alone knows the proof we gave it.
            // Another program sitting on the port could show a fake unlock page or catch AI keys.
            let proof = app.state::<ServerProof>().0.clone();
            if shell(app, "hello").map_or(false, |b| b.contains(&proof)) {
                return Ok(());
            }
            if SERVER_ENDED.load(Ordering::SeqCst) {
                return Err("Another program is using this app's port (8790). Quit it, then open Phygital Memory again.".into());
            }
        }
        if SERVER_ENDED.load(Ordering::SeqCst) {   // no point waiting: say so at once
            return Err("Its notes service stopped while starting.".into());
        }
        std::thread::sleep(Duration::from_millis(50));
    }
    Err("Its notes service didn't answer.".into())
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

// The menu bar. The page describes it in the app's language and as things stand (see menuSpec in main.js); the
// server keeps the latest one, and this asks for a newer one every moment and draws it. A click on one of our items
// goes back to the page as window.phygitalMenu(id); cut, copy, paste, hide, quit and the like are the Mac's own.
fn watch_menu(app: tauri::AppHandle) {
    std::thread::spawn(move || {
        let mut have = 0i64;
        loop {
            std::thread::sleep(Duration::from_millis(600));
            let Some(reply) = shell_with(&app, "menu", &format!("{{\"v\":{have}}}")) else { continue };
            let Ok(v) = serde_json::from_str::<serde_json::Value>(&reply) else { continue };
            let Some(spec) = v.get("spec").cloned() else { continue };
            have = v["v"].as_i64().unwrap_or(have);
            let h = app.clone();
            let _ = app.run_on_main_thread(move || {
                if let Ok(menu) = build_menu(&h, &spec) { let _ = h.set_menu(menu); }
            });
        }
    });
}

fn build_menu(app: &tauri::AppHandle, spec: &serde_json::Value) -> tauri::Result<Menu<tauri::Wry>> {
    let mut mb = MenuBuilder::new(app);
    for sub in spec.as_array().into_iter().flatten() {
        let label = sub["title"].as_str().or(sub["label"].as_str()).unwrap_or("");
        mb = mb.item(&submenu(app, label, sub)?);
    }
    mb.build()
}

fn submenu(app: &tauri::AppHandle, title: &str, v: &serde_json::Value) -> tauri::Result<Submenu<tauri::Wry>> {
    let mut sb = SubmenuBuilder::new(app, title);
    for it in v["items"].as_array().into_iter().flatten() {
        let label = it["label"].as_str().unwrap_or("");
        if it["sep"].as_bool() == Some(true) {
            sb = sb.separator();
        } else if it["items"].is_array() {
            sb = sb.item(&submenu(app, label, it)?);
        } else if let Some(n) = it["native"].as_str() {
            let t = Some(label);
            let p = match n {
                "undo" => PredefinedMenuItem::undo(app, t)?, "redo" => PredefinedMenuItem::redo(app, t)?,
                "cut" => PredefinedMenuItem::cut(app, t)?, "copy" => PredefinedMenuItem::copy(app, t)?,
                "paste" => PredefinedMenuItem::paste(app, t)?, "selectall" => PredefinedMenuItem::select_all(app, t)?,
                "hide" => PredefinedMenuItem::hide(app, t)?, "hideothers" => PredefinedMenuItem::hide_others(app, t)?,
                "showall" => PredefinedMenuItem::show_all(app, t)?, "quit" => PredefinedMenuItem::quit(app, t)?,
                "minimize" => PredefinedMenuItem::minimize(app, t)?, "zoom" => PredefinedMenuItem::maximize(app, t)?,
                "fullscreen" => PredefinedMenuItem::fullscreen(app, t)?,
                _ => continue,
            };
            sb = sb.item(&p);
        } else {
            let id = format!("pm:{}", it["id"].as_str().unwrap_or(""));
            let enabled = it["enabled"].as_bool().unwrap_or(true);
            // a shortcut the Mac can't read leaves the item without one, never the whole menu broken
            let key = it["key"].as_str();
            if let Some(on) = it["check"].as_bool() {
                let make = |k: Option<&str>| {
                    let b = CheckMenuItemBuilder::with_id(id.clone(), label).checked(on).enabled(enabled);
                    match k { Some(k) => b.accelerator(k).build(app), None => b.build(app) }
                };
                sb = sb.item(&make(key).or_else(|_| make(None))?);
            } else {
                let make = |k: Option<&str>| {
                    let b = MenuItemBuilder::with_id(id.clone(), label).enabled(enabled);
                    match k { Some(k) => b.accelerator(k).build(app), None => b.build(app) }
                };
                sb = sb.item(&make(key).or_else(|_| make(None))?);
            }
        }
    }
    sb.build()
}

// Updates come from the latest GitHub Release, signed with the app's own update key (its public half is in
// tauri.conf.json, so nothing else can pass for an update). An update only goes in while the app is opening or
// closing, never while it's in use:
// - Found while the app opens (within OPENING): the opening screen stays up as the update screen (updateScreen in
//   main.js, which follows the download through the engine); then every memory locks, it goes in place, the app
//   restarts.
// - Found later (a slow check, or the look every few hours while the app stays open): it downloads quietly and goes
//   in place when the app quits (see quit).
// If anything fails, nothing changes and it tries again later. Builds made while working on the app (debug) never update.
const OPENING: Duration = Duration::from_secs(4);
const LOOK_EVERY: Duration = Duration::from_secs(6 * 3600);
static READY: Mutex<Option<(tauri_plugin_updater::Update, Vec<u8>)>> = Mutex::new(None);   // downloaded, for quit

fn check_update(app: tauri::AppHandle) {
    if cfg!(debug_assertions) { return; }
    let opened = std::time::Instant::now();
    std::thread::spawn(move || loop {
        if READY.lock().unwrap().is_none() {
            tauri::async_runtime::block_on(update_once(&app, opened.elapsed() < OPENING));
        }
        std::thread::sleep(LOOK_EVERY);
    });
}

async fn update_once(app: &tauri::AppHandle, opening: bool) {
    use tauri_plugin_updater::UpdaterExt;
    let Ok(updater) = app.updater() else { return };
    let Ok(Some(update)) = updater.check().await else { return };
    let v: String = update.version.chars().filter(|c| c.is_ascii_alphanumeric() || ".-+".contains(*c)).collect();
    let tell = |pct: u64, state: &str| if opening {
        let _ = shell_with(app, "update", &format!("{{\"v\":\"{v}\",\"pct\":{pct},\"state\":\"{state}\"}}"));
    };
    if opening {
        tell(0, "");
        if let Some(w) = app.get_webview_window("main") {
            let _ = w.eval(&format!("window.phygitalUpdating && window.phygitalUpdating('{v}')"));
        }
    }
    let (mut got, mut said) = (0u64, 0u64);
    let bytes = update.download(|chunk, total| {
        got += chunk as u64;
        let pct = total.filter(|t| *t > 0).map(|t| (got * 100 / t).min(99)).unwrap_or(0);
        if pct != said { said = pct; tell(pct, ""); }
    }, || {}).await;
    let Ok(bytes) = bytes else { return tell(0, "failed") };
    if !opening {
        *READY.lock().unwrap() = Some((update, bytes));
        return;
    }
    tell(100, "restarting");
    let _ = shell(app, "lockall");
    if update.install(bytes).is_err() { return tell(0, "failed"); }
    MAY_EXIT.store(true, Ordering::SeqCst);
    app.restart();
}

// Check for updates, from the menu: one found installs now, like one found while opening (every memory locks, the
// app restarts). Otherwise the page says the app is up to date, or that the check failed.
async fn check_now(app: &tauri::AppHandle) {
    use tauri_plugin_updater::UpdaterExt;
    let say = |what: &str| if let Some(w) = app.get_webview_window("main") {
        let _ = w.eval(&format!("window.phygitalUpdateSays && window.phygitalUpdateSays('{what}')"));
    };
    if cfg!(debug_assertions) { return say("none"); }
    if READY.lock().unwrap().is_some() { return say("ready"); }
    let Ok(updater) = app.updater() else { return say("failed") };
    match updater.check().await {
        Ok(Some(_)) => update_once(app, true).await,
        Ok(None) => say("none"),
        Err(_) => say("failed"),
    }
}

fn quit(app: &tauri::AppHandle) {
    let _ = shell(app, "lockall");   // lock every folder and close every Finder view before we go
    if let Some((update, bytes)) = READY.lock().unwrap().take() {
        let _ = update.install(bytes);   // downloaded while the app was open: in place for the next time it opens
    }
    MAY_EXIT.store(true, Ordering::SeqCst);
    app.exit(0);
}

// The window is closing (or Cmd+Q). If a folder is open, the window hides and the small question window shows at
// once (it was made, hidden, at start): lock all, or keep open. No answer in 30 seconds locks everything. Keeping it
// leaves the app in the Dock; the server remembers that answer for 72 hours, and closing then skips the question.
// Quit (Cmd+Q, or Quit in the Dock) always asks, even while "Keep open" is remembered; there Keep open cancels the quit.
fn handle_close(app: tauri::AppHandle, quitting: bool) {
    if CLOSING.swap(true, Ordering::SeqCst) { return; }
    let reply = shell_with(&app, "close", if quitting { "{\"quit\":true}" } else { "{}" }).unwrap_or_default().replace(' ', "");
    if !reply.contains("\"keep\":true") && !reply.contains("\"ask\":true") { return quit(&app); }
    if let Some(w) = app.get_webview_window("main") {
        let _ = w.eval("window.phygitalSaveAll && window.phygitalSaveAll()");   // nothing just typed is lost
        let _ = w.hide();
    }
    let ask = if reply.contains("\"ask\":true") { app.get_webview_window("closeask") } else { None };
    if let Some(q) = &ask {
        let _ = q.eval(if quitting { "window.startAsk && window.startAsk('quit')" } else { "window.startAsk && window.startAsk()" });
        let _ = q.center();
        let _ = q.show();
        let _ = q.set_focus();
    }
    std::thread::spawn(move || {
        let mut keep = reply.contains("\"keep\":true");
        if let Some(q) = ask {
            let mut answered = false;
            for _ in 0..350 {   // the window locks by itself after 30 s with no answer; 35 s here is the backstop
                std::thread::sleep(Duration::from_millis(100));
                let a = shell(&app, "answer").unwrap_or_default().replace(' ', "");
                if a.contains("\"keep\":1") { keep = true; answered = true; break; }
                if a.contains("\"keep\":0") { answered = true; break; }
            }
            let _ = q.hide();
            if !answered { let _ = shell_with(&app, "decide", "{\"keep\":false}"); }
        }
        if !keep {
            std::thread::sleep(Duration::from_millis(500));   // let the last save land before everything locks
            return quit(&app);
        }
        CLOSING.store(false, Ordering::SeqCst);
        loop {
            std::thread::sleep(Duration::from_secs(5));
            if shell(&app, "should-exit").unwrap_or_default().replace(' ', "").contains("\"exit\":true") {
                return quit(&app);
            }
        }
    });
}

// The closing question's small window, made hidden at start so it can show the moment the main window closes.
fn ask_window(app: &tauri::AppHandle) {
    let b = WebviewWindowBuilder::new(app, "closeask", WebviewUrl::External("http://127.0.0.1:8790/closeask".parse().unwrap()))
        .title("Phygital Memory").inner_size(440.0, 230.0).resizable(false).minimizable(false).maximizable(false)
        .closable(false).always_on_top(true).visible(false).center();
    #[cfg(target_os = "macos")]
    let b = b.title_bar_style(tauri::TitleBarStyle::Overlay).hidden_title(true);
    let _ = b
        .on_navigation(|url| own_page(url))
        .initialization_script(&page_secret(app))
        .build();
}

// The page's own secret for /api: only our windows get it, so another program on this Mac can't drive the app.
fn page_secret(app: &tauri::AppHandle) -> String {
    format!("window.__PM_SHELL = {:?};", app.state::<ShellToken>().0)
}

// The window may only ever show our own local page. A note, a link or injected HTML that tries to send it
// anywhere else (a look-alike password page, say) is refused. Same class of bug as the "C1" finding
// reported to Baalda.
fn own_page(url: &tauri::Url) -> bool {
    url.scheme() == "http" && url.host_str() == Some("127.0.0.1") && url.port() == Some(8790)
}
// ...or the app's own "Starting" page, built into the app, shown until the server is up.
fn starting_page(url: &tauri::Url) -> bool {
    url.scheme() == "tauri" && url.host_str() == Some("localhost") && url.path() == "/starting.html"
}

fn main_window(app: &tauri::AppHandle) -> Result<(), String> {
    let b = WebviewWindowBuilder::new(app, "main", WebviewUrl::App("starting.html".into()))
        .title("Phygital Memory").inner_size(1200.0, 800.0).min_inner_size(720.0, 480.0).center();
    // Mac: no title bar, the page fills the window and the close/minimise buttons float over the sidebar (as Baalda).
    // Windows and Linux keep their own title bar.
    #[cfg(target_os = "macos")]
    let b = b.title_bar_style(tauri::TitleBarStyle::Overlay).hidden_title(true)
        .traffic_light_position(tauri::LogicalPosition::new(16.0, 22.0));
    let win = b
        .on_navigation(|url| own_page(url) || starting_page(url))
        .disable_drag_drop_handler()   // files dragged in from Finder reach the page (it adds them, encrypted)
        .initialization_script(&page_secret(app))
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
    // Placed from the new size directly: center() would still use the old 1200x800 and open off to the side.
    let (left, top) = (screen.work_area().position.x as f64 / scale, screen.work_area().position.y as f64 / scale);
    let _ = win.set_size(tauri::LogicalSize::new(w, h));
    let _ = win.set_position(tauri::LogicalPosition::new(left + (free_w - w) / 2.0, top + (free_h - h) / 2.0));
}

fn main() {
    let app = tauri::Builder::default()
        // Only ever one copy: opening the app again just brings back the window of the one already running.
        .plugin(tauri_plugin_single_instance::init(|app, _args, _cwd| {
            if let Some(w) = app.get_webview_window("main") { let _ = w.show(); let _ = w.unminimize(); let _ = w.set_focus(); }
            let h = app.clone();
            std::thread::spawn(move || { let _ = shell(&h, "reopen"); });
        }))
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_updater::Builder::new().build())
        .on_menu_event(|app, ev| {
            let Some(id) = ev.id().0.strip_prefix("pm:") else { return };
            // only plain ids reach the page (they're ours, but nothing odd ever goes into the script)
            let id: String = id.chars().filter(|c| c.is_ascii_alphanumeric() || "-_:.".contains(*c)).collect();
            if id == "checkupdate" {   // the app window does the looking; the page only says what came of it
                let h = app.clone();
                std::thread::spawn(move || tauri::async_runtime::block_on(check_now(&h)));
                return;
            }
            if let Some(w) = app.get_webview_window("main") {
                let _ = w.show();
                let _ = w.eval(&format!("window.phygitalMenu && window.phygitalMenu('{id}')"));
            }
        })
        .manage(Server(Mutex::new(None)))
        .manage(ShellToken(random_token()))
        .manage(ServerProof(random_token()))
        .on_window_event(|window, event| {
            if let WindowEvent::CloseRequested { api, .. } = event {
                if window.label() == "main" && !MAY_EXIT.load(Ordering::SeqCst) {
                    api.prevent_close();
                    handle_close(window.app_handle().clone(), false);
                }
            }
        })
        .setup(|app| {
            // The window opens at once with "Starting", and goes to the real page as soon as the server answers.
            // No first-run window any more: the page itself offers to create or open a locked folder.
            let _ = main_window(app.handle());
            let h = app.handle().clone();
            std::thread::spawn(move || {
                if let Err(e) = start_server(&h) {
                    let msg = format!("Phygital Memory couldn't start. {e} Quit and open it again.").replace('\'', "’");
                    let h2 = h.clone();
                    let _ = h.run_on_main_thread(move || {
                        if let Some(w) = h2.get_webview_window("main") {
                            let _ = w.eval(&format!("document.querySelector('p').textContent = '{msg}'"));
                        }
                    });
                } else {
                    let h2 = h.clone();
                    let _ = h.run_on_main_thread(move || {
                        if let Some(w) = h2.get_webview_window("main") {
                            let _ = w.navigate("http://127.0.0.1:8790/".parse().unwrap());
                        }
                        ask_window(&h2);
                    });
                    watch_menu(h.clone());
                    check_update(h.clone());
                }
            });
            Ok(())
        })
        .build(tauri::generate_context!())
        .expect("build failed");
    app.run(|h, e| match e {
        RunEvent::ExitRequested { api, .. } if !MAY_EXIT.load(Ordering::SeqCst) => {
            api.prevent_exit();
            handle_close(h.clone(), true);
        }
        #[cfg(target_os = "macos")]
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
