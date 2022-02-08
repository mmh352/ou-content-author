<script lang="ts">
    import { onDestroy } from 'svelte';
    import { message, repository, branch, block, sendMessage } from '../store';
    import { localDeleteValue, localLoadValue, localStoreValue } from '../storage';
    import Button from './Button.svelte';
    import ModalDialog from './ModalDialog.svelte';

    const repositoryStore = localLoadValue('repository', {}) as {url: string; username: string; password: string; name: string; email: string;};
    let repositoryUrl = repositoryStore.url || '';
    let repositoryUrlError = '';
    let repositoryUsername = repositoryStore.username || '';
    let repositoryPassword = repositoryStore.password || '';
    let repositoryName = repositoryStore.name || '';
    let repositoryNameError = '';
    let repositoryEmail = repositoryStore.email || '';
    let repositoryEmailError = '';
    let repositoryRemember = repositoryStore.url !== undefined && repositoryStore.username !== undefined && repositoryStore.password !== undefined && repositoryStore.name !== undefined && repositoryStore.email !== undefined;
    let commitMessage = '';
    let commitMessagError = '';
    let busyAction = '';

    function handleRespositoryEvents(ev: Event) {
        ev.preventDefault();
        if (busyAction == '') {
            if ($repository) {
                busyAction = 'delete';
                sendMessage({
                    type: 'delete-repository',
                });
            } else {
                repositoryUrlError = '';
                if (!repositoryUrl.startsWith('https://')) {
                    repositoryUrlError = 'Only https URLs are supported.';
                    return;
                }
                if (repositoryName.trim() === '') {
                    repositoryNameError = 'You must enter your name';
                    return;
                }
                if (repositoryEmail.trim() === '') {
                    repositoryEmailError = 'You must enter your e-mail address';
                    return;
                }
                let url = repositoryUrl;
                if (repositoryUsername && repositoryPassword) {
                    url = 'https://' + repositoryUsername + ':' + repositoryPassword + '@' + url.substring(8);
                }
                busyAction = 'clone';
                if (repositoryRemember) {
                    localStoreValue('repository', {
                        url: repositoryUrl,
                        username: repositoryUsername,
                        password: repositoryPassword,
                        name: repositoryName,
                        email: repositoryEmail,
                    });
                } else {
                    localDeleteValue('repository');
                }
                sendMessage({
                    type: 'clone-repository',
                    url: url,
                });
            }
        }
    }

    function handleSelectBranch(ev: Event) {
        const target = ev.target as HTMLSelectElement;
        if (target.value) {
            busyAction = 'checkout';
            sendMessage({
                type: 'checkout-branch',
                branch: target.value,
            });
        }
    }

    function handleSelectBlock(ev: Event) {
        const target = ev.target as HTMLSelectElement;
        if (target.value && $branch !== null) {
            busyAction = 'select-block';
            sendMessage({
                type: 'select-block',
                block: target.value
            });
        }
    }

    function handleCommit(ev: Event) {
        ev.preventDefault();
        if (commitMessage.trim() && $block !== null) {
            commitMessagError = '';
            busyAction = 'commit-changes';
            sendMessage({
                type: 'commit-changes',
                name: repositoryName,
                email: repositoryEmail,
                message: commitMessage
            });
        } else {
            commitMessagError = 'Please provide a commit message';
        }
    }

    function handleDiscard(ev: Event) {
        ev.preventDefault();
        commitMessage = '';
        if ($block !== null) {
            busyAction = 'discard-changes';
            sendMessage({
                type: 'discard-changes',
            });
        }
    }

    const messageUnsubscribe = message.subscribe((message) => {
        if (message) {
            if (message.type === 'repository' || message.type === 'branch' || message.type == 'block' || message.type === 'repository-deleted' || message.type == 'changes-committed' || message.type == 'changes-discarded') {
                busyAction = '';
            }
            if (message.type == 'changes-committed') {
                commitMessage = '';
            }
        }
    });

    onDestroy(() => {
        messageUnsubscribe();
    });
</script>

