<script lang="ts">
    import { onDestroy } from 'svelte';

    import { message, selectedFileContent } from '../store';
    import Button from './Button.svelte';

    let rendering = false;
    let contentUrl = '';
    let logEntries = [];
    let showLogEntries = false;
    let iframeElement = null as HTMLIFrameElement;

    const messageUnsubscribe = message.subscribe((message) => {
        if (message) {
            if (message.type === 'file-rendering') {
                rendering = true;
                logEntries = [];
            } else if (message.type === 'file-rendered') {
                rendering = false;
                if (contentUrl == '/rendered' + message.url) {
                    iframeElement.contentWindow.location.reload();
                } else {
                    contentUrl = '/rendered' + message.url;
                }
                logEntries = message.output.split('\n');
            }
        }
    });

    onDestroy(messageUnsubscribe);
</script>

<div id="page-viewer" class="relative flex-0 w-2/5 overflow-auto px-2 py-1">
    {#if rendering}
        <svg viewBox="0 0 38 38" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" class="absolute left-1/2 top-1/2 transform -translate-x-1/2 -translate-y-1/2 stroke-blue z-40 w-20 h-20">
            <g fill="none" fill-rule="evenodd">
                <g transform="translate(1 1)" stroke-width="2">
                    <circle stroke-opacity=".5" cx="18" cy="18" r="18"/>
                    <path d="M36 18c0-9.94-8.06-18-18-18">
                        <animateTransform
                            attributeName="transform"
                            type="rotate"
                            from="0 18 18"
                            to="360 18 18"
                            dur="1s"
                            repeatCount="indefinite"/>
                    </path>
                </g>
            </g>
        </svg>
        <p class="sr-only">Rendering. Please wait...</p>
    {/if}
    {#if $selectedFileContent}
        <iframe bind:this={iframeElement} src={contentUrl} title="The rendered file" class="w-full h-full overflow-auto"></iframe>
        {#if logEntries.length > 0}
            <div class="absolute right-0 top-0">
                <Button on:action={() => { showLogEntries = !showLogEntries; }}>
                    <svg viewBox="0 0 24 24" aria-hidden="true" class="w-4 h-4">
                        <path fill="currentColor" d="M14,10H2V12H14V10M14,6H2V8H14V6M2,16H10V14H2V16M21.5,11.5L23,13L16,20L11.5,15.5L13,14L16,17L21.5,11.5Z" />
                    </svg>
                </Button>
            </div>
            {#if showLogEntries}
                <ol class="absolute left-0 bottom-0 max-h-1/2 w-full bg-white z-20 overflow-auto px-2 py-2 border-t-2 border-gray-700 text-sm">
                    {#each logEntries as logEntry}
                        <li>{logEntry}</li>
                    {/each}
                </ol>
            {/if}
        {/if}
    {:else}
        <p class="absolute left-1/2 top-1/2 transform -translate-x-1/2 -translate-y-1/2 text-gray-900 text-center text-sm">The preview content will be shown here.</p>
    {/if}
</div>
