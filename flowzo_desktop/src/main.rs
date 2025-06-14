// SPDX-License-Identifier: AGPL-3.0-only
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use serde::{Deserialize, Serialize};
use std::sync::{Arc, Mutex};
use tauri::{Manager, State};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SessionState {
    pub session_id: String,
    pub state: String,
    pub elapsed_seconds: f64,
    pub remaining_seconds: f64,
    pub total_duration: i32,
    pub task: Option<String>,
}

impl Default for SessionState {
    fn default() -> Self {
        Self {
            session_id: "idle".to_string(),
            state: "idle".to_string(),
            elapsed_seconds: 0.0,
            remaining_seconds: 0.0,
            total_duration: 0,
            task: None,
        }
    }
}

type SharedSessionState = Arc<Mutex<SessionState>>;

#[tauri::command]
async fn get_session_state(state: State<'_, SharedSessionState>) -> Result<SessionState, String> {
    let session_state = state.lock().map_err(|e| e.to_string())?;
    Ok(session_state.clone())
}

#[tauri::command]
async fn abort_session(
    state: State<'_, SharedSessionState>,
    app_handle: tauri::AppHandle,
) -> Result<bool, String> {
    {
        let mut session_state = state.lock().map_err(|e| e.to_string())?;
        session_state.state = "aborted".to_string();
        session_state.remaining_seconds = 0.0;
    }
    
    // Emit event to frontend
    app_handle
        .emit_all("session_aborted", ())
        .map_err(|e| e.to_string())?;
    
    Ok(true)
}

#[tauri::command]
async fn update_session_state(
    new_state: SessionState,
    state: State<'_, SharedSessionState>,
    app_handle: tauri::AppHandle,
) -> Result<(), String> {
    {
        let mut session_state = state.lock().map_err(|e| e.to_string())?;
        *session_state = new_state.clone();
    }
    
    // Emit event to frontend
    app_handle
        .emit_all("session_updated", new_state)
        .map_err(|e| e.to_string())?;
    
    Ok(())
}

#[tauri::command]
async fn hide_overlay(app_handle: tauri::AppHandle) -> Result<(), String> {
    if let Some(window) = app_handle.get_window("main") {
        window.hide().map_err(|e| e.to_string())?;
    }
    Ok(())
}

#[tauri::command]
async fn show_overlay(app_handle: tauri::AppHandle) -> Result<(), String> {
    if let Some(window) = app_handle.get_window("main") {
        window.show().map_err(|e| e.to_string())?;
        window.set_focus().map_err(|e| e.to_string())?;
    }
    Ok(())
}

fn main() {
    let session_state: SharedSessionState = Arc::new(Mutex::new(SessionState::default()));

    tauri::Builder::default()
        .manage(session_state)
        .invoke_handler(tauri::generate_handler![
            get_session_state,
            abort_session,
            update_session_state,
            hide_overlay,
            show_overlay
        ])
        .setup(|app| {
            // Register global shortcut for ESC to abort session
            let app_handle = app.handle();
            app.global_shortcut_manager()
                .register("Escape", move || {
                    let _ = app_handle.emit_all("escape_pressed", ());
                })
                .expect("Failed to register global shortcut");
            
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
} 