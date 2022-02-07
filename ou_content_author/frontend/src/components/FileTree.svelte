<script lang="ts">
    import { derived } from 'svelte/store';
    import { block, selectedFile } from '../store';

    const fileList = derived(block, (block) => {
        if (block) {
            let sections = [];
            for (let file of block.files) {
                let found = false;
                for (let section of sections) {
                    if (section.path === file.directory) {
                        section.files.push(file);
                        found = true;
                        break
                    }
                }
                if (!found) {
                    sections.push({
                        path: file.directory,
                        files: [file],
                    });
                }
            }
            for (let section of sections) {
                section.files = section.files.sort((a: BlockFile, b: BlockFile) => {
                    if (a.filename > b.filename) {
                        return 1;
                    } else if (a.filename < b.filename) {
                        return -1;
                    } else {
                        return 0;
                    }
                });
            }
            sections = sections.sort((a, b) => {
                const aParts = a.path.split('/');
                const bParts = b.path.split('/');
                if (aParts.length > bParts.length) {
                    return 1;
                } else if (aParts.length < bParts.length) {
                    return 0;
                } else {
                    for (let idx = 0; idx < aParts.length; idx++) {
                        if (aParts[idx] > bParts[idx]) {
                            return 1;
                        } else if (aParts[idx] < bParts[idx]) {
                            return -1;
                        }
                    }
                    return 0;
                }
            });
            return sections;
        } else {
            return [];
        }
    });
</script>

<nav class="relative flex-0 border-r-2 w-1/5 overflow-auto text-sm px-2 py-1 overflow-auto">
    {#if $block !== null}
        <ol>
            {#each $fileList as section}
            <li>
                <span class="font-bold tracking-widest">{#if section.path}{section.path}{:else}/{/if}</span>
                <ol class="pl-3">
                    {#each section.files as file}
                        <li><button on:click={() => { selectedFile.set(file); }} class="text-blue hover:underline focus:underline {file === $selectedFile ? 'italic' : ''}" aria-current="{file === $selectedFile ? 'true' : 'false'}">{file.filename}</button></li>
                    {/each}
                </ol>
            </li>
            {/each}
        </ol>
    {:else}
        <p class="absolute left-1/2 top-1/2 transform -translate-x-1/2 -translate-y-1/2 text-gray-900 text-center">Select a block to see the files available for editing</p>
    {/if}
</nav>
