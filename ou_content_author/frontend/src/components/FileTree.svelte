<script lang="ts">
    import { derived } from 'svelte/store';

    import { block, selectedFile, sendMessage } from '../store';
    import Button from './Button.svelte';
    import ModalDialog from './ModalDialog.svelte';

    let showAddFile = false;
    let newFileName = '';
    let newFileNameError = '';
    let newDirectoryName = '';
    let fileToDelete = null as BlockFile;

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
                for (let idx = 0; idx < Math.max(aParts.length, bParts.length); idx++) {
                    if (idx < aParts.length && idx < bParts.length) {
                        if (aParts[idx] < bParts[idx]) {
                            return -1;
                        } else if (aParts[idx] > bParts[idx]) {
                            return 1;
                        }
                    } else if (idx < aParts.length) {
                        return 1;
                    } else if (idx < bParts.length) {
                        return -1;
                    }
                }
                /*if (aParts.length > bParts.length) {
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
                }*/
                return 0;
            });
            return sections;
        } else {
            return [];
        }
    });

    function createFile(ev: Event) {
        ev.preventDefault();
        if (newFileName.trim() !== '') {
            newFileNameError = '';
            sendMessage({
                type: 'add-file',
                block: $block.path,
                file: {
                    directory: newDirectoryName,
                    filename: newFileName,
                },
            });
            showAddFile = false;
        } else {
            newFileNameError = 'Please provide a file name';
        }
    }

    function deleteFile(ev: Event) {
        ev.preventDefault();
        sendMessage({
            type: 'delete-file',
            block: $block.path,
            file: fileToDelete,
        });
        fileToDelete = null;
    }
</script>

<div class="relative flex-0 flex flex-col border-r-2 w-1/5">
    {#if $block !== null}
        <nav class="border-b py-1 px-2">
            <ul class="flex flex-row justify-end space-x-2">
                <li role="presentation">
                    <Button on:action={() => { showAddFile = true; newFileName = ''; newFileNameError = ''; newDirectoryName = ''; }}>
                        <svg viewBox="0 0 24 24" class="w-4 h-4">
                            <path fill="currentColor" d="M12,14V11H10V14H7V16H10V19H12V16H15V14M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18" />
                        </svg>
                    </Button>
                </li>
            </ul>
        </nav>
        <nav class="flex-1 p-2 text-sm overflow-auto">
            <ol>
                {#each $fileList as section}
                    <li role="presentation">
                        <span class="font-bold tracking-widest">{#if section.path}{section.path}{:else}/{/if}</span>
                        <ol class="pl-3">
                            {#each section.files as file}
                                <li role="presentation" class="flex flex-row">
                                    <button on:click={() => { selectedFile.set(file); }} class="flex-1 text-left text-blue hover:underline focus:underline {file === $selectedFile ? 'italic' : ''}" aria-current="{file === $selectedFile ? 'true' : 'false'}">{file.filename}</button>
                                    <button on:click={() => { fileToDelete = file; }} class="flex-none text-blue" title="Delete {file.filename}"><span class="sr-only">Delete {file.filename}</span>
                                        <svg viewBox="0 0 24 24" class="w-4 h-4" aria-hidden="true">
                                            <path fill="currentColor" d="M19,4H15.5L14.5,3H9.5L8.5,4H5V6H19M6,19A2,2 0 0,0 8,21H16A2,2 0 0,0 18,19V7H6V19Z" />
                                        </svg>
                                    </button>
                                </li>
                            {/each}
                        </ol>
                    </li>
                {/each}
            </ol>
        </nav>
        {#if showAddFile}
            <form on:submit={createFile}>
                <ModalDialog>
                    <h2 slot="title">Add a file</h2>
                    <div slot="content" class="text-base">
                        <label class="block pb-2">Parent directory
                            <select bind:value={newDirectoryName} class="block w-full py-1 px-2 border" data-action="autofocus">
                                {#each $fileList as directory}
                                    <option value={directory.path}>{directory.path || '/'}</option>
                                {/each}
                            </select>
                        </label>
                        <label class="relative block">New file name (can include path to create)
                            <input bind:value={newFileName} type="text" class="block w-full py-1 px-2 border focus:outline outline-2 outline-blue outline-offset-1 focus:shadow-inner"/>
                            {#if newFileNameError}
                                <span class="block w-full border border-red bg-white shadow text-sm text-red px-2 py-1">{newFileNameError}</span>
                            {/if}
                            </label>
                    </div>
                    <div slot="buttons" class="flex flex-row justify-end space-x-2">
                        <Button on:action={() => { showAddFile = false; }} style="secondary">Don't add file</Button>
                        <Button type="submit" style="success">Add file</Button>
                    </div>
                </ModalDialog>
            </form>
        {/if}
        {#if fileToDelete}
            <form on:submit={deleteFile}>
                <ModalDialog>
                    <h2 slot="title">Delete a file</h2>
                    <div slot="content" class="text-base">
                        <label class="block pb-2">Parent directory
                            <input value={fileToDelete.directory || '/'} disabled={true} type="text" class="block w-full py-1 px-2 border focus:outline outline-2 outline-blue outline-offset-1 focus:shadow-inner"/>
                        </label>
                        <label class="relative block">File to delete
                            <input value={fileToDelete.filename} disabled={true} type="text" class="block w-full py-1 px-2 border focus:outline outline-2 outline-blue outline-offset-1 focus:shadow-inner"/>
                        </label>
                    </div>
                    <div slot="buttons" class="flex flex-row justify-end space-x-2">
                        <Button on:action={() => { fileToDelete = null; }} style="secondary">Don't delete file</Button>
                        <Button type="submit" style="failure">Delete file</Button>
                    </div>
                </ModalDialog>
            </form>
        {/if}
    {:else}
        <p class="absolute left-1/2 top-1/2 transform -translate-x-1/2 -translate-y-1/2 text-gray-900 text-center">Select a block to see the files available for editing</p>
    {/if}
</div>
