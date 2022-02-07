import { writable } from 'svelte/store';

import { message } from './connection';

export const block = writable(null as BlockMessage);

export const selectedFile = writable(null as BlockFile);

export const selectedFileContent = writable(null as FileContentMessage);

message.subscribe((message) => {
    if (message) {
        if (message.type === 'repository' || message.type == 'branch' || message.type === 'repository-deleted') {
            block.set(null);
            selectedFile.set(null);
            selectedFileContent.set(null);
        } else if (message.type === 'block') {
            block.set(message);
            selectedFile.set(null);
            selectedFileContent.set(null);
        } else if (message.type === 'file-content') {
            selectedFileContent.set(message);
        }
    }
});