<div class="flex-0 flex flex-row border-b-2 text-sm">
    <form on:submit={handleRespositoryEvents} class="flex-1 flex flex-row space-x-2 px-2 py-1">
        <label class="block w-96 relative"><span class="sr-only">Repository URL</span>
            <input bind:value={repositoryUrl} disabled={$repository !== null} type="text" placeholder="Enter the repository URL here" class="block w-full h-full px-2 border focus:outline outline-2 outline-blue outline-offset-1 focus:shadow-inner"/>
            {#if repositoryUrlError}
                <span class="absolute block w-full border border-red bg-white shadow text-sm text-red px-2 py-1">{repositoryUrlError}</span>
            {/if}
        </label>
        {#if $repository === null}
            <label class="block w-64 relative"><span class="sr-only">Repository username</span>
                <input bind:value={repositoryUsername} type="text" placeholder="Username" class="block w-full h-full px-2 border focus:outline outline-2 outline-blue outline-offset-1 focus:shadow-inner"/>
            </label>
            <label class="block w-64 relative"><span class="sr-only">Repository password</span>
                <input bind:value={repositoryPassword} type="password" placeholder="Password" class="block w-full h-full px-2 border focus:outline outline-2 outline-blue outline-offset-1 focus:shadow-inner"/>
            </label>
            <label class="block w-32 relative"><span class="sr-only">Your name</span>
                <input bind:value={repositoryName} type="text" placeholder="Name" class="block w-full h-full px-2 border focus:outline outline-2 outline-blue outline-offset-1 focus:shadow-inner"/>
                {#if repositoryNameError}
                    <span class="absolute block w-full border border-red bg-white shadow text-sm text-red px-2 py-1">{repositoryNameError}</span>
                {/if}
            </label>
            <label class="block w-40 relative"><span class="sr-only">Your e-mail address</span>
                <input bind:value={repositoryEmail} type="email" placeholder="E-Mail address" class="block w-full h-full px-2 border focus:outline outline-2 outline-blue outline-offset-1 focus:shadow-inner"/>
                {#if repositoryEmailError}
                    <span class="absolute block w-full border border-red bg-white shadow text-sm text-red px-2 py-1">{repositoryEmailError}</span>
                {/if}
            </label>
            <label class="block relative whitespace-nowrap self-center">
                <input bind:checked={repositoryRemember} type="checkbox" /> Remember
            </label>
            <Button type="submit" ariaLabel="Connect">
                <svg viewBox="0 0 24 24" aria-hidden="true" class="w-4 h-4">
                    <path fill="currentColor" d="M13,19H14A1,1 0 0,1 15,20H22V22H15A1,1 0 0,1 14,23H10A1,1 0 0,1 9,22H2V20H9A1,1 0 0,1 10,19H11V17H4A1,1 0 0,1 3,16V12A1,1 0 0,1 4,11H20A1,1 0 0,1 21,12V16A1,1 0 0,1 20,17H13V19M4,3H20A1,1 0 0,1 21,4V8A1,1 0 0,1 20,9H4A1,1 0 0,1 3,8V4A1,1 0 0,1 4,3M9,7H10V5H9V7M9,15H10V13H9V15M5,5V7H7V5H5M5,13V15H7V13H5Z" />
                </svg>
            </Button>
        {:else}
            <Button type="submit" ariaLabel="Disconnect" style="failure">
                <svg viewBox="0 0 24 24" aria-hidden="true" class="w-4 h-4">
                    <path fill="currentColor" d="M13,19H14A1,1 0 0,1 15,20H15.73L13,17.27V19M22,20V21.18L20.82,20H22M21,22.72L19.73,24L17.73,22H15A1,1 0 0,1 14,23H10A1,1 0 0,1 9,22H2V20H9A1,1 0 0,1 10,19H11V17H4A1,1 0 0,1 3,16V12A1,1 0 0,1 4,11H6.73L4.73,9H4A1,1 0 0,1 3,8V7.27L1,5.27L2.28,4L21,22.72M4,3H20A1,1 0 0,1 21,4V8A1,1 0 0,1 20,9H9.82L7,6.18V5H5.82L3.84,3C3.89,3 3.94,3 4,3M20,11A1,1 0 0,1 21,12V16A1,1 0 0,1 20,17H17.82L11.82,11H20M9,7H10V5H9V7M9,15H10V14.27L9,13.27V15M5,13V15H7V13H5Z" />
                </svg>
            </Button>
        {/if}
    </form>
    <div role="presentation" class="flex-auto"></div>
    {#if $repository !== null}
        <div class="flex-0 flex flex-row space-x-2 px-2 py-1">
            <label class="block 2 w-40"><span class="sr-only">Select branch</span>
                <select on:change={handleSelectBranch} class="block w-full h-full border">
                    <option value="">--- Select a branch ---</option>
                    {#each $repository.branches as branch}
                        <option value={branch}>{branch}</option>
                    {/each}
                </select>
            </label>
        </div>
        <div class="flex-0 flex flex-row space-x-2 px-2 py-1">
            <label class="block 2 w-40"><span class="sr-only">Select block</span>
                <select on:change={handleSelectBlock} disabled={$branch === null} class="block w-full h-full border">
                    {#if $branch !== null}
                        <option value="">--- Select block ---</option>
                        {#each $branch.blocks as block}
                            <option value={block}>{block}</option>
                        {/each}
                    {/if}
                </select>
            </label>
        </div>
        <div role="presentation" class="flex-auto"></div>
        <form on:submit={handleCommit} class="flex-1 flex flex-row space-x-2 px-2 py-1">
            <label class="relative block w-96"><span class="sr-only">Commit message</span>
                <input bind:value={commitMessage} disabled={$block === null} type="text" placeholder="Commit message" class="block w-full h-full px-2 border focus:outline outline-2 outline-blue outline-offset-1 focus:shadow-inner"/>
                {#if commitMessagError}
                    <span class="absolute block w-full border border-red bg-white shadow text-sm text-red px-2 py-1">{commitMessagError}</span>
                {/if}
            </label>
            <button disabled={$block === null} type="submit" aria-label="Commit changes" class="px-1 py-1 border-green text-green hover:bg-green hover:text-white focus:bg-green focus:text-white transition-colors focus:outline outline-2 outline-blue outline-offset-1">
                <svg viewBox="0 0 24 24" aria-hidden="true" class="w-4 h-4">
                    <path fill="currentColor" d="M21,7L9,19L3.5,13.5L4.91,12.09L9,16.17L19.59,5.59L21,7Z" />
                </svg>
            </button>
            <button disabled={$block === null} on:click={handleDiscard} type="button" aria-label="Discard changes" class="px-1 py-1 border-red text-red hover:bg-red hover:text-white focus:bg-red focus:text-white transition-colors focus:outline outline-2 outline-blue outline-offset-1">
                <svg viewBox="0 0 24 24" aria-hidden="true" class="w-4 h-4">
                    <path fill="currentColor" d="M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z" />
                </svg>
            </button>
        </form>
    {/if}
    {#if busyAction === 'clone'}
        <ModalDialog>
            <h2 slot="title">Cloning the repository</h2>
            <div slot="content" class="text-base">
                <p>Your repository is being cloned into the content authoring system.</p>
                <p>This can take a few minutes. Please wait...</p>
            </div>
        </ModalDialog>
    {:else if busyAction === 'delete'}
        <ModalDialog>
            <h2 slot="title">Disconnecting from the repository</h2>
            <div slot="content" class="text-base">
                <p>You are being disconnected from the repository.</p>
                <p>This should not take very long. Please wait...</p>
            </div>
        </ModalDialog>
    {:else if busyAction === 'checkout'}
        <ModalDialog>
            <h2 slot="title">Checking out the branch</h2>
            <div slot="content" class="text-base">
                <p>The branch is being checked out for editing.</p>
                <p>This should not take very long. Please wait...</p>
            </div>
        </ModalDialog>
    {:else if busyAction === 'select-block'}
        <ModalDialog>
            <h2 slot="title">Fetching block files</h2>
            <div slot="content" class="text-base">
                <p>The files in this block are being fetched.</p>
                <p>This should not take very long. Please wait...</p>
            </div>
        </ModalDialog>
    {:else if busyAction === 'commit-changes'}
        <ModalDialog>
            <h2 slot="title">Commiting changes</h2>
            <div slot="content" class="text-base">
                <p>Your changes are being committed and pushed.</p>
                <p>This should not take very long. Please wait...</p>
            </div>
        </ModalDialog>
    {:else if busyAction === 'discard-changes'}
        <ModalDialog>
            <h2 slot="title">Discard changes</h2>
            <div slot="content" class="text-base">
                <p>All changes since the last commit are being discarded.</p>
                <p>This should not take very long. Please wait...</p>
            </div>
        </ModalDialog>
    {/if}
</div>
