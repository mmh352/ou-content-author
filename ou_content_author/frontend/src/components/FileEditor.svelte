<script lang="ts">
    import { tick, onDestroy } from 'svelte';
    import { EditorState, Transaction } from '@codemirror/state';
    import { EditorView, keymap } from '@codemirror/view';
    import { defaultKeymap } from '@codemirror/commands';
    import { history, historyKeymap } from '@codemirror/history';
    import { markdown } from '@codemirror/lang-markdown';
    import { lineNumbers } from '@codemirror/gutter';
    import { classHighlightStyle } from '@codemirror/highlight';

    import { block, message, selectedFile, selectedFileContent, sendMessage } from '../store';

    let editorElement = null as HTMLElement;
    let editor: EditorView;
    let updateTimeout: number;

    const selectedFileUnsubscribe = selectedFile.subscribe((selectedFile) => {
        if (selectedFile) {
            selectedFileContent.set(null);
            sendMessage({
                type: 'load-file-content',
                block: $block.path,
                file: selectedFile,
            });
        };
    });

    const selectedFileContentUnsubscribe = selectedFileContent.subscribe(async (selectedFileContent) => {
        if (selectedFileContent) {
            await tick();
            const state = EditorState.create({
                doc: selectedFileContent.content,
                extensions: [
                    classHighlightStyle,
                    markdown(),
                    lineNumbers(),
                    history(),
                    EditorView.lineWrapping,
                    keymap.of(defaultKeymap),
                    keymap.of(historyKeymap),
                    keymap.of([
                        {
                            key: 'Ctrl-s',
                            run() {
                                sendMessage({
                                    type: 'save-file-content',
                                    block: $block.path,
                                    file: $selectedFile,
                                    content: editor.state.doc.toString(),
                                });
                                return true;
                            }
                        }
                    ]),
                ],
            });
            if (editor) {
                editor.setState(state);
            } else {
                editor = new EditorView({
                    state: state,
                    parent: editorElement,
                    dispatch(tr: Transaction) {
                        if (tr.docChanged) {
                            window.clearTimeout(updateTimeout);
                            updateTimeout = window.setTimeout(() => {
                                sendMessage({
                                    type: 'save-file-content',
                                    block: $block.path,
                                    file: $selectedFile,
                                    content: editor.state.doc.toString(),
                                });
                            }, 300);
                        }
                        editor.update([tr]);
                        editor = editor;
                    },
                });
            }
        } else {
            if (editor) {
                editor.destroy();
                editor = null;
            }
        }
    });

    const messageUnsubscribe = message.subscribe((message) => {
        if (message) {
            if (message.type == 'changes-discarded') {
                if ($selectedFile) {
                    selectedFileContent.set(null);
                    sendMessage({
                        type: 'load-file-content',
                        block: $block.path,
                        file: $selectedFile,
                    });
                };
            }
        }
    });

    onDestroy(() => {
        selectedFileUnsubscribe();
        selectedFileContentUnsubscribe();
        messageUnsubscribe();
        if (editor) {
            editor.destroy();
            editor = null;
        }
    });
</script>

<div class="relative flex-0 w-2/5 border-r-2">
    {#if $selectedFile === null}
        <p class="absolute left-1/2 top-1/2 transform -translate-x-1/2 -translate-y-1/2 text-gray-900 text-center text-sm">Select a file on the left to edit it.</p>
    {:else if $selectedFileContent === null}
        <p class="absolute left-1/2 top-1/2 transform -translate-x-1/2 -translate-y-1/2 text-gray-900 text-center text-sm">Loading...</p>
    {:else}
        <div bind:this={editorElement} class="w-full h-full overflow-auto"></div>
    {/if}
</div>
