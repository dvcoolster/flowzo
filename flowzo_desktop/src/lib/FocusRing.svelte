<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { invoke } from '@tauri-apps/api/tauri';
  import { listen } from '@tauri-apps/api/event';

  interface SessionState {
    session_id: string;
    state: string;
    elapsed_seconds: number;
    remaining_seconds: number;
    total_duration: number;
    task?: string;
  }

  let sessionState: SessionState = {
    session_id: 'idle',
    state: 'idle',
    elapsed_seconds: 0,
    remaining_seconds: 0,
    total_duration: 0,
    task: undefined
  };

  let progressOffset = 0;
  let updateInterval: number;
  let unlistenEscape: (() => void) | undefined;
  let unlistenSessionUpdate: (() => void) | undefined;

  const circumference = 2 * Math.PI * 140; // radius = 140

  function updateProgress() {
    if (sessionState.total_duration > 0) {
      const progress = sessionState.remaining_seconds / sessionState.total_duration;
      progressOffset = circumference * (1 - progress);
    } else {
      progressOffset = circumference;
    }
  }

  function formatTime(seconds: number): string {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  }

  function getStateColor(state: string): string {
    switch (state) {
      case 'priming': return '#f59e0b';
      case 'active': return '#3b82f6';
      case 'cooldown': return '#10b981';
      case 'aborted': return '#ef4444';
      default: return '#6b7280';
    }
  }

  async function handleAbort() {
    try {
      await invoke('abort_session');
    } catch (error) {
      console.error('Failed to abort session:', error);
    }
  }

  async function fetchSessionState() {
    try {
      const state = await invoke('get_session_state') as SessionState;
      sessionState = state;
      updateProgress();
    } catch (error) {
      console.error('Failed to fetch session state:', error);
    }
  }

  onMount(async () => {
    // Initial fetch
    await fetchSessionState();

    // Set up polling
    updateInterval = setInterval(fetchSessionState, 500);

    // Listen for escape key
    unlistenEscape = await listen('escape_pressed', handleAbort);

    // Listen for session updates
    unlistenSessionUpdate = await listen('session_updated', (event) => {
      sessionState = event.payload as SessionState;
      updateProgress();
    });
  });

  onDestroy(() => {
    if (updateInterval) {
      clearInterval(updateInterval);
    }
    if (unlistenEscape) {
      unlistenEscape();
    }
    if (unlistenSessionUpdate) {
      unlistenSessionUpdate();
    }
  });

  $: updateProgress();
</script>

<div class="focus-ring">
  <svg class="progress-ring" viewBox="0 0 284 284">
    <circle
      cx="142"
      cy="142"
      r="140"
      fill="none"
      stroke="rgba(255, 255, 255, 0.1)"
      stroke-width="4"
    />
    <circle
      class="progress-circle"
      cx="142"
      cy="142"
      r="140"
      stroke={getStateColor(sessionState.state)}
      stroke-dasharray={circumference}
      stroke-dashoffset={progressOffset}
    />
  </svg>

  <div class="content">
    {#if sessionState.task}
      <div class="task-text" title={sessionState.task}>
        {sessionState.task}
      </div>
    {/if}
    
    <div class="time-text" style="color: {getStateColor(sessionState.state)}">
      {formatTime(sessionState.remaining_seconds)}
    </div>
    
    <div class="state-text">
      {sessionState.state}
    </div>
  </div>

  <div class="abort-hint">
    ESC to abort
  </div>
</div>

<style>
  .content {
    z-index: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
  }
</style> 