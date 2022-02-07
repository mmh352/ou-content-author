import { writable } from 'svelte/store';

import { message } from './connection';

export const repository = writable(null as RepositoryMessage);

export const branch = writable(null as BranchMessage);

message.subscribe((message) => {
    if (message) {
        if (message.type === 'repository') {
            repository.set(message);
            branch.set(null);
        } else if (message.type === 'branch') {
            branch.set(message);
        } else if (message.type === 'repository-deleted') {
            repository.set(null);
            branch.set(null);
        }
    }
});
